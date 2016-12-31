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
import argparse

# ----- User config -----
IGNORE = ('*tmp_*', '*(OLD|BAZAR)*', '*sympy/*', '*modules/traceur/tableau.py',
          '*/(pyshell|idle).pyw', '*/rpdb2.py')
DEFAULT_EDITOR = 'geany'
# XXX: move this outside the script
# ------------------------

#TODO: provide default IGNORE by autodetecting .gitignore content, if any.

SUPPORTED_EDITORS = ('geany', 'gedit', 'nano', 'vim', 'emacs', 'kate', 'kile')

def gs(string='', case=True, include_comments=False, comment_marker='#', extensions=(".py", ".pyw"),
        maximum=100, codec="utf8", stats=False, replace_with=None,
        color=None, edit_with=None, edit_result=None, skip_paths=()):
    """Parcourt le répertoire courant et les sous-répertoire, à la recherche
    des fichiers dont l'extension est comprise dans 'extensions',
    mais passe les répertoires et les fichiers dont le nom commence par
    un préfixe de 'exclude_prefixe', ou finit par un suffixe de
    'exclude_suffixe'.
    Pour chaque fichier trouvé, renvoie toutes les lignes où 'string' se trouve.
    (Par défaut, la casse est prise en compte, sinon, il suffit de modifier
    la valeur de 'case'.)
    Le nombre maximal de lignes renvoyées est fixé par 'maximum', afin d'éviter
    de saturer le système.
    Si ce nombre est dépassé (ie. toutes les occurences de 'string' ne sont pas
    affichées), la fonction renvoie False, sinon, True.
    """

    if skip_paths:
        IGNORE_RE = re.compile('|'.join('(%s)' % pattern.replace('*', '.*').strip()
                                 for pattern in skip_paths if pattern))
    else:
        IGNORE_RE = None


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

    if not string:
        stats = True
    if not case:
        string = string.lower()
    if replace_with is not None:
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
        if IGNORE_RE is not None and re.search(IGNORE_RE, filename):
            continue
        F += 1
        correct_encoding = True
        with open(filename) as fichier:
            lignes = []
            results = []
            try:
                for n, s in enumerate(fichier):
                    if replace_with is not None:
                        lignes.append(s)
                    if stats:
                        s = s.strip()
                        if s:
                            if s[0] != comment_marker:
                                N += 1
                            elif s.strip(comment_marker):
                                C += 1
                            else:
                                B += 1
                        else:
                            B += 1
                        continue
                    if not include_comments and s.lstrip().startswith(comment_marker):
                        # comment line
                        continue
                    if not case:
                        s = s.lower()
                    pos = s.find(string)
                    if pos != -1:
                        if not include_comments:
                            substr = s[:pos]
                            if comment_marker in substr:
                                # test if the substring found was inside a comment
                                # at the end of the line.
                                # You have to be carefull, because `comment_marker` may be
                                # inside a string...
                                # TODO: handle triple quotes.
                                mode = None
                                for c in substr:
                                    if c in ("'", '"', comment_marker):
                                        if mode is None:
                                            mode = c
                                            if c == comment_marker:
                                                continue
                                        elif mode == c:
                                            mode = None
                                if mode == comment_marker:
                                    # substring found inside a comment
                                    continue

                        occurences += 1
                        if replace_with is not None:
                            lignes[-1] = s.replace(string, replace)
                        s = s[:pos] + blue2(s[pos:pos+len(string)]) \
                                    + s[pos+len(string):]
                        results.append("   " + blue('(' + str(n_lignes + 1) + ')')
                                          + "  line " + white(str(n + 1))
                                          + ":   " + s)

                        if edit_with is not None and (edit_result == ()
                                                    or ((n_lignes + 1) in edit_result)):
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
                print(red("ERROR:") + " Can't read %s, encoding isn't %s." % (filename, sys.getdefaultencoding()))

        if correct_encoding and results:
            print(" \u2022 in " + green(filename[:end_root_pos])
                                 + green2(filename[end_root_pos:]))
            for result in results:
                print(result.rstrip())

            if replace_with is not None:
                with open(filename, 'w') as fichier:
                    for l in lignes:
                        fichier.write(l)

    if stats:
        # C - 20*F : on décompte les préambules de tous les fichiers
        return (blue(str(N) + " lignes de code\n")
                + str(C) + " lignes de commentaires (" + str(C - 20*F)
                + " hors licence)\n"
                + str(B) + " lignes vides\n"
                + str(F) + " fichiers")
    if replace_with is None:
        return blue("\n-> %s occurence(s) trouvée(s)." % occurences)
    else:
        return blue("%s occurence(s) de %s remplacée(s) par %s."
                    % (occurences, repr(string), repr(replace_with)))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS,
            description='Search recursively for specified string in all the files of a directory.')
    parser.add_argument('string', metavar='STRING', help='string to search')
    parser.add_argument('-r', '--replace-with', metavar='REPLACEMENT_STRING',
                        help='Replace all occurrences of STRING with REPLACEMENT_STRING.')
    parser.add_argument('-e', '--edit-result', metavar='N', type=int, nargs='*',
                help='''Open editor and display result number N
                         (use --edit with no argument to
                        open all files where searched string was found).''')
    parser.add_argument('-w', '--edit-with', metavar='EDITOR', choices=SUPPORTED_EDITORS)
    parser.add_argument('-s', '--stats', help='Display statistics concerning scanned files.')
    parser.add_argument('-m', '--maximum', type=int, metavar='N', default=100,
                        help='Display only the first N results.')
    parser.add_argument('-i', '--include-comments', action='store_true',
                        help='Search in comments too.')
    parser.add_argument('-x', '--extensions', metavar='EXTENSION', nargs='+', default=('.py', '.pyw'),
                        help='Search only files whose name ends with any specified extension.')
    parser.add_argument('-n', '--no-color', dest='color', action='store_false', help='Disable colors.')
    parser.add_argument('-k', '--skip-paths', metavar='PATH_TO_SKIP', nargs='*', default=IGNORE, help='Paths to skip.')
    parser.add_argument('-c', '--discard-case', dest='case', action='store_false', help='Make search case insensitive.')
    args = parser.parse_args()

    title = "\n=== Recherche de %s ===\n" % repr(args.string)
    if sys.platform.startswith('linux'):
        title = '\033[1;37m' + title + '\033[0m'
    print(title)
    #~ print(vars(args))
    print(gs(**vars(args)))
