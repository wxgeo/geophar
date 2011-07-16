# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------##
#              WxGeometrie               #
#                tabvar                  #
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


import re

from sympy import sympify, oo, nan, limit, Symbol

from .tablatexlib import convertir_en_latex, test_parentheses, resoudre
from ...mathlib.custom_functions import ensemble_definition, custom_str
from ...mathlib.intervalles import R, conversion_chaine_ensemble
from ...mathlib.interprete import Interprete
from ... import param


def _auto_tabvar(chaine = '', derivee = True, limites = True, decimales = None):
    u"""Génère le code du tableau de variations d'une fonction à variable réelle.

    On suppose que la fonction est de classe C1 sur tout intervalle ouvert de son
    ensemble de définition.
    Par ailleurs, les zéros de sa dérivée doivent être calculables pour la librairie sympy.
    """
    # TODO: gérer le paramètre 'decimales'
    str = custom_str
    chaine_initiale = chaine

    # Ensemble de définition
    if ' sur ' in chaine:
        chaine, ens_def = chaine.split(' sur ')
        ens_def = conversion_chaine_ensemble(ens_def, utiliser_sympy = True)
    else:
        ens_def = R

    # Légende de la dernière ligne
    if '=' in chaine:
        legende, chaine = chaine.split('=', 1)
    else:
        legende = 'f'

    # Conversion en expression sympy
    interprete = Interprete()
    interprete.evaluer(chaine)
    expr = interprete.ans()
    # Récupération de la variable
    variables = expr.atoms(Symbol)
    if len(variables) > 1:
        raise ValueError, "Il y a plusieurs variables dans l'expression !"
    elif not variables:
        raise ValueError, "Il n'y a pas de variable dans l'expression !"
    var = variables.pop()
    # Récupération de l'ensemble de définition
    ens_def *= ensemble_definition(expr, var)
    valeurs_interdites = []
    xmin = ens_def.intervalles[0].inf
    if not ens_def.intervalles[0].inf_inclus:
        valeurs_interdites.append(xmin)
    sup = xmin
    for intervalle in ens_def.intervalles:
        inf = intervalle.inf
        if sup != inf:
            # Il y a un 'trou' dans l'ensemble de définition (ex: ]-oo;0[U]2;+oo[)
            raise NotImplementedError
            #TODO: utiliser || pour noter un intervalle interdit
        sup = intervalle.sup
        if not intervalle.sup_inclus:
            valeurs_interdites.append(sup)
    xmax = sup

    # On étudie la dérivée
    derivee = expr.diff(var)
    ens_def_deriv = ensemble_definition(derivee, var)
    solutions = [sol for sol in resoudre(derivee, var) if sol.is_real]

    # On liste toutes les valeurs remarquables pour la fonction
    # NB: on les convertit toutes au format Sympy, pour qu'il n'y ait pas
    # par exemple deux zéros "différents" listés (int(0), et sympy.Integer(0))
    valeurs = {sympify(xmin): None, sympify(xmax): None}
    for sol in solutions:
        if xmin <= sol <= xmax:
            valeurs[sympify(sol)] = 0
    for val in valeurs_interdites:
        if xmin <= val <= xmax:
            valeurs[sympify(val)] = nan
    liste_valeurs = sorted(valeurs)

##    def reel(val):
##        return val.is_real and -oo < val < oo

    # On génère le code, valeur après valeur
    code = str(var) + ';' + legende + ':'
    if param.debug and param.verbose:
        print "liste_valeurs", liste_valeurs, valeurs, set(valeurs), [type(val) for val in valeurs]
    for i, valeur in enumerate(liste_valeurs):
        code_point = '(' + str(valeur) + ';'
        if valeur == xmin:
            lim_plus = limit(expr, var, valeur, dir = '+')
            if valeur != -oo and valeur in valeurs_interdites:
                code_point += '|'
            # On n'affiche les limites que si 'limites == True'
            if limites or (valeur != -oo and valeur not in valeurs_interdites):
                code_point += str(lim_plus)
        elif valeur == xmax:
            lim_moins = limit(expr, var, valeur, dir = '-')
            # On n'affiche les limites que si 'limites == True'
            if limites or (valeur != +oo and valeur not in valeurs_interdites):
                code_point += str(lim_moins)
            if valeur != +oo and valeur in valeurs_interdites:
                code_point += '|'
        else:
            if valeur in valeurs_interdites:
                # On n'affiche les limites que si 'limites == True'
                lim_plus = limit(expr, var, valeur, dir = '+')
                lim_moins = limit(expr, var, valeur, dir = '-')
                if limites:
                    code_point += str(lim_moins) + '|' + str(lim_plus)
                else:
                    code_point += '|'
            else:
                # On calcule simplement l'image
                lim_moins = lim_plus = expr.subs(var, valeur)
                code_point += str(lim_moins)
        if valeur not in (-oo, oo) and valeur not in ens_def_deriv:
            # La dérivée n'est pas définie en cette valeur
            code_point += ';|'
        code_point += ')'
        if i > 0:
            #print lim_precedente, lim_moins
            if lim_precedente < lim_moins:
                code += ' << '
            elif lim_precedente > lim_moins:
                code += ' >> '
            else:
                code += ' == '
        code += code_point
        lim_precedente = lim_plus


    if param.debug and param.verbose:
        print 'Code TABVar:', code
    return tabvar(code, derivee = derivee) + '% ' + chaine_initiale + '\n'




def tabvar(chaine = "", derivee = True, limites = True, decimales = None):
    u"""Indiquer les variations de la fonction.

Exemples :
f: (-oo;3) << (1;2;0) << (3;+oo|-oo) << (5;2) >> (+oo;-oo)
\\sqrt{x};(\\sqrt{x})';x: 0;0;| << +oo;+oo"""

    chaine_originale = chaine = chaine.strip()


    #ligne_variable = ligne_derivee = ligne_fonction = ""

    if not ':' in chaine and not '>>' in chaine and not '==' in chaine and not '<<' in chaine:
        return _auto_tabvar(chaine, derivee = derivee, limites = limites, decimales = decimales)

    chaine = chaine.replace("-oo", "-\\infty").replace("+oo", "+\\infty")

    liste = chaine.split(":", 1)

    if len(liste) == 1 or len(liste[0].strip()) == 0:
        ligne_variable = "x"
        ligne_derivee = "f'(x)"
        ligne_fonction = "f"

    else:
        legende, chaine = liste
        legende = legende.split(";")

        if len(legende) > 1:
            ligne_variable = legende[0].strip()
            ligne_fonction = legende[1].strip()

            if len(legende) > 2:
                ligne_derivee = legende[2].strip()
            else:
                deb = ligne_fonction.find("(")
                if deb == -1:
                    ligne_derivee = ligne_fonction[:].strip() + "'(" + ligne_variable + ")"
                else:
                    ligne_derivee = ligne_fonction[:deb].strip() + "'(" + ligne_variable + ")"

        else: # un seul argument pour la legende: c'est alors la fonction
            ligne_fonction = legende[0].strip()
            deb = ligne_fonction.find("(")
            fin = ligne_fonction.find(")")
            if deb == -1:
                ligne_variable = "x"
                ligne_derivee = ligne_fonction + "'(x)"
            else:
                ligne_variable = ligne_fonction[deb+1:fin].strip()
                ligne_derivee = ligne_fonction[:deb].strip() + "'(" + ligne_variable + ")"




    # on découpe la chaîne, en une suite contenant soit les valeurs de x, f(x) (et éventuellement f'(x)),
    # soit le sens de variation entre ces valeurs.
    # ex: "-oo;3 << 1;2 >> 3;-oo|+oo << 5;2 << +oo;+oo" devient
    # ["-oo;3", "<<", "1;2", ">>", "3;-oo|+oo", "<<", "5;2", "<<", "+oo;+oo"]

    sequence = re.split(r"(>>|<<|==|\|\|)", chaine.strip())

    if not sequence[0]:
        # en l'absence d'indication, x varie de -oo...
        sequence[0] = "-\\infty;"
    if not sequence[-1]:
        # ... à +oo
        sequence[-1] = "+\\infty;"

    def formater(chaine):
        chaine = chaine.strip()
        if chaine not in ("<<", ">>", "==", '||'):
            # Les valeurs sont éventuellement encadrées par des parenthèses (facultatives) pour plus de lisibilité.
            # On enlève ici les parenthèses. ex: (-2;0) devient -2;0
            if chaine[0] == '(' and chaine[-1] == ')' and test_parentheses(chaine[1:-1]):
                chaine = chaine[1:-1]
            if ";" not in chaine:
                chaine += ";" # il faut au minimum un ";" pour indiquer l'absence de valeur
        return chaine

    sequence = [formater(elt) for elt in sequence]

    # On effectue un premier balayage uniquement pour detecter les niveaux.
    niveaux = [] # chaque element de la liste correspond a une portion de tableau de variation comprise entre deux valeurs interdites.
    # A chacune de ces portions va correspondre un doublon (niveau minimal atteint, niveau maximal atteint) qu'on ajoute a la liste.
    niveau = niveau_minimum = niveau_maximum = 0
    for elt in sequence:
        if (";" in elt and "|" in elt.split(";")[1]) \
                or elt == '||': # presence d'une valeur interdite
            niveaux.append((niveau_minimum, niveau_maximum))
            niveau = niveau_minimum = niveau_maximum = 0
        else:
            if elt == "<<":
                niveau += 1
            elif elt == ">>":
                niveau -= 1
            if niveau < niveau_minimum:
                niveau_minimum = niveau
            if niveau > niveau_maximum:
                niveau_maximum = niveau
    niveaux.append((niveau_minimum, niveau_maximum))
    ecart_maximal = max(val[1] - val[0] for val in niveaux)

    # L'environnement tabvar ne permet pas de positionner un texte entre deux lignes.
    # Si, dans la 3e partie du tableau (la fonction elle-même),
    # le nombre de lignes (c-à-d. ecart_maximal+1) est impair,
    # on décale le texte légèrement vers le haut pour le centrer verticalement (via raisebox).
    if ecart_maximal%2:
        ligne_fonction = "\\niveau{" + str((ecart_maximal+2)//2) +"}{" + str(ecart_maximal+1) + "}\\raisebox{0.5em}{$" + ligne_fonction + "$}"
    else:
        ligne_fonction = "\\niveau{" + str((ecart_maximal+2)//2) +"}{" + str(ecart_maximal+1) + "}" + ligne_fonction

    #print "niveaux: ", niveaux
    colonnes = 'C|' # ex: 'CCCCC' pour 5 colonnes centrées
    portion = 0 # indique la derniere portion traitee (les portions sont delimitees par les bornes de l'ensemble de definition et les valeurs interdites)
    debut = True

    def en_latex(chaine):
        return convertir_en_latex(chaine)[1:-1]

    # Deuxieme et dernier balayage :
    # on parcourt maintenant la liste pour construire colonne par colonne le tableau de variations.
    for i in xrange(len(sequence)):
        # on justifie apres chaque etape, ce qui rend une eventuelle relecture du tableau plus agreable
        n = max(len(ligne_variable), len(ligne_derivee), len(ligne_fonction))
        ligne_variable = ligne_variable.ljust(n)
        ligne_derivee = ligne_derivee.ljust(n)
        ligne_fonction = ligne_fonction.ljust(n)

        ligne_variable += "&"
        if debut:
            debut = False
            ligne_fonction += "&\\niveau{" + str(1-niveaux[portion][0]) +"}{" + str(ecart_maximal+1) + "}"
        else:
            ligne_fonction += "&"
        ligne_derivee += "&"

        elt = sequence[i]
        if elt in (">>", "<<", "==", "||"):  # il s'agit d'une variation
            colonnes += ('N' if elt == '||' else 'C')
            #ligne_variable += " "
            if elt == "<<":
                ligne_derivee += "+"
                ligne_fonction += r"\croit"
            elif elt == ">>":
                ligne_derivee += "-"
                ligne_fonction += r"\decroit"
            elif elt == "==":
                ligne_derivee += "0"
                ligne_fonction += r"\constante"
            else:
                ligne_variable += r"\hspace*{15mm}"

        else: # il s'agit des valeurs entre deux variations
            valeurs = elt.split(";")
            # valeurs = x, f(x), et eventuellement f'(x).
            # Si f(x) n'est pas defini (valeur interdite), il y a (en general) une valeur-double pour f(x) :
            # les limites a gauche et a droite, separees par un "|". (Idem pour f'(x)).


            largeur = max((3 if "|" in val else 1) for val in valeurs)
            # 3 si x est une valeur interdite pour f ou f' (ie. une valeur contient un "|"), 1 sinon.

            if largeur == 3: # x est une valeur interdite pour f(x) ou f'(x)
                ligne_variable += " &" + en_latex(valeurs[0]) + "& "

                vals_fonc = valeurs[1].split("|")
                if len(vals_fonc) == 2: # x est une valeur interdite pour f(x)
                    portion += 1 # on change de portion
                    ligne_fonction += en_latex(vals_fonc[0]) + "&\\dbarre&" \
                                    + "\\niveau{" + str(1-niveaux[portion][0]) +"}{" + str(ecart_maximal+1) + "}" \
                                    + en_latex(vals_fonc[1])
                else:
                    ligne_fonction += " &" + en_latex(vals_fonc[0]) + "&"

                if len(valeurs) < 3: # le nombre derive n'est pas specifie
                    valeurs.append("|") # si la fonction n'est pas definie en x, sa derivee non plus

                vals_deriv = valeurs[2].split("|")
                if len(vals_deriv) == 2:
                    ligne_derivee += en_latex(vals_deriv[0]) + "&\\dbarre&" + en_latex(vals_deriv[1])
                else:
                    ligne_derivee += " &" + en_latex(vals_deriv[0]) + "&"

            else: # x n'est pas une valeur interdite
                ligne_variable += en_latex(valeurs[0])
                ligne_fonction += en_latex(valeurs[1])

                if len(valeurs) < 3: # le nombre derive n'est pas specifie
                    if 0 < i < len(sequence)-1 and sequence[i-1] != sequence[i+1]:
                        # Changement de sens de variation en x :
                        # la dérivée s'annule donc.
                        valeurs.append("0")
                    else:
                        valeurs.append(" ")
                ligne_derivee += en_latex(valeurs[2])

            colonnes += largeur*'C'



    code = "\\[\\begin{tabvar}{|" + colonnes + "|}\n\\hline\n"
    code += ligne_variable + "\\\\\n"

    if derivee:
        code += "\\hline\n" + ligne_derivee + "\\\\\n"

    code += "\\hline\n" + ligne_fonction + "\\\\\n"

    code += "\\hline\n\\end{tabvar}\\]\n% " + chaine_originale + "\n"

    return code
