from . import internet
from . import pyutils as util
from . import pmath as math
from . import obsolete
__version__ = "0.1.0"
__author__ = "dank_meme#0210"

def init_pgutils():
    global pgutils
    from . import pgutils
    return pgutils

def init_cpplib():
    global cpplib
    if util.is_64bit():
        from . import cpplib64 as cpplib
    else:
        from . import cpplib32 as cpplib
    return cpplib