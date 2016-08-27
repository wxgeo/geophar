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

from PyQt4.QtGui import (QWidget, QLabel, QHBoxLayout)

from ...GUI.barre_outils import BarreOutils
from ...geolib import Arc_oriente, Arc_points, Point_generique


class BarreOutilsExEqDte(BarreOutils):
    def __init__(self, parent):
        self.parent = parent
        QWidget.__init__(self, parent)
        self._selected_button = None

        self.sizer = QHBoxLayout()

        if self.parent.param('afficher_boutons'):
            self.creer_boutons()

        self.sizer.addStretch()

        self.sizer.addWidget(QLabel("Utilisez cette barre d'outils pour construire les droites (dans le bon ordre).<br>"
                       "<i>Remarque :</i> pour créer une droite, il vous faudra deux points à coordonnées <i>entières</i>."))

        self.sizer.addStretch()
        self.setLayout(self.sizer)
        self.adjustSize()


    def creer_boutons(self):
        self.add("F1", ("Pointeur", "fleche4", "Déplacer ou modifier un objet.", self.curseur)).select()
        self.add("F3", ("Droite", "droite2", "Créer une droite.", self.droite))
        self.add("F4", ("Gommer", "gomme", "Supprimer des objets.", self.gomme))


    def rafraichir(self):
        pass
