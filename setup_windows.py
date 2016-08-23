#!/usr/bin/python
# -*- coding: utf-8 -*-

# Documentation : http://cx-freeze.readthedocs.org/en/latest/distutils.html

import sys, os
import compileall
from cx_Freeze import setup, Executable

from tools.scriptlib import cd, mv, mkdir, rmdir, cp, rm, zip7

execfile(os.path.join('wxgeometrie', 'version.py'))

# install = True -> enregistrer les paramètres dans `Documents and Settings`.
with open('wxgeometrie/param/personnaliser.py', 'w') as f:
    f.write('''# -*- coding: iso-8859-1 -*-
from __future__ import division

# Placez ici les modifications que vous souhaitez apporter au fichier de parametrage.
debug = False
install = True''')


# Patcher cx_Freeze (freezer.py) :
# EXTENSION_LOADER_SOURCE = \
# """
# def __bootstrap__():
    # import imp, os, sys
    # global __bootstrap__, __loader__
    # __loader__ = None; del __bootstrap__, __loader__
    # found = False
    # for p in sys.path:
        # if not os.path.isdir(p):
            # continue
        # f = os.path.join(p, "%s")
        # if not os.path.exists(f):
            # continue
        # m = imp.load_dynamic(__name__, f)
        # import sys
        # sys.modules[__name__] = m
        # found = True
        # break
    # if not found:
        # del sys.modules[__name__]
        # raise ImportError("No module named %%s" %% __name__)
# __bootstrap__()
# """

#############################################################################
# preparation des options
# path = sys.path.append(os.path.join("..", "..", "biblio"))
# includes = ["printx", "bibconcours"]
includes = ['sys', 'six', 'timeit', 'colorsys']
# collections.abc: cf. https://openclassrooms.com/forum/sujet/cx-freeze-no-file-named-sys
excludes = ['Tkinter', 'wx', 'collections.abc']

packages = []
# A cause du système dynamique de chargement des modules, la version de wxgeometrie contenue dans librairie.zip ne suffit pas.
include_files = ['wxgeometrie']

build_exe_options = {#"path": ['.'] + sys.path,
           "includes": includes,
           "excludes": excludes,
           "packages": packages,
           "compressed": True,
           "create_shared_zip": True,
           # Ne fonctionne pas
           # "replace_paths": [('*', 'local\\')],
           'icon' : 'wxgeometrie\\images\\icone.ico',
           'include_msvcr': True,
           'include_files': include_files,
           'append_script_to_exe': True,
           'include_in_shared_zip': False,
           }

# Shortcuts for Windows Installer.
# cf. http://stackoverflow.com/questions/15734703/use-cx-freeze-to-create-an-msi-that-adds-a-shortcut-to-the-desktop
# First, create Shortcut Table.
# http://msdn.microsoft.com/en-us/library/windows/desktop/aa371847(v=vs.85).aspx
# An example:
# http://msdn.microsoft.com/en-us/library/windows/desktop/aa372018%28v=vs.85%29.aspx
shortcut_table = [
    ("sGeophar",                # Shortcut
     "DesktopFolder",          # Directory_
     "Geophar",                # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]geophar.exe", # Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     )
    ]

# Now create the table dictionary.
msi_data = {"Shortcut": shortcut_table}

# Change some default MSI options and specify the use of the above defined tables.
bdist_msi_options = {
    'upgrade_code': '{16520F3A-DC3B-11E2-C378-082449E1B01E}',
    'add_to_path': False,
    'initial_target_dir': r'[ProgramFilesFolder]\geophar',
    'data': msi_data
    }


#############################################################################
# preparation des cibles
base = None
if sys.platform == "win32":
    base = "Win32GUI"

cible_1 = Executable(
    script = "geophar.pyw",
    base = base,
    compress = True,
    icon = None,
    shortcutName = "Geophar",
    shortcutDir = "ProgramMenuFolder"
    )

cible_2 = Executable(
    script = "geophar.pyw",
    base = None,
    targetName = 'geophar-console-mode.exe',
    compress = True,
    icon = None,
    )


#############################################################################
# creation du setup

print(u"\nCreation de l'installeur...")

setup(
    name = "Geophar",
    version = version,
    description = "Le couteau suisse du prof de maths.",
    author = "Nicolas Pourcelot",
    options = {"build_exe": build_exe_options, "bdist_msi": bdist_msi_options},
    executables = [cible_1, cible_2],
    license='GNU Public License v2+',
    url='http://wxgeo.free.fr',
    )


#############################################################################
# Optimisation et empaquetage de la version sans installation

print(u"\nCreation de la version sans installation...")

python_version = '%s.%s' % (sys.version_info.major, sys.version_info.minor)

# Un peu de ménage et de renommage des dossiers au préalable.
cd('build')
mv('exe.win32-%s' % python_version, 'geophar')
rmdir('bdist.win32')
# Nouvelle arborescence : [projet]/build/geophar/wxgeometrie/...
cd('geophar')

# install = False -> enregistrer les paramètres dans le même dossier que l'exécutable.
with open('wxgeometrie/param/personnaliser.py', 'w') as f:
    f.write('''# -*- coding: iso-8859-1 -*-
from __future__ import division

# Placez ici les modifications que vous souhaitez apporter au fichier de parametrage.
debug = False
install = False''')

# Pour plus de clarté, on regroupe les fichiers .pyd dans le dossier dll/
mkdir('dll')
mv('*.pyd', 'dll')
cd('dll')               # DIR: [projet]/build/geophar/dll
# Etrangement, il semble que les fichiers .pyd utilisés par PyQt doivent être dans le même dossier que geophar.exe.
mv('PyQt4*.pyd', '..')
mv('sip.pyd', '..')
cd('..')                # DIR: [projet]/build/geophar

# On génère les fichiers .pyc (accélère le premier démarrage du logiciel).
compileall.compile_dir('wxgeometrie', maxlevels=50)
# On supprime `wxgeometrie` de library.zip...
zip7('d library.zip wxgeometrie -r')
cd('wxgeometrie')       # DIR: [projet]/build/geophar/wxgeometrie
# ...et on ajoute sympy (sans les fichiers .py).
cd('sympy')             # DIR: [projet]/build/geophar/wxgeometrie/sympy
rm('*.py', recursive=True)
cd('..')                # DIR: [projet]/build/geophar/wxgeometrie
zip7('a ../library.zip sympy -r')
rmdir('sympy')

# On ajoute un lanceur ('geophar.exe' généré via Autokeys), pour plus de clarté.
cd('../..')             # DIR: [projet]/build
cp('../tools/resources/geophar.exe', 'geophar.exe')
cd('..')                # DIR: [projet]
mv('build', 'dist/Geophar')

# On crée un fichier 7zip auto-extractible.
print(u'\nCompression...')
cd('dist')              # DIR: [projet]/dist
# cp('../tools/resources/sfx7z.sfx', 'sfx7z.sfx')
zip7(r'a -sfx7z.sfx Geophar-sans-installation-%s.exe Geophar' %version)
# rm('sfx7z.sfx')
print(u"Version autonome finalisee !")


