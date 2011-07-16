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

from sympy import Expr
from ..pylib import regsub, split_around_parenthesis, debug



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
NBR_SIGNE = "(?:(?<![.A-Za-z0-9_])(?:[+-]?[ ]?(?:[0-9]*[.][0-9]+|[0-9]+[.]?)))"
# Nombre sans signe
NBR = "(?:(?<![.A-Za-z0-9_])(?:[0-9]*[.][0-9]+|[0-9]+[.]?))"
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

    >>> from mathlib.parsers import _arguments_latex
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

    >>> from mathlib.parsers import _convertir_latex_frac
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
        elif s[0] == '.' and s[1].isalnum():
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


def traduire_formule(formule = "", fonctions = (), OOo = True, LaTeX = True, changer_separateurs = False, separateurs_personnels = (",", ";"), simpify = False, verbose = None, mots_cles = tuple(keyword.kwlist)):

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

    # On peut choisir comme separateur decimal la virgule (convention francaise en particulier)
    if changer_separateurs:
        formule = formule.replace(separateurs_personnels[0], ".").replace(separateurs_personnels[1], ",")

    formule = _simplifier(formule)


    if verbose:
        print '0', formule

    # Différentes façons de rentrer les puissances :
    formule = formule.replace("^", "**").replace(u'²',"**2").replace(u'³',"**3")

    # Caractères unicode
    # remplace le tiret long en '-'
    formule = formule.replace(u'\u2013', "-").replace(u'\u2212', "-")


    # Conversion écriture décimale infinie périodique -> fraction
    def to_frac(reg):
        p_entiere, p_decimale, periode = reg.groups()
        chaine = '((' + p_entiere + p_decimale
        chaine += '+' + (periode.lstrip('0') or '0') + '/' + len(periode)*'9'
        chaine += ')/1' + len(p_decimale)*'0' + ')'
        return chaine
    formule = re.sub(r"(\d+)[.](\d*)\[(\d+)\]", to_frac, formule)
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
            deb = formule.find(r"\begin{" + substr + "}")
            while deb != -1:
                fin = formule.find(r"\end{" + substr + "}", deb)
                avant = formule[:deb]
                coeur = formule[deb + len(substr) + 8:fin].replace('\n', '').rstrip('\\')
                apres = formule[fin + len(substr) + 6:]
                coeur = 'mat([[' + coeur.replace(r'\\', '],[').replace('&', ',') + ']])'
                formule = avant + coeur + apres
                deb = formule.find(substr, deb)
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

    formule = _ajouter_mult_manquants(formule, fonctions = fonctions, verbose = verbose, mots_cles = mots_cles)

    if verbose:
        print '5', formule

    # n! devient factoriel(n).
    formule = regsub("\w+[!]", formule, lambda s: 'factoriel(' + s[:-1] + ')')


    # (5 2) devient binomial(5, 2)
    formule = regsub("[(]" + NBR + "[ ]+" + NBR + "[)]", formule, lambda s: 'binomial(' + ",".join(s[1:-1].split()) + ')')

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
