# -*- coding: utf-8 -*-

##--------------------------------------##
#              WxGeometrie               #
#                tabvar                  #
##--------------------------------------##
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
from numpy import arange

from .tablatexlib import traduire_latex, maths
from ...pylib import print_error
from ... import param

def _eval_math(chaine):
    return float(eval(chaine, maths.__dict__))


def _auto_tabval(chaine='', formatage_antecedents='VAL', formatage_images='VAL', precision=0.01):

    chaine_initiale = chaine

    chaine = chaine.replace(param.separateur_decimal, ".")


    m = re.match(r"(?P<fonction>[^:]+)"            # "f(x)=2x+3"
                 r"[ ]+sur[ ]+"                    # " sur "
                 r"\[(?P<intervalle>[^]]+)\]"      # "[-5;5]"
                 r"(.*[ ]+pas[ ]+(de[ ]+)?"        # " avec un pas de "
                 r"(?P<pas>[0-9.]+))?",            # "0,01"
                 chaine)

    # NOTA: Pour l'instant, seul un intervalle de la forme [a;b] est supporté.

    if m is None:
        raise ValueError("Format incorrect.")

    fonction = m.group('fonction')
    intervalle = m.group('intervalle')
    pas = _eval_math(m.group('pas') or '1')


    # Correction automatique: [-5,5] est remplacé par [-5;5]
    # (Attention, toutes les virgules ont été converties en points auparavant !)
    if ';' not in intervalle:
        intervalle = intervalle.replace('.', ';')
    a, b = intervalle.split(';')
    a = _eval_math(a)

    code = "%s:[%s]:%s,%s..%s" % (fonction, precision, a, a + pas, b)

    if param.debug and param.verbose:
        print('Code TABVal:', code)
    return tabval(code, formatage_antecedents=formatage_antecedents, formatage_images=formatage_images) + '% ' + chaine_initiale + '\n'



def tabval(chaine='', formatage_antecedents='VAL', formatage_images='VAL', precision=0.01):
    r"""Syntaxe:
fonction: [precision d'arrondi]: 1ere valeur,2e valeur..valeur finale

Exemples:
\sin(x): -5,-4.9..5
h(x)=sin(x)+1: [0.01]: -5,-4.5..0 ; 0,1..3

Utilisez ; pour séparer plusieurs bloc de valeurs, et // pour indiquer
un retour à la ligne (si le tableau est trop long).

`formatage_images` contient éventuellement une formule pour formater
les valeurs, par exemple '\nombre{VAL}'. La variable VAL correspond à la
valeur du résultat.
"""

# f(x)=x+4:-5,-4..0 ; 2 ; 5,7..10// 12,14..20
# f(x)=x+4:-5..-4..0; 2; 5..7..10// 12,14..20
# f(x)=x+4:-5 -4+1..0

    chaine_originale = chaine = chaine.strip()

    if ':' not in chaine:
        return _auto_tabval(chaine, formatage_antecedents=formatage_antecedents,
                                     formatage_images=formatage_images,
                                     precision=precision)

    chaine = chaine.replace(r'\\', '\n').replace('//', '\n')
    sequence = chaine.split(":", 2)

    if len(sequence) == 3:
        precision = _eval_math(sequence[1].strip('[] '))

    legende = [txt.strip() for txt in sequence[0].split("=", 1)]
    if len(legende) == 2:
        fonction, expression = legende
        # On devine la variable (en principe, elle est entre parenthèses)
        deb = fonction.find("(")
        fin = fonction.find(")")
        if deb == -1:
            variable = "x"
        else:
            variable = fonction[deb+1:fin].strip()
    else:
        fonction = expression = legende[0]
        # Reste à deviner la variable.
        # On cherche les lettres isolées (sauf 'e', qui représente exp(1))
        m = re.search('(?<![A-Za-z])[A-DF-Za-df-z](?![A-Za-z])', expression)
        # Si on n'en trouve pas, la variable sera 'x'
        variable = m.group() if m else 'x'


    lignes = [txt.strip() for txt in sequence[-1].split('\n') if txt.strip()]

    # On génère le code LaTeX
    code = "\\begin{center}"

    # On commence par créer la liste des valeurs
    for ligne in lignes:
        ensemble_valeurs = set()
        for intervalle in ligne.split(';'):
            if '..' in intervalle:
                premier, dernier = intervalle.split('..')
                if ',' in premier:
                    premier, suivant = premier.split(',')
                else:
                    suivant = None
                first_val = float(eval(premier, maths.__dict__))
                last_val = float(eval(dernier, maths.__dict__))
                if suivant is None:
                    pas = 1
                else:
                    next_val = float(eval(suivant, maths.__dict__))
                    pas = next_val - first_val
                ensemble_valeurs.update(arange(first_val, last_val, pas))
                ensemble_valeurs.add(last_val)
            else:
                ensemble_valeurs.add(float(eval(intervalle, maths.__dict__)))

        valeurs = sorted(ensemble_valeurs)

        nbr_colonnes = len(valeurs) + 1

        code_variable = "$" + variable + "$ "
        code_expression = "$" + fonction + "$ "

        expression = traduire_latex(expression)

        def formater(expr, formatage='VAL'):
            assert isinstance(expr, float)
            s = str(expr).rstrip('0')
            if s[-1] == '.':
                s = s[:-1]
            if param.separateur_decimal != '.':
                s = s.replace(".", param.separateur_decimal)
            return ' $' + formatage.replace('VAL', s) + '$ '


        for val in valeurs: # on construit le tableau colonne par colonne
            n = max(len(code_variable), len(code_expression))
            # on justifie avant chaque nouvelle colonne (le code LaTeX sera plus agréable à lire !)
            code_variable = code_variable.ljust(n)
            code_expression = code_expression.ljust(n)
            code_variable += '&' + formater(val, formatage_antecedents)
            try:
                dict = maths.__dict__.copy()
                dict.update({variable: val})
                evaluation = eval(expression, dict)
                if evaluation in (maths.num_oo, maths.num_nan, -maths.num_oo, maths.oo, maths.nan, -maths.oo):
                    code_expression += "& $\\times$ "
                else:
                    code_expression += '&' + formater(precision*round(evaluation/precision), formatage_images)
            except:
                print_error()
                code_expression += "& $\\times$ "

        code += "\n\\begin{tabular}{|" + nbr_colonnes*"c|" + "}\n\\hline\n"
        code += code_variable + "\\\\\n"
        code += "\\hline\n"
        code += code_expression + "\\\\\n"
        code += "\\hline\n\\end{tabular}\n"

    return code + "\\end{center}\n% " + chaine_originale + "\n"
