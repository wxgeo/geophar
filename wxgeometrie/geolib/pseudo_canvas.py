# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

##--------------------------------------#######
#                Pseudo-canvas                  #
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

from .. import param

class PseudoContexte(object):
    u"Contexte bidon ne faisant absolument rien."

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass


class PseudoCanvas(object):
    u"""Faux canvas utilisé par défaut par la feuille de travail.

    Permet de faire appel à l'objet canvas et à ses méthodes sans générer d'erreur
    lorsqu'il n'y a pas de canvas."""

    def __getattr__(self, nom):
        if param.debug:
            print('Action %s non effectuee (pas de canevas).' %nom)
        return (lambda *args, **kw: NotImplemented)
##
##    def __setattr__(self, nom, valeur):
##        pass
##
    def geler_affichage(self, *args, **kw):
        return PseudoContexte()

##    def detecter(self, *args, **kw):
##        pass
##
##    def actualiser(self, *args, **kw):
##        pass

    def __nonzero__(self):
        return False

    def __bool__(self):
        return False

##    def redessiner_et_actualiser(self, *args, **kw):
##        pass

_pseudocanvas = PseudoCanvas()
