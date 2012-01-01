# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##########################################################################
#
#                       Gestion de la securite
#
##########################################################################
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

import keyword, re, types
import math # pour avoir droit aux fonctions mathematiques dans eval_restricted par defaut.
import random as module_random# idem

from ..pylib import advanced_split
from .. import param


def _avertissement(*arg, **kw): print u"Instruction interdite en mode securisé."
#fonctions_interdites = ["eval", "compile", "execfile", "file", "open", "write", "getattr", "setattr"]

liste_blanche = set(('False', 'None', 'True', 'abs', 'all', 'any', 'basestring', 'bool',  'callable', 'chr', 'close', \
            'cmp', 'coerce', 'complex', 'dict', 'divmod', 'enumerate', 'filter', 'float', 'frozenset', 'globals', 'hash', 'hex', \
            'id', 'int', 'isinstance', 'issubclass', 'iter', 'len', 'list', 'locals', 'long', 'map', 'max', 'min', 'object', 'oct', \
            'ord', 'pow', 'range', 'reduce', 'repr', 'reversed', 'round', 'set', 'slice', 'sorted', 'str', 'sum', \
            'tuple', 'type', 'unichr', 'unicode', 'xrange', 'zip'\
            'IndexError', 'SyntaxError', 'NameError', 'StandardError', 'UnicodeDecodeError', 'RuntimeWarning', \
            'Warning', 'FloatingPointError', 'FutureWarning', 'ImportWarning', 'TypeError', 'KeyboardInterrupt', \
            'UserWarning', 'SystemError', 'BaseException', 'RuntimeError', 'GeneratorExit', 'StopIteration', \
            'LookupError', 'UnicodeError', 'IndentationError', 'Exception', 'UnicodeTranslateError', 'UnicodeEncodeError', \
            'PendingDeprecationWarning', 'ArithmeticError', 'MemoryError', 'ImportError', 'KeyError', 'SyntaxWarning', \
            'EnvironmentError', 'OSError', 'DeprecationWarning', 'UnicodeWarning', 'ValueError', 'NotImplemented', \
            'TabError', 'ZeroDivisionError', 'ReferenceError', 'AssertionError', 'UnboundLocalError', 'NotImplementedError', \
            'AttributeError', 'OverflowError', 'WindowsError'))

liste_noire = set(__builtins__.keys())
liste_noire.difference_update(liste_blanche)

dictionnaire_builtins = {}.fromkeys(list(liste_noire), _avertissement)
dictionnaire_modules = {}.fromkeys([key for key, objet in globals().items() if type(objet) == types.ModuleType])

ajouts_math = {"pi": math.pi, "e": math.e, "i": 1j}
for key, obj in math.__dict__.items():
    if type(obj) == types.BuiltinFunctionType:
        ajouts_math[key] = obj

for key, obj in module_random.__dict__.items():
    if type(obj) == types.BuiltinFunctionType:
        ajouts_math[key] = obj

##keywords = ('and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'exec', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'not', 'or', 'pass', 'print', 'raise', 'return', 'try', 'while', 'with', 'yield')

### mots clés qui peuvent être utilisés
##keywords_autorises = set('and', 'assert', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'if', 'in', 'is', 'lambda', 'not', 'or', 'pass', 'print', 'raise', 'return', 'try', 'while', 'with', 'yield')

keywords = set(keyword.kwlist)

# mots clés dont il faut s'assurer qu'ils ne puissent PAS être utilisés
keywords_interdits = set(('exec', 'global', 'import')) # attention à global !

# mots clés qui peuvent être utilisés
keywords_autorises = keywords.difference(keywords_interdits)

### ici, il s'agit de mots clés qui doivent rester en début de ligne
### (plus précisément, il est impossible de rajouter devant une affectation, style 'variable = ').
##keywords_debut_ligne = ('break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'exec', 'finally', 'pass', 'for', 'if', 'print', 'raise', 'return', 'try', 'while', 'with', 'yield')

# Mots clés devant lesquels il est possible de rajouter une affectation, style 'variable = ...'.
keywords_affectables = set(('lambda', 'not'))
# Mots clés qui ne sont jamais en début de ligne.
keywords_milieu = set(('or', 'and', 'as', 'in'))
# Les autres, qui doivent rester en tête de ligne.
keywords_non_affectables = keywords.difference(keywords_affectables).difference(keywords_milieu)

def keywords_interdits_presents(chaine):
    return bool(re.search(r'(?<!\w)(' + '|'.join(keywords_interdits) + ')(?!\w)', chaine))

def expression_affectable(chaine):
    return not bool(re.match('[ ]*(' + '|'.join(keywords_non_affectables) + ')', chaine))


# Exemple d'usage :
# dico = {"pi":3.1415926535897931, "e":2.7182818284590451}    # dictionnaire local
# dico.update(securite.dictionnaire_builtins)
# exec(string, dico)

def eval_restricted(s, dico_perso = None):
    u"""eval_restricted(s) évalue s dans un contexte vierge et sécurisé.

    Toutes les fonctions disponibles par défaut sont filtrées.
    L'évalution de chaînes unicodes se fait en utilisant l'encodage système, et non l'utf8.

    Note: eval_restricted est le plus securisée possible, mais contrairement
    à eval_safe, il utilise la fonction eval ; il peut donc y avoir des failles
    de sécurité. Merci de m'en informer.
    """
    dico = {"rand": module_random.random}
    dico.update(dictionnaire_builtins) # supprime certaines fonctions par defaut (en les redefinissant)
    dico.update(ajouts_math) # ajoute les fonctions mathematiques usuelles
    if dico_perso is not None:
        dico.update(dico_perso)
    for module in ("os", "sys", "securite"):
        dico.pop(module, None)
    if isinstance(s, unicode):
        s = s.encode(param.encodage)
    return eval(s, dico)


def eval_safe(s):
    u"""eval_safe(repr(x)) retourne x pour les types les plus usuels
    (int, long, str, unicode, float, bool, None, list, tuple, dict.)
    Mais aucune évaluation n'est faite, ce qui évite d'éxécuter un code dangereux.
    Le type de s est detecté, et la transformation appropriée appliquée.

    NB1: eval_safe n'est pas destiné à remplacer eval :
    - il est relativement lent,
    - le nombre de types supportés est volontairement réduit,
    - il n'est pas souple (eval_safe("2-3") renvoie une erreur).
    La fonction eval_safe est orientée uniquement securité.

    NB2: eval_safe est récursif (il peut lire des listes de tuples de ...).

    NB3: eval_safe est parfaitement securisé, car il ne fait (presque) jamais appel à une instruction eval.
    Contrairement à la fonction eval_restricted, qui est 'probablement' securisée."""

    s = s.strip()

    def filtre(chaine, caracteres):
        return re.match("^[%s]*$" %caracteres, chaine) is not None



    if filtre(s, "-0-9") or s[-1] == "L":   # entier
        return int(s)

    if filtre(s, "-+.e0-9"):    # flottant
        return float(s)

    if len(s) > 1 and s[0] == s[-1] and s[0] in ("'", '"'):    # chaine
        # s est évalué dans un contexte parfaitement vierge.
        return eval(s, {"__builtins__": None}, {"__builtins__": None})

    if len(s) > 2 and s[0] == "u" and s[1] == s[-1] and s[1] in ("'", '"'): #unicode
        return eval(s, {"__builtins__": None}, {"__builtins__": None}) # idem

    if s == "None":
        return None

    if s == "True":
        # Eviter return eval(s), car True peut etre redefini. Exemple : True = False (!)
        return True

    if s == "False":
        return False

    if s[0] in ("(", "["):  # tuple ou liste
        liste = [eval_safe(t) for t in advanced_split(s[1:-1], ",") if t]
        if s[0] == "(":
            liste = tuple(liste)
        return liste

    if s[0] == "{":     # dictionnaire
        dict = {}
        liste = [advanced_split(t, ":") for t in advanced_split(s[1:-1], ",") if t]
        for key, val in liste:
            dict[eval_safe(key)] = eval_safe(val)
        return dict


    raise TypeError, "types int, str, float, bool, ou None requis (ou liste ou tuple de ces types)"
