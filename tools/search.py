#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##--------------------------------------##
#              WxGeometrie               #
#        Global search utility           #
##--------------------------------------##
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


import os
import sys
import re
import subprocess

# ----- User config -----
IGNORE = ('*tmp_*', '*(OLD|BAZAR)*', '*sympy/*', '*modules/traceur/tableau.py',
          '*/(pyshell|idle).pyw')
DEFAULT_EDITOR = 'geany'
# XXX: move this outside the script
# ------------------------

#TODO: provide default IGNORE by autodetecting .gitignore content, if any.

IGNORE_RE = re.compile('|'.join('(%s)' % pattern.replace('*', '.*').strip()
                                 for pattern in IGNORE if pattern))
SUPPORTED_EDITORS = ('geany', 'gedit', 'nano', 'vim', 'emacs', 'kate', 'kile')

def gs(chaine='', case=True, exclude_comments=True, extensions=(".py", ".pyw"),
        maximum=100, codec="utf8", statistiques=False, replace=None,
        color=None, edit_with=None, edit_result=None, skip_ignore=False):
    """Parcourt le répertoire courant et les sous-répertoire, à la recherche
    des fichiers dont l'extension est comprise dans 'extensions',
    mais passe les répertoires et les fichiers dont le nom commence par
    un préfixe de 'exclude_prefixe', ou finit par un suffixe de
    'exclude_suffixe'.
    Pour chaque fichier trouvé, renvoie toutes les lignes où 'chaine' se trouve.
    (Par défaut, la casse est prise en compte, sinon, il suffit de modifier
    la valeur de 'case'.)
    Le nombre maximal de lignes renvoyées est fixé par 'maximum', afin d'éviter
    de saturer le système.
    Si ce nombre est dépassé (ie. toutes les occurences de 'chaine' ne sont pas
    affichées), la fonction renvoie False, sinon, True.
    """
    if color is None:
        color = sys.platform.startswith('linux')
    if color:
        def blue(s):
            return '\033[0;36m' + s + '\033[0m'
        def blue2(s):
            return '\033[1;36m' + s + '\033[0m'
        def red(s):
            return '\033[0;31m' + s + '\033[0m'
        def green(s):
            return '\033[0;32m' + s + '\033[0m'
        def green2(s):
            return '\033[1;32m' + s + '\033[0m'
        def yellow(s):
            return '\033[0;33m' + s + '\033[0m'
        def white(s):
            return '\033[1;37m' + s + '\033[0m'
    else:
        green = blue = white = blue2 = red = green2 = yellow = (lambda s:s)

    if not chaine:
        statistiques = True
    if not case:
        chaine = chaine.lower()
    if replace is not None:
        assert case
    cwd = os.getcwd()
    repertoires = os.walk(cwd)
    print ("Searching in " + green(cwd) + "...")
    end_root_pos = len(cwd) + 1
    print('')
    fichiers = []
    for root, dirs, files in repertoires:
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
    for filename in fichiers:
        if re.search(IGNORE_RE, filename) and not skip_ignore:
            continue
        F += 1
        correct_encoding = True
        with open(filename) as fichier:
            lignes = []
            results = []
            try:
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
                        # comment line
                        continue
                    if not case:
                        s = s.lower()
                    pos = s.find(chaine)
                    if pos != -1:
                        if exclude_comments:
                            substr = s[:pos]
                            if '#' in substr:
                                # test if the substring found was inside a comment
                                # at the end of the line.
                                # You have to be carefull, because `#` may be
                                # inside a string...
                                # TODO: handle triple quotes.
                                mode = None
                                for c in substr:
                                    if c in "'\"#":
                                        if mode is None:
                                            mode = c
                                            if c == '#':
                                                continue
                                        elif mode == c:
                                            mode = None
                                if mode == '#':
                                    # substring found inside a comment
                                    continue

                        occurences += 1
                        if replace is not None:
                            lignes[-1] = s.replace(chaine, replace)
                        s = s[:pos] + blue2(s[pos:pos+len(chaine)]) \
                                    + s[pos+len(chaine):]
                        results.append("   " + blue('(' + str(n_lignes + 1) + ')')
                                          + "  line " + white(str(n + 1))
                                          + ":   " + s)

                        if edit_with is not None and (edit_result is None
                                                    or edit_result == n_lignes + 1):
                            if edit_with not in SUPPORTED_EDITORS:
                                print(edit_with + ' is currently not supported.')
                                print('Supported editors : '
                                      + ','.join(SUPPORTED_EDITORS))
                            elif edit_with in ('geany', 'kate'):
                                command = '%s -l %s %s' % (edit_with, n + 1, filename)
                            elif edit_with in ('kile',):
                                command = '%s --line %s %s' % (edit_with, n + 1, filename)
                            else:
                                command = '%s +%s %s' % (edit_with, n + 1, filename)
                            subprocess.call(command, shell=True)

                        n_lignes += 1
                        if n_lignes > maximum:
                            return red("Maximum output exceeded...!")
            except UnicodeDecodeError:
                correct_encoding = False
                print(red("ERROR: Can't read %s, encoding isn't %s." % (f, sys.getdefaultencoding())))

        if correct_encoding and results:
            print(" \u2022 in " + green(filename[:end_root_pos])
                                 + green2(filename[end_root_pos:]))
            for result in results:
                print(result.rstrip())

            if replace is not None:
                with open(filename, 'w') as fichier:
                    for l in lignes:
                        fichier.write(l)

    if statistiques:
        # C - 20*F : on décompte les préambules de tous les fichiers
        return (blue(str(N) + " lignes de code\n")
                + str(C) + " lignes de commentaires (" + str(C - 20*F)
                + " hors licence)\n"
                + str(B) + " lignes vides\n"
                + str(F) + " fichiers")
    if replace is None:
        return blue("\n-> %s occurence(s) trouvée(s)." % occurences)
    else:
        return blue("%s occurence(s) de %s remplacée(s) par %s."
                    % (occurences, repr(chaine), repr(replace)))


def usage():
    "Affiche l'aide."
    print("""\n    === Usage ===\n
    - Rechercher la chaîne 'hello' dans le code (hors commentaires) :
        $ ./tools/search.py "hello"
    - Remplacer partout la chaîne 'hello' par la chaîne 'world':
        $ ./tools/search.py "hello" -r "world"
    - Editer le projet à l'endroit où la chaîne "hello world!" se trouve
        $ ./tools/search.py -e "hello world!"
    - Editer seulement la 5e occurence de "hello world!" dans le projet
        $ ./tools/search.py -e5 "hello world!"
    - Afficher des statistiques concernant le projet:
        $ ./tools/search.py -s
    - Retourner 1000 résultats au maximum au lieu de 100 (valeur par défaut):
        $ ./tools/search.py -m "hello world!"
    - Personnaliser le nombre maximum de résultats retournés:
        $ ./tools/search.py -m2500 "hello world!"
    - Inclure également dans les résultats les répertoires contenus dans
      la variable de configuration IGNORE (ne pas tenir compte de IGNORE).
        $ ./tools/search.py -k "hello world!"
    - Rechercher la chaîne 'hello' dans le code, y compris dans les commentaires :
        $ ./tools/search.py -a "hello"
        """)
    exit()


if __name__ == "__main__":
    args = sys.argv[1:]
    kw = {}
    if not args or args[0] in ('-h', '--help'):
        usage()
    if '-r' in args:
        i = args.index('-r')
        # L'argument suivant est la chaîne de substitution.
        if len(args) < i + 2:
            usage()
        kw['replace'] = args.pop(i + 1)
        args.pop(i) # on supprimer le '-r'
    if '-e' in args:
        args.remove('-e')
        kw['edit_with'] = DEFAULT_EDITOR
    else:
        for i, arg in enumerate(args):
            if arg.startswith('-e'):
                args.pop(i)
                break
        else:
            arg = None
        if arg is not None:
            arg = arg[2:].lstrip('=:')
            kw['edit_result'] = int(arg)
            kw['edit_with'] = DEFAULT_EDITOR

    for i, arg in enumerate(args):
        if arg.startswith('-x'):
            print('x')
            args.pop(i)
            break
    else:
        arg = None
    if arg is not None:
        arg = arg[2:].lstrip('=:')
        kw['extensions'] = arg.split(',')

    for i, arg in enumerate(args):
        if arg.startswith('-w'):
            args.pop(i)
            break
    else:
        arg = None
    if arg is not None:
        arg = arg[2:].lstrip('=:')
        kw['edit_with'] = arg

    if '-c' in args:
        args.remove('-c')
        kw['color'] = True
    if '-a' in args:
        args.remove('-a')
        kw['exclude_comments'] = False
    if '-k' in args:
        args.remove('-k')
        kw['skip_ignore'] = True
    if '-m' in args:
        args.remove('-m')
        kw['maximum'] = 1000
    else:
        for i, arg in enumerate(args):
            if arg.startswith('-m'):
                args.pop(i)
                break
        else:
            arg = None
        if arg is not None:
            arg = arg[2:].lstrip('=:')
            kw['maximum'] = int(arg)
    if '-s' in args:
        args.remove('-s')
        args.insert(0, '')
        kw['statistiques'] = True
    options = (arg.split('=', 1) for arg in args[1:])
    kw.update((key, eval(val)) for key, val in options)
    ##print kw
    title = "\n=== Recherche de %s ===\n" % repr(args[0])
    if sys.platform.startswith('linux'):
        title = '\033[1;37m' + title + '\033[0m'
    print(title)
    print(gs(args[0], **kw))
