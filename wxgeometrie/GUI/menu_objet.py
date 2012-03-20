# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

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

from PyQt4.QtGui import (QDialog, QVBoxLayout, QHBoxLayout, QFrame, QLineEdit,
                         QInputDialog, QTextEdit, QLabel, QCheckBox, QPushButton,
                         QMenu,)
from PyQt4.QtCore import Qt

from ..geolib.constantes import NOM, FORMULE, TEXTE, RIEN
from ..geolib.textes import Texte_generique
from ..geolib.points import Point_generique
from .proprietes_objets import Proprietes
from ..pylib import print_error
from .wxlib import PopUpMenu


class MenuActionsObjet(PopUpMenu):
    def __init__(self, canvas):
        PopUpMenu.__init__(self, canvas.select.nom_complet, canvas, 'crayon')
        self.canvas = canvas
        select = canvas.select

        for obj in canvas.selections:
            if obj is not select:
                # Permet de sélectionner les autres objets à proximité
                action = self.addAction(u"Sélectionner " + obj.nom_complet)
                action.triggered.connect(partial(self.select, obj))
        if len(canvas.selections) > 1:
            self.addSeparator()

        action = self.addAction(u"Supprimer")
        commande = u"%s.supprimer()" % select.nom
        action.triggered.connect(partial(self.executer, commande))

        visible = select.style("visible")
        action = self.addAction(u"Masquer" if visible else u"Afficher")
        commande = u"%s.style(visible = %s)" % (select.nom, not visible)
        action.triggered.connect(partial(self.executer, commande))

        action = self.addAction(u"Renommer")
        action.triggered.connect(self.renommer)

        msg = u"Éditer le texte" if isinstance(select, Texte_generique) else u"Texte associé"
        action = self.addAction(msg)
        action.triggered.connect(self.etiquette)

        action = self.addAction((u"Masquer" if select.label() else u"Afficher") + u" nom/texte")
        action.triggered.connect(self.masquer_nom)

        self.addSeparator()

        action = self.addAction(u"Redéfinir")
        action.triggered.connect(self.redefinir)

        self.addSeparator()

        if isinstance(canvas.select, Point_generique):
            relier = self.addMenu(u"Relier le point")

            action = relier.addAction(u"aux axes")
            commande = u"%s.relier_axes()" %select.nom
            action.triggered.connect(partial(self.executer, commande))

            action = relier.addAction(u"à l'axe des abscisses")
            commande = u"%s.relier_axe_x()" %select.nom
            action.triggered.connect(partial(self.executer, commande))

            action = relier.addAction(u"à l'axe des ordonnées")
            commande = u"%s.relier_axe_y()" %select.nom
            action.triggered.connect(partial(self.executer, commande))

            self.addSeparator()

        action = self.addAction(u"Propriétés")
        action.triggered.connect(self.proprietes)

    def executer(self, commande):
        self.canvas.executer(commande)

    def select(self, obj):
        self.canvas.select = self.canvas.select_memoire = obj
        self.canvas.selection_en_gras()

    def renommer(self):
        u"Renomme l'objet, et met l'affichage de la légende en mode 'Nom'."
        select = self.canvas.select
        txt = select.nom_corrige
        label = u"Note: pour personnaliser davantage le texte de l'objet,\n" \
                u"choisissez \"Texte associé\" dans le menu de l'objet."

        while True:
            txt, ok = QInputDialog.getText(self.canvas, u"Renommer l'objet", label, QLineEdit.Normal, txt)
            if ok:
                try:
                    # On renomme, et on met l'affichage de la légende en mode "Nom".
                    self.executer(u"%s.renommer(%s, legende = %s)" %(select.nom, repr(txt), NOM))
                except:
                    print_error()
                    continue
            break

    def etiquette(self):
        select = self.canvas.select
        old_style = select.style().copy()
        old_label = select.style(u"label")
        if old_label is None:   # le style label n'existe pas pour l'objet
            return

        dlg = QDialog(self.canvas)
        dlg.setWindowTitle("Changer la légende de l'objet (texte quelconque)")

        sizer = QVBoxLayout()
        sizer.addWidget(QLabel(u"Note: le code LATEX doit etre entre $$. Ex: $\\alpha$"))

        dlg.text = QTextEdit(dlg)
        dlg.text.setPlainText(old_label)
        dlg.setMinimumSize(300, 50)
        sizer.addWidget(dlg.text)

        dlg.cb = QCheckBox(u"Interpréter la formule", dlg)
        dlg.cb.setChecked(select.style(u"legende") == FORMULE)
        sizer.addWidget(dlg.cb)

        line = QFrame(self)
        line.setFrameStyle(QFrame.HLine)
        sizer.addWidget(line)

        box = QHBoxLayout()
        btn = QPushButton('OK')
        btn.clicked.connect(dlg.accept)
        box.addWidget(btn)
        box.addStretch(1)
        btn = QPushButton(u"Annuler")
        btn.clicked.connect(dlg.reject)
        box.addWidget(btn)
        sizer.addLayout(box)

        dlg.setLayout(sizer)
        dlg.setWindowModality(Qt.WindowModal)

        while True:
            ok = dlg.exec_()
            if ok:
                try:
                    self.executer(u"%s.label(%s, %s)" %(select.nom, repr(dlg.text.toPlainText()), dlg.cb.isChecked()))
                except:
                    select.style(**old_style)
                    print_error()
                    continue
            else:
                select.label(old_label)
            break

    def masquer_nom(self):
        select = self.canvas.select
        if select.label():
            mode = RIEN
        else:
            if select.style(u"label"):
                mode = TEXTE
            else:
                mode = NOM
        self.executer(u"%s.style(legende = %s)" %(select.nom, mode))

    def redefinir(self):
        u"""Redéfinit l'objet (si possible).

        Par exemple, on peut remplacer `Droite(A, B)` par `Segment(A, B)`."""
        select = self.canvas.select
        txt = select._definition()
        label = u"Exemple: transformez une droite en segment."

        while True:
            txt, ok = QInputDialog.getText(self.canvas, u"Redéfinir l'objet", label, QLineEdit.Normal, txt)
            if ok:
                try:
                    # On renomme, et on met l'affichage de la légende en mode "Nom".
                    self.executer(u"%s.redefinir(%s)" %(select.nom, repr(txt)))
                except:
                    print_error()
                    continue
            break

    def proprietes(self):
        win = Proprietes(self.canvas, [self.canvas.select])
        win.show()
