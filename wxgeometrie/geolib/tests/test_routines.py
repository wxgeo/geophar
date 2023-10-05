# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

from random import random
import math

import tools.unittest
from wxgeometrie.geolib.routines import (strip_trailing_zeros,)
from wxgeometrie.mathlib.universal_functions import sin as u_sin, cos as u_cos, tan as u_tan

class GeolibTest(tools.unittest.TestCase):
    def test_strip_trailing_zeros(self):
        self.assertEqual(
            strip_trailing_zeros('.0450*1.54556000+4.2003+a.e00+.003+4.000'),
            '.045*1.54556+4.2003+a.e00+.003+4')

