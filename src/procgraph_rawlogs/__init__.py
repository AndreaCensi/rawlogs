''' 
    This is a set of blocks to read from a Rawlog.
'''
from procgraph import import_succesful, import_magic
from procgraph import pg_add_this_package_models

from .read_rawlog import *
from .video_signal import *


procgraph_info = {
    # List of python packages 
    'requires': ['rawlogs']
}

pg_add_this_package_models(__file__, __package__)

