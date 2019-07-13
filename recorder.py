import numpy as np
import threading
import queue
import time
import gtec
import matplotlib.pyplot as plt
from config import *


class Recorder:
    def __init__(self, fs=FS, win_duration=WIN_DURATION, num_channels=NUM_CHANNELS * 2):

        self._stop = False
        self.fs = fs
        self.win_duration = win_duration
        self.num_channels = num_channels
        self.labels = queue.Queue()

        self.amp = gtec.GUSBamp()
        self.amp.set_sampling_frequency(
            self.fs, [True for i in range(16)], None, (48, 52, FS, 4)
        )
        self.amp.start()

    def start_offline_recording(self, live=True):
        """
        Start a thread for recording.
        """
        threading.Thread(target=self._record).start()

    def stop_offline_recording(self):
        """
        Terminate the recording thread.
        """
        self._stop = True

    def get_data(self):
        """
        Get data for the duratoin of the previously defined win_duration.
        """
        return self.read_sample_win()

    def read_sample_win(self, label=None):
        num_samples = self.win_duration * self.fs
        sample_win = np.zeros((num_samples, self.num_channels))

        # start sampling
        num_collected_samples = 0
        sampling = True
        while sampling:
            signals, _ = self.amp.get_data()
            for i_sample in range(signals.shape[0]):
                sample_win[num_collected_samples][0] = signals[i_sample][0]
                sample_win[num_collected_samples][1] = signals[i_sample][1]
                sample_win[num_collected_samples][2] = signals[i_sample][2]
                sample_win[num_collected_samples][3] = signals[i_sample][3]
                num_collected_samples += 1
                if num_collected_samples == num_samples:
                    sampling = False
                    break

        return sample_win

    def record_label(self, label):
        self.labels.put(label)

    def _record(self):
        while not self._stop:
            label = self.labels.get()
            signals = self.read_sample_win(label)

            np.savez(
                "training_data/{}_{}.npz".format(label, time.time()),
                signals=signals,
                label=label.value,
            )


def main():
    recorder = Recorder(win_duration=2)
    raw_data = recorder.get_data()

    raw_data = recorder.get_data()

    bp = BandPassFilter()
    for channel in range(raw_data.shape[1]):
        raw_data[:, channel] = bp(raw_data[:, channel])

    # fig = plt.figure(figsize=(12, 10))
    # ax1 = fig.add_subplot(6, 1, 1)
    # ax1.set_title("EOG signal channel 1")
    # ax1.set_xlabel("samples")
    # ax1.set_ylabel("voltage")
    # ax1.plot(raw_data[2 * FS :, 0])

    # ax2 = fig.add_subplot(6, 1, 2)
    # ax2.set_title("EOG signal channel 2")
    # ax2.set_xlabel("samples")
    # ax2.set_ylabel("voltage")
    # ax2.plot(raw_data[2 * FS :, 1])

    # ax3 = fig.add_subplot(6, 1, 3)
    # ax3.set_title("EOG signal channel 3")
    # ax3.set_xlabel("samples")
    # ax3.set_ylabel("voltage")
    # ax3.plot(raw_data[2 * FS :, 2])

    # ax4 = fig.add_subplot(6, 1, 4)
    # ax4.set_title("EOG signal channel 4")
    # ax4.set_xlabel("samples")
    # ax4.set_ylabel("voltage")
    # ax4.plot(raw_data[2 * FS :, 3])

    # ax2 = fig.add_subplot(6, 1, 5)
    # ax2.set_title("EOG signal channel 2 - channel 1")
    # ax2.set_xlabel("samples")
    # ax2.set_ylabel("voltage")
    # ax2.plot(raw_data[2 * FS :, 1] - raw_data[2 * FS :, 0])

    # ax2 = fig.add_subplot(6, 1, 6)
    # ax2.set_title("EOG signal channel 4 - channel 3")
    # ax2.set_xlabel("samples")
    # ax2.set_ylabel("voltage")
    # ax2.plot(raw_data[2 * FS :, 3] - raw_data[2 * FS :, 2])
    fig = plt.figure(figsize=(12, 10))
    ax2 = fig.add_subplot(2, 1, 1)
    ax2.set_title("EOG signal channel 2 - channel 1")
    ax2.set_xlabel("samples")
    ax2.set_ylabel("voltage")
    ax2.plot(raw_data[:, 1] - raw_data[:, 0])

    ax2 = fig.add_subplot(2, 1, 2)
    ax2.set_title("EOG signal channel 4 - channel 3")
    ax2.set_xlabel("samples")
    ax2.set_ylabel("voltage")
    ax2.plot(raw_data[:, 3] - raw_data[:, 2])

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
