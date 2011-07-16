from os.path import split, realpath, abspath
import sys
# XXX: Hack temporaire, permettant de trouver sympy.
sys.path.append(abspath(split(realpath(sys._getframe().f_code.co_filename))[0]))

from .param import version as __version__
from .geolib import *
