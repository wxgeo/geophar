# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from tools.testlib import rand
from wxgeometrie.geolib import Texte


def test_Texte():
    t = Texte("spam & eggs", rand(), rand())
    assert(t.texte == "spam & eggs")
