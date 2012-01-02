# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                  Variable                   #
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

import re, time

from sympy import Symbol, Basic, sympify

from .objet import Ref, Argument, Objet, Objet_numerique, souffler, TYPES_REELS,\
                   contexte
from ..pylib import property2, print_error, fullrange, is_in
from ..mathlib.parsers import VAR_NOT_ATTR, NBR_SIGNE
import param


class Variable_generique(Objet_numerique):
    u"""Une variable g�n�rique.

    Usage interne : la classe m�re pour tous les types de variables."""

    _prefixe_nom = "k"
    _style_defaut = param.variables

    def __init__(self, **styles):
        Objet.__init__(self,  **styles)

    @staticmethod
    def _convertir(objet):
        u"Convertit un objet en variable."
##        if isinstance(objet, Variable):   #  Inutile (?)
##            return objet.copy()
        return Variable(objet)


class Variable(Variable_generique):
    u"""Une variable libre.

    Une variable num�rique ; l'argument peut �tre un nombre, ou une expression sous forme de chaine de caract�res.
    Exemple: Variable(17.5), Variable('AB.longeur+1').
    Dans ce dernier cas, il est n�cessaire qu'une feuille de travail soit d�finie.

    Note : ne pas d�finir directement l'attribut __contenu !"""


    # RE correspondant � un nom de variable (mais pas d'attribut)
    __re = re.compile('(' + VAR_NOT_ATTR + ')')

    def _set_contenu(self, value):
        if isinstance(value, Variable):
            if value.__feuille__ is not None:
                value.__feuille__ = self.__feuille__
            if value._Variable__fonction is None:
                return value.contenu
            return value.val
        elif isinstance(value, basestring):
            value = value.replace(" ","")
            # Si c'est un nombre:
            if not "." in value:
                try:
                    symp = sympify(value)
                    if not symp.atoms(Symbol):
                        value = symp
                except AttributeError:
                    pass
            elif re.match(NBR_SIGNE + "$", value):
                value = eval(value, {})
        elif isinstance(value, Basic):
            if not value.is_real:
                raise RuntimeError, "La variable doit etre reelle."
        return value


    __contenu = Argument(TYPES_REELS + (basestring,), None,  _set_contenu, defaut = 0)

    def __init__(self, contenu = 0, **styles):
        Variable_generique.__init__(self,  **styles)
        self.__liste = []
        self.__fonction = None
        self.__contenu = contenu = Ref(contenu)

    def _test_dependance_circulaire(self, valeur):
        u"""Provoque une erreur si l'objet se retrouve d�pendre de lui-m�me avec la nouvelle valeur.

        Retourne une liste compos�e alternativement d'instructions et d'objets de la feuille,
        et un ensemble constitu� des objets de la feuille mis en jeu dans le code.
        (... � documenter ...)"""
        if isinstance(valeur, basestring) and self.__feuille__ is not None:
            liste = re.split(self.__re, valeur)
            ensemble = set()
            for i in xrange(1, len(liste), 2):
                obj = self.__feuille__.objets[liste[i]]
                if isinstance(obj, Objet):
                    liste[i] = obj
                    ensemble.add(obj)
                    if self is obj or is_in(self, obj._tous_les_ancetres()):
                        print self,
                        raise RuntimeError, "Definition circulaire dans %s : l'objet %s se retrouve dependre de lui-meme." %(self, obj)
            return liste, ensemble
        return None, None


    def _compile(self,  liste, ensemble):
        u"""Compile l'expression stock�e dans la variable ; les arguments sont les valeurs retourn�es par '_test_dependance_circulaire'.

        La compilation doit toujours avoir lieu � la fin de la proc�dure de red�finition de la variable,
        car elle ne doit �tre ex�cut�e que si la red�finition de la variable va effectivement avoir lieu,
        c'est-�-dire si tout le processus pr�c�dent s'est ex�cut� sans erreur."""
        if self._type == "compose" and self.__feuille__ is not None:
##            re.findall(self.__re,  self.valeur)
            self.__liste = liste
            self.__fonction = eval("lambda:" + self.__contenu, self.__feuille__.objets)
            # on supprime la variable de la liste des vassaux pour les objets dont elle ne d�pendra plus desormais:
            for objet in self._ancetres:
                objet.vassaux.remove(self)
            self._ancetres = ensemble
            self._modifier_hierarchie()
            for objet in self._ancetres:   # l'objet est vassal de chacun des objets dont il depend
                objet.vassaux.append(self)
        else:
            for objet in self._ancetres:
                objet.vassaux.remove(self)
            self._ancetres = set()
            self._modifier_hierarchie()
            self.__liste = []
            self.__fonction = None


    @property2
    def contenu(self, value = None):
        if value is None:
            if self.__liste: # variable contenant une expression compil�e
                # On reg�n�re l'expression � partir de l'expression compil�e.
                # C'est important, car certains objets de la feuille peuvent avoir chang� de nom entre temps.
                valeur = ""
                for elt in self.__liste:
                    if isinstance(elt, Objet):
                        valeur += elt.nom
                    else:
                        valeur += elt
                return valeur
            else:
                return self.__contenu
        else:
            args = self._test_dependance_circulaire(value)
            self.__contenu = value
            self._compile(*args)


    def _get_valeur(self):
        # cf. self._conditions_existence
        return self.__val_cache if contexte['exact'] else self.__val_cache_approche



    def _set_valeur(self, valeur):
        self.contenu = valeur


    def _set_feuille(self):
        self._compile(*self._test_dependance_circulaire(self.__contenu))
        self._heritiers_a_recalculer(self._heritiers())

    @property
    def _type(self):
        return isinstance(self.__contenu, basestring) and "compose" or "simple"



    def _recenser_les_ancetres(self):
#        warning("'_recenser_les_ancetres' n'a aucun effet pour une variable.")
        self._modifier_hierarchie()



    def _conditions_existence(self): # conditions specifiques pour que l'objet existe, a definir pour chaque objet
        if self._type == "compose":
            try:
                self.__val_cache = self.__fonction()
                if isinstance(self.__val_cache, Variable):
                    self.__val_cache = self.__val_cache.val
            except Exception:
                if param.verbose:
                    print_error(u"Impossible de d�terminer la valeur de la variable " + self.nom + repr(self))
                return False
        else:
            self.__val_cache = self.contenu
        try:
            self.__val_cache_approche = float(self.__val_cache)
        except TypeError:
            print_error(u"Variable de type incorrect.")
            return False
        return True


    def __str__(self):
        return str(self.contenu)

    def _definition(self):
        if self._type == "compose":
            return repr(self.contenu)
        else:
            return str(self.contenu)



    def _update(self, objet):
        if not isinstance(objet, Variable):
            objet = self._convertir(objet)
        if isinstance(objet, Variable):
            if objet.__feuille__ is not None:
                objet.__feuille__ = self.__feuille__
            if objet._Variable__fonction is None:
                self.contenu = objet.contenu
            else:
                self.val = objet.val
        else:
            raise TypeError, "l'objet n'est pas une variable."



    def varier(self, debut = 0, fin = 1, pas = 0.02, periode = 0.03):
        if self.__feuille__ is not None:
            self.__feuille__.start()
            for i in fullrange(debut, fin, pas):
                t = time.clock()
                self.val = i
                while time.clock() < t + periode:
                    souffler()
                    if self.__feuille__._stop:
                        break
                souffler()
                if self.__feuille__._stop:
                    break


### Addition et multiplication li�es
### ------------------------------------------------

### Est-ce encore bien utile ?

##    def add(self, y):
##        u"Addition li�e (le r�sultat est une variable qui reste toujours �gale � la somme des 2 valeurs)."
##        if self._type == "simple":
##            if isinstance(y, TYPES_NUMERIQUES) or (isinstance(y, Variable) and y._type == "simple"):
##                return Variable(self + y)
##        var = Variable("(%s)+(%s)" %(self, y))
##        var.__feuille__ = self.__feuille__
##        return var

##    def mul(self, y):
##        u"Multiplication li�e (le r�sultat est une variable qui reste toujours �gale au produit des 2 valeurs)."
##        if self._type == "simple":
##           if isinstance(y, TYPES_NUMERIQUES) or (isinstance(y, Variable) and y._type == "simple"):
##                return Variable(self * y)
##        var = Variable("(%s)*(%s)" %(self, y))
##        var.__feuille__ = self.__feuille__
##        return var


class Rayon(Variable_generique):
    u"""Le rayon d'un cercle.

    >>> from wxgeometrie.geolib import Cercle, Rayon
    >>> c = Cercle((0, 0), 1)
    >>> c.rayon
    1
    >>> r = Rayon(c)
    >>> r.val
    1
    >>> c.rayon = 2
    >>> r.val
    2
    """

    __cercle = cercle = Argument("Cercle_Arc_generique")

    def __init__(self, cercle, **styles):
        self.__cercle = cercle = Ref(cercle)
        Variable_generique.__init__(self, **styles)

    def _get_valeur(self):
        return self.__cercle.rayon



class Mul(Variable_generique):
    u"""Le produit de deux variables."""

    __var1 = var1 = Argument(Variable_generique)
    __var2 = var2 = Argument(Variable_generique)

    def __init__(self, var1, var2, **styles):
        self.__var1 = var1 = Ref(var1)
        self.__var2 = var2 = Ref(var2)
        Variable_generique.__init__(self, **styles)

    def _get_valeur(self):
        return self.__var1.val*self.__var2.val


class Add(Variable_generique):
    u"""La somme de deux variables."""

    __var1 = var1 = Argument(Variable_generique)
    __var2 = var2 = Argument(Variable_generique)

    def __init__(self, var1, var2, **styles):
        self.__var1 = var1 = Ref(var1)
        self.__var2 = var2 = Ref(var2)
        Variable_generique.__init__(self, **styles)

    def _get_valeur(self):
        return self.__var1.val + self.__var2.val
