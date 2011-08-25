# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#        Proprietes de la feuille             #
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

from PyQt4.QtGui import (QWidget, QTabWidget, QGridLayout, QLabel, QLineEdit,
                         QPushButton, QVBoxLayout, QTextEdit, QDialog)

from ..pylib import uu

class ProprietesDescription(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.feuille = parent.feuille
        gbs = QGridLayout()
        gbs.setSpacing(10)

        gbs.addWidget(QLabel(u"Titre : "), 1, 1)
        self.titre = titre = QLineEdit(self)
        titre.setText(self.feuille.infos("titre"))
        titre.setMinimumWidth(300)
        gbs.addWidget(titre, 1, 2)

        gbs.addWidget(QLabel(u"Auteur : "), 2, 1)
        self.auteur = auteur = QLineEdit(self)
        auteur.setText(self.feuille.infos("auteur"))
        auteur.setMinimumWidth(300)
        gbs.addWidget(auteur, 2, 2)

        gbs.addWidget(QLabel(u"Version : "), 3, 1)
        self.version = version = QLineEdit(self)
        version.setText(self.feuille.infos("version"))
        version.setMinimumWidth(300)
        gbs.addWidget(version, 3, 2)

        gbs.addWidget(QLabel(u"Resumé : "), 4, 1)
        self.resume = resume = QTextEdit(self)
        resume.setPlainText(self.feuille.infos("resume"))
        resume.setMinimumSize(300, 50)
        gbs.addWidget(resume, 4, 2)

        gbs.addWidget(QLabel(u"Notes : "), 5, 1)
        self.notes = notes = QTextEdit(self)
        notes.setPlainText(self.feuille.infos("notes"))
        notes.setMinimumSize(300, 100)
        gbs.addWidget(notes, 5, 2)

        boutons = QGridLayout()
        boutons.setSpacing(10)
        ok = QPushButton(u'OK', clicked=self.ok)
        appliquer = QPushButton(u"Appliquer", clicked=self.appliquer)
        effacer = QPushButton(u"Effacer", clicked=self.effacer)
        annuler = QPushButton(u"Annuler", clicked=self.annuler)

        boutons.addWidget(ok, 1, 0)
        boutons.addWidget(appliquer, 1, 1)
        boutons.addWidget(effacer, 1, 2)
        boutons.addWidget(annuler, 1, 3)
        ##boutons.addWidget(QLabel(''), 2, 1)
        gbs.addWidget(boutons, 6, 2)

        ##gbs.SetEmptyCellSize(wx.Size(10, 10))
        ##boutons.SetEmptyCellSize(wx.Size(4, 4))
        self.setLayout(gbs)
        ##self.parent.parent.dim1 = self.sizer.CalcMin().Get()

    def ok(self):
        self.appliquer()
        self.close()

    def appliquer(self):
        self.feuille.infos(titre=self.titre.text(), auteur=self.auteur.text(),
                           version=self.version.text(),
                           resume=self.resume.toPlainText(),
                           notes=self.notes.toPlainText())
        self.parent.parent.panel.rafraichir_titre()

    def effacer(self):
        self.titre.clear()
        self.auteur.clear()
        self.version.clear()
        self.resume.clear()
        self.notes.clear()



class ProprietesStatistiques(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.feuille = parent.feuille

        sizer = QVBoxLayout()
        sizer.addWidget(QLabel(u"Informations sur " + uu(self.feuille.nom) + " :"))
        sizer.addWidget(QLabel(u"Date de création :  " + uu(self.feuille.infos("creation"))))
        sizer.addWidget(QLabel(u"Dernière modification :  " + uu(self.feuille.infos("modification"))))
        sizer.addWidget(QLabel(u"Nombre d'objets :  " + str(len(self.feuille.liste_objets(True)))))
        self.setLayout(sizer)
#        self.parent.parent.dim2 = self.sizer.CalcMin().Get()



class OngletsProprietesFeuille(QTabWidget):
    def __init__(self, parent):
        self.parent = parent
        self.feuille = parent.feuille
        QTabWidget.__init__(self, parent)
        self.description = ProprietesDescription(self)
        self.addTab(self.description, u"Description")
        self.statistiques = ProprietesStatistiques(self)
        self.addTab(self.statistiques, u"Statistiques")




class ProprietesFeuille(QDialog):
    def __init__(self, parent, feuille):
        QDialog.__init__(self, parent)
        self.setWindowTitle(u"Propriétés de " + uu(feuille.nom))
        self.parent = parent
        self.feuille = feuille
        self.fenetre_principale = self
        while hasattr(self.fenetre_principale, "parent"): # detection de la fenetre principale de WxGeometrie.
            self.fenetre_principale = self.fenetre_principale.parent
        self.panel = self.fenetre_principale.onglets.onglet_actuel
        self.onglets = OngletsProprietesFeuille(self)
        ##self.SetSize(wx.Size(*(max(dimensions) + 50 for dimensions in zip(self.dim1, self.dim2))))
