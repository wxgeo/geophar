#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                        Geolib                     #
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


class Contexte(dict):
    u"""Gestionnaire de contexte.

    Exemple d'usage:
    >>> from wxgeometrie.geolib.objet import Contexte
    >>> # Contexte global
    >>> contexte = Contexte(exact = False, decimales = 7)
    >>> # Contexte local
    >>> with contexte(exact = True):
    ...     print contexte['exact']
    True
    >>> print contexte['exact']
    False
    """

    __slots__ = '__local_dicts', '__no_direct_call'

    def __init__(self, **kw):
        dict.__init__(self, **kw)
        self.__local_dicts = []
        # Surveille que la méthode .__call__() ne soit jamais appelée directement
        self.__no_direct_call = True

    def __getitem__(self, key):
        # On cherche d'abord dans les contextes locaux (en commençant par le dernier)
        for dico in reversed(self.__local_dicts):
            if dico.has_key(key):
                return dico[key]
        return dict.__getitem__(self, key)

    def __call__(self, **kw):
        u"""Cette méthode ne doit *JAMAIS* être appelée en dehors d'un contexte 'with'.

        Exemple d'usage:
        >>> from wxgeometrie.geolib.objet import Contexte
        >>> contexte = Contexte(exact = False, decimales = 7)
        >>> with contexte(exact = True):
        ...     print contexte['exact']
        True
        """
        # On ajoute un contexte local
        self.__local_dicts.append(kw)
        # On surveille que la méthode .__call__() ne soit jamais appelée directement
        # Cela conduirait à des memory leaks (empilement de contextes locaux jamais effacés)
        assert self.__no_direct_call, "Utilisation precedente en dehors d'un contexte 'with'."
        self.__no_direct_call = False
        return self

    def __enter__(self):
        # La méthode __enter__() est appelée juste après la méthode __call__()
        self.__no_direct_call = True

    def __exit__(self, type, value, traceback):
        # On supprime le dernier contexte local
        self.__local_dicts.pop()




contexte = Contexte(exact = True,
                    decimales = param.decimales,
                    unite_angle = param.unite_angle,
                    tolerance = param.tolerance,
                    afficher_messages = param.afficher_messages,
                    )
