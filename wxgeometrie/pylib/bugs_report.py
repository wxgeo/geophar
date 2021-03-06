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

import urllib.request, urllib.parse
import cgi

from .. import param
from .infos import informations_configuration

def rapporter(titre='', auteur='', email='', description='', historique='',
              log='', config='', fichier=''):
    parametres = param.__dict__.copy()
    parametres.pop("__builtins__", {})
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
    "fichier": fichier, # fichier en cours
    }
    for key, value in data.items():
#        data[key] = zlib.compress(uu(value.replace("\n", "\n<br>\n")).encode("utf-8"), 9).replace("\x01", "\x01\x03").replace("\x00", "\x01\x02") # php n'aime pas les caractères nuls dans une chaîne semble-t-il...
        data[key] = cgi.escape(value).replace("\n", "\n<br>\n").encode("iso-8859-1", 'xmlcharrefreplace')
    msg = 'Erreur inconnue.'
    try:
        filename, headers = urllib.request.urlretrieve("http://wxgeo.free.fr/wordpress/contact")
        with open(filename) as f:
            adresse = f.read(300)
        remote = urllib.request.urlopen(adresse, urllib.parse.urlencode(data))
        msg = remote.read()
        remote.close()
        return True, msg
    except Exception:
        # XXX: print_error() is not thread safe.
        return False, msg
