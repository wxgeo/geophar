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

# version unicode

__doc__ = """
Cette librairie contient des versions modifiées des fonctions courantes, pour qu'elles puissent être appliquées aussi bien à des nombres qu'à des variables formelles ou encore des listes...

Le dictionnaire fonctions_mathematiques contient les infos suivantes : {<nom de la fonction>: [<nom dans math>, <nom dans numpy>, <nom dans sympy>]}

Il est générée via le code suivant :

import math
liste = math.__dict__.items()
dico = {}
ignore_liste = ("ldexp", "frexp", "pow", "degrees", "radians", "atan2", "hypot", "modf", "fmod", "fabs")
dico.update([(nom,[nom,nom,nom]) for nom, objet in liste if not nom.startswith("_") and hasattr(objet, "__call__") and not nom in ignore_liste])
# fonctions ayant un nom différent dans numpy :
dico["asin"][1] = "arcsin"; dico["acos"][1] = "arccos"; dico["atan"][1] = "arctan"
# fonctions ayant un nom différent dans sympy :
dico["ceil"][2] = "ceiling"
# fonctions à renommer :
dico["ln"] = dico.pop("log")
dico["log"] = dico.pop("log10")
liste = dico.items()
liste.sort()
s = "_fonctions_mathematiques = " + repr(liste).replace("[(", "{\n").replace(")]", "}").replace(", [", ": [").replace("), (", ",\n")
print s
exec(s)

# Vérification du contenu du dictionnaire :
import math, sympy, numpy
sympy.log10 = lambda x: sympy.log(x, 10)
for elt in _fonctions_mathematiques.items():
m, n, s = elt[1]
getattr(math, m)
getattr(numpy, n)
getattr(sympy, s)

# Génération du code :

_fonctions_mathematiques = {
    'acos': ['acos', 'acos', 'acos'],
    'asin': ['asin', 'asin', 'asin'],
    'atan': ['atan', 'atan', 'atan'],
    'ceil': ['ceil', 'ceil', 'ceiling'],
    'cos': ['cos', 'cos', 'cos'],
    'cosh': ['cosh', 'cosh', 'cosh'],
    'exp': ['exp', 'exp', 'exp'],
    'floor': ['floor', 'floor', 'floor'],
    'ln': ['log', 'log', 'log'],
    'log': ['log10', 'log10', 'log10'],
    'sin': ['sin', 'sin', 'sin'],
    'sinh': ['sinh', 'sinh', 'sinh'],
    'sqrt': ['sqrt', 'sqrt', 'sqrt'],
    'tan': ['tan', 'tan', 'tan'],
    'tanh': ['tanh', 'tanh', 'tanh']}

for _nom, _noms in _fonctions_mathematiques.items():
    _nom_math, _nom_numpy, _nom_sympy = _noms
    print  '''\n\ndef %s(*args, **kw):
    arg0 = args[0]
    if isinstance(arg0, (int, float, long)):
        return _math.%s(*args,**kw)
    elif isinstance(arg0, complex):
        return _cmath.%s(*args,**kw)
    elif isinstance(arg0, _sympy.Basic):
        return _sympy.%s(*args,**kw)
    else:
        return _numpy.%s(*args,**kw)''' %(_nom, _nom_math, _nom_math, _nom_sympy, _nom_numpy)

"""


_fonctions_mathematiques = {
    'abs':['abs', 'abs', 'abs'],
    'acos': ['acos', 'acos', 'acos'],
    'asin': ['asin', 'asin', 'asin'],
    'atan': ['atan', 'atan', 'atan'],
    'ceil': ['ceil', 'ceil', 'ceiling'],
    'cos': ['cos', 'cos', 'cos'],
    'cosh': ['cosh', 'cosh', 'cosh'],
    'exp': ['exp', 'exp', 'exp'],
    'floor': ['floor', 'floor', 'floor'],
    'ln': ['log', 'log', 'log'],
    'log': ['log10', 'log10', 'log10'],
    'sin': ['sin', 'sin', 'sin'],
    'sinh': ['sinh', 'sinh', 'sinh'],
    'sqrt': ['sqrt', 'sqrt', 'sqrt'],
    'tan': ['tan', 'tan', 'tan'],
    'tanh': ['tanh', 'tanh', 'tanh']}

import numpy as _numpy, sympy as _sympy, math as _math, cmath as _cmath
_sympy.log10 = lambda x: _sympy.log(x, 10)

_cmath.floor = _math.floor # afin de renvoyer une erreur si floor est appelé avec un complexe

_math.abs = _cmath.abs = abs

# Le code suivant est généré automatiquement (voir plus haut)


def sinh(*args, **kw):
    arg0 = args[0]
    if isinstance(arg0, (int, float, long)):
        return _math.sinh(*args,**kw)
    elif isinstance(arg0, complex):
        return _cmath.sinh(*args,**kw)
    elif isinstance(arg0, _sympy.Basic):
        return _sympy.sinh(*args,**kw)
    else:
        return _numpy.sinh(*args,**kw)


def asin(*args, **kw):
    arg0 = args[0]
    if isinstance(arg0, (int, float, long)):
        return _math.asin(*args,**kw)
    elif isinstance(arg0, complex):
        return _cmath.asin(*args,**kw)
    elif isinstance(arg0, _sympy.Basic):
        return _sympy.asin(*args,**kw)
    else:
        return _numpy.asin(*args,**kw)


def cos(*args, **kw):
    arg0 = args[0]
    if isinstance(arg0, (int, float, long)):
        return _math.cos(*args,**kw)
    elif isinstance(arg0, complex):
        return _cmath.cos(*args,**kw)
    elif isinstance(arg0, _sympy.Basic):
        return _sympy.cos(*args,**kw)
    else:
        return _numpy.cos(*args,**kw)


def log(*args, **kw):
    arg0 = args[0]
    if isinstance(arg0, (int, float, long)):
        return _math.log10(*args,**kw)
    elif isinstance(arg0, complex):
        return _cmath.log10(*args,**kw)
    elif isinstance(arg0, _sympy.Basic):
        return _sympy.log10(*args,**kw)
    else:
        return _numpy.log10(*args,**kw)


def atan(*args, **kw):
    arg0 = args[0]
    if isinstance(arg0, (int, float, long)):
        return _math.atan(*args,**kw)
    elif isinstance(arg0, complex):
        return _cmath.atan(*args,**kw)
    elif isinstance(arg0, _sympy.Basic):
        return _sympy.atan(*args,**kw)
    else:
        return _numpy.atan(*args,**kw)


def floor(*args, **kw):
    arg0 = args[0]
    if isinstance(arg0, (int, float, long)):
        return _math.floor(*args,**kw)
    elif isinstance(arg0, complex):
        return _cmath.floor(*args,**kw)
    elif isinstance(arg0, _sympy.Basic):
        return _sympy.floor(*args,**kw)
    else:
        return _numpy.floor(*args,**kw)


def ln(*args, **kw):
    arg0 = args[0]
    if isinstance(arg0, (int, float, long)):
        return _math.log(*args,**kw)
    elif isinstance(arg0, complex):
        return _cmath.log(*args,**kw)
    elif isinstance(arg0, _sympy.Basic):
        return _sympy.log(*args,**kw)
    else:
        return _numpy.log(*args,**kw)


def tanh(*args, **kw):
    arg0 = args[0]
    if isinstance(arg0, (int, float, long)):
        return _math.tanh(*args,**kw)
    elif isinstance(arg0, complex):
        return _cmath.tanh(*args,**kw)
    elif isinstance(arg0, _sympy.Basic):
        return _sympy.tanh(*args,**kw)
    else:
        return _numpy.tanh(*args,**kw)


def sqrt(*args, **kw):
    arg0 = args[0]
    if isinstance(arg0, (int, float, long)):
        return _math.sqrt(*args,**kw)
    elif isinstance(arg0, complex):
        return _cmath.sqrt(*args,**kw)
    elif isinstance(arg0, _sympy.Basic):
        return _sympy.sqrt(*args,**kw)
    else:
        return _numpy.sqrt(*args,**kw)


def cosh(*args, **kw):
    arg0 = args[0]
    if isinstance(arg0, (int, float, long)):
        return _math.cosh(*args,**kw)
    elif isinstance(arg0, complex):
        return _cmath.cosh(*args,**kw)
    elif isinstance(arg0, _sympy.Basic):
        return _sympy.cosh(*args,**kw)
    else:
        return _numpy.cosh(*args,**kw)


def exp(*args, **kw):
    arg0 = args[0]
    if isinstance(arg0, (int, float, long)):
        return _math.exp(*args,**kw)
    elif isinstance(arg0, complex):
        return _cmath.exp(*args,**kw)
    elif isinstance(arg0, _sympy.Basic):
        return _sympy.exp(*args,**kw)
    else:
        return _numpy.exp(*args,**kw)


def acos(*args, **kw):
    arg0 = args[0]
    if isinstance(arg0, (int, float, long)):
        return _math.acos(*args,**kw)
    elif isinstance(arg0, complex):
        return _cmath.acos(*args,**kw)
    elif isinstance(arg0, _sympy.Basic):
        return _sympy.acos(*args,**kw)
    else:
        return _numpy.acos(*args,**kw)


def ceil(*args, **kw):
    arg0 = args[0]
    if isinstance(arg0, (int, float, long)):
        return _math.ceil(*args,**kw)
    elif isinstance(arg0, complex):
        return _cmath.ceil(*args,**kw)
    elif isinstance(arg0, _sympy.Basic):
        return _sympy.ceil(*args,**kw)
    else:
        return _numpy.ceiling(*args,**kw)


def sin(*args, **kw):
    arg0 = args[0]
    if isinstance(arg0, (int, float, long)):
        return _math.sin(*args,**kw)
    elif isinstance(arg0, complex):
        return _cmath.sin(*args,**kw)
    elif isinstance(arg0, _sympy.Basic):
        return _sympy.sin(*args,**kw)
    else:
        return _numpy.sin(*args,**kw)


def tan(*args, **kw):
    arg0 = args[0]
    if isinstance(arg0, (int, float, long)):
        return _math.tan(*args,**kw)
    elif isinstance(arg0, complex):
        return _cmath.tan(*args,**kw)
    elif isinstance(arg0, _sympy.Basic):
        return _sympy.tan(*args,**kw)
    else:
        return _numpy.tan(*args,**kw)


def abs(*args, **kw):
    arg0 = args[0]
    if isinstance(arg0, (int, float, long)):
        return _math.abs(*args,**kw)
    elif isinstance(arg0, complex):
        return _cmath.abs(*args,**kw)
    elif isinstance(arg0, _sympy.Basic):
        return _sympy.abs(*args,**kw)
    else:
        return _numpy.abs(*args,**kw)


# Code écrit à la main (ne pas effacer donc !)

def arg(complexe):
    if isinstance(complexe, (int, complex, long, float)):
        return _cmath.log(complexe).imag
    elif isinstance(complexe, _sympy.Basic):
        return _sympy.arg(complexe)
    else:
        return _numpy.imag(_numpy.log(complex))



# Le code suivant génère automatiquement les objets I, E et Pi modifiés
# -------------------------------------------------------

# Note : les noms de classe ne doivent pas être les mêmes que pour sympy

# Bugs connus :
# les opérations ne sont pas commutatives.
# ex: 1.3*e*pi donne une valeur numérique, mais e*pi*1.3 donne une valeur exacte

"""
for symb, classe in (('i', 'ImaginaryUnit'), ('pi', 'Pi'), ('e', 'Exp1')):
    print "class _%s(_sympy.numbers.%s):" %(classe, classe)
    for methode in ('add', 'sub', 'pow', 'mul', 'div', 'truediv', 'mod', 'floordiv', 'divmod'):
        for prefixe in ('', 'r'):
            meth = prefixe + methode
            print '''
    def __%s__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__%s__(y)
        return super(_%s, self).__%s__(self, y)''' %(meth, meth, classe, meth)
    print "\n%s = _%s()\n\n" %(symb, classe)
"""


class _ImaginaryUnit(_sympy.numbers.ImaginaryUnit):

    def __add__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__add__(y)
        return super(_ImaginaryUnit, self).__add__(self, y)

    def __radd__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__radd__(y)
        return super(_ImaginaryUnit, self).__radd__(self, y)

    def __sub__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__sub__(y)
        return super(_ImaginaryUnit, self).__sub__(self, y)

    def __rsub__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rsub__(y)
        return super(_ImaginaryUnit, self).__rsub__(self, y)

    def __pow__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__pow__(y)
        return super(_ImaginaryUnit, self).__pow__(self, y)

    def __rpow__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rpow__(y)
        return super(_ImaginaryUnit, self).__rpow__(self, y)

    def __mul__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__mul__(y)
        return super(_ImaginaryUnit, self).__mul__(self, y)

    def __rmul__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rmul__(y)
        return super(_ImaginaryUnit, self).__rmul__(self, y)

    def __div__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__div__(y)
        return super(_ImaginaryUnit, self).__div__(self, y)

    def __rdiv__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rdiv__(y)
        return super(_ImaginaryUnit, self).__rdiv__(self, y)

    def __truediv__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__truediv__(y)
        return super(_ImaginaryUnit, self).__truediv__(self, y)

    def __rtruediv__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rtruediv__(y)
        return super(_ImaginaryUnit, self).__rtruediv__(self, y)

    def __mod__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__mod__(y)
        return super(_ImaginaryUnit, self).__mod__(self, y)

    def __rmod__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rmod__(y)
        return super(_ImaginaryUnit, self).__rmod__(self, y)

    def __floordiv__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__floordiv__(y)
        return super(_ImaginaryUnit, self).__floordiv__(self, y)

    def __rfloordiv__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rfloordiv__(y)
        return super(_ImaginaryUnit, self).__rfloordiv__(self, y)

    def __divmod__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__divmod__(y)
        return super(_ImaginaryUnit, self).__divmod__(self, y)

    def __rdivmod__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rdivmod__(y)
        return super(_ImaginaryUnit, self).__rdivmod__(self, y)

i = _ImaginaryUnit()


class _Pi(_sympy.numbers.Pi):

    def __add__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__add__(y)
        return super(_Pi, self).__add__(self, y)

    def __radd__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__radd__(y)
        return super(_Pi, self).__radd__(self, y)

    def __sub__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__sub__(y)
        return super(_Pi, self).__sub__(self, y)

    def __rsub__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rsub__(y)
        return super(_Pi, self).__rsub__(self, y)

    def __pow__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__pow__(y)
        return super(_Pi, self).__pow__(self, y)

    def __rpow__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rpow__(y)
        return super(_Pi, self).__rpow__(self, y)

    def __mul__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__mul__(y)
        return super(_Pi, self).__mul__(self, y)

    def __rmul__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rmul__(y)
        return super(_Pi, self).__rmul__(self, y)

    def __div__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__div__(y)
        return super(_Pi, self).__div__(self, y)

    def __rdiv__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rdiv__(y)
        return super(_Pi, self).__rdiv__(self, y)

    def __truediv__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__truediv__(y)
        return super(_Pi, self).__truediv__(self, y)

    def __rtruediv__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rtruediv__(y)
        return super(_Pi, self).__rtruediv__(self, y)

    def __mod__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__mod__(y)
        return super(_Pi, self).__mod__(self, y)

    def __rmod__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rmod__(y)
        return super(_Pi, self).__rmod__(self, y)

    def __floordiv__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__floordiv__(y)
        return super(_Pi, self).__floordiv__(self, y)

    def __rfloordiv__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rfloordiv__(y)
        return super(_Pi, self).__rfloordiv__(self, y)

    def __divmod__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__divmod__(y)
        return super(_Pi, self).__divmod__(self, y)

    def __rdivmod__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rdivmod__(y)
        return super(_Pi, self).__rdivmod__(self, y)

pi = _Pi()


class _Exp1(_sympy.numbers.Exp1):

    def __add__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__add__(y)
        return super(_Exp1, self).__add__(self, y)

    def __radd__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__radd__(y)
        return super(_Exp1, self).__radd__(self, y)

    def __sub__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__sub__(y)
        return super(_Exp1, self).__sub__(self, y)

    def __rsub__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rsub__(y)
        return super(_Exp1, self).__rsub__(self, y)

    def __pow__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__pow__(y)
        return super(_Exp1, self).__pow__(self, y)

    def __rpow__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rpow__(y)
        return super(_Exp1, self).__rpow__(self, y)

    def __mul__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__mul__(y)
        return super(_Exp1, self).__mul__(self, y)

    def __rmul__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rmul__(y)
        return super(_Exp1, self).__rmul__(self, y)

    def __div__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__div__(y)
        return super(_Exp1, self).__div__(self, y)

    def __rdiv__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rdiv__(y)
        return super(_Exp1, self).__rdiv__(self, y)

    def __truediv__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__truediv__(y)
        return super(_Exp1, self).__truediv__(self, y)

    def __rtruediv__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rtruediv__(y)
        return super(_Exp1, self).__rtruediv__(self, y)

    def __mod__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__mod__(y)
        return super(_Exp1, self).__mod__(self, y)

    def __rmod__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rmod__(y)
        return super(_Exp1, self).__rmod__(self, y)

    def __floordiv__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__floordiv__(y)
        return super(_Exp1, self).__floordiv__(self, y)

    def __rfloordiv__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rfloordiv__(y)
        return super(_Exp1, self).__rfloordiv__(self, y)

    def __divmod__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__divmod__(y)
        return super(_Exp1, self).__divmod__(self, y)

    def __rdivmod__(self, y):
        if isinstance(y, (float, int, long)):
            return float(self).__rdivmod__(y)
        return super(_Exp1, self).__rdivmod__(self, y)

e = _Exp1()
