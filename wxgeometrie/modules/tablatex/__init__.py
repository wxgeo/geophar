#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

##--------------------------------------#######
#                Calculatrice                 #
##--------------------------------------#######
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


from PyQt4.QtGui import (QHBoxLayout, QVBoxLayout, QCheckBox, QPushButton,
                         QTextEdit, QLineEdit, QLabel, QComboBox, QGroupBox,
                         QSpinBox)

from ...GUI.app import app
from ...GUI.ligne_commande import LigneCommande
from ...GUI.menu import MenuBar
from ...GUI.panel import Panel_simple
from ... import param
from ...pylib import warning, print_error
from ...pylib.erreurs import message
from .tabsign import tabsign
from .tabval import tabval
from .tabvar import tabvar






class TabLaTeXMenuBar(MenuBar):
    def __init__(self, panel):
        MenuBar.__init__(self, panel)
        self.ajouter(u"Fichier", ['session'], ["quitter"])
        self.ajouter(u"Affichage", [u"onglet"], ["plein_ecran"])
        self.ajouter(u"Outils",
                        [u"Mémoriser le résultat", u"Copie le code LaTeX généré "
                        "dans le presse-papier, afin de pouvoir l'utiliser ailleurs.",
                        "Ctrl+M", self.panel.vers_presse_papier],
                        None,
                        [u"options"])
        self.ajouter(u"avance2")
        self.ajouter("?")




class TabLaTeX(Panel_simple):
    titre = u"Tableaux LaTeX" # Donner un titre a chaque module

    def __init__(self, *args, **kw):
        Panel_simple.__init__(self, *args, **kw)

        self.sizer = QVBoxLayout()

        self.entree = LigneCommande(self, longueur = 500, action = self.generer_code)
        self.sizer.addWidget(self.entree)

        self.sizer_type = QHBoxLayout()
        self.type_tableau = QComboBox(self)
        self.type_tableau.addItems([u"Tableau de variations", u"Tableau de signes",
                                    u"Tableau de valeurs"])
        self.type_tableau.setCurrentIndex(self._param_.mode)
        self.sizer_type.addWidget(QLabel(u"Type de tableau :", self))
        self.sizer_type.addWidget(self.type_tableau)
        self.sizer_type.addSpacing(15)

        self.utiliser_cellspace = QCheckBox(u"Utiliser le paquetage cellspace.", self)
        self.utiliser_cellspace.setChecked(self._param_.utiliser_cellspace)
        self.utiliser_cellspace.setToolTip(u"Le paquetage cellspace évite que "
                "certains objets (comme les fractions) touchent les bordures du tableaux.")
        self.sizer_type.addSpacing(10)
        self.sizer_type.addWidget(self.utiliser_cellspace)

        self.derivee = QCheckBox(u"Dérivée.", self)
        self.derivee.setChecked(self._param_.derivee)
        self.derivee.setToolTip(u"Afficher une ligne indiquant le signe de la dérivée.")
        self.sizer_type.addSpacing(10)
        self.sizer_type.addWidget(self.derivee)

        self.limites = QCheckBox(u"Limites.", self)
        self.limites.setChecked(self._param_.limites)
        self.limites.setToolTip(u"Afficher les limites dans le tableau de variations.")
        self.sizer_type.addSpacing(10)
        self.sizer_type.addWidget(self.limites)

        self.decimales_tabvar_tabsign = QSpinBox()
        self.decimales_tabvar_tabsign.setRange(-1, 20)
        self.decimales_tabvar_tabsign.setSuffix(u" décimales")
        self.decimales_tabvar_tabsign.setSpecialValueText(u"Valeurs exactes")
        self.decimales_tabvar_tabsign.setValue(self._param_.decimales_tabvar_tabsign)
        ##self.decimales_tabvar_tabsign.setAccelerated(True)
        aide = u"Nombre de décimales pour l'affichage des extrema, ou valeur exacte."
        self.decimales_tabvar_tabsign.setToolTip(aide)
        self.sizer_type.addSpacing(10)
        self.sizer_type.addWidget(self.decimales_tabvar_tabsign)

        self.decimales_tabval = QSpinBox()
        self.decimales_tabval.setRange(0, 20)
        self.decimales_tabval.setSuffix(u" décimales")
        self.decimales_tabval.setValue(self._param_.decimales_tabval)
        ##self.decimales_tabval.setAccelerated(True)
        aide = u"Nombre de décimales pour les valeurs du tableau."
        self.decimales_tabval.setToolTip(aide)
        self.sizer_type.addSpacing(10)
        self.sizer_type.addWidget(self.decimales_tabval)

        self.sizer_type.addSpacing(15)
        self.lbl_formatage = lbl = QLabel(u"Formatage des résultats :")
        self.sizer_type.addWidget(lbl)
        self.formatage_images = QLineEdit()
        ##self.formatage_images.setMinimumWidth(200)
        self.formatage_images.setText(self._param_.formatage_images)
        aide = u"Formatage à appliquer au résultat (VAL est la valeur du résultat)."
        lbl.setToolTip(aide)
        self.formatage_images.setToolTip(aide)
        self.sizer_type.addSpacing(10)
        self.sizer_type.addWidget(self.formatage_images)

        self.sizer_type.addStretch()

        self.sizer.addLayout(self.sizer_type)

        box = QGroupBox(u"Code LaTeX permettant de de générer le tableau", self)
        self.bsizer = QVBoxLayout()
        box.setLayout(self.bsizer)

        self.code_tableau = QTextEdit(self)
        self.code_tableau.setMinimumSize(700, 200)
        self.code_tableau.setReadOnly(True)
        self.bsizer.addWidget(self.code_tableau)

        self.copier_code = QPushButton(u"Copier dans le presse-papier", self)
        self.bsizer.addWidget(self.copier_code)

        txt = u"Pensez à rajouter dans l'entête de votre fichier LaTeX la ligne suivante :"
        self.bsizer.addWidget(QLabel(txt, self))

        self.sizer_entete = QHBoxLayout()
        self.code_entete = QLineEdit(self)
        self.code_entete.setMinimumWidth(200)
        self.code_entete.setReadOnly(True)
        self.code_entete.setText(u"\\usepackage{tabvar}")
        self.sizer_entete.addWidget(self.code_entete)
        self.copier_entete = QPushButton(u"Copier cette ligne", self)
        self.sizer_entete.addWidget(self.copier_entete)

        self.bsizer.addLayout(self.sizer_entete)

        self.sizer.addWidget(box)


        self.cb = QCheckBox(u"Copier automatiquement le code LaTeX dans le presse-papier.", self)
        self.cb.setChecked(self._param_.copie_automatique)
        self.sizer.addWidget(self.cb)

        self.setLayout(self.sizer)
        self.adjustSize()

        self.type_tableau.currentIndexChanged.connect(self.EvtChoix)
        self.EvtChoix()

        def copier_code():
            return self.vers_presse_papier(self.code_tableau.toPlainText())
        self.copier_code.clicked.connect(copier_code)

        def copier_entete():
            return self.vers_presse_papier(self.code_entete.text())
        self.copier_entete.clicked.connect(copier_entete)

        def regler_mode_copie():
            self._param_.copie_automatique = self.cb.isChecked()
            if self._param_.copie_automatique:
                copier_code()
        self.cb.stateChanged.connect(regler_mode_copie)

        def regler_cellspace():
            self._param_.utiliser_cellspace = self.utiliser_cellspace.isChecked()
            if self._param_.utiliser_cellspace:
                self.code_entete.setText(u"\\usepackage{cellspace}")
            else:
                self.code_entete.setText(u"")
            self.valider()
        self.utiliser_cellspace.stateChanged.connect(regler_cellspace)

        def regler_parametres(event=None):
            self._param_.derivee = self.derivee.isChecked()
            self._param_.limites = self.limites.isChecked()
            self._param_.formatage_images = self.formatage_images.text()
            self.valider()

        def regler_decimales(event=None):
            try:
                self.focus_widget = app.focusWidget()
                self._param_.decimales_tabvar_tabsign = self.decimales_tabvar_tabsign.value()
                self._param_.decimales_tabval = self.decimales_tabval.value()
                self.valider()
            finally:
                self.focus_widget = self.entree

        self.derivee.stateChanged.connect(regler_parametres)
        self.limites.stateChanged.connect(regler_parametres)
        self.formatage_images.editingFinished.connect(regler_parametres)
        self.decimales_tabvar_tabsign.valueChanged.connect(regler_decimales)
        self.decimales_tabval.valueChanged.connect(regler_decimales)

        self.focus_widget = self.entree


    def activer(self):
        Panel_simple.activer(self)
        # Actions à effectuer lorsque l'onglet devient actif
        self.entree.setFocus()


    def generer_code(self, commande, **kw):
        if not commande.strip():
            return
        # Utilisé pour la sauvegarde automatique:x+3

        self.modifie = True
        try:
            if self._param_.mode == 0:
                code_latex = tabvar(commande, derivee=self._param_.derivee,
                                    limites=self._param_.limites,
                                    decimales=self._param_.decimales_tabvar_tabsign,
                                    approche=(self._param_.decimales_tabvar_tabsign != -1))
            elif self._param_.mode == 1:
                code_latex = tabsign(commande, cellspace=self._param_.utiliser_cellspace,
                                    decimales=self._param_.decimales_tabvar_tabsign,
                                    approche=(self._param_.decimales_tabvar_tabsign != -1))
            elif self._param_.mode == 2:
                code_latex = tabval(commande,
                    formatage_antecedents=self._param_.formatage_antecedents,
                    formatage_images=self._param_.formatage_images,
                    precision=10**-self._param_.decimales_tabval)
            else:
                warning("Type de tableau non reconnu.")

            self.code_tableau.setText(code_latex)
            if self._param_.copie_automatique:
                self.vers_presse_papier(texte = code_latex)
            self.focus_widget.setFocus()
            self.message(u"Le code LaTeX a bien été généré.")
        except BaseException as erreur:
            self.message(u"Impossible de générer le code LaTeX. " + message(erreur))
            self.code_tableau.setText(u"<i><b>Erreur.</b> Impossible de générer le code LaTeX.</i>")
            self.entree.setFocus()
            if param.debug:
                raise


    def EvtChoix(self, event = None):
        self._param_.mode = self.type_tableau.currentIndex()
        # Tableaux de variations
        if self._param_.mode == 0:
            self.code_entete.setText(u"\\usepackage{tabvar}")
            self.entree.setToolTip(tabvar.__doc__)
            self.utiliser_cellspace.hide()
            self.derivee.show()
            self.limites.show()
            self.decimales_tabvar_tabsign.show()
            self.formatage_images.hide()
            self.lbl_formatage.hide()
            self.decimales_tabval.hide()
        # Tableaux de signes
        elif self._param_.mode == 1:
            self.utiliser_cellspace.show()
            self.derivee.hide()
            self.limites.hide()
            self.formatage_images.hide()
            self.lbl_formatage.hide()
            self.decimales_tabvar_tabsign.show()
            self.decimales_tabval.hide()
            self.entree.setToolTip(tabsign.__doc__)
            if self._param_.utiliser_cellspace:
                self.code_entete.setText(u"\\usepackage{cellspace}")
            else:
                self.code_entete.setText(u"")
        # Tableaux de valeurs
        elif self._param_.mode == 2:
            self.utiliser_cellspace.hide()
            self.derivee.hide()
            self.limites.hide()
            self.decimales_tabvar_tabsign.hide()
            self.decimales_tabval.show()
            self.lbl_formatage.show()
            self.formatage_images.show()
            self.entree.setToolTip(tabval.__doc__)
            self.code_entete.setText(u"")
        self.valider()


    def valider(self):
        try:
            self.entree.valider()
        except Exception:
            print_error()
