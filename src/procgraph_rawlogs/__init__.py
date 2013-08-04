''' 
    This is a set of blocks to read from a Rawlog.
'''
from procgraph import import_succesful, import_magic

procgraph_info = {
    # List of python packages 
    'requires': ['rawlogs']
}

from procgraph import pg_add_this_package_models
pg_add_this_package_models(__file__, __package__)

from .read_rawlog import *

