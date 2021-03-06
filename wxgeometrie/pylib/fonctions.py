# -*- coding: utf-8 -*-

##########################################################################
#
#       Fonctions couramment utilisees, et non implementees en Python
#                     (...du moins, à ma connaissance !)
#
##########################################################################
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


import re
import weakref
import sys, zlib
import os.path
import warnings, traceback, linecache

from .decorator import decorator

from .. import param # paramètres du programme
from sympy import sympify


def is_in(element, _list):
    """Teste si l'élement est dans la liste, en effectuant un test d'identité (is) et non d'égalité (==)."""
    for elt in _list:
        if elt is element:
            return True
    return False

# This is 'a lot' slower (2.4 times about) :
##def isin2(element, _list):
##    u"""Teste si l'élement est dans la liste, en effectuant un test d'identité (is) et non d'égalité (==)."""
##    return id(element) in (id(elt) for elt in _list)

# And this too... (2 times about on python 2.5)
##def isin3(element, _list):
##    u"""Teste si l'élement est dans la liste, en effectuant un test d'identité (is) et non d'égalité (==)."""
##    return any(elt is element for elt in _list)

def mreplace(main_string, list_of_strings, new_string = ""):
    """Remplace, dans "main_string", toutes les sous-chaines de "list_of_strings", par la chaine "new_string"."""
    for old_string in list_of_strings:
        main_string = main_string.replace(old_string, new_string)
    return main_string

def recursive_replace(main_string, old_string, new_string = "", max_loops = 10000, max_len = 1000000):
    """Remplace, dans "main_string", la sous-chaîne "old_string" par "new_string", au besoin en plusieurs passes.

    En fin de processus, la sous-chaîne old_string ne subsiste plus dans la chaîne.
    Renvoie une erreur si le processus ne semble pas converger.
    (C'est en particulier le cas si old_string est strictement inclus dans new_string)

    La différence avec replace est claire sur cette exemple :
    >>> from wxgeometrie.pylib.fonctions import recursive_replace
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
    while chaine != main_string:
        loops += 1
        chaine = main_string
        main_string = main_string.replace(old_string, new_string)
        if loops > max_loops:
            raise RuntimeError("Nombre de passes superieur au maximum autorise.")
        if len(main_string) > max_len:
            raise OverflowError("Taille de la chaine superieure au maximum autorise.")
    return main_string


def recursive_mreplace(main_string, list_of_strings, new_string = "", max_loops = 10000, max_len = 1000000):
    """Remplace, dans "main_string", toutes les sous-chaines de "list_of_strings" par "new_string", au besoin en plusieurs passes.

    En fin de processus, la sous-chaîne old_string ne subsiste plus dans la chaîne.
    Renvoie une erreur si le processus ne semble pas converger.

    Voir également recursive_replace() et mreplace().

    Remarque: recursive_mreplace n'est pas équivalent des appels successifs de recursive_replace().
    >>> from wxgeometrie.pylib.fonctions import recursive_replace, recursive_mreplace
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
    while chaine != main_string:
        loops += 1
        chaine = main_string
        main_string = mreplace(main_string, list_of_strings, new_string)
        if loops > max_loops:
            raise RuntimeError("Nombre de passes superieur au maximum autorise.")
        if len(main_string) > max_len:
            raise OverflowError("Taille de la chaine superieure au maximum autorise.")
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
    """Découpe la chaine "main_string", selon les séparateurs définis dans "list_of_separators"."""
    return mreplace(main_string, list_of_separators[1:], list_of_separators[0]).split(list_of_separators[0])



def removeend(main_string, *substrings):
    "Enlève les éventuelles occurences de substring en fin de chaine."
    if substrings and '' not in substrings: # pour éviter une éventuelle boucle infinie.
        run = True
        while run:
            run = False
            for sub in substrings:
                if main_string.endswith(sub):
                    main_string =  main_string[:-len(sub)]
                    run = True
    return main_string


def removestart(main_string, *substrings):
    "Enlève les éventuelles occurences de substring en début de chaine."
    if substrings and '' not in substrings: # pour éviter une éventuelle boucle infinie.
        run = True
        while run:
            run = False
            for sub in substrings:
                if main_string.startswith(sub):
                    main_string =  main_string[len(sub):]
                    run = True
    return main_string


def no_twin(liste):
    """Elimine les doublons dans une liste.
    Si tous les élements de la liste sont 'hashables', mieux vaut utiliser la fonction set."""
    dico = {}
    for elt in liste:
        dico[id(elt)] = elt
    return list(dico.values())

#def ntwin(l): return dict((id(elt), elt) for elt in l).values() # plus élégant, mais 50% plus lent ?!?




def advanced_split(main_string, separator, keep_empty_str = False, symbols = "([{}])"):
    """Découpe la chaine "main_string" de manière intelligente,
    en ignorant les séparateurs compris dans un groupe entre parenthèses, crochets, accolades, guillemets.
    Attention, separateur ne peut donc pas être une parenthèse, un crochet, une accolade ou un guillemet !
    Par défaut, supprime également les chaines vides."""
    in_string = False # est-on dans une chaine ?
    in_string_sep = "'" # caractere encadrant la chaine (" ou ')
    parentheses = 0 # tient le compte des parentheses ouvertes non fermees
    crochets = 0 # idem pour les crochets
    accolades = 0 # idem
    coupures = [-1] # endroits ou il faudra couper la chaine
    for i in range(len(main_string)):
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
    """Transforme la chaine "main_string" :
    Il applique aux parties vérifiant "regular_exp" le traitement "action".

    >>> from wxgeometrie.pylib.fonctions import regsub
    >>> regsub("[a-z]", "salut les amis !", "?")
    '????? ??? ???? !'
    >>> regsub("[a-z]+", "hello world !", lambda s: s[1:])
    'ello orld !'
    """
    if isinstance(action, str):
        return re.sub(regular_exp, action, main_string)
    else:
        return re.sub(regular_exp, lambda x: action(x.group(0)), main_string)




class WeakList(weakref.WeakValueDictionary):
    """Une 'liste' de réferences faibles.

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
        self[max(self.keys(), default=0) + 1] = valeur

    def remove(self, valeur):
        """Supprime la valeur de la liste.

        Un test d'identité (et non d'égalité) est effectué ('is' et non '==').
        Si la valeur est présente plusieurs fois, elle n'est supprimée qu'une seule fois.
        Si la valeur n'est pas présente, une erreur de type ValueError est émise.
        """
        for key, value in self.items():
            if value is valeur:
                del self[key] # il faut qu'il s'agisse du même objet
                return
        raise ValueError(repr(valeur) + " is not in WeakList")

    def compare_and_remove(self, valeur):
        """Supprime la valeur de la liste.

        Un test d'égalité est effectué ('==' et non 'is').
        Si la valeur est présente plusieurs fois, elle n'est supprimée qu'une seule fois.
        Si la valeur n'est pas présente, une erreur de type ValueError est émise.
        """
        for key, value in self.items():
            if value == valeur:
                del self[key] # un objet égal suffit
                return
        raise ValueError(repr(valeur) + " not in WeakList")

    def remove_all(self, valeur):
        """Supprime la valeur de la liste.

        Un test d'identité (et non d'égalité) est effectué ('is' et non '==').
        Toutes les occurences de la valeur sont supprimées.
        Si la valeur n'est pas présente, aucune erreur n'est émise."""
        for key, value in self.items():
            if value is valeur: del self[key] # il faut qu'il s'agisse du même objet

    def compare_and_remove_all(self, valeur):
        """Supprime la valeur de la liste.

        Un test d'égalité est effectué ('==' et non 'is').
        Toutes les occurences de la valeur sont supprimées.
        Si la valeur n'est pas présente, aucune erreur n'est émise."""
        for key, value in self.items():
            if value == valeur: del self[key] # un objet égal suffit

    def __str__(self):
        return str(list(self.values())) + " (WeakList)"

    def __iter__(self):
        return iter(self.values())

    def __getitem__(self, n):
        return list(self.values())[n]

    def __contains__(self, item):
        return item in self.values()


class WeakMultiSet(weakref.WeakKeyDictionary):
    """A WeakValueDictionary which keeps count of how many times an object was added.

    The interface implements only the methods remove() and add()
    to emulate a set.

    When an element is removed, the count is actually decrease.
    If count reaches 0, the element is discarded (key is removed).

    Additionnaly, method remove_completely() discard the element
    whatever the count.

    This is quite similar to collect.Counter, except that entries are deleted
    when count reaches 0, and weak refrences are used."""
    def remove(self, elt):
        self[elt] -= 1
        if self[elt] == 0:
            del self[elt]

    def add(self, elt):
        if elt in self:
            self[elt] += 1
        else:
            self[elt] = 1

    def remove_completely(self, elt):
        del self[elt]



def extract_error(chaine=''):
    lignes = []
    if chaine:
        lignes.append(chaine)
    typ, val, tb = sys.exc_info()
    tb = traceback.extract_tb(tb)
    lignes.append('Traceback (most recent call last)')
    for fichier, ligne, fonction, code in tb:
        lignes.append('    File "%s", line %s, in %s'
                % (str(fichier), str(ligne), str(fonction)))
        if code is not None:
            lignes.append('        ' + str(code))
    lignes.append(typ.__name__ + ": " + str(val))
    lignes.append("Warning: this error was not raised.")
    return '\n'.join(lignes)



def print_error(chaine=''):
    """Affiche l'erreur sans interrompre le programme.
    C'est un alias de sys.excepthook, mais qui est plus souple avec les encodages.
    """
    print(extract_error(chaine))


def rstrip_(s, end):
    """Supprime récursivement 'end' de la fin de la chaîne 's'.

    >>> from wxgeometrie.pylib.fonctions import rstrip_
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


# http://stackoverflow.com/questions/2556108/rreplace-how-to-replace-the-last-occurence-of-an-expression-in-a-string
def rreplace(s, old, new, count):
    """rreplace (s, old, new, count) -> string

    Return a copy of string S with the first count occurrences of substring
    old replaced by new, starting from right to left."""
    return new.join(s.rsplit(old, count))



def split_geoname(name):
    """Tente de décomposer un nom d'objet géométrique en plusieurs noms.

    Ex:
    1) "AB" -> ("A","B")
    2) "A12B" -> ("A12","B")
    3) "AB1" -> ("A","B1")
    4) "A'B\"" -> ("A'", "B\"")
    5) "ABC" -> ("A", "B", "C")
    """

    return tuple(nom.strip() for nom in re.split("""([ ]*[A-Za-z][_]?[0-9"']*[ ]*)""", name) if nom)


def convert_geoname(name, level = 0):
    """Convertit le nom entré par l'utilisateur en un nom réellement interprétable.

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
    """Coupe le premier groupe entre parentheses rencontré, en tenant compte des guillemets.

    'leftbracket' peut prendre les valeurs "(", "[" ou "{"
    La parenthese ouvrante du groupe sera la première trouvée à droite de 'position'
    Exemple: '1+4*(5+3*(2+7)+2-")")*7+(2-3)+4' -> ['1+4*', '(5+3*(2+7)+2-")")', '*7+(2-3)+4']
    """
    in_string = False # est-on dans une chaine ?
    in_string_sep = "'" # caractere encadrant la chaine (" ou ')
    position = main_string.find(leftbracket, position)
    if position == -1:
        return (main_string,)
    parentheses = 1 # tient le compte des parentheses ouvertes non fermees
    rightbracket = {"(": ")", "[": "]", "{": "}"}[leftbracket]
    prefixe = main_string[:position]
    chaine = main_string[position + 1:]
    for i in range(len(chaine)):
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
            if parentheses == 0:
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

    raise ValueError('unbalanced brackets (%s) while scanning %s...' %(balance, repr(expr_deb)))


def warning(message, type_warning = Warning, level=0):
    if param.warning:
        warnings.warn(message, type_warning, stacklevel = (level + 3))

def deprecation(message, level=0):
    warnings.warn(message, DeprecationWarning, stacklevel = (level + 3))





def path2(chemin):
    """Transforme le chemin en remplaçant les / et \\ selon le séparateur utilisé par le système.

    % est remplacé par l'emplacement du programme (contenu dans param.EMPLACEMENT).
    Exemple : path2("%/wxgeometrie/images/archives/old.png").
    ~ fait référence au répertoire personnel de l'utilisateur (ex: /home/SteveB/ sous Linux.
    """
    return os.path.normpath(os.path.expanduser(chemin.replace("%", param.EMPLACEMENT)))



# L'idée de compiler en une fois pour toute les expressions regulières n'est pas avantageuse,
# car python le fait déjà automatiquement pour celles utilisées le plus souvent.

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


#~ class WeakRef(weakref.ref):
    #~ """WeakRef surclasse weakref.ref en modifiant sa méthode '__eq__'.

    #~ a == b <=> type(a) == type(b) == WeakRef and a() is b().
    #~ Le but est de ne pas appeler les méthodes __eq__ des objets référencés."""

    #~ def __eq__(self, y):
        #~ if not isinstance(y, WeakRef):
            #~ return False
        #~ if self() is None or y() is None:
            #~ return self is y
        #~ return self() is y()

    #~ def __hash__(self):
        #~ return id(self())


#~ class CustomWeakKeyDictionary(weakref.WeakKeyDictionary):
    #~ """WeakKeyDictionary utilisant Weakref au lieu de weakref.ref.
    #~ """

    #~ def __delitem__(self, key):
        #~ del self.data[WeakRef(key)]

    #~ def __getitem__(self, key):
        #~ return self.data[WeakRef(key)]

    #~ def __repr__(self):
        #~ return "<WeakKeyDictionary at %s>" % id(self)

    #~ def __setitem__(self, key, value):
        #~ self.data[WeakRef(key, self._remove)] = value

    #~ def copy(self):
        #~ new = CustomWeakKeyDictionary()
        #~ for key, value in self.data.items():
            #~ o = key()
            #~ if o is not None:
                #~ new[o] = value
        #~ return new

    #~ def get(self, key, default=None):
        #~ return self.data.get(WeakRef(key),default)

    #~ def has_key(self, key):
        #~ try:
            #~ wr = WeakRef(key)
        #~ except TypeError:
            #~ return 0
        #~ return wr in self.data

    #~ def __contains__(self, key):
        #~ try:
            #~ wr = WeakRef(key)
        #~ except TypeError:
            #~ return 0
        #~ return wr in self.data



    #~ def pop(self, key, *args):
        #~ return self.data.pop(WeakRef(key), *args)

    #~ def setdefault(self, key, default=None):
        #~ return self.data.setdefault(WeakRef(key, self._remove),default)

    #~ def update(self, dict=None, **kwargs):
        #~ d = self.data
        #~ if dict is not None:
            #~ if not hasattr(dict, "items"):
                #~ dict = type({})(dict)
            #~ for key, value in dict.items():
                #~ d[WeakRef(key, self._remove)] = value
        #~ if len(kwargs):
            #~ self.update(kwargs)



def debug(*messages):
    """Affiche un (ou plusieurs) message(s) si le déboguage est actif."""
    if param.debug:
        for message in messages:
            print(message)

@decorator
def trace(f, *args, **kw):
    if param.debug:
        print("Calling %s with args %s, %s" % (f.__name__, args, kw))
    return f(*args, **kw)

@decorator
def full_trace(f, *args, **kw):
    if param.debug:
        print('** Debugging info **')
        traceback.print_stack()
        print("Calling %s with args %s, %s" % (f.__name__, args, kw))
        print('-------------------\n')
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
    """'Trace' (suit) une fonction python.

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
        print("%s:%s: %s" % (name, lineno, line.rstrip()))
    return traceit


def tracer_(booleen = True):
    if booleen:
        sys.settrace(traceit)
    else:
        sys.settrace(None)


def property2(fonction):
    return property(fonction, fonction)


def _archive(string):
    return zlib.compress(string.encode('utf8'))

def _extract(data):
    return zlib.decompress(data).decode('utf8')


class CompressedList(list):
    def append(self, s):
        list.append(self, _archive(s))

    def __getitem__(self, i):
        return _extract(list.__getitem__(self, i))

    def __setitem__(self, i, s):
        list.__setitem__(self, i, _archive(s))

    def remove(self, s):
        list.remove(self, _archive(s))

    def count(self, s):
        return list.count(self, _archive(s))

    def extend(self, iterable):
        list.extend(self, (_archive(s) for s in iterable))

    def index(self, s):
        list.index(self, _archive(s))

    def insert(self, i, s):
        list.insert(self, i, _archive(s))

    def pop(self, i = -1):
        return _extract(list.pop(self, i))


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
    '''Utilisé comme valeur par défaut, pour savoir si un argument optionnel
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
        return "MyOrderedDict(%s)"%repr(list(self.items()))

    def keys(self):
        return self.__keys[:]

    def values(self):
        return [self[key] for key in self.__keys]

    def items(self):
        return [(key, self[key]) for key in self.__keys]

    def copy(self):
        return self.__class__(iter(self.items()))

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
