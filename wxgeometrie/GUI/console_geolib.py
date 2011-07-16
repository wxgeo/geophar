# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------##
#               Console pour geolib               #
##--------------------------------------##
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
from .ligne_commande import LigneCommande
from ..pylib import print_error

class ConsoleGeolib(wx.Panel):
    def __init__(self, parent, couleur = None):
        self.parent = parent
        wx.Panel.__init__(self, parent, -1, style = wx.TAB_TRAVERSAL|wx.WANTS_CHARS)
        self.SetBackgroundColour(couleur if couleur is not None else wx.NamedColor(u"WHITE"))
        vsizer = wx.BoxSizer(wx.VERTICAL)
        label = u"Tapez une commande ci-dessus, puis appuyez sur [Entrée]."
        self.resultats = wx.StaticText(self, size = (500, -1), label = label)
        italic = wx.Font(self.GetFont().GetPointSize(),
                          self.GetFont().GetFamily(),
                          wx.ITALIC, wx.NORMAL)
        self.resultats.SetFont(italic)
        self.ligne_commande = LigneCommande(self, longueur = 500, action = self.action)
        vsizer.Add(self.ligne_commande, 1, wx.ALL|wx.EXPAND, 0)
        vsizer.Add(self.resultats, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(vsizer)
        self.Fit()

    def action(self, commande, **kw):
        try:
            resultat = self.parent.feuille_actuelle.executer(commande)
            self.resultats.SetLabel(resultat)
            self.ligne_commande.Clear()
        except:
            print_error()
            self.resultats.SetLabel('Erreur.')
