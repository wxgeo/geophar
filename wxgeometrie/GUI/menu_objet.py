# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

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

from functools import partial

from PyQt4.QtGui import (QDialog, QVBoxLayout, QHBoxLayout, QFrame, QLineEdit,
                         QInputDialog, QTextEdit, QLabel, QCheckBox, QPushButton,
                         QMenu,)
from PyQt4.QtCore import Qt

from ..geolib import Texte_generique, Point_generique, Champ, Texte, Polygone_generique
from .proprietes_objets import Proprietes
from ..pylib import print_error
from .qtlib import PopUpMenu


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

        if isinstance(select, Texte_generique):
            action = self.addAction(u"Éditer le texte")
            action.triggered.connect(self.etiquette)
            action = self.addAction(u"Formatage mathématique" if select.style('formatage') == 'rien'
                                            else u"Formatage par défaut")
            action.triggered.connect(self.mode_formatage)

        elif select.etiquette is not None:
            action = self.addAction(u"Texte associé")
            action.triggered.connect(self.etiquette)
            action = self.addAction((u"Masquer" if select.label() else u"Afficher") + u" nom/texte")
            action.triggered.connect(self.masquer_nom)

        self.addSeparator()

        action = self.addAction(u"Redéfinir")
        action.triggered.connect(self.redefinir)

        self.addSeparator()

        app_style = self.addMenu(u"Appliquer ce style")
        if isinstance(select, Polygone_generique):
            action = app_style.addAction(u"aux côtés de ce polygone")
            action.triggered.connect(self.copier_style_cotes)
        action = app_style.addAction(u"aux autres " + select.style('sous-categorie'))
        action.triggered.connect(partial(self.copier_style, critere='sous-categorie'))
        action = app_style.addAction(u"à tous les objets compatibles (%s)"
                                                % select.style('categorie'))
        action.triggered.connect(partial(self.copier_style, critere='categorie'))

        self.addSeparator()

        if isinstance(select, Point_generique):
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
                    self.executer(u"%s.renommer(%s, afficher_nom=True)" %(select.nom, repr(txt)))
                except:
                    print_error()
                    continue
            break


    def etiquette(self):
        select = self.canvas.select
        etiquette = select.etiquette if select.etiquette is not None else select
        old = {'mode': etiquette.style("mode"), 'texte': etiquette.texte}

        # ----------------
        # Cas particuliers
        # ----------------

        if isinstance(select, Champ):
            if select.style('choix'):
                choix = select.style('choix')
                try:
                    index = choix.index(select.texte)
                except ValueError:
                    index = 0
                text, ok = QInputDialog.getItem(self.canvas, u"Choisir une valeur",
                                u"Réponse :", choix, index, False)
            else:
                text, ok = QInputDialog.getText(self.canvas, u"Éditer le champ",
                            u"Réponse :", QLineEdit.Normal, select.texte)
            if ok:
                select.label(text)
            return

        # -----------
        # Cas général
        # -----------

        dlg = QDialog(self.canvas)
        dlg.setWindowTitle(u"Changer la légende de l'objet (texte quelconque)")

        sizer = QVBoxLayout()
        sizer.addWidget(QLabel(u"Note: le code LATEX doit etre entre $$. Ex: $\\alpha$"))

        dlg.text = QTextEdit(dlg)
        dlg.text.setPlainText(etiquette.texte)
        dlg.setMinimumSize(300, 50)
        sizer.addWidget(dlg.text)

        dlg.cb = QCheckBox(u"Interpréter la formule", dlg)
        dlg.cb.setChecked(select.mode_affichage == 'formule')
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
                    nom = select.nom
                    txt = repr(dlg.text.toPlainText())
                    mode = repr('formule' if dlg.cb.isChecked() else 'texte')
                    self.executer(u"%s.label(%s, %s)" %(nom, txt, mode))
                except:
                    # Au cas où une formule incorrecte fasse buguer l'affichage (?)
                    etiquette.texte = old['texte']
                    etiquette.style(mode=old['mode'])
                    print_error()
                    continue
            else:
                etiquette.texte = old['texte']
                etiquette.style(mode=old['mode'])
            break

    def copier_style(self, critere='categorie'):
        u"""Applique le style de l'objets à tous les objets de même catégorie.

        Si `critere='sous-categorie'`, le style est seulement appliqué aux objets
        de même sous-catégorie (ex. 'vecteurs'), et non à la catégorie entière
        (ex. 'lignes').
        """
        select = self.canvas.select
        feuille = self.canvas.feuille_actuelle
        cible = select.style(critere)
        with self.canvas.geler_affichage(actualiser=True, sablier=True):
            for obj in feuille.liste_objets(objets_caches=False, etiquettes=True):
                if obj.style(critere) == cible:
                    obj.copier_style(select)
            feuille.interprete.commande_executee()

    def copier_style_cotes(self):
        u"Applique le style du polygone à ses côtés."
        select = self.canvas.select
        with self.canvas.geler_affichage(actualiser=True, sablier=True):
            for cote in select.cotes:
                cote.copier_style(select)
            self.canvas.feuille_actuelle.interprete.commande_executee()

    def masquer_nom(self):
        select = self.canvas.select
        if select.label():
            mode = 'rien'
        else:
            if select.legende:
                mode = 'texte'
            else:
                mode = 'nom'
        self.executer(u"%s.label(mode = %r)" % (select.nom, mode))

    def mode_formatage(self):
        select = self.canvas.select
        actuel = select.style('formatage')
        select.style(formatage=('math' if actuel == 'rien' else 'rien'))

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
