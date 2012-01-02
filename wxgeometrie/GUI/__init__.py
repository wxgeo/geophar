# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

#    WxGeometrie
#    Dynamic geometry, graph plotter, and more for french mathematic teachers.
#    Copyright (C) 2005-2010  Nicolas Pourcelot
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import traceback

import param

import sip
# PyQt new API (PyQt 4.6+)
sip.setapi('QDate', 2)
sip.setapi('QDateTime', 2)
sip.setapi('QString', 2)
sip.setapi('QTextStream', 2)
sip.setapi('QTime', 2)
sip.setapi('QUrl', 2)
sip.setapi('QVariant', 2)


try:
    import matplotlib
    matplotlib.use(param.moteur_de_rendu, warn = False)
    #import pylab # cette ligne semble n�cessaire sous Ubuntu Feisty (python 2.5 - matplotlib 0.87.7) ??
except Exception:
    print "Warning : Erreur lors de l'import de pylab.\n"
    if param.debug:
        print traceback.format_exc()


import wx

from .menu import MenuBar
from .panel import Panel_simple, Panel_API_graphique

# NB: Ne *PAS* importer modules.py ici (ou alors, modifier le script d'initialisation).
# En effet, la mise � jour des param�tres en fonction des pr�f�rences de l'utilisateur
# doit avoir lieu avant d'importer modules.py, qui lui-m�me utilise param.modules_actifs.
