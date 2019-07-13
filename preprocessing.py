from scipy.signal import butter, filtfilt, iirnotch
import numpy as np
import scipy
from config import *


class BandPassFilter:
    """
    EOG signal information is mainly contained in the low frequencies.
    (http://matrix.dte.us.es/grupotais/images/articulos/eogdir.pdf)
    """

    def __init__(self, lowcut=0.5, highcut=30, fs=FS, order=4):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        self.b, self.a = butter(order, [low, high], btype="band")

    def __call__(self, signal):
        return filtfilt(self.b, self.a, signal)


class BandStopFilter:
    def __init__(self, w0=0.9, Q=50):
        self.b, self.a = iirnotch(w0, Q)

    def __call__(self, signal):
        return filtfilt(self.b, self.a, signal)
