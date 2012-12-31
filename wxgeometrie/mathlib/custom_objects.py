#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
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

from sympy import Symbol, Matrix

from .internal_objects import ObjetMathematique
from ..pylib import GenericWrapper


class Fonction(ObjetMathematique):
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
    del __op__

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


class Matrice(Matrix):
    def __repr__(self):
        return "Matrice(%s)" %repr(self.mat)


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
        return j, h, m, s + dec

    def __str__(self):
        return  "%s j %s h %s min %s s" %self.jhms()

    def __repr__(self):
        return "Temps(%s)" %self.secondes

