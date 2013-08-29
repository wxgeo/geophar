# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

#    :--------------------------------------------:
#    :                  Traceur                   :
#    :--------------------------------------------:
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

from functools import partial
import re

from PyQt4.QtGui import (QCheckBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                         QGroupBox)
from PyQt4.QtCore import pyqtSignal

from ...GUI.menu import MenuBar
from ...GUI.panel import Panel_API_graphique
from ...geolib import Courbe, Fonction
from . import suites


class TraceurMenuBar(MenuBar):
    def __init__(self, panel):
        MenuBar.__init__(self, panel)

        self.ajouter(u"Fichier", [u"nouveau"], [u"ouvrir"], [u"ouvrir ici"], None,
                                 [u"enregistrer"], [u"enregistrer_sous"],
                                 [u"exporter"], [u"exporter&sauver"], None,
                                 [u'session'], None,
                                 [u"imprimer"], [u"presse-papier"], None,
                                 [u"proprietes"], None,
                                 self.panel.doc_ouverts, None,
                                 ["fermer"], ["quitter"])
        self.ajouter(u"Editer", ["annuler"], ["refaire"], ["modifier"], ["supprimer"])
        self.ajouter(u"creer")
        self.ajouter("affichage")
        self.ajouter("autres")
        self.ajouter(u"Outils",
        #[u"Tableau de valeurs", u"Tableaux de valeurs des fonctions.", u"Ctrl+T", self.panel.tableau],
        [u"Représenter une suite", u"Représenter une suite numérique.", None, self.panel.suite],
        None, [u"options"])
        self.ajouter(u"avance1")
        self.ajouter(u"?")



class TCheckBox(QCheckBox):
    enter = pyqtSignal()
    leave = pyqtSignal()

    def enterEvent(self, event):
        self.enter.emit()
        QCheckBox.enterEvent(self, event)

    def leaveEvent(self, event):
        self.leave.emit()
        QCheckBox.leaveEvent(self, event)

class TLineEdit(QLineEdit):
    enter = pyqtSignal()
    leave = pyqtSignal()

    def enterEvent(self, event):
        self.enter.emit()
        QLineEdit.enterEvent(self, event)

    def leaveEvent(self, event):
        self.leave.emit()
        QLineEdit.leaveEvent(self, event)


class Traceur(Panel_API_graphique):

    titre = u"Traceur de courbes" # Donner un titre a chaque module

    def __init__(self, *args, **kw):
        Panel_API_graphique.__init__(self, *args, **kw)

        self.couleurs = u"bgrmkcy"

        self.nombre_courbes = self._param_.nombre_courbes
        self.boites = []
        self.equations = []
        self.intervalles = []

        eq_box = QGroupBox(u"Équations")
        entrees = QVBoxLayout()
        eq_box.setLayout(entrees)

        for i in range(self.nombre_courbes):
            ligne = QHBoxLayout()

            check = TCheckBox('f%s:'%(i+1))
            self.boites.append(check)
            check.setChecked(True) # Par defaut, les cases sont cochees.
            check.stateChanged.connect(self.synchronise_et_affiche)
            check.enter.connect(partial(self.select, i))
            check.leave.connect(self.select)
            ligne.addWidget(check)

            ligne.addWidget(QLabel("Y ="))

            eq = TLineEdit()
            self.equations.append(eq)
            eq.setMinimumWidth(120)
            eq.enter.connect(partial(self.select, i))
            eq.leave.connect(self.select)
            eq.returnPressed.connect(partial(self.valider, i))
            ligne.addWidget(eq)

            ligne.addWidget(QLabel("sur"))

            intervalle = TLineEdit()
            self.intervalles.append(intervalle)
            intervalle.setMinimumWidth(100)
            intervalle.enter.connect(partial(self.select, i))
            intervalle.leave.connect(self.select)
            intervalle.returnPressed.connect(partial(self.valider, i))
            ligne.addWidget(intervalle)

            entrees.addLayout(ligne)
        entrees.addStretch()

        self.sizer = QHBoxLayout()
        self.sizer.addWidget(self.canvas, 1)
        self.sizer.addWidget(eq_box)
        self.finaliser(contenu=self.sizer)
        self._changement_feuille()


    def activer(self):
        Panel_API_graphique.activer(self)
        # Actions à effectuer lorsque l'onglet devient actif
        self.equations[0].setFocus()

    def _changement_feuille(self):
        u"""Après tout changement de feuille."""
        if hasattr(self, 'nombre_courbes'): # initialisation terminée
            self._synchroniser_champs()
            self.feuille_actuelle.lier(self._synchroniser_champs)


    def _synchroniser_champs(self):
        u"""On synchronise le contenu des champs de texte avec les courbes.

        Lors de l'ouverture d'un fichier, ou d'un changement de feuille,
        ou lorsqu'une commande est exécutée dans la feuille."""
        print "Synchronisation des champs..."
        for i in xrange(self.nombre_courbes):
            nom_courbe = 'Cf' + str(i + 1)
            if self.feuille_actuelle.objets.has_key(nom_courbe):
                objet = self.feuille_actuelle.objets[nom_courbe]
                self.boites[i].setChecked(objet.style('visible'))
                expression = objet.fonction.expression
                if expression.strip():
                    self.equations[i].setText(expression)
                    self.boites[i].setEnabled(True)
                else:
                    self.boites[i].setEnabled(False)
                ensemble = objet.fonction.ensemble
                ensemble = re.sub(r"(?<=[][])\+(?=[][])", 'U', ensemble)
                extremites_cachees = (str(e) for e in objet.fonction.style('extremites_cachees'))
                parties = ensemble.split('|')

                j = 0
                for partie, extremites in zip(parties, extremites_cachees):
                    def f(m):
                        a, b, c, d = m.groups()
                        return (a if b not in extremites else ' ') + b + ';' \
                                + c + (d if c not in extremites else ' ')
                    parties[j] = re.sub(r"([][])([^][;]+);([^][;]+)([][])", f, partie)
                    j += 1

                self.intervalles[i].setText('|'.join(parties))
            else:
                self.boites[i].setEnabled(False)
                self.equations[i].setText('')
                self.intervalles[i].setText('')

    def _synchroniser_courbes(self):
        u"""Opération inverse : on synchronise les courbes avec le contenu des champs de texte.

        Après un changement dans les champs de textes/cases à cocher."""
        objets = self.feuille_actuelle.objets
        for i in xrange(self.nombre_courbes):
            nom_courbe = 'Cf' + str(i + 1)
            nom_fonction = 'f' + str(i + 1)
            expr = self.equations[i].text()
            ensemble = self.intervalles[i].text()
            visible = self.boites[i].isChecked()
            if not expr.strip():
                visible = False
#                self.boites[i].Disable()
            if self.feuille_actuelle.objets.has_key(nom_fonction):
                objets[nom_fonction].modifier_expression_et_ensemble(expression=expr, ensemble=ensemble)
            else:
                objets[nom_fonction] = Fonction(expr, ensemble, 'x')
            if self.feuille_actuelle.objets.has_key(nom_courbe):
                objets[nom_courbe].style(visible = visible)
            else:
                f = objets[nom_fonction]
                objets[nom_courbe] = Courbe(f, visible=visible,
                                            couleur=self.couleurs[i%len(self.couleurs)])


    def _ouvrir(self, fgeo):
        Panel_API_graphique._ouvrir(self, fgeo)
        # On synchronise le contenu des champs de texte avec les courbes *à la fin*.
        self._synchroniser_champs()

    ##def EvtChar(self, event=None, i=None):
        ##assert (i is not None)
        ##code = (event.GetKeyCode() if event is not None else wx.WXK_RETURN)
##
        ##if code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            ##self.boites[i].SetValue(event is None or not event.ShiftDown())
            ##self.synchronise_et_affiche()
        ##elif code == wx.WXK_ESCAPE:
            ##self.boites[i].SetValue(False)
            ##self.synchronise_et_affiche()
        ##else:
            ##event.Skip()
    def valider(self, i):
        self.boites[i].setEnabled(True)
        self.boites[i].setChecked(True)
        self.synchronise_et_affiche()
        ##if (self.boites[i].underMouse() or self.equations[i].underMouse() or
            ##self.intervalles[i].underMouse()):
            ##self.select(i)
            # XXX: la courbe ne se met pas en gras

    def select(self, i=None):
        if i is None:
            self.canvas.select = None
        else:
            nom_courbe = 'Cf' + str(i + 1)
            self.canvas.select = self.feuille_actuelle.objets.get(nom_courbe, None)
        self.canvas.selection_en_gras()

    def synchronise_et_affiche(self):
        self._synchroniser_courbes()
        self.action_effectuee(u'Courbes modifiées.')
        self.affiche()
        #event.Skip()

#    def tableau(self, event = None):
#        self.parent.a_venir()
#        return
#        table = tableau.TableauValeurs(self)
#        table.Show(True)
        #table.SetSize(wx.Size(200,250))
        #table.SetDimensions(-1, -1, -1, 300)


    def suite(self):
        suite = suites.CreerSuite(self)
        suite.show()
