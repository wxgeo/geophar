# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

######################################
#
#    FICHIER DE CONFIGURATION
#
######################################
#
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
#
######################################

# Note :
# eviter d'utiliser des listes au maximum, preferer les tuples.
# en effet, il est souvent utile de copier les parametres.
# Mais par defaut, une liste n'est pas reellement copiee (il faut faire l2 = l1[:]).
# Si de plus, on utilise des listes de listes, on a vite fait d'obtenir des bugs etranges...

from locale import getdefaultlocale
from math import pi

python_min = (2, 6) # version minimale requise

# debuguage (affichage des erreurs + diverses infos)
debug = True
# Le logiciel est-il installé ?
# Cela change les répertoires par défaut (session, etc.)
install = False
# affichage ou non des avertissements
warning = debug
verbose = 1 # 0, 1, 2 ou 3
# À terme, verbose=0 doit couper *tous* les messages (pour ne pas parasiter les tests).
# => créer une fonction print() personnalisée.
# Indique si geolib doit afficher les différents messages. Dans certaines consoles (ex: pyshell), cela provoque des comportements indésirables.
afficher_messages = True
#TODO: retravailler ces différents paramètres.

fermeture_instantanee = False # Utile en mode développement

# affichage de la ligne de commande (utile pour le développement)
ligne_commande = debug

NOMPROG = u"WxGéométrie"
NOMPROG2 = 'WxGeometrie' # sans accent
GUIlib = 'wx'

version_wxpython = "2.8-unicode"

# Les valeurs sont les noms des paquets sous Debian/Ubuntu.
dependances = {'wx': 'python-wxgtk2.8', 'matplotlib': 'python-matplotlib', 'numpy': 'python-numpy'}

latex = False
latex_unicode = True # (sera éventuellement désactivé ultérieurement, après l'import de wx)

moteur_de_rendu = 'WXAgg' # ou 'Wx' pour supprimer l'anti-crénêlage


# jeu de caractère à utiliser
encodage = getdefaultlocale()[1] or "utf8"

# Utiliser pysco si disponible (JIT compiler qui accélère le code python)
# True -> tout compiler : psyco.full()
# None -> compilation optimisée : psyco.profile()
# False -> ne pas essayer d'importer psyco
charger_psyco = False

# Modules activés par défaut
modules_par_defaut = (
    "geometre",
    "traceur",
    "statistiques",
    "calculatrice",
    "probabilites",
    "surfaces",
        )

# Multi-threading pour les macros
# -------------------------------

multi_threading = False

# c'est assez instable...

if multi_threading is None:
    multi_threading = (plateforme == 'Windows') # ca ne marche pas avec le serveur X (sous Linux par ex.)


# Paramètres généraux
# --------------------

utilisateur = "" # nom de l'utilisateur, pour inclure dans les documents créés

dimensions_fenetre = (890, 630)
confirmer_quitter = True
nbr_annulations = 50
# Créer un fichier .log (conseillé)
historique_log = True
# Modifier ce fichier en temps réel (peu utile)
historique_log_continu = False
# Enregistrer les messages (notamment d'erreur) dans messages.log
enregistrer_messages = True
# Sauver les préférences à la fermeture du programme, pour les restaurer au prochain démarrage
sauver_preferences = True
# Sauver la session en cours à la fermeture du programme, pour la restaurer au prochain démarrage
sauver_session = True
# Paramètre utilisé essentiellement en interne (quand on lance WxGéometrie avec l'option --defaut)
charger_preferences = True

# Intervalle de temps (en dizaines de secondes) entre 2 sauvegardes automatiques
sauvegarde_automatique = 2
# (Mettre 0 pour la désactiver)

tolerance = 1e-8 # seuil de tolérance, utilisé en particulier par geolib pour savoir si 2 points sont confondus
# ce paramètre permet un compromis acceptable entre les faux negatifs
# (2 points confondus considérés à tort comme distincts, du fait d'imprécisions de calculs qui se cumulent)
# et les faux positifs (deux points proches considerés à tort comme confondus).

# Parametres d'affichage
# ----------------------

orthonorme = False
grille_aimantee = False # force les points à se placer sur le quadrillage

afficher_barre_outils = False
afficher_console_geolib = False
afficher_boutons = True  # Possibilité de ne pas afficher les boutons, pour obliger à une construction pas à pas.

zoom_texte = 1
zoom_ligne = 1

#bouger_curseur = None

#if bouger_curseur is None:
#    bouger_curseur = (platform.system() in ('Windows', 'Linux'))

#constantes
RIEN = 0
NOM = 1
TEXTE = 2
FORMULE = 3
DEBUT = 0
MILIEU = 0.5
FIN = 1
#TODO: supprimer cette section une fois qu'une partie de param sera directement intégrée à geolib.

# Styles liés à la catégorie:
styles_de_lignes = ['-', '--', '-.', ':', 'None']
styles_de_points = ['+', 'x', 'o', '.', ',', '1', '2', '3', '4', '<', '>', '^', 'v', 'D', 'H', '_', '|', 'd', 'h', 'p', 's']
styles_de_textes = ["normal", "italic", "oblique"]
styles_de_angles = ['-', '--', '-.', ':', 'steps', 'None']
familles_de_textes = ["sans-serif", "serif", "cursive", "fantasy", "monospace"]
codage_des_lignes = ['', '/', '//', '///', 'x', 'o']
codage_des_angles = ['', '^', ')', '))', ')))', '|', '||', 'x', 'o']

# Enumère les styles 'variables' :
# - soit parce qu'ils ont des significations assez différentes selon les objets
# - soit parce qu'ils ne peuvent pas prendre les mêmes valeurs suivant les objets
# Ces styles ne seront copiés d'un objet à l'autre que s'ils appartiennent à la même catégorie
styles_a_signification_variable = ("style", "codage", "famille", "taille", "angle")

# Ces styles ne seront pas copiés, quelque soit la catégorie de la cible
styles_a_ne_pas_copier = ("categorie", "niveau", "trace", "fixe", "label", "_rayon_", "_k_", "_angle_", "_noms_", "legende")


types_de_hachures = [' ', '/', '//', '\\', '\\\\', '|', '-', '+', 'x', 'o', 'O', '.', '..', '*']
# en réalité, on peut aussi les panacher...


defaut_objets = {
    "legende": RIEN,
    "visible": True,
    "label": "",
    "niveau": 0,
    }
widgets = {"bidon":1,
    }
variables = {
    "visible": False,
    }
points = {
    "couleur": "b",
    "epaisseur": 1.,
    "style": "+",
    "categorie": "points",
    "taille": 8,
    "visible": True,
    "legende": NOM,
    "niveau": 6,
    "trace": False,
    }
points_deplacables = {
    "couleur": "r",
    "niveau": 10,
    "fixe": False,
    }
segments = {
    "couleur": "g",
    "epaisseur": 1.,
    "style": "-",
    "visible": True,
    "niveau": 3,
    "categorie": "lignes",
    "codage": codage_des_lignes[0],
    }
interpolations = {
    "couleur": "g",
    "epaisseur": 1.,
    "style": "-",
    "visible": True,
    "niveau": 3,
    "categorie": "lignes",
    "codage": codage_des_lignes[0],
    "debut": True,
    "fin": True,
    }
droites = {"couleur": "b",
    "epaisseur": 1.,
    "style": "-",
    "visible": True,
    "niveau": 2,
    "categorie": "lignes",
    }
courbes = {"couleur": "b",
    "epaisseur": 1.,
    "style": "-",
    "visible": True,
    "niveau": 2,
    "categorie": "lignes",
    "extremites": True,
    "extremites_cachees": (),
    }
vecteurs = {
    "couleur": "g",
    "epaisseur": 1.,
    "style": "-",
    "taille": 10,
    "visible": True,
    "niveau": 4,
    "categorie": "lignes",
    "angle": 60,
    "position": FIN,
    "double_fleche": False,
    }
axes = {
    "couleur": "k",
    "epaisseur": 1.,
    "style": "-",
    "taille": 10,
    "visible": True,
    "niveau": .1,
    "categorie": "lignes",
    "angle": 60,
    "position": FIN,
    "double_fleche": False,
    }
cercles = {
    "couleur": "b",
    "epaisseur": 1.,
    "style": "-",
    "visible": True,
    "niveau": 1,
    "categorie": "lignes",
    }
arcs = {
    "couleur": "b",
    "epaisseur": 1.,
    "style": "-",
    "visible": True,
    "niveau": 1,
    "categorie": "lignes",
    "codage": codage_des_lignes[0],
    }
arcs_orientes = {
    "couleur": "g",
    "epaisseur": 1.,
    "style": "-",
    "taille": 10,
    "visible": True,
    "niveau": 4,
    "categorie": "lignes",
    "angle": 60,
    "position": FIN,
    "double_fleche": False,
    }
polygones = {
    "couleur": "y",
    "epaisseur": 1.,
    "style": "-",
    "visible": True,
    "alpha": .2,
    "niveau": 0.1,
    "hachures": types_de_hachures[0],
    "categorie": "lignes",
    }
cotes = {
    "couleur": "y",
    "epaisseur": 1.,
    "style": "-",
    "visible": True,
    "alpha": 1,
    "niveau": 0,
    "categorie": "lignes",
    "codage": codage_des_lignes[0],
    }
polyedres = {
    "couleur": "y",
    "epaisseur": 1.,
    "style": "None",
    "visible": True,
    "alpha": .2,
    "niveau": 0,
    "hachures": types_de_hachures[0],
    "categorie": "lignes",
    }
aretes = {
    "couleur": "y",
    "epaisseur": 1.,
    "style": "-",
    "visible": True,
    "niveau": 0.5,
    "categorie": "lignes",
    }
textes = {
    "couleur": "k",
    "epaisseur": 5, # 1 -> 9
    #"largeur": ("normal", "narrow", "condensed", "wide")[0],  # mal gere par matploltib (version 0.87)
    "taille": 18.,
    "style": "normal",
    "famille": familles_de_textes[1],
    "visible": True,
    "angle": 0,
    "legende": TEXTE,
    "fixe": False,
    "categorie": "textes",
    "niveau": 7,
    "alignement_vertical": "center",
    "alignement_horizontal": "center",
    "alpha": 1,
    }
boutons = {
    "couleur": 'k',
    "couleur_fond": (.3, .8, .9),
    "epaisseur": 1,
    "taille": 18.,
    "style": "italic",
    "visible": True,
    "angle": 0,
    "legende": TEXTE,
    "fixe": True,
    "categorie": "widgets",
    "niveau": 10,
    "alignement_vertical": "center",
    "alignement_horizontal": "center",
    "marge": 3,
    }
labels = {
    "couleur": "k",
    "epaisseur": 6, # 1 -> 9
    #"largeur": ("normal", "narrow", "condensed", "wide")[0],  # mal gere par matploltib (version 0.87)
    "taille": 18.,
    "style": "normal",
    "famille": familles_de_textes[1],
    "visible": True,
    "angle": 0,
    "legende": TEXTE,
    "fixe": False,
    "categorie": "textes",
    "niveau": 7,
    "alignement_vertical": "bottom",
    "alignement_horizontal": "left",
    }
angles = {
    "couleur": "b",
    "epaisseur": 1.,
    "style": "-",
    "visible": True,
    "niveau": 5,
    "categorie": "angles",
    "codage": codage_des_angles[0],
    "alpha": .2,
}

# le parametre niveau est utilisé pour détecter l'objet sur la feuille :
# en cas de conflit entre deux objets proches, il permet de savoir l'objet à sélectionner.
# les petits objets (points, ...) doivent être au dessus des plus gros, et avoir un niveau supérieur.
# Rq: les objets modifiables devraient etre "au dessus" des autres, indépendamment de leur taille.
# Attention, ce parametre n'influe pas sur l'affichage des objets (pour cela, c'est le parametre "zorder" de matplotlib)

# le parametre "categorie" indique quelle liste de styles est à appliquer.
# par défaut, on applique souvent 'styles_de_lignes'.

del NOM, FORMULE, TEXTE, RIEN, DEBUT, MILIEU, FIN



# Options de style pour les objets geometriques :
#   couleur:      str
#   epaisseur:    float
#   taille:       float
#   style:        str
#   visible:      bool
#   fixe:         bool
#   label:        str
#   extra:       dict
# 'extra' est un dictionnaire d'options de matplotlib
# attention, ces options seront appliquees a toutes les composantes (plot, fill, text) de la representation graphique

codage = {"angle": 60, "taille": 6, "rayon": 20}
codage_automatique_angle_droits = True


# taille de differents elements graphiques

taille = {"o" : 3, "(" : 5, ">" : 10, "|" : 8}


# Distance maximale entre une etiquette et son objet associé :
distance_max_etiquette = 50

# DÉSUET :
##chiffres_significatifs = 4 # intervient dans l'affichage des propriétés des objets essentiellement.

decimales = 2

# Note: en interne, ce sont toujours les radians qui sont utilisés.
unite_angle = ("r", "d", "g")[0] # radian, degré ou grad


liste_axes = (0, 1)
# 0 -> axe des abscisses ;  1 -> axe des ordonnees

afficher_axes = True
afficher_fleches = True # fleches au bout des axes.

# Pour se reperer, deux possibilites :
# 1. Un repere proprement dit
repere = ("O", "I", "J") # en majuscule, ce sont des points ; en minuscule, des vecteurs.
# 2. Deux axes gradues
origine_axes = (0, 0)
# Pour choisir le mode :
utiliser_repere = True
# -> utiliser ou non un repère (même origine sur chaque axe...)
# -> si on n'utilise pas le repère, on affiche deux valeurs distinctes à l'intersection des axes

gradu = (1, 1) # espacement entre deux graduations pour chaque axe. (0 => pas de graduations).
saturation =  0.3 # valeur de saturation pour le coefficient pas()/gradu
# au dela du coefficient de saturation, les graduations ne sont plus affichees
# cela evite de bloquer le programme...

# Nombre de cm pour une unité en export
echelle_cm = (1, 1)

# Couleur de fond des figures.
couleur_fond = "w"

afficher_quadrillage = True # affiche un quadrillage a la place des graduations
quadrillages = (((None, None), ":", .5, "k"),)
# Chaque couple correspond a un quadrillage.
# Le format est : ([espacement horizontal, espacement vertical], style, epaisseur, couleur).
# On peut omettre des elements :
# quadrillages = ((),)
# Si un espacement vaut None, la valeur de gradu correspondante sera utilisee.
# Valeurs possibles pour le style : (cf http://matplotlib.sourceforge.net/matplotlib.pylab.html#-plot)
# "--" tirets
# "-" lignes continues
# ":" points
# "-." alternance de points et de tirets
# On peut superposer plusieurs quadrillages :
# quadrillages = (((1, 1), "-", 0.25, "k"), ((0.25, 0.25), ":", .25, "k"),)
# ou encore :
# quadrillages = (((1, 1), ":", 1, "k"), ((0.2, 0.2), ":", .125, "k"),)
couleur_papier_millimetre = '#aa7733' # couleur à utiliser pour le papier millimétré entre autres

resolution = 1000 # resolution utilisee pour le tracage des courbes (plus la valeur est importante, plus la courbe est lisse)
fenetre = (origine_axes[0]-8, origine_axes[0]+8, origine_axes[1]-5, origine_axes[1]+5)   # xmin, xmax, ymin, ymax

zoom_in = 1.1 # coefficient d'agrandissement des objets lors d'un zoom.
zoom_out = 0.9 # coefficient de reduction des objets lors d'un zoom.

zoom_texte_in = 1.05
zoom_texte_out = 0.95

zoom_ligne_in = 1.07
zoom_ligne_out = 0.93

dpi_ecran = 80
# Tableau récapitulatif des résolutions les plus courantes :
# http://forum.notebookreview.com/notebook-dummy-guide-articles/124093-guide-screen-sizes-dots-per-inch-dpi.html

dpi_export = 200 # resolution utilisee lors de l'exportation des images
compresser_geo = False # compresser les fichiers .geo par défaut

afficher_coordonnees = True # affiche en permanence les coordonnees
afficher_pixels = False # pour débogage (mettre afficher_coordonnes à False précédemment)

afficher_objets_caches = False # affiche en grisé les objets masqués

precision_selection = 10 # plus la precision est importante, plus il faut etre pres d'un objet pour pouvoir le saisir
# Si le chiffre est trop petit, ca devient fastidieux de selectionner un objet
# A l'inverse, s'il est trop grand, il devient difficile de selectionner celui qu'on veut entre deux objets proches


nom_multiple = False # autorise à 'nommer' plusieurs objets avec le même nom
# (en fait, un seul objet aura le nom 'A' par exemple, les autres auront 'A' comme étiquette).

# ------------------------------
# Code à réécrire
# Tranformation linéaire appliquée au graphique : (EXPERIMENTAL !)
transformation = None
# Couple de la forme (a, b, c, d) tel que :
# |x'|     |a b| |x|
# |y'|  =  |c d| |y|
# Exemple (permutation des axes) :
#transformation = (0, 1, 1, 1)
# ------------------------------

afficher_barre_outils = False
afficher_console_geolib = False

# Tenter la virgule comme séparateur si le point a échoué, et vice-versa.
# (À désactiver pour faciliter le débogage.)
adapter_separateur = True



# Répertoires par défaut
# ----------------------

# Répertoire où on sauve les fichiers par défaut
rep_save = None
# rep_save = repertoire
# Répertoire où on ouvre les fichiers par défaut
rep_open = None
# rep_open = repertoire
# Répertoire où on exporte les fichiers par défaut
rep_export = None
# rep_export = repertoire


emplacements = {}

taille_max_log = 10000 # taille max du fichier de log (en Ko)

taille_max_log *= 1024


try:
    from .personnaliser import * # permet de générer un fichier personnaliser.py lors de l'installation, ou de la première utilisation, et dont les parametres remplaceront ceux-ci.
except ImportError:
    try:
        from .personnaliser_ import *
    except ImportError:
        pass

if install:
    # Les préférences, fichiers log, etc... sont stockés dans le dossier de l'utilisateur.
    # ~ se réfère au répertoire de l'utilisateur (ex: /home/BillG/ sous Linux, ou C:\Documents and Settings\LTorvald\ sous Windows)
    emplacements.setdefault("log", "~/.wxgeometrie/log")
    emplacements.setdefault("preferences", "~/.wxgeometrie/preferences")
    emplacements.setdefault("macros", "~/.wxgeometrie/macros")
    emplacements.setdefault("session", "~/.wxgeometrie/session")
else:
    # Utilisation sans installation. Tout est stocké directement dans le dossier wxgeometrie/.
    # % se réfère au dossier contenant WxGeometrie (indiqué par param.EMPLACEMENT)
    emplacements.setdefault("log", "%/log") # dans log/ par défaut
    emplacements.setdefault("preferences", "%/preferences") # dans preferences/ par défaut
    emplacements.setdefault("macros", "%/macros") # dans macros/ par défaut
    emplacements.setdefault("session", "%/session") # dans session/ par défaut

print(u'Import des paramètres terminé.')
