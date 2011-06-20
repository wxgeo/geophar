#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#           Mathlib 2 (sympy powered)         #
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

# version unicode

## Cette librairie contient les fonctions de haut niveau non inclues dans sympy.

import sympy
from sympy import exp, ln, Add, Mul, pi

import custom_objects
import math
import internal_functions
import sympy_functions
import intervalles
import pylib
import param



#def deg(x):
#    u'Conversion radians -> degrés.'
#    return custom_objects.MesureDegres(x)

def deg(x):
    u'Conversion radians -> degrés.'
    return x*180/pi

#def rad(x):
#    u'Conversion degrés -> radians.'
#    return x*sympy.pi/180

def jhms(s):
    u"Convertit un temps en secondes en jours-heures-minutes-secondes."
    return custom_objects.Temps(s = s)


def cbrt(x):
    u"Racine cubique de x."
    return cmp(x, 0)*math.exp(math.log(abs(x))/3)

def root(x, n):
    u"""Racine nième de x.

    N'est définie pour x négatif que si n est pair."""
    if n%2:
        return cmp(x, 0)*math.exp(math.log(abs(x))/n)
    return math.exp(math.log(x)/n)

def prod(facteurs):
    return reduce(lambda x,y:x*y, facteurs, 1)


def gcd(a, b):
    u"pgcd de a et de b"
    # algorithme d'Euclide
    a, b = max(abs(a),abs(b)), min(abs(a),abs(b))
    while b:
        a, b = b, a%b
    return a

def lcm(a, b):
    u"ppcm de a et de b"
    return a*b//gcd(a,b)

def pgcd(*termes):
    u"Le plus grand dénominateur commun à un nombre quelconque d'entiers."
    return reduce(lambda x,y:gcd(x,y), termes)


def ppcm(*termes):
    u"Le plus petit multiple commun à un nombre quelconque d'entiers."
    return reduce(lambda x,y:lcm(x,y), termes)



def n_premiers(n = 100, maximum = 50000): # securite face aux erreurs de frappe...!
    u"Donne la liste des n premiers nombres premiers."
    liste = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    m = liste[-1] + 2
    if n > maximum:
        raise OverflowError
    while len(liste) < n:
        r = math.sqrt(m)
        for k in liste:
            if k > r: # pas de diviseurs inferieurs à sa racine, donc le nombre est premier
                liste.append(m)
                break
            if not m%k:
                break
        m += 2
    return liste


# Approximation rationnelle par fractions continues
# cf. http://fr.wikipedia.org/wiki/Fraction_continue
def frac(valeur, n = 20, epsilon = 1e-15):
    u"Donne une fraction approximativement égale à la valeur."
    assert epsilon > 0
    p_ = 0
    p = 1
    q_ = 1
    q = 0
    x = valeur
    for i in xrange(n):
        a = int(x)
        p, p_ = a*p + p_, p
        q, q_ = a*q + q_, q
        delta = x - a
        if abs(delta) < epsilon or abs(valeur - p/q) < epsilon:
            return sympy.Rational(p, q)
        x = 1/delta
    return valeur


def bin(n):
    u"Conversion en binaire."
    s = ""
    while n:
        s = str(n%2) + s
        n //= 2
    return s







def custom_latex(expr, profile = None):
    return custom_objects.CustomLatexPrinter(profile).doprint(expr)

def custom_str(expr, profile = None):
    return custom_objects.CustomStrPrinter(profile).doprint(expr)

def auto_collect(expression):
    u"""Factorise une expression en utilisant sympy.collect, sans préciser manuellement ce par quoi factoriser."""
    if expression.is_Add:
        for terme in expression.args:
            if terme.is_Mul:
                for facteur in terme.args:
                    expression_transformee = sympy.collect(expression, facteur)
                    if expression_transformee.is_Mul:
                        resultat = 1
                        for arg in expression_transformee.args:
                            resultat *= auto_collect(arg)
                        return resultat
        for symbole in internal_functions.syms(expression):
            expression_transformee = sympy.collect(expression, symbole)
            if expression_transformee.is_Mul:
                resultat = 1
                for arg in expression_transformee.args:
                    resultat *= auto_collect(arg)
                return resultat
    return expression

def _Pow2list(expression):
    u"""On décompose une puissance en liste de facteurs."""
    base, puissance = expression.as_base_exp()
    if puissance.is_integer:
        return int(puissance)*[base]
    elif base == sympy.E:
        coeff = puissance.as_coeff_mul()[0]
        if coeff.is_integer:
            return int(abs(coeff))*[base**(puissance/abs(coeff))]
    return [expression]

def _Mul2list(expression):
    u"""On décompose un produit en une liste de facteurs ; les puissances sont converties préalablement en produits."""
    liste = []
    if expression.is_Mul:
        for facteur in expression.args:
            liste += _Pow2list(facteur)
        return liste
    return _Pow2list(expression)


def auto_collect(expression):
    u"""Factorise une expression en utilisant sympy.collect, sans préciser manuellement ce par quoi factoriser."""
    if expression.is_Add:
        dico = {}
        liste0 = _Mul2list(expression.args[0])
        for elt in liste0:
            dico[elt] = liste0.count(elt)
        for terme in expression.args[1:]:
            liste = _Mul2list(terme)
            for elt in liste0:
                dico[elt] = min(dico[elt], liste.count(elt))
        produit = 1
        for key in dico:
            produit *= key**dico[key]
        return produit*sum(arg/produit for arg in expression.args)
    return expression



def derivee(f):
    if isinstance(f, pylib.types.FunctionType):
        x = sympy.Symbol('x')
        return custom_objects.Fonction(x, sympy.diff(f(x), x))
    return custom_objects.Fonction(f.variables[0], sympy.diff(f.expression, f.variables[0]))


def nul(expression, variable = None, intervalle = True):
    u"""Retourne l'ensemble sur lequel une expression à variable réelle est nulle."""
    if variable is None:
        variable = internal_functions.extract_var(expression)
    expression = sympy_functions.factor(expression, variable, "R", decomposer_entiers = False)
    if expression.is_Mul:
        facteurs = expression.args
    else:
        facteurs = [expression]

    solutions = (intervalles.vide if intervalle else set())

    for facteur in facteurs:
        liste_solutions = sympy_functions.solve(facteur, variable, ensemble = "R")
        if intervalle:
            solutions += intervalles.Union(*liste_solutions)
        else:
            solutions.update(liste_solutions)
    return solutions


def ensemble_definition(expression, variable = None):
##    print expression, variable
    if variable is None:
        variable = internal_functions.extract_var(expression)
    ens_def = intervalles.R
    if hasattr(expression, "is_Add") and expression.is_Add:
        for terme in expression.args:
            ens_def *= ensemble_definition(terme, variable)
        return ens_def
##    try:
##        expression = sympy_functions.factor(expression, variable, "R", decomposer_entiers = False)
##    except (NotImplementedError, TypeError):
##        if param.debug:
##            print "Warning: Factorisation impossible de ", expression
    if hasattr(expression, "subs"):
        old_variable = variable
        variable = sympy.Symbol("_tmp",real=True)
        expression = expression.subs({old_variable:variable})
    if hasattr(expression, "is_Pow") and expression.is_Pow:
        base, p = expression.as_base_exp()
        if p.is_integer:
            if p >= 0:
                return ensemble_definition(base, variable)
            else:
                return ensemble_definition(base, variable) - nul(base, variable)
        elif p.is_rational:
            n, d = p.as_numer_denom()
            if abs(n) == 1 and not d.is_even:
                if p >= 0:
                    return ensemble_definition(base, variable)
                else:
                    return ensemble_definition(base, variable) - nul(base, variable)
            else:
                if p >= 0:
                    return positif(base, variable)
                else:
                    return positif(base, variable, strict = True)
        else:
            if p >= 0:
                return positif(base, variable)
            else:
                return positif(base, variable, strict = True)
    elif hasattr(expression, "is_Mul") and expression.is_Mul:
        for facteur in expression.args:
            ens_def *= ensemble_definition(facteur, variable)
        return ens_def
    elif isinstance(expression, sympy.tan):
        arg = expression.args[0] # -pi/2 < arg < pi/2
        return positif(arg + sympy.pi/2, variable, strict = True)*positif(sympy.pi/2-arg, variable, strict = True)
    elif isinstance(expression, sympy.ln):
        arg = expression.args[0] # 0 < arg
        return positif(arg, variable, strict = True)
    return ens_def


def _is_pos(expr):
    return getattr(expr, "is_positive", float(expr) > 0)

def _is_neg(expr):
    return getattr(expr, "is_negative", float(expr) < 0)

def _is_var(expression, variable):
    return hasattr(expression, "has_any_symbols") and expression.has(variable)

def positif(expression, variable = None, strict = False):
    u"""Retourne l'ensemble sur lequel une expression à variable réelle est positive (resp. strictement positive)."""
    # L'étude du signe se fait dans R, on indique donc à sympy que la variable est réelle.
    if variable is None:
        variable = internal_functions.extract_var(expression)
    if hasattr(expression, "subs"):
        old_variable = variable
        variable = sympy.Symbol("_tmp",real=True)
        expression = expression.subs({old_variable:variable})
    ens_def = ensemble_definition(expression, variable)
    try:
        expression = sympy_functions.factor(expression, variable, "R", decomposer_entiers = False)
    except NotImplementedError:
        if param.debug:
            print "Warning: Factorisation impossible de ", expression
##    print "T455451", expression, variable
    if hasattr(expression, "is_Pow") and expression.is_Pow and expression.as_base_exp()[1].is_rational:
        base, p = expression.as_base_exp()
        # Le dénominateur ne doit pas s'annuler :
        if p < 0:
            strict = True
        if p.is_integer and p.is_even:
            if strict:
                return ens_def*(intervalles.R - (positif(base, variable, strict = False) - positif(base, variable, strict = True)))
            else:
                return ens_def
        else:
            return ens_def*positif(base, variable, strict = strict)
    if hasattr(expression, "is_Mul") and expression.is_Mul:
        posit = intervalles.R
        posit_nul = intervalles.R
        for facteur in expression.args:
            # pos : ensemble des valeurs pour lequelles l'expression est positive
            # pos_nul : ensemble des valeurs pour lequelles l'expression est positive ou nulle
            pos = positif(facteur, variable, strict = True)
            pos_nul = positif(facteur, variable, strict = False)
            # posit : les deux sont strictements positifs, ou les deux sont strictements négatifs
            # posit_nul : les deux sont positifs ou nuls, ou les deux sont négatifs ou nuls
            posit, posit_nul = (posit*pos + (-posit_nul)*(-pos_nul))*ens_def, (posit_nul*pos_nul + (-posit)*(-pos))*ens_def

##            print "resultat", facteur, res
####            if res is NotImplemented:
####                return NotImplemented
##            # le résultat est positif si les deux facteurs sont positifs, ou si les deux facteurs sont négatifs:
##            resultat = resultat*res + (-resultat)*(-res)
        if strict:
            return posit
        else:
            return posit_nul
    if getattr(expression, "is_positive", None) is True: # > 0
        return ens_def
    if getattr(expression, "is_negative", None) is True: # < 0
        return intervalles.vide
    if getattr(expression, "is_positive", None) is False and strict: # <= 0
        return intervalles.vide
    if getattr(expression, "is_negative", None) is False and not strict: # >= 0
        return ens_def
    if getattr(expression, "is_zero", None) is True and not strict: # == 0
        return ens_def
    if isinstance(expression, (int, float, long)):
        if expression > 0 or (expression == 0 and not strict):
            return ens_def
        else:
            return intervalles.vide
    # pas besoin de l'ensemble de définition pour les fonctions polynomiales
    if hasattr(expression, "is_polynomial") and expression.is_polynomial():
        oo = sympy.oo
        Intervalle = intervalles.Intervalle
        P = expression.as_poly(variable)
        if P.degree() == 1:
            a, b = P.all_coeffs()
            if a > 0:
                return Intervalle(-b/a, +oo, inf_inclus = not strict)
            else: # a<0 (car a != 0)
                return Intervalle(-oo, -b/a, sup_inclus = not strict)
        elif P.degree() == 2:
            a, b, c = P.all_coeffs()
            d = b**2 - 4*a*c
            if d > 0:
                x1 = (-b - sympy.sqrt(d))/(2*a)
                x2 = (-b + sympy.sqrt(d))/(2*a)
                x1, x2 = min(x1, x2), max(x1, x2)
                if a > 0:
                    return Intervalle(-oo, x1, sup_inclus = not strict) + Intervalle(x2, +oo, inf_inclus = not strict)
                else: # a<0 (car a != 0)
                    return Intervalle(x1, x2, inf_inclus = not strict, sup_inclus = not strict)
            elif d == 0:
                x0 = -b/(2*a)
                if a > 0:
                    return Intervalle(-oo, x0, sup_inclus  = not strict) + Intervalle(x0, +oo, inf_inclus = not strict)
                else:
                    return Intervalle(x0, x0, sup_inclus  = not strict)
            else: # d < 0
               if a > 0:
                   return intervalles.R
               else:
                   return intervalles.vide

    # a*f(x)+b > 0 <=> f(x)+b/a > 0 pour a > 0, -f(x) - b/a > 0 pour a < 0
    if getattr(expression, "is_Add", False):
        args = expression.args
        if len(args) == 2:
            liste_constantes = []
            liste_autres = []
            for arg in args:
                if _is_var(arg, variable):
                    liste_autres.append(arg)
                else:
                    liste_constantes.append(arg)
            if len(liste_autres) == 1:
                partie_constante = sympy.Add(*liste_constantes)
                partie_variable = liste_autres[0]
                if getattr(partie_variable, "is_Mul", False):
                    liste_facteurs_constants = []
                    liste_autres_facteurs = []
                    for facteur in partie_variable.args:
                        if _is_var(facteur, variable):
                            liste_autres_facteurs.append(facteur)
                        else:
                            liste_facteurs_constants.append(facteur)
                    if liste_facteurs_constants:
                        facteur_constant = sympy.Mul(*liste_facteurs_constants)
                        autre_facteur = sympy.Mul(*liste_autres_facteurs)
                        if _is_pos(facteur_constant):
                            return positif(autre_facteur + partie_constante/facteur_constant, variable, strict = strict)
                        elif _is_neg(facteur_constant):
                            return ens_def*(intervalles.R - positif(autre_facteur + partie_constante/facteur_constant, variable, strict = not strict))


    # Logarithme :
    if isinstance(expression, sympy.ln):
        return positif(expression.args[0] - 1, variable, strict = strict)
    # Résolution de ln(X1) + ln(X2) + ... + b > 0, où X1=f1(x), X2 = f2(x) ...
    if getattr(expression, "is_Add", False):
        args = expression.args
        liste_constantes = []
        liste_ln = []
        # Premier passage : on remplace a*ln(X1) par ln(X1**a)
        for arg in args:
            if getattr(arg, "is_Mul", False):
                liste_constantes = []
                liste_ln = []
                for facteur in arg.args:
                    if isinstance(facteur, sympy.ln) and _is_var(facteur, variable):
                        liste_ln.append(facteur)
                    elif not _is_var(facteur, variable):
                        liste_constantes.append(facteur)
##                print facteur, liste_constantes, liste_ln
                if len(liste_constantes) == len(arg.args) - 1 and len(liste_ln) == 1:
                    expression += sympy.ln(liste_ln[0].args[0]**sympy.Add(*liste_constantes)) - arg
##        print "Resultat 1er passage:", expression
        # Deuxième passage : ln(X1)+ln(X2)+b>0 <=> X1*X2-exp(-b)>0
        for arg in args:
            if isinstance(arg, sympy.ln) and hasattr(arg, "has_any_symbols") and arg.has(variable):
                liste_ln.append(arg)
            elif not hasattr(arg, "has_any_symbols") or not arg.has(variable):
                liste_constantes.append(arg)

        if liste_ln and len(liste_ln) + len(liste_constantes) == len(args):
            # ln(X1)+ln(X2)+b>0 <=> X1*X2-exp(-b)>0
            contenu_log = sympy.Mul(*(logarithme.args[0] for logarithme in liste_ln))
            contenu_cst = sympy.exp(- sympy.Add(*liste_constantes))
            return ens_def*positif(contenu_log - contenu_cst, variable, strict = strict)



    # Exponentielle
    # Résolution de a*exp(f(x)) + b > 0
    if getattr(expression, "is_Add", False):
        a_ = sympy.Wild('a')
        b_ = sympy.Wild('b')
        X_ = sympy.Wild('X')
        match = expression.match(a_*exp(X_) + b_)
        if match is not None:
            a = match[a_]
            b = match[b_]
            X = match[X_]
            if  a != 0 and not a.has(variable) and not b.has(variable):
                if _is_pos(b):
                    if _is_pos(a):
                        return ens_def
                    elif _is_neg(a):
                        # l'ensemble de définition ne change pas
                        return positif(- X + ln(-b/a), variable, strict = strict)
                elif _is_neg(b):
                    if _is_pos(a):
                        return positif(X - ln(-b/a), variable, strict = strict)
                    elif _is_neg(a):
                        return intervalles.vide

    # Cas très particulier : on utilise le fait que exp(x)>=x+1 sur R
    if getattr(expression, "is_Add", False):
        expr = expression
        changements = False
        for arg in expr.args:
            if isinstance(arg, sympy.exp):
                changements = True
                expr += arg.args[0] + 1 - arg
        if changements and (ens_def - positif(expr, variable, strict = strict) == intervalles.vide):
            return ens_def

    # Sommes contenant des logarithmes :
    if getattr(expression, "is_Add", False):
        # Cas très particulier : on utilise le fait que ln(x)<=x-1 sur ]0;+oo[
        expr = expression
        changements = False
        for arg in expr.args:
            if isinstance(arg, sympy.ln):
                changements = True
                expr += arg.args[0] + 1 - arg
        if changements:
            try:
##                print "S458475",  -expr
                non_positif = positif(-expr, variable, strict = not strict) # complementaire
                (ens_def - positif(expr, variable, strict = not strict) == intervalles.vide)
                if (ens_def - non_positif == intervalles.vide):
                    return intervalles.vide
            except NotImplementedError:
                pass

            # Somme contenant des logarithmes : si aucune autre méthode n'a fonctionné, on tente ln(a)+ln(b)>0 <=> a*b>1 (pour a>0 et b>0)
            expr = sympy.Mul(*(sympy.exp(arg) for arg in expression.args)) - 1
            try:
                return ens_def*positif(expr, variable, strict = strict)
            except NotImplementedError:
                pass


##    print "Changement de variable."
    # En dernier recours, on tente un changement de variable :
    tmp2 = sympy.Symbol("_tmp2", real=True)
    # changements de variables courants : x², exp(x), ln(x), sqrt(x), x³ :
    for X in (variable**2, variable**3, sympy.exp(variable), sympy.ln(variable), sympy.sqrt(variable)):
        expr = expression.subs(X, tmp2)
        # Si la nouvelle variable apparait une seule fois,
        # le changement de variable produirait une récurrence infinie !
        if variable not in expr.atoms() and internal_functions.count_syms(expr, X) > 1:
##            print "nouvelle variable:", X
            solution_temp = positif(expr, tmp2, strict = strict)
            solution = intervalles.vide
            for intervalle in solution_temp.intervalles:
                sol = intervalles.R
                a = intervalle.inf
                b = intervalle.sup
                if a != - sympy.oo:
                    sol *= positif(X - a, variable, strict = strict)
                if b != sympy.oo:
                    sol *= positif(b - X, variable, strict = strict)
                solution += sol
            return ens_def*solution
    raise NotImplementedError


def resoudre(chaine, variables = (), local_dict = None):
    if local_dict is None:
        evaluer = sympy.sympify
    else:
        def evaluer(expression, local_dict = local_dict):
            return eval(expression, local_dict.globals, local_dict)

    if not variables:
        arguments = chaine.split(',')
        variables = [sympy.Symbol(s.strip()) for s in arguments[1:]]
        if not variables:
            variables = set()
            expressions = pylib.msplit(arguments[0], ('et', 'ou', '>', '<', '=', '!', ')', '(', '*', '/', '-', '+'))
            for expr in expressions:
                if expr.strip():
##                    print expr
                    ev = evaluer(expr)
                    if hasattr(ev, 'atoms') and not isinstance(ev, sympy.FunctionClass):
                        variables.update(ev.atoms(sympy.Symbol))
#            variables = list(evaluer(arguments[0].replace("et","+").replace("ou","+")
#                            .replace("<", "+").replace(">", "+")
#                            .replace("=", "+").replace("!", "+")).atoms(sympy.Symbol))
        chaine = arguments[0]

    if len(variables) > 1:
        return systeme(chaine, local_dict = local_dict)
#    fin = ",".join(arguments[1:])
#    if fin:
#        fin = "," + fin
    chaine = chaine.replace(')et', ') et').replace(')ou', ') ou').replace('et(', 'et (').replace('ou(', 'ou (')
    debut = ''
    while chaine:
        l = [s for s in pylib.split_around_parenthesis(chaine)]
        if len(l) == 3:
            if l[0].strip() == l[2].strip() == '':
                return resoudre(chaine[1:-1], variables = variables, local_dict = local_dict)
            if ' et ' in l[0]:
                retour = chaine.split(' et ', 1)
                retour[0] = debut + retour[0]
                return resoudre(retour[0], variables = variables, local_dict = local_dict)*resoudre(retour[1], variables = variables, local_dict = local_dict)
            elif ' ou ' in l[0]:
                retour = chaine.split(' ou ', 1)
                retour[0] = debut + retour[0]
                return resoudre(retour[0], variables = variables, local_dict = local_dict) + resoudre(retour[1], variables = variables, local_dict = local_dict)
            chaine = l[2]
            debut += l[0] + l[1]
        else:
            if ' et ' in chaine:
                retour = chaine.split(' et ', 1)
                retour[0] = debut + retour[0]
                return resoudre(retour[0], variables = variables, local_dict = local_dict)*resoudre(retour[1], variables = variables, local_dict = local_dict)
            elif ' ou ' in chaine:
                retour = chaine.split(' ou ', 1)
                retour[0] = debut + retour[0]
                return resoudre(retour[0], variables = variables, local_dict = local_dict) + resoudre(retour[1], variables = variables, local_dict = local_dict)
            else:
                break
    chaine = debut + chaine
    chaine = chaine.replace("==", "=").replace("<>", "!=").replace("=>", ">=").replace("=<", "<=")

    if ">=" in chaine:
        gauche, droite = chaine.split(">=")
        return positif(evaluer(gauche + "-(" + droite + ")"), *variables)
    elif "<=" in chaine:
        gauche, droite = chaine.split("<=")
        return positif(evaluer(droite + "-(" + gauche + ")"), *variables)
    if ">" in chaine:
        gauche, droite = chaine.split(">")
        return positif(evaluer(gauche + "-(" + droite + ")"), *variables, **{"strict": True})
    elif "<" in chaine:
        gauche, droite = chaine.split("<")
        return positif(evaluer(droite + "-(" + gauche + ")"), *variables, **{"strict": True})
    elif "!=" in chaine:
        gauche, droite = chaine.split("!=")
        expression = evaluer(gauche + "-(" + droite + ")")
        return ensemble_definition(expression, *variables) - nul(expression, *variables)
    elif "=" in chaine:
        gauche, droite = chaine.split("=")
        expression = evaluer(gauche + "-(" + droite + ")")
        return nul(expression, *variables)
    else:
        raise TypeError, "'" + chaine + "' must be an (in)equation."


def systeme(chaine, variables = (), local_dict = None):
    chaine = chaine.replace("==", "=")
    if local_dict is None:
        evaluer = sympy.sympify
    else:
        def evaluer(expression, local_dict = local_dict):
            return eval(expression, local_dict.globals, local_dict)

    def transformer(eq):
        gauche, droite = eq.split("=")
        return evaluer(gauche + "-(" + droite + ")")

    if not variables:
        arguments = chaine.split(',')
        variables = tuple(sympy.Symbol(s.strip()) for s in arguments[1:])
        chaine = arguments[0]
    eqs = tuple(transformer(eq) for eq in chaine.split("et"))
    if not variables:
        variables = set()
        for eq in eqs:
            variables.update(eq.atoms(sympy.Symbol))
    return sympy.solve(eqs, *variables)


def _convertir_frequences(frequences, serie):
    if frequences is None:
        n = len(serie)
        return n*[sympy.Rational(1, n)]
    else:
        total = sum(frequences)
        if total != 1:
            return [val/total for val in frequences]
        return frequences

def moyenne(serie, coeffs = None):
    u"Calcule l'espérance de la série des (xi, fi)."
    frequences = _convertir_frequences(coeffs, serie)
    return sum(xi*fi for xi, fi in zip(serie, frequences))

def variance(serie, coeffs = None):
    u"Calcule la variance de la serie des (xi, fi)"
    frequences = _convertir_frequences(coeffs, serie)
    M = moyenne(serie, frequences)
    return sum(fi*(xi - M)**2 for xi, fi in zip(serie, frequences))

def ecart_type(serie, coeffs = None):
    u"Retourne l'écart-type de la série des (xi, fi)."
    return sympy.sqrt(variance(serie, coeffs))

def covariance(serie1, serie2, coeffs = None):
    u"Retourne la covariance des deux séries."
    assert len(serie1) == len(serie2), u"Les deux séries doivent avoir le même nombre de valeurs."
    frequences = _convertir_frequences(coeffs, serie1)
    x_ = moyenne(serie1, frequences)
    y_ = moyenne(serie2, frequences)
    return sum(fi*(xi - x_)*(yi - y_) for xi, yi, fi in zip(serie1, serie2, frequences))

def linreg(serie1, serie2, coeffs = None):
    u"""Droite de régression par la méthode des moindres carrés.

    Retourne les coefficients a et b de l'équation y=ax+b
     de la droite de régression par la méthode des moindres carrés.

     >>> from mathlib.custom_functions import linreg
     >>> linreg((85.6,84.5,81,80.2,72.8,71.2,73,48.1),(78.7,77.6,75.2,71.1,67.7,66.3,59.1,46.8))
     (0.849191825268073, 4.50524942626518)
     """
    frequences = _convertir_frequences(coeffs, serie1)
    a = covariance(serie1, serie2)/variance(serie1)
    b = moyenne(serie2) - a*moyenne(serie1)
    return a, b


def pstfunc(chaine):
    u"Convertit une chaine représentant une fonction pst-trick en une fonction sympy."
    args = []
    dict_op = {'mul':'*','add':'+','exp':'**','div':'/','sub':'-'}
    dict_fn = {'ln':'ln'}

    def code_arg(s):
        return '(' + str(sympy.sympify(s)) + ')'

    for s in chaine.split(' '):
        if s in dict_op:
            assert len(args) >= 2, 'Il faut deux arguments pour ' + s
            args[-2] = code_arg(dict_op[s].join(args[-2:]))
            args.pop()
        elif s in dict_fn:
            args[-1] = code_arg(dict_fn[s] + '(' + args[-1] + ')')
        elif s:
            args.append(code_arg(s))
    assert len(args) == 1, 'Il doit rester un seul argument a la fin.'
    return custom_str(sympy.sympify(args[0]))

def aide(fonction):
    u"Retourne (si possible) de l'aide sur la fonction saisie."
    if getattr(fonction, '__name__', None) and getattr(fonction, '__doc__', None):
        hlp = "\n== Aide sur %s ==" %fonction.__name__
        for ligne in fonction.__doc__.split('\n'):
            hlp += '\n' + ligne.lstrip()
        return hlp
    else:
        from end_user_functions import __classement__
        for val in __classement__.itervalues():
            if val[1] == getattr(fonction, '__name__', str(fonction)):
                hlp = "\n== Aide sur %s ==\n" %fonction.__name__
                hlp += val[2]
                return hlp
        return "Pas d'aide disponible."

def arrondir(valeur, chiffres = 0):
    # Nombre de chiffres de la partie entière :
    n = sympy.floor(sympy.log10(valeur)) + 1
    return valeur.evalf(chiffres + n)
