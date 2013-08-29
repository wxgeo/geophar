# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

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
#
######################################

from functools import partial

from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import (QDialog, QTabWidget, QWidget, QVBoxLayout, QGroupBox,
                         QHBoxLayout, QPushButton, QLabel, QCheckBox, QSpinBox,
                         QComboBox, QFileDialog, QLineEdit)

from ..param.options import Section, Parametre
##from .app import white_palette
##OptionsModifiedEvent, EVT_OPTIONS_MODIFIED = wx.lib.newevent.NewEvent()

class FenetreOptions(QDialog):
    options_modified = pyqtSignal(set)

    def __init__(self, parent, options):
        QDialog.__init__(self, parent)
        ##self.setPalette(white_palette)
        self.setWindowTitle(options.titre)
        self.parent = parent
        self.onglets = QTabWidget(self)
        main_sizer = QVBoxLayout()
        main_sizer.addWidget(self.onglets)
        self.setLayout(main_sizer)
        ##dimensions_onglets = []
        self.widgets = {}
        for theme in options:
            panel = QWidget(self.onglets)
            sizer = QVBoxLayout()
            self.onglets.addTab(panel, theme.titre)
            for elt in theme:
                if isinstance(elt, Section):
                    box = QGroupBox(elt.titre, panel)
                    bsizer = QVBoxLayout()
                    box.setLayout(bsizer)
                    bsizer.addSpacing(3)
                    for parametre in elt:
                        if isinstance(parametre, Parametre):
                            psizer = self.ajouter_parametre(parametre, panel, sizer)
                            bsizer.addLayout(psizer)
                        elif isinstance(parametre, basestring):
                            bsizer.addWidget(QLabel(parametre))
                        else:
                            raise NotImplementedError, repr(type(elt))
                    bsizer.addSpacing(3)
                    sizer.addWidget(box)
                elif isinstance(elt, Parametre):
                    psizer = self.ajouter_parametre(elt, panel, sizer)
                    sizer.addLayout(psizer)
                elif isinstance(elt, basestring):
                    sizer.addWidget(QLabel(elt))
                else:
                    raise NotImplementedError, repr(type(elt))

            boutons = QHBoxLayout()
            ok = QPushButton(u'OK', clicked=self.ok)
            boutons.addWidget(ok)

            defaut = QPushButton(u"Défaut", clicked=self.defaut)
            boutons.addWidget(defaut)

            annuler = QPushButton(u"Annuler", clicked=self.close)
            boutons.addWidget(annuler)
            sizer.addStretch()
            sizer.addLayout(boutons)
            panel.setLayout(sizer)
            ##dimensions_onglets.append(sizer.CalcMin().Get())

        ##w, h = (max(dimensions) for dimensions in zip(*dimensions_onglets))
        ##self.SetSize(wx.Size(w + 10, h + 50))
        ##self.CenterOnParent()



    def ajouter_parametre(self, parametre, panel, sizer):
        type_ = parametre.type
        psizer = QHBoxLayout()
        if type_ is not bool:
            psizer.addWidget(QLabel(parametre.texte + ' :'))

        if type_ is bool:
            widget = QCheckBox(parametre.texte, panel)
        elif type_ in (file, str):
            widget = QLineEdit(panel)
            widget.setMinimumWidth(200)
        elif isinstance(type_, tuple):
            widget = QSpinBox(panel)
            widget.setRange(*type_)
        elif isinstance(type_, list):
            widget = QComboBox(panel)
            widget.addItems(type_)
        else:
            print type_
            raise NotImplementedError
        self.widgets[parametre.nom] = widget
        widget.parametre = parametre
        self.set_value(widget, parametre.valeur)
        psizer.addWidget(widget)
        if type_ is file:
            parcourir = QPushButton(u'Parcourir', clicked=partial(self.parcourir, widget))
            psizer.addWidget(parcourir)
        return psizer

    def set_value(self, widget, valeur):
        type_ = widget.parametre.type
        if type_ is bool:
            widget.setChecked(valeur)
        elif type_ in (file, str):
            widget.setText(valeur)
        elif isinstance(type_, tuple):
            widget.setValue(valeur)
        elif isinstance(type_, list):
            widget.setCurrentIndex(widget.findText(valeur))
        else:
            print type_
            raise NotImplementedError

    def get_value(self, widget):
        type_ = widget.parametre.type
        if type_ is bool:
            return widget.isChecked()
        elif type_ in (file, str):
            return widget.text()
        elif isinstance(type_, tuple):
            return widget.value()
        elif isinstance(type_, list):
            return widget.currentText()
        else:
            print type_
            raise NotImplementedError

    def defaut(self):
        for widget in self.widgets.itervalues():
            self.set_value(widget, widget.parametre.defaut)

    def ok(self):
        modifs = set()
        for widget in self.widgets.itervalues():
            new_val = self.get_value(widget)
            if new_val != widget.parametre.valeur:
                widget.parametre.valeur = new_val
                modifs.add(widget.parametre.prefixe)
        self.options_modified.emit(modifs)
        self.close()

    def parcourir(self, widget):
        widget.setText(QFileDialog.getExistingDirectory(self, u"Choisissez un répertoire :",
                                                 widget.text(),
                                                 QFileDialog.ShowDirsOnly))