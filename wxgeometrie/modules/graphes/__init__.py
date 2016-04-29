# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

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

import re
from collections import defaultdict
from random import randint
from itertools import count

from PyQt4.QtGui import QInputDialog, QLineEdit

from sympy import latex

from ...GUI.menu import MenuBar
from ...GUI.panel import Panel_API_graphique
from ...mathlib.graphes import Graph, colors, colors_dict
from .barre_outils_graphes import BarreOutilsGraphes
from ...geolib import Arc_oriente


class GraphesMenuBar(MenuBar):
    def __init__(self, panel):
        MenuBar.__init__(self, panel)
        self.ajouter(u"Fichier", [u"nouveau"], [u"ouvrir"], [u"ouvrir ici"], None,
                    [u"enregistrer"], [u"enregistrer_sous"], [u"exporter"],
                    [u"exporter&sauver"], None,
                    ['session'], None, [u"imprimer"], [u"presse-papier"],
                    None, [u"proprietes"], None, self.panel.doc_ouverts, None,
                    [u"fermer"], [u"quitter"])
        self.ajouter(u"Editer", [u"annuler"], [u"refaire"], [u"modifier"], [u"supprimer"])
        self.ajouter(u"creer")
        self.ajouter("affichage")
        self.ajouter("autres")
        self.ajouter(u"Outils",
#                        [u"Créer le graphe", u"(Entrée à supprimer).", "Ctrl+E", self.panel.creer_graphe],
                        [u"Colorier le graphe", u"Coloriage par l'algorithme de Welsh & Powell.", None, self.panel.colorier],
                        [u"Latex -> Presse-papier",
                            [u"Dijkstra", u"Recherche d'un trajet minimal entre deux points.", None, self.panel.latex_Dijkstra],
                            [u"Welsh & Powell", u"Coloriage par l'algorithme de Welsh & Powell.", None, self.panel.latex_WelshPowell],
                            [u"Matrice", u"Matrice du graphe.", None, self.panel.latex_matrix],
                            [u"Matrice (poids)", u"Matrice de graphe pondéré.", None, self.panel.latex_matrix_poids],
                            ],
                        [u"options"],
                        )
##        self.ajouter(u"Avancé", [u"historique"], [u"securise"], [u"ligne_commande"], [u"debug"])
        self.ajouter(u"avance1")
        self.ajouter(u"?")




class Graphes(Panel_API_graphique):

    titre = u"Graphes" # Donner un titre à chaque module
    #_param_ = _param_

    def __init__(self, *args, **kw):
        Panel_API_graphique.__init__(self, *args, BarreOutils = BarreOutilsGraphes, **kw)
        self.finaliser()


    def creer_graphe(self, event=None):
        aretes = list(self.feuille_actuelle.objets.segments)
        aretes_orientees = list(self.feuille_actuelle.objets.vecteurs)
        for arc in self.feuille_actuelle.objets.arcs:
            if isinstance(arc, Arc_oriente):
                aretes_orientees.append(arc)
            else:
                aretes.append(arc)

        def poids(arete):
            try:
                return float(arete.label().replace(',', '.'))
            except Exception:
                return 1

        sommets = [s for s in self.feuille_actuelle.objets.points if s.visible]


        dic = {}
        # Ex: {"A": {"B":[1], "C":[2, 5]}, "B": {}, "C": {"A": [2], "C": [1]}}
        for sommet in sommets:
            d_sommet = defaultdict(list)
            for arete in aretes:
                A, B = arete.extremites
                if sommet is A:
                    d_sommet[B.nom].append(poids(arete))
                elif sommet is B:
                    d_sommet[A.nom].append(poids(arete))
            for arete in aretes_orientees:
                A, B = arete.extremites
                if sommet is A:
                    d_sommet[B.nom].append(poids(arete))
            dic[nom(sommet)] = d_sommet

        self.graph = Graph(dic, oriented=bool(aretes_orientees),
                           labels = self.correspondance_noms_etiquette())

    def matrice(self, event=None, creer=True, poids=False):
        if creer:
            self.creer_graphe()
        if poids:
            return self.graph.matrix2(default=0)
        return self.graph.matrix

    def chaine_eulerienne(self, event=None, chaine=None):
        self.creer_graphe()
        return self.graph.eulerian_trail(chaine)

    def colorier(self, event=None):
        def rnd():
            return randint(5, 250)
            # Range is (5, 250) so as to avoid pure colors (most are already used).
        def rgb(r, g, b):
            return (r/255., g/255., b/255.)

        symbs = ('o', 'D', '*', 's', '<', '>', 'H', '^', 'd', 'h', 'p', 'v')

        self.creer_graphe()

        for sommets, colorname, i in zip(self.graph.coloring(), colors(), count()):
            couleur = colors_dict.get(colorname, (rnd(), rnd(), rnd()))
            for sommet in sommets:
                self.feuille_actuelle.objets[sommet].style(couleur=rgb(*couleur),
                                                           style=symbs[i%len(symbs)])
        self.feuille_actuelle.interprete.commande_executee()
        self.latex_WelshPowell(creer=False)

    def latex_Dijkstra(self, event=None, creer=True, start=None, end=None):
        ask = not (start and end)
        if creer:
            self.creer_graphe()
        if start is None:
            start = min(self.graph.nodes)
        if end is None:
            end = max(self.graph.nodes)
        if ask:
            while True:
                txt, ok = QInputDialog.getText(self, u"Précisez le départ et l'arrivée.",
                        u"Entrez le sommet de départ et le sommet d'arrivée (séparés par un espace).",
                        QLineEdit.Normal, '%s %s' % (start, end))
                if not ok:
                    return
                try:
                    start, end = re.split('[ ]*[, ][ ]*', txt.strip())
                    break
                except Exception:
                    print_error()

        latex_ = self.graph.latex_Dijkstra(start, end)
        self.vers_presse_papier(latex_)
        self.code_copie()

    def latex_WelshPowell(self, event=None, creer=True, first_nodes=()):
        if creer:
            self.creer_graphe()
        latex_ = self.graph.latex_WelshPowell(*first_nodes)
        self.vers_presse_papier(latex_)
        self.code_copie()

    def latex_matrix(self, event=None, creer=True):
        self.vers_presse_papier(latex(self.matrice(creer=creer)))
        self.code_copie()

    def latex_matrix_poids(self, event=None, creer=True):
        self.vers_presse_papier(latex(self.matrice(creer=creer, poids=True)))
        self.code_copie()

    def code_copie(self):
        self.canvas.message(u"Code LaTeX copié dans le presse-papier.")

    def correspondance_noms_etiquette(self):
        # On utilise les étiquettes si elles ne sont pas vides.
        correspondance = {}
        for s in self.feuille_actuelle.objets.points:
            if s.visible:
                label = s.label()
                if label != "":
                    correspondance[s.nom] = label
        return correspondance

