# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------##
#               Widget LigneCommande              #
##--------------------------------------##
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

from PyQt4.QtGui import QWidget


class LigneCommande(QWidget):
    u"Un TextCtrl muni d'un historique et associé à un bouton pour valider."
    def __init__(self, parent, longueur = 500, texte = None,
                action = (lambda *args, **kw: True), afficher_bouton = True,
                legende = None):
        self.parent = parent
        self.action = action
        QWidget.__init__(self, parent)
#        self.SetBackgroundColour(self.parent.GetBackgroundColour())

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.texte = QLineEdit(self)
        #TODO: implement longueur
        self.texte.returnPressed.connect(self.EvtButton)
        self.texte.Bind(wx.EVT_KEY_UP, self.EvtChar)
        if texte is None:
            self.bouton = wx.Button(self, wx.ID_OK)
        else:
            self.bouton = wx.Button(self, label = texte)
        self.bouton.Bind(wx.EVT_BUTTON, self.EvtButton)
        self.bouton.setVisible(afficher_bouton)

        if legende is not None:
            sizer.Add(wx.StaticText(self, -1, legende), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.texte, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)
        sizer.Add(self.bouton, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        self.SetSizer(sizer)
        self.adjustSize()

        self.initialiser()


    def initialiser(self):
        self.historique = []
        self.position = None
        self.setFocus()
        self.clear()

    def GetValue(self):
        return self.texte.GetValue()

    def SetValue(self, value):
        self.texte.SetValue(value)

    def SetFocus(self):
        self.texte.setFocus()

    def clear(self):
        self.texte.clear()

    def GetSelection(self):
        return self.texte.GetSelection()

    def GetInsertionPoint(self):
        return self.texte.GetInsertionPoint()

    def SetInsertionPoint(self, num):
        return self.texte.SetInsertionPoint(num)

    def setText(self, texte):
        self.texte.setText(texte)

    def SetSelection(self, deb, fin):
        self.texte.SetSelection(deb, fin)

    def setToolTip(self, tip):
        self.texte.setToolTip(tip)

    def EvtButton(self, event):
        commande = self.GetValue()
        self.position = None
        if commande:
            self.historique.append(commande)
        elif self.historique:
            # Appuyer une deuxième fois sur [Entrée] permet de répéter l'action précédente.
            commande = self.historique[-1]
        kw = {}
        for modifier in ('shift', 'alt', 'meta', 'control'):
            kw[modifier] = getattr(event, modifier.capitalize() + 'Down', lambda: None)()
        self.action(commande, **kw)


    def keyPressEvent(self, event):
        key = event.key()
        commande = self.text()

#        if code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
#            self.EvtButton(event)

        if key == Qt.Key_Up:
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

        elif key == Qt.Key_Down:
            # On redescend dans l'historique (-> entrées plus récentes)
            if self.position is None or self.position == len(self.historique) - 1:
                if commande and commande != self.historique[-1]:
                    self.historique.append(commande)
                self.texte.clear()
                self.position = len(self.historique)
            elif self.position < len(self.historique) - 1:
                self.position += 1
                self.texte.SetValue(self.historique[self.position])
        else:
            self.position = None
#            event.Skip()

    def Command(*args, **kwargs):
        pass
    def Create(*args, **kwargs):
        pass
    def GetAlignment(*args, **kwargs):
        pass
    def GetLabelText(*args, **kwargs):
        pass
