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

from sympy import Symbol, Integer, Matrix

from sympy.printing.latex import LatexPrinter
from sympy.printing.str import StrPrinter
from sympy.printing.precedence import precedence

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


class CustomStrPrinter(StrPrinter):
    def _print_str(self, expr):
        return '"%s"' %expr.replace('"', r'\"')

    def _print_unicode(self, expr):
        return '"%s"' %expr.replace('"', r'\"')

    def _print_Exp1(self, expr):
        return 'e'

    def _print_Abs(self, expr):
        return 'abs(%s)'%self._print(expr.args[0])

    def _print_ImaginaryUnit(self, expr):
        return 'i'

    def _print_Infinity(self, expr):
        return '+oo'

    def _print_log(self, expr):
        return "ln(%s)"%self.stringify(expr.args, ", ")

    def _print_Pow(self, expr):
        PREC = precedence(expr)
        if expr.exp.is_Rational and expr.exp.p == 1 and expr.exp.q == 2:
            return 'sqrt(%s)' % self._print(expr.base)
        if expr.exp.is_Rational and expr.exp.is_negative:
            return '1/%s'%self._print(expr.base**abs(expr.exp))
        else:
            return '%s^%s'%(self.parenthesize(expr.base, PREC),
                             self.parenthesize(expr.exp, PREC))

    def _print_Float(self, expr):
        string = StrPrinter._print_Float(self, expr)
        return string.replace('e+', '*10^').replace('e-', '*10^-')

    def doprint(self, expr):
        return StrPrinter.doprint(self, expr) if not isinstance(expr, unicode) else expr



class CustomLatexPrinter(LatexPrinter):
    def __init__(self, profile = None):
        _profile = {
            "mat_str" : "pmatrix",
            "mat_delim" : "",
            "mode": "inline",
        }
        if profile is not None:
            _profile.update(profile)
        LatexPrinter.__init__(self, _profile)

    def _print_Temps(self, expr):
        return r"%s \mathrm{j}\, %s \mathrm{h}\, %s \mathrm{min}\, %s \mathrm{s}" %expr.jhms()

    def _print_exp(self, expr, exp=None):
        tex = r"\mathrm{e}^{%s}" % self._print(expr.args[0])
        return self._do_exponent(tex, exp)

    def _print_Exp1(self, expr):
        return r"\mathrm{e}"

    def _print_Abs(self, expr):
        return r'\left|{%s}\right|'%self._print(expr.args[0])

    def _print_ImaginaryUnit(self, expr):
        return r"\mathrm{i}"

    def _print_Fonction(self, expr):
        return ", ".join(expr._variables()) + "\\mapsto " + self._print(expr.expression)

    def _print_Function(self, expr, exp=None):
        func = expr.func.__name__

        if hasattr(self, '_print_' + func):
            return getattr(self, '_print_' + func)(expr, exp)

        else:
            if exp is not None:
                name = r"\mathrm{%s}^{%s}" % (func, exp)
            else:
                name = r"\mathrm{%s}" % func
            if len(expr.args) == 1 and isinstance(expr.args[0], (Symbol, Integer)):
                return name + "(" + str(self._print(expr.args[0])) +")"
            else:
                args = [ str(self._print(arg)) for arg in expr.args ]
                return name + r"\left(%s\right)" % ",".join(args)

    def _print_ProduitEntiers(self, expr):
        def formater(exposant):
            if exposant == 1:
                return ""
            return "^" + str(exposant)
        return "\\times ".join((str(entier) + formater(exposant)) for entier, exposant in expr.couples)

    def _print_Float(self, expr):
        s = str(expr)
        if "e" in s:
            nombre,  exposant = s.split("e")
            return nombre + "\\times 10^{" + exposant.lstrip("+") + "}"
        else:
            return s

    def _print_Infinity(self, expr):
        return r"+\infty"

    def _print_Order(self, expr):
        return r"\mathcal{O}\left(%s\right)" % \
            self._print(expr.args[0])

    def _print_abs(self, expr, exp=None):
        tex = r"\left|{%s}\right|" % self._print(expr.args[0])

        if exp is not None:
            return r"%s^{%s}" % (tex, exp)
        else:
            return tex

    def _print_Union(self, expr):
        tex = r"\cup".join(self._print(intervalle) for intervalle in expr.intervalles)
        tex = tex.replace(r"\}\cup\{", "\,;\, ")
        return tex

    def _print_Intervalle(self, expr):
        if expr.vide:
            return r"\varnothing"
        elif expr.inf_inclus and expr.sup_inclus and expr.inf == expr.sup:
            return r"\{%s\}" % self._print(expr.inf)
        if expr.inf_inclus:
            left = "["
        else:
            left = "]"
        if expr.sup_inclus:
            right = "]"
        else:
            right = "["
        return r"%s%s;%s%s" % (left, self._print(expr.inf), self._print(expr.sup), right)

    def _print_Singleton(self, expr):
        return r"\{%s\}" % self._print(expr.inf)

    def _print_tuple(self, expr):
        return "(" + ",\,".join(self._print(item) for item in expr) + ")"

    def _print_log(self, expr, exp=None):
        if len(expr.args) == 1 and isinstance(expr.args[0], (Symbol, Integer)):
            tex = r"\ln(%s)" % self._print(expr.args[0])
        else:
            tex = r"\ln\left(%s\right)" % self._print(expr.args[0])
        return self._do_exponent(tex, exp)

    def _print_function(self, expr):
        return r"\mathrm{Fonction}\, " + expr.func_name


    def doprint(self, expr):
        tex = LatexPrinter.doprint(self, expr)
        return tex.replace(r'\operatorname{', r'\mathrm{')
