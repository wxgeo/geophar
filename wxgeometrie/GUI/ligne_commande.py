# -*- coding: utf-8 -*-

##--------------------------------------##
#               Widget LigneCommande              #
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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QLineEdit, QLabel, QPushButton



class LigneCommande(QWidget):
    """Un TextCtrl muni d'un historique et associé à un bouton pour valider.

    On peut personnaliser le texte du bouton (via `texte="Mon texte"`),
    ou même directement le bouton, en utilisant `bouton=...`.
    """
    def __init__(self, parent, longueur = 500, texte = None, bouton = None,
                action = (lambda *args, **kw: True), afficher_bouton = True,
                legende = None):
        self.parent = parent
        self.action = action
        QWidget.__init__(self, parent)

        sizer = QHBoxLayout()
        self.texte = QLineEdit()
        self.texte.setMinimumWidth(longueur)
        if bouton is None:
            self.bouton = QPushButton('OK' if texte is None else texte)
        else:
            self.bouton = bouton
        self.bouton.setVisible(afficher_bouton)
        self.bouton.clicked.connect(self.valider)

        if legende is not None:
            sizer.addWidget(QLabel(legende, self))
        sizer.addWidget(self.texte)
        sizer.addWidget(self.bouton)
        self.setLayout(sizer)
        self.initialiser()


    def initialiser(self):
        self.historique = []
        self.position = None
        self.setFocus()
        self.clear()

    def text(self):
        return self.texte.text()

    def setText(self, value):
        self.texte.setText(value)

    def setFocus(self):
        self.texte.setFocus()

    def clear(self):
        self.texte.clear()

    def getSelection(self):
        if self.texte.hasSelectedText():
            start = self.texte.selectionStart()
            length = len(self.texte.selectedText())
            end = start + length
        else:
            start = end = self.texte.cursorPosition()
        return start, end

    def cursorPosition(self):
        return self.texte.cursorPosition()

    def setCursorPosition(self, num):
        return self.texte.setCursorPosition(num)

    def insert(self, texte):
        self.texte.insert(texte)

    def setSelection(self, deb, fin):
        self.texte.setSelection(deb, fin)

    def setToolTip(self, tip):
        self.texte.setToolTip(tip)

    def valider(self, **kw):
        # kw: shift|alt|meta|control=True|False'
        commande = str(self.text())
        self.position = None
        if commande:
            self.historique.append(commande)
        elif self.historique:
            # Appuyer une deuxième fois sur [Entrée] permet de répéter l'action précédente.
            commande = self.historique[-1]
        self.action(commande, **kw)


    def keyPressEvent(self, event):
        key = event.key()
        commande = self.text()

        if key == Qt.Key_Up and self.historique:
            # On remonte dans l'historique (-> entrées plus anciennes)
            if self.position is None:
                # cas d'une commande en cours d'édition :
                if commande:
                    if commande != self.historique[-1]:
                        # on enregistre la commande en cours
                        self.historique.append(commande)
                    self.position = len(self.historique) - 1
                else:
                    self.position = len(self.historique)
            if self.position > 0:
                self.position -= 1
                self.texte.setText(self.historique[self.position])

        elif key == Qt.Key_Down and self.historique:
            # On redescend dans l'historique (-> entrées plus récentes)
            if self.position is None or self.position == len(self.historique) - 1:
                if commande and commande != self.historique[-1]:
                    self.historique.append(commande)
                self.texte.clear()
                self.position = len(self.historique)
            elif self.position < len(self.historique) - 1:
                self.position += 1
                self.texte.setText(self.historique[self.position])
        elif key in (Qt.Key_Enter, Qt.Key_Return):
            modifiers = event.modifiers()
            kw = {'shift': modifiers & Qt.ShiftModifier,
                  'alt': modifiers & Qt.AltModifier,
                  'meta': modifiers & Qt.MetaModifier,
                  'control': modifiers & Qt.ControlModifier,
                      }
            self.valider(**kw)
        else:
            self.position = None
