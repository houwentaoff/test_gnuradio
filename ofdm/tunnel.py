#!/usr/bin/env python
#

# /////////////////////////////////////////////////////////////////////////////
#
#    This code sets up up a virtual ethernet interface (typically gr0),
#    and relays packets between the interface and the GNU Radio PHY+MAC
#
#    What this means in plain language, is that if you've got a couple
#    of USRPs on different machines, and if you run this code on those
#    machines, you can talk between them using normal TCP/IP networking.
#
# /////////////////////////////////////////////////////////////////////////////


from gnuradio import gr, digital
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
from optparse import OptionParser

# from current dir
from receive_path import receive_path
from transmit_path import transmit_path

from gnuradio import iio
import os, sys
import random, time, struct
import socket
import dpkt
#print os.getpid()
#raw_input('Attach and press enter')


# /////////////////////////////////////////////////////////////////////////////
#
#   Use the Universal TUN/TAP device driver to move packets to/from kernel
#
#   See /usr/src/linux/Documentation/networking/tuntap.txt
#
# /////////////////////////////////////////////////////////////////////////////

# Linux specific...
# TUNSETIFF ifr flags from <linux/tun_if.h>

IFF_TUN		= 0x0001   # tunnel IP packets
IFF_TAP		= 0x0002   # tunnel ethernet frames
IFF_NO_PI	= 0x1000   # don't pass extra packet info
IFF_ONE_QUEUE	= 0x2000   # beats me ;)

keepcount = 10

def open_tun_interface(tun_device_filename, ifr_name):
    from fcntl import ioctl
    
    mode = IFF_TAP | IFF_NO_PI
    TUNSETIFF = 0x400454ca

    tun = os.open(tun_device_filename, os.O_RDWR)
    ifs = ioctl(tun, TUNSETIFF, struct.pack("16sH", ifr_name, mode))
    ifname = ifs[:16].strip("\x00")
    return (tun, ifname)

class nicutil(object):
    @staticmethod
    def get_ip(name):
        from fcntl import ioctl
        sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        ip=ioctl(sock.fileno(),0x8915,struct.pack('64s',name))
        ip = ip[20:24]
        '''
        sip=socket.inet_ntoa(ip)
        print "ip:", sip
        '''
        return ip
    @staticmethod
    def get_mac(name):
        from fcntl import ioctl
        sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        mac=ioctl(sock.fileno(),0x8927,struct.pack('64s',name))
        mac = mac[18:24]
        '''
        print "mac:",
        for c in mac:
            print hex(ord(c)),
        print 
        '''
        return mac


# /////////////////////////////////////////////////////////////////////////////
#                             the flow graph
# /////////////////////////////////////////////////////////////////////////////

class my_top_block(gr.top_block):
    def __init__(self, callback, options):
        gr.top_block.__init__(self)

        self.samp_rate = samp_rate = 1000000

        self.source = iio.pluto_source(options.dev_ip, options.rx_freq, samp_rate, long(options.bandwidth*2), 0xA000, True, True, True, "fast_attack", 64.0, '', True)
        
        """
        self.source = uhd_receiver(options.args,
                                   options.bandwidth,
                                   options.rx_freq,
                                   options.lo_offset, options.rx_gain,
                                   options.spec, options.antenna,
                                   options.clock_source, options.verbose)
        """
        #0x8000
        self.sink = iio.pluto_sink(options.dev_ip, options.tx_freq, samp_rate, long(options.bandwidth), 0xA000, False, 10.0, '', True)
        """self.sink = uhd_transmitter(options.args,
                                    options.bandwidth, options.tx_freq,
                                    options.lo_offset, options.tx_gain,
                                    options.spec, options.antenna,
                                    options.clock_source, options.verbose)
        """
        self.txpath = transmit_path(options)
        self.rxpath = receive_path(callback, options)

        self.connect(self.txpath, self.sink)
        self.connect(self.source, self.rxpath)

    def carrier_sensed(self):
        """
        Return True if the receive path thinks there's carrier
        """
        print "carrier_sensed"
        return self.rxpath.carrier_sensed()

    def set_freq(self, target_freq):
        """
        Set the center frequency we're interested in.
        """
        print 'set freq:', target_freq
        self.u_snk.set_freq(target_freq)
        self.u_src.set_freq(target_freq)
        

# /////////////////////////////////////////////////////////////////////////////
#                           Carrier Sense MAC
# /////////////////////////////////////////////////////////////////////////////

class cs_mac(object):
    """
    Prototype carrier sense MAC

    Reads packets from the TUN/TAP interface, and sends them to the PHY.
    Receives packets from the PHY via phy_rx_callback, and sends them
    into the TUN/TAP interface.

    Of course, we're not restricted to getting packets via TUN/TAP, this
    is just an example.
    """
    def __init__(self, tun_fd, name, verbose=False):
        self.tun_fd = tun_fd       # file descriptor for TUN/TAP interface
        self.verbose = verbose
        self.tb = None             # top block (access to PHY)
        self.nic_name = name

    def set_flow_graph(self, tb):
        self.tb = tb

    def phy_rx_callback(self, ok, payload):
        """
        Invoked by thread associated with PHY to pass received packet up.

        Args:
            ok: bool indicating whether payload CRC was OK
            payload: contents of the packet (string)
        """
        if self.verbose:
            print "Rx: ok = %r  len(payload) = %4d" % (ok, len(payload))
            if ok:
                for c in payload:
                    print "0x%.2x" % ord(c),
                print 
        if ok:
            os.write(self.tun_fd, payload)
        #if ok:
        # use lwip replace icmp,arp
        if False:
            eth = dpkt.ethernet.Ethernet(payload)
            # ip
            if isinstance(eth.data , dpkt.ip.IP):
                ip = eth.data 
                #icmp
                if isinstance(ip.data , dpkt.icmp.ICMP):
                    icmp = ip.data 
                    locip = nicutil.get_ip(self.nic_name)
                    locmac = nicutil.get_mac(self.nic_name)
                    if icmp.type == dpkt.icmp.ICMP_ECHO:
                        print 'icmp echo'
                        sip=socket.inet_ntoa(ip.src)
                        dip=socket.inet_ntoa(ip.dst)
                        print sip, '-->', dip
                        # to me
                        if eth.dst == locmac and ip.dst == locip:
                            sendicmp = dpkt.icmp.ICMP(
                                    type=0,
                                    data=dpkt.icmp.ICMP.Echo(
                                        id=icmp.data.id,
                                        seq=icmp.data.seq,
                                        data=icmp.data.data
                                        )
                                    )
                            if self.verbose:
                                print 'icmp context:'
                                for c in sendicmp.pack():
                                    print "0x%.2x" % ord(c),
                                print
                            sendip = dpkt.ip.IP(id=ip.id, src=ip.dst,
                                    dst = ip.src, data=sendicmp, 
                                    p=dpkt.ip.IP_PROTO_ICMP)
                            sendip.pack()
                            sendeth = dpkt.ethernet.Ethernet(
                                dst=eth.src, src=eth.dst, 
                                type=dpkt.ethernet.ETH_TYPE_IP,
                                data=sendip)
                            sendeth.pack()
                            if self.verbose:
                                print 'send icmp reply'
                                for c in sendeth.pack():
                                    print "0x%.2x" % ord(c),
                                print
                            for i in range(0, keepcount):
                                self.tb.txpath.send_pkt(sendeth.pack())
                            return
                        else:
                            return

                    elif icmp.type == dpkt.icmp.ICMP_ECHOREPLY:
                        print 'icmp echo reply'
                        sip=socket.inet_ntoa(ip.src)
                        dip=socket.inet_ntoa(ip.dst)
                        print sip, '-->', dip
                        if locip == ip.src:
                            return
            #arp
            elif isinstance(eth.data , dpkt.arp.ARP):
                print 'recv a arp '
                arp = eth.data
                sip=socket.inet_ntoa(arp.spa)
                dip=socket.inet_ntoa(arp.tpa)
                print sip, '-->', dip
                ip = nicutil.get_ip(self.nic_name)
                if arp.op == dpkt.arp.ARP_OP_REQUEST:
                    print 'req'
                    # to me
                    if arp.tpa == ip:
                        locmac = nicutil.get_mac(self.nic_name)
                        print "send arp reply:"
                        eth2 = dpkt.ethernet.Ethernet(
                            dst=eth.src, src=locmac,
                            data=dpkt.arp.ARP(op=dpkt.arp.ARP_OP_REPLY,
                            sha=locmac, spa=arp.tpa, tha=arp.sha, tpa=arp.spa))
                        if self.verbose:
                            print 'loc mac:'
                            for c in locmac:
                                print "0x%.2x" % ord(c),
                            print
                            for c in eth2.pack():
                                print "0x%.2x" % ord(c),
                            print
                        for i in range(0, keepcount):
                            self.tb.txpath.send_pkt(eth2.pack())
                        return
                    else:
                        return
                elif arp.op == dpkt.arp.ARP_OP_REPLY:
                    print 'reply'
                    if arp.spa == ip:
                        return
            os.write(self.tun_fd, payload)

    def main_loop(self):
        """
        Main loop for MAC.
        Only returns if we get an error reading from TUN.

        FIXME: may want to check for EINTR and EAGAIN and reissue read
        """
        min_delay = 0.001               # seconds

        while 1:
            payload = os.read(self.tun_fd, 10*1024)
            if not payload:
                self.tb.txpath.send_pkt(eof=True)
                break

            if self.verbose:
                print "Tx: len(payload) = %4d" % (len(payload),)
                for c in payload:
                    print "0x%.2x" %ord(c),
                print 
            
            delay = min_delay
            while self.tb.carrier_sensed():
                sys.stderr.write('B')
                time.sleep(delay)
                if delay < 0.050:
                    delay = delay * 2       # exponential back-off
            
            for i in range(0, keepcount):
                self.tb.txpath.send_pkt(payload)


# /////////////////////////////////////////////////////////////////////////////
#                                   main
# /////////////////////////////////////////////////////////////////////////////

def main():

    parser = OptionParser (option_class=eng_option, conflict_handler="resolve")
    expert_grp = parser.add_option_group("Expert")

    parser.add_option("-m", "--modulation", type="choice", choices=['bpsk', 'qpsk'],
                      default='bpsk',
                      help="Select modulation from: bpsk, qpsk [default=%%default]")
    parser.add_option("-i", "--ip", dest="dev_ip",  
                      help="set device ip [default=%default]", default="193.168.2.1")  
    parser.add_option("-d", "--nicname", dest="nic_name",  
                      help="set NIC name [default=%default]", default="tap0")  
    parser.add_option("","--rfreq", type="int",dest="rx_freq", default=500000000,
                      help="set rx freq [default=%default]")
    parser.add_option("","--tfreq", type="int",dest="tx_freq", default=500000000,
                      help="set tx freq [default=%default]")
    parser.add_option("-v","--verbose", action="store_true", default=False)
    expert_grp.add_option("-c", "--carrier-threshold", type="eng_float", default=30,
                          help="set carrier detect threshold (dB) [default=%default]")
    expert_grp.add_option("","--tun-device-filename", default="/dev/net/tun",
                          help="path to tun device file [default=%default]")

    digital.ofdm_mod.add_options(parser, expert_grp)
    digital.ofdm_demod.add_options(parser, expert_grp)
    transmit_path.add_options(parser, expert_grp)
    receive_path.add_options(parser, expert_grp)
    
    (options, args) = parser.parse_args ()
    if len(args) != 0:
        parser.print_help(sys.stderr)
        sys.exit(1)

    if options.rx_freq is None or options.tx_freq is None:
        sys.stderr.write("You must specify -f FREQ or --freq FREQ\n")
        parser.print_help(sys.stderr)
        sys.exit(1)

    # open the TUN/TAP interface
    (tun_fd, tun_ifname) = open_tun_interface(options.tun_device_filename, options.nic_name)

    # Attempt to enable realtime scheduling
    r = gr.enable_realtime_scheduling()
    if r == gr.RT_OK:
        realtime = True
    else:
        realtime = False
        print "Note: failed to enable realtime scheduling"

    # instantiate the MAC
    mac = cs_mac(tun_fd, verbose=True, name=options.nic_name)


    # build the graph (PHY)
    tb = my_top_block(mac.phy_rx_callback, options)

    mac.set_flow_graph(tb)    # give the MAC a handle for the PHY

    print "modulation:     %s"   % (options.modulation,)
    print "freq:           %s"      % (eng_notation.num_to_str(options.tx_freq))

    tb.rxpath.set_carrier_threshold(options.carrier_threshold)
    print "Carrier sense threshold:", options.carrier_threshold, "dB"
    
    print
    print "Allocated virtual ethernet interface: %s" % (tun_ifname,)
    print "You must now use ifconfig to set its IP address. E.g.,"
    print
    print "  $ sudo ifconfig %s 192.168.200.1" % (tun_ifname,)
    print
    print "Be sure to use a different address in the same subnet for each machine."
    print


    tb.start()    # Start executing the flow graph (runs in separate threads)

    mac.main_loop()    # don't expect this to return...

    tb.stop()     # but if it does, tell flow graph to stop.
    tb.wait()     # wait for it to finish
                

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
