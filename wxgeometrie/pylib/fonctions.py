# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##########################################################################
#
#       Fonctions couramment utilisees, et non implementees en Python
#                     (...du moins, à ma connaissance !)
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


import re
import weakref
import sys, zlib
import os.path
import warnings, traceback, linecache

from .decorator import decorator

from .. import param # paramètres du programme
from sympy import sympify


def is_in(element, _list):
    u"""Teste si l'élement est dans la liste, en effectuant un test d'identité (is) et non d'égalité (==)."""
    test = False
    for elt in _list:
        if elt is element:
            test = True
            break
    return test

# This is 'a lot' slower (2.4 times about) :
##def isin2(element, _list):
##    u"""Teste si l'élement est dans la liste, en effectuant un test d'identité (is) et non d'égalité (==)."""
##    return id(element) in (id(elt) for elt in _list)

# And this too... (2 times about on python 2.5)
##def isin3(element, _list):
##    u"""Teste si l'élement est dans la liste, en effectuant un test d'identité (is) et non d'égalité (==)."""
##    return any(elt is element for elt in _list)

def mreplace(main_string, list_of_strings, new_string = ""):
    u"""Remplace, dans "main_string", toutes les sous-chaines de "list_of_strings", par la chaine "new_string"."""
    for old_string in list_of_strings:
        main_string = main_string.replace(old_string, new_string)
    return main_string

def recursive_replace(main_string, old_string, new_string = "", max_loops = 10000, max_len = 1000000):
    u"""Remplace, dans "main_string", la sous-chaîne "old_string" par "new_string", au besoin en plusieurs passes.

    En fin de processus, la sous-chaîne old_string ne subsiste plus dans la chaîne.
    Renvoie une erreur si le processus ne semble pas converger.
    (C'est en particulier le cas si old_string est strictement inclus dans new_string)

    La différence avec replace est claire sur cette exemple :
    >>> from pylib.fonctions import recursive_replace
    >>> "Hi HelloHello world world !".replace("Hello world", "")
    'Hi Hello world !'
    >>> recursive_replace("Hi HelloHello world world !", "Hello world", "")
    'Hi  !'

    Il y a un cas particulier ou la sous-chaîne reste présente :
    >>> recursive_replace("Hi HelloHello world world !", "Hello world", "Hello world")
    'Hi HelloHello world world !'
    """

    chaine = ""
    loops = 0
    while chaine <> main_string:
        loops += 1
        chaine = main_string
        main_string = main_string.replace(old_string, new_string)
        if loops > max_loops:
            raise RuntimeError, "Nombre de passes superieur au maximum autorise."
        if len(main_string) > max_len:
            raise OverflowError, "Taille de la chaine superieure au maximum autorise."
    return main_string


def recursive_mreplace(main_string, list_of_strings, new_string = "", max_loops = 10000, max_len = 1000000):
    u"""Remplace, dans "main_string", toutes les sous-chaines de "list_of_strings" par "new_string", au besoin en plusieurs passes.

    En fin de processus, la sous-chaîne old_string ne subsiste plus dans la chaîne.
    Renvoie une erreur si le processus ne semble pas converger.

    Voir également recursive_replace() et mreplace().

    Remarque: recursive_mreplace n'est pas équivalent des appels successifs de recursive_replace().
    >>> from pylib.fonctions import recursive_replace, recursive_mreplace
    >>> s = "tbtbaoao"
    >>> s = recursive_mreplace(s, ("to", "ba"))
    >>> s
    ''
    >>> s="tbtbaoao"
    >>> for i in ("to", "ba"):
    ...     s = recursive_replace(s, i)
    >>> s
    'tbtoao'
    """

    chaine = ""
    loops = 0
    while chaine <> main_string:
        loops += 1
        chaine = main_string
        main_string = mreplace(main_string, list_of_strings, new_string)
        if loops > max_loops:
            raise RuntimeError, "Nombre de passes superieur au maximum autorise."
        if len(main_string) > max_len:
            raise OverflowError, "Taille de la chaine superieure au maximum autorise."
    return main_string


def mfind(chaine, car):
    n = 0
    l = []
    while True:
        n = chaine.find(car, n)
        if n == -1: break
        l.append(n)
        n += 1
    return l



def msplit(main_string, list_of_separators):
    u"""Découpe la chaine "main_string", selon les séparateurs définis dans "list_of_separators"."""
    return mreplace(main_string, list_of_separators[1:], list_of_separators[0]).split(list_of_separators[0])



def removeend(main_string, *substrings):
    u"Enlève les éventuelles occurences de substring en fin de chaine."
    if substrings and True not in (sub == "" for sub in substrings): # pour éviter une éventuelle boucle infinie.
        test = True
        while test:
            for sub in substrings:
                if main_string.endswith(sub):
                    main_string =  main_string[:-len(sub)]
                    test = None
            if test is None:
                test = True
            else:
                test = False
    return main_string


def removestart(main_string, *substrings):
    u"Enlève les éventuelles occurences de substring en début de chaine."
    if substrings and True not in (sub == "" for sub in substrings): # pour éviter une éventuelle boucle infinie.
        test = True
        while test:
            for sub in substrings:
                if main_string.startswith(sub):
                    main_string =  main_string[len(sub):]
                    test = None
            if test is None:
                test = True
            else:
                test = False
    return main_string


def no_twin(liste):
    u"""Elimine les doublons dans une liste.
    Si tous les élements de la liste sont 'hashables', mieux vaut utiliser la fonction set."""
    dico = {}
    for elt in liste:dico[id(elt)] = elt
    return dico.values()

#def ntwin(l): return dict((id(elt), elt) for elt in l).values() # plus élégant, mais 50% plus lent ?!?




def advanced_split(main_string, separator, keep_empty_str = False, symbols = "([{}])"):
    u"""Découpe la chaine "main_string" de manière intelligente,
    en ignorant les séparateurs compris dans un groupe entre parenthèses, crochets, accolades, guillemets.
    Attention, separateur ne peut donc pas être une parenthèse, un crochet, une accolade ou un guillemet !
    Par défaut, supprime également les chaines vides."""
    in_string = False # est-on dans une chaine ?
    in_string_sep = "'" # caractere encadrant la chaine (" ou ')
    parentheses = 0 # tient le compte des parentheses ouvertes non fermees
    crochets = 0 # idem pour les crochets
    accolades = 0 # idem
    coupures = [-1] # endroits ou il faudra couper la chaine
    for i in xrange(len(main_string)):
        a = main_string[i]
        if a in ("'", '"'):
            if in_string:
                if in_string_sep == a: # attention, il y a 2 indicateurs de chaine (" et ')
                    in_string = False
            else:
                in_string = True
                in_string_sep = a
        elif a in symbols:
            if a == "(" and not in_string:
                parentheses += 1
            elif a == ")" and not in_string:
                parentheses -= 1
            elif a == "[" and not in_string:
                crochets += 1
            elif a == "]" and not in_string:
                crochets -= 1
            elif a == "{" and not in_string:
                accolades += 1
            elif a == "}" and not in_string:
                accolades -= 1
        elif a == separator and not (in_string or parentheses or crochets or accolades) :
            coupures.append(i)
    coupures.append(None)
    # chaine[i:None] retourne la fin de chaine

    return [main_string[i+1:j] for i, j in zip(coupures[:-1], coupures[1:]) if main_string[i+1:j] or keep_empty_str]


def regsub(regular_exp, main_string, action = ""):
    u"""Transforme la chaine "main_string" :
    Il applique aux parties vérifiant "regular_exp" le traitement "action".

    >>> from wxgeometrie.geolib.fonctions import regsub
    >>> regsub("[a-z]", "salut les amis !", "?")
    '????? ??? ???? !'
    >>> regsub("[a-z]+", "hello world !", lambda s: s[1:])
    'ello orld !'
    """
    if isinstance(action, basestring):
        return re.sub(regular_exp, action, main_string)
    else:
        return re.sub(regular_exp, lambda x: action(x.group(0)), main_string)


class WeakList(weakref.WeakValueDictionary):
    u"""Une 'liste' de réferences faibles.

    Le terme 'liste' est trompeur, la syntaxe des listes de python n'est pas implémentée,
    exceptée les méthodes append(), et remove(), et la conversion en liste.

    En outre, le contenu s'obtient par la méthode values().

    Note:
    L'implémentation de remove est un peu différente :
    'remove' utilise le comparateur 'is', et non "==", ce qui fait que remove([]) ne fera jamais rien, par exemple.
    (Il faut qu'il s'agisse du meme objet, et non d'un objet égal).
    Sinon, il faut utiliser compare_and_remove."""

    def __init__(self):
        weakref.WeakValueDictionary.__init__(self)

    def append(self, valeur):
        u"Ajoute une valeur en fin de liste."
        self[max(self.keys() or [0]) + 1] = valeur

    def remove(self, valeur):
        u"""Supprime la valeur de la liste.

        Un test d'identité (et non d'égalité) est effectué ('is' et non '==').
        Si la valeur est présente plusieurs fois, elle n'est supprimée qu'une seule fois.
        Si la valeur n'est pas présente, une erreur de type ValueError est émise.
        """
        for key, value in self.items():
            if value is valeur:
                del self[key] # il faut qu'il s'agisse du même objet
                return
        raise ValueError,  repr(valeur) + " is not in WeakList"

    def compare_and_remove(self, valeur):
        u"""Supprime la valeur de la liste.

        Un test d'égalité est effectué ('==' et non 'is').
        Si la valeur est présente plusieurs fois, elle n'est supprimée qu'une seule fois.
        Si la valeur n'est pas présente, une erreur de type ValueError est émise.
        """
        for key, value in self.items():
            if value == valeur:
                del self[key] # un objet égal suffit
                return
        raise ValueError,  repr(valeur) + " not in WeakList"

    def remove_all(self, valeur):
        u"""Supprime la valeur de la liste.

        Un test d'identité (et non d'égalité) est effectué ('is' et non '==').
        Toutes les occurences de la valeur sont supprimées.
        Si la valeur n'est pas présente, aucune erreur n'est émise."""
        for key, value in self.items():
            if value is valeur: del self[key] # il faut qu'il s'agisse du même objet

    def compare_and_remove_all(self, valeur):
        u"""Supprime la valeur de la liste.

        Un test d'égalité est effectué ('==' et non 'is').
        Toutes les occurences de la valeur sont supprimées.
        Si la valeur n'est pas présente, aucune erreur n'est émise."""
        for key, value in self.items():
            if value == valeur: del self[key] # un objet égal suffit

    def __str__(self):
        return str(self.values()) + " (WeakList)"

    def __iter__(self):
        return self.itervalues()

    def __getitem__(self, n):
        return self.values()[n]


def print_error(chaine = ''):
    u"""Affiche l'erreur sans interrompre le programme.
    C'est un alias de sys.excepthook, mais qui est plus souple avec les encodages.
    """
    if chaine:
        print(chaine)
    typ, val, tb = sys.exc_info()
    tb = traceback.extract_tb(tb)
    print 'Traceback (most recent call last)'
    for fichier, ligne, fonction, code in tb:
        print '    File "' + uu(fichier) +'", line ' + str(ligne) + ', in ' + uu(fonction)
        if code is not None:
            print '        ' + uu(code)
    print uu(typ.__name__) + ": " + uu(val)
    print "Warning: this error was not raised."


def rstrip_(s, end):
    u"""Supprime récursivement 'end' de la fin de la chaîne 's'.

    >>> from pylib.fonctions import rstrip_
    >>> rstrip_('blabla_suffixe_fixe_suffixe_suffixe', '_suffixe')
    'blabla_suffixe_fixe'

    Nota :
        * ne pas confondre avec str.rstrip() :
        >>> 'blabla_suffixe_fixe_suffixe_suffixe'.rstrip('_suffixe')
        'blabla'

        * si end == '', la chaîne de départ est retournée :
        >>> rstrip_('bonjour', '')
        'bonjour'
    """
    if not end:
        return s
    i = -len(end)
    while s.endswith(end):
        s = s[:i]
    return s


def split_geoname(name):
    u"""Tente de décomposer un nom d'objet géométrique en plusieurs noms.

    Ex:
    1) "AB" -> ("A","B")
    2) "A12B" -> ("A12","B")
    3) "AB1" -> ("A","B1")
    4) "A'B\"" -> ("A'", "B\"")
    5) "ABC" -> ("A", "B", "C")
    """

    return tuple(nom.strip() for nom in re.split("""([ ]*[A-Za-z][_]?[0-9"']*[ ]*)""", name) if nom)


def convert_geoname(name, level = 0):
    u"""Convertit le nom entré par l'utilisateur en un nom réellement interprétable.

    Une conversion de niveau 1 est appliquée dans les boîtes de dialogue.

    Une conversion de niveau 0 est appliquée dans la console."""

    if level > 0:
        if level > 1:
            if " " not in name:
                name = " ".join(split_geoname)
        name = name.replace('"', "''")
        name = name.replace("'''", "_tierce")
        name = name.replace("''", "_seconde")
        name = name.replace("'", "_prime")
    name = name.replace("```", "_tierce")
    name = name.replace("``", "_seconde")
    name = name.replace("`", "_prime")




def split_around_parenthesis(main_string, position = 0, leftbracket = "("):
    u"""Coupe le premier groupe entre parentheses rencontré, en tenant compte des guillemets.

    'leftbracket' peut prendre les valeurs "(", "[" ou "{"
    La parenthese ouvrante du groupe sera la première trouvée à droite de 'position'
    Exemple: '1+4*(5+3*(2+7)+2-")")*7+(2-3)+4' -> ['1+4*', '(5+3*(2+7)+2-")")', '*7+(2-3)+4']
    """
    in_string = False # est-on dans une chaine ?
    in_string_sep = "'" # caractere encadrant la chaine (" ou ')
    position = main_string.find(leftbracket, position)
    if position is -1:
        return (main_string,)
    parentheses = 1 # tient le compte des parentheses ouvertes non fermees
    rightbracket = {"(": ")", "[": "]", "{": "}"}[leftbracket]
    prefixe = main_string[:position]
    chaine = main_string[position + 1:]
    for i in xrange(len(chaine)):
        a = chaine[i]
        if a in ("'", '"'):
            if in_string:
                if in_string_sep == a: # attention, il y a 2 indicateurs de chaine (" et ')
                    in_string = False
            else:
                in_string = True
                in_string_sep = a
        elif a == leftbracket and not in_string:
            parentheses += 1
        elif a == rightbracket and not in_string:
            parentheses -= 1
            if parentheses is 0:
                chaine = chaine
                return (prefixe, leftbracket + chaine[:i + 1], chaine[i + 1:])
    return (main_string,) # aucune parenthese fermante n'a été trouvée pour ce groupe.


def find_closing_bracket(expr, start = 0, brackets = '{}'):
    expr_deb = expr[:min(len(expr), 30)]
    # for debugging
    index = 0
    balance = 1
    # None if we're not presently in a string
    # Else, string_type may be ', ''', ", or """
    string_type = None
    reg = re.compile('["' + brackets + "']") # ', ", { and } matched
    open_bracket = brackets[0]
    close_bracket = brackets[1]
    if start:
        expr = expr[start:]
    while balance:
        m = re.search(reg, expr)
        #~ print 'scan:', m
        if m is None:
            break

        result = m.group()
        i = m.start()
        if result == open_bracket:
            if string_type is None:
                balance += 1
        elif result == close_bracket:
            if string_type is None:
                balance -= 1

        # Brackets in string should not be recorded...
        # so, we have to detect if we're in a string at the present time.
        elif result in ("'", '"'):
            if string_type is None:
                if expr[i:].startswith(3*result):
                    string_type = 3*result
                    i += 2
                else:
                    string_type = result
            elif string_type == result:
                string_type = None
            elif string_type == 3*result:
                if expr[i:].startswith(3*result):
                    string_type = None
                    i += 2

        i += 1 # counting the current caracter as already scanned text
        index += i
        expr = expr[i:]

    else:
        return start + index - 1 # last caracter is the searched bracket :-)

    raise ValueError, 'unbalanced brackets (%s) while scanning %s...' %(balance, repr(expr_deb))


def warning(message, type_warning = Warning, level=0):
    if param.warning:
        warnings.warn(message, type_warning, stacklevel = (level + 3))

def deprecation(message, level=0):
    warnings.warn(message, DeprecationWarning, stacklevel = (level + 3))

#def unicode2(string_or_unicode, encodage = None):
#    u"Convertit en unicode si besoin est, avec l'encodage de 'param.encodage' par défaut."
#    if isinstance(string_or_unicode, str):
#        try:
#            return unicode(string_or_unicode, encodage or param.encodage)
#        except UnicodeDecodeError:
##            try:
##                print "chaine :\n", string_or_unicode
##                print unicode(string_or_unicode, "cp1252")
##            except Exception:
##                pass
#            raise
#    elif isinstance(string_or_unicode, unicode):
#        return string_or_unicode
#    else:
#        try:
#            return unicode(string_or_unicode)
#        except UnicodeDecodeError:
#            print type(string_or_unicode)
#            raise



def str2(string_or_unicode, encodage = None):
    u"Convertit en string si besoin est, avec l'encodage de 'param.encodage' par défaut."
    if isinstance(string_or_unicode, str):
        return string_or_unicode
    elif isinstance(string_or_unicode, unicode):
        return string_or_unicode.encode(encodage or param.encodage)
    else:
        return str(string_or_unicode)

def str3(unicode):
    dict = {
                'a': (u'à', u'â', u'ä', ),
                'e': (u'é', u'è', u'ê', u'ë', ),
                'i': (u'î', u'ï', ),
                'o': (u'ô', u'ö', ),
                'u': (u'ù', u'û', u'ü',  ),
                'c': (u'ç', ),
                'A': (u'À', u'Â', u'Ä', ),
                'E': (u'É', u'È', u'Ê', u'Ë', ),
                'I': (u'Î', u'Ï', ),
                'O': (u'Ô', u'Ö', ),
                'U': (u'Ù', u'Û', u'Ü',  ),
                'C': (u'Ç', ),
                }
    for key, liste in dict.items():
        for item in liste:
            unicode = unicode.replace(item, key)
    return str(unicode)



def universal_unicode(chaine):
    u"Convertit en unicode si besoin est, avec l'encodage de 'param.encodage' par défaut."
    if not isinstance(chaine, basestring):
        chaine = str(chaine)
    if not isinstance(chaine, unicode):
        try:
            chaine = chaine.decode(param.encodage)
        except UnicodeError:
            try:
                chaine = chaine.decode('utf8')
            except UnicodeError:
                chaine = chaine.decode('iso-8859-1')
    return chaine

uu = universal_unicode



def path2(chemin):
    u"""Transforme le chemin en remplaçant les / et \\ selon le séparateur utilisé par le système.

    % est remplacé par l'emplacement du programme (contenu dans param.EMPLACEMENT).
    Exemple : path2("%/images/archives/old.png").
    ~ fait référence au répertoire personnel de l'utilisateur (ex: /home/SteveB/ sous Linux.
    """
    return os.path.normpath(os.path.expanduser(uu(chemin).replace("%", uu(param.EMPLACEMENT))))



# L'idée de compiler en une fois pour toute les expressions regulières n'est pas avantageuse : le temps gagné ainsi est perdu à rechercher les entrées dans le dictionnaire.

#~ def regsub(regular_exp, main_string, action = ""):
    #~ u"""Transforme la chaine "main_string" :
    #~ Il applique aux parties vérifiant "regular_exp" le traitement "action".

    #~ >>> regsub("[a-z]", "salut les amis !", "?")
    #~ '????? ??? ???? !'
    #~ >>> regsub("[a-z]+", "hello world !", lambda s: s[1:])
    #~ 'ello orld !'
    #~ """
    #~ if isinstance(regular_exp, basestring):
        #~ if isinstance(action, basestring):
            #~ return re.sub(regular_exp, action, main_string)
        #~ else:
            #~ return re.sub(regular_exp, lambda x: action(x.group(0)), main_string)
    #~ else:
        #~ if isinstance(action, basestring):
            #~ return regular_exp.sub(action, main_string)
        #~ else:
            #~ return regular_exp.sub(lambda x: action(x.group(0)), main_string)


#~ class REStorageDict(dict):
    #~ u"""Un dictionnaire qui stocke les RE sous forme compilée.

    #~ """
    #~ def __getitem__(self, name):
        #~ try:
            #~ return dict.__getitem__(self, name)
        #~ except KeyError:
            #~ value = re.compile(name)
            #~ self.__setitem__(name, value)
            #~ return value


class WeakRef(weakref.ref):
    u"""WeakRef surclasse weakref.ref en modifiant sa méthode '__eq__'.

    a == b <=> type(a) == type(b) == WeakRef and a() is b().
    Le but est de ne pas appeler les méthodes __eq__ des objets référencés."""

    def __eq__(self, y):
        if not (isinstance(self, WeakRef) and isinstance(y, WeakRef)):
            return False
        if self() is None or y() is None:
            return self is y
        return  self() is y()



class CustomWeakKeyDictionary(weakref.WeakKeyDictionary):
    """WeakKeyDictionary utilisant Weakref au lieu de weakref.ref.
    """

    def __init__(self, dict=None):
        self.data = {}
        def remove(k, selfref=weakref.ref(self)):
            self = selfref()
            if self is not None:
                del self.data[k]
        self._remove = remove
        if dict is not None: self.update(dict)

    def __delitem__(self, key):
        del self.data[WeakRef(key)]

    def __getitem__(self, key):
        return self.data[WeakRef(key)]

    def __repr__(self):
        return "<WeakKeyDictionary at %s>" % id(self)

    def __setitem__(self, key, value):
        self.data[WeakRef(key, self._remove)] = value

    def copy(self):
        new = CustomWeakKeyDictionary()
        for key, value in self.data.items():
            o = key()
            if o is not None:
                new[o] = value
        return new

    def get(self, key, default=None):
        return self.data.get(WeakRef(key),default)

    def has_key(self, key):
        try:
            wr = WeakRef(key)
        except TypeError:
            return 0
        return wr in self.data

    def __contains__(self, key):
        try:
            wr = WeakRef(key)
        except TypeError:
            return 0
        return wr in self.data



    def pop(self, key, *args):
        return self.data.pop(WeakRef(key), *args)

    def setdefault(self, key, default=None):
        return self.data.setdefault(WeakRef(key, self._remove),default)

    def update(self, dict=None, **kwargs):
        d = self.data
        if dict is not None:
            if not hasattr(dict, "items"):
                dict = type({})(dict)
            for key, value in dict.items():
                d[WeakRef(key, self._remove)] = value
        if len(kwargs):
            self.update(kwargs)



def debug(*messages):
    u"""Affiche un (ou plusieurs) message(s) si le déboguage est actif."""
    if param.debug:
        for message in messages:
            print(message)

@decorator
def trace(f, *args, **kw):
    if param.debug:
        print "Calling %s with args %s, %s" % (f.func_name, args, kw)
    return f(*args, **kw)

@decorator
def full_trace(f, *args, **kw):
    if param.debug:
        print '** Debugging info **'
        traceback.print_stack()
        print "Calling %s with args %s, %s" % (f.func_name, args, kw)
        print '-------------------\n'
    return f(*args, **kw)

def deprecated(message = ''):
    "A decorator for deprecated functions"
    @decorator
    def _deprecated(func, *args, **kw):
        "A decorator for deprecated functions"
        warnings.warn('\n'.join(('La fonction %r est desuette.' %func.__name__, message)),
                      DeprecationWarning, stacklevel = 3)
        return func(*args, **kw)
    return _deprecated


##@decorator
##def deprecated(func, *args, **kw):
##    "A decorator for deprecated functions"
##    warnings.warn(
##        ('Calling the deprecated function %r\n'
##         'Downgrade to decorator 2.3 if you want to use this functionality')
##        % func.__name__, DeprecationWarning, stacklevel=3)
##    return func(*args, **kw)



def traceit(frame, event, arg):
    u"""'Trace' (suit) une fonction python.

        Usage:
        import sys
        sys.settrace(traceit)"""
    if event == "line":
        lineno = frame.f_lineno
        filename = frame.f_globals["__file__"]
        if (filename.endswith(".pyc") or
            filename.endswith(".pyo")):
            filename = filename[:-1]
        name = frame.f_globals["__name__"]
        line = linecache.getline(filename, lineno)
        print "%s:%s: %s" % (name, lineno, line.rstrip())
    return traceit


def tracer_(booleen = True):
    if booleen:
        sys.settrace(traceit)
    else:
        sys.settrace(None)


def property2(fonction):
    return property(fonction, fonction)

# Permet de contourner un bug de exec() sous Python 2.5 lorsque with_statement est activé
assert "with_statement" not in locals()
assert "with_statement" not in globals()
def exec_(s, globals, locals):
    exec(s, globals, locals)


class CompressedList(list):
    def append(self, s):
        list.append(self, zlib.compress(s))

    def __getitem__(self, i):
        return zlib.decompress(list.__getitem__(self, i))

    def __setitem__(self, i, s):
        list.__setitem__(self, i, zlib.compress(s))

    def remove(self, s):
        list.remove(self, zlib.compress(s))

    def count(self, s):
        return list.count(self, zlib.compress(s))

    def extend(self, iterable):
        list.extend(self, (zlib.compress(s) for s in iterable))

    def index(self, s):
        list.index(self, zlib.compress(s))

    def insert(self, i, s):
        list.insert(self, i, zlib.compress(s))

    def pop(self, i = -1):
        return zlib.decompress(list.pop(self, i))

def pstfunc(chaine):
    args = []
    dict_op = {'mul':'*','add':'+','exp':'**','div':'/','sub':'-'}
    dict_fn = {'ln':'ln'}

    def code_arg(s):
        return '(' + str(sympify(s)) + ')'

    for s in chaine.split(' '):
        if s in dict_op:
            args = [code_arg(dict_op[s].join(args))]
        elif s in dict_fn:
            assert len(args) == 1
            args = [code_arg(dict_fn + '(' + args[0] + ')')]
        elif s:
            args.append(code_arg(s))
    assert len(args) == 1
    return args[0]


class NoArgument(object):
    u'''Utilisé comme valeur par défaut, pour savoir si un argument optionnel
    a été passé. Une seule instance peut-être crée.'''
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

no_argument = NoArgument()



class OrderedDict(dict):
    def __init__(self, seq = ()):
        self.__keys = []
        dict.__init__(self)
        for key, val in seq:
            self[key] = val

    def __setitem__(self, key, value):
        if key not in self:
            self.__keys.append(key)
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.__keys.remove(key)

    def __iter__(self):
        return iter(self.__keys)

    def __repr__(self):
        return "MyOrderedDict(%s)"%repr(self.items())

    def keys(self):
        return self.__keys[:]

    def values(self):
        return [self[key] for key in self.__keys]

    def items(self):
        return [(key, self[key]) for key in self.__keys]

    def copy(self):
        return self.__class__(self.iteritems())

    def iterkeys(self):
        return iter(self)

    def iteritems(self):
        return ((key, self[key]) for key in self.__keys)

    def itervalues(self):
        return (self[key] for key in self.__keys)

    def update(self, E, **F):
        if hasattr(E, 'keys'):
            for k in E:
                self[k] = E[k]
        else:
            for (k, v) in E:
                self[k] = v
        for k in F:
            self[k] = F[k]

    def setdefaut(self, k, d = None):
        if k not in self:
            self[k] = d
        return self[k]

    def clear(self):
        del self.__keys[:]
        dict.clear(self)

    def pop(self, k, d=no_argument):
        try:
            v = dict.pop(self, k)
            self.__keys.remove(k)
            return v
        except KeyError:
            if d is no_argument:
                raise
            return d

    def __reversed__(self):
        return reversed(self.__keys)

    def popitem(self):
        if not self:
            raise KeyError('dictionary is empty')
        key = self.__keys.pop()
        value = dict.pop(self, key)
        return key, value
