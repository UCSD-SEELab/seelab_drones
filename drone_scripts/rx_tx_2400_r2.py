#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Rx Tx 2400 R2
# Generated: Sun Mar 19 20:12:37 2017
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import math
import osmosdr
import time
import blade_rx


class rx_tx_2400_r2(gr.top_block):

    def __init__(self, center_freq=446500000, filename="_send.bin"):
        gr.top_block.__init__(self, "Rx Tx 2400 R2")

        ##################################################
        # Parameters
        ##################################################
        self.center_freq = center_freq
        self.filename = filename

        ##################################################
        # Variables
        ##################################################
        self.sps = sps = 10
        self.prefix = prefix = '/usr/share/adafruit/webide/repositories/bladerf/BladeRX/'
        self.baud_rate_tx = baud_rate_tx = 2490
        self.txvga2 = txvga2 = 25
        self.txvga1 = txvga1 = -4
        self.samp_rate_tx = samp_rate_tx = int(baud_rate_tx * sps)
        self.rx_vga_gain = rx_vga_gain = 35
        self.rx_lna_gain = rx_lna_gain = 6
        self.quad_gain = quad_gain = 8
        self.freq = freq = center_freq
        self.filepath = filepath = prefix + filename
        self.blade_samp_rate = blade_samp_rate = 400000
        self.baud_rate_rx = baud_rate_rx = 2530

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=blade_samp_rate,
                decimation=samp_rate_tx,
                taps=None,
                fractional_bw=None,
        )
        self.osmosdr_source_0 = osmosdr.source( args="numchan=" + str(1) + " " + "bladerf=0" )
        self.osmosdr_source_0.set_sample_rate(blade_samp_rate)
        self.osmosdr_source_0.set_center_freq(freq, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(1, 0)
        self.osmosdr_source_0.set_iq_balance_mode(1, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(rx_lna_gain, 0)
        self.osmosdr_source_0.set_if_gain(0, 0)
        self.osmosdr_source_0.set_bb_gain(rx_vga_gain, 0)
        self.osmosdr_source_0.set_antenna("", 0)
        self.osmosdr_source_0.set_bandwidth(0, 0)
          
        self.osmosdr_sink_0 = osmosdr.sink( args="numchan=" + str(1) + " " + "bladerf=0" )
        self.osmosdr_sink_0.set_sample_rate(blade_samp_rate)
        self.osmosdr_sink_0.set_center_freq(freq, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(txvga2, 0)
        self.osmosdr_sink_0.set_if_gain(0, 0)
        self.osmosdr_sink_0.set_bb_gain(txvga1, 0)
        self.osmosdr_sink_0.set_antenna("", 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)
          
        self.low_pass_filter_0 = filter.fir_filter_ccf(1, firdes.low_pass(
        	1, blade_samp_rate, 6000, 6000, firdes.WIN_HAMMING, 6.76))
        self.fir_filter_xxx_0 = filter.fir_filter_fff(16, (firdes.low_pass(1.0, baud_rate_rx*sps, baud_rate_rx, 0.25*baud_rate_rx)))
        self.fir_filter_xxx_0.declare_sample_delay(0)
        self.digital_pfb_clock_sync_xxx_0 = digital.pfb_clock_sync_fff(sps, 2*3.14159265/100, (firdes.low_pass(1.0, baud_rate_rx*sps, baud_rate_rx, 0.25*baud_rate_rx)), 32, 16, 1.5, 1)
        self.digital_gfsk_mod_0 = digital.gfsk_mod(
        	samples_per_symbol=sps,
        	sensitivity=1.0,
        	bt=1,
        	verbose=False,
        	log=False,
        )
        self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_char*1, filepath, True)
        self.blocks_file_sink_0_0 = blocks.file_sink(gr.sizeof_char*1, "/usr/share/adafruit/webide/repositories/bladerf/BladeRX/_out.bin", False)
        self.blocks_file_sink_0_0.set_unbuffered(True)
        self.blocks_add_const_vxx_0 = blocks.add_const_vff((0, ))
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(quad_gain)
        self.analog_pwr_squelch_xx_0 = analog.pwr_squelch_cc(-70, 1e-4, 0, True)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_pwr_squelch_xx_0, 0), (self.low_pass_filter_0, 0))    
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.blocks_add_const_vxx_0, 0))    
        self.connect((self.blocks_add_const_vxx_0, 0), (self.digital_pfb_clock_sync_xxx_0, 0))    
        self.connect((self.blocks_file_source_0, 0), (self.digital_gfsk_mod_0, 0))    
        self.connect((self.digital_binary_slicer_fb_0, 0), (self.blocks_file_sink_0_0, 0))    
        self.connect((self.digital_gfsk_mod_0, 0), (self.rational_resampler_xxx_0, 0))    
        self.connect((self.digital_pfb_clock_sync_xxx_0, 0), (self.fir_filter_xxx_0, 0))    
        self.connect((self.fir_filter_xxx_0, 0), (self.digital_binary_slicer_fb_0, 0))    
        self.connect((self.low_pass_filter_0, 0), (self.analog_quadrature_demod_cf_0, 0))    
        self.connect((self.osmosdr_source_0, 0), (self.analog_pwr_squelch_xx_0, 0))    
        self.connect((self.rational_resampler_xxx_0, 0), (self.osmosdr_sink_0, 0))    

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.set_freq(self.center_freq)

    def get_filename(self):
        return self.filename

    def set_filename(self, filename):
        self.filename = filename
        self.set_filepath(self.prefix + self.filename)

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.set_samp_rate_tx(int(self.baud_rate_tx * self.sps))
        self.fir_filter_xxx_0.set_taps((firdes.low_pass(1.0, self.baud_rate_rx*self.sps, self.baud_rate_rx, 0.25*self.baud_rate_rx)))
        self.digital_pfb_clock_sync_xxx_0.update_taps((firdes.low_pass(1.0, self.baud_rate_rx*self.sps, self.baud_rate_rx, 0.25*self.baud_rate_rx)))

    def get_prefix(self):
        return self.prefix

    def set_prefix(self, prefix):
        self.prefix = prefix
        self.set_filepath(self.prefix + self.filename)

    def get_baud_rate_tx(self):
        return self.baud_rate_tx

    def set_baud_rate_tx(self, baud_rate_tx):
        self.baud_rate_tx = baud_rate_tx
        self.set_samp_rate_tx(int(self.baud_rate_tx * self.sps))

    def get_txvga2(self):
        return self.txvga2

    def set_txvga2(self, txvga2):
        self.txvga2 = txvga2
        self.osmosdr_sink_0.set_gain(self.txvga2, 0)

    def get_txvga1(self):
        return self.txvga1

    def set_txvga1(self, txvga1):
        self.txvga1 = txvga1
        self.osmosdr_sink_0.set_bb_gain(self.txvga1, 0)

    def get_samp_rate_tx(self):
        return self.samp_rate_tx

    def set_samp_rate_tx(self, samp_rate_tx):
        self.samp_rate_tx = samp_rate_tx

    def get_rx_vga_gain(self):
        return self.rx_vga_gain

    def set_rx_vga_gain(self, rx_vga_gain):
        self.rx_vga_gain = rx_vga_gain
        self.osmosdr_source_0.set_bb_gain(self.rx_vga_gain, 0)

    def get_rx_lna_gain(self):
        return self.rx_lna_gain

    def set_rx_lna_gain(self, rx_lna_gain):
        self.rx_lna_gain = rx_lna_gain
        self.osmosdr_source_0.set_gain(self.rx_lna_gain, 0)

    def get_quad_gain(self):
        return self.quad_gain

    def set_quad_gain(self, quad_gain):
        self.quad_gain = quad_gain
        self.analog_quadrature_demod_cf_0.set_gain(self.quad_gain)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.osmosdr_sink_0.set_center_freq(self.freq, 0)
        self.osmosdr_source_0.set_center_freq(self.freq, 0)

    def get_filepath(self):
        return self.filepath

    def set_filepath(self, filepath):
        self.filepath = filepath
        self.blocks_file_source_0.open(self.filepath, True)

    def get_blade_samp_rate(self):
        return self.blade_samp_rate

    def set_blade_samp_rate(self, blade_samp_rate):
        self.blade_samp_rate = blade_samp_rate
        self.osmosdr_sink_0.set_sample_rate(self.blade_samp_rate)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.blade_samp_rate, 6000, 6000, firdes.WIN_HAMMING, 6.76))
        self.osmosdr_source_0.set_sample_rate(self.blade_samp_rate)

    def get_baud_rate_rx(self):
        return self.baud_rate_rx

    def set_baud_rate_rx(self, baud_rate_rx):
        self.baud_rate_rx = baud_rate_rx
        self.fir_filter_xxx_0.set_taps((firdes.low_pass(1.0, self.baud_rate_rx*self.sps, self.baud_rate_rx, 0.25*self.baud_rate_rx)))
        self.digital_pfb_clock_sync_xxx_0.update_taps((firdes.low_pass(1.0, self.baud_rate_rx*self.sps, self.baud_rate_rx, 0.25*self.baud_rate_rx)))


def argument_parser():
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    parser.add_option(
        "-f", "--center-freq", dest="center_freq", type="intx", default=446500000,
        help="Set center_freq [default=%default]")
    parser.add_option(
        "-n", "--filename", dest="filename", type="string", default="_send.bin",
        help="Set filename [default=%default]")
    return parser


def main(top_block_cls=rx_tx_2400_r2, options=None):
    blade_rx.blade_rf_sdr(1).load_fpga(True)
    if options is None:
        options, _ = argument_parser().parse_args()

    tb = top_block_cls(center_freq=options.center_freq, filename=options.filename)
    tb.start()
    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
