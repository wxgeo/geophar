#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#   Mathlib 2 (sympy powered) #
##--------------------------------------#######
#WxGeometrie
#Dynamic geometry, graph plotter, and more for french mathematic teachers.
#Copyright (C) 2005-2010  Nicolas Pourcelot
#
#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

## Objets complémentaires à ceux de sympy

from sympy import Symbol, Rational, Expr, Integer, Basic
from sympy.core.cache import cacheit
from sympy.core.numbers import Infinity

from .internal_objects import ObjetMathematique
from ..pylib import GenericWrapper



def convert2decim(expr, prec=None):
    if not isinstance(expr, Basic):
        return expr
    dico = {}
    for a in expr.atoms():
        if a.is_Rational:
            dico[a] = Decim(a, prec=prec)
    return expr.subs(dico)



class Decim(Rational):
    """
    Fonctionne comme un rationnel sympy, mais s'affiche comme un décimal.

    Ceci permet, dans la calculatrice, de faire des calculs avec des décimaux,
    tout en ayant en interne des résultats exacts, et donc d'éviter les cumuls
    d'erreurs d'arrondis.
    """

    __slots__ = ['p', 'q', 'prec']

    @cacheit
    def __new__(cls, p, q=None, prec=15):
        rat = Rational.__new__(cls, p, q)
        if isinstance(rat, (Integer, Infinity)):
            return rat
        obj = Expr.__new__(cls)
        obj.p = rat.p
        obj.q = rat.q
        obj.prec = prec
        return obj

    def to_Rational(self):
        return Rational(self.p, self.q)

    def __neg__(self):
        return Decim(-self.p, self.q, prec=self.prec)

    def __abs__(self):
        return Decim(abs(self.p), self.q, prec=self.prec)

# On modifie les méthodes __add__, __sub__, etc. de Rational()
# pour renvoyer un objet Decim() si l'un des objets de l'opération
# est de type Decim.

def _compatible(meth):
    u"Modifie la méthode `meth` pour qu'elle prenne en compte le type Decim()."
    # La méthode doit avoir exactement 2 arguments.
    # Exemple type : .__add__(self, other).
    assert meth.func_code.co_argcount == 2
    def new_meth(self, other):
        result = meth(self, other)
        prec = None
        if isinstance(self, Decim):
            prec = self.prec
        if isinstance(other, Decim):
            prec = max(prec, other.prec)
        if prec is not None:
            if isinstance(result, Rational):
                result = Decim(result, prec=prec)
            else:
                result = convert2decim(result, prec=prec)
        return result
    return new_meth

for _name in ('__add__', '__radd__', '__sub__', '__mul__', '__div__',
                     '__rdiv__', '__pow__', '__rpow__', '__mod__', '__rmod__',
                     '_eval_power', '__truediv__'):
    setattr(Rational, _name, _compatible(getattr(Rational, _name)))

del _name, _compatible


class Fonction(ObjetMathematique):
    u"""Une fonction de une ou plusieurs variables."""
    def __init__(self, variables, expression):
        if not isinstance(variables, (list, tuple)):
            variables = (variables,)
        self.variables = variables
        self.expression = expression

    @classmethod
    def _substituer(cls, expression, dico):
        if hasattr(expression, "__iter__"):
            return expression.__class__(cls._substituer(elt, dico) for elt in expression)
        return expression.subs(dico)

    def __call__(self, *args, **kw):
        if kw:
            if args:
                raise TypeError, "les arguments sont entres de deux facons differentes."
            return self._substituer(self.expression, [(Symbol(key), value) for key, value in kw.iteritems()])
        if len(args) > len(self.variables):
            raise TypeError, "il y a plus d'arguments que de variables."
        return self._substituer(self.expression, zip(self.variables[:len(args)], args))

    def _variables(self):
        return tuple(str(arg) for arg in self.variables)

    def __str__(self):
        return ", ".join(self._variables()) + " -> " + str(self.expression)

    def __repr__(self):
        return "Fonction(%s, %s)" %(repr(self.variables), repr(self.expression))

    for op in ("add", "mul", "div", "rdiv", "pow", "rpow"):
        op = "__" + op + "__"
        def __op__(self, y, op = op):
            if isinstance(y, Fonction):
                if self.variables == y.variables or not y.variables:
                    return Fonction(self.variables, getattr(self.expression, op)(y.expression),)
                elif not self.variables:
                    return Fonction(y.variables, getattr(self.expression, op)(y.expression),)
                else:
                    raise ValueError, "les deux fonctions n'ont pas les memes variables."
            else:
                return Fonction(self.variables, getattr(self.expression, op)(y),)
        exec("%s=__op__" %op)
    del __op__, op

    def __ne__(self):
        return Fonction(self.variables, -self.expression)

    def __abs__(self):
        return Fonction(self.variables, abs(self.expression))

    def __eq__(self, y):
        if isinstance(y, Fonction):
            return self.expression == y.expression
        else:
            return self.expression == y

    def __gt__(self, y):
        if isinstance(y, Fonction):
            return self.expression > y.expression
        else:
            return self.expression > y


class ProduitEntiers(long):
    u"""Usage interne : destiné à être utilisé avec sympy.factorint."""

    def __new__(cls, *couples):
        val = 1
        for (m, p) in couples:
            val *= m**p
        self = long.__new__(cls, val)
        self.couples = couples
        return self

#    __slots__ = ["couples"]

    def __str__(self):
        def formater(exposant):
            if exposant == 1:
                return ""
            return "**" + str(exposant)
        return "*".join((str(entier) + formater(exposant)) for entier, exposant in self.couples)

    def __repr__(self):
        return "ProduitEntiers(*%s)" %repr(self.couples)




#TODO: créer une classe Wrapper, dont MesureDegres doit hériter,
# Note: this must wrap all special methods
# http://docs.python.org/reference/datamodel.html#more-attribute-access-for-new-style-classes
class MesureDegres(GenericWrapper):
    u"""Usage interne : destiné à être utilisé avec deg."""

    __slots__ = ('__val',)

    def __str__(self):
        return str(self.__val) + '°'

    def __repr__(self):
        return repr(self.__val) + '°'

    def __unicode__(self):
        return unicode(self.__val) + u'°'





class Temps(object):
    def __init__(self, secondes = 0, **kw):
        self.secondes = secondes + kw.get("s", 0) \
                                 + 60*kw.get("m", 0) + 60*kw.get("min", 0) \
                                 + 3600*kw.get("h", 0) \
                                 + 86400*kw.get("j", 0) + 86400*kw.get("d", 0)

    def jhms(self):
        s = float(self.secondes)
        s, dec = int(s), s-int(s)
        j, s = s//86400, s%86400
        h, s = s//3600, s%3600
        m, s = s//60, s%60
        if dec:
            s += dec
        return j, h, m, s

    def __str__(self):
        return  "%s j %s h %s min %s s" % self.jhms()

    def __repr__(self):
        return "Temps(%s)" %self.secondes

