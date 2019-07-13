from config import *
import numpy as np


def calc_pav(signal):
    return np.max(signal)

def calc_vav(signal):
    return np.max(signal)

def calc_auc(signal):
    return np.sum(np.abs(signal))

def calc_tcv(signal):
    tcv = 0
    prev = 0.0
    t = 3
    tm = -t
    for x in signal:
        if (x < t and prev > t) or (x > t and prev <= t):
            prev = x
            tcv += 1
        elif (x < tm and prev > tm) or (x > tm and prev <= tm):
            prev = x
            tcv += 1
    return float(tcv)

def calc_var(signal):
    return np.var(signal)

class Preprocessor:
    def __init__(self, num_channels=NUM_CHANNELS, duration=1, fs=FS):
        self.fs = fs
        self.num_channels = num_channels
        self.duration = duration
        self.num_features = 5

    def _extract_features_from_channel(self, signal):
        pav = calc_pav(signal)
        vav = calc_vav(signal)
        auc = calc_auc(signal)
        tcv = calc_tcv(signal)
        var = calc_var(signal)

        return np.array([pav, vav, auc, tcv, var])

    def extract_features(self, signals):
        features = np.zeros(self.num_channels * self.num_features)

        for i in range(self.num_channels):
            sigs = signals[:, i * 2] - signals[:, i * 2 + 1]
            # import matplotlib.pyplot as plt
            # plt.plot(sigs)
            # plt.show()
            features[
                i * self.num_features : (i + 1) * self.num_features
            ] = self._extract_features_from_channel(sigs[:])

        return features
