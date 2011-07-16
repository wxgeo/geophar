# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                 Fenetres                              #
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

from .pythonSTC import PythonSTC
from wxlib import MyMiniFrame
import wx

####################################################################################################

# Code de la feuille actuelle


class FenCode(MyMiniFrame):
    def __init__(self, parent, titre, contenu, fonction_modif):
        MyMiniFrame.__init__(self, parent, titre)
        self.parent = parent
        self.fonction_modif = fonction_modif
##        self.texte = wx.TextCtrl(self, -1, contenu, size=(300, 10), style=wx.TE_MULTILINE)
        self.texte = PythonSTC(self, -1, size=(300, 10))
        self.texte.AddText(contenu)
        self.texte.Bind(wx.EVT_CHAR, self.EvtChar)
##        self.texte.SetInsertionPointEnd()
        self.texte.SetFocus()


        tb = self.CreateToolBar( wx.TB_HORIZONTAL
                                 | wx.NO_BORDER
                                 | wx.TB_FLAT
                                 | wx.TB_TEXT )
        self.a = wx.Button(tb, -1, u"Modifier - F5")
        tb.AddControl(self.a)
        tb.AddSeparator()
        tb.AddSeparator()
        self.b = wx.Button(tb, -1, u"Annuler - ESC")
        tb.AddControl(self.b)
        tb.Realize()

        self.Bind(wx.EVT_BUTTON, self.executer, self.a)
        self.Bind(wx.EVT_BUTTON, self.fermer, self.b)
        self.SetSize((400, 500))
        self.CenterOnParent(wx.BOTH)


    def EvtChar(self, event):
        key = event.GetKeyCode()
        if key == wx.WXK_ESCAPE: self.fermer()
        elif key == wx.WXK_F5: self.executer()
        else : event.Skip()

    def fermer(self, event = None):
        self.Close(True)

    def executer(self, event = None):
        # On exécute le code (de la feuille par ex.) éventuellement modifié
##        self.fonction_modif(self.texte.GetValue())
        self.fonction_modif(self.texte.GetText())
        self.fermer()
