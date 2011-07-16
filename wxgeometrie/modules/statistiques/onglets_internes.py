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


class CstmPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.main = self.parent.parent
        self.SetBackgroundColour(wx.NamedColor(u"WHITE"))
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

    def finaliser(self):
        self.SetSizer(self.main_sizer)
        self.Fit()

    def add(self, item):
        self.main_sizer.Add(item, 0, wx.ALL, 5)


class Donnees(CstmPanel):
    def __init__(self, parent):
        CstmPanel.__init__(self, parent)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticText(self, -1, u"Effectifs et valeurs associées:  "), 0, wx.ALIGN_CENTER|wx.ALL, 5)
        self.valeurs = wx.TextCtrl(self, -1, self.main.donnees_valeurs, size=(500, -1), style=wx.TE_PROCESS_ENTER)
        aide = u"Valeurs simples:\n8 8 9 12 17 18\nEffectifs et valeurs:\n2*7 14*8 5*9 1*10\nClasses et effectifs:\n17*[0;10[ 24*[10;20["
        self.valeurs.SetToolTipString(aide)
        self.valeurs.Bind(wx.EVT_CHAR, self.main.EvtChar)
        sizer.Add(self.valeurs, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 4)
        self.add(sizer)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sc = wx.StaticText(self, -1, u"Regroupement par classes:  ")
        sizer.Add(self.sc, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.classes = wx.TextCtrl(self, -1, self.main.donnees_classes, size=(500, -1), style=wx.TE_PROCESS_ENTER)
        self.classes.SetToolTipString(u"Exemple:\n[0;10[ [10;20[ [20;30[")
        self.classes.Bind(wx.EVT_CHAR, self.main.EvtChar)
        sizer.Add(self.classes, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 4)
        self.add(sizer)

        self.finaliser()


class Legende(CstmPanel):
    def __init__(self, parent):
        CstmPanel.__init__(self, parent)
        # Légendes
        box = wx.StaticBox(self, -1, u"Légende des axes")
        sizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)

        self.sx = wx.StaticText(self, -1, u"Abscisses:")
        sizer.Add(self.sx, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.x = wx.TextCtrl(self, -1, self.main.legende_x, size=(200, -1), style=wx.TE_PROCESS_ENTER)
        self.x.Bind(wx.EVT_CHAR, self.main.EvtChar)
        sizer.Add(self.x, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)

        self.sy = wx.StaticText(self, -1, u"Ordonnées:")
        sizer.Add(self.sy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.y = wx.TextCtrl(self, -1, self.main.legende_y, size=(200, -1), style=wx.TE_PROCESS_ENTER)
        self.y.Bind(wx.EVT_CHAR, self.main.EvtChar)
        sizer.Add(self.y, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)

        self.sa = wx.StaticText(self, -1, u"Aire:")
        sizer.Add(self.sa, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.a = wx.TextCtrl(self, -1, self.main.legende_a, size=(100, -1), style=wx.TE_PROCESS_ENTER)
        self.a.SetToolTipString(u"Pour les histogrammes.\nIndique en quelle unité s'exprime la quantité.\nExemples:\npersonnes, ampoules, %, $, ...")
        self.a.Bind(wx.EVT_CHAR, self.main.EvtChar)
        sizer.Add(self.a, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        self.add(sizer)

        self.finaliser()


class Graduation(CstmPanel):
    def __init__(self, parent):
        CstmPanel.__init__(self, parent)
        msizer = wx.BoxSizer(wx.HORIZONTAL)
        # Graduations
        box = wx.StaticBox(self, -1, u"Taille d'une graduation")
        sizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)

        self.sx = wx.StaticText(self, -1, u"Abscisses:")
        sizer.Add(self.sx, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.x = wx.TextCtrl(self, -1, self.main.gradu_x, size=(50, -1), style=wx.TE_PROCESS_ENTER)
        self.x.SetToolTipString(u"Graduation en abscisses.")
        self.x.Bind(wx.EVT_CHAR, self.main.EvtChar)
        sizer.Add(self.x, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)

        self.sy = wx.StaticText(self, -1, u"Ordonnées:")
        sizer.Add(self.sy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.y = wx.TextCtrl(self, -1, self.main.gradu_y, size=(50, -1), style=wx.TE_PROCESS_ENTER)
        self.y.SetToolTipString(u"Graduation en ordonnées.")
        self.y.Bind(wx.EVT_CHAR, self.main.EvtChar)
        sizer.Add(self.y, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)

        self.sa = wx.StaticText(self, -1, u"Aire:")
        sizer.Add(self.sa, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.a = wx.TextCtrl(self, -1, self.main.gradu_a, size=(50, -1), style=wx.TE_PROCESS_ENTER)
        self.a.SetToolTipString(u"Dimensions du carré ou rectangle donnant l'échelle.\nExemple:\n 1 (carré), 1x2 (rectangle)")
        self.a.Bind(wx.EVT_CHAR, self.main.EvtChar)
        sizer.Add(self.a, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        msizer.Add(sizer, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)

        msizer.Add(wx.StaticText(self, -1, '   '), 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)

        # Origine
        box = wx.StaticBox(self, -1, u"Origine des axes")
        sizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)

        self.sox = wx.StaticText(self, -1, u"Abscisses:")
        sizer.Add(self.sox, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.origine_x = wx.TextCtrl(self, -1, self.main.origine_x, size=(50, -1), style=wx.TE_PROCESS_ENTER)
        self.origine_x.SetToolTipString(u"Origine de l'axe des abscisses.")
        self.origine_x.Bind(wx.EVT_CHAR, self.main.EvtChar)
        sizer.Add(self.origine_x, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)

        self.soy = wx.StaticText(self, -1, u"Ordonnées:")
        sizer.Add(self.soy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.origine_y = wx.TextCtrl(self, -1, self.main.origine_y, size=(50, -1), style=wx.TE_PROCESS_ENTER)
        self.origine_y.SetToolTipString(u"Origine de l'axe des ordonnées.")
        self.origine_y.Bind(wx.EVT_CHAR, self.main.EvtChar)
        sizer.Add(self.origine_y, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)

        msizer.Add(sizer, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)

        self.add(msizer)

        self.finaliser()


class Autres(CstmPanel):
    def __init__(self, parent):
        CstmPanel.__init__(self, parent)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        vsizer = wx.BoxSizer(wx.VERTICAL)


        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sm = wx.StaticText(self, -1, u'Affichage des effectifs:  ')
        hsizer.Add(self.sm, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        self.mode = wx.Choice(self, -1, (100, 50), choices = (u'tels quels', u'en pourcentages', u'en fréquences'))
        self.mode.SetSelection(self.main.param("mode_effectifs"))
        self.mode.Bind(wx.EVT_CHOICE, self.main.EvtCheck)
        hsizer.Add(self.mode, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)

        vsizer.Add(hsizer, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 7)

        sizer.Add(vsizer, 0, wx.ALL, 0)

        vsizer = wx.BoxSizer(wx.VERTICAL)

        #~ self.pourcentages = wx.CheckBox(self, label = u'Effectifs en Pourcentages.   ')
        #~ self.pourcentages.SetValue(self.main.param("mode_pourcentages"))
        #~ self.pourcentages.Bind(wx.EVT_CHECKBOX, self.main.EvtCheck)
        #~ vsizer.Add(self.pourcentages, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 7)

        self.hachures = wx.CheckBox(self, label = u'Mode noir et blanc (hachures).')
        self.hachures.SetValue(self.main.param("hachures"))
        self.hachures.Bind(wx.EVT_CHECKBOX, self.main.EvtCheck)
        vsizer.Add(self.hachures, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 7)

        self.auto = wx.CheckBox(self, label = u"Réglage automatique de la fenêtre d'affichage.")
        self.auto.SetValue(self.main.param("reglage_auto_fenetre"))
        self.auto.Bind(wx.EVT_CHECKBOX, self.main.EvtCheck)
        vsizer.Add(self.auto, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 7)

        sizer.Add(vsizer, 0, wx.LEFT, 7)
        self.add(sizer)

        self.finaliser()

class Autres_quantile(CstmPanel):
    def __init__(self, parent):
        CstmPanel.__init__(self, parent)

        box = wx.StaticBox(self, -1, u"Construction de quantiles")
        sizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)

        self.mediane = wx.CheckBox(self, label = u'Construire la médiane')
        self.mediane.SetValue(self.main.choix_quantiles["mediane"][0])
        self.mediane.Bind(wx.EVT_CHECKBOX, self.main.EvtCheck)

        sizer.Add(self.mediane, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 7)
        sizer.AddSpacer(10) # valeur à ajuster

        self.quartiles = wx.CheckBox(self, label = u'Construire les quartiles')
        self.quartiles.SetValue(self.main.choix_quantiles["quartiles"][0])
        self.quartiles.Bind(wx.EVT_CHECKBOX, self.main.EvtCheck)
        sizer.Add(self.quartiles, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 7)
        sizer.AddSpacer(10) # valeur à ajuster

        self.deciles = wx.CheckBox(self, label = u'Construire les déciles')
        self.deciles.SetValue(self.main.choix_quantiles["deciles"][0])
        self.deciles.Bind(wx.EVT_CHECKBOX, self.main.EvtCheck)
        sizer.Add(self.deciles, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 7)
        sizer.AddSpacer(10) # valeur à ajuster

        self.add(sizer)

        self.finaliser()


class OngletsStatistiques(wx.Notebook):
    def __init__(self, parent):
        self.parent = parent
        wx.Notebook.__init__(self, parent, style=wx.NB_TOP)
        self.donnees = Donnees(self)
        self.legende = Legende(self)
        self.graduation = Graduation(self)
        self.autres = Autres(self)
        self.autresq = Autres_quantile(self)

        self.AddPage(self.donnees, u'Données')
        self.AddPage(self.legende, u'Légende')
        self.AddPage(self.graduation, u'Graduation')
        self.AddPage(self.autres, u'Réglages')
        self.AddPage(self.autresq, u'Quantiles')


    def enable(self, x, y, a, classes=False, legende_x=False):
        self.donnees.classes.Enable(a or classes)
        self.donnees.sc.Enable(a or classes)

        self.legende.Enable(x or y or a or legende_x)
        self.legende.x.Enable(x or legende_x)
        self.legende.sx.Enable(x or legende_x)
        self.legende.y.Enable(y)
        self.legende.sy.Enable(y)
        self.legende.a.Enable(a)
        self.legende.sa.Enable(a)

        self.graduation.Enable(x or y or a)
        self.graduation.x.Enable(x)
        self.graduation.sx.Enable(x)
        self.graduation.y.Enable(y)
        self.graduation.sy.Enable(y)
        self.graduation.a.Enable(a)
        self.graduation.sa.Enable(a)
        self.graduation.origine_x.Enable(x)
        self.graduation.sox.Enable(x)
        self.graduation.origine_y.Enable(y)
        self.graduation.soy.Enable(y)

        self.autres.mode.Enable(y or a)
        self.autres.sm.Enable(y or a)
