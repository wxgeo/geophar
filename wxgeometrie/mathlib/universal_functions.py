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


__doc__ = """
Cette librairie contient des versions modifiées des fonctions courantes,
pour qu'elles puissent être appliquées aussi bien à des nombres
qu'à des variables formelles ou encore des listes...

Le dictionnaire fonctions_mathematiques contient les infos suivantes :
{<nom de la fonction>: [<nom dans math>, <nom dans numpy>, <nom dans sympy>]}

Il est générée via le code suivant::

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

_math.abs = _cmath.abs = _sympy.abs = abs

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
