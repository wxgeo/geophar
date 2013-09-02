# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##########################################################################
#
#                          Wrapper générique
#
##########################################################################
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


# Motivation:
# http://docs.python.org/reference/datamodel.html#more-attribute-access-for-new-style-classes


#TODO:this must wrap all special methods


class GenericWrapper(object):

    slots = '__val'

    def __init__(self, val):
        object.__setattr__(self, '_GenericWrapper__val', val)

    def __getattribute__(self, name):
        val = object.__getattribute__(self, '_GenericWrapper__val')
        return getattr(val, name)

    def __setattr__(self, name, val):
        val = object.__getattribute__(self, '_GenericWrapper__val')
        return setattr(val, name, val)
