import fire
from recorder import Recorder
import random
import numpy as np
from pydub import AudioSegment
from pydub.playback import play
from features import Preprocessor
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
from config import *
from utils import save_model, read_training_data
from sklearn.ensemble import RandomForestClassifier


training_data_dir = "training_data/"


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
        signals, labels = read_training_data()

        features = []
        for i in range(len(signals)):
            features.append(self._preprocessor.extract_features(signals[i]))
        features = np.array(features)

        # clf = LinearDiscriminantAnalysis()
        # clf = SVM()
        clf = RandomForestClassifier(n_estimators=100, max_depth=18, random_state=0)

        # fsl = EFS(
        #     clf, min_features=4, max_features=4, scoring="accuracy", print_progress=True
        # )
        fsl = SFS(
            clf,
            k_features=24,
            forward=True,
            floating=False,
            verbose=2,
            scoring="accuracy",
            n_jobs=-1,
            cv=4,
        )

        fsl.fit(features, labels)
        # print("Best accuracy score: %.2f" % fsl.best_score_)
        # print("Best subset (indices):", fsl.best_idx_)
        # print("Best subset (corresponding names):", fsl.best_feature_names_)

        # save_model(fsl)

    def evaluate(self, trials=10):
        pass


def main():
    fire.Fire(App)


if __name__ == "__main__":
    main()
