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


# Ce module sert à tester que toutes les dépendances sont satisfaites,
# et à y remédier dans le cas contraire (si possible).

import sys
import importlib
import importlib.util
import platform
import os
import shutil
import subprocess

# ------------------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------------------

from .version import NOMPROG

# Les valeurs sont les noms des paquets sous Debian/Ubuntu.
dependances = {'PyQt5': 'python3-pyqt5',
               'matplotlib': 'python3-matplotlib',
               'scipy': 'python3-scipy',
               'numpy': 'python3-numpy',
               'mpmath': 'python3-mpmath',
               'PyQt5.Qsci': 'python3-pyqt5.qsci',
               'PyQt5.QtSvg': 'python3-pyqt5.qtsvg',
               }


# Most of the time, the name of the pip package is just the module name.
# However, those are exceptions:
pip_packages = {'PyQt5.Qsci': 'Qscintilla',
               'PyQt5.QtSvg': '', # already included in PyQt5
               }


python_version_min = (3, 5)
python_version_max = (3, 99)

plateforme = platform.system() #'Windows' ou 'Linux' par exemple.

# Paramètres de matplotlib
# Utiliser une installation LaTeX existante (meilleur rendu mais très lent !)
latex = False
latex_unicode = True
moteur_de_rendu = 'Qt5Agg'

# ------------------------------------------------------------------------------

def in_virtual_environment():
    """Test if python is running inside a virtual environment.

    This is used to adapt pip installation mode.
    """
    return sys.prefix != sys.base_prefix

def find_spec(module_name):
    try:
        return importlib.util.find_spec(module_name)
    except ModuleNotFoundError:
        return None

def tester_dependances():
    if hasattr(sys, 'frozen'):
        # Ne pas faire ces tests avec py2exe/py2app/CxFreeze (non seulement inutiles, mais en plus ils échouent).
        return
    # Make sure I have the right Python version.
    version_python_supportee = True
    if sys.version_info[:2] < python_version_min:
        print(" ** Erreur fatale **")
        print(NOMPROG + " nécessite Python %d.%d au minimum." % python_version_min)
        version_python_supportee = False
    elif sys.version_info[:2] > python_version_max:
        print(" ** Erreur fatale **")
        print(NOMPROG + " supporte Python %d.%d au maximum." % python_version_max)
        version_python_supportee = False

    if not version_python_supportee:
        print("Python %d.%d détecté." % sys.version_info[:2])
        sys.exit(-1)

    # Test for dependencies:
    modules_manquants = [
        module_name for module_name in dependances if find_spec(module_name) is None
        ]



    if modules_manquants:
        try:
            if not sys.stdin.isatty():
                raise ImportError
            if input(f"Certaines librairies manquent : {modules_manquants}.\n"
                      "Voulez-vous les installer automatiquement ? (o/N)"
                     ).lower() not in ('o', 'oui', 'yes', 'y'):
                 raise ImportError
            # Try to install missing modules using pip.
            pip_modules = list(filter(None, [pip_packages.get(module, module) for module in modules_manquants]))
            try:
                print("Trying to install following modules using pip: "+ ", ".join(pip_modules))
                if in_virtual_environment():
                    # The `--user` flag is meaningless in a virtual environment.
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + pip_modules)
                else:
                    # However, it is cleaner to use it if we are not in a virtual environment.
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--user'] + pip_modules)
            except subprocess.CalledProcessError:
                print("L'installation automatique des modules manquants a échouée.")
                raise ImportError
            print('Des modules indispensables ont été installés.')
            print('Redémarrage de Géophar...')
            os.execv(sys.executable, [sys.executable] + sys.argv)
            sys.exit()
        except ImportError:
            if plateforme == 'Linux' and shutil.which('apt'):
                paquets = ' '.join(dependances[m] for m in modules_manquants)
                print(f"""
[\033[91mERREUR\033[39m] Certains paquets sont manquants : {paquets}.

Votre distribution semble être dérivée de Debian ou d'Ubuntu,
il est possible de remédier à cette situation en lançant la commande :
----------------------------------------------------------------------
\033[1m\
sudo apt update; sudo apt install {paquets}\
\033[0m
----------------------------------------------------------------------
Vous pourrez ensuite relancer Géophar.
""")
        else:
            print('** Erreur fatale **\nLes modules suivants sont introuvables !')
            print('MODULE(S) MANQUANT(S): %s.' % ', '.join(modules_manquants))
        sys.exit(-1)


def configurer_dependances():
    import PyQt5

    # ---------------------------
    # Configuration de Matplotlib
    # ---------------------------
    try:
        # Cx_Freeze version needs this (so that matplotlib can found pyparsing).
        import pyparsing
    except ImportError:
        pass
    import matplotlib
    matplotlib.rcParams['backend'] = 'Qt5Agg'
    try:
        # For old versions of matplotlib (version < 3.0)
        if matplotlib.__version__.split(".")[0] < '3':
            matplotlib.rcParams['backend.qt5'] ='PyQt5'
            matplotlib.rcParams["text.latex.unicode"] = latex_unicode
    except KeyError:
        pass
    matplotlib.use(moteur_de_rendu)
    matplotlib.rcParams['text.usetex'] = latex

    # A changer *avant* d'importer pylab ?
    matplotlib.rcParams['font.family'] ='serif'
    #matplotlib.rcParams['font.sans-serif'] ='STIXGeneral'
    matplotlib.rcParams['font.serif'] ='STIXGeneral'
    #matplotlib.rcParams['font.monospace'] ='STIXGeneral'
    matplotlib.rcParams['mathtext.fontset'] ='stix'

