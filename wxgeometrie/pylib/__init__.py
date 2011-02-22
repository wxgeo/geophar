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

# version unicode

import __builtin__ as builtin
import random as module_random
import copy as module_copy
import math, cmath
import os, string, re, types, inspect, sys, traceback, gc, weakref, tempfile, urllib, webbrowser, zlib, zipfile, time, new, itertools, functools, operator

import thread

import decorator

import param # parametres du programme
#~ try:
    #~ import wxversion
    #~ wxversion.select(param.version_wxpython) # version à utiliser de préférence
#~ except:  # ou bien la version n'est pas trouvée, ou bien on est dans py2exe
    #~ print u"Erreur : impossible de charger la version %s de WxPython." %param.version_wxpython
#from copy import copy
from random import normalvariate

from fonctions import * # librairie regroupant diverses fonctions "maison"
from infos import * # librairie servant a generer des infos sur la configuration (utile pour le debugage)
import fonctions
import securite # outils pour gerer la securite lors d'execution de code (tache delicate !)
import bugs_report
import erreurs
import rapport
from generic_wrapper import GenericWrapper

from decorator import decorator

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



types.ArrayType = type(numpy.array([])) # compense un manque de la librairie types.
types.UfuncType = type(numpy.absolute)
fonctions_maths = [key for key, val in math.__dict__.items() if type(val) == types.BuiltinFunctionType]
fonctions_matplotlib = [key for key, val in pylab.__dict__.items() if type(val) == types.UfuncType]

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
