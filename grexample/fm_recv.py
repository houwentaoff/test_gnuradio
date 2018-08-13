#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: GPL-3.0
#
##################################################
# GNU Radio Python Flow Graph
# Title: Fm Recv
# Generated: Mon Aug 13 17:36:35 2018
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
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import iio
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import sip
import sys
from gnuradio import qtgui


class fm_recv(gr.top_block, Qt.QWidget):

    def __init__(self, audio_device="dmix:CARD=monitor,DEV=0", decimation=1, fm_station=401100000, hostname='127.0.0.1', uri='192.168.2.1'):
        gr.top_block.__init__(self, "Fm Recv")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Fm Recv")
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

        self.settings = Qt.QSettings("GNU Radio", "fm_recv")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())


        ##################################################
        # Parameters
        ##################################################
        self.audio_device = audio_device
        self.decimation = decimation
        self.fm_station = fm_station
        self.hostname = hostname
        self.uri = uri

        ##################################################
        # Variables
        ##################################################
        self.sample_rate = sample_rate = 2304000

        ##################################################
        # Blocks
        ##################################################
        self.qtgui_sink_x_0 = qtgui.sink_f(
        	1024, #fftsize
        	firdes.WIN_BLACKMAN_hARRIS, #wintype
        	fm_station, #fc
        	200000, #bw
        	"", #name
        	True, #plotfreq
        	True, #plotwaterfall
        	True, #plottime
        	True, #plotconst
        )
        self.qtgui_sink_x_0.set_update_time(1.0/10)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_sink_x_0_win)

        self.qtgui_sink_x_0.enable_rf_freq(True)



        self.pluto_source_0 = iio.pluto_source('', fm_station, sample_rate, 20000, 0x20000, True, True, True, "manual", 64.0, '', True)
        self.low_pass_filter_0 = filter.fir_filter_ccf(sample_rate / (384000 * decimation), firdes.low_pass(
        	1, sample_rate / decimation, 200000, 20000, firdes.WIN_HAMMING, 6.76))
        self.audio_sink_0 = audio.sink(48000, '', True)
        self.analog_wfm_rcv_0 = analog.wfm_rcv(
        	quad_rate=384000,
        	audio_decimation=8,
        )



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_wfm_rcv_0, 0), (self.audio_sink_0, 0))
        self.connect((self.analog_wfm_rcv_0, 0), (self.qtgui_sink_x_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.analog_wfm_rcv_0, 0))
        self.connect((self.pluto_source_0, 0), (self.low_pass_filter_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "fm_recv")
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
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.sample_rate / self.decimation, 200000, 20000, firdes.WIN_HAMMING, 6.76))

    def get_fm_station(self):
        return self.fm_station

    def set_fm_station(self, fm_station):
        self.fm_station = fm_station
        self.qtgui_sink_x_0.set_frequency_range(self.fm_station, 200000)
        self.pluto_source_0.set_params(self.fm_station, self.sample_rate, 20000, True, True, True, "manual", 64.0, '', True)

    def get_hostname(self):
        return self.hostname

    def set_hostname(self, hostname):
        self.hostname = hostname

    def get_uri(self):
        return self.uri

    def set_uri(self, uri):
        self.uri = uri

    def get_sample_rate(self):
        return self.sample_rate

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        self.pluto_source_0.set_params(self.fm_station, self.sample_rate, 20000, True, True, True, "manual", 64.0, '', True)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.sample_rate / self.decimation, 200000, 20000, firdes.WIN_HAMMING, 6.76))


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
        "", "--uri", dest="uri", type="string", default='192.168.2.1',
        help="Set URI [default=%default]")
    return parser


def main(top_block_cls=fm_recv, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()
    if gr.enable_realtime_scheduling() != gr.RT_OK:
        print "Error: failed to enable real-time scheduling."

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(audio_device=options.audio_device, decimation=options.decimation, fm_station=options.fm_station, hostname=options.hostname, uri=options.uri)
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
