# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

######################################
#
#    Détection des modules
#
######################################
#
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
#
######################################

import os

from .parametres import modules_par_defaut

# Modules a importer
# ----------------
_skip_dir = ('OLD',)
_modules_dir = os.path.normpath(os.path.join(__file__, '..', '..', 'modules'))

def _detecter_modules():
    modules = []
    descriptions = {}
    def err(nom, msg):
        print("Warning: %s n'est pas un module valide (%s)." %(nom, msg))
    for nom in os.listdir(_modules_dir):
        if nom not in _skip_dir and os.path.isdir(os.path.join(_modules_dir, nom)):
            description_file = os.path.join(_modules_dir, nom, 'description.py')
            if os.path.isfile(description_file):
                try:
                    compile(nom + '=0', '', 'single') # On teste si le nom est valide
                    try:
                        d = {}
                        execfile(description_file, d)
                        if d['description']['groupe'] != "Modules":
                            # Sert à désactiver les modules en construction.
                            continue
                        descriptions[nom] = d['description']
                        modules.append(nom)
                    except:
                        err(nom, u"fichier '%s' incorrect" %description_file)
                except Exception:
                    err(nom, u"nom de module invalide")
            else:
                err(nom, u"fichier 'description.py' introuvable")
    return modules, descriptions

try:
    modules, descriptions_modules = _detecter_modules()
except OSError:
    print(u"Warning: impossible de détecter les modules (répertoire '%s') !" % _modules_dir)
    modules = []
    descriptions_modules = {}


modules_actifs = dict.fromkeys(modules, False)

for nom in modules_par_defaut:
    modules_actifs[nom] = True


def _key(nom):
    # les modules activés par défaut apparaissent en premier,
    # les autres sont classés par ordre alphabétique.
    key = [1000000,  nom]
    if nom in modules_par_defaut:
        key[0] = modules_par_defaut.index(nom)
    return key

modules.sort(key = _key)
