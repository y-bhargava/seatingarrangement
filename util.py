import pickle
import os


def load_pickle(fname):
    if not os.path.exists(fname):
        return None, 'Roll Number File: {} does not exist'.format(fname)
    with open(fname, 'rb') as fid:
        return pickle.load(fid), None


def save_pickle(fname, dat):
    with open(fname, 'wb') as fid:
        return pickle.dump(dat, fid), None
