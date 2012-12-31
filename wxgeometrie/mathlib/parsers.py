# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                Objets CALC                  #
##--------------------------------------#######
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

import keyword, re
from itertools import chain, izip_longest

from matplotlib.mathtext import (MathTextParser, AutoHeightChar, Hlist, SUB1,
                                 SUBDROP, Kern, SCRIPT_SPACE, Hbox, HCentered,
                                 ParseFatalException, Vlist, SUP1, DELTA)

import matplotlib
from sympy import Expr

from ..pylib.fonctions import regsub, split_around_parenthesis, debug, \
                                warning, rreplace#, find_closing_bracket
from .. import param


_mathtext_raw_parser = MathTextParser("PS").parse

# Commandes LaTeX à caractères uniquement alphabétiques (sans le \ préliminaire)
dictionnaire_latex_commandes = {
                                "nombre" : "",
                                "nb": "",
                                "left": "",
                                "right": "",
                                "sqrt": " sqrt",
                                "sin": " sin",
                                "cos": " cos",
                                "tan": " tan",
                                "ln":" ln",
                                "log": " log",
                                "exp": " exp",
                                "times": "*",
                                "infty": "oo",
                                "oo": "oo",
                                "i": " i",
                                "e": " e",
                                "pi": " pi",
                                "quad": " ",
                                "qquad": " ",
                                "text": "",
                                "mathrm": "",
                                "bar": "conjug",
                                "le": "<=",
                                "leqslant": "<=",
                                "ge": ">=",
                                "geqslant": ">=",
                                "displaystyle": "",
                                }


# Commandes LaTeX à caractères NON uniquement alphabétiques
dictionnaire_latex_special = {
                                "~": " ",
                                "\\,": " ",
                                "\\!": " ",
                                "\\;": " ",
                                "\\:": " ",
                                "\\\\": " ",
                                }

# Nom de variable
VAR = "(?:[_A-Za-z][_A-Za-z0-9]*)"
# Nom de variable, mais pas d'attribut
VAR_NOT_ATTR = "(?:(?<![.A-Za-z0-9_])[A-Za-z_][A-Za-z0-9_]*)"
##VAR_NOT_ATTR_compile = re.compile(VAR_NOT_ATTR)
##NBR = "([+-]?[ ]?(([0-9]+[.]?)|([0-9]*[.][0-9]+)))"
# Nombre avec un signe éventuel devant
NBR_SIGNE = "(?:(?<![.A-Za-z0-9_])(?:(((?<=[*/^])|^)[+-])?[ ]?(?:[0-9]*[.][0-9]+|[0-9]+[.]?)))"
# Nombre sans signe
NBR = "(?:(?<![.A-Za-z0-9_])(?:[0-9]*[.][0-9]+|[0-9]+[.]?))"
# Nombre à virgule écrit au format français (le séparateur décimal est la virgule, et non le point)
NBR_VIRGULE = "(?:(?<![.A-Za-z0-9_])(?:[0-9]+[,][0-9]+))"
# Nombre sans signe ou variable
NBR_OR_VAR = "(?:" + NBR + "|" + VAR + ")"
NBR_SIGNE_OR_VAR = "(?:" + NBR_SIGNE + "|" + VAR + ")"


def _simplifier(formule):
    u"""Suppressions d'espaces inutiles."""
#    formule = formule.strip()
    # - un seul caractère d'espacement
#    formule = regsub("[ ]+", formule, " ")
    # - espaces supprimés autour de la plupart des caractères.
    formule = regsub("(?<![A-Za-z0-9_.])[ ]", formule, "")
    formule = regsub("[ ](?![A-Za-z0-9_.])", formule, "")
    return formule

def _arguments_latex(chaine, nbr_arguments = 2):
    u"""Renvoie les arguments d'une commande LaTeX (ainsi que le reste de la chaîne).

    >>> from wxgeometrie.mathlib.parsers import _arguments_latex
    >>> _arguments_latex('2{x+1}+4', 2)
    ['2', '{x+1}', '+4']
    >>> _arguments_latex('{x+2}5+4x-17^{2+x}', 2)
    ['{x+2}', '5', '+4x-17^{2+x}']
   """
    liste = []
    while len(liste) < nbr_arguments:
        if not chaine:
            raise TypeError, "Il manque des arguments."
        if chaine[0] != "{":
            liste.append(chaine[0])
            chaine = chaine[1:]
        else:
            l = split_around_parenthesis(chaine, 0, "{")
            if len(l) != 3:
                raise TypeError, "Arguments mal formes: il manque des '}'."
            liste.append(l[1])
            chaine = l[2]
    liste.append(chaine)
    return liste


def _convertir_latex_frac(chaine):
    u"""Convertit \frac{a}{b}, \dfrac{a}{b} et \tfrac{a}{b} en ((a)/(b)).

    >>> from wxgeometrie.mathlib.parsers import _convertir_latex_frac
    >>> _convertir_latex_frac('3+\dfrac{1}{2x+1}+5x+1')
    '3+((1)/(2x+1))+5x+1'
    """
    for substr in (r"\frac", r"\dfrac", r"\tfrac"):
        i = chaine.find(substr)
        while i != -1:
            arg1, arg2, reste = _arguments_latex(chaine[i + len(substr):], 2)
            if arg1[0] == '{' and arg1[-1] == '}':
                arg1 = '(' + arg1[1:-1] + ')'
            if arg2[0] == '{' and arg2[-1] == '}':
                arg2 = '(' + arg2[1:-1] + ')'
            chaine = chaine[:i] + "(" + arg1 + "/" + arg2 + ")" + reste
            i = chaine.find(substr, i)
    return chaine



def _ajouter_mult_manquants(formule, fonctions = (), verbose = None, mots_cles = ()):
    if isinstance(fonctions, dict):
        # On récupère les fonctions de l'espace des noms
        # (tout objet 'callable' sauf certains objets Sympy).
        fonctions = [key for key, val in fonctions.items() if hasattr(val, "__call__") and not isinstance(val, Expr)]

    if verbose:
        print '1', formule

    # Le code qui suit remplace les expressions style 3x ou 2.5cos(x) par 3*x et 2.5*cos(x).
    formule = regsub(NBR + "[ ]?(?=[a-zA-Z_])", formule, lambda s: s.rstrip() + '*')
    # TODO: traiter le cas des mots-clés

    # De meme, on rajoute les * entre deux parentheses...
    formule = formule.replace(")(",")*(")

    if verbose:
        print '2', formule

    # Si a, b, c... ne sont pas des fonctions, on remplace "a(" par "a*(", etc...
    def f1(s):
        s = s.strip()
        if s in fonctions:# or s in mots_cles:
            return s
        elif s[0] == '.' and not s[1:].isdigit():
            # Probablement une méthode
            # TODO: améliorer détection en remontant avant le point
            # (pour distinguer entre 2.x(1+x) et a2.x(1+x))
            return s
        else:
            return s + "*"
    formule = regsub("[.]?" + NBR_OR_VAR + "[ ]?(?=[(])", formule, f1)

    if verbose:
        print '3', formule

    # "f x" devient "f(x)" si f est une fonction, "f*x" sinon ;
    # de même, "f 2.5" devient "f(2.5)" si f est une fonction, et "f*2.5" sinon.
    # (Si f est un mot-clé (if, then, else, for...), on n'y touche pas.)
    def f2(s):
        l = s.split()
        if l[0] in mots_cles:
            return s
        elif l[0] in fonctions:
            return l[0] + "(" + l[1] + ")"
        else:
            return l[0] + "*" + l[1]
    formule_initiale = ""
    i = 0 # sécurité sans doute inutile...
    while formule != formule_initiale and i < 1000:
        formule_initiale = formule
        formule = regsub(VAR + "[ ]" + NBR + "?[*/]?" + NBR_OR_VAR , formule, f2)
        i += 1

    if verbose:
        print '4', formule

    # On remplace ")x" par ")*x"
    formule = regsub("[)][ ]?\w", formule, lambda s: s[0] + '*' + s[-1])
    # TODO: traiter le cas des mots-clés

    # Cas des mots-clés: on supprime les '*' introduits à tort.
    mc = '|'.join(mots_cles)
    formule = regsub("(?<![A-Za-z0-9_])(%s)[*]" %mc, formule, lambda s:s[:-1] + ' ')
    formule = regsub("[*](%s)(?![A-Za-z0-9_])" %mc, formule, lambda s:' ' + s[1:])

    return formule


def _extract_inner_str(s):
    # <@> is a marker for substring emplacements.
    s = s.replace('@', '@@')
    start = end = None
    morceaux = []
    subs = []
    pos = 0
    while pos < len(s):
        if start is None:
            # Start of a new substring.
            start = s.find('"', pos)
            if start == -1:
                start = None
            morceaux.append(s[end:start])
            if start is None:
                break
            # Two types of substrings are recognised: "type 1", and """type 2""".
            marker = ('"""' if s.startswith('"""', start) else '"')
            n = len(marker)
            pos = start + n
        else:
            # End of the substring.
            end = s.find(marker, pos)
            if s.endswith('\\', 0, end):
                # Use \" to escape " caracter.
                pos = end + 1 # '"""\"+1\" ici, et non \"+n\""""'
                continue
            if end == -1:
                raise SyntaxError, "String unclosed !"
            end += n
            subs.append(s[start:end])
            pos = end
            start = None
    return '<@>'.join(morceaux), subs


def _inject_inner_str(s, str_list):
    s_list = s.split('<@>')
    # Combine alternativement les 2 listes
    i = filter(None, chain.from_iterable(izip_longest(s_list, str_list)))
    return ''.join(i).replace('@@', '@')


def _convertir_separateur_decimal(s):
    s = regsub(NBR_VIRGULE, s, (lambda s: s.replace(',', '.')))
    return s.replace(';', ',')


def traduire_formule(formule='', fonctions=(), OOo=True, LaTeX=True,
            simpify=False, verbose=None, mots_cles=tuple(keyword.kwlist)):

    # Les chaînes internes ne doivent pas être modifiées
    # http://wxgeo.free.fr/tracker/index.php?do=details&task_id=129&project=1
    # Algorithme pour le parser de mathlib:
    # - remplacer @ par @@
    # - détection des chaînes de textes, remplacées par <@>
    # -> génération d'une liste de chaînes (ex: ["texte 1", """texte 2""", "texte 3", "texte 4"])
    # On applique le parser...
    #- remplacer <@> par les chaînes prélablement enregistrées
    #-remplacer @@ par @


    formule, substrings_list = _extract_inner_str(formule)

    # En français, le séparateur décimal est la virgule.
    formule = _convertir_separateur_decimal(formule)

    formule = _simplifier(formule)


    if verbose:
        print '0', formule

    # Différentes façons de rentrer les puissances :
    formule = formule.replace("^", "**").replace(u'²',"**2").replace(u'³',"**3")
    formule = formule.replace(u'\u2074',"**4").replace(u'\u2075',"**5").replace(u'\u2076',"**6")
    formule = formule.replace(u'\u2077',"**7").replace(u'\u2078',"**8").replace(u'\u2079',"**9")

    # Caractères unicode
    # remplace le tiret long en '-'
    formule = formule.replace(u'\u2013', "-").replace(u'\u2212', "-")


    # Conversion écriture décimale infinie périodique -> fraction
    def to_frac(reg):
        p_entiere, p_decimale, periode = reg.groups()
        chaine = '((' + p_entiere.lstrip('0') + p_decimale
        chaine += '+' + (periode.lstrip('0') or '0') + '/' + len(periode)*'9'
        chaine += ')/1' + len(p_decimale)*'0' + ')'
        return chaine
    formule = re.sub(r"(\d+)[.,](\d*)\[(\d+)\]", to_frac, formule)
    # exemple: 17.03[45] -> ((1703+45/99)/100)
    # Après calcul, on on obtiendra bien 17.03454545... = 9369/550


    # il est plus intuitif d'utiliser le symbole % pour les pourcentages, et mod pour le modulo.
    if LaTeX:
        formule = formule.replace("\\%", "/100 ")
    formule = formule.replace("%", "/100 ")
    formule = _simplifier(formule)
    formule = formule.replace(" mod ", "%").replace(" modulo ", "%")
    formule = formule.replace(")mod ", ")%").replace(")modulo ", ")%")
    formule = formule.replace("}mod ", "}%").replace("}modulo ", "}%")

    # interprétation de 0+ et de 0- (entre autres)
    formule = formule.replace("+)", ",'+')").replace("-)", ",'-')")

    # conversion degrés -> radians
    formule = formule.replace(u'°', '*pi/180')

    if OOo:
        # Gestion des matrices.
        # NB: à faire en premier, en tout cas avant de remplacer '{}' par '()'.
        deb = formule.find("matrix{")
        while deb != -1:
            matrice, reste = _arguments_latex(formule[deb + 6:], 1)
            matrice = 'mat([[' + matrice[1:-1].replace(r'##', '],[').replace('#', ',') + ']])'
            formule = formule[:deb] + matrice + reste
            deb = formule.find("matrix{", deb)


    #Conversion de quelques formules latex ultra-fréquentes (comme \frac, \dfrac, \tfrac, \sqrt, suppression de \nombre, etc.).
    if LaTeX:
        # Gestion des matrices.
        # NB: à faire en premier, en tout cas avant de remplacer '\\'.
        for substr in (r"matrix",
                        r"pmatrix",
                        r"bmatrix",
                        r"vmatrix",
                        r"Vmatrix",
                        r"smallmatrix",
                        ):
            while True:
                deb = formule.find(r"\begin{" + substr + "}")
                if deb == -1:
                    break
                fin = formule.find(r"\end{" + substr + "}", deb)
                avant = formule[:deb]
                coeur = formule[deb + len(substr) + 8:fin].replace('\n', '').rstrip('\\')
                apres = formule[fin + len(substr) + 6:]
                coeur = 'mat([[' + coeur.replace(r'\\', '],[').replace('&', ',') + ']])'
                formule = avant + coeur + apres
        # Suppression ou remplacement de commandes courantes
        for pattern, repl in dictionnaire_latex_commandes.items():
            formule = re.sub("\\\\" + pattern + "(?![A-Za-z])", repl, formule)
        for substr, repl in dictionnaire_latex_special.items():
            formule = formule.replace(substr, repl)
        formule = _simplifier(formule)

        # '\dfrac{a}{b}' devient '(a)/(b)' (idem pour \frac et \tfrac)
        formule = _convertir_latex_frac(formule)

        formule = formule.replace("{", "(").replace("}", ")")


    if OOo:
        # transforme les accolades en parentheses (utile par exemple pour les fonctions issues d'OpenOffice.org).
        formule = formule.replace("{", "(").replace("}", ")")
        formule = regsub("[ ]?(left|right)[])([]", formule, lambda s: s[-1])
        # De même, les notations "times", "over" et "sup" d'OpenOffice.org sont converties.
        formule = regsub("\Wtimes\W", formule, lambda s: (s[0] + '*' + s[-1]).strip())
        formule = regsub("\Wover\W", formule, lambda s: (s[0] + '/' + s[-1]).strip())
        formule = regsub("\Wsup\W", formule, lambda s: (s[0] + '**' + s[-1]).strip())
        formule = formule.replace('infinity', 'oo')

    # Conversion des | | **nom imbriqués** en abs().
    # NB: il est impossible de convertir des | | imbriqués, car certaines
    # expressions sont ambigues, par exemple |x|y|z| peut être compris comme
    # abs(x)*y*abs(z) ou abs(x*abs(y)*z).
    formule = regsub('[|][^|]+[|]', formule, (lambda s: 'abs(%s)' % s[1:-1]))

    formule = _ajouter_mult_manquants(formule, fonctions = fonctions, verbose = verbose, mots_cles = mots_cles)

    if verbose:
        print '5', formule

    # n! devient factoriel(n).
    formule = regsub("\w+[!]", formule, (lambda s: 'factoriel(%s)' % s[:-1]))


    # (5 2) devient binomial(5, 2)
    formule = regsub("[(]%s[ ]+%s[)]" % (NBR, NBR), formule,
                       lambda s: 'binomial(%s)' % ",".join(s[1:-1].split()))

    if verbose:
        print '6', formule

    # f' devient derivee(f), f'' devient derivee(derivee(f)), etc.
    def prime2derivee(s):
        n = s.count("'") # nombre de '
        return n*"derivee(" + s.rstrip("'") + n*")"

    formule = regsub(VAR + "[']+", formule, prime2derivee)

    formule = formule.replace("`", "'")

    if verbose:
        print '7', formule

    if simpify:
        def transformer(chaine):
            if "." in chaine:
                return "__decimal__('" + chaine + "')"
            else:
                return "__sympify__(" + chaine + ")"
        formule = regsub(NBR, formule, transformer)

    formule = _inject_inner_str(formule, substrings_list)

    if verbose is not False:
        debug(formule, "[formule transformee]")

    return formule


def simplifier_ecriture(formule):
    formule = formule.replace('**', '^')
    formule = formule.replace('*(', '(')
    formule = formule.replace(')*', ')')
    formule = re.sub(r'[*](?![-+.0-9])', ' ', formule)
    return formule


##def simplifier_ecriture(formule):
##    # Simplification de l'écriture des puissances
##    formule = formule.replace('**', '^')
##
##    # Simplification de l'écriture des racines
##    def simp_sqrt(m):
##        return 'sqrt(' + m.group(1) + ')'
##    formule = re.sub(r'\(([^()]+)\)\^\(1/2\)', simp_sqrt, formule)
##    formule = re.sub(r'([A-Za-z_][A-Za-z_0-9]*|[0-9]+)\^\(1/2\)', simp_sqrt, formule)

##    # Simplification de l'écriture des produits
##    formule = formule.replace(')*(', ')(')
##    def simp_mul(m):
##        return m.group(0).replace('*', ' ')
##    formule = re.sub(r'(?<![0-9.A-Za-z_])[0-9.A-Za-z_]+([*][A-Za-z_])+', simp_mul, formule)
##    return formule


def _fast_closing_bracket_search(string, start=0):
    u"""Recherche rudimentaire de la parenthèse fermante correspondante.

    Les parenthèses imbriquées sont gérées, mais pas la détection des chaînes de
    caractères qui peuvent fausser les résultats.
    Tant que cette fonction est appliquée à des expressions mathématiques,
    cela ne pose pas problème.

    La recherche commence à partir de la position `start`, qui doit correspondre
    à une parenthèse ouvrante dans la chaîne.

    Retourne la position de la parenthèse fermante.
    """
    # k : position de la 1ère parenthèse rencontrée
    k = start + 1
    # level : profondeur des parenthèses imbriquées.
    level = 1
    while True:
        i = string.find('(', k)
        j = string.find(')', k)
        if i == j == -1:
            # Plus aucune parenthèse.
            raise ValueError, "No matching parenthesis, or string doesn't start with `(`."
        elif i < j and i != -1:
            # La 1ère parenthèse rencontrée est ouvrante `(`.
            level += 1
            k = i + 1
        else:
            # La 1ère parenthèse rencontrée est fermante `)`.
            level -= 1
            k = j + 1
        if level == 0:
            return k


def _fast_opening_bracket_search(string):
    u"""Recherche rudimentaire de la parenthèse ouvrante correspondante.

    Puisqu'on cherche la parenthèse ouvrante, la recherche s'effectue donc
    de droite à gauche.

    Les parenthèses imbriquées sont gérées, mais pas la détection des chaînes de
    caractères qui peuvent fausser les résultats.
    Tant que cette fonction est appliquée à des expressions mathématiques,
    cela ne pose pas problème.

    La chaîne doit se terminer par une parenthèse fermante.

    Retourne la position de la parenthèse ouvrante.
    """
    # k : position de la 1ère parenthèse rencontrée
    k = -1
    # level : profondeur des parenthèses imbriquées.
    level = 1
    while True:
        i = string.rfind('(', None, k)
        j = string.rfind(')', None, k)
        if i == j == -1:
            # Plus aucune parenthèse.
            raise ValueError, "No matching parenthesis, or string doesn't end with `)`."
        elif i > j:
            # La 1ère parenthèse rencontrée est ouvrante `(`.
            level -= 1
            k = i
        else:
            # La 1ère parenthèse rencontrée est fermante `)`.
            level += 1
            k = j
        if level == 0:
            return k


def _strip_parenthesis(string):
    u"""Supprime les parenthèses autour de l'expression, si elles correspondent."""
    while string and string[0] == '(':
        if _fast_closing_bracket_search(string) == len(string):
            string = string[1:-1]
        else:
            break
    return string


def _rechercher_numerateur(chaine):
    u"""Part de la fin de la chaîne, et remonte la chaîne pour chercher
    le plus grand groupe possible pouvant correspondre à un numérateur.

    Retourne la position du début du numérateur dans la chaîne.

    La chaîne doit être préparée au préalable. En particulier, l'opérateur utilisé
    pour les puissances est  `^`, et non `**`, et les espaces autour des opérateurs
    / et ^ sont supprimés.
    """
    if not chaine:
        return
    fonctions = ('cos', 'sin', 'tan', 'ln', 'log', 'exp', 'sqrt')
    if chaine[-1] == ')':
        try:
            deb = _fast_opening_bracket_search(chaine)
            # Si les parenthèses sont précédées par une fonction, la fonction
            # fait aussi partie du numérateur. Par exemple, dans `cos(x)/2`,
            # le numérateur est `cos(x)`, et pas seulement `(x)`.
            for fonction in fonctions:
                if chaine.endswith(fonction, 0, deb):
                    deb -= len(fonction)
        except ValueError:
            # Parenthésage incorrect.
            return
    else:
        # Le caractère @ est utilisé par `_convertir_en_latex` pour remplacer les
        # fractions déjà détectées.
        m = re.search('(%s|@)$' % NBR_OR_VAR, chaine)
        if m is None:
            # Rien qui ressemble à un numérateur
            return
        deb = m.start()
    # La puissance est prioritaire sur la division.
    # Dans une expression du genre `2^x/3`, le numérateur est `2^x`, et non `x`.
    if deb != 0 and chaine[deb - 1] == '^':
        deb = _rechercher_numerateur(chaine[:deb - 1])
    elif deb > 1 and chaine[deb - 2:deb] == '^-':
        deb = _rechercher_numerateur(chaine[:deb - 2])
    return deb


def _rechercher_denominateur(chaine):
    u"""Part de la fin de la chaîne, et remonte la chaîne pour chercher
    le plus grand groupe possible pouvant correspondre à un numérateur.

    Retourne la position du début du numérateur dans la chaîne.

    La chaîne doit être préparée au préalable. En particulier, l'opérateur utilisé
    pour les puissances est  `^`, et non `**`, et les espaces autour des opérateurs
    / et ^ sont supprimés.
    """
    if not chaine:
        return
    fonctions = ('cos', 'sin', 'tan', 'ln', 'log', 'exp', 'sqrt')
    # Si le dénominateur commence par un nom de fonction, on continue à chercher
    # après ce nom...
    fin = 0
    for fonction in fonctions:
        if chaine.startswith(fonction):
            fin += len(fonction)
    if chaine[fin] == '(':
        try:
            fin += _fast_closing_bracket_search(chaine[fin:])
        except ValueError:
            # Parenthésage incorrect.
            return
    else:
        m = re.search('(%s)' % NBR_SIGNE_OR_VAR, chaine[fin:])
        if m is None:
            # Rien qui ressemble à un numérateur
            return
        fin += m.end()
    # La puissance est prioritaire sur la division.
    # Dans une expression du genre `2^x/3`, le numérateur est `2^x`, et non `x`.
    if fin < len(chaine) and chaine[fin] == '^':
        fin += _rechercher_denominateur(chaine[fin + 1:]) + 1
    elif chaine[fin:fin + 2] == '^-':
        fin += _rechercher_denominateur(chaine[fin + 2:]) + 2
    return fin


def _convertir_en_latex(chaine):
    ##import time
    ##time0 = time.time()

    # Puissances
    chaine = chaine.replace("**", "^")

    # On remplace +- par -, -- par +, --- par -, etc.
    def simpl(m):
        return '-' if m.group(0).count('-')%2 else '+'
    chaine = re.sub('[-+]{2,}', simpl, chaine)
    if chaine != '+':
        chaine = chaine.lstrip('+')


    # --------------------------------
    # Suppression des espaces inutiles
    # --------------------------------
    # Les espaces inutiles ne sont pas gênants en LaTeX, mais leur suppresion
    # simplifie le traitement ultérieur de la chaîne de caractères.
    chaine = re.sub(r'[ ]+', ' ', chaine)
    chaine = re.sub(r'[ ]?([/^()+*-])[ ]?', (lambda m: m.group(1)), chaine)

    # ------------------------
    # Conversion des fractions
    # ------------------------
    # On traite maintenant le (délicat) cas des fractions,
    # ie. 2/3, mais aussi (pi+3)/(5-e)^2, ou cos(2)/3
    securite = 1000
    while '/' in chaine:
        # Voir plus bas l'explication pour les 2 `while` imbriqués.
        fractions = []
        while '/' in chaine:
            securite -= 1
            if securite < 0:
                raise RuntimeError, "Boucle probablement infinie."
            i = chaine.find("/")
            # Début de la fraction
            deb = _rechercher_numerateur(chaine[:i])
            if deb is None:
                if param.debug:
                    warning("Expression incorrecte: numerateur introuvable.")
                return chaine
            # Fin de la fraction
            _fin = _rechercher_denominateur(chaine[i + 1:])
            if _fin is None:
                if param.debug:
                    warning("Expression incorrecte: denominateur introuvable.")
                return chaine
            fin = i + 1 + _fin

            # Suppression des parenthèses inutiles.
            numerateur = _strip_parenthesis(chaine[deb:i])
            denominateur = _strip_parenthesis(chaine[i + 1:fin])
            fractions.append(r'\frac{%s}{%s}' % (numerateur, denominateur))
            # On marque la position de la fraction en la remplaçant par `@`,
            # au lieu de la remplacer directement par le code LaTeX.
            # En effet, un mixte de code LaTeX et de code Python serait trop
            # délicat à traiter.
            # Ce n'est qu'une fois qu'on aura identifié toutes les fractions
            # qu'on remplacera tous les `@` par les fractions correspondantes.
            chaine = chaine[:deb] + '@' + chaine[fin:]

            # Il se peut qu'après avoir effectué ce remplacement, il reste des `/`
            # en fin de chaîne, à l'intérieur du dénominateur d'une grande fraction.
            # Dans ce cas, on recommence le processus (d'où les 2 `while` imbriqués).
            # La chaîne contient alors un mixte de fractions LaTeX et de fractions
            # Python.
            # Cependant, dans ce cas précis, ce n'est pas gênant : ce qui importe
            # en effet, pour que `_rechercher_numerateur` et `_rechercher_denominateur`
            # détectent bien le numérateur et le dénominateur d'une fraction Python,
            # c'est qu'il n'y ait pas de fraction LaTeX imbriquée dedans.
            # Et c'est bien le cas : comme le parser fonctionne de gauche à droite,
            # et remplace chaque fraction trouvée par `@`, les fractions Python
            # qui restent sont forcément contenues dans un dénominateur
            # d'une fraction LaTeX, qui a été remplacée par `@` avant que son
            # dénominateur ait pu être parsé.

        for fraction in reversed(fractions):
            chaine = rreplace(chaine, '@', fraction, 1)
        assert '@' not in chaine

    # --------------------
    # Autres remplacements
    # --------------------
    chaine = re.sub(r"(?<!\w|\\)(pi|e|sin|cos|tan|ln|log|exp|sqrt)(?!\w)", lambda m:"\\" + m.group(), chaine)
    chaine = re.sub(r"(?<!\w|\\)oo(?!\w)", lambda m:"\\infty", chaine)
    for func in ('sqrt', '^'):
        i = 0
        while True:
            i = chaine.find(func + '(', i)
            if i == -1:
                break
            i += len(func)
            j = _fast_closing_bracket_search(chaine, start=i)
            if j is None:
                if param.debug:
                    warning("Expression incorrecte: %s." % chaine)
                return chaine
            chaine = chaine[:i] + '{' + chaine[i + 1:j - 1] + '}' + chaine[j:]

    chaine = re.sub(r'\*' + NBR_SIGNE, lambda m: r'\times ' + m.group()[1:], chaine)
    chaine = chaine.replace("*", " ")

    # Puissances : 2^27 -> 2^{27}
    chaine = re.sub(r'(?<=\^)' + NBR_SIGNE, (lambda m: '{' + m.group() + '}'), chaine)

    if chaine.startswith(r'\infty'):
        chaine = '+' + chaine

    return _strip_parenthesis(chaine)


def convertir_en_latex(chaine, mode='$'):
    u"""Convertit une chaine représentant un calcul en Python, en du code LaTeX.

    modes actuels: '$', None

    L'intérêt de ne pas passer par sympy, c'est que le code n'a pas besoin
    d'être évalué. Si le code était évalué par sympy, cela pourrait modifier
    l'ordre des termes (par exemple, transformer `2-x` en `-x+2`).
    """
    chaine = _convertir_en_latex(chaine)
    if mode == '$':
        chaine = "$" + chaine + "$"
    return chaine


def latex2mathtext(chaine):
    u"""Convertit la chaîne pour qu'elle puisse être affichée par mathtext.

    Matplotlib offre 2 possibilités pour l'affichage de chaînes LaTeX :

        * soit utiliser une installation LaTeX existante,
        * soit utiliser son propre moteur de rendu, mathtext.

    Le rendu de matplotlib.mathtext est loin d'avoir la qualité du vrai LaTeX,
    mais il ne nécessite pas d'avoir LaTeX installé, il est bien plus rapide,
    et il permet l'export au format vectoriel (matplotlib utilise dvi2png sinon).

    C'est donc le format utilisé par défaut.
    """
    if '$' in chaine:
        if chaine.startswith(r"$\begin{bmatrix}"):
            chaine = chaine.replace(r"\begin{bmatrix}", r'\left({')
            chaine = chaine.replace(r"\end{bmatrix}", r'}\right)')
            chaine = chaine.replace(r"&", r'\,')
        if r'\left' in chaine:
            chaine = chaine.replace(r'\left\{', r'\left{')
            chaine = chaine.replace(r'\right\}', r'\right}')
    return chaine


def mathtext_parser(txt):
    return _mathtext_raw_parser(latex2mathtext(txt))


def tex_dollars(txt):
    u"Rajoute des $ si l'expression LaTeX ainsi obtenue est correcte."
    try:
        mathtext_parser('$' + txt + '$')
        return '$' + txt + '$'
    except Exception:
        return txt


# HACK pour contourner un bug de matplotlib mathtext (v 1.1.1)
# Les délimiteurs \left et \right ne sont pas gérés correctement
# (à supprimer probablement quand matplotlib 1.2 sera dans les dépôts Ubuntu)
def _hacked_auto_sized_delimiter(self, s, loc, toks):
    #~ print "auto_sized_delimiter", toks
    front, middle, back = toks
    state = self.get_state()
    height = max([getattr(x, 'height', 0) for x in middle])
    depth = max([getattr(x, 'depth', 0) for x in middle])
    parts = []
    # \left. and \right. aren't supposed to produce any symbols
    if front != '.':
        parts.append(AutoHeightChar(front, height, depth, state))
    parts.extend(middle.asList())
    if back != '.':
        parts.append(AutoHeightChar(back, height, depth, state))
    hlist = Hlist(parts)
    return hlist


# HACK pour contourner un bug de matplotlib mathtext (v 1.1.1)
# L'unicode est mal géré: 'str' utilisé à la place de 'basestring'.
def _hacked_subsuperscript(self, s, loc, toks):
    assert(len(toks)==1)
    # print 'subsuperscript', toks

    nucleus = None
    sub = None
    super = None

    # Pick all of the apostrophe's out
    napostrophes = 0
    new_toks = []
    for tok in toks[0]:
        if isinstance(tok, basestring) and tok not in ('^', '_'):
            napostrophes += len(tok)
        else:
            new_toks.append(tok)
    toks = new_toks

    if len(toks) == 0:
        assert napostrophes
        nucleus = Hbox(0.0)
    elif len(toks) == 1:
        if not napostrophes:
            return toks[0] # .asList()
        else:
            nucleus = toks[0]
    elif len(toks) == 2:
        op, next = toks
        nucleus = Hbox(0.0)
        if op == '_':
            sub = next
        else:
            super = next
    elif len(toks) == 3:
        nucleus, op, next = toks
        if op == '_':
            sub = next
        else:
            super = next
    elif len(toks) == 5:
        nucleus, op1, next1, op2, next2 = toks
        if op1 == op2:
            if op1 == '_':
                raise ParseFatalException("Double subscript")
            else:
                raise ParseFatalException("Double superscript")
        if op1 == '_':
            sub = next1
            super = next2
        else:
            super = next1
            sub = next2
    else:
        raise ParseFatalException(
            "Subscript/superscript sequence is too long. "
            "Use braces { } to remove ambiguity.")

    state = self.get_state()
    rule_thickness = state.font_output.get_underline_thickness(
        state.font, state.fontsize, state.dpi)
    xHeight = state.font_output.get_xheight(
        state.font, state.fontsize, state.dpi)

    if napostrophes:
        if super is None:
            super = Hlist([])
        for i in range(napostrophes):
            super.children.extend(self.symbol(s, loc, ['\prime']))

    # Handle over/under symbols, such as sum or integral
    if self.is_overunder(nucleus):
        vlist = []
        shift = 0.
        width = nucleus.width
        if super is not None:
            super.shrink()
            width = max(width, super.width)
        if sub is not None:
            sub.shrink()
            width = max(width, sub.width)

        if super is not None:
            hlist = HCentered([super])
            hlist.hpack(width, 'exactly')
            vlist.extend([hlist, Kern(rule_thickness * 3.0)])
        hlist = HCentered([nucleus])
        hlist.hpack(width, 'exactly')
        vlist.append(hlist)
        if sub is not None:
            hlist = HCentered([sub])
            hlist.hpack(width, 'exactly')
            vlist.extend([Kern(rule_thickness * 3.0), hlist])
            shift = hlist.height
        vlist = Vlist(vlist)
        vlist.shift_amount = shift + nucleus.depth
        result = Hlist([vlist])
        return [result]

    # Handle regular sub/superscripts
    shift_up = nucleus.height - SUBDROP * xHeight
    if self.is_dropsub(nucleus):
        shift_down = nucleus.depth + SUBDROP * xHeight
    else:
        shift_down = SUBDROP * xHeight
    if super is None:
        # node757
        sub.shrink()
        x = Hlist([sub])
        # x.width += SCRIPT_SPACE * xHeight
        shift_down = max(shift_down, SUB1)
        clr = x.height - (abs(xHeight * 4.0) / 5.0)
        shift_down = max(shift_down, clr)
        x.shift_amount = shift_down
    else:
        super.shrink()
        x = Hlist([super, Kern(SCRIPT_SPACE * xHeight)])
        # x.width += SCRIPT_SPACE * xHeight
        clr = SUP1 * xHeight
        shift_up = max(shift_up, clr)
        clr = x.depth + (abs(xHeight) / 4.0)
        shift_up = max(shift_up, clr)
        if sub is None:
            x.shift_amount = -shift_up
        else: # Both sub and superscript
            sub.shrink()
            y = Hlist([sub])
            # y.width += SCRIPT_SPACE * xHeight
            shift_down = max(shift_down, SUB1 * xHeight)
            clr = (2.0 * rule_thickness -
                   ((shift_up - x.depth) - (y.height - shift_down)))
            if clr > 0.:
                shift_up += clr
                shift_down += clr
            if self.is_slanted(nucleus):
                x.shift_amount = DELTA * (shift_up + shift_down)
            x = Vlist([x,
                       Kern((shift_up - x.depth) - (y.height - shift_down)),
                       y])
            x.shift_amount = shift_down

    result = Hlist([nucleus, x])
    return [result]




matplotlib.mathtext.Parser.auto_sized_delimiter = _hacked_auto_sized_delimiter
matplotlib.mathtext.Parser.subsuperscript = _hacked_subsuperscript