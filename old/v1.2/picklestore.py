import pickle


def read_pk(fn):
    result = None
    with fn.open('rb') as fd:
        result = pickle.load(fd)
    return result


def write_pk(obj, fn):
    with fn.open('wb') as fd:
        pickle.dump(obj, fd)
 
