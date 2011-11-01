# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

##------------------------------------------#######
#                   Satistiques                   #
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

#from GUI import *

#from functools import partial

from PyQt4.QtGui import (QWidget, QTabWidget, QCheckBox, QGroupBox,
                         QVBoxLayout, QLabel, QHBoxLayout, QComboBox,
                         QLayout, QLineEdit)


class CstmPanel(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.main = self.parent.parent
        self.setStyleSheet("background-color:white")
        self.main_sizer = QVBoxLayout()

    def finaliser(self):
        self.setLayout(self.main_sizer)
        self.adjustSize()

    def add(self, item):
        if isinstance(item, QLayout):
            self.main_sizer.addLayout(item)
        else:
            self.main_sizer.addWidget(item)


class Donnees(CstmPanel):
    def __init__(self, parent):
        CstmPanel.__init__(self, parent)
        sizer = QHBoxLayout()
        sizer.addWidget(QLabel(u"Effectifs et valeurs associées:  "))
        self.valeurs = QLineEdit()
        self.valeurs.setText(self.main.donnees_valeurs)
        self.valeurs.setMinimumWidth(500)
        aide = u"Valeurs simples:\n8 8 9 12 17 18\nEffectifs et valeurs:\n2*7 14*8 5*9 1*10\nClasses et effectifs:\n17*[0;10[ 24*[10;20["
        self.valeurs.setToolTip(aide)
        self.valeurs.returnPressed.connect(self.main.actualiser)
        sizer.addWidget(self.valeurs)
        self.add(sizer)

        sizer = QHBoxLayout()
        self.sc = QLabel(u"Regroupement par classes:  ")
        sizer.addWidget(self.sc)
        self.classes = QLineEdit()
        self.classes.setText(self.main.donnees_classes)
        self.classes.setMinimumWidth(500)
        self.classes.setToolTip(u"Exemple:\n[0;10[ [10;20[ [20;30[")
        self.classes.returnPressed.connect(self.main.actualiser)
        sizer.addWidget(self.classes)
        self.add(sizer)

        self.finaliser()


class Legende(CstmPanel):
    def __init__(self, parent):
        CstmPanel.__init__(self, parent)
        # Légendes
        box = QGroupBox(u"Légende des axes")
        sizer = QHBoxLayout()
        box.setLayout(sizer)

        self.sx = QLabel(u"Abscisses:")
        sizer.addWidget(self.sx)
        self.x = QLineEdit()
        self.x.setText(self.main.legende_x)
        self.x.setMinimumWidth(200)
        self.x.returnPressed.connect(self.main.actualiser)
        sizer.addWidget(self.x)

        self.sy = QLabel(u"Ordonnées:")
        sizer.addWidget(self.sy)
        self.y = QLineEdit()
        self.y.setText(self.main.legende_y)
        self.y.setMinimumWidth(200)
        self.y.returnPressed.connect(self.main.actualiser)
        sizer.addWidget(self.y)

        self.sa = QLabel(u"Aire:")
        sizer.addWidget(self.sa)
        self.a = QLineEdit()
        self.a.setText(self.main.legende_a)
        self.a.setMinimumWidth(100)
        self.a.setToolTip(u"Pour les histogrammes.\nIndique en quelle unité s'exprime la quantité.\nExemples:\npersonnes, ampoules, %, $, ...")
        self.a.returnPressed.connect(self.main.actualiser)
        sizer.addWidget(self.a)
        self.add(box)

        self.finaliser()


class Graduation(CstmPanel):
    def __init__(self, parent):
        CstmPanel.__init__(self, parent)
        msizer = QHBoxLayout()
        # Graduations
        box = QGroupBox(u"Taille d'une graduation")
        sizer = QHBoxLayout()
        box.setLayout(sizer)

        self.sx = QLabel(u"Abscisses:")
        sizer.addWidget(self.sx)
        self.x = QLineEdit()
        self.x.setText(self.main.gradu_x)
        self.x.setMinimumWidth(50)
        self.x.setToolTip(u"Graduation en abscisses.")
        self.x.returnPressed.connect(self.main.actualiser)
        sizer.addWidget(self.x)

        self.sy = QLabel(u"Ordonnées:")
        sizer.addWidget(self.sy)
        self.y = QLineEdit()
        self.y.setText(self.main.gradu_y)
        self.y.setMinimumWidth(50)
        self.y.setToolTip(u"Graduation en ordonnées.")
        self.y.returnPressed.connect(self.main.actualiser)
        sizer.addWidget(self.y)

        self.sa = QLabel(u"Aire:")
        sizer.addWidget(self.sa)
        self.a = QLineEdit()
        self.a.setText(self.main.gradu_a)
        self.a.setMinimumWidth(50)
        self.a.setToolTip(u"Dimensions du carré ou rectangle donnant l'échelle.\nExemple:\n 1 (carré), 1x2 (rectangle)")
        self.a.returnPressed.connect(self.main.actualiser)
        sizer.addWidget(self.a)
        msizer.addWidget(box)

        msizer.addWidget(QLabel('   '))

        # Origine
        box = QGroupBox(u"Origine des axes")
        sizer = QHBoxLayout()
        box.setLayout(sizer)

        self.sox = QLabel(u"Abscisses:")
        sizer.addWidget(self.sox)
        self.origine_x = QLineEdit()
        self.origine_x.setText(self.main.origine_x)
        self.origine_x.setMinimumWidth(50)
        self.origine_x.setToolTip(u"Origine de l'axe des abscisses.")
        self.origine_x.returnPressed.connect(self.main.actualiser)
        sizer.addWidget(self.origine_x)

        self.soy = QLabel(u"Ordonnées:")
        sizer.addWidget(self.soy)
        self.origine_y = QLineEdit()
        self.origine_y.setText(self.main.origine_y)
        self.origine_y.setMinimumWidth(50)
        self.origine_y.setToolTip(u"Origine de l'axe des ordonnées.")
        self.origine_y.returnPressed.connect(self.main.actualiser)
        sizer.addWidget(self.origine_y)

        msizer.addWidget(box)

        self.add(msizer)

        self.finaliser()


class Autres(CstmPanel):
    def __init__(self, parent):
        CstmPanel.__init__(self, parent)
        sizer = QHBoxLayout()
        vsizer = QVBoxLayout()


        hsizer = QHBoxLayout()
        self.sm = QLabel(u'Affichage des effectifs:  ')
        hsizer.addWidget(self.sm)
        self.mode = QComboBox()
        self.mode.addItems((u'tels quels', u'en pourcentages', u'en fréquences'))
        self.mode.setCurrentIndex(self.main.param("mode_effectifs"))
        self.mode.currentIndexChanged.connect(self.main.EvtCheck)
        hsizer.addWidget(self.mode)

        vsizer.addLayout(hsizer)

        sizer.addLayout(vsizer)

        vsizer = QVBoxLayout()

        #~ self.pourcentages = wx.CheckBox(u'Effectifs en Pourcentages.   ')
        #~ self.pourcentages.SetValue(self.main.param("mode_pourcentages"))
        #~ self.pourcentages.stateChanged.connect(self.main.EvtCheck)
        #~ vsizer.addWidget(self.pourcentages, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 7)

        self.hachures = QCheckBox(u'Mode noir et blanc (hachures).')
        self.hachures.setChecked(self.main.param("hachures"))
        self.hachures.stateChanged.connect(self.main.EvtCheck)
        vsizer.addWidget(self.hachures)

        self.auto = QCheckBox(u"Réglage automatique de la fenêtre d'affichage.")
        self.auto.setChecked(self.main.param("reglage_auto_fenetre"))
        self.auto.stateChanged.connect(self.main.EvtCheck)
        vsizer.addWidget(self.auto)

        sizer.addLayout(vsizer, 0)
        self.add(sizer)

        self.finaliser()

class Autres_quantile(CstmPanel):
    def __init__(self, parent):
        CstmPanel.__init__(self, parent)

        box = QGroupBox(u"Construction de quantiles")
        sizer = QHBoxLayout()
        box.setLayout(sizer)

        self.mediane = QCheckBox(u'Construire la médiane')
        self.mediane.setChecked(self.main.choix_quantiles["mediane"][0])
        self.mediane.stateChanged.connect(self.main.EvtCheck)

        sizer.addWidget(self.mediane)
        sizer.addSpacing(10) # valeur à ajuster

        self.quartiles = QCheckBox(u'Construire les quartiles')
        self.quartiles.setChecked(self.main.choix_quantiles["quartiles"][0])
        self.quartiles.stateChanged.connect(self.main.EvtCheck)
        sizer.addWidget(self.quartiles)
        sizer.addSpacing(10) # valeur à ajuster

        self.deciles = QCheckBox(u'Construire les déciles')
        self.deciles.setChecked(self.main.choix_quantiles["deciles"][0])
        self.deciles.stateChanged.connect(self.main.EvtCheck)
        sizer.addWidget(self.deciles)
        sizer.addSpacing(10) # valeur à ajuster

        self.add(box)

        self.finaliser()


class OngletsStatistiques(QTabWidget):
    def __init__(self, parent):
        self.parent = parent
        QTabWidget.__init__(self, parent)
        self.donnees = Donnees(self)
        self.legende = Legende(self)
        self.graduation = Graduation(self)
        self.autres = Autres(self)
        self.autresq = Autres_quantile(self)

        self.addTab(self.donnees, u'Données')
        self.addTab(self.legende, u'Légende')
        self.addTab(self.graduation, u'Graduation')
        self.addTab(self.autres, u'Réglages')
        self.addTab(self.autresq, u'Quantiles')


    def enable(self, x, y, a, classes=False, legende_x=False):
        self.donnees.classes.setEnabled(a or classes)
        self.donnees.sc.setEnabled(a or classes)

        self.legende.setEnabled(x or y or a or legende_x)
        self.legende.x.setEnabled(x or legende_x)
        self.legende.sx.setEnabled(x or legende_x)
        self.legende.y.setEnabled(y)
        self.legende.sy.setEnabled(y)
        self.legende.a.setEnabled(a)
        self.legende.sa.setEnabled(a)

        self.graduation.setEnabled(x or y or a)
        self.graduation.x.setEnabled(x)
        self.graduation.sx.setEnabled(x)
        self.graduation.y.setEnabled(y)
        self.graduation.sy.setEnabled(y)
        self.graduation.a.setEnabled(a)
        self.graduation.sa.setEnabled(a)
        self.graduation.origine_x.setEnabled(x)
        self.graduation.sox.setEnabled(x)
        self.graduation.origine_y.setEnabled(y)
        self.graduation.soy.setEnabled(y)

        self.autres.mode.setEnabled(y or a)
        self.autres.sm.setEnabled(y or a)
