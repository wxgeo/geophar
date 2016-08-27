# -*- coding: utf-8 -*-

##--------------------------------------##
#               Barre d'outils pour la géométrie               #
##--------------------------------------##
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

#from LIB import *
#from GUI.wxlib import png
from ...GUI.barre_outils import BarreOutils
from ...geolib import Arc_oriente, Arc_points, Point_generique


class BarreOutilsGraphes(BarreOutils):
    def __init__(self, parent):
        BarreOutils.__init__(self, parent)


    def creer_boutons(self):
        self.add("F1", ("Pointeur", "fleche4", "Déplacer ou modifier un objet.", self.curseur),
                  ("Zoomer", "zoombox2", "Recentrer la zone d'affichage.", self.zoombox),
                  ("Sélectionner", "selection", "Sélectionner une partie de la feuille.",
                  self.selectionner)).select()
        self.add("F2", ("Sommet", "point2","Créer un point.", self.point))
        self.add("F3", ("Arête", "segment2", "Créer une arête droite.", self.segment))
        self.add("F4", ("Arête orientée", "vecteur", "Créer une arête orientée droite.", self.vecteur),
                    )
        self.add("F5", ("Arête courbe", "arc_points",
                    "Créer une arête courbe (définir 3 points).", self.arc_points),
                    )
        self.add("F6", ("Arête orientée (courbe)", "arc_oriente",
                    "Créer une arête orientée courbe (définir 3 points).", self.arc_oriente),
                    )
        self.add("F7", ("Texte", "texte", "Créer un texte.", self.texte))
        self.add("F8", ("Masquer", "masquer", "Masquer des objets.", self.masque))
        self.add("F9", ("Gommer", "gomme", "Supprimer des objets.", self.gomme))
        self.add("Shift+F2", ("Copier", "pinceau", "Copier le style d'un objet.", self.pinceau))




    def arc_points(self, event = False, **kw):
        if event is False:
            self.arc(Arc_points, nom_style='arc', **kw)
        else:
            self.interagir(self.arc_points, "Choisissez ou créez 3 points.")

    def arc_oriente(self, event = False, **kw):
        if event is False:
            self.arc(Arc_oriente, nom_style='arcs_orientes', **kw)
        else:
            self.interagir(self.arc_oriente, "Choisissez ou créez 3 points.")


    def arc(self, classe, nom_style = '', **kw):
        "Création d'un arc défini par 3 points. Un style spécial est appliqué au point intermédaire."
        if self.test(True, **kw):
            self.cache = [obj for obj in self.cache if obj.nom and obj.feuille is self.feuille_actuelle]
            selection = kw["selection"]

            n = len(self.cache)

            if n == 1:
                # Le point intermédiaire a un style différent,
                # et ne doit donc pas coïncider avec un point déjà existant.
                point = self.point(nom_style='points_ancrage', editer=None, **kw)
                self.cache.append(point)
                style = self.style(nom_style)
                style["previsualisation"] = True
                self.feuille_actuelle.objet_temporaire(classe(*(tuple(self.cache) + (self.feuille_actuelle.point_temporaire(),)), **style))
            elif isinstance(selection, Point_generique):
                self.cache.append(selection)
                nouveau_point = False
            else:
                self.cache.append(self.point(**kw))
                nouveau_point = True

            if n == 2:
                self.feuille_actuelle.objet_temporaire(None)
                code = classe.__name__ + "(" + ",".join(obj.nom for obj in self.cache) + ", **%s)" %self.style(nom_style)
                if nouveau_point: # on edite le nom du nouveau point (dernier parametre de self.executer)
                    self.executer(code, editer = self.cache[-1])
                else: # si c'est un vieux point, pas besoin d'editer son nom
                    self.executer(code)

            elif n > 3: # ne se produit que si l'execution a plante...
                self.initialiser()

        elif self.cache:
            style = self.style(nom_style)
            style["previsualisation"] = True
            self.feuille_actuelle.objet_temporaire(classe(*(tuple(self.cache) + (self.feuille_actuelle.point_temporaire(),)), **style))
        else:
            self.feuille_actuelle.objet_temporaire(None)
