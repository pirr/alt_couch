import yaml, os
from alt.dict_ import dict_

def read(cfg_file=None):

    if not cfg_file:
        this_dir = os.path.dirname(__file__).replace('\\','/')
        main_pos = this_dir.rfind('/main/')
        if main_pos==-1:
            raise Exception('Can not find main dir')
        cfg_file = this_dir[:main_pos] + '/main/_cfg/main.cfg'

    with open(cfg_file) as f:
        cfg = yaml.load(f)
        
    return dict_(cfg)        