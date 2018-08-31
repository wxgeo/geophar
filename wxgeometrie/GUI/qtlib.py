# -*- coding: utf-8 -*-

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


import os
from PyQt5.QtCore import Qt, QThread, QEvent, pyqtSignal, QSize
from PyQt5.QtGui import QCursor, QPixmap, QFont, QIcon, QPalette
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QPushButton, QColorDialog,\
    QMenu, QLabel, QListWidget, QDialogButtonBox, QAbstractItemView

from .. import param
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
    """Adresse complète de l'image `nom`.png du repertoire 'images/'.

    Le nom doit être indiqué sans l'extension '.png'."""
    return os.path.normpath(os.path.join(param.EMPLACEMENT, 'wxgeometrie/images', nom + ".png"))


def png(nom):
    """Charge l'image <nom>.png depuis le repertoire 'images/'.

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
    "A bouton used to select a color."

    colorSelected = pyqtSignal('QColor')

    def __init__(self, parent, color=None):
        QPushButton.__init__(self, parent)
        self.parent = parent
        self.setColor(color)
        self.clicked.connect(self.onClick)
        self.setMinimumSize(QSize(25, 25))
        self.setMaximumSize(QSize(25, 25))

    def onClick(self):
        self.setColor(QColorDialog.getColor(self.color, self, "Choisissez une couleur"))

    def setColor(self, color):
        if color is None:
            color = self.parent.palette().color(QPalette.Active, QPalette.Window)
        if color.isValid():
            # Couleur invalide -> l'utilisateur a cliqué sur "Annuler"
            self.color = color
            if color is not None:
                self.setStyleSheet("ColorSelecter { border-radius: 4px; \
                    background-color: %s ; border-color:#AAAAAA #AAAAAA #444444 #444444; \
                    border-style:solid; border-width:1px;} \
                    ColorSelecter:disabled {border-color:#AAAAAA #AAAAAA #444444 #444444;} \
                    ColorSelecter:hover { background-color: %s }"
                    % (color.name(), color.lighter(125).name()))
            self.colorSelected.emit(color)


class PopUpMenu(QMenu):
    """Un menu avec un titre visible."""

    def __init__(self, title, parent, icon=None):
        QMenu.__init__(self, title, parent)
        if icon is None:
            title = '\u2022 ' + title
            self._title = self.addAction(title)
        else:
            if isinstance(icon, str):
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


class MultipleChoiceDialog(QDialog):
    def __init__(self, parent, title, text, items):
        QDialog.__init__(self, parent)
        self.setWindowTitle(title)
        self.layout = QVBoxLayout()
        label = QLabel(text)
        self.layout.addWidget(label)
        self.listwidget = QListWidget(self)
        self.listwidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        for item in items:
            self.listwidget.addItem(item)
        self.layout.addWidget(self.listwidget)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(buttonBox)
        self.setLayout(self.layout)

    def selectedItems(self):
        return self.listwidget.selectedItems()
