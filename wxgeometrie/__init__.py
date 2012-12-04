# -*- coding: utf-8 -*-
"""Regroupe la majorité des outils utiles à un professeur de mathématiques."""

from os.path import dirname, realpath, abspath
import sys
# XXX: Hack temporaire, permettant de préférer la version locale de sympy.
path = abspath(dirname(realpath(sys._getframe().f_code.co_filename)))
sys.path.insert(0, path)

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
    ##from . import GUI # initialisation de la version de sip
    from .geolib import *
