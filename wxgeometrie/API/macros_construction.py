# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#              Macros de construction         #
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


import re
from .sauvegarde import FichierGEO




class Macro_construction(object):
    u"""Lecteur de macros.

    Lit et interprète le fichier de macro de construction.
    """

    def __init__(self, nom = None):
        self.nom = nom
        self.fichier = FichierGEO(type = "Macro de construction WxGeometrie", nom = nom or "")
        self.figure = ""
        pass

    def ouvrir(self, path):
        self.fichier.ouvrir(path)
        if self.fichier.has_key("Figure"):
            self.figure = self.fichier.contenu["Figure"][0] # code python correspondant à la figure
        else:
            self.figure = ""

        if self.fichier.has_key("Parametres_macro"):
            self.parametres = self.fichier.contenu["Parametres_macro"][0]
#            self.nom = self.parametres["nom"][0].strip()
            self.arguments = self.parametres["arguments"][0].strip().split(",") # arguments de la macro (ex: 3 points pour un triangle)
#            self.decoration = self.parametres["decoration"][0].strip().split(",") # éléments ne devant pas être construits (texte de commentaire par exemple).

        else: # par défaut, les arguments sont tous les points libres
            self.arguments = []
            for ligne in self.figure.split("\n"):
                re_match = re.match("[A-Za-z_][A-Za-z0-9_]*[ ]*=[ ]*Point(", ligne)
                if re_match:
                    self.arguments.append(re_match.group().split("=")[0].strip()) # on rajoute le nom du point
#            self.decoration = ()


    def enregistrer(self, path):
        pass


#        self.ouvrir(fichier)

#    def ouvrir(self, path):
#        pass
