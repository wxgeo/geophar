# -*- coding: utf-8 -*-
"""Regroupe la majorité des outils utiles à un professeur de mathématiques."""

#~ import os
from os.path import dirname, realpath, abspath, join
import sys

from .dependances import tester_dependances, configurer_dependances
tester_dependances()
configurer_dependances()


# VERSION COMPILEE AVEC CX_FREEZE
# -------------------------------
if getattr(sys, 'frozen', False) and sys.platform == "win32":
    application_path = dirname(sys.executable)
    # XXX: Hack temporaire, permettant de préférer la version locale de sympy.
    sympy_path = join(application_path, 'library.zip', 'wxgeometrie')
    sys.path.insert(0, sympy_path)

    # On range les fichiers .pyd dans `wxgeometrie/dll`.
    dll_directory = join(application_path, 'dll')
    sys.path.append(dll_directory)
    # print('\nPATHS:')
    # for path in sys.path:
        # print ' * ' + path
    # print('')
    # On range également les fichiers .dll dans `wxgeometrie/dll`.
    # os.environ['PATH'] = ';'.join([dll_directory, os.environ['PATH']])

# CAS GENERAL
# -----------
else:
    # XXX: Hack temporaire, permettant de préférer la version locale de sympy.
    # Attention, on ne peut pas toujours utiliser `sys._geophar_path`
    # (car `geophar.pyw` peut être placé ailleurs dans l'arborescence,
    #  c'est le cas par exemple dans l'installation Debian).
    sympy_path = abspath(dirname(realpath(sys._getframe().f_code.co_filename)))
    sys.path.insert(0, sympy_path)

    if not getattr(sys, '_launch_geophar', False):
        # Lorsque wxgeometrie/geophar est utilisée comme librairie,
        # on charge dans l'espace de nom du module tous les objets les plus
        # utiles pour l'utilisateur final.
        #
        # Ceci permet d'effectuer par exemple :
        # >>> from wxgeometrie import Point
        # >>> A = Point(1, 2)
        #
        # Par contre, lorsque le programme géophar est lancé, il a besoin
        # de lancer **en tout premier** la fonction `initialiser()`
        # de wxgeometrie.initialisation, avant même que les paramètres et
        # préférences soient chargés.
        # Ceci permet de gérer en 1er les options de la ligne de commande,
        # d'avoir une mesure plus correcte du temps de démarrage, et d'afficher
        # potentiellement le SplashScreen plus tôt (TODO).
        # Dans ce cas, il ne faut donc pas charger wxgeometrie.geolib ici,
        # car ceci implique d'importer le module wxgeometrie.param.

        from .param import version as __version__
        from .geolib import *
