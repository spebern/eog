import fire
from recorder import Recorder
import random
import numpy as np
from enum import Enum
from pydub import AudioSegment
from pydub.playback import play
from preprocessing import Preprocessor
import time
import os
from record_animation import RecordApp
from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from mlxtend.feature_selection import SequentialFeatureSelector as SFS
from mlxtend.feature_selection import ExhaustiveFeatureSelector as EFS
from sklearn import svm
import matplotlib.pyplot as plt
import matplotlib


training_data_dir = "training_data/"


class EyeMovement(Enum):
    RIGHT = "right"
    LEFT = "left"
    UP = "up"
    DOWN = "down"


def gen_labels(trials, label_types):
    """
    Generate an array of length trials containing a random
    sequence of label types.
    """
    labels = (trials // (len(label_types) - 1)) * label_types[1:]
    while len(labels) < trials:
        labels.append(random.choice(label_types[1:]))
    random.shuffle(labels)

    relaxtion_label = label_types[0]
    labels_with_relaxation = []
    for label in labels:
        for _ in range(5):
            labels_with_relaxation.append(relaxtion_label)
        for _ in range(5):
            labels_with_relaxation.append(label)
    return labels_with_relaxation


class App(object):
    def __init__(self):
        self._preprocessor = Preprocessor()
        self._recorder = None

    def _init_recorder(self):
        recorder = Recorder()
        # recorder.start_recording()
        self._recorder = recorder

    def __del__(self):
        if self._recorder is not None:
            self._recorder.stop_offline_recording()

    def record(self, trials=10):
        self._init_recorder()
        recorder = self._recorder
        recorder.start_offline_recording()

        labels = gen_labels(trials, list(EyeMovement))

        app = RecordApp(recorder, labels)
        app.run()

    def train(self):
        pass

    def evaluate(self, trials=10):
        pass


def main():
    fire.Fire(App)


if __name__ == "__main__":
    main()
