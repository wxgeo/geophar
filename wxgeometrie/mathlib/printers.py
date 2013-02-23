#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#           Mathlib 2 (sympy powered)         #
##--------------------------------------#######
#WxGeometrie
#Dynamic geometry, graph plotter, and more for french mathematic teachers.
#Copyright (C) 2005-2013  Nicolas Pourcelot
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

## Surclasse les printers de sympy

from sympy import Symbol, Integer, Float, Basic
from sympy.printing.latex import LatexPrinter
from sympy.printing.str import StrPrinter, precedence
from sympy.core import S, Rational, Pow, Mul
from sympy.core.mul import _keep_coeff

from .custom_objects import Decim


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

    def _print_Pow(self, *args, **kw):
        return StrPrinter._print_Pow(self, *args, **kw).replace('**', '^')

    def _print_Float(self, expr):
        string = StrPrinter._print_Float(self, expr)
        return string.replace('e+', '*10^').replace('e-', '*10^-')

    def _print_Union(self, expr):
        return expr.__str__()

    def _print_Fonction(self, expr):
        return "%s -> %s" % (", ".join(expr._variables()),
                        self._print(self._convert_Decim(expr.expression)))

    def _convert_Decim(self, expr):
        conv = self._convert_Decim
        if hasattr(expr, 'atoms') and hasattr(expr, 'subs'):
            dico = {}
            for a in expr.atoms():
                if a.is_Rational and isinstance(a, Decim):
                    dico[a] = Float(a, prec=a.prec)
            expr = expr.subs(dico)
        elif isinstance(expr, (list, tuple)):
            return expr.__class__(conv(item) for item in expr)
        elif isinstance(expr, dict):
            return dict((conv(key), conv(val)) for key, val in expr.iteritems())
        return expr

    def doprint(self, expr):
        # Mieux vaut faire la substitution une seule fois dès le départ.
        expr = self._convert_Decim(expr)
        return StrPrinter.doprint(self, expr) if not isinstance(expr, unicode) else expr

def custom_str(expr, **settings):
    return CustomStrPrinter(settings).doprint(expr)

# Modifie Basic.__repr__ pour utiliser `custom_str` au lieu de `sstr` (printer de sympy)
# Can't use partial() for this (cf. http://bugs.python.org/issue4331)

Basic.__repr__ = (lambda self: custom_str(self, order=None))

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

    def _print_Abs(self, *args, **kw):
        res = LatexPrinter._print_Abs(self, *args, **kw)
        return res.replace(r'\lvert', r'\left|').replace(r'\rvert', r'\right|')

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
        s = LatexPrinter._print_Float(self, expr)
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

    def _print_Union(self, expr):
        tex = r"\cup".join(self._print(intervalle) for intervalle in expr.intervalles)
        tex = tex.replace(r"\right\}\cup\left\{", "\,;\, ")
        return tex

    def _print_Intervalle(self, expr):
        if expr.vide:
            return r"\varnothing"
        elif expr.inf_inclus and expr.sup_inclus and expr.inf == expr.sup:
            return r"\left\{%s\right\}" % self._print(expr.inf)
        if expr.inf_inclus:
            left = r"\left["
        else:
            left = r"\left]"
        if expr.sup_inclus:
            right = r"\right]"
        else:
            right = r"\right["
        return r"%s%s;%s%s" % (left, self._print(expr.inf), self._print(expr.sup), right)

    def _print_tuple(self, expr):
        return r"\left(" + ",\,".join(self._print(item) for item in expr) + r"\right)"

    def _print_log(self, expr, exp=None):
        if len(expr.args) == 1 and isinstance(expr.args[0], (Symbol, Integer)):
            tex = r"\ln(%s)" % self._print(expr.args[0])
        else:
            tex = r"\ln\left(%s\right)" % self._print(expr.args[0])
        return self._do_exponent(tex, exp)

    def _print_function(self, expr):
        return r"\mathrm{Fonction}\, " + expr.func_name

    def _print_Decim(self, expr):
        return self._print_Float(Float(expr, prec=expr.prec))

    def doprint(self, expr):
        tex = LatexPrinter.doprint(self, expr)
        return tex.replace(r'\operatorname{', r'\mathrm{')


def custom_latex(expr, profile = None):
    return CustomLatexPrinter(profile).doprint(expr)
