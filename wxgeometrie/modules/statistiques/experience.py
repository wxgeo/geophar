# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##------------------------------------------#######
#                   Experience                   #
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

import wx
from numpy.random import rand
from numpy import sum
# NB: numpy.sum est 100 fois plus rapide que __builtin__.sum !

from ...GUI.wxlib import MyMiniFrame
from ...pylib import msplit

ent = int

def alea(n = None):
    u"""Nombre entier aléatoire compris entre 0 et n-1.
    Si n = None, nombre décimal entre 0 et 1."""
    if n == None:
        return rand()
    return int(n*rand())

def de(k = 1):
    return sum(1+(6*rand(k)).astype(int))


def sondage(pourcentage = 50, k = 1000):
    pourcentage /= 100.
    return 100.*sum(rand(k)<pourcentage)/k





class ExperienceFrame(MyMiniFrame):
    def __init__(self, parent):

        MyMiniFrame.__init__(self, parent, u"Simulation d'une expérience")
        self.SetExtraStyle(wx.WS_EX_BLOCK_EVENTS )
        self.parent = parent

        p = self.panel = wx.Panel(self, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        exp = wx.BoxSizer(wx.HORIZONTAL)
        exp.Add(wx.StaticText(p, -1, u"Experience:"), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        self.experience = wx.TextCtrl(p, -1, "", size=(120, -1))
        self.experience.Bind(wx.EVT_CHAR, self.EvtChar)
        exp.Add(self.experience, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(exp)

        nbr = wx.BoxSizer(wx.HORIZONTAL)
        nbr.Add(wx.StaticText(p, -1, u"Nombre d'expériences:"), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sc = self.sc = wx.SpinCtrl(p, -1, "", (30, 50))
        sc.SetRange(1,100000)
        sc.SetValue(5)
        self.sc.Bind(wx.EVT_CHAR, self.EvtChar)
        self.Bind(wx.EVT_SPINCTRL, self.EvtSpin, sc)
        self.Bind(wx.EVT_TEXT, self.EvtSpinText, sc)
        #n = wx.TextCtrl(p, -1, "", size=(100, -1))
        nbr.Add(sc, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(nbr)

        val = wx.BoxSizer(wx.HORIZONTAL)
        val.Add(wx.StaticText(p, -1, u"Valeurs possibles:"), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        self.valeurs = wx.TextCtrl(p, -1, "", size=(120, -1))
        self.valeurs.Bind(wx.EVT_CHAR, self.EvtChar)
        val.Add(self.valeurs, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(val)

#        self.iconfiance = wx.CheckBox(p, -1, "Afficher l'intervalle de confiance")
#        sizer.Add(self.iconfiance, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
#        self.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox, self.iconfiance)

        self.cb = wx.CheckBox(p, -1, u"Lancer une animation:")
        sizer.Add(self.cb, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        self.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox, self.cb)

        boutons = wx.BoxSizer(wx.HORIZONTAL)
        fermer = wx.Button(p, -1, u"Fermer")
        boutons.Add(fermer, 0, wx.ALL, 5)
        lancer = wx.Button(p, -1, u"Lancer l'experience")
        boutons.Add(lancer, 0, wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.OnCloseMe, fermer)
        self.Bind(wx.EVT_BUTTON, self.actualiser, lancer)

        sizer.Add(boutons)
        p.SetSizerAndFit(sizer)
        self.SetClientSize(p.GetSize())

    def actualiser(self, event = None):
        n = self.sc.GetValue()
        exp = self.experience.GetValue()
        vals = msplit(self.valeurs.GetValue(), (" ", ",", ";"))
        if exp:
            self.parent.experience(exp, n, [eval(val) for val in vals if val])




    def OnCloseMe(self, event):
        self.Close(True)

    def EvtCheckBox(self, event):
        self.actualiser()

    def EvtSpin(self, event):
        self.actualiser()

    def EvtSpinText(self, event):
        pass
    #    self.actualiser()

    def EvtChar(self, event):
        code = event.GetKeyCode()

        if code == 13:
            self.actualiser()
        else:
            event.Skip()




class LancerDes(MyMiniFrame):
    def __init__(self, parent):

        MyMiniFrame.__init__(self, parent, u"Simulation de lancers de dés")
        self.parent = parent

        p = self.panel = wx.Panel(self, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(p, -1, u"On simule le lancer d'un ou plusieurs dés"), 0, wx.LEFT|wx.TOP|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(wx.StaticText(p, -1, u"à 6 faces, et on étudie la somme des points."), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        exp = wx.BoxSizer(wx.HORIZONTAL)
        exp.Add(wx.StaticText(p, -1, u"Nombre de dés:"), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        ex = self.experience = wx.SpinCtrl(p, -1, "",  (30, 50))
        ex.SetRange(1, 100000)
        ex.SetValue(1)
        ex.Bind(wx.EVT_CHAR, self.EvtChar)
        self.Bind(wx.EVT_SPINCTRL, self.EvtSpin, ex)
        self.Bind(wx.EVT_TEXT, self.EvtSpinText, ex)
        exp.Add(self.experience, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(exp)

        nbr = wx.BoxSizer(wx.HORIZONTAL)
        nbr.Add(wx.StaticText(p, -1, u"Nombre de lancers:"), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sc = self.sc = wx.SpinCtrl(p, -1, "", (30, 50))
        sc.SetRange(1, 100000)
        sc.SetValue(1)
        self.sc.Bind(wx.EVT_CHAR, self.EvtChar)
        self.Bind(wx.EVT_SPINCTRL, self.EvtSpin, sc)
        self.Bind(wx.EVT_TEXT, self.EvtSpinText, sc)
        nbr.Add(sc, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(nbr)

        self.cb = wx.CheckBox(p, -1, u"Conserver les valeurs")
        sizer.Add(self.cb, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)


        boutons = wx.BoxSizer(wx.HORIZONTAL)
        fermer = wx.Button(p, -1, u"Fermer")
        boutons.Add(fermer, 0, wx.ALL, 5)
        lancer = wx.Button(p, -1, u"Lancer l'expérience")
        boutons.Add(lancer, 0, wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.OnCloseMe, fermer)
        self.Bind(wx.EVT_BUTTON, self.actualiser, lancer)

        sizer.Add(boutons)
        p.SetSizerAndFit(sizer)
        self.SetClientSize(p.GetSize())

    def actualiser(self, event = None):
        if not self.cb.GetValue():
            self.parent.actualiser(False)
        self.parent.graph = 'batons'
        n = self.sc.GetValue()
        des = self.experience.GetValue()
        for val in range(des, 6*des + 1):
            self.parent.ajouter_valeur(val, 0)
        self.parent.ajouter_valeurs(*[de(des) for i in xrange(n)])
        self.parent.calculer()
        self.parent.legende_x = u"points obtenus"
        self.parent.legende_y = u"nombre de lancers"
        self.parent.affiche()





    def OnCloseMe(self, event):
        self.Close(True)


    def EvtSpin(self, event):
        self.actualiser()

    def EvtSpinText(self, event):
        pass

    def EvtChar(self, event):
        code = event.GetKeyCode()

        if code == 13:
            self.actualiser()
        else:
            event.Skip()






class Sondage(MyMiniFrame):
    def __init__(self, parent):

        MyMiniFrame.__init__(self, parent, u"Simulation d'un sondage")
        self.parent = parent

        p = self.panel = wx.Panel(self, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(p, -1, u"On simule un sondage simple (réponse par oui ou non)."), 0, wx.LEFT|wx.TOP|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(wx.StaticText(p, -1, u"Exemple: \"préférez-vous le candidat A au candidat B ?\""), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        exp = wx.BoxSizer(wx.HORIZONTAL)
        exp.Add(wx.StaticText(p, -1, u"Pourcentage de réponses affirmatives sur l'ensemble de la population:"), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        ex = self.experience = wx.SpinCtrl(p, -1, "",  (30, 50))
        ex.SetRange(0,100)
        ex.SetValue(50)
        ex.Bind(wx.EVT_CHAR, self.EvtChar)
        self.Bind(wx.EVT_SPINCTRL, self.EvtSpin, ex)
        self.Bind(wx.EVT_TEXT, self.EvtSpinText, ex)
        exp.Add(self.experience, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(exp)

        nbr = wx.BoxSizer(wx.HORIZONTAL)
        nbr.Add(wx.StaticText(p, -1, u"Taille de l'echantillon:"), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sc = self.sc1 = wx.SpinCtrl(p, -1, "", (30, 50))
        sc.SetRange(1, 100000)
        sc.SetValue(1000)
        sc.Bind(wx.EVT_CHAR, self.EvtChar)
        self.Bind(wx.EVT_SPINCTRL, self.EvtSpin, sc)
        self.Bind(wx.EVT_TEXT, self.EvtSpinText, sc)
        nbr.Add(sc, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(nbr)

        self.cb = wx.CheckBox(p, -1, u"Afficher l'intervalle de confiance")
        sizer.Add(self.cb, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        self.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox, self.cb)


        nbr = wx.BoxSizer(wx.HORIZONTAL)
        nbr.Add(wx.StaticText(p, -1, u"Nombre de sondages:"), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sc = self.sc2 = wx.SpinCtrl(p, -1, "", (30, 50))
        sc.SetRange(1,100000)
        sc.SetValue(1)
        sc.Bind(wx.EVT_CHAR, self.EvtChar)
        self.Bind(wx.EVT_SPINCTRL, self.EvtSpin, sc)
        self.Bind(wx.EVT_TEXT, self.EvtSpinText, sc)
        nbr.Add(sc, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(nbr)


        boutons = wx.BoxSizer(wx.HORIZONTAL)
        fermer = wx.Button(p, -1, u"Fermer")
        boutons.Add(fermer, 0, wx.ALL, 5)
        lancer = wx.Button(p, -1, u"Lancer l'experience")
        boutons.Add(lancer, 0, wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.OnCloseMe, fermer)
        self.Bind(wx.EVT_BUTTON, self.actualiser, lancer)

        sizer.Add(boutons)
        p.SetSizerAndFit(sizer)
        self.SetClientSize(p.GetSize())



##    def actualiser(self, event = None):
##        self.parent.actualiser(False)
##        self.parent.graph = 1
##        self.parent.choix.SetSelection(self.parent.graph)
##        echantillon = self.sc1.GetValue()
##        n = self.sc2.GetValue()
##        esperance = self.experience.GetValue()
##        self.parent.ajouter_valeurs(*[sondage(esperance, echantillon) for i in xrange(n)])
##        self.parent.calculer()
##        self.parent.legende_x = u"résultat des sondages (en %)"
##        self.parent.legende_y = u"nombre de sondages"
##        self.parent.affiche()
####        self.mem = self.parent.canvas.graph.en_cache()
##        if self.cb.GetValue():
##            self.parent.intervalle_confiance(echantillon)
##            self.parent.canvas.rafraichir_affichage(dessin_temporaire = True)
##
##
##
##    def EvtCheckBox(self, event):
##        echantillon = self.sc1.GetValue()
##        if self.cb.GetValue():
##            self.parent.intervalle_confiance(echantillon)
####        else:
####            self.parent.canvas.graph.restaurer(self.mem)
####            self.parent.canvas.affiche()
###        self.parent.canvas.rafraichir_affichage(dessin_temporaire = self.cb.GetValue())
##        self.parent.canvas.rafraichir_affichage(dessin_temporaire = True)



    def actualiser(self, event = None):
        self.parent.actualiser(False)
        self.parent.graph = 'batons'
        echantillon = self.sc1.GetValue()
        n = self.sc2.GetValue()
        esperance = self.experience.GetValue()
        self.parent.ajouter_valeurs(*(sondage(esperance, echantillon) for i in xrange(n)))
        self.parent.calculer()
        self.parent.legende_x = u"résultat des sondages (en %)"
        self.parent.legende_y = u"nombre de sondages"
        self.parent.affiche()


    def EvtCheckBox(self, event):
        echantillon = self.sc1.GetValue()
        if self.cb.GetValue():
            self.parent.intervalle_confiance = echantillon
        else:
            self.parent.intervalle_confiance = None
        self.parent.affiche()

    def OnCloseMe(self, event):
        self.parent.intervalle_confiance = None
        self.Close(True)

    def EvtSpin(self, event):
        self.actualiser()

    def EvtSpinText(self, event):
        pass

    def EvtChar(self, event):
        code = event.GetKeyCode()

        if code == 13:
            self.actualiser()
        else:
            event.Skip()
