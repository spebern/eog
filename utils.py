import numpy as np
import os
import pickle
import time

TRAINING_DATA_DIR = "training_data/"
MODEL_DIR = "models/"


def read_training_data():
    labels = []
    signals = []
    for filename in sorted(os.listdir(TRAINING_DATA_DIR)):
        fullpath = os.path.join(TRAINING_DATA_DIR, filename)
        data = np.load(fullpath)
        # if data["label"] != "fist" and data["label"] != "normal":
        #     continue
        labels.append(data["label"])
        signals.append(data["signals"])
        # import math
        # bla = np.array(signals)
        # for s in bla.flatten():
        #     if math.isnan(s):
        #         print(fullpath)
        #         import sys
        #         sys.exit()
    signals = np.array(signals)
    return signals, labels


def save_model(model):
    pickle.dump(model, open(os.path.join(MODEL_DIR, "{}.p".format(time.time())), "wb"))
