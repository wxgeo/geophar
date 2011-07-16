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

import urllib
from .infos import informations_configuration
from .. import param
from .fonctions import uu

def rapporter(titre = "", auteur = "", email = "", description = "", historique = "", log = ""):
    parametres = param.__dict__.copy()
    parametres.pop("__builtins__", None)
    parametres = "\n".join(str(key) + " = " + repr(val) for key, val in parametres.items())

    data = {
    "version": param.version,
    "config": informations_configuration(),
    "titre": titre,
    "auteur": auteur,
    "email": email,
    "param": parametres,
    "description": description,
    "historique": historique,
    "log": log,
    }
    for key, value in data.items():
#        data[key] = zlib.compress(uu(value.replace("\n", "\n<br>\n")).encode("utf-8"), 9).replace("\x01", "\x01\x03").replace("\x00", "\x01\x02") # php n'aime pas les caractères nuls dans une chaîne semble-t-il...
        data[key] = uu(value).replace("\n", "\n<br>\n").encode("iso-8859-1")
    try:
        f = urllib.urlopen("http://www.wxgeo.free.fr/bugs_report.php", urllib.urlencode(data))
        if param.debug:
            print f.read()
        f.close()
        return True
    except IOError:
        return False
