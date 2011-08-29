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

from operator import attrgetter

from PyQt4.QtGui import (QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMenu,
                         QLineEdit, QPushButton, QFrame,)
from PyQt4.QtCore import Qt

##from .wxlib import MyMiniFrame
from ..geolib.variables import Variable


class DialogueAnimation(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setWindowTitle(u"Créer une animation")
        self.parent = parent
        self.feuille_actuelle = self.parent.onglet_actuel.feuille_actuelle

        self.sizer = sizer = QVBoxLayout()

        terme = QHBoxLayout()
        terme.addWidget(QLabel(u"Variable :"))
        self.var = var = QLineEdit()
        var.setMinimumWidth(50)
        var.setContextMenuPolicy(Qt.CustomContextMenu)
        var.customContextMenuRequested.connect(self.propositions)
        terme.addWidget(var)
        sizer.addLayout(terme)

        ##line = QFrame(self)
        ##line.setFrameStyle(QFrame.HLine)
        ##sizer.addWidget(line)

        terme = QHBoxLayout()
        terme.addWidget(QLabel(u"Début :"))
        self.deb = QLineEdit()
        self.deb.setText("0")
        self.deb.setMinimumWidth(25)
        terme.addWidget(self.deb)
        terme.addWidget(QLabel(u"Fin :"))
        self.fin = QLineEdit()
        self.fin.setText("1")
        self.fin.setMinimumWidth(25)
        terme.addWidget(self.fin)
        terme.addWidget(QLabel(u"Pas :"))
        self.pas = QLineEdit()
        self.pas.setText("0.05")
        self.pas.setMinimumWidth(25)
        terme.addWidget(self.pas)
        sizer.addLayout(terme)

        terme = QHBoxLayout()
        terme.addWidget(QLabel(u"Période (s) :"))
        self.periode = QLineEdit()
        self.periode.setText("0.1")
        self.periode.setMinimumWidth(50)
        terme.addWidget(self.periode)
        sizer.addLayout(terme)

        ##line = QFrame(self)
        ##line.setFrameStyle(QFrame.HLine)
        ##sizer.addWidget(line)

        boutons = QHBoxLayout()
        self.btn_lancer = QPushButton(u"Animer", clicked=self.Animer)
        boutons.addWidget(self.btn_lancer)
        boutons.addStretch(1)
        fermer = QPushButton(u"Fermer", clicked=self.close)
        boutons.addWidget(fermer)
        sizer.addLayout(boutons)

        self.setLayout(sizer)

        self.en_cours = False


    def Animer(self):
        if self.en_cours:
            self.feuille_actuelle.stop()
        else:
            self.en_cours = True
            self.btn_lancer.setText('Stop')
            self.feuille_actuelle.animer(nom = self.var.text(),
                        debut=float(self.deb.text()), fin=float(self.fin.text()),
                        pas=float(self.pas.text()), periode=float(self.periode.text()))
        self.en_cours = False
        self.btn_lancer.setText('Animer')

    def propositions(self):
        u"Liste des noms de variables de la feuille actuelle."
        self.var.setFocus()
        liste_objets = self.feuille_actuelle.objets.lister(False, type = Variable)
        liste_objets.sort(key=attrgetter('nom')) # ordre alphabétique
        if liste_objets:
            menu = QMenu()
            for obj in liste_objets:
                action = menu.addAction(obj.nom_complet)
                action.nom = obj.nom
            action = menu.exec_()
            if action:
                self.var.setText(action.nom)
