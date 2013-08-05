__version__ = '1.0dev1'

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


from .interface import *
from .configuration import *
from .db import *
