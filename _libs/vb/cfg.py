import os

def main_dir():

    dir_ = os.path.dirname(__file__).replace('\\', '/')
    pos = dir_.rfind('/main/')
    if pos == -1:
        raise Exception('No main dir')
    dir_ = dir_[:pos] + '/main/'

    return dir_
