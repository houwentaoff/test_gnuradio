#!/usr/bin/env python
#python benchmark_tx.py -s 128 -M 0.1 -v #python2
from gnuradio import gr
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
from optparse import OptionParser
import time, struct, sys

from gnuradio import iio
from gnuradio import digital
from gnuradio import blocks

# from current dir
from transmit_path import transmit_path
#from uhd_interface import uhd_transmitter

class my_top_block(gr.top_block):
    def __init__(self, options):
        gr.top_block.__init__(self)

        self.samp_rate = samp_rate = 1000000
        self.band_width = band_width = 20000000
        if(options.tx_freq is not None):
            self.sink = iio.pluto_sink('193.168.2.1', options.tx_freq, samp_rate, long(options.bandwidth), 0x8000, False, 10.0, '', True)
            #self.sink = uhd_transmitter(options.args,
            #                            options.bandwidth, options.tx_freq, 
            #                            options.lo_offset, options.tx_gain,
            #                            options.spec, options.antenna,
            #                            options.clock_source, options.verbose)
        elif(options.to_file is not None):
            self.sink = blocks.file_sink(gr.sizeof_gr_complex, options.to_file)
        else:
            self.sink = blocks.null_sink(gr.sizeof_gr_complex)

        # do this after for any adjustments to the options that may
        # occur in the sinks (specifically the UHD sink)
        self.txpath = transmit_path(options)

        self.connect(self.txpath, self.sink)
        
# /////////////////////////////////////////////////////////////////////////////
#                                   main
# /////////////////////////////////////////////////////////////////////////////

def main():

    def send_pkt(payload='', eof=False):
        return tb.txpath.send_pkt(payload, eof)

    parser = OptionParser(option_class=eng_option, conflict_handler="resolve")
    expert_grp = parser.add_option_group("Expert")
    parser.add_option("","--discontinuous", action="store_true", default=False,
                      help="enable discontinuous mode")
    parser.add_option("","--from-file", default=None,
                      help="use intput file for packet contents")
    parser.add_option("","--to-file", default=None,
                      help="Output file for modulated samples")

    parser.add_option("","--freq", type="int",dest="tx_freq", default=500000000,
                      help="set tx freq")
    transmit_path.add_options(parser, expert_grp)
    digital.ofdm_mod.add_options(parser, expert_grp)
    #uhd_transmitter.add_options(parser)

    (options, args) = parser.parse_args ()

    # build the graph
    tb = my_top_block(options)
    
    r = gr.enable_realtime_scheduling()
    if r != gr.RT_OK:
        print "Warning: failed to enable realtime scheduling"

    tb.start()                       # start flow graph
    
    # generate and send packets
    n = 0
    pktno = 0
    c = 0
    while True:
        data = raw_input()
        payload = data
        send_pkt(payload)
    send_pkt(eof=True)
    time.sleep(2)               # allow time for queued packets to be sent
    tb.wait()                   # wait for it to finish

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
