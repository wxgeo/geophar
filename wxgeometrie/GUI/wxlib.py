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


import os

from PyQt4.QtCore import Qt, QThread, QEvent, pyqtSignal
from PyQt4.QtGui import (QCursor, QDialog, QPixmap, QPushButton, QColorDialog,
                         QMenu, QFont, QIcon)

import param
from ..pylib import uu
from .app import app

#class PseudoEvent(object):
#    u"Cette classe est destinée à maintenir en vie un évènement périmé."

#    _methodes = ("AltDown", "ControlDown", "ShiftDown", "GetPositionTuple",
#                "RightIsDown", "RightIsUp", "LeftIsDown", "LeftIsUp", "GetWheelRotation")

#    def __init__(self, event):
#        self._dict = {}
#        for methode in self._methodes:
#            if hasattr(event, methode):
#                self._dict[methode] = getattr(event, methode)()

#    def __getattr__(self, name):
#        try:
#            return lambda:self._dict[name]
#        except KeyError:
#            print(u"La méthode " + name + " n'est actuellement pas définie pour les pseudo-évènements.")
#            raise

#    def Skip(self):
#        pass


#TransmitEvent, EVT_TRANSMIT = wx.lib.newevent.NewEvent()


class BusyCursor(object):
    def __enter__(self):
        app.setOverrideCursor(QCursor(Qt.WaitCursor))

    def __exit__(self, type, value, traceback):
        app.restoreOverrideCursor()


class MyMiniFrame(QDialog):
    def __init__(self, parent, titre=''):
        QDialog.__init__(self, parent)
        self.setModal(False)
        self.setWindowTitle(titre)

def png_pth(nom):
    u"""Adresse complète de l'image `nom`.png du repertoire 'images/'.

    Le nom doit être indiqué sans l'extension '.png'."""
    return os.path.normpath(os.path.join(uu(param.EMPLACEMENT), 'images', nom + ".png"))


def png(nom):
    u"""Charge l'image <nom>.png depuis le repertoire 'images/'.

    L'image doit être au format png, et son nom doit indiqué sans l'extension '.png'."""
    pixmap = QPixmap()
    pixmap.load(png_pth(nom), 'PNG')
    return pixmap


class GenericThread(QThread):
    def __init__(self, function, *args, **kwargs):
        QThread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __del__(self):
        self.wait()

    def run(self):
        self.function(*self.args,**self.kwargs)


#class MyFont(wx.Font):
#    u"""Créé une nouvelle police, héritant par défaut ses attributs de 'widget'."""
#    def __init__(self, widget, size=None, family=None, style=None, weight=None, underline=None):
#        font = widget.GetFont()
#        if size is None:
#            size = font.GetPointSize()
#        if family is None:
#            family = font.GetFamily()
#        if style is None:
#            style = font.GetStyle()
#        if weight is None:
#            weight = font.GetWeight()
#        if underline is None:
#            underline = font.GetUnderlined()
#        wx.Font.__init__(self, size, family, style, weight, underline)

def shift_down(event):
    return event.modifiers() & Qt.ShiftModifier

def alt_down(event):
    return event.modifiers() & Qt.AltModifier

def ctrl_down(event):
    return event.modifiers() & Qt.ControlModifier

def meta_down(event):
    return event.modifiers() & Qt.MetaModifier

def left_down(event):
    return event.buttons() & Qt.LeftButton

def right_down(event):
    return event.buttons() & Qt.RightButton

def lieu(event_or_widget):
    if isinstance(event_or_widget, QEvent):
        p = event_or_widget.pos()
    else:
        p = event_or_widget.mapFromGlobal(QCursor.pos())
    return p.x(), p.y()


class ColorSelecter(QPushButton):
    u"A bouton used to select a color."

    colorSelected = pyqtSignal('QColor')

    def __init__(self, parent, color=None):
        QPushButton.__init__(self, parent)
        self.setColor(color)
        self.clicked.connect(self.onClick)

    def onClick(self):
        self.setColor(QColorDialog.getColor(self.color, self, u"Choisissez une couleur"))

    def setColor(self, color):
        self.color = color
        if color is not None:
            self.setStyleSheet("ColorSelecter { background-color: %s }"
                           "ColorSelecter:pressed { background-color: %s }" % (
                           color.name(), color.light(125).name()))
        self.colorSelected.emit(color)


class PopUpMenu(QMenu):
    u"""Un menu avec un titre visible."""

    def __init__(self, title, parent, icon=None):
        QMenu.__init__(self, title, parent)
        if icon is None:
            title = u'\u2022 ' + title
            self._title = self.addAction(title)
        else:
            if isinstance(icon, basestring):
                ##icon = QIcon(png(icon))
                icon = QIcon(png_pth(icon))
            self._title = self.addAction(icon, title)
        self._title.setEnabled(False)
        self._title.setIconVisibleInMenu(True)
        font = QFont()
        font.setBold(True)
        font.setStyle(QFont.StyleItalic)
        self._title.setFont(font)
        self.addSeparator()

    def setTitle(self, title):
        self._title.setText(title)
        QMenu.setTitle(title)