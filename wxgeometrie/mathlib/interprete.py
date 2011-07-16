#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#   Mathlib 2 (sympy powered) #
##--------------------------------------#######
#WxGeometrie
#Dynamic geometry, graph plotter, and more for french mathematic teachers.
#Copyright (C) 2005-2010  Nicolas Pourcelot
#
#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import re, math, types
import  numpy

from sympy import Symbol, Basic, Float, sympify

from .intervalles import Ensemble
from .custom_functions import custom_str, custom_latex
from .custom_objects import Temps, Fonction, Matrice, ProduitEntiers
from . import sympy_functions
from ..mathlib import end_user_functions
from ..pylib import print_error, split_around_parenthesis, regsub,\
                    securite
from .parsers import simplifier_ecriture, NBR, traduire_formule
from .. import param

class LocalDict(dict):
    globals = {}
##    def __getitem__(self, name):
##        #~ print "Nom de clef: ", name
##        #~ print "local: ", self.has_key(name)
##        #~ print "global: ", self.globals.has_key(name)
##        if self.has_key(name) or self.globals.has_key(name): # doit renvoyer une KeyError si la clé est dans le dictionnaire global, pour que Python y aille chercher ensuite la valeur associée à la clé
##            return dict.__getitem__(self, name)
##        return Symbol(name)

    def __missing__(self, key):
        # _59 is an alias for ans(59)
        if key.startswith('_'):
            if key[1:].isalnum():
                return self.globals['ans'](int(key[1:]))
            else:
                if key == len(key)*'_':
                    return self.globals['ans'](-len(key))
        return self.globals.get(key, Symbol(key))

    def __setitem__(self, name, value):
        # Pour éviter que l'utilisateur redéfinisse pi, i, e, etc. par mégarde.
        if self.globals.has_key(name) or (name.startswith('_') and name[1:].isalnum()):
            raise NameError, "%s est un nom reserve" %name
        if isinstance(value, str):
            # exec/eval encodent les chaînes crées en utf8.
            value = value.decode("utf8").encode(param.encodage)
        # [[1,2],[3,4]] est converti en une matrice
        if isinstance(value, list) and len(value):
            if isinstance(value[0], list):
                n = len(value[0])
                test = True
                for elt in value[1:]:
                    if not isinstance(elt, list) or len(elt) != n:
                        test = False
                        break
                if test:
                    value = sympy_functions.mat(value)
        dict.__setitem__(self, name, value)




class Interprete(object):
    def __init__(self,  calcul_exact=True,
                        ecriture_scientifique=False,
                        forme_algebrique=True,
                        simplifier_ecriture_resultat=True,
                        changer_separateurs=False,
                        separateurs_personnels=(",", ";"),
                        copie_automatique=False,
                        formatage_OOo=True,
                        formatage_LaTeX=True,
                        ecriture_scientifique_decimales=2,
                        precision_calcul=60,
                        precision_affichage=18,
                        simpify=True,
                        verbose=None,
                        appliquer_au_resultat=None,
                        adapter_separateur=None,
                        ):
        # Dictionnaire local (qui contiendra toutes les variables définies par l'utilisateur).
        self.locals = LocalDict()
        # Dictionnaire global (qui contient les fonctions, variables et constantes prédéfinies).
        self.globals = vars(end_user_functions).copy()
        self.globals.update({
                "__builtins__": None,
                "Fonction": Fonction,
                "Matrice": Matrice,
                "Temps": Temps,
                "ProduitEntiers": ProduitEntiers,
                "Ensemble": Ensemble,
                "__sympify__": sympify,
                "ans": self.ans,
                "rep": self.ans, # alias en français :)
                "__vars__": self.vars,
#                "__decimal__": Decimal,
                "__decimal__": self._decimal,
                "__local_dict__": self.locals,
                "range": numpy.arange,
                "arange": numpy.arange,
                            })
        # pour éviter que les procédures de réécriture des formules ne touchent au mots clefs,
        # on les référence comme fonctions (elles seront inaccessibles, mais ce n'est pas grave).
        # ainsi, "c and(a or b)" ne deviendra pas "c and*(a or b)" !
        # self.globals.update({}.fromkeys(securite.keywords_autorises, lambda:None))

        # On import les fonctions python qui peuvent avoir une utilité éventuel (et ne présentent pas de problème de sécurité)
        a_importer = ['all', 'unicode', 'isinstance', 'dict', 'oct', 'sorted', 'list', 'iter', 'set', 'reduce', 'issubclass', 'getattr', 'hash', 'len', 'frozenset', 'ord', 'filter', 'pow', 'float', 'divmod', 'enumerate', 'basestring', 'zip', 'hex', 'chr', 'type', 'tuple', 'reversed', 'hasattr', 'delattr', 'setattr', 'str', 'int', 'unichr', 'any', 'min', 'complex', 'bool', 'max', 'True', 'False']

        for nom in a_importer:
            self.globals[nom] = __builtins__[nom]

        self.locals.globals = self.globals

        # gerer les fractions et les racines de maniere exacte si possible.
        self.calcul_exact = calcul_exact
        # afficher les resultats en ecriture scientifique.
        self.ecriture_scientifique = ecriture_scientifique
        # mettre les résultats complexes sous forme algébrique
        self.forme_algebrique = forme_algebrique
        # Écrire le résultat sous une forme plus agréable à lire
        # (suppression des '*' dans '2*x', etc.)
        self.simplifier_ecriture_resultat = simplifier_ecriture_resultat
        # appliquer les séparateurs personnalisés
        self.changer_separateurs = changer_separateurs
        # séparateurs personnalisés (séparateur décimal, séparateur de listes)
        self.separateurs_personnels = separateurs_personnels
        # d'autres choix sont possibles, mais pas forcément heureux...
        # copie automatique de chaque résultat dans le presse-papier
        self.copie_automatique = copie_automatique
        self.formatage_OOo = formatage_OOo
        self.formatage_LaTeX = formatage_LaTeX
        self.ecriture_scientifique_decimales = ecriture_scientifique_decimales
        self.precision_calcul = precision_calcul
        self.precision_affichage = precision_affichage
        self.verbose = verbose
        self.simpify = simpify
        # une fonction à appliquer à tous les résultats
        self.appliquer_au_resultat = appliquer_au_resultat
        self.adapter_separateur = (param.adapter_separateur if adapter_separateur is None
                                                            else adapter_separateur)
        self.latex_dernier_resultat = ''
        self.initialiser()

    def _decimal(self, nbr, prec = None):
        if prec is None:
            prec = self.precision_calcul
        return Float(nbr, prec)

    def initialiser(self):
        self.locals.clear()
        self.derniers_resultats = []

    def evaluer(self, calcul = ""):
        self.warning = ""
        # calcul = re.sub("[_]+", "_", calcul.strip()) # par mesure de sécurité, les "__" sont interdits.
        # Cela permet éventuellement d'interdire l'accès à des fonctions.
        # Warning: inefficace. Cf. "_import _builtins_import _

        # Ferme automatiquement les parentheses.
        parentheses = "({[", ")}]"
        for i in range(3):
            difference = calcul.count(parentheses[0][i])-calcul.count(parentheses[1][i])
            if difference > 0:
                calcul += difference*parentheses[1][i]
                self.warning += u" Attention, il manque des parenthèses \"" + parentheses[1][i] + "\"."
            elif difference < 0:
                self.warning += u" Attention, il y a des parenthèses \"" + parentheses[1][i] + "\" superflues."
                if calcul.endswith(abs(difference)*parentheses[1][i]):
                    calcul = calcul[:difference]

##        # Transforme les ' en ` et les " en ``
##        calcul = calcul.replace("'", "`").replace('"', '``')

        if self.verbose:
            print "Traitement ({[]}) :  ", calcul

        if calcul and calcul[0] in "><!=^*/%+":
            calcul = "_" + calcul

        if self.verbose:
            print "Traitement ><!=^*/%+ :  ", calcul

        if self.formatage_LaTeX and calcul.rstrip().endswith("\\approx"):
            calcul = calcul.rstrip()[:-7] + ">>evalf"

        if ">>" in calcul:
            liste = calcul.split(">>")
            calcul = liste[0]
            for s in liste[1:]:
                calcul = s + "(" + calcul + ")"

        if self.verbose:
            print "Traitement >> :  ", calcul

        if calcul.startswith('?'):
            calcul = 'aide(%s)' %calcul[1:]
        elif calcul.endswith('?'):
            calcul = 'aide(%s)' %calcul[:-1]

        try:
            param.calcul_approche = not self.calcul_exact
            # utilisé en particulier dans la factorisation des polynômes
            self._executer(calcul)
        except Exception as err:
            if not self.adapter_separateur:
                raise
            # Si le calcul échoue, c'est peut-être que l'utilisateur a utilisé une virgule pour les décimaux
            sep = self.separateurs_personnels[0]
            _raise = True
            if not self.changer_separateurs and re.search(r'\d[' + sep + r']\d', calcul):
                self.changer_separateurs = True
                try:
                    # On retente le calcul après avoir défini la virgule comme séparateur décimal
                    self._executer(calcul)
                    self.warning += u" Attention: séparateur décimal incorrect."
                    _raise = False
                except Exception:
                    # C'est l'erreur **initiale** qui nous intéresse, pas celle-ci !
                    pass
                finally:
                    self.changer_separateurs = False
            if _raise:
                raise err # Erreur initiale (c-à-d. avant de changer les séparateurs).
        finally:
            param.calcul_approche = False

        self.derniers_resultats.append(self.locals["_"])

        if not self.calcul_exact:
            return self._formater(sympy_functions.evalf(self.locals["_"], self.precision_calcul))
        return self._formater(self.locals["_"])


    def _ecriture_scientifique(self, chaine):
        valeur = float(chaine)
        mantisse = int(math.floor(math.log10(abs(valeur))))
        chaine = str(round(valeur/10.**mantisse, self.ecriture_scientifique_decimales))
        if mantisse:
            chaine += "*10^"+str(mantisse)
        return  chaine

    def _ecriture_scientifique_latex(self, chaine):
        valeur = float(chaine)
        mantisse = int(math.floor(math.log10(abs(valeur))))
        chaine = str(round(valeur/10.**mantisse, self.ecriture_scientifique_decimales))
        if mantisse:
            chaine += "\\times 10^{%s}" %mantisse
        return  chaine




    def _formater_decimaux(self, chaine):
        if "." in chaine:
            chaine = str(Float(str(chaine), self.precision_calcul).evalf(self.precision_affichage))
            chaine = chaine.rstrip('0')
            if chaine.endswith("."):
                chaine = chaine[:-1]
        return chaine


    def _formater(self, valeur):
##        resultat = self._formatage_simple(valeur)
        resultat = custom_str(valeur)
        if valeur is None:
            latex = ""
        else:
            try:
                latex = custom_latex(valeur)
            except Exception:
                print_error()
                latex = ''


        if self.ecriture_scientifique and not self.calcul_exact:
            resultat = regsub(NBR, resultat, self._ecriture_scientifique)
            latex = regsub(NBR, latex, self._ecriture_scientifique_latex)
        else:
##            print "initial", resultat
            resultat = regsub(NBR, resultat, self._formater_decimaux)
##            print "final", resultat
            latex = regsub(NBR, latex, self._formater_decimaux)

##        if re.match("[0-9]*[.][0-9]+$", resultat):
##            resultat = resultat.rstrip('0')
##            if resultat.endswith("."):
##                resultat += "0"
##            latex = "$" + resultat + "$"
        if self.changer_separateurs and not isinstance(valeur, basestring):
            resultat = resultat.replace(",", self.separateurs_personnels[1]).replace(".", self.separateurs_personnels[0])
            latex = latex.replace(",", self.separateurs_personnels[1]).replace(".", self.separateurs_personnels[0])
            # TODO: utiliser un parser, pour détecter les chaînes, et ne pas remplacer à l'intérieur.

        if isinstance(valeur, basestring):
            latex = u'\u201C%s\u201D' %valeur

        self.latex_dernier_resultat = latex
        if self.simplifier_ecriture_resultat:
            resultat = simplifier_ecriture(resultat)
        return resultat, latex


    def _traduire(self, formule):
        variables = self.globals.copy()
        variables.update(self.locals)
        #callable_types = (  types.BuiltinFunctionType,
                            #types.BuiltinMethodType,
                            #types.FunctionType,
                            #types.UfuncType,
                            #types.MethodType,
                            #types.TypeType,
                            #types.ClassType)
        #fonctions = [key for key, val in variables.items() if isinstance(val, callable_types)]
##        fonctions = [key for key, val in variables.items() if hasattr(val, "__call__") and not isinstance(val, sympy.Atom)]
        #print fonctions
        # La fonction traduire_formule de la librairie formatage permet d'effectuer un certain nombre de conversions.
        formule = traduire_formule(formule, fonctions = variables,
                        OOo = self.formatage_OOo,
                        LaTeX = self.formatage_LaTeX,
                        changer_separateurs = self.changer_separateurs,
                        separateurs_personnels = self.separateurs_personnels,
                        simpify = self.simpify,
                        verbose = self.verbose,
                        )

        formule = re.sub("(?<![A-Za-z0-9_])(resous|solve)", "resoudre", formule)
        i = formule.find("resoudre(")
        if i != -1:
            while formule.find("(et)") != -1:
                formule = formule.replace("(et)", "et")
            while formule.find("(ou)") != -1:
                formule = formule.replace("(ou)", "ou")
            formule = formule.replace("*ou*", " ou ").replace("*et*", " et ")\
                        .replace("*ou-", " ou -").replace("*et-", " et -")\
                        .replace("*ou+", " ou +").replace("*et+", " et +")
            deb, bloc, fin = split_around_parenthesis(formule, i)
            formule = deb + '("' + bloc[1:-1] + '", local_dict = __local_dict__)'
        if self.verbose or (self.verbose is None and param.debug):
            print "test_resoudre: ", i, formule
        return formule


    def _executer(self, instruction):
        # Cas d'une fonction.
        # Exemple: 'f(x,y)=x+y+3' sera traduit en 'f=Fonction((x,y), x+y+3)'
        if re.match("[^=()]+[(][^=()]+[)][ ]*=[^=]", instruction):
            var, val = instruction.split("=", 1)
            var = var.strip()
            i = var.find("(")
            nom = var[:i]
            variables = var[i:]
            instruction = nom + "=Fonction(" + variables + "," + self._traduire(val) + ")"
        else:
            instruction = self._traduire(instruction)

        # dans certains cas, il ne faut pas affecter le résultat à la variable "_" (cela provoquerait une erreur de syntaxe)
        # (Mots clés devant se trouver en début de ligne : dans ce cas, on ne modifie pas la ligne)
##        if True in [instruction.startswith(exception + " ") for exception in securite.__keywords_debut_ligne__]:
##        def re_keywords(liste):
##            global pylib
##            return "("+"|".join(securite.keywords_debut_ligne)+")[ :(;'\"]"

##        if re.match(re_keywords(securite.keywords_debut_ligne), instruction):
##            self.locals["_"] = None
##        else:
##            instruction = "_=" + instruction

        if securite.expression_affectable(instruction):
            instruction = "_=" + instruction
        else:
            self.locals["_"] = None

##        keywords_interdits = [kw + " " for kw in securite.__keywords_interdits__] + [kw + "(" for kw in securite.__keywords_interdits__]
##        instruction = recursive_mreplace(instruction, keywords_interdits)
        if securite.keywords_interdits_presents(instruction):
            self.warning += 'Les mots-clefs ' + ', '.join(sorted(securite.keywords_interdits)) \
                            + ' sont interdits.'
            raise RuntimeError, "Mots-clefs interdits."
##        regsub(re_keywords(securite.keywords_interdits), instruction, " ")

        #print self.globals.keys()
        try:
            exec(instruction, self.globals, self.locals)
        except NotImplementedError:
            print_error()
            self.locals["_"] = "?"
        if self.forme_algebrique and isinstance(self.locals["_"], Basic) and hasattr(self.locals["_"], "is_number") and self.locals["_"].is_number:
            try:
                self.locals["_"] = self.locals["_"].expand(complex=True)
            except NotImplementedError:
                print_error()
        if self.appliquer_au_resultat is not None:
            self.locals["_"] = self.appliquer_au_resultat(self.locals["_"])


    def vars(self):
        dictionnaire = self.globals.copy()
        dictionnaire.update(self.locals)
        return dictionnaire


    def ans(self, n = -1):
        if n >= 0:
            n = int(n-1)
        else:
            n = int(n)
        if self.derniers_resultats: return self.derniers_resultats[n]
        self.warning += u" Ans(): aucun calcul antérieur."
        return 0

    def clear_state(self):
        self.locals.clear()

    def save_state(self):
        def repr2(expr):
            if isinstance(expr, (types.BuiltinFunctionType, types.TypeType, types.FunctionType)):
                return expr.__name__
            return repr(expr)
        return '\n'.join(k + ' = ' + repr2(v) for k, v in self.locals.items()) \
                + '\n\n@derniers_resultats = [\n    ' + '\n    '.join(repr(repr2(res)) +',' for res in self.derniers_resultats) + '\n    ]'

    def load_state(self, state):
        def evaltry(expr):
            u"Evalue l'expression. En cas d'erreur, intercepte l'erreur et retourne None."
            try:
                return eval(expr, self.globals, self.locals)
            except Exception:
                print("Error: l'expression suivante n'a pu être évaluée par l'interprète: %s." %repr(expr))
                print_error()

        self.clear_state()
        etat_brut, derniers_resultats = state.split('@derniers_resultats = ', 1)
        etat = (l.split(' = ', 1) for l in etat_brut.split('\n') if l)
        self.locals.update((k, evaltry(v)) for k, v in etat)
        liste_repr = eval(derniers_resultats, self.globals, self.locals)
        self.derniers_resultats = [evaltry(s) for s in liste_repr]
