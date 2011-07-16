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

# choisit comme répertoire courant le repertoire d'execution du script (pour Linux)
from codecs import getwriter
import sys, os
from os.path import dirname, join, realpath

if sys.platform == 'win32':
    sys.stdout = getwriter('cp850')(sys.stdout)
else:
    sys.stdout = getwriter('utf8')(sys.stdout)

path = join(dirname(realpath(sys._getframe().f_code.co_filename)), 'wxgeometrie')
os.chdir(path)
sys.path.insert(0, path)

from wxgeometrie.initialisation import initialiser

if __name__ == '__main__':
    initialiser()
