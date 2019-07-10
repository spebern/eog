from config import *
import numpy as np


class Preprocessor:
    def __init__(
        self, num_channels=NUM_CHANNELS, duration=1, fs=FS, win_size=0.2, win_shift=0.05
    ):
        self.fs = fs
        self.num_channels = num_channels
        self.duration = duration
        self.win_size = win_size
        self.win_shift = win_shift
        self.num_windows = int(self.duration / (self.win_size - self.win_shift))
        self.num_features = self.num_windows * 3

    def _extract_features_from_channel(self, signal):
        mav_features = np.zeros(self.num_windows)
        wl_features = np.zeros(self.num_windows)
        var_features = np.zeros(self.num_windows)

        for i in range(self.num_windows):
            start = int((i * (self.win_size - self.win_shift)) * self.fs)
            end = int(((i + 1) * self.win_size - i * self.win_shift) * self.fs)

            mav = np.mean(np.abs(signal[start:end]))
            wl = np.sum(np.abs(np.diff(signal[start:end])))
            var = np.var(signal[start:end])

            wl_features[i] = wl
            mav_features[i] = mav
            var_features[i] = var

        return mav_features, wl_features, var_features

    def extract_features(self, signals):
        features = np.zeros(self.num_channels * self.num_features)

        for i in range(self.num_channels):
            sigs = signals[:, i * 2] - signals[:, i * 2 + 1]
            mavs, wls, vars = self._extract_features_from_channel(sigs[:])
            features[
                i * self.num_features : (i + 1) * self.num_features
            ] = np.concatenate((mavs, wls, vars))

        return features
