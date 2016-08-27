# -*- coding: utf-8 -*-

##--------------------------------------#######
#                 Geometre                    #
##--------------------------------------#######
#    WxGeometrie
#    Dynamic geometry, graph plotter, and more for french mathematic teachers.
#    Copyright (C) 2005-2013  Nicolas Pourcelot
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


from ...GUI.menu import MenuBar
from ...GUI.panel import Panel_API_graphique

class GeometreMenuBar(MenuBar):
    def __init__(self, panel):
        MenuBar.__init__(self, panel)
        self.ajouter("Fichier", ["nouveau"], ["ouvrir"], ["ouvrir ici"], None,
                    ["enregistrer"], ["enregistrer_sous"], ["exporter"],
                    ["exporter&sauver"], None,
                    ['session'], None, ["imprimer"], ["presse-papier"],
                    None, ["proprietes"], None, self.panel.doc_ouverts, None,
                    ["fermer"], ["quitter"])
        self.ajouter("Editer", ["annuler"], ["refaire"], ["modifier"], ["supprimer"])
        self.ajouter("creer")
        self.ajouter("affichage")
        self.ajouter("autres")
        self.ajouter("Outils", ["options"])
        self.ajouter("avance1")
        self.ajouter("?")


class Geometre(Panel_API_graphique):

    titre = "Géométrie dynamique" # Donner un titre à chaque module

    def __init__(self, *args, **kw):
        Panel_API_graphique.__init__(self, *args, **kw)
        self.finaliser()
