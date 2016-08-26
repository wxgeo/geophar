#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement, print_function
from __future__ import absolute_import
from __future__ import unicode_literals

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


import os, sys, stat
from os.path import join, expanduser, isdir
from .scriptlib import command, cd, cp

_module_path = os.path.split(os.path.realpath(sys._getframe().f_code.co_filename))[0]

print('Repertoire courant : ' + _module_path)

paths = {
        'root': '/usr/local', # os.environ['XDG_DATA_DIRS'].split(':')[-1],
        'local': expanduser('~/.local'),
        }

locations = {
        'desktop_path': 'applications',
        'mime_root_path': 'mime',
        'mime_path': 'mime/packages',
        'svg_icon_path': 'icons/hicolor/scalable/apps',
        'png_icon_path': 'icons/hicolor/48x48/apps',
        }

# Choix du mode d'installation (local ou global).

while True:
    choice = raw_input('Installer pour tous les utilisateurs (o/N) ?')
    if choice in ('n', 'N', ''):
        choice = 'local'
        break
    elif choice in ('o', 'O'):
        if not os.access(paths['root'], os.W_OK):
            print("\n\033[1;31m*** ERREUR ***\033[0m")
            print("Vous n'avez pas la permission d'installer pour "
                  "tous les utilisateurs.")
            print("Tapez '\033[0;32msudo python tools/linux-install.py\033[0m' pour une "
                  "installation multi-utilisateurs.")
            sys.exit(1)
        choice = 'root'
        break
    else:
        print(u"Réponse incorrecte (tapez 'o' ou 'N').")


for loc in locations:
    locations[loc] = join(paths[choice], 'share', locations[loc])
    if not isdir(locations[loc]):
        os.makedirs(locations[loc])

# Copie des fichiers.

cd(join(_module_path, 'resources'))

cp('geophar.desktop', locations['desktop_path'])
cp('geophar.svg', locations['svg_icon_path'])
cp('geophar.png', locations['png_icon_path'])
cp('x-geophar.xml', locations['mime_path'])

cd('../..')

# Création du fichier sh.
if choice == 'root':
    exec_path = '/usr/local/bin'
else:
    exec_path = expanduser('~/bin')
    if not isdir(exec_path):
        os.mkdir(exec_path)

script_name = join(exec_path, 'geophar')

with open(script_name, 'w') as f:
    f.write('#!/bin/sh\n')
    f.write('exec %s/geophar.pyw $*' % os.getcwd())

if choice == 'root':
    os.chmod(script_name, stat.S_IRWXU|stat.S_IXOTH)
else:
    os.chmod(script_name, stat.S_IRWXU)

# Mise à jour des bases de données.

update_desktop = 'update-desktop-database %s' % locations['desktop_path']
update_mime = 'update-mime-database %s' % locations['mime_root_path']
command(update_desktop)
command(update_mime)

# Création du script de désinstallation.

cd(_module_path)

with open('linux-uninstall.py', 'w') as f:
    f.write('#!/usr/bin/env python\n')
    f.write('# -*- coding: utf-8 -*-\n')
    f.write('from scriptlib import *\n')
    f.write('rm(%s)\n' % repr(join(locations['desktop_path'], 'geophar.desktop')))
    f.write('rm(%s)\n' % repr(join(locations['mime_path'], 'x-geophar.xml')))
    f.write('rm(%s)\n' % repr(join(locations['svg_icon_path'], 'geophar.svg')))
    f.write('rm(%s)\n' % repr(join(locations['png_icon_path'], 'geophar.png')))
    f.write('rm(%s)\n' % repr(script_name))
    f.write('command(%s)\n' % repr(update_desktop))
    f.write('command(%s)\n' % repr(update_mime))
    f.write('print("=== Desinstallation terminee. ===")')

os.chmod('linux-uninstall.py', stat.S_IRWXU)

print(u"=== L'installation est terminée. ===")
print(u"Un fichier linux-uninstall.py a été généré.")
