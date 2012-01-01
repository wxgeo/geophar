# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                  Feuille                                  #
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

from variables import *




class Widget(Objet):
    u"""Un accessoire.

    La classe mère de tous les widgets (usage interne)."""

    _affichage_depend_de_la_fenetre = True

#
#    def __init__(self, **kw):
#        Objet.__init__(self)
#
#    def supprimer(self):
#        Objet.supprimer(self)
#        if self.__canvas__().select is self:
#            self.__canvas__().select = None
#        self.Destroy()
#
#    def _get_coordonnees(self):
#        return self.x(), self.y()
#
#    def _set_coordonnees(self, x = None, y = None):
#        if x is not None:
#            if y is None: # _set_coordonnees((-1,2)) est accepté
#                x, y = x
#            self.x(x)
#            self.y(y)
#
#    def abscisse(self):
#        return self.coordonnees()[0]
#
#    def ordonnee(self):
#        return self.coordonnees()[1]
#
#    def _espace_vital(self):
#        x, y = self.coordonnees()
#        l, h = self.GetSize()
#        l *= self.coeff(0); h*= self.coeff(1)
#        return (x, x + l, y, y + h)
#
#
#    def _distance_inf(self, x, y, d):
#        x0, y0 = self.position()
#        l, h = self.GetSize()
#        return x0 - d < x < x0 + l + d and y0 - d < y < y0 + h + d
#
#
#
##    _call = Objet.coordonnees
#
#
#
#
#
#
#
#
#class Champ(Widget, wx.TextCtrl):
#    u"""Un champ.
#
#    Un champ de saisie de texte."""
#
#    def __init__(self, texte = "", x = None, y = None, taille = 60, **kw):
#        if x is None:
#            self.synchroniser_feuille()
#            if self.__canvas__():
#                xmin, xmax, ymin, ymax = self.__canvas__().fen()
#                x = module_random.uniform(xmin,xmax)
#                y = module_random.uniform(ymin,ymax)
#                del xmin, xmax, ymin, ymax # evite d'enregistrer les variables xmin, xmax...
#            else:
#                x = y = 0
#
#        x0, y0 = self.__canvas__().XYcoo2pix((x, y), -1) # coordonnées en pixels
#
#        x, y, taille = self.nb2var(x), self.nb2var(y), self.nb2var(taille)
#        # on convertit l'entree en Variable (voir la definition de la Classe Variable en fin de page)
#        Widget.__init__(self, **kw)
#        wx.TextCtrl.__init__(self, self.__canvas__(), value = texte, pos = (int(x0), int(y0)), size = (taille, -1))
#        self.style(**param.widgets)
#        self.finaliser(basestring, Variable, Variable, Variable)
#
#    def _affiche(self):
#        x, y = self.coordonnees()
#        x0, y0 = self.__canvas__().XYcoo2pix((x, y), -1) # coordonnées en pixels
#        wx.TextCtrl.SetPosition(self, (int(x0), int(y0)))
#        wx.TextCtrl.SetSize(self, (self.taille(), -1))
#
#
#    def __getattribute__(self, nom):
#        if nom == "texte":
#            object.__getattribute__(self, "__dict__")["texte"] = self.GetValue()
#        return object.__getattribute__(self, nom)
#
#
#    def __setattr__(self, nom, valeur):
#        if nom == "texte":
#            self.SetValue(valeur)
#        object.__getattribute__(self, "__dict__")[nom] = valeur
#
#
#
#
#
#class Bouton(Widget, wx.Button):
#    u"""Un bouton.
#
#    Un bouton cliquable, auquel on peut associer différentes actions."""
#
#
#    def __init__(self, texte = "", x = None, y = None, macro = None, **kw):
#        if x is None:
#            self.synchroniser_feuille()
#            if self.__canvas__():
#                xmin, xmax, ymin, ymax = self.__canvas__().fen()
#                x = module_random.uniform(xmin,xmax)
#                y = module_random.uniform(ymin,ymax)
#                del xmin, xmax, ymin, ymax # evite d'enregistrer les variables xmin, xmax...
#            else:
#                x = y = 0
#
#        x0, y0 = self.__canvas__().XYcoo2pix((x, y), -1) # coordonnées en pixels
#
#        x, y = self.nb2var(x), self.nb2var(y)
#        # on convertit l'entree en Variable (voir la definition de la Classe Variable en fin de page)
#        Widget.__init__(self, **kw)
#        wx.Button.__init__(self, self.__canvas__(), label = texte, pos = self.__canvas__().XYcoo2pix((int(x), int(y)), -1))
#        self.Bind(wx.EVT_BUTTON, self.action)
#        self.style(**param.widgets)
#        self.finaliser(basestring, Variable, Variable)
#
#    def action(self, event = None):
#        if self.macro is not None:
#            self.macro()
#
#
#    def _affiche(self):
#        x, y = self.coordonnees()
#        x0, y0 = self.__canvas__().XYcoo2pix((x, y), -1) # coordonnées en pixels
#        wx.Button.SetPosition(self, (int(x0), int(y0)))
