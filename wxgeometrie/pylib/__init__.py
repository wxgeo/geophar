# -*- coding: utf-8 -*-

#    WxGeometrie
#    Dynamic geometry, graph plotter, and more for french mathematic teachers.
#    Copyright (C) 2005-2013  Nicolas Pourcelot
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
from .fonctions import uu, is_in, WeakList, print_error, property2, \
                      CompressedList, rstrip_, no_twin, warning, \
                      CustomWeakKeyDictionary, debug, no_argument, path2, \
                      removeend, advanced_split, regsub, split_around_parenthesis,\
                      msplit, OrderedDict, find_closing_bracket
# outils pour gerer la securite lors d'execution de code (tache delicate !)
from .securite import eval_safe, eval_restricted
#import bugs_report
#import erreurs
#import rapport
from .generic_wrapper import GenericWrapper

from .decorator import decorator

import numpy


def fullrange(a, b, pas):
    '''Comme range(), mais avec des flottants, et contient en dernière valeur 'b'.

    Équivalent de numpy.append(numpy.arrange(a, b, pas), b).'''
    return numpy.append(numpy.arange(a, b, pas), b)
