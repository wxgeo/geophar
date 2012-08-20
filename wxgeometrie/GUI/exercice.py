# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

#    .----------------------------------------.
#    |    Exercices : Équations de droites    |
#    '----------------------------------------'
#    Géophar
#    Dynamic geometry, graph plotter, and more for french mathematic teachers.
#    Copyright (C) 2005-2012  Nicolas Pourcelot
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


from random import randint

from PyQt4.QtGui import (QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
                         QColor)

from sympy import S
##from sympy.core.sympify import SympifyError

from .menu import MenuBar
from .panel import Panel_API_graphique
from ..geolib import Champ
##from ..pylib import print_error
##from ..mathlib.parsers import convertir_en_latex, traduire_formule
from .. import param


# TODO:
# - ajouter un bonus substantiel si les résultats sont donnés
#   sous forme de fraction simplifiée.
# - possibilité de définir facilement les niveaux (fichier texte externe ?)
# - gestion des carrés, des nombres seuls



class ExerciceMenuBar(MenuBar):
    def __init__(self, panel):
        MenuBar.__init__(self, panel)

        self.ajouter(u"Fichier", [u"Recommencer", u"Recommencer au niveau 0.", u"Ctrl+N", panel.reinitialiser],
                    [u"ouvrir"],
                    [u"enregistrer"], [u"enregistrer_sous"], [u"exporter"],
                    [u"exporter&sauver"], None, [u"imprimer"], [u"presse-papier"],
                    None, [u"proprietes"], None, ["fermer"], ["quitter"])
        self.ajouter(u"Editer", ["annuler"], ["refaire"])
        self.ajouter(u"Affichage", ["onglet"], ["plein_ecran"], None, ["zoom_texte"], ["zoom_ligne"], ["zoom_general"])
        self.ajouter(u"Outils", [u"options"])
        self.ajouter(u"avance1")
        self.ajouter(u"?")



class Exercice(Panel_API_graphique):

    titre = u"Exercice" # À adapter pour chaque module

    def __init__(self, *args, **kw):
        Panel_API_graphique.__init__(self, *args, **kw)

        self.entrees = QVBoxLayout()
        self.entrees.addSpacing(30)

        self.panneau = QLabel('')
        self.entrees.addWidget(self.panneau)

        self.entrees.addStretch()
        self.felicitations = QLabel('')
        self.entrees.addWidget(self.felicitations)

        self.entrees.addSpacing(30)
        self.btn_niveau = QPushButton(u"Niveau suivant", self)
        self.btn_niveau.clicked.connect(self.niveau_suivant)
        self.entrees.addWidget(self.btn_niveau)
        self.entrees.addSpacing(50)

        self.sizer = QHBoxLayout()
        self.sizer.addWidget(self.canvas, 1)
        self.sizer.addLayout(self.entrees, 0.2)
        self.finaliser(contenu=self.sizer)

        self.reinitialiser()


    def reinitialiser(self):
        u"""Revient au 1er niveau, et remet tous les réglages par défaut.

        Chaque niveau peut bien sûr modifier ces réglages.

        Quelques remarques:
        * le clic droit est désactivé, car il permet d'obtenir la réponse
          en éditant les propriétés du champ de texte.
        * l'édition des champs/textes avec [Entrée] est désactivée
          (car cela s'est avéré perturber les élèves).
        """
        # Ne pas éditer les champs/textes avec [Entrée]
        self.canvas.editeur.active = False
        # Ne pas éditer les objets par un clic droit
        self.canvas.edition_par_clic_droit = False

        # Réglages par défaut
        self.canvas.fixe = True
        self.canvas.afficher_axes = False
        self.canvas.afficher_quadrillage = False
        self.afficher_barre_outils(False)
        self.canvas.ratio = None

        # Réinitialisation du score et retour au niveau 1
        if param.debug:
            print(u'Module %s: réinitialisation...' % self.nom)
        self.score = 0
        self.niveau = 0
        self.erreurs = 0
        self.niveau_suivant()



    def niveau_suivant(self, niveau=None):
        # On ferme toutes les feuilles ouvertes (inutile en principe),
        # et on en ouvre une nouvelle.
        self.fermer_feuilles()
        # Et on change de niveau...
        if niveau in (None, False):
            # None ou False (False est renvoyé par Qt via QAbstractBouton.clicked)
            self.niveau += 1
        else:
            self.niveau = niveau
        if param.debug:
            print("== Niveau %s ==" % self.niveau)
        getattr(self, 'niveau%s' % self.niveau)()

        self.btn_niveau.setEnabled(False)
        self.felicitations.setStyleSheet(
            """QLabel {background-color: white; padding: 5px; border-radius: 5px;
            color:white;}""")
        self.update_panneau()

    n = niveau_suivant


    def update_panneau(self):
        self.panneau.setStyleSheet(
            """QLabel { padding: 10px; border-width: 2px; border-style:solid;
            border-radius: 5px; border-color:%s; background-color: %s }"""
            %(QColor(30, 144, 255).name(), QColor(176, 226, 255).name())
                        )
        self.panneau.setText((u"<p><b><i>Niveau :</i> %s</b></p>" % self.niveau) +
                                 (u"<p><b><i>Points :</i> %s</b></p>" % self.score) +
                                 (u"<p><i>Erreurs :</i> %s</p>" % self.erreurs))
        champs = self.feuille_actuelle.objets.lister(type=Champ)
        if champs and all(obj.correct for obj in champs):
            if hasattr(self, 'niveau' + str(self.niveau + 1)):
                self.btn_niveau.setEnabled(True)
                self.btn_niveau.setFocus(True)
                self.felicitations.setText(u'<p><b>Félicitations !</b></p>' +
                                           u'<p>Passer au niveau %s</p>' %(self.niveau + 1))
                self.felicitations.setStyleSheet(
                    """QLabel {background-color: %s; padding: 5px;
                       border-radius: 5px;
                       color:white;}""" %QColor(255, 153, 0).name())

            else:
                self.felicitations.setText(u'<p><b>Félicitations !</b></p>' +
                                           u'<p>Dernier niveau terminé !</p>')
                self.felicitations.setStyleSheet(
                    """QLabel {background-color: %s; padding: 5px; border-radius: 5px;
                    color:white;}""" %QColor(102, 205, 0).name())

    ##def _sauvegarder(self, fgeo, feuille = None):
        ##Panel_API_graphique._sauvegarder(self, fgeo, feuille)
        ##fgeo.contenu[u"niveau"] = [str(self.niveau)]
        ##fgeo.contenu[u"expression"] = [self.raw_expression]
        ##fgeo.contenu[u"score"] = [str(self.score)]
        ##fgeo.contenu[u"erreurs"] = [str(self.erreurs)]
##
    def _ouvrir(self, fgeo):
        pass
        ### Il ne doit y avoir qu'une seule feuille ouverte à la fois.
        ### XXX: intégrer cette fonctionnalité directement au Panel.
        ##self.fermer_feuilles()
        ##Panel_API_graphique._ouvrir(self, fgeo)
        ##if fgeo.contenu.has_key(u"expression"):
            ##self.generer_expression(expr=fgeo.contenu[u"expression"][0])
            ##self.dessiner_tableau()
        ##if fgeo.contenu.has_key(u"niveau"):
            ##self.niveau = int(fgeo.contenu[u"niveau"][0])
        ##if fgeo.contenu.has_key(u"score"):
            ##self.score = int(fgeo.contenu[u"score"][0])
        ##if fgeo.contenu.has_key(u"erreurs"):
            ##self.erreurs = int(fgeo.contenu[u"erreurs"][0])
        ##self.update_panneau()

    ##def _affiche(self):
        ##self.dessiner_tableau()


    # --------------------------------
    # Génération de nombres aléatoires
    # --------------------------------

    @staticmethod
    def signe():
        return 2*randint(0, 1) - 1

    def naturel(self, n=15):
        u'''Retourne un entier entre 2 et `n`.'''
        return randint(2, n)

    def relatif(self, n=15):
        u'''Retourne un entier entre -`n` et -2, ou entre 2 et `n`.'''
        # signe: 1 ou -1
        return self.signe()*self.naturel(n)

    def decimal(self, chiffres=2):
        u'''Retourne un nombre décimal, `chiffres` est le nombre de chiffres.'''
        return  S('%s.%s' % (self.relatif(), self.naturel()))

    def rationnel(self, n=7):
        u'''Retourne un quotient d'entiers.'''
        while True:
            p = self.naturel(n)
            q = self.naturel(n)
            if p%q:
                break
        return self.signe()*S(p)/S(q)

    def couple(self, m=7, n=7):
        u"""Retourne un couple d'entiers relatifs."""
        return self.relatif(m), self.relatif(n)

    def autocompleter(self):
        u"""Compléter automatiquement avec les bonnes réponses
        pour pouvoir passer au niveau suivant.
        Essentiellement pour déboguer."""
        ##if self.btn_niveau.isEnabled():
            ##self.niveau_suivant()
        self.btn_niveau.click()
        for t in self.feuille_actuelle.objets.lister(type=Champ):
            t.texte = t.style('attendu')
            t.style(color='g')
        ##self.parent.parent.ligne_commande.setFocus()

    a = property(autocompleter)

    def bonus(self, expr):
        u"""À surclasser pour accorder un bonus si l'expression vérifie
        certaines conditions.
        Par exemple, on peut tester que le résultat est bien simplifié."""
        return False

    def compter_points(self, **kw):
        if 'correct' in kw and 'correct_old' in kw and 'champ' in kw:
            champ = kw['champ']
            if kw['correct']:
                if not kw['correct_old']:
                    if not champ.style('choix'):
                        # C'est plus dur s'il n'y a pas de choix proposé.
                        # On accorde une bonification si le résultat est
                        # un minimum simplifié.
                        if self.bonus(champ.label()):
                            self.score += 3
                        self.score += 1
                    self.score += 1
            else:
                self.score -= 1
                self.erreurs += 1
        if all(obj.correct for obj in self.feuille_actuelle.objets.lister(type=Champ)):
            self.score += 10*(self.niveau + 1)
        self.update_panneau()
