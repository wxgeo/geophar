#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------##
#              WxGeometrie               #
#              main program              #
##--------------------------------------##
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

# choisit comme répertoire courant le repertoire d'execution du script (pour Linux)
import os, sys, codecs

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('cp850')(sys.stdout)
else:
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)
    
try:
    path = os.path.split(__file__)[0]
    if path:    
        os.chdir(path)
except NameError:
    os.chdir(os.path.split(sys.executable)[0]) # le repertoire courant change quand le programme est lancé avec un fichier .geo en paramètre
    sys.path = [os.path.dirname(sys.executable)] + sys.path
    # On charge param seulement après avoir modifié sys.path
    # (cela permet de chercher de préférence le module dans wxgeometrie/param/__init__.py, s'il existe, plutôt que dans wxgeometrie/library.zip)
    import param 
    param.py2exe = True

  
from initialisation import initialiser


if __name__ == '__main__':
    initialiser()



