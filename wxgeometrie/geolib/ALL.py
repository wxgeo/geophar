# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                 ALL GEOLIB                  #
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

# version unicode

from pylib import *
from mathlib import *

from variables import *
from labels import *
from vecteurs import *
from cercles import *
from angles import *
from transformations import *
from courbes import *
from polygones import *
from intersections import *
from interpolations import *
from fonctions import *
from polyedres import *
from widgets import * # NON FONCTIONNEL

#~ from widgets import *


for __classe__ in vars().values():
    if isinstance(__classe__, type) and issubclass(__classe__, Objet):
        prefixe = "_" + __classe__.__name__ + "__"
        __arguments__ = []
        for key, value in vars(__classe__).iteritems():
            if isinstance(value, BaseArgument) and key.startswith(prefixe):
                # Chaque argument récupère son nom...
                value.nom = key
                # ...et sa classe de rattachement :
                value.rattachement = __classe__
                # Chaque classe recupère la liste de ses arguments... (en évitant d'utiliser 'inspect', qui n'est pas compatible avec psycho)
                # On cherche les entrées de la classe 'MaClasse' qui soient de type 'Argument' ou 'Arguments',
                # et qui commencent par '_MaClasse__'.
                # Exemple : '_MaClasse__monargument' qui est stocké comme 'monargument' (on enlève le préfixe).
                __arguments__.append((value.__compteur__, key[len(prefixe):]))
        # on trie les arguments par ordre de déclaration dans la classe
        __arguments__.sort()
        __classe__.__arguments__ = tuple(key for compteur, key in __arguments__) # tuple pour éviter des bugs (partage d'1 même liste entre plusieurs classes par ex.)

del __classe__

_vecteur_unite = Vecteur_libre(1, 0)
