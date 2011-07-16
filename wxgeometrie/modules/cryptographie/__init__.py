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

import wx

#from ...GUI.wxlib import MyFont
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
    __titre__ = u"Cryptographie" # Donner un titre à chaque module

    def __init__(self, *args, **kw):
        Panel_simple.__init__(self, *args, **kw)

        self._freeze = False
        self._actualiser = None

        # La clé est la permutation de l'alphabet actuellement utilisée
        self.cle = self.generer_cle()

        # Signe indiquant un caractère non déchiffré
        self.symbole = '-' # '.'

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        font = self.GetFont()
#        italic = wx.Font(font.GetPointSize(), font.GetFamily(), wx.ITALIC, wx.NORMAL)
        bold = wx.Font(font.GetPointSize(), font.GetFamily(), wx.NORMAL, wx.BOLD)

        self.textes = wx.GridBagSizer(5, 5)
        size = (400, 300)

        TE_STYLE = wx.TE_MULTILINE|wx.TE_RICH2#|wx.TE_CHARWRAP

        txt_clair = wx.StaticText(self, -1, u"Texte en clair")
        txt_clair.SetFont(bold)
        self.clair = wx.TextCtrl(self, style=TE_STYLE, size=size)
        # self.clair.Bind(wx.EVT_LEFT_UP, self.clairLeft)
        self.clair.Bind(wx.EVT_TEXT, partial(self.formater, widget=self.clair))
        self.clair.Bind(wx.EVT_LEFT_UP, partial(self.formater, widget=self.clair))
        self.clair.Bind(wx.EVT_KEY_DOWN, partial(self.formater, widget=self.clair))
        self.copier_clair = wx.Button(self, label=u'Copier le texte en clair')
        self.copier_clair.Bind(wx.EVT_BUTTON, partial(self.copier, widget=self.clair))

        txt_code = wx.StaticText(self, -1, u"Texte codé")
        txt_code.SetFont(bold)
        self.code = wx.TextCtrl(self, style=TE_STYLE, size=size)
        # self.code.Bind(wx.EVT_LEFT_UP, self.codeLeft)
        self.code.Bind(wx.EVT_LEFT_UP, partial(self.formater, widget=self.code))
        self.code.Bind(wx.EVT_TEXT, self.code_modifie)
        self.code.Bind(wx.EVT_KEY_DOWN, partial(self.formater, widget=self.code))
        self.copier_code = wx.Button(self, label=u'Copier le texte codé')
        self.copier_code.Bind(wx.EVT_BUTTON, partial(self.copier, widget=self.code))

        self.textes.Add(txt_clair, (0, 0), flag=wx.ALIGN_CENTER)
        self.textes.AddSpacer((50, 1), (0, 1))
        self.textes.Add(txt_code, (0, 2), flag=wx.ALIGN_CENTER)
        self.textes.Add(self.clair, (1, 0), flag=wx.ALIGN_CENTER)
        self.textes.Add(self.code, (1, 2), flag=wx.ALIGN_CENTER)
        self.textes.Add(self.copier_code, (2, 2), flag=wx.ALIGN_CENTER)
        self.textes.Add(self.copier_clair, (2, 0), flag=wx.ALIGN_CENTER)

        self.table = wx.GridBagSizer(5, 5)
        self.cases = {}
        size = (30, -1)
        self.table.Add(wx.StaticText(self, -1, u"Codé:"), (0, 0), flag=wx.ALIGN_CENTER)
        self.table.Add(wx.StaticText(self, -1, u"Clair:"), (1, 0), flag=wx.ALIGN_CENTER)
        for i, l in enumerate(majuscules):
            txtctrl = wx.TextCtrl(self, value=l, size=size, style=wx.TE_READONLY|wx.TE_CENTRE)
            txtctrl.Disable()
            self.table.Add(txtctrl, (0, i + 1))
        for i, l in enumerate(majuscules):
            self.cases[l] = wx.TextCtrl(self, size=size, style=wx.TE_CENTRE)
            self.cases[l].SetMaxLength(1)
            self.table.Add(self.cases[l], (1, i + 1))
            self.cases[l].Bind(wx.EVT_LEFT_DOWN, partial(self.EvtLeftDown, l=l))
            self.cases[l].Bind(wx.EVT_KEY_DOWN,  partial(self.EvtKey, l=l))
            self.cases[l].Bind(wx.EVT_TEXT, self.decoder)

        self.sizer.Add(self.textes, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        self.sizer.Add(self.table, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        self.SetSizer(self.sizer)
        self.Fit()

        couleur_position = wx.Color(255, 205, 179)
        couleur1 = wx.Color(90, 40, 190)
        couleur2 = wx.Color(200, 100, 0)
        black = wx.Color(0, 0, 0)
        white = wx.Color(255, 255, 255)
        self.special = wx.TextAttr(wx.NullColour, couleur_position)
        self.fond = wx.TextAttr(couleur1, wx.NullColour) #"sky blue"
        self.fond2 = wx.TextAttr(couleur2, wx.NullColour) # "Lime Green"
        self.defaut = wx.TextAttr(black, white)

        self.Bind(wx.EVT_IDLE, self.OnIdle)

        # DEBUG:
        # self.code.SetValue('WR IRAMXPZRHRDZ IK HRYYOVR AL IRYYBKY RYZ NOALWLZR POM WR NOLZ FKR W BD O VOMIR WRY YLVDRY IR PBDAZKOZLBD RZ WRY RYPOARY RDZMR WRY HBZY OWBMY FKR I QOELZKIR BD VMBKPR WRY WRZZMRY ALDF POM ALDF')

    def copier(self, evt=None, widget=None):
        self.vers_presse_papier(widget.GetValue())


    def DlgModifierCle(self, evt=None):
        dlg = wx.TextEntryDialog(self, u"La clé doit être une permutation de l'alphabet,\nou un chiffre qui indique de combien l'alphabet est décalé.", u"Modifier la clé", str(self.cle))
        test = True
        while test:
            test = dlg.ShowModal()
            if test == wx.ID_OK:
                try:
                    self.modifier_cle(dlg.GetValue())
                    break
                except:
                    print_error()

            if test == wx.ID_CANCEL:
                break
        dlg.Destroy()


    @staticmethod
    def generer_cle(evt=None):
        l = list(majuscules)
        shuffle(l)
        return ''.join(l)


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
        clair = self.clair.GetValue().upper()
        for key, val in dict_accents.items():
            clair = clair.replace(key, val)
        d = dict(zip(majuscules, cle))
        code = ''.join(d.get(s, ' ') for s in clair)
        code = re.sub(' +', ' ', code)
        if not espaces:
            code = code.replace(' ', '')
        self.code.SetValue(code)


    @staticmethod
    def _vigenere(l1, l2):
        return chr((ord(l1) + ord(l2) - 130)%26 + 65)

    def coder_vigenere(self, evt=None, msg=None, cle=None):
        if msg is None:
            msg = self.clair.GetValue()
        if cle is None:
            pass
        return ''.join(self._vigenere(l1, l2) for l1, l2 in izip(cycle(cle), msg))


    def decoder(self, evt=None):
        code = self.code.GetValue().upper()
        def f(s):
            if s in majuscules:
                return self.cases[s].GetValue() or self.symbole
            return s

        clair = ''.join(f(s) for s in code)
        self.clair.SetValue(clair)
        if evt is not None:
            evt.Skip()

    def EvtLeftDown(self, evt=None, l=None):
        self.cases[l].SetFocusFromKbd()
        self.cases[l].SelectAll()

    def EvtKey(self, evt, l):
        self.message(u'')
        n = evt.GetKeyCode()
        if 65 <= n <= 90 or 97 <= n <= 122:
            c = chr(n).upper()
            for case in self.cases.values():
                if case.GetValue() == c:
                    self.message(u'La lettre %s est déjà utilisée !' %c)
                    return
            self.cases[l].SetValue(c)
        else:
            evt.Skip()

    def code_modifie(self, evt):
        self.decoder(evt)
        self.formater(evt, widget=self.code)

    def formater(self, evt, widget=None):
        evt.Skip()
        if self._freeze:
            return
        self._actualiser = widget


    def _formater(self, widget):
        self._freeze = True
        txt = widget.GetValue()
        pos = widget.GetInsertionPoint()
        if param.plateforme == "Windows":
            self.copier_clair.SetFocusFromKbd()
        for w in (self.code, self.clair):
            w.Freeze()
            last = w.GetLastPosition()
            w.SetStyle(0, last, self.defaut)
            if ' ' in txt:
                i = 0
                fond = self.fond
                fond2 = self.fond2
                while i < last:
                    j = txt.find(' ', i)
                    if j == -1:
                        j = last
                    w.SetStyle(i, j, fond)
                    fond, fond2 = fond2, fond
                    i = j + 1
            w.SetStyle(pos, pos + 1, self.special)
            if param.plateforme == "Windows":
                wx.CallAfter(w.SetSelection, pos, pos)
                wx.CallAfter(w.Thaw)
            else:
                w.Thaw()
        widget.SetFocusFromKbd()
        self._freeze = False
        self._actualiser = None

    def OnIdle(self, evt):
        if self._actualiser is not None and not self.parent.parent.closing:
            self._formater(self._actualiser)
