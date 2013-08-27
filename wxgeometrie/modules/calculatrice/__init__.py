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

from functools import partial

from PyQt4.QtGui import (QHBoxLayout, QVBoxLayout, QCheckBox, QIcon, QPushButton,
                         QTextEdit, QMenu, QLabel, QSpinBox, QCursor, QTextCursor,
                         QToolButton, QWidget, QTabWidget, QGroupBox, QComboBox)
from PyQt4.QtCore import Qt

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ...GUI.ligne_commande import LigneCommande
from ...GUI.qtlib import png
from ...GUI.inspecteur import FenCode
from ...GUI.menu import MenuBar
from ...GUI.panel import Panel_simple
from ...mathlib.interprete import Interprete
from ...mathlib.parsers import latex2mathtext
from ...mathlib.end_user_functions import __classement__

from ...pylib import print_error, uu, debug, no_argument, eval_safe
from ... import param


class CalculatriceMenuBar(MenuBar):
    def __init__(self, panel):
        MenuBar.__init__(self, panel)
        self.ajouter(u"Fichier", [u"Réinitialiser",
                                    u"Réinitialiser la calculatrice.", "Ctrl+N",
                                    self.panel.initialiser],
                                [u"ouvrir"], [u"enregistrer"],
                                [u"enregistrer_sous"], ['session'], None, ["quitter"])
        self.ajouter(u"Affichage", ["onglet"], ["plein_ecran"])
        for rubrique in __classement__:
            self.ajouter(rubrique, *(self.formater(contenu, rubrique != "Symboles") for contenu in __classement__[rubrique]))
            # pas de parenthese apres un symbole
        self.ajouter(u"Outils",
                        [u"Mémoriser le résultat", u"Copie le resultat du calcul dans le presse-papier, afin de pouvoir l'utiliser ailleurs.", "Ctrl+M", self.panel.vers_presse_papier],
#                        [u"LaTeX",
#                            [u"Inverser les sommes", "Inverser l'ordre d'affichage des termes des sommes.", None, self.panel.inverser_sommes_LaTeX, self.panel.inverser_sommes_LaTeX]
#                            ],
                        [u"options"],
                        )
        self.ajouter(u"Avancé",
                        [u"État interne de l'interprète", u"État de l'interprète de commandes.", u"Ctrl+H", self.panel.EtatInterne],
                        [u"ligne_commande"],
                        ["debug"],
                        )
        self.ajouter("?")


    def formater(self, contenu, parentheses = True):
        if contenu is None:
            return
        titre, nom, doc = contenu
        return [titre, doc, "", partial(self.panel.insere, nom=nom, parentheses=parentheses)]



class BoutonValider(QToolButton):

    modes = [('exact', u'résultats exacts'), ('approche', u'résultats approchés'),
             ('scientifique', u'résultats en écriture scientifique')]

    def __init__(self, parent):
        QToolButton.__init__(self)
        self.parent = parent
        self.setAutoRaise(True)
        self.mode_normal()

        self.menu = menu = QMenu(self)
        self.setMenu(menu)
        for mode, titre in self.modes:
            nom = 'mode_' + mode
            action = menu.addAction(QIcon(png(nom)), titre)
            action.setIconVisibleInMenu(True)
            action.triggered.connect(getattr(self, nom))
        self.clicked.connect(self.mode_occupe)


    def _set_icon(self, nom):
        pix = png(nom)
        self.setIcon(QIcon(pix))
        self.setIconSize(pix.size())

    def mode_exact(self, *args):
        self._set_icon('mode_exact_')
        self.parent.param("calcul_exact", True)
        self.parent.param("ecriture_scientifique", False)

    def mode_approche(self, *args):
        self._set_icon('mode_approche_')
        self.parent.param("calcul_exact", False)
        self.parent.param("ecriture_scientifique", False)

    def mode_scientifique(self, *args):
        self._set_icon('mode_scientifique_')
        self.parent.param("calcul_exact", False)
        self.parent.param("ecriture_scientifique", True)

    def mode_occupe(self):
        self._set_icon('thinking2_')

    def mode_normal(self):
        if self.parent.param("calcul_exact"):
            self.mode_exact()
        elif self.parent.param("ecriture_scientifique"):
            self.mode_scientifique()
        else:
            self.mode_approche()



class PaveNumerique(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.parent = parent
        ### Pave numerique de la calculatrice ###
        # On construit le pavé de la calculatrice.
        # Chaque bouton du pavé doit provoquer l'insertion de la commande correspondante.

        self.pave = pave = QVBoxLayout()
#        pave.setSpacing(1)
        boutons = ["2nde", "ans", "ouv", "ferm", "egal", "7", "8", "9", "div", "x", "4", "5", "6", "mul", "y", "1", "2", "3", "minus", "z", "0", "pt", "pow", "plus", "t", "rac", "sin", "cos", "tan", "exp", "i", "pi", "e", "abs", "mod"]
        inserer = ["", "ans()", "(", ")", "=", "7", "8", "9",  "/", "x", "4", "5", "6", "*", "y", "1", "2", "3", "-", "z", "0", ".", "^", "+", "t", "sqrt(", ("sin(", "asin(", "sinus / arcsinus"), ("cos(", "acos(", "cosinus / arccosinus"), ("tan(", "atan(", "tangente / arctangente"), ("exp(", "ln(", "exponentielle / logarithme neperien"), ("i", "cbrt(", "i / racine cubique"), ("pi", "sinh(", "pi / sinus hyperbolique"), ("e", "cosh", "e / cosinus hyperbolique"), ("abs(", "tanh", "valeur absolue / tangente hyperbolique"), (" mod ", "log10(", "modulo / logarithme decimal")]

        self.seconde = False # indique si la touche 2nde est activee.

        self.actions = [self.touche_2nde]

        for i, nom_bouton in enumerate(boutons):
            # On aligne les boutons de la calculatrice par rangées de 5.
            if i%5 == 0:
                self.rangee = rangee = QHBoxLayout()
                rangee.addStretch(1)
                pave.addLayout(rangee)

            # Ensuite, on construit une liste de fonctions, parallèlement à la liste des boutons.
            if i > 0:
                self.actions.append(partial(self.action, commande=inserer[i]))

            bouton = QPushButton()
            pix = png('btn_' + nom_bouton)
            bouton.setIcon(QIcon(pix))
            bouton.setIconSize(pix.size())
            bouton.setFlat(True)
#            bouton.SetBackgroundColour(self.GetBackgroundColour())
            rangee.addWidget(bouton)
            if i%5 == 4:
                rangee.addStretch(2)
            # A chaque bouton, on associe une fonction de la liste.
            bouton.clicked.connect(self.actions[i])
            if type(inserer[i]) == tuple:
                bouton.setToolTip(inserer[i][2])

            self.setLayout(self.pave)

    def touche_2nde(self, event=None):
        self.seconde = not self.seconde
        if self.seconde:
            self.message(u"Touche [2nde] activée.")
        else:
            self.message("")

    def action(self, event=None, commande=''):
        entree = self.parent.entree
        if type(commande) == tuple:
            entree.insert(commande[self.seconde])
        else:
            entree.insert(commande)
        n = entree.cursorPosition()
        entree.setFocus()
        entree.setCursorPosition(n)
        self.seconde = False
        self.parent.message("")



class Options(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.parent = parent
        prm = parent.param

        self.ensembles = ('R', 'C')

        ### Liste des options de la calculatrice ###
        self.pave = QVBoxLayout()

        # Chiffres significatifs
        box = QGroupBox(u"Mode calcul approché")
        box_layout = QVBoxLayout()
        box.setLayout(box_layout)

        ligne = QHBoxLayout()
        box_layout.addLayout(ligne)
        ligne.addWidget(QLabel(u"Afficher "))
        self.sc_precision_affichage = sc = QSpinBox(self)
        # param.precision_calcul = 60 par défaut
        sc.setRange(1, 50)
        sc.setValue(prm("precision_affichage"))
        sc.valueChanged.connect(self.EvtPrecisionAffichage)
        ligne.addWidget(sc)
        ligne.addWidget(QLabel(u" chiffre(s) significatif(s)."))
        ligne.addStretch()

        self.pave.addWidget(box)

        # Nombre de décimales
        box = QGroupBox(u"Mode écriture scientifique")
        box_layout = QVBoxLayout()
        box.setLayout(box_layout)

        ligne = QHBoxLayout()
        box_layout.addLayout(ligne)
        ligne.addWidget(QLabel(u"Arrondir les résultats à "))
        self.sc_decimales = sc = QSpinBox(self)
        sc.setRange(0, 11)
        sc.setValue(prm("ecriture_scientifique_decimales"))
        sc.valueChanged.connect(self.EvtDecimales)
        ligne.addWidget(sc)
        ligne.addWidget(QLabel(u" décimale(s)."))
        ligne.addStretch()

        self.pave.addWidget(box)

        box = QGroupBox(u"Copie Automatique")
        box_layout = QVBoxLayout()
        box.setLayout(box_layout)
        # Copie du résultat dans le presse-papier
        ligne = QHBoxLayout()
        box_layout.addLayout(ligne)
        self.cb_copie_automatique = cb = QCheckBox(self)
        cb.setChecked(prm("copie_automatique"))
        cb.stateChanged.connect(self.EvtCopieAutomatique)
        ligne.addWidget(cb)
        ligne.addWidget(QLabel(u"Copie du résultat dans le presse-papier."))
        ligne.addStretch()

        # En mode LaTeX
        ligne = QHBoxLayout()
        box_layout.addLayout(ligne)
        self.cb_copie_automatique_LaTeX = cb = QCheckBox(self)
        cb.setChecked(prm("copie_automatique_LaTeX"))
        ligne.addWidget(cb)
        cb.stateChanged.connect(self.EvtCopieAutomatiqueLatex)
        self.st_copie_automatique_LaTeX = st = QLabel(u"Copie au format LaTeX (si possible).")
        ligne.addWidget(st)
        ligne.addStretch()

        self.pave.addWidget(box)
        #~ self.pave.addStretch()

        box = QGroupBox(u"Ensemble de résolution")
        box_layout = QVBoxLayout()
        box.setLayout(box_layout)
        ligne = QHBoxLayout()
        box_layout.addLayout(ligne)
        ligne.addWidget(QLabel(u'Résoudre et factoriser dans '))
        self.cb_ensemble = cb = QComboBox()
        ligne.addWidget(cb)
        cb.addItems((u'R (réels)', u'C (complexes)'))
        cb.setCurrentIndex(self.ensembles.index(prm('ensemble')))
        cb.currentIndexChanged.connect(self.EvtEnsemble)
        self.pave.addWidget(box)
        self.pave.addStretch()

        self.setLayout(self.pave)
        # Pour (dés)activer la ligne "Copie au format LaTeX" au besoin.
        self.EvtCopieAutomatique()

    def EvtPrecisionAffichage(self, event=None):
        val = self.sc_precision_affichage.value()
        self.parent.param("precision_affichage", val)


    def EvtDecimales(self, event=None):
        val = self.sc_decimales.value()
        self.parent.param("ecriture_scientifique_decimales", val)


    def EvtCopieAutomatique(self, event=None):
        valeur = self.cb_copie_automatique.isChecked()
        self.parent.param("copie_automatique", valeur)
        if valeur:
            self.cb_copie_automatique_LaTeX.setEnabled(True)
            self.st_copie_automatique_LaTeX.setEnabled(True)
        else:
            self.cb_copie_automatique_LaTeX.setEnabled(False)
            self.st_copie_automatique_LaTeX.setEnabled(False)


    def EvtCopieAutomatiqueLatex(self, event=None):
        val = self.cb_copie_automatique_LaTeX.isChecked()
        self.parent.param("copie_automatique_LaTeX", val)


    def EvtEnsemble(self, index):
        self.parent.param("ensemble", self.ensembles[index])




class OngletsCalc(QTabWidget):
    def __init__(self, parent):
        ##self.parent = parent
        QTabWidget.__init__(self, parent)
        self.addTab(PaveNumerique(parent), u' Pavé numérique ')
        self.addTab(Options(parent), u'Options')
        self.setTabPosition(QTabWidget.South)
        self.setStyleSheet("""
QTabBar::tab:selected {
background: white;
border: 1px solid #C4C4C3;
border-top-color: white; /* same as the pane color */
border-bottom-left-radius: 4px;
border-bottom-right-radius: 4px;
border-top-left-radius: 0px;
border-top-right-radius: 0px;
min-width: 8ex;
padding: 7px;
}
QStackedWidget {background:white}
QTabBar QToolButton {
background:white;
border: 1px solid #C4C4C3;
border-top-color: white; /* same as the pane color */
border-bottom-left-radius: 4px;
border-bottom-right-radius: 4px;
border-top-left-radius: 0px;
border-top-right-radius: 0px;
}
""")





class Calculatrice(Panel_simple):
    titre = u"Calculatrice" # Donner un titre a chaque module

    def __init__(self, *args, **kw):
        Panel_simple.__init__(self, *args, **kw)
        self.interprete = Interprete(calcul_exact = self.param("calcul_exact"),
                                ecriture_scientifique = self.param("ecriture_scientifique"),
                                formatage_OOo = self.param("formatage_OOo"),
                                formatage_LaTeX = self.param("formatage_LaTeX"),
                                ecriture_scientifique_decimales = self.param("ecriture_scientifique_decimales"),
                                precision_calcul = self.param("precision_calcul"),
                                precision_affichage = self.param("precision_affichage"),
                                simpify = True,
                                ensemble=self.param('ensemble'),
                                )

        bouton = BoutonValider(self)
        bouton.setToolTip(u"Laissez appuyé pour changer de mode.")
        self.entree = entree = LigneCommande(self, longueur=550,
                                action=self.affichage_resultat, bouton=bouton)
        entree.setToolTip(u"[Maj]+[Entrée] pour une valeur approchée.")
        self.entree.texte.setContextMenuPolicy(Qt.CustomContextMenu)
        self.entree.texte.customContextMenuRequested.connect(self.EvtMenu)


        self.sizer = sizer = QVBoxLayout()
        sizer.addWidget(entree)
        self.corps = corps = QHBoxLayout()
        sizer.addLayout(corps)
        self.resultats = resultats = QTextEdit(self)
        resultats.setMinimumSize(450, 310)
        resultats.setReadOnly(True)
        corps.addWidget(resultats, 1)
        onglets = OngletsCalc(self)
        corps.addWidget(onglets)
        onglets.setCurrentIndex(self.param('onglet'))
        onglets.currentChanged.connect(self.EvtCurrentChanged)

        self.figure = Figure(figsize=(5,1.3), frameon=True, facecolor="w")
        self.visualisation = FigureCanvas(self.figure)
        self.axes = axes = self.figure.add_axes([0, 0, 1, 1], frameon=False)
        axes.axison = False
        self.pp_texte = axes.text(0.5, 0.5, "", horizontalalignment='center',
                verticalalignment='center', transform = axes.transAxes, size=18)
        self.visualisation.setContextMenuPolicy(Qt.CustomContextMenu)
        self.visualisation.customContextMenuRequested.connect(self.EvtMenuVisualisation)
        sizer.addWidget(self.visualisation)

        self.setLayout(self.sizer)
        self.initialiser()


    def activer(self):
        Panel_simple.activer(self)
        # Actions à effectuer lorsque l'onglet devient actif
        self.entree.setFocus()


    def _sauvegarder(self, fgeo):
        fgeo.contenu["Calculatrice"] = [{}]
        fgeo.contenu["Calculatrice"][0]["Historique"] = [repr(self.entree.historique)]
#        fgeo.contenu["Calculatrice"][0]["Resultats"] = [repr(self.interprete.derniers_resultats)]
        fgeo.contenu["Calculatrice"][0]["Affichage"] = [self.resultats.toPlainText()]
        fgeo.contenu["Calculatrice"][0]["Etat_interne"] = [self.interprete.save_state()]
        ##fgeo.contenu["Calculatrice"][0]["Options"] = [{}]
        ##for i in range(len(self.options)):
            ##fgeo.contenu["Calculatrice"][0]["Options"][0][self.options[i][1]] = [str(self.options_box[i].isChecked())]



    def _ouvrir(self, fgeo):
        if fgeo.contenu.has_key("Calculatrice"):
            calc = fgeo.contenu["Calculatrice"][0]
            self.initialiser()

            self.entree.historique = eval_safe(calc["Historique"][0])
#            self.interprete.derniers_resultats = securite.eval_safe(calc["Resultats"][0])
            resultats = calc["Affichage"][0]
            if resultats:
                resultats += '\n\n'
            self.resultats.setPlainText(resultats)
            self.resultats.moveCursor(QTextCursor.End)
            self.interprete.load_state(calc["Etat_interne"][0])

            ##liste = calc["Options"][0].items()
            ##options = [option for aide, option in self.options]
            ##for key, value in liste:
                ##value = eval_safe(value[0])
                ##self.param(key, value)
                ##if key in options:
                    ##self.options_box[options.index(key)].setChecked(value)
            # il faudrait encore sauvegarder les variables, mais la encore, 2 problemes :
            # - pb de securite pour evaluer les variables
            # - pb pour obtenir le code source d'une fonction.
            # Pour remedier a cela, il faut envisager de :
            # - creer un module d'interpretation securisee.
            # - rajouter a chaque fonction un attribut __code__, ou creer une nouvelle classe.


    def modifier_pp_texte(self, chaine):
        u"""Modifier le résultat affiché en LaTeX (pretty print)."""
        if self.param("latex"):
            # On utilise directement LaTeX pour le rendu
            chaine = "$" + chaine + "$"
        else:
            # On utilise le parser matplotlib.mathtext, moins complet mais bien
            # plus rapide. Certaines adaptations doivent être faites.
            chaine = latex2mathtext(chaine)
        self.pp_texte.set_text(chaine)
        self.visualisation.draw()

    def vers_presse_papier(self, event = None, texte = None):
        if texte is None:
            texte = self.dernier_resultat
        Panel_simple.vers_presse_papier(texte)

    def copier_latex(self, event = None):
        self.vers_presse_papier(texte = self.interprete.latex_dernier_resultat.strip("$"))

    def initialiser(self, event = None):
        self.dernier_resultat = "" # dernier resultat, sous forme de chaine formatee pour l'affichage
        self.entree.initialiser()
        self.interprete.initialiser()
        self.resultats.clear()

    def affichage_resultat(self, commande, **kw):
        # Commandes spéciales:
        if commande in ('clear', 'clear()', 'efface', 'efface()'):
            self.initialiser()
            self.modifier_pp_texte(u"Calculatrice réinitialisée.")
            return

        self.modifie = True
        try:
            try:
                ##self.parent.parent.application.processEvents()
                if kw.get("shift"):
                    self.interprete.calcul_exact = False
                resultat, latex = self.interprete.evaluer(commande)
                if latex == "$?$": # provoque une erreur (matplotlib 0.99.1.1)
                    latex = u"Désolé, je ne sais pas faire..."
            finally:
                self.interprete.calcul_exact = self.param('calcul_exact')
                self.entree.bouton.mode_normal()
            aide = resultat.startswith("\n== Aide sur ")
            if aide:
                latex = ''
            elif not latex:
                latex = resultat
            #LaTeX
            debug("Expression LaTeX: " + latex)
            try:
                try:
                    # Affichage en LaTeX si possible.
                    self.modifier_pp_texte(latex)
                except Exception:
                    print_error()
                    # Sinon, affichage en texte simple.
                    #  `matplotlib.mathtext` est encore loin d'être
                    # pleinement compatible avec LaTeX !
                    self.modifier_pp_texte(resultat)
            except Exception:
                print_error()
                # Si tout a raté... mais ça ne devrait jamais arrivé.
                self.modifier_pp_texte("<Affichage impossible>")
            #Presse-papier
            self.dernier_resultat = resultat
            if self.param("copie_automatique"):
                if self.param("copie_automatique_LaTeX"):
                    self.copier_latex()
                else:
                    self.vers_presse_papier()
            # TextCtrl
            numero = str(len(self.interprete.derniers_resultats))
            # Évite le décalage entre la première ligne et les suivantes (matrices)
            if "\n" in resultat and not aide:
                resultat = "\n" + "\n".join(20*" " + ligne for ligne in resultat.split("\n"))
            self.resultats.moveCursor(QTextCursor.End)
            self.resultats.insertPlainText(u" Calcul n\xb0" + numero + " :   "
                                                        + uu(commande) + u"\n Résultat :"
                                                        + " "*(4+len(numero))
                                                        + resultat + "\n__________________\n\n")
            self.resultats.moveCursor(QTextCursor.End)
            self.message(u"Calcul effectué." + self.interprete.warning)
            self.entree.clear()
#            self.resultats.setCursorPosition(len(self.resultats.plainText()))
#            self.resultats.setFocus()
#            self.resultats.ScrollLines(1)
            self.entree.setFocus()
        except Exception:
            self.message(u"Calcul impossible.")
            self.entree.setFocus()
            if param.debug:
                raise


    def insere(self, event=None, nom='', parentheses=True):
        entree = self.entree
        deb, fin = entree.getSelection()
        if parentheses:
            entree.setCursorPosition(fin)
            entree.insert(")")
            entree.setCursorPosition(deb)
            entree.insert(nom + "(")
            entree.setFocus()
            if deb == fin:
                final = fin + len(nom) + 1
            else:
                final = fin + len(nom) + 2
        else:
            entree.insert(nom)
            final = fin + len(nom)
        entree.setFocus()
        entree.setCursorPosition(final)


    def EvtMenu(self, event):
#        if not event.ControlDown():
#            event.Skip()
#            return
#            entree.setSelection(final, final)
        menu = QMenu()
        menu.setWindowTitle(u"Fonctions mathématiques")
        debut = True
        for rubrique in __classement__:
            if not debut:
                menu.addSeparator()
            debut = False
            for titre, nom, doc in filter(None, __classement__[rubrique]):
                action = menu.addAction(titre, partial(self.insere, nom=nom, parentheses=(rubrique != "Symboles")))
                # Pas de parenthèses après un symbole.
                action.setToolTip(doc)
        menu.exec_(QCursor.pos())


    def EvtMenuVisualisation(self, event):
        menu = QMenu()
        action = menu.addAction("Copier LaTeX", self.copier_latex)
        action.setToolTip("Copier le code LaTeX dans le presse-papier.")
        menu.exec_(QCursor.pos())
#        self.PopupMenu(menu)
#        menu.Destroy()

    def EvtCurrentChanged(self, index):
        self.param('onglet', index)

    def param(self, parametre, valeur = no_argument, defaut = False):
        if valeur is not no_argument:
            setattr(self.interprete, parametre, valeur)
        return Panel_simple.param(self, parametre = parametre, valeur = valeur, defaut = defaut)

    def EtatInterne(self, event):
        contenu = self.interprete.save_state()
        h = FenCode(self, u"État interne de l'inteprète", contenu, self.interprete.load_state)
        h.show()
