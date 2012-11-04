# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

#    WxGeometrie
#    Dynamic geometry, graph plotter, and more for french mathematic teachers.
#    Copyright (C) 2005-2012  Nicolas Pourcelot
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


import optparse

from .version import NOMPROG2, version
nomprog = NOMPROG2.lower()

# FIXME : supprimer la dépendance à param.
# Par exemple, parser un fichier VERSION contenant simplement
# `nom_prog version num_version`

# with open('VERSION') as f:
#     txt = f.read(10000)
#     m = re.match('(?P<nom>[^ ]+) version (?P<version>[^ ]+) [(](?P<date>[^ ]+)[)]', txt)
#     nom =
#     NOMPROG2, version = .split(' version ')

def gerer_arguments():
    u"""On récupère les options éventuelles passées au programme.

    -a ou --all : essaie de détecter tous les modules possibles pour les intégrer au démarrage
    ex: python wxgeometrie.pyw --all monfichier1.geo monfichier2.geo

    -p ou --param ou --parametres : modifier le contenu du module 'param'. Les parametres sont séparés par des points-virgules.
    ex: python wxgeometrie.pyw --param version='0.1';tolerance=0.01 monfichier1.geo monfichier2.geo

    -d ou --defaut : ne pas charger les préférences"""

    parametres_additionnels = {}

    parser = optparse.OptionParser(prog = NOMPROG2, usage = "usage: %prog [options] [fichiers...]",
                                   version = "%prog " + version,
                                   description = NOMPROG2 + """ est un logiciel de mathematiques de niveau lycee.
                                                    Il permet notamment de faire de la geometrie dynamique et du calcul formel.""")
    parser.add_option("-a", "--all", action = "store_true", help="detecter tous les modules presents et les integrer au demarrage")
    parser.add_option("-m", "--modules", help="specifier les modules a charger. ex: %s -m traceur,calculatrice" %nomprog)
    parser.add_option("-l", "--lister-modules", action = "store_true", help="affiche la liste des modules disponibles.")
    parser.add_option("-d", "--defaut", action = "store_true", help="utiliser les parametres par defaut, sans tenir compte des preferences")
    parser.add_option("-n", "--nouveau", action = "store_true", help="ouvrir une nouvelle session vierge")
    parser.add_option("-b", "--debug", action = "store_true", help="afficher les eventuels messages d'erreurs lors de l'execution")
    parser.add_option("--nodebug", action = "store_true", help="ne pas afficher les messages d'erreurs lors de l'execution")
    parser.add_option("-w", "--warning", action = "store_true", help="afficher les eventuels avertissements lors de l'execution")
    parser.add_option("--nowarning", action = "store_true", help="ne pas afficher les avertissements lors de l'execution")
    parser.add_option("-p", "--parametres", help="modifier les parametres. ex: %s -p 'tolerance=0.001;version=\"1.0\"'" %nomprog)
    parser.add_option("-r", "--recompile", action = "store_true", help="supprimer recursivement tous les fichiers .pyc, pour obliger python a recompiler tous les fichiers sources au demarrage.")
    parser.add_option("-s", "--script", action = "store_true", help="passer en mode script (ie. sans interface graphique). Ex: %s -s -i mon_script.txt -o mon_image.png" %nomprog)
    parser.add_option("-i", "--input", help="(mode script) fichier contenant le script de construction de figure, ou fichier .geo.")
    parser.add_option("-o", "--output", help="(mode script) fichier image. L'extension determine le type de fichier.")

# parser.set_defaults()

    (options, args) = parser.parse_args()

    if options.defaut:
        param.charger_preferences = False

    if options.lister_modules:
        print(u"\nListe des modules détectés :\n----------------------------")
        print '  '.join(param.modules)
        exit()

    if options.modules:
        # Les séparateurs acceptés entre les noms de modules sont , et ;
        if ',' in options.modules:
            a_activer = options.modules.split(',')
        else:
            a_activer = options.modules.split(';')
        parametres_additionnels["modules_actifs"] = dict((module, (module in a_activer)) for module in param.modules)

    if options.all:
        parametres_additionnels["modules_actifs"] = dict.fromkeys(param.modules, True)

    if options.debug:
        parametres_additionnels["debug"] = True

    if options.nodebug:
        parametres_additionnels["debug"] = False

    if options.warning:
        parametres_additionnels["warning"] = True

    if options.nowarning:
        parametres_additionnels["warning"] = False

    if options.parametres:
        for parametre in options.parametres.split(";"):
            try:
                nom, valeur = parametre.split("=", 1)
                parametres_additionnels[nom] = eval(valeur) # pas sensass question sécurité... :-( (?)
            except Exception:
                #raise
                print "Erreur: Parametre incorrect :", parametre
                print sys.exc_info()[0].__name__, ": ", sys.exc_info()[1]

    if options.recompile:
        for root, dirs, files in os.walk(os.getcwdu()):
            for file in files:
                if file.endswith(".pyc"):
                    os.remove(os.path.join(root,file))

    if (options.input or options.output) and not options.script:
        print("Warning: options --input et --output incorrectes en dehors du mode script.\n"
              "Exemple d'utilisation correcte : %s -s -i mon_script.txt -o mon_image.png." %nomprog)

    arguments = []

    # Sous les Unix-like, les espaces dans les noms de fichiers sont mal gérés par python semble-t-il.
    # Par exemple, "mon fichier.geo" est coupé en "mon" et "fichier.geo"
    complet = True
    for arg in args:
        if complet:
            arguments.append(arg)
        else:
            arguments[-1] += " " + arg
        complet = arg.endswith(".geo") or arg.endswith(".geoz")

    for nom in parametres_additionnels:
        if not hasattr(param, nom):
            print(u"Attention: Paramètre inconnu : " + nom)

    return parametres_additionnels, arguments, options
