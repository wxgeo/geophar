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
from ...GUI.wxlib import MyMiniFrame
from ...geolib import Point, Segment, Droite, RIEN, TEXTE
from ...pylib import eval_safe


class CreerSuite(MyMiniFrame):
    def __init__(self, parent):
        MyMiniFrame.__init__(self, parent, u"Représenter une suite")
        self.SetExtraStyle(wx.WS_EX_BLOCK_EVENTS )
        self.parent = parent
        self._param_ = self.parent._param_
        p = self.panel = wx.Panel(self, -1)

        self.sizer = sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(p, -1, u"Choisissez le mode de génération de la suite :"), 0, wx.ALIGN_LEFT|wx.ALL,5)
        self.mode = wx.Choice(p, -1, (100, 50), choices = [u"u(n+1)=f(u(n))", u"u(n)=f(n)"])
        self.mode.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.EvtChoixMode, self.mode)
        sizer.Add(self.mode, 0, wx.ALIGN_LEFT|wx.ALL,5)

        f = wx.BoxSizer(wx.HORIZONTAL)
        f.Add(wx.StaticText(p, -1, u"Choisissez la fonction f :"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,5)
        self.fonction = wx.Choice(p, -1, (100, 50), choices = ["Y" + str(i+1) for i in xrange(self.parent.nombre_courbes)])
        self.fonction.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.EvtChoixFonction, self.fonction)
        f.Add(self.fonction, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,5)
        sizer.Add(f)

        start = wx.BoxSizer(wx.HORIZONTAL)
        start.Add(wx.StaticText(p, -1, u"Commencer pour n ="), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,5)
        self.n0 = wx.SpinCtrl(p, -1, "", size = (50, -1))
        self.n0.SetRange(0, 1000000)
        self.n0.SetValue(0)
        start.Add(self.n0, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,5)
        sizer.Add(start)

        self.terme = terme = wx.BoxSizer(wx.HORIZONTAL)
        terme.Add(wx.StaticText(p, -1, u"Terme initial :"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,5)
        self.un0 =  wx.TextCtrl(p, -1, "1", size=(100, -1))
        terme.Add(self.un0, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,5)
        sizer.Add(terme)

        sizer.Add(wx.StaticLine(p, -1, style=wx.LI_HORIZONTAL), 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        nbr = wx.BoxSizer(wx.HORIZONTAL)
        nbr.Add(wx.StaticText(p, -1, u"Construire les"), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL
|wx.ALL,5)
        self.termes = wx.SpinCtrl(p, -1, "", size = (50, -1))
        self.termes.SetRange(0, 100)
        self.termes.SetValue(5)
        nbr.Add(self.termes, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,5)
        nbr.Add(wx.StaticText(p, -1, u"premiers termes."), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,5)
        sizer.Add(nbr)

        sizer.Add(wx.StaticLine(p, -1, style=wx.LI_HORIZONTAL), 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        #p.SetSizer(sizer)
        boutons = wx.BoxSizer(wx.HORIZONTAL)
        fermer = wx.Button(p, -1, u"Fermer")
        boutons.Add(fermer, 0, wx.ALL, 5)
        lancer = wx.Button(p, -1, u"Créer")
        boutons.Add(lancer, 0, wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.OnCloseMe, fermer)
        self.Bind(wx.EVT_BUTTON, self.Creer, lancer)
        sizer.Add(boutons)

        p.SetSizerAndFit(sizer)
        self.SetClientSize(p.GetSize())





    def Creer(self, event = None):
##        self.parent.creer_feuille() # nouvelle feuille de travail
        # style des lignes :
        style, epaisseur = self._param_.style_suites_recurrentes
        kw_lignes = {"style": style, "epaisseur": epaisseur}

        # Les suites s'enregistrent auprès du module traceur
#        if not hasattr(self.parent, "suites"):
#            self.parent.suites = {}

        objets = self.parent.feuille_actuelle.objets
        i=self.fonction.GetSelection()
        nom_courbe = 'Cf' + str(i + 1)

        if objets.has_key(nom_courbe):
            courbe = objets[nom_courbe]
            fonction = courbe.fonction
        elif self.parent.boites[i].GetValue():
            self.parent.EvtChar(i=i)
            courbe = objets[nom_courbe]
            fonction = courbe.fonction
        else:
            # TODO: afficher un vrai message d'erreur
            raise KeyError,  "courbe inexistante : %s" %nom_courbe


        if self.mode.GetSelection() == 0: # cas des suites définies par récurrence
            u0 = eval_safe(self.un0.GetValue())
            n0 = self.n0.GetValue()

            objets.suiteDroited = Droite(Point(0, 0), Point(1, 1), legende = TEXTE, label = "$y\ =\ x$")
            M = objets.suitePointM0 = Point(u0, 0, legende = TEXTE, label = "$u_%s$" %(n0))
#            self.parent.suites["u"] = [d, M]

            for i in xrange(self.termes.GetValue() - 1):
                # (Attention, ça ne va pas marcher pour les fonctions définies par morceau)
                u1 = fonction(u0)
                N = Point(u0, u1, legende = RIEN, visible = self._param_.afficher_points_de_construction)
                s = Segment(M, N, **kw_lignes)
                P = Point(0, u1, legende = TEXTE, label = "$u_%s$" %(i + n0 + 1))
                t = Segment(N, P, **kw_lignes)
                Q = Point(u1, u1, legende = RIEN, visible = self._param_.afficher_points_de_construction)
                r = Segment(P, Q, **kw_lignes)
                M = Point(u1, 0, legende = TEXTE, label = "$u_%s$" %(i + n0 + 1))
                #self.parent.suites[u"u"].append([M, N, P, s, t])
                setattr(objets, "SuitePointN" + str(i), N)
                setattr(objets, "suitePointP" + str(i), P)
                setattr(objets, "suitePointQ" + str(i), Q)
                setattr(objets, "suiteSegments" + str(i), s)
                setattr(objets, "suiteSegmentt" + str(i), t)
                setattr(objets, "suiteSegmentr" + str(i), r)
                setattr(objets, "suitePointM" + str(i + 1), M)
                a = Segment(Q, M, **kw_lignes)
                setattr(objets, "suiteSegmenta" + str(i), a)
                u0 = u1
            self.parent.canvas.zoom_auto()

        else:   # suites définies explicitement
            n0 = self.n0.GetValue()
#            self.parent.suites[u"u"] = []
            for i in xrange(n0, n0 + self.termes.GetValue()):
                yi = fonction(i)
                M = Point(i, 0, legende = TEXTE, label = str(i))
                N = Point(i, yi, legende = RIEN)
                P = Point(0, yi, legende = TEXTE, label = "$u_%s$" %i)
                s = Segment(M, N, **kw_lignes)
                t = Segment(N, P, **kw_lignes)
                setattr(objets, "suitePointM" + str(i), M)
                setattr(objets, "suitePointN" + str(i), N)
                setattr(objets, "suitePointP" + str(i), P)
                setattr(objets, "suiteSegments" + str(i), s)
                setattr(objets, "suiteSegmentt" + str(i), t)
            self.parent.canvas.zoom_auto()



    def EvtChoixMode(self, event):
        if event.GetSelection() == 1:
            self.terme.ShowItems(False)
        else:
            self.terme.ShowItems(True)

    def EvtChoixFonction(self, event):
        n = event.GetSelection()
        for i in xrange(self.parent.nombre_courbes):
            self.parent.boites[i].SetValue(i == n)

    def OnCloseMe(self, event):
        self.Close(True)
