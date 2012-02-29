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

#import wx
from PyQt4.QtGui import (QHBoxLayout, QVBoxLayout, QCheckBox, QIcon, QPushButton,
                         QTextEdit, QMenu, QLabel, QSpinBox, QCursor, QTextCursor)
from PyQt4.QtCore import Qt

#from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ...GUI.ligne_commande import LigneCommande
from ...GUI.wxlib import png
from ...GUI.inspecteur import FenCode
from ...GUI import MenuBar, Panel_simple
from ...mathlib.interprete import Interprete
from ...mathlib.end_user_functions import __classement__

from ...pylib import print_error, uu, debug, no_argument, eval_safe
from ... import param


class CalculatriceMenuBar(MenuBar):
    def __init__(self, panel):
        MenuBar.__init__(self, panel)
        self.ajouter(u"Fichier", ["quitter"])
        self.ajouter(u"Affichage", ["onglet"])
        for rubrique in __classement__:
            self.ajouter(rubrique, *(self.formater(contenu, rubrique != "Symboles") for contenu in __classement__[rubrique]))
            # pas de parenthese apres un symbole
        self.ajouter(u"Outils",
                        [u"Mémoriser le résultat", u"Copie le resultat du calcul dans le presse-papier, afin de pouvoir l'utiliser ailleurs.", "Ctrl+M", self.panel.vers_presse_papier],
                        [u"Réinitialiser", u"Réinitialiser la calculatrice.", "Ctrl+I", self.panel.initialiser],
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

#    def generer_fonction(self, nom, parenthese = True):
#        def f(event = None, panel = self.panel, nom = nom, parenthese = parenthese):
#            entree = panel.entree
#            deb, fin = panel.entree.getSelection()
#            if parenthese:
#                panel.entree.setCursorPosition(fin)
#                panel.entree.insert(")")
#                panel.entree.setCursorPosition(deb)
#                panel.entree.insert(nom + "(")
#                panel.entree.setFocus()
#                if deb == fin:
#                    final = fin + len(nom) + 1
#                else:
#                    final = fin + len(nom) + 2
#            else:
#                panel.entree.insert(nom)
#                final = fin + len(nom)
#            panel.entree.setFocus()
#            panel.entree.setCursorPosition(final)
#            panel.entree.setSelection(final, final)
#        return f

#    def insere(event=None, nom=nom, parentheses=parentheses):
#        entree = self.panel.entree
#        deb, fin = panel.entree.getSelection()
#        if parenthese:
#            panel.entree.setCursorPosition(fin)
#            panel.entree.insert(")")
#            panel.entree.setCursorPosition(deb)
#            panel.entree.insert(nom + "(")
#            panel.entree.setFocus()
#            if deb == fin:
#                final = fin + len(nom) + 1
#            else:
#                final = fin + len(nom) + 2
#        else:
#            panel.entree.insert(nom)
#            final = fin + len(nom)
#        panel.entree.setFocus()
#        panel.entree.setCursorPosition(final)
#        panel.entree.setSelection(final, final)




class Calculatrice(Panel_simple):
    __titre__ = u"Calculatrice" # Donner un titre a chaque module

    def __init__(self, *args, **kw):
        Panel_simple.__init__(self, *args, **kw)
        self.interprete = Interprete(calcul_exact = self.param("calcul_exact"),
                                ecriture_scientifique = self.param("ecriture_scientifique"),
                                changer_separateurs = self.param("changer_separateurs"),
                                separateurs_personnels = self.param("separateurs_personnels"),
                                copie_automatique = self.param("copie_automatique"),
                                formatage_OOo = self.param("formatage_OOo"),
                                formatage_LaTeX = self.param("formatage_LaTeX"),
                                ecriture_scientifique_decimales = self.param("ecriture_scientifique_decimales"),
                                precision_calcul = self.param("precision_calcul"),
                                precision_affichage = self.param("precision_affichage"),
                                simpify = True,
                                )

##        self.entrees = wx.BoxSizer(wx.HORIZONTAL)
##        self.entree = wx.TextCtrl(self, size = (550, -1), style = wx.TE_PROCESS_ENTER)
##        self.entrees.Add(self.entree, 1, wx.ALL|wx.GROW, 5)
##        self.valider = wx.Button(self, wx.ID_OK)
##        self.entrees.Add(self.valider, 0, wx.ALL, 5)
        self.entree = entree = LigneCommande(self, longueur = 550, action = self.affichage_resultat)
        entree.setToolTip(u"[Maj]+[Entrée] pour une valeur approchée.")
        self.entree.texte.setContextMenuPolicy(Qt.CustomContextMenu)
        self.entree.texte.customContextMenuRequested.connect(self.EvtMenu)


        self.sizer = sizer = QVBoxLayout()
        sizer.addWidget(entree)
        self.corps = corps = QHBoxLayout()
        sizer.addLayout(corps)
        self.gauche = gauche = QVBoxLayout()
        corps.addLayout(gauche, 1)
        self.resultats = resultats = QTextEdit(self)
        resultats.setMinimumSize(450, 310)
        resultats.setReadOnly(True)
        gauche.addWidget(resultats)

        self.figure = Figure(figsize=(5,1.3), frameon=True, facecolor="w")
        self.visualisation = FigureCanvas(self.figure)
        self.axes = axes = self.figure.add_axes([0, 0, 1, 1], frameon=False)
        axes.axison = False
        self.pp_texte = axes.text(0.5, 0.5, "", horizontalalignment='center', verticalalignment='center', transform = axes.transAxes, size=18)
        gauche.addWidget(self.visualisation) # wx.ALL|wx.ALIGN_CENTER
        self.visualisation.setContextMenuPolicy(Qt.CustomContextMenu)
        self.visualisation.customContextMenuRequested.connect(self.EvtMenuVisualisation)

        ### Pave numerique de la calculatrice ###
        # On construit le pavé de la calculatrice.
        # Chaque bouton du pavé doit provoquer l'insertion de la commande correspondante.

        self.pave = pave = QVBoxLayout()
        corps.addLayout(pave)
#        pave.setSpacing(1)
        boutons = ["2nde", "ans", "ouv", "ferm", "egal", "7", "8", "9", "div", "x", "4", "5", "6", "mul", "y", "1", "2", "3", "minus", "z", "0", "pt", "pow", "plus", "t", "rac", "sin", "cos", "tan", "exp", "i", "pi", "e", "abs", "mod"]
        inserer = ["", "ans()", "(", ")", "=", "7", "8", "9",  "/", "x", "4", "5", "6", "*", "y", "1", "2", "3", "-", "z", "0", ".", "^", "+", "t", "sqrt(", ("sin(", "asin(", "sinus / arcsinus"), ("cos(", "acos(", "cosinus / arccosinus"), ("tan(", "atan(", "tangente / arctangente"), ("exp(", "ln(", "exponentielle / logarithme neperien"), ("i", "cbrt(", "i / racine cubique"), ("pi", "sinh(", "pi / sinus hyperbolique"), ("e", "cosh", "e / cosinus hyperbolique"), ("abs(", "tanh", "valeur absolue / tangente hyperbolique"), (" mod ", "log10(", "modulo / logarithme decimal")]

        self.seconde = False # indique si la touche 2nde est activee.

        def action(event = None):
            self.seconde = not self.seconde
            if self.seconde:
                self.message(u"Touche [2nde] activée.")
            else:
                self.message("")

        self.actions = [action]

        for i in range(len(boutons)):
            # On aligne les boutons de la calculatrice par rangées de 5.
            if i%5 == 0:
                self.rangee = rangee = QHBoxLayout()
                rangee.addStretch(1)
                pave.addLayout(rangee)

            # Ensuite, on construit une liste de fonctions, parallèlement à la liste des boutons.
            if i > 0:
                #XXX: ce serait plus propre en utilisant partial().
                def action(event = None, entree = self.entree, j = i):
                    if type(inserer[j]) == tuple:
                        entree.insert(inserer[j][self.seconde])
                    else:
                        entree.insert(inserer[j])
                    n = entree.cursorPosition()
                    entree.setFocus()
                    entree.setCursorPosition(n)
                    self.seconde = False
                    self.message("")
                self.actions.append(action)

            bouton = QPushButton()
            pix = png('btn_' + boutons[i])
            bouton.setIcon(QIcon(pix))
            bouton.setIconSize(pix.size())
            bouton.setFlat(True)
#            bouton.setSize()
#            bouton.SetBackgroundColour(self.GetBackgroundColour())
            rangee.addWidget(bouton)
            if i%5 == 4:
                rangee.addStretch(2)
            # A chaque bouton, on associe une fonction de la liste.
            bouton.clicked.connect(self.actions[i])
            if type(inserer[i]) == tuple:
                bouton.setToolTip(inserer[i][2])

#        self.pave.Add(QHBoxLayout())


        ### Liste des options ###
        # En dessous du pavé apparait la liste des différents modes de fonctionnement de la calculatrice.

        # Calcul exact
        ligne = QHBoxLayout()
        pave.addLayout(ligne)
        self.cb_calcul_exact = QCheckBox(self)
        self.cb_calcul_exact.setChecked(not self.param("calcul_exact"))
        ligne.addWidget(self.cb_calcul_exact) #, flag = wx.ALIGN_CENTER_VERTICAL)
        ligne.addWidget(QLabel(u"Valeur approchée."))#, flag = wx.ALIGN_CENTER_VERTICAL)
        ligne.addStretch()

        self.cb_calcul_exact.stateChanged.connect(self.EvtCalculExact)

        # Notation scientifique
        ligne = QHBoxLayout()
        pave.addLayout(ligne)
        self.cb_notation_sci = QCheckBox(self)
        self.cb_notation_sci.setChecked(self.param("ecriture_scientifique"))
        ligne.addWidget(self.cb_notation_sci)#, flag = wx.ALIGN_CENTER_VERTICAL)
        self.st_notation_sci = QLabel(u"Écriture scientifique (arrondie à ")
        ligne.addWidget(self.st_notation_sci)#, flag = wx.ALIGN_CENTER_VERTICAL)
        self.sc_decimales = sd = QSpinBox(self)
        # size = (45, -1)
        sd.setRange(0, 11)
        self.sc_decimales.setValue(self.param("ecriture_scientifique_decimales"))
        ligne.addWidget(self.sc_decimales)#, flag = wx.ALIGN_CENTER_VERTICAL)
        self.st_decimales = QLabel(u" décimales).")
        ligne.addWidget(self.st_decimales)#, flag = wx.ALIGN_CENTER_VERTICAL)
        ligne.addStretch()
        self.EvtCalculExact()

        self.cb_notation_sci.stateChanged.connect(self.EvtNotationScientifique)
        self.sc_decimales.valueChanged.connect(self.EvtNotationScientifique)

        # Copie du résultat dans le presse-papier
        ligne = QHBoxLayout()
        pave.addLayout(ligne)
        self.cb_copie_automatique = QCheckBox(self)
        self.cb_copie_automatique.setChecked(self.param("copie_automatique"))
        ligne.addWidget(self.cb_copie_automatique)#, flag = wx.ALIGN_CENTER_VERTICAL)
        ligne.addWidget(QLabel(u"Copie du résultat dans le presse-papier."))#, flag = wx.ALIGN_CENTER_VERTICAL)
        ligne.addStretch()

        self.cb_copie_automatique.stateChanged.connect(self.EvtCopieAutomatique)

        # En mode LaTeX
        ligne = QHBoxLayout()
        pave.addLayout(ligne)
        self.cb_copie_automatique_LaTeX = QCheckBox(self)
        self.cb_copie_automatique_LaTeX.setChecked(self.param("copie_automatique_LaTeX"))
        ligne.addWidget(self.cb_copie_automatique_LaTeX)
        self.st_copie_automatique_LaTeX = QLabel(u"Copie au format LaTeX (si possible).")
        ligne.addWidget(self.st_copie_automatique_LaTeX)
        ligne.addStretch()

        self.EvtCopieAutomatique()
        self.cb_copie_automatique_LaTeX.stateChanged.connect(self.EvtCopieAutomatiqueLatex)

        # Autres options
        self.options = [(u"Virgule comme séparateur décimal.", u"changer_separateurs"),
##                    (u"Copie du résultat dans le presse-papier.", u"copie_automatique"),
                    (u"Accepter la syntaxe OpenOffice.org", u"formatage_OOo"),
                    (u"Accepter la syntaxe LaTeX", u"formatage_LaTeX"),
                        ]
        self.options_box = []
        for i in range(len(self.options)):
            ligne = QHBoxLayout()
            pave.addLayout(ligne)
            self.options_box.append(QCheckBox(self))
            ligne.addWidget(self.options_box[i])
            self.options_box[i].setChecked(self.param(self.options[i][1]))
            def action(event, chaine = self.options[i][1], entree = self.entree, self = self):
                self.param(chaine, not self.param(chaine))
                entree.setFocus()
            self.options_box[i].stateChanged.connect(action)
            ligne.addWidget(QLabel(self.options[i][0]))
            ligne.addStretch()

        self.setLayout(self.sizer)
#        self.adjustSize()

        #TODO:
#        self.entree.texte.Bind(wx.EVT_RIGHT_DOWN, self.EvtMenu)
#        self.visualisation.Bind(wx.EVT_RIGHT_DOWN, self.EvtMenuVisualisation)

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
        fgeo.contenu["Calculatrice"][0]["Options"] = [{}]
        for i in range(len(self.options)):
            fgeo.contenu["Calculatrice"][0]["Options"][0][self.options[i][1]] = [str(self.options_box[i].isChecked())]



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

            liste = calc["Options"][0].items()
            options = [option for aide, option in self.options]
            for key, value in liste:
                value = eval_safe(value[0])
                self.param(key, value)
                if key in options:
                    self.options_box[options.index(key)].setChecked(value)
            # il faudrait encore sauvegarder les variables, mais la encore, 2 problemes :
            # - pb de securite pour evaluer les variables
            # - pb pour obtenir le code source d'une fonction.
            # Pour remedier a cela, il faut envisager de :
            # - creer un module d'interpretation securisee.
            # - rajouter a chaque fonction un attribut __code__, ou creer une nouvelle classe.


    def modifier_pp_texte(self, chaine):
        u"""Modifier le résultat affiché en LaTeX (pretty print)."""
        if self.param("latex"):
            chaine = "$" + chaine + "$"
        else:
            chaine = chaine.replace("\\mapsto", "\\rightarrow")
            if chaine.startswith(r"$\begin{bmatrix}"):
                chaine = chaine.replace(r"\begin{bmatrix}", r'\left({')
                chaine = chaine.replace(r"\end{bmatrix}", r'}\right)')
                chaine = chaine.replace(r"&", r'\,')
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
                if kw["shift"]:
                    self.interprete.calcul_exact = False
                resultat, latex = self.interprete.evaluer(commande)
                if latex == "$?$": # provoque une erreur (matplotlib 0.99.1.1)
                    latex = u"Désolé, je ne sais pas faire..."
            finally:
                self.interprete.calcul_exact = self.param('calcul_exact')
            aide = resultat.startswith("\n== Aide sur ")
            #LaTeX
            debug("Expression LaTeX: " + latex)
            try:
                self.modifier_pp_texte((latex or resultat) if not aide else '')
            except Exception:
                print_error()
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



    def param(self, parametre, valeur = no_argument, defaut = False):
        if valeur is not no_argument:
            setattr(self.interprete, parametre, valeur)
        return Panel_simple.param(self, parametre = parametre, valeur = valeur, defaut = defaut)

    def EvtCalculExact(self, event = None):
        valeur = self.cb_calcul_exact.isChecked()
        self.param("calcul_exact", not valeur)
        if valeur:
            self.cb_notation_sci.setEnabled(True)
            self.st_notation_sci.setEnabled(True)
            self.sc_decimales.setEnabled(True)
            self.st_decimales.setEnabled(True)
        else:
            self.cb_notation_sci.setEnabled(False)
            self.st_notation_sci.setEnabled(False)
            self.sc_decimales.setEnabled(False)
            self.st_decimales.setEnabled(False)


    def EvtNotationScientifique(self, event = None):
        self.param("ecriture_scientifique", self.cb_notation_sci.isChecked())
        self.param("ecriture_scientifique_decimales", self.sc_decimales.value())

    def EvtCopieAutomatique(self, event = None):
        valeur = self.cb_copie_automatique.isChecked()
        self.param("copie_automatique", valeur)
        if valeur:
            self.cb_copie_automatique_LaTeX.setEnabled(True)
            self.st_copie_automatique_LaTeX.setEnabled(True)
        else:
            self.cb_copie_automatique_LaTeX.setEnabled(False)
            self.st_copie_automatique_LaTeX.setEnabled(False)

    def EvtCopieAutomatiqueLatex(self, event = None):
        self.param("copie_automatique_LaTeX", self.cb_copie_automatique_LaTeX.isChecked())

    def EtatInterne(self, event):
        contenu = self.interprete.save_state()
        h = FenCode(self, u"État interne de l'inteprète", contenu, self.interprete.load_state)
        h.show()
