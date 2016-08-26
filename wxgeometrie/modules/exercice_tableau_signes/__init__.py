# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

#    .-------------------------------------.
#    |    Exercices : tableaux de signes   |
#    '-------------------------------------'
#    Géophar
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

from sympy import S, solve, gcd
from sympy.core.sympify import SympifyError

from ...GUI.panel import Panel_API_graphique
from ...GUI.exercice import ExerciceMenuBar, Exercice
from ...GUI.qtlib import BusyCursor
from ...geolib import Champ
from ...geolib.routines import nice_str
from ...pylib import OrderedDict, print_error
from ...mathlib.parsers import convertir_en_latex, NBR, NBR_SIGNE
from ... import param


# TODO:
# - ajouter un bonus substantiel si les résultats sont donnés
#   sous forme de fraction simplifiée.
# - possibilité de définir facilement les niveaux (fichier texte externe ?)
# - gestion des carrés, des nombres seuls



class TabMenuBar(ExerciceMenuBar):
        pass



class ExercicesTableauxSignes(Exercice):

    titre = u"Tableaux de signes" # Donner un titre a chaque module


    def niveau1(self):
        self.generer_expression("n*x+z")

    def niveau2(self):
        self.generer_expression("-n*x+q")

    def niveau3(self):
        self.generer_expression("1|q*x+z")

    def niveau4(self):
        self.generer_expression("z*x+z,z*x+z")

    def niveau5(self):
        self.generer_expression("z*x+q|z*x+z")

    def niveau6(self):
        self.generer_expression("z*x+z,z*x+z|z*x+z")

    def niveau7(self):
        self.generer_expression("z*x+z,z*x+z|z*x+z,z*x+z")

    def niveau8(self):
        self.generer_expression("-n,z*x+z|-x,(z*x+z)**2")


    def _sauvegarder(self, fgeo, feuille = None):
        Panel_API_graphique._sauvegarder(self, fgeo, feuille)
        fgeo.contenu[u"niveau"] = [str(self.niveau)]
        fgeo.contenu[u"expression"] = [self.raw_expression]
        fgeo.contenu[u"score"] = [str(self.score)]
        fgeo.contenu[u"erreurs"] = [str(self.erreurs)]

    def _ouvrir(self, fgeo):
        # Il ne doit y avoir qu'une seule feuille ouverte à la fois.
        # XXX: intégrer cette fonctionnalité directement au Panel.
        self.fermer_feuilles()
        Panel_API_graphique._ouvrir(self, fgeo)
        if u"expression" in fgeo.contenu:
            self.generer_expression(expr=fgeo.contenu[u"expression"][0])
            ##self.dessiner_tableau()
        if u"niveau" in fgeo.contenu:
            self.niveau = int(fgeo.contenu[u"niveau"][0])
        if u"score" in fgeo.contenu:
            self.score = int(fgeo.contenu[u"score"][0])
        if u"erreurs" in fgeo.contenu:
            self.erreurs = int(fgeo.contenu[u"erreurs"][0])
        self.update_panneau()


    def _affiche(self):
        with BusyCursor():
            self.dessiner_tableau()

    def _formater(self, expression):
        expression = expression.replace('**', '^').replace('*', '').replace(' ', '')
        if not re.match('-?(%s)?x?(\(.+\)(\^%s)?)?$' % (NBR, NBR), expression):
            expression = '(' + expression + ')'
        return expression

    def str_naturel(self, m):
        return str(self.naturel())

    def str_relatif(self, m):
        return str(self.relatif())

    def str_decimal(self, m):
        return str(self.decimal())

    def str_rationnel(self, m):
        return str(self.rationnel())

    def generer_expression(self, pattern):
        u"""Génère une expression aléatoire en fonction respectant le format
        en cours.

        Si `pattern` est déjà une expression, l'expression retournée
        est identique à la valeur entrée.
        """
        # Génération de l'expression:
        x = S('x')
        k = 0
        while True:
            k += 1
            # 10000 essais au maximum
            assert k < 10000
            expression = re.sub('n', self.str_naturel, pattern)
            expression = re.sub('z', self.str_relatif, expression)
            expression = re.sub('d', self.str_decimal, expression)
            expression = re.sub('q', self.str_rationnel, expression)
            self.raw_expression = expression
            expression = expression.replace('+-', '-').replace('-+', '-')
            if '|' in expression:
                num, den = expression.split('|')
            else:
                num = expression
                den = ''
            num = num.strip()
            den = den.strip()
            if not num or num == '1':
                self.numerateur = []
            else:
                self.numerateur = num.split(',')
            if not den or den == '1':
                self.denominateur = []
            else:
                self.denominateur = den.split(',')
            # On évite les racines multiples
            racines = []
            for facteur in self.numerateur + self.denominateur:
                racines.extend(solve(facteur))
            if len(racines) == len(set(racines)):
                # Pas de racine multiple
                break

        # Génération de l'expression:
        if len(self.numerateur) > 1:
            num = ''.join(self._formater(facteur) for facteur in self.numerateur)
        else:
            num = self.numerateur[0] if self.numerateur else '1'
        if len(self.denominateur) > 1:
            den = ''.join(self._formater(facteur) for facteur in self.denominateur)
        else:
            den = self.denominateur[0] if self.denominateur else '1'
        if den == '1':
            self.expression = num
        else:
            self.expression = '(%s)/(%s)' %(num, den)

        # On génère tous les dictionnaires utiles à la construction du tableau
        self.expression_latex = convertir_en_latex(self.expression, mode=None)
        num = '*'.join('(' + s + ')' for s in self.numerateur)
        den = '*'.join('(' + s + ')' for s in self.denominateur)
        if den and num:
            self.expression_sympy = S('(%s)/(%s)' %(num, den))
        elif num:
            self.expression_sympy = S('(%s)' %num)
        else:
            assert den
            self.expression_sympy = S('1/(%s)' %den)

        self.facteurs_latex = fact_latex = OrderedDict((expr, convertir_en_latex(expr, mode=None))
                                for expr in self.numerateur + self.denominateur)
        self.facteurs_sympy = fact_sympy = OrderedDict((expr, S(expr)) for expr in fact_latex)
        self.facteurs_sols = OrderedDict((expr, solve(fact_sympy[expr])) for expr in fact_latex)
        self.facteurs_diff = OrderedDict((expr, fact_sympy[expr].diff(S('x'))) for expr in fact_latex)

        # valeurs remarquables de x
        self.sols = []
        for sols in self.facteurs_sols.values():
            self.sols.extend(sols)
        self.sols.sort()
        if param.debug:
            print('(Exercice tableau de signes) Liste des solutions: ' + str(self.sols))



    def dessiner_tableau(self):
        ##self.fermer_feuille()
        can = self.canvas
        expression_latex = self.expression_latex
        expression_sympy = self.expression_sympy
        facteurs_latex = self.facteurs_latex
        facteurs_sympy = self.facteurs_sympy
        facteurs_sols = self.facteurs_sols
        facteurs_diff = self.facteurs_diff
        sols = self.sols


        # Lorsque l'affichage est actualisé (fenêtre redimensionnée par
        # exemple), le champ n'est pas récréé, mais seulement mis à jour.
        # C'est primordial, car sinon, de nouveaux champs vides se superposent
        # aux anciens, au lieu que les anciens soient déplacés.
        # Si la feuille contient déjà des champs, c'est qu'il s'agit d'une
        # simple mise à jour ; il ne faut donc *pas* recréer les champs.
        creation = self.feuille_actuelle.objets.lister(type=Champ) == []

        # Les pixels et les unités correspondent:
        width, height = can.dimensions
        can.fenetre = 0, width, 0, height

        def dessiner_ligne_h(y, **kw):
            return can.dessiner_ligne((10, width - 30), (height - y, height - y), 'k', **kw)

        def dessiner_champ(x, y, resultat, compteur=[0], **kw):
            va = kw.pop('va', 'center')
            ha = kw.pop('ha', 'center')
            size = kw.pop('size', 16)
            ##Cls = Choix if 'choix' in kw else Champ
            nom = 'champ' + str(compteur[0])
            if creation:
                t = Champ('', x, height - y, couleur='b',
                       alignement_horizontal=ha, alignement_vertical=va,
                       attendu=resultat, taille=size, **kw)
                self.feuille_actuelle.objets[nom] = t
            else:
                t = self.feuille_actuelle.objets[nom]
                t.x = x
                t.y = height - y
                t.style(couleur='b',
                       alignement_horizontal=ha, alignement_vertical=va,
                       attendu=resultat, taille=size, **kw)
            t.evt_valider = self.compter_points
            t.valider = self._valider
            # Compteur qui s'incrémente à chaque nouveau champ.
            # Le but est que chaque champ ait un identifiant unique.
            compteur[0] += 1


        def dessiner_texte(x, y, texte, **kw):
            va = kw.pop('va', 'center')
            size = kw.pop('size', 16)
            return can.dessiner_texte(x, height - y, texte, size=size, va=va, **kw)


        # Paramètre d'espacement (marge entre le bord d'une case et le texte).
        marge = 4

        # --------
        # Consigne
        # --------

        txt = dessiner_texte(10, 10, u"Étudier le signe de l'expression $"
                                  + expression_latex + u'$ sur $\u211D$.',
                                  va='top', weight='bold', backgroundcolor='#ffffb5')
        box = can.txt_box(txt)
        h = 10 + box.height + 4*marge

        # -------------------------------
        # Équations préalables au tableau
        # -------------------------------

        choix = [u'décroissante', u'croissante']

        # On écrit au dessus du tableau les équations à résoudre :
        for expression, latex in facteurs_latex.items():
            # S'il y a des solutions:
            if facteurs_sols[expression]:
                assert len(facteurs_sols[expression]) == 1, \
                    ("%s a plusieurs solution (non pris en charge pour l'instant)." % expression)
                if facteurs_diff[expression] == 0:
                    continue # Fonction constante

                txt = dessiner_texte(10, h, r'$\bullet\,' + latex +
                                        r'\,=\,0\,\,\Longleftrightarrow\,\,x\,=\,$')
                box = can.txt_box(txt)
                resultat = nice_str(facteurs_sols[expression][0])
                ##print resultat
                dessiner_champ(18 + box.width, h, ha='left', resultat=resultat)
                ##dessiner_texte(220, height - h, u'\u2713', color='g') # 263A  00D8
                ##dessiner_texte(240, height - h, u'\u2639', color='r') #u'\u26A0'
                h += box.height + 2*marge

                if facteurs_sympy[expression].has('x'):
                    if not facteurs_diff[expression].has('x'):
                        # C'est une fonction affine.
                        txt = dessiner_texte(30, h, u'Sur $\u211D$, la fonction affine'
                                               u' $x\\mapsto %s$ est strictement' %latex)
                        box = can.txt_box(txt)
                        sens = (u'décroissante' if facteurs_diff[expression] < 0 else u'croissante')
                        dessiner_champ(35 + box.width, h, ha='left', choix=choix, resultat=sens)
                        h += box.height + 3*marge
                    elif facteurs_sympy[expression].as_base_exp()[1] == 2:
                        # C'est un carré.
                        txt = dessiner_texte(30, h, u'Sur $\u211D$, un carré est toujours')
                        box = can.txt_box(txt)
                        dessiner_champ(35 + box.width, h, ha='left', resultat='positif')
                        h += box.height + 3*marge



        # -------------------------------------------------------------
        # |     x      | -oo        val1     ...     valn          +oo |
        # -------------------------------------------------------------
        # | facteur 1  |                                               |
        # -------------------------------------------------------------
        # |    ...     |                                               |
        # -------------------------------------------------------------
        # | facteur n  |                                               |
        # -------------------------------------------------------------
        # | Expression |                                               |
        # -------------------------------------------------------------


        # -----------------
        # Tableau de signes
        # -----------------

        # Hauteur de chaque ligne horizontale
        hauteurs = []
        # Objets texte de matplotlib
        txts = []
        # Largeur de la première colonne
        largeur_max = 0

        # Hauteur de la 1ère ligne
        tab_hmin = h

        # On n'affiche pas la dernière ligne si il n'y a qu'un seul
        # "facteur". Par ex, si l'expression est juste 2*x+3.
        print_last_line = self.denominateur or len(self.numerateur) > 1

        textes = ['x'] + facteurs_latex.values()
        if print_last_line:
            textes.append(expression_latex)

        # on dessine les lignes verticales et les textes de la 1ère colonne.
        for txt in textes:
            dessiner_ligne_h(h)
            hauteurs.append(h)
            h += marge
            y = height - h
            txt = dessiner_texte(10, y, '$%s$' %txt, ha='center')
            box = can.txt_box(txt)
            hauteur_txt = max(box.height, 25)
            txt.set_y(y - .5*hauteur_txt)
            txts.append(txt)

            h += hauteur_txt + marge
            largeur_max = max(largeur_max, box.width)
        dessiner_ligne_h(h)
        hauteurs.append(h)

        # Hauteur de la 1ère ligne
        tab_hmax = h

        # On centre les textes dans la colonne
        for txt in txts:
            txt.set_x(10 + marge + largeur_max/2)

        def dessiner_ligne_v(x, **kw):
            return can.dessiner_ligne((x, x), (height - tab_hmin, height - tab_hmax) , 'k', **kw)

        # Bords verticaux du tableau
        dessiner_ligne_v(10)
        dessiner_ligne_v(width - 30)
        # Trait vertical à la fin de la première colonne
        col1 = largeur_max + 10 + 2*marge
        dessiner_ligne_v(col1)

        # Position de chaque ligne verticale
        colonnes = [10, col1]

        # On dessine les cases
        n = len(sols)
        largeur_restante = width - 30 - col1 - 2*marge
        largeur_case = largeur_restante/(n + 1)
        choix = [' ', '0', u'\u2551']
        for i, sol in enumerate(sols):
            x = col1 + (i + 1)*largeur_case
            dessiner_ligne_v(x, alpha=.15)
            colonnes.append(x)
            resultat = nice_str(sol)
            dessiner_champ(x, .5*(hauteurs[0] + hauteurs[1]), resultat=resultat)
            resultat_final = '0'
            for k, expr in enumerate(facteurs_sols):
                if sol in facteurs_sols[expr]:
                    resultat = '0'
                    if expr in self.denominateur:
                        resultat_final = u'\u2551'
                else:
                    resultat = ' '
                ##signe = is sol - 1
                h = .5*(hauteurs[k + 1] + hauteurs[k + 2])
                dessiner_champ(x, h, resultat=resultat, choix=choix)
            if print_last_line:
                h = .5*(hauteurs[-1] + hauteurs[-2])
                dessiner_champ(x, h, resultat=resultat_final, choix=choix)

        colonnes.append(width - 30)

        # On place -oo et +oo
        h = .5*(hauteurs[0] + hauteurs[1])
        dessiner_texte(col1 + marge, h, '$-\\infty$')
        dessiner_texte(width - 30 - marge, h, '$+\\infty$', ha='right')

        # Pour remplir le tableau de signes, le plus simple est encore
        # de tester le signe dans chaque case, par exemple avec la valeur
        # centrale de la case.
        xmin = sols[0] - 10   # pour remplacer -oo
        xmax = sols[-1] + 10  # pour remplacer +oo
        valeurs = [xmin] + sols + [xmax]

        var_x = S('x')
        choix = ['-', '+']
        for i, val in enumerate(valeurs[:-1]):
            m = .5*(val + valeurs[i + 1])
            for k, expr in enumerate(facteurs_sols):
                img = facteurs_sympy[expr].subs(var_x, m)
                assert img != 0
                signe = ('+' if img > 0 else '-')
                h = .5*(hauteurs[k + 1] + hauteurs[k + 2])
                x = .5*(colonnes[i + 1] + colonnes[i + 2])
                dessiner_champ(x, h, resultat=signe, choix=choix)

            if print_last_line:
                img = expression_sympy.subs(var_x, m)
                signe = ('+' if img > 0 else '-')
                h = .5*(hauteurs[-2] + hauteurs[-1])
                dessiner_champ(x, h, resultat=signe, choix=choix)

        ##self.feuille_actuelle.interprete.commande_executee()
        ##self.feuille_actuelle.objets._.encadrer('r')

    @staticmethod
    def _valider(reponse, attendu):
        attendu = attendu.replace(' ', '').replace(',', '.')
        reponse = reponse.replace(' ', '').replace(',', '.')
        if attendu == reponse:
            return True
        else:
            try:
                if abs(float(S(attendu) - S(reponse))) < param.tolerance:
                    return True
            except (SympifyError, ValueError):
                pass
            except Exception:
                print_error()
        return False
##
    ##def _valider_txt(reponse, attendu):
        ##return reponse.replace(' ', '').rstrip('.') == attendu.replace(' ', '')

    def bonus(self, expr):
        expr = expr.replace(',', '.')
        return bool(re.match("(%s|%s/%s)$" % (NBR_SIGNE, NBR_SIGNE, NBR_SIGNE), expr))
