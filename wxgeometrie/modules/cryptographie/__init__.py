#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                Calculatrice                 #
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


from string import ascii_uppercase as majuscules
from functools import partial
from itertools import cycle, izip
from random import shuffle
import re

from PyQt4.QtGui import (QVBoxLayout, QInputDialog, QPushButton,
                         QTextEdit, QGridLayout, QLabel, QLineEdit, QSpacerItem)
from PyQt4.QtCore import Qt, QTimer

from ...GUI import MenuBar, Panel_simple
from ...pylib import print_error
from ... import param


dict_accents = {
u"é": "E",
u"É": "E",
u"ê": "E",
u"Ê": "E",
u"è": "E",
u"È": "E",
u"à": "A",
u"À": "A",
u"â": "A",
u"Â": "A",
u"ô": "O",
u"Ô": "O",
u"î": "I",
u"Î": "I",
u"ù": "U",
u"Ù": "U",
u"û": "U",
u"Û": "U",
u"ç": "C",
u"Ç": "C",
}


class CaseLettre(QLineEdit):
    def __init__(self, parent):
        self.parent = parent
        QLineEdit.__init__(self, parent)
        self.setAlignment(Qt.AlignCenter)

    def keyPressEvent(self, evt):
        self.parent.message(u'')
        n = evt.key()
        if 65 <= n <= 90 or 97 <= n <= 122:
            c = chr(n).upper()
            for case in self.parent.cases.values():
                if case.text() == c:
                    self.parent.message(u'La lettre %s est déjà utilisée !' %c)
                    return
            self.setText(c)
        elif n in (Qt.Key_Backspace, Qt.Key_Delete):
            self.clear()
            ##QLineEdit.keyPressEvent(self, evt)


class CryptographieMenuBar(MenuBar):
    def __init__(self, panel):
        MenuBar.__init__(self, panel)
        self.ajouter(u"Fichier", ["quitter"])
        self.ajouter(u"Affichage", ["onglet"])
        self.ajouter(u"Outils",
                        [u"Coder un message", u"Code le message par substitution mono-alphabétique.",
                                "Ctrl+K", panel.coder],
                        [u"Coder avec espaces", u"Code le message en conservant les espaces (substitution mono-alphabétique).",
                                "Ctrl+Shift+K", partial(panel.coder, espaces=True)],
                        [u"Générer une nouvelle clé", u"Générer une nouvelle permutation de l'alphabet.", None, panel.generer_cle],
                        [u"Modifier la clé", u"Générer une nouvelle permutation de l'alphabet.", None, panel.DlgModifierCle],
                        None,
                        [u"options"])
        self.ajouter(u"avance2")
        self.ajouter("?")




class Cryptographie(Panel_simple):
    titre = u"Cryptographie" # Donner un titre à chaque module

    def __init__(self, *args, **kw):
        Panel_simple.__init__(self, *args, **kw)

        self._freeze = False
        self.widget_modifie = None

        # La clé est la permutation de l'alphabet actuellement utilisée
        self.generer_cle()

        # Signe indiquant un caractère non déchiffré
        self.symbole = '-' # '.'

        self.sizer = QVBoxLayout()

        self.textes = QGridLayout()
        self.textes.setSpacing(5)
        size = (400, 300)

        txt_clair = QLabel(u"<b>Texte en clair</b>")
        self.clair = QTextEdit()
        self.clair.setMinimumSize(*size)
        formater_clair = partial(self.formater, widget=self.clair)
        self.clair.textChanged.connect(formater_clair)
        self.clair.cursorPositionChanged.connect(formater_clair)
        self.copier_clair = QPushButton(u'Copier le texte en clair')
        self.copier_clair.clicked.connect(partial(self.copier, widget=self.clair))

        txt_code = QLabel(u"<b>Texte codé</b>")
        self.code = QTextEdit()
        self.code.setMinimumSize(*size)
        self.code.textChanged.connect(self.code_modifie)
        self.code.cursorPositionChanged.connect(partial(self.formater, widget=self.code))
        self.copier_code = QPushButton(u'Copier le texte codé')
        self.copier_code.clicked.connect(partial(self.copier, widget=self.code))

        self.textes.addWidget(txt_clair, 0, 0)
        self.textes.addItem(QSpacerItem(50, 1), 0, 1)
        self.textes.addWidget(txt_code, 0, 2)
        self.textes.addWidget(self.clair, 1, 0)
        self.textes.addWidget(self.code, 1, 2)
        self.textes.addWidget(self.copier_code, 2, 2)
        self.textes.addWidget(self.copier_clair, 2, 0)

        self.table = QGridLayout()
        self.table.setSpacing(3)
        self.cases = {}
        self.table.addWidget(QLabel(u"Codé : ", self), 0, 0)
        self.table.addWidget(QLabel(u"Clair : ", self), 1, 0)
        ##self.table.setColumnStretch(0, 100)
        for i, l in enumerate(majuscules):
            lettre = QLineEdit(l, self)
            lettre.setAlignment(Qt.AlignCenter)
            lettre.setReadOnly(True)
            lettre.setEnabled(False)
            self.table.addWidget(lettre, 0, i + 1)
            ##self.table.setColumnStretch(i + 1, 1)
        for i, l in enumerate(majuscules):
            c = self.cases[l] = CaseLettre(self)
            c.setMaxLength(1)
            self.table.addWidget(c, 1, i + 1)
            c.textChanged.connect(self.decoder)
        self.sizer.addLayout(self.textes)
        self.sizer.addLayout(self.table)
        self.setLayout(self.sizer)
        ##self.adjustSize()

        self.couleur1 = "5A28BE" # sky blue
        self.couleur2 = "C86400" # Lime Green
        self.couleur_position = "FFCDB3"
        self.reg = re.compile("([-A-Za-z]|<##>|</##>)+")
        ##couleur_position = wx.Color(255, 205, 179) # FFCDB3
        ##couleur1 = wx.Color(90, 40, 190) # 5A28BE
        ##couleur2 = wx.Color(200, 100, 0) # C86400
        ##black = wx.Color(0, 0, 0) # 000000
        ##white = wx.Color(255, 255, 255) # FFFFFF
        ##self.special = wx.TextAttr(wx.NullColour, couleur_position)
        ##self.fond = wx.TextAttr(couleur1, wx.NullColour) #"sky blue"
        ##self.fond2 = wx.TextAttr(couleur2, wx.NullColour) # "Lime Green"
        ##self.defaut = wx.TextAttr(black, white)
##
        ##self.Bind(wx.EVT_IDLE, self.OnIdle)
        timer = QTimer(self)
        timer.timeout.connect(self.OnIdle)
        timer.start(100)


        # DEBUG:
        ##self.code.setPlainText('WR IRAMXPZRHRDZ IK HRYYOVR AL IRYYBKY RYZ NOALWLZR POM WR NOLZ FKR W BD O VOMIR WRY YLVDRY IR PBDAZKOZLBD RZ WRY RYPOARY RDZMR WRY HBZY OWBMY FKR I QOELZKIR BD VMBKPR WRY WRZZMRY ALDF POM ALDF')

    def copier(self, evt=None, widget=None):
        self.vers_presse_papier(widget.toPlainText())


    def DlgModifierCle(self, evt=None):
        while True:
            text, ok = QInputDialog.getText(self, u"Modifier la clé",
                    u"La clé doit être une permutation de l'alphabet,\n"
                    u"ou un chiffre qui indique de combien l'alphabet est décalé.",
                    text=str(self.cle))
            if ok:
                try:
                    self.modifier_cle(text)
                except:
                    print_error()
                    continue
            break


    def generer_cle(self):
        l = list(majuscules)
        shuffle(l)
        self.cle = ''.join(l)


    def modifier_cle(self, cle):
        cle = cle.strip().upper()
        if cle.isdigit():
            n = int(cle)
            cle = majuscules[n:] + majuscules[:n]
        # On teste qu'il s'agit bien d'une permutation de l'alphabet:
        assert ''.join(sorted(cle)) == majuscules
        self.cle = cle


    def coder(self, evt=None, cle=None, espaces=False):
        cle = (self.cle if cle is None else cle)
        clair = self.clair.toPlainText().upper()
        for key, val in dict_accents.items():
            clair = clair.replace(key, val)
        d = dict(zip(majuscules, cle))
        code = ''.join(d.get(s, ' ') for s in clair)
        code = re.sub(' +', ' ', code)
        if not espaces:
            code = code.replace(' ', '')
        self.code.setPlainText(code)


    @staticmethod
    def _vigenere(l1, l2):
        return chr((ord(l1) + ord(l2) - 130)%26 + 65)

    def coder_vigenere(self, evt=None, msg=None, cle=None):
        if msg is None:
            msg = self.clair.GetValue()
        if cle is None:
            pass
        return ''.join(self._vigenere(l1, l2) for l1, l2 in izip(cycle(cle), msg))


    def decoder(self, txt=None):
        code = self.code.toPlainText().upper()
        def f(s):
            if s in majuscules:
                return self.cases[s].text() or self.symbole
            return s

        clair = ''.join(f(s) for s in code)
        self.clair.setPlainText(clair)


    def code_modifie(self, txt=None):
        self.decoder(txt)
        self.formater(txt, widget=self.code)

    def formater(self, evt=None, widget=None):
        ##evt.Skip()
        if self._freeze:
            return
        self.widget_modifie = widget



    def _formater(self, widget_modifie):
        # Impossible de formater les 2 textes de la même manière s'ils
        # ne sont pas de la même longueur.
        # Cela ne devrait se produire que temporairement (par ex.,
        # l'utilisateur copie un nouveau texte)
        if len(self.code.toPlainText()) != len(self.clair.toPlainText()):
            if self.code.toPlainText() and self.clair.toPlainText():
                print(u'Warning: le message codé et le message en clair ne sont '
                      u'pas de même longueur.')
            return

        def colorier(m, col1=[self.couleur1], col2=[self.couleur2]):
            s = m.group(0)
            s = "<font color='#%s'>%s</font>" % (col1[0], s)
            col1[0], col2[0] = col2[0], col1[0]
            return s
        self._freeze = True
        pos = widget_modifie.textCursor().position()
        for w in (self.code, self.clair):
            txt = w.toPlainText()
            if pos != len(txt):
                txt = txt[:pos] + '<##>' + txt[pos] + '</##>' + txt[pos + 1:]
            new_txt = re.sub(self.reg, colorier, txt)
            new_txt = new_txt.replace("<##>",
                        "<font style='background-color: #%s;'>" % self.couleur_position)
            new_txt = new_txt.replace("</##>", "</font>")
            w.setHtml(new_txt)
        cursor = widget_modifie.textCursor()
        cursor.setPosition(pos)
        widget_modifie.setTextCursor(cursor)
        self._freeze = False
        self.widget_modifie = None


    def OnIdle(self, evt=None):
        if self.widget_modifie is not None and not self.parent.parent.closing:
            self._formater(self.widget_modifie)
