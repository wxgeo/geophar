# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#               Objets mathlib                #
##--------------------------------------#######
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

import numpy

UfuncType = type(numpy.absolute)
fonctions_numpy = [key for key, val in numpy.__dict__.items() if type(val) == UfuncType]

class ObjetMathematique(object):
    u"Classe mère de la plupart des objets mathématiques."

    def __lt__(self, y):
        return not self >= y

    def __ge__(self, y):
        return self > y or self == y

    def __le__(self, y):
        return not self > y

    def __ne__(self, y):
        return not self.__eq__(y)

    def __nonzero__(self): # la valeur logique de l'objet (la doc officielle est fausse ??)
        return self != 0    # utilisée dans un test "if" par exemple.

    def __truediv__(self, y):
        return self.__div__(y)

    def __rtruediv__(self, y):
        return self.__rdiv__(y)

    def __sub__(self, y):   return self + (- y)

    def __rsub__(self, y):  return y + (- self)

    def __radd__(self,y):   return self.__add__(y)

    def __rmul__(self, y): return self.__mul__(y)

    def __pos__(self):      return self

    def __cmp__(self, y):
        if hasattr(self, "__gt__") and isinstance(y, (ObjetMathematique, float, int, long)):
            if self > y:
                return 1
            elif self < y:
                return -1
            else:
                return 0
        return NotImplemented


class Reel(ObjetMathematique):
    u"""Classe mère pour les objets mathématiques supportant les fonctions usuelles.
    Permet de leur appliquer les opérations mathématiques de pylab."""

    for nom in fonctions_numpy:
        exec("""
def %s(self, *args):
    arguments = []
    for arg in args:
        arguments.append(float(arg))
    return numpy.%s(float(self), *arguments)""" %(nom, nom))
    del nom
