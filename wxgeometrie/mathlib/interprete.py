# -*- coding: utf-8 -*-

##--------------------------------------#######
#   Mathlib 2 (sympy powered) #
##--------------------------------------#######
#WxGeometrie
#Dynamic geometry, graph plotter, and more for french mathematic teachers.
#Copyright (C) 2005-2013  Nicolas Pourcelot
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

import re, types
import  numpy

import sympy
from sympy import Symbol, Basic, Float, sympify, nsimplify, S, Matrix

from .intervalles import Ensemble
from .printers import custom_str, custom_latex
from .custom_functions import frac
from .custom_objects import Temps, Fonction, ProduitEntiers, Decim
from . import sympy_functions
from ..mathlib import end_user_functions
from ..pylib import print_error, split_around_parenthesis, securite
from .parsers import simplifier_ecriture, NBR, traduire_formule, NBR_FLOTTANT, \
                     extraire_chaines, injecter_chaines
from .. import param


class LocalDict(dict):
    def __init__(self, defaut=None):
        dict.__init__(self)
        self.defaut = (defaut if defaut is not None else {})
        self.update(self.defaut)


    def __missing__(self, key):
        # _59 is an alias for ans(59)
        if key.startswith('_'):
            if key[1:].isnumeric():
                return self['ans'](int(key[1:]))
            else:
                if key == len(key)*'_':
                    return self['ans'](-len(key))
        if key in sympy.__dict__:
            return sympy.__dict__[key]
        else:
            return Symbol(key)

    def __setitem__(self, name, value):
        # Pour éviter que l'utilisateur redéfinisse pi, i, e, etc. par mégarde.
        # (Cas particulier: le débugueur winpdb a besoin d'accéder à __builtins__).
        if (name in self.defaut or (name.startswith('_') and name[1:].isalnum())) and name != '__builtins__':
            raise NameError("%s est un nom reserve" %name)
        dict.__setitem__(self, name, value)




class Interprete(object):
    """Un interprêteur de commandes mathématiques, avec gestion des sessions.

    Les options sont les suivantes::

        * `calcul_exact`: mode calcul exact ou calcul approché
        * `ecriture_scientifique`: affiche les résultats en écriture scientifique
          (essentiellement pertinent pour des résultats numériques)
        * `forme_algebrique`: affiche les nombres complexes sous la forme a+ib
        * `simplifier_ecriture_resultat`: Écrire le résultat sous une forme plus
          agréable à lire (suppression des '*' dans '2*x', etc.)
        * `separateur_decimal`: point ou virgule (',' par défaut)
        * `formatage_OOo`: convertir et interpréter les formules OpenOffice
          ou LibreOffice
        * `formatage_LaTeX`: convertir et interpréter les formules LaTeX
        * `ecriture_scientifique_decimales`: nombre de décimales affichées
          en mode écriture scientifique.
        * `precision_calcul`: précision utilisée en interne pour les calculs
          approchés (nombre de chiffres).
        * `precision_affichage`: nombre de chiffres affichés pour les résultats
          approchés
        * `simpify`: convertir automatiquement les expressions au format sympy
        * `verbose`: afficher le détail des transformations effectuées
        * `appliquer_au_resultat`: une opération à appliquer éventuellement
          au résultat. La résultat est représenté par un underscore : _.
          Exemple : 'factoriser(_)'.
        * `ensemble`: 'R' ou 'C' (utilisé pour la résolution des équations).
    """
    def __init__(self,  calcul_exact=True,
                        ecriture_scientifique=False,
                        forme_algebrique=True,
                        simplifier_ecriture_resultat=True,
                        separateur_decimal=',',
                        formatage_OOo=True,
                        formatage_LaTeX=True,
                        ecriture_scientifique_decimales=2,
                        precision_calcul=60,
                        precision_affichage=18,
                        simpify=True,
                        verbose=None,
                        appliquer_au_resultat=None,
                        ensemble='R'
                        ):

        # Dictionnaire par défaut (qui contient les fonctions, variables et constantes prédéfinies).
        self.defaut = vars(end_user_functions).copy()
        self.defaut.update({
                "__builtins__": {},
                "Fonction": Fonction,
                "Matrice": Matrix,
                "Temps": Temps,
                "ProduitEntiers": ProduitEntiers,
                "Ensemble": Ensemble,
                "__sympify__": sympify,
                "ans": self.ans,
                "rep": self.ans, # alias en français :)
#                "__vars__": self.vars,
#                "__decimal__": Decimal,
                "__decimal__": self._decimal,
                "range": numpy.arange,
                "arange": numpy.arange,
                "frac": self._frac,
                "Decim": Decim,
                            })

        # On importe les fonctions python qui peuvent avoir une utilité éventuelle,
        # l'idée étant de ne pas encombrer l'espace des noms inutilement.
        a_importer = ['all', 'isinstance', 'dict', 'oct', 'sorted',
                      'list', 'iter', 'set', 'issubclass', 'getattr',
                      'hash', 'len', 'frozenset', 'ord', 'filter', 'pow',
                      'float', 'divmod', 'enumerate', 'zip',
                      'hex', 'chr', 'type', 'tuple', 'reversed', 'hasattr',
                      'delattr', 'setattr', 'str', 'int', 'any',
                      'min', 'complex', 'bool', 'max', 'True', 'False']

        for nom in a_importer:
            self.defaut[nom] = __builtins__[nom]

        # Espace de noms de l'interprète (qui contiendra notamment toutes
        # les variables définies par l'utilisateur).
        self.vars = LocalDict(self.defaut)
        # Permet à resoudre() et systeme() d'avoir accès à self.vars.
        self.vars['__local_dict__'] = self.vars
        self.defaut['__local_dict__'] = self.vars

        self.calcul_exact = calcul_exact
        # afficher les resultats en ecriture scientifique.
        self.ecriture_scientifique = ecriture_scientifique
        # mettre les résultats complexes sous forme algébrique
        self.forme_algebrique = forme_algebrique
        # Écrire le résultat sous une forme plus agréable à lire
        # (suppression des '*' dans '2*x', etc.)
        self.simplifier_ecriture_resultat = simplifier_ecriture_resultat
        # appliquer les séparateurs personnalisés
        self.separateur_decimal = separateur_decimal or param.separateur_decimal
        # d'autres choix sont possibles, mais pas forcément heureux...
        self.formatage_OOo = formatage_OOo
        self.formatage_LaTeX = formatage_LaTeX
        self.ecriture_scientifique_decimales = ecriture_scientifique_decimales
        self.precision_calcul = precision_calcul
        self.precision_affichage = precision_affichage
        self.verbose = verbose
        self.simpify = simpify
        # Une opération à appliquer à tous les résultats.
        self.appliquer_au_resultat = appliquer_au_resultat
        self.ensemble = ensemble
        self.latex_dernier_resultat = ''
        self.initialiser()

    def _decimal(self, nbr, prec=None):
        """Convertit en fraction avec affichage décimal.
        """
        if prec is None:
            prec = self.precision_calcul
        return Decim(nsimplify(nbr, rational=True), prec=prec)

    def _frac(self, arg):
        """Convertit en fraction.
        """
        return frac(arg)


    def initialiser(self):
        self.clear_state()
        self.derniers_resultats = []


    def evaluer(self, calcul = "", calcul_exact=None):
        if calcul_exact is None:
            calcul_exact = self.calcul_exact

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
                self.warning += " Attention, il manque des parenthèses \"" + parentheses[1][i] + "\"."
            elif difference < 0:
                self.warning += " Attention, il y a des parenthèses \"" + parentheses[1][i] + "\" superflues."
                if calcul.endswith(abs(difference)*parentheses[1][i]):
                    calcul = calcul[:difference]

##        # Transforme les ' en ` et les " en ``
##        calcul = calcul.replace("'", "`").replace('"', '``')

        if self.verbose:
            print("Traitement ({[]}) :  ", calcul)

        if calcul and calcul[0] in "><!=^*/%+":
            calcul = "_" + calcul

        if self.verbose:
            print("Traitement ><!=^*/%+ :  ", calcul)

        if self.formatage_LaTeX and calcul.rstrip().endswith("\\approx"):
            calcul = calcul.rstrip()[:-7] + ">>evalf"

        if ">>" in calcul:
            liste = calcul.split(">>")
            calcul = liste[0]
            for s in liste[1:]:
                calcul = s + "(" + calcul + ")"

        if self.verbose:
            print("Traitement >> :  ", calcul)

        if calcul.startswith('?'):
            calcul = 'aide(%s)' %calcul[1:]
        elif calcul.endswith('?'):
            calcul = 'aide(%s)' %calcul[:-1]

        try:
            param.calcul_approche = not calcul_exact
            # utilisé en particulier dans la factorisation des polynômes
            self._executer(calcul)
        finally:
            param.calcul_approche = False

        if self.appliquer_au_resultat is not None:
            self._executer(self.appliquer_au_resultat)

        dernier_resultat = self.vars["_"]

        self.derniers_resultats.append(dernier_resultat)

        if not calcul_exact:
            return self._formater(sympy_functions.evalf(dernier_resultat, self.precision_calcul))
        return self._formater(dernier_resultat)


    def _formater(self, valeur):
        if isinstance(valeur, Basic):
            valeur = valeur.subs(Float(1), S.One)

        parametres = {'decimales': self.precision_affichage,
                      'mode_scientifique': self.ecriture_scientifique,
                      'decimales_sci': self.ecriture_scientifique_decimales,
                      }
        resultat = custom_str(valeur, **parametres)
        if valeur is None:
            latex = ""
        else:
            try:
                latex = custom_latex(valeur, **parametres)
            except Exception:
                print_error()
                latex = ''


        if self.separateur_decimal != '.' and not isinstance(valeur, str):
            # On détecte les chaînes pour ne pas remplacer à l'intérieur :
            # on extrait les sous-chaînes pour les garder intact.
            resultat, sous_chaines_resultat = extraire_chaines(resultat)
            latex, sous_chaines_latex = extraire_chaines(latex)
            resultat = re.sub(r"[ ]*[,;][ ]*", ' ; ', resultat)
            # Éviter de remplacer \, par \; en LaTex.
            latex = re.sub(r"(?<![\\ ])[ ]*,[ ]*", ';', latex)
            def sep(m):
                return m.group().replace('.', self.separateur_decimal)
            resultat = re.sub(NBR, sep, resultat)
            latex = re.sub(NBR, sep, latex)
            # On réinjecte les sous-chaînes à la fin.
            resultat = injecter_chaines(resultat, sous_chaines_resultat)
            latex = injecter_chaines(latex, sous_chaines_latex)

        if isinstance(valeur, str):
            latex = '\u201C%s\u201D' %valeur

        self.latex_dernier_resultat = latex
        if self.simplifier_ecriture_resultat:
            resultat = simplifier_ecriture(resultat)
        return resultat, latex


    def _traduire(self, formule):
        # La fonction traduire_formule de la librairie formatage permet d'effectuer un certain nombre de conversions.
        if self.verbose or (self.verbose is None and param.debug):
            print('Avant traduction: %s' % repr(formule))
        # traduire_formule() fait le tri entre les fonctions et les autres entrées de self.vars.
        formule = traduire_formule(formule, fonctions=self.vars,
                        OOo=self.formatage_OOo,
                        LaTeX=self.formatage_LaTeX,
                        simpify=self.simpify,
                        verbose=self.verbose,
                        )
        if self.verbose or (self.verbose is None and param.debug):
            print('Après traduction: %s' % repr(formule))

        formule = re.sub("(?<![A-Za-z0-9_])(resous|solve)[(]", "resoudre(", formule)
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
            formule = ('%s("%s", local_dict=__local_dict__, ensemble=%s)%s'
                       % (deb, bloc[1:-1], repr(self.ensemble), fin))
        if self.verbose or (self.verbose is None and param.debug):
            print("Debugging resoudre(): ", i, formule)
        formule = re.sub("(?<![A-Za-z0-9_])(factor|factorise)[(]", "factoriser(", formule)
        i = formule.find("factoriser(")
        if i != -1:
            deb, bloc, fin = split_around_parenthesis(formule, i)
            formule = ('%s(%s, ensemble=%s)'
                       % (deb, bloc[1:-1], repr(self.ensemble)))
        if self.verbose or (self.verbose is None and param.debug):
            print("Debugging factor(): ", formule)
        return formule


    def _executer(self, instruction):
        instruction = instruction.strip()
        # Cas d'une fonction.
        # Exemple: 'f(x,y)=x+y+3' sera traduit en 'f=Fonction((x,y), x+y+3)'
        if re.match("[^=()]+[(][^=()]+[)][ ]*=[^=]", instruction):
            var, val = instruction.split("=", 1)
            var = var.strip()
            i = var.find("(")
            nom = var[:i]
            variables = var[i:]
            instruction = nom + "=Fonction(" + variables + "," + self._traduire(val) + ")"
        # Cas d'une matrice.
        # Exemple : 'mat A = 1 2 3  4 5 6' sera traduit en 'A=mat([[1, 2, 3], [4, 5, 6]])'
        # La syntaxe 'mat A = 1&2&3\\4&5&6' est aussi supportée.
        elif re.match(r"mat\s+\w+\s*=[^=]", instruction):
            var, val = instruction.split("=", 1)
            var = var[3:].strip()
            val = val.strip()
            if self.verbose:
                print(f"Matrice détectée : {val!r}.")
            # Generate the code for the matrix.
            if '\\' in val:
                if r"\\" in val:
                    # mat A = 1 & 2 & 3 \\ 4 & 5 & 6
                    matrix = [s.split('&') for s in val.split(r'\\')]
                else:
                    # mat A = 1 & 2 & 3 \ 4 & 5 & 6
                    matrix = [s.split('&') for s in val.split('\\')]
            else:
                if ";" in val:
                    # mat A = 1 2 3 ; 4 5 6
                    matrix = [s.split() for s in val.split(';')]
                else:
                    # mat A = 1 2 3  4 5 6
                    matrix = [s.split() for s in re.split(r'\s\s+', val)]
            def to_str(liste):
                return "[%s]" % ', '.join(liste)
            matrix_code = to_str(to_str(line) for line in matrix)
            instruction = self._traduire(f"{var}=mat({matrix_code})")
        # Cas général
        else:
            instruction = self._traduire(instruction)

        # dans certains cas, il ne faut pas affecter le résultat à la variable "_" (cela provoquerait une erreur de syntaxe)
        # (Mots clés devant se trouver en début de ligne : dans ce cas, on ne modifie pas la ligne)
        vars = self.vars

        if securite.expression_affectable(instruction):
            instruction = "_=" + instruction
        else:
            vars["_"] = None

        if securite.keywords_interdits_presents(instruction):
            self.warning += ('Les mots-clefs %s sont interdits.'
                               % ', '.join(sorted(securite.keywords_interdits)))
            raise RuntimeError("Mots-clefs interdits.")

        try:
            exec(instruction, vars)
        except NotImplementedError:
            print_error()
            vars["_"] = "?"
        if isinstance(vars["_"], Basic):
            vars["_"] = vars["_"].subs({1.0: 1, -1.0: -1})
            if (self.forme_algebrique and vars["_"].is_number):
                try:
                    vars["_"] = vars["_"].expand(complex=True)
                except NotImplementedError:
                    print_error()

    def ans(self, n = -1):
        if n >= 0:
            n = int(n-1)
        else:
            n = int(n)
        if self.derniers_resultats: return self.derniers_resultats[n]
        self.warning += " Ans(): aucun calcul antérieur."
        return 0

    def clear_state(self):
        self.vars.clear()
        self.vars.update(self.defaut)

    def save_state(self):
        def repr2(expr):
            if isinstance(expr, (types.BuiltinFunctionType, type, types.FunctionType)):
                return expr.__name__
            return repr(expr).replace('\n', ' ')

        l = []
        for k, v in self.vars.items():
            if k not in self.defaut or self.defaut[k] is not v:
                l.append(k + ' = ' + repr2(v))
        variables = '\n'.join(l)

        resultats = '\n    '.join(repr(repr2(res)) + ',' for res in self.derniers_resultats)
        return '%s\n\n@derniers_resultats = [\n    %s\n    ]' % (variables, resultats)


    def load_state(self, state):
        def evaltry(expr):
            "Evalue l'expression. En cas d'erreur, intercepte l'erreur et retourne None."
            # Remplacer 1.23 par Decim('1.23'), sauf à l'intérieur d'une chaîne.
            chaine, sous_chaines = extraire_chaines(expr)
            chaine = re.sub(NBR_FLOTTANT, (lambda x: "Decim('%s')" % x.group()), chaine)
            expr = injecter_chaines(chaine, sous_chaines)

            try:
                return sympify(expr, self.vars.copy())
            except Exception:
                print("Error: l'expression suivante n'a pu être évaluée par l'interprète: %s." %repr(expr))
                print_error()

        self.clear_state()
        etat_brut, derniers_resultats = state.split('@derniers_resultats = ', 1)
        etat = (l.split(' = ', 1) for l in etat_brut.split('\n') if l)
        self.vars.update((k, evaltry(v)) for k, v in etat)
        liste_repr = eval(derniers_resultats, self.vars)
        self.derniers_resultats = [evaltry(s) for s in liste_repr]
