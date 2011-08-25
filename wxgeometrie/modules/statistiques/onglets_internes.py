# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

##------------------------------------------#######
#                   Satistiques                   #
##------------------------------------------#######
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

#from GUI import *

#from functools import partial

import wx


class CstmPanel(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.main = self.parent.parent
        self.setStyleSheet("background-color:white")
        self.main_sizer = QVBoxLayout()

    def finaliser(self):
        self.setLayout(self.main_sizer)
        self.adjustSize()

    def add(self, item):
        self.main_sizer.Add(item)


class Donnees(CstmPanel):
    def __init__(self, parent):
        CstmPanel.__init__(self, parent)
        sizer = QHBoxLayout()
        sizer.Add(QLabel(self, u"Effectifs et valeurs associées:  "), 0, wx.ALIGN_CENTER|wx.ALL, 5)
        self.valeurs = wx.TextCtrl(self, -1, self.main.donnees_valeurs, size=(500, -1), style=wx.TE_PROCESS_ENTER)
        aide = u"Valeurs simples:\n8 8 9 12 17 18\nEffectifs et valeurs:\n2*7 14*8 5*9 1*10\nClasses et effectifs:\n17*[0;10[ 24*[10;20["
        self.valeurs.setToolTip(aide)
        self.valeurs.Bind(wx.EVT_CHAR, self.main.EvtChar)
        sizer.Add(self.valeurs)
        self.add(sizer)

        sizer = QHBoxLayout()
        self.sc = QLabel(self, u"Regroupement par classes:  ")
        sizer.Add(self.sc)
        self.classes = wx.TextCtrl(self, -1, self.main.donnees_classes, size=(500, -1), style=wx.TE_PROCESS_ENTER)
        self.classes.setToolTip(u"Exemple:\n[0;10[ [10;20[ [20;30[")
        self.classes.Bind(wx.EVT_CHAR, self.main.EvtChar)
        sizer.Add(self.classes)
        self.add(sizer)

        self.finaliser()


class Legende(CstmPanel):
    def __init__(self, parent):
        CstmPanel.__init__(self, parent)
        # Légendes
        box = QGroupBox(self, -1, u"Légende des axes")
        sizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)

        self.sx = QLabel(self, u"Abscisses:")
        sizer.Add(self.sx)
        self.x = wx.TextCtrl(self, -1, self.main.legende_x, size=(200, -1), style=wx.TE_PROCESS_ENTER)
        self.x.Bind(wx.EVT_CHAR, self.main.EvtChar)
        sizer.Add(self.x)

        self.sy = QLabel(self, u"Ordonnées:")
        sizer.Add(self.sy)
        self.y = wx.TextCtrl(self, -1, self.main.legende_y, size=(200, -1), style=wx.TE_PROCESS_ENTER)
        self.y.Bind(wx.EVT_CHAR, self.main.EvtChar)
        sizer.Add(self.y)

        self.sa = QLabel(self, u"Aire:")
        sizer.Add(self.sa)
        self.a = wx.TextCtrl(self, -1, self.main.legende_a, size=(100, -1), style=wx.TE_PROCESS_ENTER)
        self.a.setToolTip(u"Pour les histogrammes.\nIndique en quelle unité s'exprime la quantité.\nExemples:\npersonnes, ampoules, %, $, ...")
        self.a.Bind(wx.EVT_CHAR, self.main.EvtChar)
        sizer.Add(self.a)
        self.add(sizer)

        self.finaliser()


class Graduation(CstmPanel):
    def __init__(self, parent):
        CstmPanel.__init__(self, parent)
        msizer = QHBoxLayout()
        # Graduations
        box = QGroupBox(self, -1, u"Taille d'une graduation")
        sizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)

        self.sx = QLabel(self, u"Abscisses:")
        sizer.Add(self.sx)
        self.x = wx.TextCtrl(self, -1, self.main.gradu_x, size=(50, -1), style=wx.TE_PROCESS_ENTER)
        self.x.setToolTip(u"Graduation en abscisses.")
        self.x.Bind(wx.EVT_CHAR, self.main.EvtChar)
        sizer.Add(self.x)

        self.sy = QLabel(self, u"Ordonnées:")
        sizer.Add(self.sy)
        self.y = wx.TextCtrl(self, -1, self.main.gradu_y, size=(50, -1), style=wx.TE_PROCESS_ENTER)
        self.y.setToolTip(u"Graduation en ordonnées.")
        self.y.Bind(wx.EVT_CHAR, self.main.EvtChar)
        sizer.Add(self.y)

        self.sa = QLabel(self, u"Aire:")
        sizer.Add(self.sa)
        self.a = wx.TextCtrl(self, -1, self.main.gradu_a, size=(50, -1), style=wx.TE_PROCESS_ENTER)
        self.a.setToolTip(u"Dimensions du carré ou rectangle donnant l'échelle.\nExemple:\n 1 (carré), 1x2 (rectangle)")
        self.a.Bind(wx.EVT_CHAR, self.main.EvtChar)
        sizer.Add(self.a)
        msizer.Add(sizer)

        msizer.Add(QLabel(self, '   '))

        # Origine
        box = QGroupBox(self, -1, u"Origine des axes")
        sizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)

        self.sox = QLabel(self, u"Abscisses:")
        sizer.Add(self.sox)
        self.origine_x = wx.TextCtrl(self, -1, self.main.origine_x, size=(50, -1), style=wx.TE_PROCESS_ENTER)
        self.origine_x.setToolTip(u"Origine de l'axe des abscisses.")
        self.origine_x.Bind(wx.EVT_CHAR, self.main.EvtChar)
        sizer.Add(self.origine_x)

        self.soy = QLabel(self, u"Ordonnées:")
        sizer.Add(self.soy)
        self.origine_y = wx.TextCtrl(self, -1, self.main.origine_y, size=(50, -1), style=wx.TE_PROCESS_ENTER)
        self.origine_y.setToolTip(u"Origine de l'axe des ordonnées.")
        self.origine_y.Bind(wx.EVT_CHAR, self.main.EvtChar)
        sizer.Add(self.origine_y)

        msizer.Add(sizer)

        self.add(msizer)

        self.finaliser()


class Autres(CstmPanel):
    def __init__(self, parent):
        CstmPanel.__init__(self, parent)
        sizer = QHBoxLayout()
        vsizer = QVBoxLayout()


        hsizer = QHBoxLayout()
        self.sm = QLabel(self, u'Affichage des effectifs:  ')
        hsizer.Add(self.sm, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        self.mode = QComboBox(self, -1, (100, 50), choices = (u'tels quels', u'en pourcentages', u'en fréquences'))
        self.mode.setSelection(self.main.param("mode_effectifs"))
        self.mode.Bind(wx.EVT_CHOICE, self.main.EvtCheck)
        hsizer.Add(self.mode, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)

        vsizer.Add(hsizer)

        sizer.Add(vsizer)

        vsizer = QVBoxLayout()

        #~ self.pourcentages = wx.CheckBox(self, label = u'Effectifs en Pourcentages.   ')
        #~ self.pourcentages.SetValue(self.main.param("mode_pourcentages"))
        #~ self.pourcentages.Bind(wx.EVT_CHECKBOX, self.main.EvtCheck)
        #~ vsizer.Add(self.pourcentages, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 7)

        self.hachures = QCheckBox(self, label = u'Mode noir et blanc (hachures).')
        self.hachures.SetValue(self.main.param("hachures"))
        self.hachures.Bind(wx.EVT_CHECKBOX, self.main.EvtCheck)
        vsizer.Add(self.hachures)

        self.auto = QCheckBox(self, label = u"Réglage automatique de la fenêtre d'affichage.")
        self.auto.SetValue(self.main.param("reglage_auto_fenetre"))
        self.auto.Bind(wx.EVT_CHECKBOX, self.main.EvtCheck)
        vsizer.Add(self.auto)

        sizer.Add(vsizer, 0, wx.LEFT, 7)
        self.add(sizer)

        self.finaliser()

class Autres_quantile(CstmPanel):
    def __init__(self, parent):
        CstmPanel.__init__(self, parent)

        box = QGroupBox(self, -1, u"Construction de quantiles")
        sizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)

        self.mediane = QCheckBox(self, label = u'Construire la médiane')
        self.mediane.SetValue(self.main.choix_quantiles["mediane"][0])
        self.mediane.Bind(wx.EVT_CHECKBOX, self.main.EvtCheck)

        sizer.Add(self.mediane)
        sizer.addSpacing(10) # valeur à ajuster

        self.quartiles = QCheckBox(self, label = u'Construire les quartiles')
        self.quartiles.SetValue(self.main.choix_quantiles["quartiles"][0])
        self.quartiles.Bind(wx.EVT_CHECKBOX, self.main.EvtCheck)
        sizer.Add(self.quartiles)
        sizer.addSpacing(10) # valeur à ajuster

        self.deciles = QCheckBox(self, label = u'Construire les déciles')
        self.deciles.SetValue(self.main.choix_quantiles["deciles"][0])
        self.deciles.Bind(wx.EVT_CHECKBOX, self.main.EvtCheck)
        sizer.Add(self.deciles)
        sizer.addSpacing(10) # valeur à ajuster

        self.add(sizer)

        self.finaliser()


class OngletsStatistiques(QTabWidget):
    def __init__(self, parent):
        self.parent = parent
        QTabWidget.__init__(self, parent, style=wx.NB_TOP)
        self.donnees = Donnees(self)
        self.legende = Legende(self)
        self.graduation = Graduation(self)
        self.autres = Autres(self)
        self.autresq = Autres_quantile(self)

        self.addTab(self.donnees, u'Données')
        self.addTab(self.legende, u'Légende')
        self.addTab(self.graduation, u'Graduation')
        self.addTab(self.autres, u'Réglages')
        self.addTab(self.autresq, u'Quantiles')


    def enable(self, x, y, a, classes=False, legende_x=False):
        self.donnees.classes.setEnabled(a or classes)
        self.donnees.sc.setEnabled(a or classes)

        self.legende.setEnabled(x or y or a or legende_x)
        self.legende.x.setEnabled(x or legende_x)
        self.legende.sx.setEnabled(x or legende_x)
        self.legende.y.setEnabled(y)
        self.legende.sy.setEnabled(y)
        self.legende.a.setEnabled(a)
        self.legende.sa.setEnabled(a)

        self.graduation.setEnabled(x or y or a)
        self.graduation.x.setEnabled(x)
        self.graduation.sx.setEnabled(x)
        self.graduation.y.setEnabled(y)
        self.graduation.sy.setEnabled(y)
        self.graduation.a.setEnabled(a)
        self.graduation.sa.setEnabled(a)
        self.graduation.origine_x.setEnabled(x)
        self.graduation.sox.setEnabled(x)
        self.graduation.origine_y.setEnabled(y)
        self.graduation.soy.setEnabled(y)

        self.autres.mode.setEnabled(y or a)
        self.autres.sm.setEnabled(y or a)
