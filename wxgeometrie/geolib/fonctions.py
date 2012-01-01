# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                   Fonctions                    #
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

# version unicode

import re
from .objet import Objet_numerique, Objet, contexte, ArgumentNonModifiable, \
                   Argument, Ref

#from .. import param
from ..pylib import is_in, property2
from ..mathlib.intervalles import preformatage_geolib_ensemble, formatage_ensemble
from ..mathlib.parsers import VAR_NOT_ATTR, traduire_formule
from .variables import Variable

class Fonction(Objet_numerique):
    u"""Une fontion.

    Une fonction numérique à une variable; l'argument est une expression sous forme de chaine de caractères.
    Exemple: Fonction('2*x+1', variable = 'x', ensemble = 'R')."""

    _prefixe_nom = "f"

    # nom de variable (mais pas d'attribut)
    __re = re.compile('(' + VAR_NOT_ATTR + ')')


    __expression = Argument("basestring")
    __ensemble = Argument("basestring")
    variable = __variable = ArgumentNonModifiable("basestring")

    @property2
    def expression(self, expression = None):
        if expression is None:
            if self.__liste_expression:
                # On regénère l'expression à partir de l'expression compilée.
                # C'est important, car certains objets de la feuille peuvent avoir changé de nom entre temps.
                expr = ""
                for elt in self.__liste_expression:
                    if isinstance(elt, Objet):
                        expr += elt.nom
                    else:
                        expr += elt
                return expr
            else:
                return self.__expression
        else:
            self.modifier_expression_et_ensemble(expression = expression)


    @property2
    def ensemble(self, ensemble = None):
        if ensemble is None:
            if self.__liste_ensemble:
                # On regénère l'ensemble à partir de l'ensemble compilée.
                # C'est important, car certains objets de la feuille peuvent avoir changé de nom entre temps.
                ens = ""
                for elt in self.__liste_ensemble:
                    if isinstance(elt, Objet):
                        ens += elt.nom
                    else:
                        ens += elt
                return ens
            else:
                return self.__ensemble
        else:
            self.modifier_expression_et_ensemble(ensemble = ensemble)


    def modifier_expression_et_ensemble(self, expression = None, ensemble = None):
        u"""Si l'on modifie à la fois l'expression et l'ensemble,
        il est beaucoup plus rapide d'utiliser cette méthode."""
#        print "modification!"
        if expression is None:
            expression = self.__expression
        if ensemble is None:
            ensemble = self.__ensemble
        else:
            ensemble, extremites_cachees = preformatage_geolib_ensemble(ensemble)
            extremites_cachees = tuple([Variable(x) for x in partie] for partie in extremites_cachees)
            self.style(extremites_cachees = extremites_cachees)
        if ensemble == self.__ensemble and expression == self.__expression:
            # Aucune modification
            return
        args = self._test_dependance_circulaire(expression, ensemble)
        self.__expression = expression
        self.__ensemble = ensemble
        self._compile(*args)


    def __init__(self, expression, ensemble = "R", variable = "x", **styles):
        Objet.__init__(self,  **styles)
        if variable not in 'xt':
            raise NotImplementedError
        # *Pré*formatage
        ensemble, extremites_cachees = preformatage_geolib_ensemble(ensemble)
        if self.style("extremites_cachees"):
            extremites_cachees = self.style("extremites_cachees")
        else:
            extremites_cachees = tuple([Variable(x) for x in partie] for partie in extremites_cachees)
        self.__liste_expression = []
        self.__liste_ensemble = []
        # Une fonction peut être définie par morceaux
        # Liste des fonctions correspondant à chaque morceau
        self.__fonctions = None
        # Liste des (unions d'intervalles correspondant à chaque morceau
        self.__unions = None
        # Les arguments non modifiables ne sont pas encapsulés dans des références (classe Ref)
        self.__expression = expression = Ref(expression)
        self.__ensemble = ensemble = Ref(ensemble)
        self.__variable = variable
        self.style(extremites_cachees = extremites_cachees)


    def _test_dependance_circulaire(self, expression, ensemble, deuxieme_essai = False):
        u"""Provoque une erreur si l'objet se retrouve dépendre de lui-même avec la nouvelle valeur.

        Retourne deux listes (list) composées alternativement d'instructions et d'objets de la feuille,
        et un ensemble (set) constitué des objets de la feuille mis en jeu dans le code.
        (... à documenter ...)"""
        if self.__feuille__ is not None:
            try:
                with contexte(afficher_messages = False):
                    liste_expression = re.split(self.__re, expression)
                    liste_ensemble = re.split(self.__re, ensemble)
                    objets = set()
                    for i in xrange(1, len(liste_expression), 2):
                        obj = self.__feuille__.objets[liste_expression[i]]
                        if isinstance(obj, Objet):
                            liste_expression[i] = obj
                            objets.add(obj)
                            if self is obj or is_in(self, obj._tous_les_ancetres()):
                                print self,
                                raise RuntimeError, "Definition circulaire dans %s : l'objet %s se retrouve dependre de lui-meme." %(self, obj)
                    for i in xrange(1, len(liste_ensemble), 2):
                        obj = self.__feuille__.objets[liste_ensemble[i]]
                        if isinstance(obj, Objet):
                            liste_ensemble[i] = obj
                            objets.add(obj)
                            if self is obj or is_in(self, obj._tous_les_ancetres()):
                                print self,
                                raise RuntimeError, "Definition circulaire dans %s : l'objet %s se retrouve dependre de lui-meme." %(self, obj)
                    return liste_expression, liste_ensemble, objets
            except KeyError:
                if deuxieme_essai:
                    raise
                # L'erreur peut-être due à la présence de code LaTeX dans la fonction ;
                # on tente un 2e essai après traduction du code LaTeX éventuel.
                expression = traduire_formule(expression, fonctions = self.__feuille__.objets)
                return self._test_dependance_circulaire(expression, ensemble, deuxieme_essai = True)
        return None, None, None


    def _compile(self,  liste_expression, liste_ensemble, objets):
        u"""Compile l'expression stockée dans la variable ; les arguments sont les valeurs retournées par '_test_dependance_circulaire'.

        La compilation doit toujours avoir lieu à la fin de la procédure de redéfinition de la variable,
        car elle ne doit être exécutée que si la redéfinition de la variable va effectivement avoir lieu,
        c'est-à-dire si tout le processus précédent s'est exécuté sans erreur."""
        #print "compilation !"
        if self.__feuille__ is not None:
            self.__liste_expression = liste_expression
            self.__liste_ensemble = liste_ensemble
            self.__fonctions = []
            self.__unions = []
            expressions = self.__expression.split("|")
            ensembles = self.__ensemble.split("|")
            # TODO: Prévoir le cas où les deux listes ne sont pas de même longueur
            n = min(len(expressions), len(ensembles))
            for i in xrange(n):
                express = traduire_formule(expressions[i], fonctions = self.__feuille__.objets)
                # On force ensuite la variable à apparaitre dans l'expression de la formule.
                # C'est important quand la fonction est constante :
                # l'image d'un tableau par la fonction doit être un tableau, et non la constante.
                if self.__variable not in express:
                    express += "+0.*" + self.__variable
                self.__fonctions.append(eval("lambda " + self.__variable + ":" + express, self.__feuille__.objets))
                ensemb = formatage_ensemble(ensembles[i], preformatage = False)
                self.__unions.append(eval(ensemb, self.__feuille__.objets))

            # on supprime la variable de la liste des vassaux pour les objets dont elle ne dépendra plus desormais:
            for objet in self._ancetres:
                objet.vassaux.remove(self)
            self._ancetres = objets
            self._modifier_hierarchie()
            for objet in self._ancetres:   # l'objet est vassal de chacun des objets dont il depend
                objet.vassaux.append(self)
        else:
            for objet in self._ancetres:
                objet.vassaux.remove(self)
            self._ancetres = set()
            self._modifier_hierarchie()
            self.__liste_expression = []
            self.__liste_ensemble = []
            self.__fonctions = None
            self.__unions = None


    def _set_feuille(self):
        self._compile(*self._test_dependance_circulaire(self.__expression, self.__ensemble))
        self._heritiers_a_recalculer(self._heritiers())




    def _recenser_les_ancetres(self):
#        warning("'_recenser_les_ancetres' n'a aucun effet pour une variable.")
        self._modifier_hierarchie()






##    def affiche(self, actualiser = False):
##        if actualiser and self.__feuille__ is not None:
##            canvas = self.__canvas__
##            if canvas:
##                canvas.actualiser()


    @staticmethod
    def _convertir(objet):
        u"Convertit un objet en fonction."
        return Fonction(objet)


    def __call__(self, valeur):
        for i in xrange(len(self.__unions)):
            if valeur in self.__unions[i]:
                return self.__fonctions[i](valeur)
        raise ValueError, "math domain error"



    def _update(self, objet):
        if not isinstance(objet, Fonction):
            objet = self._convertir(objet)
        if isinstance(objet, Fonction):
            if objet.__feuille__ is not None: # ??
                objet.__feuille__ = self.__feuille__
            self.modifier_expression_et_ensemble(objet.expression, objet.ensemble)
        else:
            raise TypeError, "l'objet n'est pas une fonction."
