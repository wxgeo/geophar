#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

from math import floor, log

from sympy import Symbol, Integer, Float, Basic, FunctionClass, I, Mul
from sympy.core.core import BasicMeta
from sympy.printing.latex import LatexPrinter
from sympy.printing.str import StrPrinter
from sympy.core import S

from .custom_objects import Decim


class MyCustomPrinter(object):
    u"""Personnalisation du printer de sympy.

    * implémentation de méthodes génériques pour gérer les objets Decim.
    * changement de l'ordre de recherche des méthodes d'impression :
      on cherche d'abord l'existence d'une méthode _print_ClasseObjet,
      avant de regarder si l'objet a une méthode ._latex() ou ._str().

      Ceci facilite la personnalisation de l'impression : il est plus
      propre de rajouter une méthode au printer que de modifier les
      méthodes d'impressions de nombreux objets par surclassage ou
      par "Monkey Patching" !
    """

    def _print(self, expr, *args, **kwargs):
        """Internal dispatcher

        Tries the following concepts to print an expression:
            1. Take the best fitting method defined in the printer.
            2. Let the object print itself if it knows how.
            3. As fall-back use the emptyPrinter method for the printer.
        """
        self._print_level += 1
        try:
            # See if the class of expr is known, or if one of its super
            # classes is known, and use that print function
            for cls in type(expr).__mro__:
                printmethod = '_print_' + cls.__name__
                if hasattr(self, printmethod):
                    return getattr(self, printmethod)(expr, *args, **kwargs)

            # If the printer defines a name for a printing method
            # (Printer.printmethod) and the object knows for itself how it
            # should be printed, use that method.
            if (self.printmethod and hasattr(expr, self.printmethod)
                    and not isinstance(expr, BasicMeta)):
                return getattr(expr, self.printmethod)(self, *args, **kwargs)

            # Unknown object, fall back to the emptyPrinter.
            return self.emptyPrinter(expr)
        finally:
            self._print_level -= 1

    def _convert_Decim(self, expr):
        conv = self._convert_Decim
        if isinstance(expr, FunctionClass):
            return expr
        elif hasattr(expr, 'atoms') and hasattr(expr, 'subs'):
            dico = {}
            for a in expr.atoms():
                if a.is_Rational and isinstance(a, Decim):
                    dico[a] = Float(a, prec=60)
            expr = expr.subs(dico).subs(Float(1), S.One)
        elif isinstance(expr, (list, tuple)):
            return expr.__class__(conv(item) for item in expr)
        elif isinstance(expr, dict):
            return dict((conv(key), conv(val)) for key, val in expr.iteritems())
        return expr

    def _float_evalf(self, expr):
        u"Évalue le flottant en respectant le réglage du printer (nombre de décimales)."
        if self._settings['mode_scientifique']:
            decimales = self._settings['decimales_sci'] + 1
        else:
            decimales = self._settings['decimales']
        # Le nombre de décimales ne doit pas dépasser la précision interne
        # du flottant, au risque d'ajouter des décimales fausses.
        # Cette précision interne est notée en bits, qu'il faut convertir en
        # nombre de décimales.
        # Nota: log(2)/log(10) = 0.3010299956639812
        precision_interne = round(expr._prec*0.3010299956639812) - 1
        decimales = max(min(decimales, precision_interne), 1)
        return expr.evalf(decimales)


class CustomStrPrinter(MyCustomPrinter, StrPrinter):
    def __init__(self, settings):
        defaults = {'decimales': 18,
                    'mode_scientifique': False,
                    'decimales_sci': 2
                    }
        self._default_settings.update(defaults)
        StrPrinter.__init__(self, settings)

    def _print_str(self, expr):
        return '"%s"' % expr.replace('"', r'\"')

    def _print_unicode(self, expr):
        return '"%s"' % expr.replace('"', r'\"')

    def _print_Exp1(self, expr):
        return 'e'

    def _print_Abs(self, expr):
        return 'abs(%s)' % self._print(expr.args[0])

    def _print_ImaginaryUnit(self, expr):
        return 'i'

    def _print_Infinity(self, expr):
        return '+oo'

    def _print_log(self, expr):
        return "ln(%s)" % self.stringify(expr.args, ", ")

    def _print_Pow(self, *args, **kw):
        return StrPrinter._print_Pow(self, *args, **kw).replace('**', '^')

    def _print_Float(self, expr):
        exposant = None
        if self._settings['mode_scientifique']:
            # Conversion en écriture scientifique.
            puissance = int(floor(log(expr, 10)))
            flottant = self._float_evalf(expr*10**-puissance)
            mantisse = StrPrinter._print_Float(self, flottant)
            exposant = str(puissance)
        else:
            chaine = StrPrinter._print_Float(self, self._float_evalf(expr))
            if 'e' in chaine:
                # Déjà en mode scientifique (ex: 1.3e-15)
                mantisse, exposant = chaine.split('e')

        if exposant is not None:
            # Affichage en mode scientifique
            mantisse = mantisse.rstrip('0')
            # On laisse la mantisse sous forme de flottant.
            # Ainsi, '2,00000*10^-8' devient '2,0*10^-8', et non '2*10^-8'.
            # Lorsqu'on sauvegarde l'état de l'interprète de la calculatrice,
            # les décimaux du type 0,00000002 sont ainsi sauvegardés sous
            # forme décimale, et non sous forme fractionnaire.
            if mantisse.endswith('.'):
                mantisse += '0'
            exposant = exposant.lstrip('+')
            return '%s*10^%s' % (mantisse, exposant)
        else:
            # Par contre, lorsque les décimaux sont des entiers, inutile de les
            # sauvegarder sous forme décimale.
            return chaine.rstrip('0').rstrip('.')

    def _print_Union(self, expr):
        return expr.__str__()

    def _print_set(self, expr):
        return '{%s}' % ' ; '.join(self._print(val) for val in expr)

    def _print_Fonction(self, expr):
        return "%s -> %s" % (", ".join(expr._variables()),
                        self._print(self._convert_Decim(expr.expression)))

    def doprint(self, expr):
        # Mieux vaut faire la substitution une seule fois dès le départ.
        expr = self._convert_Decim(expr)
        return StrPrinter.doprint(self, expr) if not isinstance(expr, unicode) else expr

def custom_str(expr, **settings):
    return CustomStrPrinter(settings).doprint(expr)

# Modifie Basic.__repr__ pour utiliser `custom_str` au lieu de `sstr` (printer de sympy)
# Can't use partial() for this (cf. http://bugs.python.org/issue4331)

Basic.__repr__ = (lambda self: custom_str(self, order=None))


class CustomLatexPrinter(MyCustomPrinter, LatexPrinter):

    def __init__(self, settings):
        defaults = {'decimales': 18,
                    'mode_scientifique': False,
                    'decimales_sci': 2,
                    "mat_str" : "pmatrix",
                    "mat_delim" : "",
                    "mode": "inline",
                    "fold_frac_powers": False,
                    "fold_short_frac": False,
                    }
        self._default_settings.update(defaults)
        LatexPrinter.__init__(self, settings)

    def _print_Temps(self, expr):
        return r"%s \mathrm{j}\, %s \mathrm{h}\, %s \mathrm{min}\, %s \mathrm{s}" % expr.jhms()

    def _print_exp(self, expr, exp=None):
        tex = r"\mathrm{e}^{%s}" % self._print(expr.args[0])
        return self._do_exponent(tex, exp)

    def _print_Exp1(self, expr):
        return r"\mathrm{e}"

    def _print_Abs(self, *args, **kw):
        res = LatexPrinter._print_Abs(self, *args, **kw)
        return res.replace(r'\lvert', r'|').replace(r'\rvert', r'|')

    def _print_Pi(self, *args, **kw):
        return r"\pi"

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
        if self._settings['mode_scientifique']:
            # Gestion de l'écriture scientifique.
            n = int(floor(log(expr, 10)))
            s = LatexPrinter._print_Float(self, self._float_evalf(expr*10**-n))
            return r"%s \times 10^{%s}" % (s, n)
        s = LatexPrinter._print_Float(self, self._float_evalf(expr))
        if s.startswith(r'1.0 \times '): # sympy 0.7.3
            return s[11:]
        elif s.startswith(r'1.0 \cdot '): # sympy 0.7.5
            return s[10:]
        elif r'\times' not in s:
            # Ne pas supprimer un zéro de la puissance !
            s = s.rstrip('0').rstrip('.')
        return s

    def _print_Infinity(self, expr):
        return r"+\infty"

    def _print_Order(self, expr):
        return r"\mathcal{O}\left(%s\right)" % \
            self._print(expr.args[0])

    def _print_Union(self, expr):
        if expr.vide:
            return r"\varnothing"
        tex = r"\cup".join(self._print(intervalle) for intervalle in expr.intervalles)
        tex = tex.replace(r"\right\}\cup\left\{", "\,;\, ")
        return tex

    def _print_Mul(self, expr):
        args = expr.args
        if args[-1] is I:
            if len(args) == 2 and args[0] == -1:
                return LatexPrinter._print_Mul(self, expr)
            return '%s %s' % (self._print(Mul(*args[:-1])), self._print(I))
        return LatexPrinter._print_Mul(self, expr)
        #return ' '.join(self._print(arg) for arg in expr.args)

    def _print_set(self, expr):
        if expr:
            return r'\left\{%s\right\}' % '\,;\,'.join(self._print(val) for val in expr)
        return r"\emptyset"

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
        expr = self._convert_Decim(expr)
        tex = LatexPrinter.doprint(self, expr)
        return tex.replace(r'\operatorname{', r'\mathrm{')


def custom_latex(expr, **settings):
    return CustomLatexPrinter(settings).doprint(expr)
