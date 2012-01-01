#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------##
#              WxGeometrie               #
#        Global search utility           #
##--------------------------------------##
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


import os
import sys

def gs(chaine = '', case = True, exclude_comments = True, extensions = (".py", ".pyw"), exclude_prefixe = ("tmp_", "Copie"), exclude_suffixe = ("_OLD", "(copie)"), exclude_dir = ('sympy', 'tools', 'BAZAR', 'OLD'), maximum = 100, codec="latin1", statistiques = False, replace=None):
    u"""Parcourt le répertoire courant et les sous-répertoire, à la recherche des fichiers dont l'extension
    est comprise dans 'extensions', mais passe les répertoires et les fichiers dont le nom commence par un préfixe
    de 'exclude_prefixe', ou finit par un suffixe de 'exclude_suffixe'.
    Pour chaque fichier trouvé, renvoie toutes les lignes où 'chaine' se trouve.
    (Par défaut, la casse est prise en compte, sinon, il suffit de modifier la valeur de 'case'.)
    Le nombre maximal de lignes renvoyées est fixé par 'maximum', afin d'éviter de saturer le système.
    Si ce nombre est dépassé (ie. toutes les occurences de 'chaine' ne sont pas affichées), la fonction renvoie False, sinon, True.
    """
    if not chaine:
        statistiques = True
    if not case:
        chaine = chaine.lower()
    if replace is not None:
        assert case
    repertoires = os.walk(os.getcwd())
    fichiers = []
    for root, dirs, files in repertoires:
        #print root
        if any((os.sep + prefixe in root) for prefixe in exclude_prefixe):
            continue
        if any((os.sep + dir + os.sep) in root for dir in exclude_dir):
            continue
        if any(root.endswith(os.sep + dir) for dir in exclude_dir):
            continue
        if any(root.endswith(suffixe) for suffixe in exclude_suffixe):
            continue
        if any((suffixe + os.sep) in root for suffixe in exclude_suffixe):
            continue
        files = [f for f in files if not any(f.startswith(prefixe) for prefixe in exclude_prefixe) and not any(f.endswith(suffixe + extension) for suffixe in exclude_suffixe for extension in extensions)]
        files = [f for f in files if f[f.rfind("."):] in extensions]

        fichiers += [root + os.sep + f for f in files]
    # nombre de lignes de code au total
    N = 0
    # nombre de lignes de commentaires au total
    C = 0
    # nombre de fichiers
    F = 0
    # nombre de lignes vides
    B = 0
    # nombre de lignes contenant l'expression recherchée
    n_lignes = 0
    # Nombre d'occurences trouvées.
    occurences = 0
    for f in fichiers:
        F += 1
        with open(f, "r") as fichier:
            lignes = []
            found = False
            for n, s in enumerate(fichier):
                if replace is not None:
                    lignes.append(s)
                if statistiques:
                    s = s.strip()
                    if s:
                        if s[0] != '#':
                            N += 1
                        elif s.strip('#'):
                            C += 1
                        else:
                            B += 1
                    else:
                        B += 1
                    continue
                if (exclude_comments and s.lstrip().startswith("#")):
                    continue
                if not case:
                    s = s.lower()
                if s.find(chaine) != -1:
                    found = True
                    occurences += 1
                    if replace is not None:
                        lignes[-1] = s.replace(chaine, replace)
                    print u"in %s " %f
                    print u"line " + unicode(n + 1) + ":   " + s.decode(codec)
                    n_lignes += 1
                    if n_lignes > maximum:
                        print "Maximum output exceeded...!"
                        return False
        if replace is not None and found:
            with open(f, 'w') as fichier:
                for l in lignes:
                    fichier.write(l)

    if statistiques:
        # C - 20*F : on décompte les préambules de tous les fichiers
        return str(N) + " lignes de code\n" + str(C) + " lignes de commentaires (" + str(C - 20*F) + " hors licence)\n" + str(B) + " lignes vides\n" + str(F) + " fichiers"
    if replace is None:
        return u"%s occurence(s) trouvée(s)." %occurences
    else:
        return u"%s occurence(s) de %s remplacée(s) par %s." %(occurences, repr(chaine), repr(replace))


def gr(chaine, chaine_bis, exceptions = (), extensions = (".py", ".pyw"), fake=True):
    u"""Remplace 'chaine' par 'chaine_bis' dans tous les fichiers dont l'extension (.txt, .bat, ...)
    est comprise dans 'extensions', et n'est pas comprise dans 'exceptions'.

    Deprecated. Use gs() instead.
    """
    y = yes = True
    n = no = False
    txt_exceptions = ("but " + ", ".join(exceptions) + " " if exceptions else "")
    b = input("Warning: Replace string '%s' by string '%s' in ALL files %s[y/n] ?" %(chaine, chaine_bis, txt_exceptions))
    if b is not True:
        return "Nothing done."
    repertoires=os.walk(os.getcwd())
    fichiers = []
    for r in repertoires:
        fichiers += [r[0] + os.sep + f for f in r[2] if f[f.rfind("."):] in extensions and f not in exceptions]
    n_lignes = 0
    occurences = 0 # nombre de remplacements effectués
    for f in fichiers:
        fichier = open(f, "r")
        s = fichier.read()
        fichier.close()
        k = s.count(chaine)
        occurences += k
        if k and not fake:
            fichier = open(f, "w")
            s = fichier.write(s.replace(chaine, chaine_bis))
            fichier.close()
    return u"%s remplacement(s) effectué(s)." %occurences


def usage():
    print u"""\n    === Usage ===\n
    - Rechercher la chaîne 'hello' dans le code :
        $ ./tools/search.py "hello"
    - Remplacer partout la chaîne 'hello' par la chaîne 'world':
        $ ./tools/search.py -r "hello" "world"
        """
    exit()


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        usage()
    if args[0] == '-r':
        if len(args) < 3:
            usage()
        print gr(args[1], args[2])
    else:
        print "\n=== Recherche de %s ===\n" %repr(args[0])
        print gs(args[0])
