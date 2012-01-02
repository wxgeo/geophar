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

import urllib

import param
from .infos import informations_configuration
from .fonctions import uu

def rapporter(titre='', auteur='', email='', description='', historique='',
              log='', config=''):
    parametres = param.__dict__.copy()
    parametres.pop("__builtins__", None)
    parametres = "\n".join(str(key) + " = " + repr(val) for key, val in parametres.items())

    data = {
    "version": param.version,
    "config": config or informations_configuration(),
    "titre": titre,
    "auteur": auteur,
    "email": email,
    "param": parametres,
    "description": description,
    "historique": historique,
    "log": log,
    }
    for key, value in data.items():
#        data[key] = zlib.compress(uu(value.replace("\n", "\n<br>\n")).encode("utf-8"), 9).replace("\x01", "\x01\x03").replace("\x00", "\x01\x02") # php n'aime pas les caract�res nuls dans une cha�ne semble-t-il...
        data[key] = uu(value).replace("\n", "\n<br>\n").encode("iso-8859-1")
    msg = 'Erreur inconnue.'
    try:
        filename, headers = urllib.urlretrieve("http://wxgeo.free.fr/wordpress/contact")
        with open(filename) as f:
            adresse = f.read(300)
        remote = urllib.urlopen(adresse, urllib.urlencode(data))
        msg = remote.read()
        remote.close()
        return True, uu(msg)
    except Exception:
        # XXX: print_error() is not thread safe.
        return False, uu(msg)
