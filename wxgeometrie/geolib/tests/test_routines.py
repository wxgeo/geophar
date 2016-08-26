# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from random import random
import math

from tools.testlib import assertAlmostEqual, assertEqual, assertNotAlmostEqual

from wxgeometrie.geolib.routines import (strip_trailing_zeros,)
from wxgeometrie.mathlib.universal_functions import sin as u_sin, cos as u_cos, tan as u_tan


def test_strip_trailing_zeros():
    assertEqual(strip_trailing_zeros('.0450*1.54556000+4.2003+a.e00+.003+4.000'), '.045*1.54556+4.2003+a.e00+.003+4')

