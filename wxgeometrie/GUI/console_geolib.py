# -*- coding: utf-8 -*-

##--------------------------------------##
#               Console pour geolib               #
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

from PyQt4.QtGui import QWidget, QVBoxLayout, QLabel

from .app import white_palette
from .ligne_commande import LigneCommande
from ..pylib import print_error


class ConsoleGeolib(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.setPalette(white_palette)
        vsizer = QVBoxLayout()
        txt = "<i>Tapez une commande ci-dessus, puis appuyez sur </i>[<i>Entrée</i>]<i>.</i>"
        self.resultats = QLabel(txt)
        self.resultats.setMinimumWidth(500)
        self.ligne_commande = LigneCommande(self, longueur=500, action=self.action)
        vsizer.addWidget(self.ligne_commande)
        vsizer.addWidget(self.resultats)
        self.setLayout(vsizer)

    def action(self, commande, **kw):
        try:
            resultat = self.parent.feuille_actuelle.executer(commande)
            self.resultats.setText(resultat)
            print(resultat)
            self.ligne_commande.clear()
        except:
            print_error()
            self.resultats.setText('Erreur.')
