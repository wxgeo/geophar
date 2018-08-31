# -*- coding: utf-8 -*-

##--------------------------------------#######
#                    Suites                   #
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

from operator import attrgetter

from PyQt5.QtWidgets import QDialog, QWidget, QLabel, QMenu, QLineEdit, \
    QPushButton, QFrame, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QCoreApplication

##from .wxlib import MyMiniFrame
from ..geolib.variables import Variable, Objet


# Nécessaire pour que l'affichage soit rafraîchi au sein d'une boucle.
Objet.souffler = QCoreApplication.processEvents


class DialogueAnimation(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setWindowTitle("Créer une animation")
        self.parent = parent
        self.feuille_actuelle = self.parent.onglet_actuel.feuille_actuelle

        self.sizer = sizer = QVBoxLayout()

        terme = QHBoxLayout()
        terme.addWidget(QLabel("Variable :"))
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
        terme.addWidget(QLabel("Début :"))
        self.deb = QLineEdit()
        self.deb.setText("0")
        self.deb.setMinimumWidth(25)
        terme.addWidget(self.deb)
        terme.addWidget(QLabel("Fin :"))
        self.fin = QLineEdit()
        self.fin.setText("1")
        self.fin.setMinimumWidth(25)
        terme.addWidget(self.fin)
        terme.addWidget(QLabel("Pas :"))
        self.pas = QLineEdit()
        self.pas.setText("0.05")
        self.pas.setMinimumWidth(25)
        terme.addWidget(self.pas)
        sizer.addLayout(terme)

        terme = QHBoxLayout()
        terme.addWidget(QLabel("Période (s) :"))
        self.periode = QLineEdit()
        self.periode.setText("0.1")
        self.periode.setMinimumWidth(50)
        terme.addWidget(self.periode)
        sizer.addLayout(terme)

        ##line = QFrame(self)
        ##line.setFrameStyle(QFrame.HLine)
        ##sizer.addWidget(line)

        boutons = QHBoxLayout()
        self.btn_lancer = QPushButton("Animer", clicked=self.Animer)
        boutons.addWidget(self.btn_lancer)
        boutons.addStretch(1)
        fermer = QPushButton("Fermer", clicked=self.close)
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
            self.feuille_actuelle.animer(nom=self.var.text(),
                        debut=self.evaluer(self.deb), fin=self.evaluer(self.fin),
                        pas=self.evaluer(self.pas), periode=self.evaluer(self.periode))
        self.en_cours = False
        self.btn_lancer.setText('Animer')

    def propositions(self):
        "Liste des noms de variables de la feuille actuelle."
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

    def evaluer(self, champ):
        return eval(champ.text(), self.feuille_actuelle.objets)
