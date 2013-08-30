# -*- coding: utf-8 -*-
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

from sympy import oo, nan, Symbol

from .tablatexlib import convertir_en_latex, traduire_latex, test_parentheses,\
                         maths, extraire_facteurs, nice_str
from ...mathlib.sympy_functions import solve
from ...mathlib.intervalles import R, conversion_chaine_ensemble
from ...mathlib.solvers import ensemble_definition
from ...mathlib.interprete import Interprete
from ...mathlib.parsers import VAR
from ... import param

def _auto_tabsign(chaine, cellspace = False):
    u"""Génère le code du tableau de signe à partir d'une expression à variable réelle.

    On suppose que l'expression est continue sur tout intervalle de son
    ensemble de définition.
    Par ailleurs, ses zéros doivent être calculables pour la librairie sympy.
    """

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
        legende = chaine
    legende = legende.strip()

    # Décomposition en produit
    facteurs = extraire_facteurs(chaine)#.replace('/', '*'))
    # Conversion en expression sympy
    interprete = Interprete()
    interprete.evaluer(chaine)
    expr = interprete.ans()
    # Récupération de la variable
    variables = expr.atoms(Symbol)
    # On tente de récupérer le nom de variable dans la légende.
    # Par exemple, si la légende est 'f(x)', la variable est 'x'.
    m = re.match(r'%s\((%s)\)' % (VAR, VAR), legende)
    if m is not None:
        variables.add(Symbol(str(m.group(1))))
    if len(variables) > 1:
        # Il est impossible de dresser le tableau de variations avec des
        # variables non définies (sauf cas très particuliers, comme f(x)=a).
        raise ValueError, "Il y a plusieurs variables dans l'expression !"
    elif not variables:
        # Variable par défaut.
        variables = [Symbol('x')]
    var = variables.pop()
    # Récupération de l'ensemble de définition
    ens_def *= ensemble_definition(expr, var)
    if param.debug and param.verbose:
        print '-> Ensemble de definition:', ens_def

    code = str(var) # chaîne retournée, respectant la syntaxe de tabsign()
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
        sup = intervalle.sup
        if not intervalle.sup_inclus:
            valeurs_interdites.append(sup)
        code += ': ' + ('' if (intervalle.inf_inclus or inf == -oo) else '!') + nice_str(inf) + ';' \
                     + ('' if (intervalle.sup_inclus or sup == oo) else '!') + nice_str(sup)
    xmax = sup


    # Étude du signe de chaque facteur
    for facteur in facteurs:
        interprete.evaluer(facteur)
        f_expr = interprete.ans()
        f_ens_def = ensemble_definition(f_expr, var)
        valeurs = {xmin: None, xmax: None}
        solutions = [sol for sol in solve(f_expr, var)
                        if xmin.evalf(200) <= sol.evalf(200) <= xmax.evalf(200)]
        for sol in solutions:
            valeurs[sol] = 0
        for val in valeurs_interdites:
            if val not in f_ens_def and val not in (-oo, oo):
                valeurs[val] = nan
        liste_valeurs = sorted(valeurs)
        # On génère le code de la ligne
        code += '// '
        #print solutions, valeurs_interdites
        if solutions and all(sol in valeurs_interdites for sol in solutions):
            code += '!'
        code += facteur + ':'
        for i, valeur in enumerate(liste_valeurs):
            if valeurs[valeur] == 0:
                code += nice_str(valeur)
            elif valeurs[valeur] == nan:
                code += '!' + nice_str(valeur)

            if i != len(liste_valeurs) - 1:
                valeur_suivante = liste_valeurs[i + 1]
                if valeur == -oo:
                    if valeur_suivante == +oo:
                        val_intermediaire = 0
                    else:
                        val_intermediaire = valeur_suivante - 1
                elif valeur_suivante == +oo:
                    val_intermediaire = valeur + 1
                else:
                    val_intermediaire = (valeur + valeur_suivante)/2
                # On suppose la fonction continue sur tout intervalle de son ensemble de définition.
                if f_expr.subs(var, val_intermediaire) > 0:
                    code += ' ++ '
                else:
                    code += ' -- '

    code += '// ' + legende
    if param.debug and param.verbose:
        print 'Code TABSign:', code
    return tabsign(code, cellspace = cellspace) + '% ' + chaine_initiale + '\n'



def _augmenter(val):
    u"""Retourne une valeur numérique *légèrement* supérieure à la valeur rentrée.

    La valeur retournée est aussi proche que possible de la valeur rentrée, tout
    en s'assurant que _augmenter(val)>val.
    """
    if float(val) == float('-inf'):
        return -100000000000000000000000000000000
    eps = 1e-20
    while val + eps <= val:
        eps *= 10
        if eps > 1e200:
            raise OverflowError, "Can't find value bigger than %s." % val
    return val + eps


def tabsign(chaine = '', cellspace = False):
    u"""Indiquer ligne par ligne le signe de chaque facteur.
La dernière ligne (produit ou quotient) est générée automatiquement.

Exemples:
x:-pi;pi //  sin(x):-pi -- 0 ++ pi //  !cos(x):-- -pi/2 ++ pi/2 -- // tan(x)
x:-2;2 // x+1:-- -1 ++ // !x-1:-- 1 ++

Le point d'exclamation avant une expression signifie qu'elle correspond à un dénominateur."""

    chaine_originale = chaine = chaine.strip()
    chaine = chaine.replace('//', '\n').replace(r'\\', '\n').replace("-oo", r"-\infty").replace("+oo", r"+\infty")

    lignes = [ligne.strip() for ligne in chaine.split('\n') if ligne.strip()]

    if len(lignes) == 1:
        if ':' in lignes[0]:
            lignes = [''] + lignes
        else:
            return _auto_tabsign(lignes[0], cellspace = cellspace)

    # 'resultat' est la dernière ligne, sauf si elle contient ':'
    # (Dans ce cas, 'resultat' sera généré automatiquement plus tard, à partir des autres lignes).
    resultat = (lignes.pop() if ':' not in lignes[-1] else '')

    ligne_variable = lignes.pop(0)
    #print lignes
    if ":" in ligne_variable:
        variable, donnees_variable = ligne_variable.split(":", 1)
    elif ";" in ligne_variable:
        variable = ""
        donnees_variable = ligne_variable
    else:
        variable = ligne_variable
        donnees_variable = ""

    variable = variable.strip()
    if ';' not in donnees_variable:
        donnees_variable += ';'

    def _inter2tuple(s):
        inf, sup = s.split(';')
        inf = inf.strip()
        sup = sup.strip()
        if not inf:
            inf = '-oo'
        if not sup:
            sup = '+oo'
        return (inf, sup)

    intervalles = [_inter2tuple(inter) for inter in donnees_variable.split(':')]

    # Séparation de la légende et des autres données pour chaque ligne
    expressions = []
    donnees_expressions = []
    for ligne in lignes:
        expression, signe_expression = ligne.split(":")
        expressions.append(expression.strip())
        donnees_expressions.append(signe_expression.strip())

    # Au besoin, on génère la légende de la dernière ligne (c.à-d. le résultat - produit ou quotient)
    if resultat == "":
        numerateur = []
        denominateur = []
        for expression in expressions:
            if expression[0] == "!":
                liste = denominateur
                expression = expression[1:]
            else:
                liste = numerateur
            if "+" in expression or "-" in expression[1:]:
                # il s'agit d'une somme ou d'une difference, il faut donc des parentheses
                liste.append("(" + expression + ")")
            else:
                liste.append(expression)
        if denominateur:
            if len(denominateur) == 1 and denominateur[0][0] == "(" and denominateur[0][-1] == ")":
                denominateur[0] = denominateur[0][1:-1]
            if len(numerateur) == 1 and numerateur[0][0] == "(" and numerateur[0][-1] == ")":
                numerateur[0] = numerateur[0][1:-1]
            if not numerateur:
                numerateur = ["1"]
            resultat = "\\frac{%s}{%s}" %("".join(numerateur), "".join(denominateur))
        else:
            resultat = "".join(numerateur)

        resultat_genere_automatiquement = True
    else:
        resultat_genere_automatiquement = False

    # Cas particulier : 'produit' de 1 seul élément -> inutile d'afficher une ligne résultat
    if len(expressions) == 1 and not expressions[0].startswith("!"):
        afficher_resultat = False
    else:
        afficher_resultat = True

    # Au besoin, on génère la légende de la première ligne (c.à-d. la variable),
    # à partir du résultat.
    if not variable:
        # On regarde si le résultat est de la forme `fonction(variable)`,
        # par exemple, `f(x)`.
        m = re.match(r'%s\((%s)\)' % (VAR, VAR), resultat.strip())
        if m is not None:
            variable = m.group(1)
        else:
            # On cherche les lettres isolées (sauf 'e', qui représente exp(1))
            m = re.search('(?<![A-Za-z])[A-DF-Za-df-z](?![A-Za-z])', resultat)
            # Si on n'en trouve pas, la variable sera 'x'
            variable = m.group() if m else 'x'

    # On récupère la liste de toutes les valeurs de x
    valeurs = set() # va contenir toutes les valeurs numeriques
    correspondances = {} # servira à retrouver le code (LaTeX notamment) à partir de la valeur numérique.

    valeurs_interdites = set()

    # `defaut_val` permet de construire des tableaux de signes contenant
    # des valeurs symboliques (par exemple "f(x): -- x_1 ++ x_2 --").
    # Pour attribuer une valeur numérique à cette valeur symbolique,
    # on prend une valeur légèrement supérieure à la dernière valeur numérique rencontrée.
    # NOTE: cet algorithme n'est pas parfait, mais permet de gérer les cas simples.
    # Pour les cas plus compliqués, l'utilisateur garde la possibilité de rentrer
    # manuellement une valeur numérique associée à la valeur symbolique.
    # Exemple: f(x): -- x_1=0.27 ++ x_2=3.58 --

    defaut_val = None

    # On convertit les bornes du domaine en valeurs numériques
    for intervalle in intervalles:
        for borne in intervalle:
            exclue = (borne[0] == '!')
            if exclue:
                borne = borne[1:]
            num = eval(traduire_latex(borne), maths.__dict__)
            if defaut_val is None:
                # Un peu plus que la borne inférieure.
                defaut_val = _augmenter(num)
            if exclue:
                valeurs_interdites.add(num)
            valeurs.add(num)
            correspondances[num] = borne

    # Idem pour toutes les autres valeurs
    for i, donnees in enumerate(donnees_expressions):
        donnees = re.split(r'(\+\+|--|00)', donnees)
        for j, valeur in enumerate(donnees):
            valeur = valeur.strip()
            if valeur not in ('++', '--', '00', ''):
                # On préformate les donnees en vue d'un traitement ulterieur.
                # Ex: '-5 ++ (1;|) -- 4' devient [(-5, "0"), "+", (1, "|"), "-", (4, "0")].
                if valeur[0] == '(' and valeur[-1] == ')' and test_parentheses(valeur[1:-1]):
                    valeur = valeur[1:-1]
                vals = [val.strip() for val in valeur.split(';')]
                if len(vals) == 1:
                    if vals[0].startswith('!'):
                        vals[0] = vals[0][1:]
                        vals.append('|')
                    else:
                        vals.append('0')
                else:
                    vals[1] = '$' + vals[1] + '$'
                if '=' in vals[0]:
                    vals[0], valeur_num = vals[0].split('=', 1)
                    valeur_num = eval(traduire_latex(valeur_num), maths.__dict__)
                else:
                    try:
                        valeur_num = eval(traduire_latex(vals[0]), maths.__dict__)
                        defaut_val = valeur_num
                    except (NameError, SyntaxError):
                        defaut_val = _augmenter(defaut_val)
                        valeur_num = defaut_val

                valeurs.add(valeur_num)
                correspondances[valeur_num] = vals[0]
                vals[0] = valeur_num
                donnees[j] = vals
        #print donnees
        donnees_expressions[i] = donnees

    # 'donnees_expressions' est désormais une liste de liste.
    # Pour chaque ligne du tableau, 'donnees_expressions' contient une liste
    # du genre [(-5, "0"), "+", (1, "|"), "-", (4, "0")].

    valeurs = sorted(valeurs)

    indices_denominateurs = []
    # indique que les lignes correspondantes se trouvent au denominateur

    # On initialise le code LaTeX de chaque ligne avec sa légende.
    # NB: la liste 'lignes' contiendra le code LaTeX pour chaque ligne.
    n = max(len(chaine) for chaine in expressions + [variable, resultat])
    lignes = [convertir_en_latex(variable)]
    i = 1
    for expression in expressions:
        if expression[0] == "!":
            expression = expression[1:]
            indices_denominateurs.append(i)
        lignes.append(convertir_en_latex(expression))
        i += 1
    lignes.append(convertir_en_latex(resultat))

    # On justifie le texte de la première colonne pour que le code LaTeX généré soit plus lisible.
    n = max(len(texte) for texte in lignes) + 1
    for i, ligne in enumerate(lignes):
        lignes[i] = ligne.ljust(n)

    def latex_signe(val, co):
        u"Retourne le signe à afficher dans le tableau, selon la valeur (et la colonne)."
        if val == nan:
            return '||'
        elif val > 0:
            return '+' if not co%2 else ''
        elif val < 0:
            return '$-$' if not co%2 else ''
        else:
            return '0'

    dict_signes = {'++': 1, '--': -1, '00': 0}


    # On génère maintenant le code LaTeX correspondant au tableau proprement dit.
    # On procède colonne par colonne.
    nbr_colonnes = 2*len(valeurs)
    for co in xrange(1, nbr_colonnes):
        colonne = ['' for i in xrange(len(donnees_expressions) + 2)]

        signe = 1
        # (1 pour positif, -1 pour négatif, nan pour valeur interdite -> cf. latex_signe())

        # Première ligne (valeurs de la variable)
        if co%2:
            # Il s'agit d'une valeur (et non d'un signe + ou -)
            valeur_num = valeurs[(co - 1)//2]
            valeur = correspondances[valeur_num]

            # On applique un formatage LaTeX à certaines expressions :
            colonne[0] = convertir_en_latex(valeur)

            if valeur_num in valeurs_interdites:
                signe = nan


        # Autres lignes
        for li, donnees in enumerate(donnees_expressions):
            # À quel endroit de la ligne sommes-nous ? (3 cas)
            valeurs_precedentes = [k for k, val in enumerate(donnees) if not isinstance(val, basestring) and val[0]<=valeur_num]
            if valeurs_precedentes:
                # position de la dernière valeur de la ligne
                position = valeurs_precedentes[-1]
                if co%2: # 1er cas: on est au niveau d'une valeur
                    if donnees[position][0] == valeur_num:
                        if donnees[position][1] == '|':
                            colonne[li + 1] = '||'
                            signe = nan
                        else:
                            colonne[li + 1] = donnees[position][1]
                            signe *= 0
                        if li + 1 in indices_denominateurs:
                            signe = nan
                else: # 2e cas: on est entre deux valeurs
                    assert position + 1 < len(donnees), "Verifiez que les valeurs de la ligne sont bien rangees dans l'ordre croissant."
                    signe_ = dict_signes[donnees[position + 1]]
                    colonne[li + 1] += latex_signe(signe_, co) # le signe qui est juste apres la derniere valeur
                    signe *= signe_
            else: # 3e cas: on est en début de ligne
                if co%2 == 0: # on est entre deux valeurs
                    signe_ = dict_signes[donnees[1]]
                    colonne[li + 1] += latex_signe(signe_, co)
                    signe *= signe_

        # Dernière ligne : signe du produit ou du quotient
        colonne[-1] += latex_signe(signe, co)

        # On centre le texte dans la colonne pour que le code LaTeX généré soit plus lisible.
        n = max(len(texte) for texte in colonne) + 2
        for i, ligne in enumerate(colonne):
            colonne[i] = ligne.center(n)

        # Une fois la colonne entièrement générée, le texte de la colonne est rajouté à chaque ligne
        for num, text in enumerate(colonne):
            lignes[num] += '&' + text


    # Cas particulier : 'produit' de 1 seul élément
    if not afficher_resultat:
        lignes.pop(-1 if resultat_genere_automatiquement else -2)
        # NB: si le resultat n'a pas été généré automatiquement, on garde la dernière ligne,
        # et on supprime l'avant dernière, pour garder le nom éventuel de la fonction
        # par exemple, si f(x)=x-1
        # cela permet d'avoir   f(x) | -  1  +   dans le tableau,
        # au lieu de            x-1  | -  1  +

    # Et on rassemble les lignes
    if cellspace:
        code = "\\begin{center}\n\\begin{tabular}{|Sc|" + (nbr_colonnes - 1)*"Sc" + "|}\n\\hline\n"
    else:
        code = "\\begin{center}\n\\begin{tabular}{|c|" + (nbr_colonnes - 1)*"c" + "|}\n\\hline\n"
    for ligne in lignes:
        code += ligne + "\\\\\n\\hline\n"
    code += "\\end{tabular}\n\\end{center}\n% " + chaine_originale + "\n"
    return code
