# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

mode_effectifs = 0 # 0: par défaut, 1: en pourcentages, 2: en fréquences
reglage_auto_fenetre = True
hachures = False
quantiles = {"mediane": [True, [0.5], 'r', '-'], \
             "quartiles": [True, [0.25, 0.75], 'b', '--'],\
             "deciles": [True, [0.1, 0.9], 'g', ':']}
