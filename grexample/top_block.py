#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: GPL-3.0
#
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Fri Aug 10 22:52:55 2018
# GNU Radio version: 3.7.12.0
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from PyQt4 import Qt
from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import iio
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import sys
from gnuradio import qtgui


class top_block(gr.top_block, Qt.QWidget):

    def __init__(self, audio_device="dmix:CARD=monitor,DEV=0", decimation=1, fm_station=401100000, hostname='127.0.0.1', interpolation=2, uri='193.168.2.1', wav_file='/home/work/github/gnuradio/grexample/111.wav'):
        gr.top_block.__init__(self, "Top Block")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Top Block")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())


        ##################################################
        # Parameters
        ##################################################
        self.audio_device = audio_device
        self.decimation = decimation
        self.fm_station = fm_station
        self.hostname = hostname
        self.interpolation = interpolation
        self.uri = uri
        self.wav_file = wav_file

        ##################################################
        # Variables
        ##################################################
        self.sample_rate = sample_rate = 2200000
        self.samp_rate = samp_rate = 2304000

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=8 / interpolation,
                decimation=1,
                taps=None,
                fractional_bw=None,
        )
        self.pluto_source_0 = iio.pluto_source(uri, fm_station, sample_rate, 20000000, 0x20000, True, True, True, "manual", 64.0, '', True)
        self.pluto_sink_0 = iio.pluto_sink(uri, fm_station, samp_rate, 20000, 0x8000, False, 10.0, '', True)
        self.low_pass_filter_0 = filter.fir_filter_ccf(sample_rate / (384000 * decimation), firdes.low_pass(
        	1, sample_rate / decimation, 44100, 44100, firdes.WIN_HAMMING, 6.76))
        self.blocks_wavfile_source_0 = blocks.wavfile_source('/home/work/github/gnuradio/grexample/111.wav', True)
        self.blocks_add_xx_0 = blocks.add_vff(1)
        self.audio_sink_0 = audio.sink(48000, audio_device, True)
        self.analog_wfm_rcv_0 = analog.wfm_rcv(
        	quad_rate=384000,
        	audio_decimation=8,
        )
        self.analog_nbfm_tx_0 = analog.nbfm_tx(
        	audio_rate=48000,
        	quad_rate=samp_rate / 8,
        	tau=75e-6,
        	max_dev=75e3,
        	fh=-1.0,
                )



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_nbfm_tx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.analog_wfm_rcv_0, 0), (self.audio_sink_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.analog_nbfm_tx_0, 0))
        self.connect((self.blocks_wavfile_source_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_wavfile_source_0, 1), (self.blocks_add_xx_0, 1))
        self.connect((self.low_pass_filter_0, 0), (self.analog_wfm_rcv_0, 0))
        self.connect((self.pluto_source_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.pluto_sink_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_audio_device(self):
        return self.audio_device

    def set_audio_device(self, audio_device):
        self.audio_device = audio_device

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.sample_rate / self.decimation, 44100, 44100, firdes.WIN_HAMMING, 6.76))

    def get_fm_station(self):
        return self.fm_station

    def set_fm_station(self, fm_station):
        self.fm_station = fm_station
        self.pluto_source_0.set_params(self.fm_station, self.sample_rate, 20000000, True, True, True, "manual", 64.0, '', True)
        self.pluto_sink_0.set_params(self.fm_station, self.samp_rate, 20000, 10.0, '', True)

    def get_hostname(self):
        return self.hostname

    def set_hostname(self, hostname):
        self.hostname = hostname

    def get_interpolation(self):
        return self.interpolation

    def set_interpolation(self, interpolation):
        self.interpolation = interpolation

    def get_uri(self):
        return self.uri

    def set_uri(self, uri):
        self.uri = uri

    def get_wav_file(self):
        return self.wav_file

    def set_wav_file(self, wav_file):
        self.wav_file = wav_file

    def get_sample_rate(self):
        return self.sample_rate

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        self.pluto_source_0.set_params(self.fm_station, self.sample_rate, 20000000, True, True, True, "manual", 64.0, '', True)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.sample_rate / self.decimation, 44100, 44100, firdes.WIN_HAMMING, 6.76))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.pluto_sink_0.set_params(self.fm_station, self.samp_rate, 20000, 10.0, '', True)


def argument_parser():
    parser = OptionParser(usage="%prog: [options]", option_class=eng_option)
    parser.add_option(
        "", "--audio-device", dest="audio_device", type="string", default="dmix:CARD=monitor,DEV=0",
        help="Set Audio device [default=%default]")
    parser.add_option(
        "", "--decimation", dest="decimation", type="intx", default=1,
        help="Set Decimation [default=%default]")
    parser.add_option(
        "", "--fm-station", dest="fm_station", type="intx", default=401100000,
        help="Set FM station [default=%default]")
    parser.add_option(
        "", "--hostname", dest="hostname", type="string", default='127.0.0.1',
        help="Set Hostname [default=%default]")
    parser.add_option(
        "", "--interpolation", dest="interpolation", type="intx", default=2,
        help="Set Interpolation [default=%default]")
    parser.add_option(
        "", "--uri", dest="uri", type="string", default='193.168.2.1',
        help="Set URI [default=%default]")
    parser.add_option(
        "", "--wav-file", dest="wav_file", type="string", default='/home/work/github/gnuradio/grexample/111.wav',
        help="Set WAV File [default=%default]")
    return parser


def main(top_block_cls=top_block, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(audio_device=options.audio_device, decimation=options.decimation, fm_station=options.fm_station, hostname=options.hostname, interpolation=options.interpolation, uri=options.uri, wav_file=options.wav_file)
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
