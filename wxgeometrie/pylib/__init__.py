# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

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

from .. import param # parametres du programme

#from fonctions import * # librairie regroupant diverses fonctions "maison"
#from infos import * # librairie servant a generer des infos sur la configuration (utile pour le debugage)
from .fonctions import uu, is_in, WeakList, print_error, property2, str3, \
                      CompressedList, rstrip_, str2, no_twin, warning, \
                      CustomWeakKeyDictionary, debug, no_argument, path2, \
                      removeend, advanced_split, regsub, split_around_parenthesis,\
                      msplit, OrderedDict, find_closing_bracket
# outils pour gerer la securite lors d'execution de code (tache delicate !)
from .securite import eval_safe, eval_restricted
#import bugs_report
#import erreurs
#import rapport
from generic_wrapper import GenericWrapper

from .decorator import decorator

import matplotlib, matplotlib.mathtext
matplotlib.rcParams['text.usetex'] = param.latex
matplotlib.rcParams["text.latex.unicode"] = param.latex_unicode

# A changer *avant* d'importer pylab ?
matplotlib.rcParams['font.family'] ='serif'
#matplotlib.rcParams['font.sans-serif'] ='STIXGeneral'
matplotlib.rcParams['font.serif'] ='STIXGeneral'
#matplotlib.rcParams['font.monospace'] ='STIXGeneral'
matplotlib.rcParams['mathtext.fontset'] ='stix'

import pylab_ as pylab
# le fichier pylab_.py est modifie lors d'une "compilation" avec py2exe
import numpy

mathtext_parser = matplotlib.mathtext.MathTextParser("PS").parse

def tex(txt):
    u"Rajoute des $ si l'expression LaTeX ainsi obtenue est correcte."
    try:
        mathtext_parser('$' + txt + '$')
        return '$' + txt + '$'
    except Exception:
        return txt

def fullrange(a, b, pas):
    u'''Comme range(), mais avec des flottants, et contient en dernière valeur 'b'.

    Équivalent de numpy.append(numpy.arrange(a, b, pas), b).'''
    return numpy.append(numpy.arange(a, b, pas), b)
