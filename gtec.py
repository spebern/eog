#!/usb/bin/env python

# gtec.py
# Copyright (C) 2013  Bastian Venthur
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


# TODO: update to new version of pyusb

import struct
import time
import logging

import usb
from scipy.signal import iirfilter
import numpy as np

from libmushu.amplifier import Amplifier


logger = logging.getLogger(__name__)
logger.info('Logger started')

ID_VENDOR_GTEC = 0x153c
# I saw an am with this vendorid too
ID_VENDOR_GTEC2 = 0x15c3
ID_PRODUCT_GUSB_AMP = 0x0001

CX_OUT = usb.TYPE_VENDOR | usb.ENDPOINT_OUT

SUPPORTED_SAMPLING_FREQUENCIES = [
    32,
    64,
    256,
    512,
    1200,
    2400,
    4800,
    9600,
    19200,
    38400
]

SUPPORTED_BANDPASS_PARAMS = [
    (0.10, 0.0, 32, 8),
    (1.00, 0.0, 32, 8),
    (2.00, 0.0, 32, 8),
    (5.00, 0.0, 32, 8),
    (0.00, 15.0, 32, 8),
    (0.01, 15.0, 32, 8),
    (0.10, 15.0, 32, 8),
    (0.50, 15.0, 32, 8),
    (2.00, 15.0, 32, 8),
    (0.10, 0.0, 64, 8),
    (1.00, 0.0, 64, 8),
    (2.00, 0.0, 64, 8),
    (5.00, 0.0, 64, 8),
    (0.00, 30.0, 64, 8),
    (0.01, 30.0, 64, 8),
    (0.10, 30.0, 64, 8),
    (0.50, 30.0, 64, 8),
    (2.00, 30.0, 64, 8),
    (0.10, 0.0, 128, 8),
    (1.00, 0.0, 128, 8),
    (2.00, 0.0, 128, 8),
    (5.00, 0.0, 128, 8),
    (0.00, 30.0, 128, 8),
    (0.00, 60.0, 128, 8),
    (0.01, 30.0, 128, 8),
    (0.01, 60.0, 128, 8),
    (0.10, 30.0, 128, 8),
    (0.10, 60.0, 128, 8),
    (0.50, 30.0, 128, 8),
    (0.50, 60.0, 128, 8),
    (2.00, 30.0, 128, 8),
    (2.00, 60.0, 128, 8),
    (0.10, 0.0, 256, 8),
    (1.00, 0.0, 256, 8),
    (2.00, 0.0, 256, 8),
    (5.00, 0.0, 256, 8),
    (0.00, 30.0, 256, 8),
    (0.00, 60.0, 256, 8),
    (0.00, 100.0, 256, 8),
    (0.01, 30.0, 256, 6),
    (0.01, 60.0, 256, 8),
    (0.01, 100.0, 256, 8),
    (0.10, 30.0, 256, 8),
    (0.10, 60.0, 256, 8),
    (0.10, 100.0, 256, 8),
    (0.50, 30.0, 256, 8),
    (0.50, 60.0, 256, 8),
    (0.50, 100.0, 256, 8),
    (2.00, 30.0, 256, 8),
    (2.00, 60.0, 256, 8),
    (2.00, 100.0, 256, 8),
    (5.00, 30.0, 256, 8),
    (5.00, 60.0, 256, 8),
    (5.00, 100.0, 256, 8),
    (0.10, 0.0, 512, 8),
    (1.00, 0.0, 512, 8),
    (2.00, 0.0, 512, 8),
    (5.00, 0.0, 512, 8),
    (0.00, 30.0, 512, 8),
    (0.00, 60.0, 512, 8),
    (0.00, 100.0, 512, 8),
    (0.00, 200.0, 512, 8),
    (0.01, 30.0, 512, 6),
    (0.01, 60.0, 512, 6),
    (0.01, 100.0, 512, 6),
    (0.01, 200.0, 512, 8),
    (0.10, 30.0, 512, 8),
    (0.10, 60.0, 512, 8),
    (0.10, 100.0, 512, 8),
    (0.10, 200.0, 512, 8),
    (0.50, 30.0, 512, 8),
    (0.50, 60.0, 512, 8),
    (0.50, 100.0, 512, 8),
    (0.50, 200.0, 512, 8),
    (2.00, 30.0, 512, 8),
    (2.00, 60.0, 512, 8),
    (2.00, 100.0, 512, 8),
    (2.00, 200.0, 512, 8),
    (5.00, 30.0, 512, 8),
    (5.00, 60.0, 512, 8),
    (5.00, 100.0, 512, 8),
    (5.00, 200.0, 512, 8),
    (0.10, 0.0, 600, 8),
    (1.00, 0.0, 600, 8),
    (2.00, 0.0, 600, 8),
    (5.00, 0.0, 600, 8),
    (0.00, 30.0, 600, 8),
    (0.00, 60.0, 600, 8),
    (0.00, 100.0, 600, 8),
    (0.00, 200.0, 600, 8),
    (0.00, 250.0, 600, 8),
    (0.01, 60.0, 600, 6),
    (0.01, 100.0, 600, 6),
    (0.01, 200.0, 600, 6),
    (0.01, 250.0, 600, 8),
    (0.10, 60.0, 600, 8),
    (0.10, 100.0, 600, 8),
    (0.10, 200.0, 600, 8),
    (0.10, 250.0, 600, 8),
    (0.50, 30.0, 600, 8),
    (0.50, 60.0, 600, 8),
    (0.50, 100.0, 600, 8),
    (0.50, 200.0, 600, 8),
    (0.50, 250.0, 600, 8),
    (2.00, 30.0, 600, 8),
    (2.00, 60.0, 600, 8),
    (2.00, 100.0, 600, 8),
    (2.00, 200.0, 600, 8),
    (2.00, 250.0, 600, 8),
    (5.00, 30.0, 600, 8),
    (5.00, 60.0, 600, 8),
    (5.00, 100.0, 600, 8),
    (5.00, 200.0, 600, 8),
    (5.00, 250.0, 600, 8),
    (0.10, 0.0, 1200, 8),
    (1.00, 0.0, 1200, 8),
    (2.00, 0.0, 1200, 8),
    (5.00, 0.0, 1200, 8),
    (0.00, 30.0, 1200, 8),
    (0.00, 60.0, 1200, 8),
    (0.00, 100.0, 1200, 8),
    (0.00, 200.0, 1200, 8),
    (0.00, 250.0, 1200, 8),
    (0.00, 500.0, 1200, 8),
    (0.01, 100.0, 1200, 6),
    (0.01, 200.0, 1200, 6),
    (0.01, 250.0, 1200, 6),
    (0.01, 500.0, 1200, 6),
    (0.10, 100.0, 1200, 6),
    (0.10, 200.0, 1200, 8),
    (0.10, 250.0, 1200, 8),
    (0.10, 500.0, 1200, 8),
    (0.50, 100.0, 1200, 8),
    (0.50, 200.0, 1200, 8),
    (0.50, 250.0, 1200, 8),
    (0.50, 500.0, 1200, 8),
    (2.00, 100.0, 1200, 8),
    (2.00, 200.0, 1200, 8),
    (2.00, 250.0, 1200, 8),
    (2.00, 500.0, 1200, 8),
    (5.00, 100.0, 1200, 8),
    (5.00, 200.0, 1200, 8),
    (5.00, 250.0, 1200, 8),
    (5.00, 500.0, 1200, 8),
    (0.10, 0.0, 2400, 8),
    (1.00, 0.0, 2400, 8),
    (2.00, 0.0, 2400, 8),
    (5.00, 0.0, 2400, 8),
    (0.00, 30.0, 2400, 8),
    (0.00, 60.0, 2400, 8),
    (0.00, 100.0, 2400, 8),
    (0.00, 200.0, 2400, 8),
    (0.00, 250.0, 2400, 8),
    (0.00, 500.0, 2400, 8),
    (0.00, 1000.0, 2400, 8),
    (0.01, 200.0, 2400, 4),
    (0.01, 250.0, 2400, 6),
    (0.01, 500.0, 2400, 6),
    (0.01, 1000.0, 2400, 6),
    (0.10, 200.0, 2400, 6),
    (0.10, 250.0, 2400, 6),
    (0.10, 500.0, 2400, 8),
    (0.10, 1000.0, 2400, 8),
    (0.50, 200.0, 2400, 8),
    (0.50, 250.0, 2400, 8),
    (0.50, 500.0, 2400, 8),
    (0.50, 1000.0, 2400, 8),
    (2.00, 200.0, 2400, 8),
    (2.00, 250.0, 2400, 8),
    (2.00, 500.0, 2400, 8),
    (2.00, 1000.0, 2400, 8),
    (5.00, 200.0, 2400, 8),
    (5.00, 250.0, 2400, 8),
    (5.00, 500.0, 2400, 8),
    (5.00, 1000.0, 2400, 8),
    (0.10, 0.0, 4800, 6),
    (1.00, 0.0, 4800, 8),
    (2.00, 0.0, 4800, 8),
    (5.00, 0.0, 4800, 8),
    (0.00, 30.0, 4800, 8),
    (0.00, 60.0, 4800, 8),
    (0.00, 100.0, 4800, 8),
    (0.00, 200.0, 4800, 8),
    (0.00, 250.0, 4800, 8),
    (0.00, 500.0, 4800, 8),
    (0.00, 1000.0, 4800, 8),
    (0.00, 2000.0, 4800, 8),
    (0.01, 500.0, 4800, 6),
    (0.01, 1000.0, 4800, 6),
    (0.01, 2000.0, 4800, 6),
    (0.10, 500.0, 4800, 6),
    (0.10, 1000.0, 4800, 6),
    (0.10, 2000.0, 4800, 8),
    (0.50, 500.0, 4800, 8),
    (0.50, 1000.0, 4800, 8),
    (0.50, 2000.0, 4800, 8),
    (2.00, 500.0, 4800, 8),
    (2.00, 1000.0, 4800, 8),
    (2.00, 2000.0, 4800, 8),
    (5.00, 500.0, 4800, 8),
    (5.00, 1000.0, 4800, 8),
    (5.00, 2000.0, 4800, 8)
]

SUPPORTED_NOTCHFILTER_PARAMS = [
    (48.00, 52.0, 128, 4),
    (58.00, 62.0, 128, 4),
    (48.00, 52.0, 256, 4),
    (58.00, 62.0, 256, 4),
    (48.00, 52.0, 512, 4),
    (58.00, 62.0, 512, 4),
    (48.00, 52.0, 600, 4),
    (58.00, 62.0, 600, 4),
    (48.00, 52.0, 1200, 4),
    (58.00, 62.0, 1200, 4),
    (48.00, 52.0, 2400, 4),
    (58.00, 62.0, 2400, 4),
    (48.00, 52.0, 4800, 4),
    (58.00, 62.0, 4800, 4)
]


class GUSBamp(Amplifier):

    def __init__(self):
        logger.info('Initializing GUSBamp instance')
        # list of available amps
        self.amps = []
        for bus in usb.busses():
            for device in bus.devices:
                if (device.idVendor in [ID_VENDOR_GTEC, ID_VENDOR_GTEC2] and
                    device.idProduct == ID_PRODUCT_GUSB_AMP):
                    self.amps.append(device)
        self.devh = None
        self.mode = None
        # Initialize the amplifier and make it ready.
        device = self.amps[0]
        self.devh = device.open()
        # detach kernel driver if nessecairy
        config = device.configurations[0]
        self.devh.setConfiguration(config)
        assert(len(config.interfaces) > 0)
        # sometimes it is the other one
        first_interface = config.interfaces[0][0]
        if first_interface is None:
            first_interface = config.interfaces[0][1]
        first_setting = first_interface.alternateSetting
        self.devh.claimInterface(first_interface)
        self.devh.setAltInterface(first_interface)
        # initialization straight from the usb-dump
        self.set_mode('data')
        self.devh.controlMsg(CX_OUT, 0xb6, value=0x80, buffer=0)
        self.devh.controlMsg(CX_OUT, 0xb5, value=0x80, buffer=0)
        self.devh.controlMsg(CX_OUT, 0xb9, value=0x00, buffer=b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10')
        self.set_slave_mode(False)
        self.devh.controlMsg(CX_OUT, 0xd3, value=0x01, buffer=0)
        self.devh.controlMsg(CX_OUT, 0xca, value=0x01, buffer=0)
        self.devh.controlMsg(CX_OUT, 0xc8, value=0x01, buffer=b'\x00'*16)
        self.set_common_reference()
        self.set_common_ground()
        self.set_calibration_mode('sine')
        self.fs = None
        self.set_sampling_frequency(1200, [False for i in range(16)], None, None)
        self.devh.setAltInterface(1)


    def start(self):
        self.devh.controlMsg(CX_OUT, 0xb5, value=0x08, buffer=0)
        self.devh.controlMsg(CX_OUT, 0xf7, value=0x00, buffer=0)

    def stop(self):
        self.devh.controlMsg(CX_OUT, 0xb8, [])

    def get_data(self):
        """Get data."""
        # TODO: should we use numpy arrays right here?
        # TODO: what is the in-endpoint
        # 0x2 or 0x86
        endpoint = 0x86
        # TODO what is the optimal number here
        size = 2028 #512
        try:
            # TODO what is the optimal timeout here?
            data = self.devh.bulkRead(endpoint, size, 100)
        except usb.USBError as e:
            logger.error("Got usb error: {}".format(e))
            data = []
        data = np.frombuffer(data, np.float32, len(data) // 4)
        try:
            data = data.reshape(-1, 17)
        except:
            logger.error("Got incomplete packet from the amp, discarding it!")
            data = np.array([]).reshape(-1, 17)
        if self.mode == 'impedance':
            data = self.calculate_impedance(data)
        elif self.mode == 'data':
            # get data in mV
            data /= 8.15
        return data, []

    def get_channels(self):
        return [str(i) for i in range(17)]

    @staticmethod
    def is_available():
        for bus in usb.busses():
            for device in bus.devices:
                if (device.idVendor in [ID_VENDOR_GTEC, ID_VENDOR_GTEC2] and
                    device.idProduct == ID_PRODUCT_GUSB_AMP):
                    return True
        return False

    ###########################################################################
    # Low level amplifier methods
    ###########################################################################

    def set_mode(self, mode):
        """Set mode, 'impedance', 'data'."""
        if mode == 'impedance':
            self.devh.controlMsg(CX_OUT, 0xc9, value=0x00, buffer=0)
            self.devh.controlMsg(CX_OUT, 0xc2, value=0x03, buffer=0)
            self.mode = 'impedance'
        elif mode == 'calibrate':
            self.devh.controlMsg(CX_OUT, 0xc1, value=0x00, buffer=0)
            self.devh.controlMsg(CX_OUT, 0xc2, value=0x02, buffer=0)
            self.mode = 'calibration'
        elif mode == 'data':
            self.devh.controlMsg(CX_OUT, 0xc0, value=0x00, buffer=0)
            self.devh.controlMsg(CX_OUT, 0xc2, value=0x01, buffer=0)
            self.mode = 'data'
        else:
            raise AmpError('Unknown mode: %s' % mode)


    def set_sampling_frequency(self, fs, channels, bpfilter, notchfilter):
        """ Set the sampling frequency and filters for individual channels.

        Parameters:
        fs -- sampling frequency
        channels -- list of booleans: channels[0] == True: enable filter for channel 0
        bpfilter -- tuple: parameters for the band pass filter (hp, lp, fs, order) or None
        notchfilter -- tuple: parameters for the band stop filter (hp, lp, fs, order) or None

        """
        if fs not in SUPPORTED_SAMPLING_FREQUENCIES:
            raise Exception(
                "Sampling frequency {} not supported. Please choose among: {}".format(
                    fs,
                    SUPPORTED_SAMPLING_FREQUENCIES
                )
            )

        if bpfilter is not None and bpfilter not in SUPPORTED_BANDPASS_PARAMS:
            raise Exception(
                "Bandpass params {} not supported. Please choose among: {}".format(
                    bpfilter,
                    SUPPORTED_BANDPASS_PARAMS
                )
            )

        if notchfilter is not None and notchfilter not in SUPPORTED_NOTCHFILTER_PARAMS:
            raise Exception(
                "Notchfilter params {} not supported. Please choose among: {}".format(
                    bpfilter,
                    SUPPORTED_NOTCHFILTER_PARAMS
                )
            )

        # we have: hp, lp, fs, order, typ
        # signal.iirfilter(order/2, [hp/(fs/2), lp/(fs/2)], ftype='butter', btype='band')
        # we get 18 coeffs and put them in as '<d' in the buffer
        # struct.pack('<'+'d'*18, *coeffs)

        # special filter: means no filter
        null_filter = b'\x00\x00\x00\x00\x00\x00\xf0\x3f'+b'\x00\x00\x00\x00\x00\x00\x00\x00'*17

        if bpfilter:
            bp_hp, bp_lp, bp_fs, bp_order = bpfilter
            bp_b, bp_a = iirfilter(bp_order/2, [bp_hp/(bp_fs/2), bp_lp/(bp_fs/2)], ftype='butter', btype='band')
            # bp_filter = list(bp_b)
            # bp_filter.extend(list(bp_a))
            # if len(bp_filter) < 18:
            #     diff = 18 - len(bp_filter)
            #     bp_filter.extend([0.0 for i in range(diff)])
            print(bp_b)
            bp_filter = []
            for _ in range(18):
                bp_filter.append(1)
            bp_filter = struct.pack("<"+"d"*18, *bp_filter)
        else:
            bp_filter = null_filter

        if notchfilter:
            bs_hp, bs_lp, bs_fs, bs_order = notchfilter
            bs_b, bs_a = iirfilter(bs_order/2, [bs_hp/(bs_fs/2), bs_lp/(bs_fs/2)], ftype='butter', btype='bandstop')
            bs_filter = list(bs_b)
            # the notch filter has (always?) an order of 4 so fill the gaps with
            # zeros
            if len(bs_filter) < 9:
                diff = 9 - len(bs_filter)
                bs_filter.extend([0.0 for i in range(diff)])
            bs_filter.extend(list(bs_a))
            if len(bs_filter) < 18:
                diff = 18 - len(bs_filter)
                bs_filter.extend([0.0 for i in range(diff)])
            bs_filter = struct.pack("<"+"d"*18, *bs_filter)
        else:
            bs_filter = null_filter

        # set the filters for all channels
        if bpfilter == notchfilter == None:
            self.devh.controlMsg(CX_OUT, 0xc6, value=0x01, buffer=bp_filter)
            self.devh.controlMsg(CX_OUT, 0xc7, value=0x01, buffer=bs_filter)
        else:
            idx = 1
            for i in channels:
                if i:
                    self.devh.controlMsg(CX_OUT, 0xc6, value=idx, buffer=bp_filter)
                    self.devh.controlMsg(CX_OUT, 0xc7, value=idx, buffer=bs_filter)
                idx += 1

        # set the sampling frequency
        self.devh.controlMsg(CX_OUT, 0xb6, value=fs, buffer=0)
        self.fs = fs

    def get_sampling_frequency(self):
        """ Get the sampling frequency. """
        return self.fs

    def set_calibration_mode(self, mode):
        # buffer: [0x03, 0xd0, 0x07, 0x02, 0x00, 0xff, 0x07]
        #          ====  ==========
        # (1) mode:
        # (2) amplitude: little endian (0x07d0 = 2000)
        if mode == 'sine':
            self.devh.controlMsg(CX_OUT, 0xcb, value=0x00, buffer=b'\x03\xd0\x07\x02\x00\xff\x07')
        elif mode == 'sawtooth':
            self.devh.controlMsg(CX_OUT, 0xcb, value=0x00, buffer=b'\x02\xd0\x07\x02\x00\xff\x07')
        elif mode == 'whitenoise':
            self.devh.controlMsg(CX_OUT, 0xcb, value=0x00, buffer=b'\x05\xd0\x07\x02\x00\xff\x07')
        elif mode == 'square':
            self.devh.controlMsg(CX_OUT, 0xcb, value=0x00, buffer=b'\x01\xd0\x07\x02\x00\xff\x07')
        else:
            raise AmpError('Unknown mode: %s' % mode)

    def calculate_impedance(self, u_measured, u_applied=1e4):
        return (u_measured * 1e6) / (u_applied - u_measured) - 1e4


    def set_common_ground(self, a=False, b=False, c=False, d=False):
        """Set common ground for the electrodes.

        Parameters:
            a, b, c, d -- correspond to the groups on the amp, either of them
                can be true or false

        """
        v = (d << 3) + (c << 2) + (b << 1) + a
        self.devh.controlMsg(CX_OUT, 0xbe, value=v, buffer=0)


    def set_common_reference(self, a=False, b=False, c=False, d=False):
        """Set common reference for the electrodes.

        Parameters:
            a, b, c, d -- correspond to the groups on the amp, either of them
                can be true or false

        """
        v = (d << 3) + (c << 2) + (b << 1) + a
        self.devh.controlMsg(CX_OUT, 0xbf, value=v, buffer=0)


    def set_slave_mode(self, slave):
        """Set amp into slave or master mode.

        Parameters:
            slave -- if true, set into slave mode, set to master otherwise

        """
        v = 1 if slave else 0
        self.devh.controlMsg(CX_OUT, 0xcd, value=v, buffer=0)


class AmpError(Exception):
    pass



def main():
    amp = GUSBamp()
    amp.start()

    num_samples = 0
    start = time.time()
    for i in range(100):
        data, _ = amp.get_data()
        num_samples += data.shape[0]
    fs = num_samples / (time.time() -start)
    print(fs)
    amp.stop()

if __name__ == '__main__':
    import sys
    import cProfile
    if len(sys.argv) > 1 and sys.argv[1].startswith('prof'):
        cProfile.run('main()', 'prof')
    else:
        main()
