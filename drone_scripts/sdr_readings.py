'''
For use with Nuand BladeRF. This script will scan the frequencies listed in fc
list and perform basic statistics to estimate which channel has the lowest
utilization. It will return the channel to use and the data it scanned.

We will be using 440 MHz, 925 MHz, and 1270 MHz to talk on since these are in
HAM or ISM bands.

NOTE: You must have a HAM radio license to do any transmitting!
'''

# import rtlsdr as rtl
import blade_rx as blade
import numpy as np
from time import sleep
import time
import threading
from pubsub import pub

SAVE = False
DATABASE = True
FILENAME = "blade_2_5mhz.txt"

mhz = 1000000.0
khz = 1000.0
RX_MIN_FREQ = 300 * mhz
np.set_printoptions(precision=4)

fcLow = 100
fcHigh = 200
fs = 0.4                                     # 0.4 MHz, 400 kHz
f1 = 440
f2 = 925
f3 = 1270
fc = f1                                      # default frequency in MHz
lnagain = 6
rxvga1 = 30
rxvga2 = 30
txvga1 = -4
txvga2 = 25
NFFT = 1024
NUM_DECIMAL = 3
SCAN_RES = 1

# rxSDR is an old name used for the rtl. Change it if you want future person
class rxSDR(threading.Thread):

    def __init__(self):
        super(rxSDR, self).__init__()
        self._delay = 10
        self.daemon = True
        # Configure SDR parameters
        self.sdr = blade.blade_rf_sdr(1)         # init bladeRF, load FPGA
        self.setGainDefaults()
        # self.setFc(fc, 'mhz', 'rx')
        self.setFs(fs, 'mhz')
        
        self.start()

    '''
    Probs dont need this
    def setBwKhz(self, bw_khz):     # does not work for some reason?
        self.sdr.set_bandwidth(bw_khz*khz)
    '''

    def setGainDefaults(self): # input gain in dB, "auto" by default
        gain_list = ['lnagain', 'rxvga1', 'rxvga2', 'txvga1', 'txvga2']
        gain_vals = [lnagain, rxvga1, rxvga2, txvga1, txvga2]
        self.sdr.set_amplifier_gain(gain_list, gain_vals)

    '''
    Probs dont need this
    def getGain(self):                   # get tuner gain in dB
        return self.sdr.get_gain()

    def getGains(self, unit = ".1dB"):  # default to output in 0.1dB
        gains = self.sdr.get_gains()
        if (unit == "dB"):
            gainsdB = [i / 10.0 for i in gains]
            return gainsdB
        else: return gains

    def printGain(self):
        print("gain=" + str(self.getGain()) + " dB")

    def printGains(self, unit = ".1dB"):   # print out gains. defaults to 0.1dB
        gains = self.getGains(unit)
        if (unit == "dB"):
            print("gains (dB):" + "\n" + str(gains))
        else: print("gains (0.1dB): " + "\n" + str(gains))
    '''

    def setFc(self, Fc, unit = "mhz", mode='rx'):
        '''Auto converted to MHz later so pass in MHz now. This is messy I'll
        clean it up if I have time'''
        '''
        if (unit == "hz"):             Fc = Fc
        elif (unit == "khz"):          Fc = Fc * khz
        else:                          Fc = Fc * mhz
        '''
        if (Fc < (RX_MIN_FREQ / mhz)):
            print("Error. Fc too low. Setting to " + str(RX_MIN_FREQ))
            Fc = RX_MIN_FREQ / mhz

        self.sdr.set_center_freq(mode, Fc)

    '''
    Probs don't need this
    def getFc(self, unit = "mhz"):      # get center frequency. defaults to mhz
        freq_hz = self.sdr.get_center_freq()
        if (unit == "hz"):      return freq_hz
        elif (unit == "khz"):   return freq_hz / khz
        else:                   return freq_hz / mhz

    def printFc(self, unit = "mhz"):
        if ((unit != "khz") and (unit != "hz")): unit = "mhz"
        print("Fc=" + str(self.getFc(unit)) + " " + unit)
    '''

    def setFs(self, Fs, unit = "hz"):     # default to Hz
        '''This should be good to go. Sloppy for now'''
        # if (unit == "khz"): self.sdr.set_sample_rate(Fs * khz)
        # elif (unit == "mhz"): self.sdr.set_sample_rate(Fs * mhz)
        # else: self.sdr.set_sample_rate(Fs)
        self.sdr.set_sample_rate(Fs)

    '''
    Probs don't need this:
    def getFs(self, unit):          # get sample rate. defaults to mhz
        freq_hz = self.sdr.get_sample_rate()
        if (unit == "hz"): return freq_hz
        elif (unit == "khz"): return freq_hz / khz
        else: return freq_hz / mhz

    def printFs(self, unit):
        if ((unit != "hz") and (unit != "khz")): unit = "mhz"
        print("Fs=" + str(self.getFs(unit)) + " " + unit)
    '''

    def getFrequencies(self, nfft):
        '''This should be properly updated. Report back after test'''
        # Get width number of raw samples so the number of frequency bins is
		# the same as the display width.  Add two because there will be mean/DC
		# values in the results which are ignored.
        filename = '/usr/share/adafruit/webide/repositories/seelab_drones/database_files/trial.csv'
        samples = self.sdr.rx_samples('1K', 'csv', filename)
        hw_time = np.hamming(nfft)
        # fft and take abs() to get frequency bin magnitudes
        freqs = np.absolute(np.fft.fft(np.multiply(samples, hw_time)))
        # ignore the mea/DC values at the ends
        # freqs = freqs[1:-1]
        # fftshift to have 0 freqs at center
        freqs = np.fft.fftshift(freqs)
        # convert to  dB
        freqs = 20.0*np.log10(freqs)
        return freqs
    
    def _callback(self, sdr_data):
        '''Send SDR scan data to subscribers'''
        pub.sendMessage("sensor-messages.sdr-data", arg1=sdr_data)
    
    def get_average(data)
    
    def get_reading(self, fc_list):
        '''
        This function tests features that I add to the rxSDR class
        '''

        if SAVE:
            with open(FILENAME, 'a') as file:
                file.write('fs,%f,mhz,nfft,%d'%(fs,NFFT)+'\n')
        now = time.time()
        i = 0
        data = []
        # store best channel data in form [avg of fft, frequency in MHz]
        best_channel = [3000, fc]
        
        for x in fc_list:
            data.append([])
            self.setFc(x, 'mhz', 'rx')
            
            if ((time.time() - now) < 0.025): time.sleep(0.025 - (time.time()-now)) # allow PLL to settle
            
            freqs = self.getFrequencies(NFFT)
            
            if SAVE:
                with open(FILENAME, 'a') as f:
                    f.write(','.join(map(str, np.round(freqs, NUM_DECIMAL))) + '\n')
            if DATABASE:
                params = ['freq',x,'fs',fs,'mhz','nfft',NFFT]
                freqs = freqs.tolist()
                freqs.insert(0, params)
            
            data[i].append(freqs)
            i = i + 1
            fft_avg = sum(freqs) / float(len(freqs))
            if fft_avg < best_channel[0]:
                best_channel[0] = fft_avg
                best_channel[1] = x
                print('Should change to ' + str(x) + 'MHz')
        
        print("Scan required " + str(time.time() - now) + " seconds")
        return data

    
    def run(self):
        # fc_list = np.linspace(fcLow, fcHigh, ((fcHigh - fcLow)/(SCAN_RES*fs) + 1))
        fc_list = [f1, f2, f3]
        while True:
            data = self.get_reading(fc_list)  # get the frequency data
            if data is not None:                     # if successful
                self._callback(data)                 # send the data to be logged
            time.sleep(self._delay)