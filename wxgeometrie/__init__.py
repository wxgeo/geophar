# -*- coding: utf-8 -*-
"""Regroupe la majorité des outils utiles à un professeur de mathématiques."""

from os.path import dirname, realpath, abspath
import sys
# XXX: Hack temporaire, permettant de préférer la version locale de sympy.
path = abspath(dirname(realpath(sys._getframe().f_code.co_filename)))
sys.path.insert(0, path)

from .param import version as __version__
from . import GUI # initialisation de la version de wx
from .geolib import *
