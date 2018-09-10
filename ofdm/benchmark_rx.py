#!/usr/bin/env python
#  python  benchmark_rx.py -v #python2
from gnuradio import gr
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
from optparse import OptionParser

from gnuradio import blocks
from gnuradio import digital

from gnuradio import iio
# from current dir
from receive_path import receive_path
#from uhd_interface import uhd_receiver

import struct, sys

class my_top_block(gr.top_block):
    def __init__(self, callback, options):
        gr.top_block.__init__(self)

        self.samp_rate = samp_rate = 1000000
        self.band_width = band_width = 20000000
        if(options.rx_freq is not None):
            self.source = iio.pluto_source('192.168.2.1', options.rx_freq, samp_rate, long(options.bandwidth), 0x8000, True, True, True, "slow_attack", 64.0, '', True)
            #self.source = uhd_receiver(options.args,
            #                           options.bandwidth, options.rx_freq, 
            #                           options.lo_offset, options.rx_gain,
            #                           options.spec, options.antenna,
            #                           options.clock_source, options.verbose)
        elif(options.from_file is not None):
            self.source = blocks.file_source(gr.sizeof_gr_complex, options.from_file)
        else:
            self.source = blocks.null_source(gr.sizeof_gr_complex)

        # Set up receive path
        # do this after for any adjustments to the options that may
        # occur in the sinks (specifically the UHD sink)
        self.rxpath = receive_path(callback, options)

        self.connect(self.source, self.rxpath)
        

# /////////////////////////////////////////////////////////////////////////////
#                                   main
# /////////////////////////////////////////////////////////////////////////////

def main():

    global n_rcvd, n_right
        
    n_rcvd = 0
    n_right = 0

    def rx_callback(ok, payload):
        global n_rcvd, n_right
        n_rcvd += 1
        try:
            (pktno,) = struct.unpack('!I', payload[0:4])
        except:
            print "joy:Unexpected error:", sys.exc_info()[0]
            return
        if ok:
            n_right += 1
            for x in payload[4:]:
                print hex(ord(x)),
            print
        print "ok: %r \t pktno: %d \t n_rcvd: %d \t n_right: %d" % (ok, pktno, n_rcvd, n_right)

        if 0:
            #printlst = list()
            for x in payload[2:]:
                print hex(ord(x)),
                
                #t = hex(ord(x)).replace('0x', '')
                #if(len(t) == 1):
                #    t = '0' + t
                #printlst.append(t)
            #printable = ''.join(printlst)

            #print printable
            #print "\n"

    parser = OptionParser(option_class=eng_option, conflict_handler="resolve")
    expert_grp = parser.add_option_group("Expert")
    parser.add_option("","--discontinuous", action="store_true", default=False,
                      help="enable discontinuous")
    parser.add_option("","--from-file", default=None,
                      help="input file of samples to demod")

    parser.add_option("","--freq", type="int",dest="rx_freq", default=500000000,
                      help="set rx freq")
    receive_path.add_options(parser, expert_grp)
    #uhd_receiver.add_options(parser)
    digital.ofdm_demod.add_options(parser, expert_grp)

    (options, args) = parser.parse_args ()

    if options.from_file is None:
        if options.rx_freq is None:
            sys.stderr.write("You must specify -f FREQ or --freq FREQ\n")
            parser.print_help(sys.stderr)
            sys.exit(1)

    # build the graph
    tb = my_top_block(rx_callback, options)

    r = gr.enable_realtime_scheduling()
    if r != gr.RT_OK:
        print "Warning: failed to enable realtime scheduling"

    tb.start()                      # start flow graph
    tb.wait()                       # wait for it to finish

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
