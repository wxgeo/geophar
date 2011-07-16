# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#        Proprietes de la feuille             #
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

from .wxlib import MyMiniFrame
from ..pylib import uu

class ProprietesDescription(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.feuille = parent.feuille
        self.sizer = gbs = wx.GridBagSizer(10, 10)
        self.infos = {}



        gbs.Add(wx.StaticText(self, -1, u"Titre : "), (1, 1))
        self.titre = wx.TextCtrl(self, value = self.feuille.infos("titre"), size=wx.Size(300, -1))
        self.Bind(wx.EVT_TEXT, self.EvtTitre, self.titre)
        gbs.Add(self.titre, (1, 2), flag = wx.EXPAND)

        gbs.Add(wx.StaticText(self, -1, u"Auteur : "), (2, 1))
        self.auteur = wx.TextCtrl(self, value = self.feuille.infos("auteur"), size=wx.Size(300, -1))
        self.Bind(wx.EVT_TEXT, self.EvtAuteur, self.auteur)
        gbs.Add(self.auteur, (2, 2), flag = wx.EXPAND)

        gbs.Add(wx.StaticText(self, -1, u"Version : "), (3, 1))
        self.version = wx.TextCtrl(self, value = self.feuille.infos("version"), size=wx.Size(300, -1))
        self.Bind(wx.EVT_TEXT, self.EvtVersion, self.version)
        gbs.Add(self.version, (3, 2), flag = wx.EXPAND)

        gbs.Add(wx.StaticText(self, -1, u"Resumé : "), (4, 1))
        self.resume = wx.TextCtrl(self, value = self.feuille.infos("resume"), size=wx.Size(300, 50), style=wx.TE_MULTILINE)
        self.Bind(wx.EVT_TEXT, self.EvtResume, self.resume)
        gbs.Add(self.resume, (4, 2), flag = wx.EXPAND)

        gbs.Add(wx.StaticText(self, -1, u"Notes : "), (5, 1))
        self.notes = wx.TextCtrl(self, value = self.feuille.infos("notes"), size=wx.Size(300, 100), style=wx.TE_MULTILINE)
        self.Bind(wx.EVT_TEXT, self.EvtNotes, self.notes)
        gbs.Add(self.notes, (5, 2), flag = wx.EXPAND)

        boutons = wx.GridBagSizer(10, 10)
        ok = wx.Button(self, wx.ID_OK)
        ok.Bind(wx.EVT_BUTTON, self.EvtOk)
        appliquer = wx.Button(self, label = u"Appliquer")
        appliquer.Bind(wx.EVT_BUTTON, self.EvtAppliquer)
        effacer = wx.Button(self, label = u"Effacer")
        effacer.Bind(wx.EVT_BUTTON, self.EvtEffacer)
        annuler = wx.Button(self, label = u"Annuler")
        annuler.Bind(wx.EVT_BUTTON, self.EvtAnnuler)

        boutons.Add(ok, (1, 0))
        boutons.Add(appliquer, (1, 1))
        boutons.Add(effacer, (1, 2))
        boutons.Add(annuler, (1, 3))
        boutons.Add(wx.StaticText(self, -1, ""), (2, 1))
        boutons.Add
        gbs.Add(boutons, (6, 2))#, (1, 2))

        gbs.SetEmptyCellSize(wx.Size(10, 10))
        boutons.SetEmptyCellSize(wx.Size(4, 4))
        self.SetSizerAndFit(self.sizer)
        self.parent.parent.dim1 = self.sizer.CalcMin().Get()


    def EvtTitre(self, event):
        self.infos["titre"] = event.GetString()

    def EvtAuteur(self, event):
        self.infos["auteur"] = event.GetString()

    def EvtVersion(self, event):
        self.infos["version"] = event.GetString()

    def EvtResume(self, event):
        self.infos["resume"] = event.GetString()

    def EvtNotes(self, event):
        self.infos["notes"] = event.GetString()


    def EvtOk(self, event):
        self.EvtAppliquer(event)
        self.EvtAnnuler(event)

    def EvtAppliquer(self, event):
        self.feuille.infos(**self.infos)
        self.parent.parent.panel.rafraichir_titre()

    def EvtEffacer(self, event):
        self.titre.SetValue("")
        self.auteur.SetValue("")
        self.version.SetValue("")
        self.resume.SetValue("")
        self.notes.SetValue("")

    def EvtAnnuler(self, event):
        self.parent.parent.Close() # fermeture de la frame



class ProprietesStatistiques(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.feuille = parent.feuille

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(wx.StaticText(self, -1, u"Informations sur " + uu(self.feuille.nom) + " :"), 0, wx.ALL, 8)
        self.sizer.Add(wx.StaticText(self, -1, u"Date de création :  " + uu(self.feuille.infos("creation"))), 0, wx.ALL, 8)
        self.sizer.Add(wx.StaticText(self, -1, u"Dernière modification :  " + uu(self.feuille.infos("modification"))), 0, wx.ALL, 8)
        self.sizer.Add(wx.StaticText(self, -1, u"Nombre d'objets :  " + str(len(self.feuille.liste_objets(True)))), 0, wx.ALL, 8)
        self.SetSizerAndFit(self.sizer)
        self.parent.parent.dim2 = self.sizer.CalcMin().Get()



class OngletsProprietesFeuille(wx.Notebook):
    def __init__(self, parent):
        self.parent = parent
        self.feuille = parent.feuille
        wx.Notebook.__init__(self, parent)
        self.description = ProprietesDescription(self)
        self.AddPage(self.description, u"Description")
        self.statistiques = ProprietesStatistiques(self)
        self.AddPage(self.statistiques, u"Statistiques")












class ProprietesFeuille(MyMiniFrame):
    def __init__(self, parent, feuille):
        self.parent = parent
        self.feuille = feuille
        self.fenetre_principale = self
        while hasattr(self.fenetre_principale, "parent"): # detection de la fenetre principale de WxGeometrie.
            self.fenetre_principale = self.fenetre_principale.parent
        self.panel = self.fenetre_principale.onglets.onglet_actuel
        MyMiniFrame.__init__(self, parent, u"Propriétés de " + uu(self.feuille.nom))
        self.onglets = OngletsProprietesFeuille(self)
        self.SetSize(wx.Size(*(max(dimensions) + 50 for dimensions in zip(self.dim1, self.dim2))))
