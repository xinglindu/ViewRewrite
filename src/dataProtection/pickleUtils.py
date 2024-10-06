import pickle


def pickle_write(data, path):
    with open(path, 'wb') as f:
        pickle.dump(data, f)


def pickle_read(path):
    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data
