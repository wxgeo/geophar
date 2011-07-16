# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                    Suites                   #
##--------------------------------------#######
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

import wx
from operator import attrgetter

from .wxlib import MyMiniFrame
from ..geolib.variables import Variable


class DialogueAnimation(MyMiniFrame):
    def __init__(self, parent):
        MyMiniFrame.__init__(self, parent, u"Créer une animation")
        self.SetExtraStyle(wx.WS_EX_BLOCK_EVENTS )
        self.parent = parent
        self.feuille_actuelle = self.parent.onglet_actuel.feuille_actuelle
        p = self.panel = wx.Panel(self, -1)

        self.sizer = sizer = wx.BoxSizer(wx.VERTICAL)

        terme = wx.BoxSizer(wx.HORIZONTAL)
        terme.Add(wx.StaticText(p, -1, u"Variable :"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,5)
        self.var =  wx.TextCtrl(p, -1, "", size=(100, -1))
        terme.Add(self.var, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,5)
        self.var.Bind(wx.EVT_MIDDLE_DOWN, self.Propositions)
        sizer.Add(terme)

        sizer.Add(wx.StaticLine(p, -1, style=wx.LI_HORIZONTAL), 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        terme = wx.BoxSizer(wx.HORIZONTAL)
        terme.Add(wx.StaticText(p, -1, u"Début :"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,5)
        self.deb =  wx.TextCtrl(p, -1, "0", size=(50, -1))
        terme.Add(self.deb, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,5)
        terme.Add(wx.StaticText(p, -1, u"Fin :"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,5)
        self.fin =  wx.TextCtrl(p, -1, "1", size=(50, -1))
        terme.Add(self.fin, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,5)
        terme.Add(wx.StaticText(p, -1, u"Pas :"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,5)
        self.pas =  wx.TextCtrl(p, -1, "0.05", size=(50, -1))
        terme.Add(self.pas, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,5)
        sizer.Add(terme)

        terme = wx.BoxSizer(wx.HORIZONTAL)
        terme.Add(wx.StaticText(p, -1, u"Période (s) :"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,5)
        self.periode =  wx.TextCtrl(p, -1, "0.1", size=(100, -1))
        terme.Add(self.periode, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,5)
        sizer.Add(terme)



        sizer.Add(wx.StaticLine(p, -1, style=wx.LI_HORIZONTAL), 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        boutons = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_lancer = lancer = wx.Button(p, -1, u"Animer")
        boutons.Add(lancer, 0, wx.ALL, 5)
        fermer = wx.Button(p, -1, u"Fermer")
        boutons.Add(fermer, 0, wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.Animer, lancer)
        self.Bind(wx.EVT_BUTTON, self.OnCloseMe, fermer)
        sizer.Add(boutons)

        p.SetSizerAndFit(sizer)
        self.SetClientSize(p.GetSize())
        self.en_cours = False





    def Animer(self, event = None):
        if self.en_cours:
            self.feuille_actuelle.stop()
        else:
            self.en_cours = True
            self.btn_lancer.SetLabel('Stop')
            self.feuille_actuelle.animer(nom = self.var.GetValue(),
                        debut=eval(self.deb.GetValue()), fin=eval(self.fin.GetValue()),
                        pas=eval(self.pas.GetValue()), periode=eval(self.periode.GetValue()))
        self.en_cours = False
        self.btn_lancer.SetLabel('Animer')

    def Propositions(self, event = None):
        u"Liste des noms de variables de la feuille actuelle."
        self.var.SetFocus()
        liste_objets = self.feuille_actuelle.objets.lister(False, type = Variable)
        liste_objets.sort(key=attrgetter('nom')) # ordre alphabétique
        if not liste_objets:
            return
        ids = [wx.NewId() for obj in liste_objets]
        menu = wx.Menu()
        for i in xrange(len(liste_objets)):
            menu.Append(ids[i], liste_objets[i].nom_complet)
            def select(event, nom = liste_objets[i].nom, champ = self.var):
                champ.SetValue(nom)
            menu.Bind(wx.EVT_MENU, select, id = ids[i])
        self.PopupMenu(menu)
        menu.Destroy()


    def OnCloseMe(self, event):
        self.Close(True)
