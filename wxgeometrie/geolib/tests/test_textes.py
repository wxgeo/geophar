# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from geolib.tests.geotestlib import *

from geolib import Texte


def test_Texte():
    t = Texte("spam & eggs", rand(), rand())
    assert(t.texte == "spam & eggs")


