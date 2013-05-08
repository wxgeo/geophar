# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##------------------------------------------#######
#                   Experience                   #
##------------------------------------------#######
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

from PyQt4.QtGui import (QWidget, QSpinBox, QCheckBox, QPushButton,
                         QVBoxLayout, QLabel, QHBoxLayout, QLineEdit)
from numpy.random import rand
import math
from numpy import sum
# NB: numpy.sum est 100 fois plus rapide que __builtin__.sum !

from ...GUI.qtlib import MyMiniFrame
from ...pylib import msplit

ent = int

def alea(n = None):
    u"""Nombre entier aléatoire compris entre 0 et n-1.
    Si n = None, nombre décimal entre 0 et 1."""
    if n == None:
        return rand()
    return int(n*rand())

def de(k = 1):
    return sum(1+(6*rand(k)).astype(int))


def sondage(pourcentage = 50, k = 1000):
    pourcentage /= 100.
    return 100.*sum(rand(k)<pourcentage)/k

DIC = {'rand': rand, 'random': rand, 'ent': ent, 'alea': alea}
DIC.update(math.__dict__)




class ExperienceFrame(MyMiniFrame):
    def __init__(self, parent):

        MyMiniFrame.__init__(self, parent, u"Simulation d'une expérience")
        self.parent = parent

        sizer = QVBoxLayout()
        exp = QHBoxLayout()
        exp.addWidget(QLabel(u"Experience:"))
        self.experience = QLineEdit()
        self.experience.setMinimumWidth(120)
        self.experience.returnPressed.connect(self.actualiser)
        exp.addWidget(self.experience)
        sizer.addLayout(exp)

        nbr = QHBoxLayout()
        nbr.addWidget(QLabel(u"Nombre d'expériences:"))
        sc = self.sc = QSpinBox()
        sc.setRange(1, 100000)
        sc.setValue(5)
        sc.valueChanged.connect(self.actualiser)
        nbr.addWidget(sc)
        sizer.addLayout(nbr)

        val = QHBoxLayout()
        val.addWidget(QLabel(u"Valeurs possibles:"))
        self.valeurs = QLineEdit()
        self.valeurs.setMinimumWidth(120)
        self.valeurs.returnPressed.connect(self.actualiser)
        val.addWidget(self.valeurs)
        sizer.addLayout(val)

        self.cb = QCheckBox(u"Lancer une animation:")
        sizer.addWidget(self.cb)
        self.cb.stateChanged.connect(self.actualiser)

        boutons = QHBoxLayout()
        fermer = QPushButton(u"Fermer")
        boutons.addWidget(fermer)
        lancer = QPushButton(u"Lancer l'experience")
        boutons.addWidget(lancer)
        fermer.clicked.connect(self.close)
        lancer.clicked.connect(self.actualiser)

        sizer.addLayout(boutons)
        self.setLayout(sizer)


    def actualiser(self, event = None):
        n = self.sc.value()
        exp = self.experience.text()
        vals = msplit(self.valeurs.text(), (" ", ",", ";"))
        print alea
        if exp:
            self.parent.experience(exp, n, [eval(val, DIC) for val in vals if val])





class LancerDes(MyMiniFrame):
    def __init__(self, parent):

        MyMiniFrame.__init__(self, parent, u"Simulation de lancers de dés")
        self.parent = parent

        sizer = QVBoxLayout()
        sizer.addWidget(QLabel(u"On simule le lancer d'un ou plusieurs dés"))
        sizer.addWidget(QLabel(u"à 6 faces, et on étudie la somme des points."))
        exp = QHBoxLayout()
        exp.addWidget(QLabel(u"Nombre de dés:"))
        ex = self.experience = QSpinBox()
        ex.setRange(1, 100000)
        ex.setValue(1)
        ex.valueChanged.connect(self.actualiser)
        exp.addWidget(self.experience)
        sizer.addLayout(exp)

        nbr = QHBoxLayout()
        nbr.addWidget(QLabel(u"Nombre de lancers:"))
        sc = self.sc = QSpinBox()
        sc.setRange(1, 100000)
        sc.setValue(1)
        self.sc.valueChanged.connect(self.actualiser)
        nbr.addWidget(sc)
        sizer.addLayout(nbr)

        self.cb = QCheckBox(u"Conserver les valeurs")
        sizer.addWidget(self.cb)


        boutons = QHBoxLayout()
        fermer = QPushButton(u"Fermer")
        boutons.addWidget(fermer)
        lancer = QPushButton(u"Lancer l'expérience")
        boutons.addWidget(lancer)
        fermer.clicked.connect(self.close)
        lancer.clicked.connect(self.actualiser)

        sizer.addLayout(boutons)
        self.setLayout(sizer)


    def actualiser(self, event = None):
        if not self.cb.isChecked():
            self.parent.actualiser(False)
        self.parent.graph = 'batons'
        n = self.sc.value()
        des = self.experience.value()
        for val in range(des, 6*des + 1):
            self.parent.ajouter_valeur(val, 0)
        self.parent.ajouter_valeurs(*[de(des) for i in xrange(n)])
        self.parent.calculer()
        self.parent.legende_x = u"points obtenus"
        self.parent.legende_y = u"nombre de lancers"
        self.parent.affiche()





class Sondage(MyMiniFrame):
    def __init__(self, parent):

        MyMiniFrame.__init__(self, parent, u"Simulation d'un sondage")
        self.parent = parent

        sizer = QVBoxLayout()
        sizer.addWidget(QLabel(u"On simule un sondage simple (réponse par oui ou non)."))
        sizer.addWidget(QLabel(u"Exemple: \"préférez-vous le candidat A au candidat B ?\""))
        exp = QHBoxLayout()
        exp.addWidget(QLabel(u"Pourcentage de réponses affirmatives sur l'ensemble de la population:"))
        ex = self.experience = QSpinBox()
        ex.setRange(0, 100)
        ex.setValue(50)
        ex.valueChanged.connect(self.actualiser)
        exp.addWidget(self.experience)
        sizer.addLayout(exp)

        nbr = QHBoxLayout()
        nbr.addWidget(QLabel(u"Taille de l'echantillon:"))
        sc = self.sc1 = QSpinBox()
        sc.setRange(1, 100000)
        sc.setValue(1000)
        sc.valueChanged.connect(self.actualiser)
        nbr.addWidget(sc)
        sizer.addLayout(nbr)

        self.cb = QCheckBox(u"Afficher l'intervalle de fluctuation")
        sizer.addWidget(self.cb)
        self.cb.stateChanged.connect(self.EvtCheckBox)


        nbr = QHBoxLayout()
        nbr.addWidget(QLabel(u"Nombre de sondages:"))
        sc = self.sc2 = QSpinBox()
        sc.setRange(1, 100000)
        sc.setValue(1)
        sc.valueChanged.connect(self.actualiser)
        nbr.addWidget(sc)
        sizer.addLayout(nbr)


        boutons = QHBoxLayout()
        fermer = QPushButton(u"Fermer")
        boutons.addWidget(fermer)
        lancer = QPushButton(u"Lancer l'experience")
        boutons.addWidget(lancer)
        lancer.setDefault(True)
        fermer.clicked.connect(self.close)
        lancer.clicked.connect(self.actualiser)

        sizer.addLayout(boutons)
        self.setLayout(sizer)


    def actualiser(self, event = None):
        self.parent.actualiser(False)
        self.parent.graph = 'batons'
        echantillon = self.sc1.value()
        self.parent.intervalle_fluctuation = (echantillon if self.cb.isChecked() else None)
        n = self.sc2.value()
        esperance = self.experience.value()
        self.parent.ajouter_valeurs(*[sondage(esperance, echantillon) for i in xrange(n)])
        self.parent.calculer()
        self.parent.legende_x = u"résultat des sondages (en %)"
        self.parent.legende_y = u"nombre de sondages"
        self.parent.affiche()


    def EvtCheckBox(self, event):
        echantillon = self.sc1.value()
        self.parent.intervalle_fluctuation = (echantillon if self.cb.isChecked() else None)
        self.parent.affiche()

    def closeEvent(self, event):
        self.parent.intervalle_fluctuation = None

