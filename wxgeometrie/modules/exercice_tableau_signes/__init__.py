# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

##--------------------------------------#######
#                Probabilités                 #
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

import re
from random import randint
from itertools import chain
from functools import partial

from PyQt4.QtGui import QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox, QTextEdit

from sympy import S, solve

from ...GUI import MenuBar, Panel_API_graphique
from ...GUI.proprietes_objets import Proprietes
from ...geolib import Segment, Texte, Point, Champ, TEXTE
from ...geolib.routines import nice_str
from ...pylib import OrderedDict, print_error
from ...mathlib.parsers import convertir_en_latex
from ... import param






class TabMenuBar(MenuBar):
    def __init__(self, panel):
        MenuBar.__init__(self, panel)

        self.ajouter(u"Fichier", [u"nouveau"], [u"ouvrir"], [u"ouvrir ici"],
                    [u"enregistrer"], [u"enregistrer_sous"], [u"exporter"],
                    [u"exporter&sauver"], None, [u"imprimer"], [u"presse-papier"],
                    None, [u"proprietes"], None, self.panel.doc_ouverts, None, ["fermer"], ["quitter"])
        self.ajouter(u"Editer", ["annuler"], ["refaire"], ["modifier"], ["supprimer"])
        self.ajouter(u"creer")
        self.ajouter(u"Affichage", ["onglet"], None, ["repere"], ["quadrillage"], ["orthonorme"], None, ["zoom_texte"], ["zoom_ligne"], ["zoom_general"], None, ["fenetre"], ["zoomer"], ["dezoomer"], ["orthonormaliser"], [u"zoom_auto"])
        self.ajouter(u"Autres actions", [u"detecter"])
        self.ajouter(u"Outils", [u"options"])
##        self.ajouter(u"Avancé", [u"historique"], [u"securise"], [u"ligne_commande"], [u"debug"])
        self.ajouter(u"avance1")
        self.ajouter(u"?")



class ExercicesTableauxSignes(Panel_API_graphique):

    __titre__ = u"Tableaux de signes" # Donner un titre a chaque module

    def __init__(self, *args, **kw):
        Panel_API_graphique.__init__(self, *args, **kw)
        self.pattern = "n*x+n,n*x+n|n*x+n"
        ##"(nx+n)(nx+n)|nx+n"
        # numerateur|denominateur
        # facteur1, facteur2,...|facteur1, facteur2,...
        # n: entier, q: fraction, d: decimal
        self.canvas.fixe = True

        self.entrees = QVBoxLayout()

        self.entrees.addWidget(QLabel(u" Instructions :"))

        self.appliquer = QPushButton(u"Générer l'arbre", self)
        ##self.appliquer.clicked.connect(self.Appliquer)
        self.entrees.addWidget(self.appliquer)

        self.sizer = QHBoxLayout()
        self.sizer.addWidget(self.canvas, 1)
        self.sizer.addLayout(self.entrees, 0)
        self.finaliser(contenu=self.sizer)
        self.generer_expression()


    def _sauvegarder(self, fgeo, feuille = None):
        Panel_API_graphique._sauvegarder(self, fgeo, feuille)
        ##fgeo.contenu[u"Instructions"] = [self.instructions.toPlainText()]


    def _ouvrir(self, fgeo):
        Panel_API_graphique._ouvrir(self, fgeo)
        if fgeo.contenu.has_key(u"Instructions"):
            self.instructions.setPlainText(fgeo.contenu[u"Instructions"][0])

    def _affiche(self):
        self.dessiner_tableau()

    def new_int(self, m=None):
        u'''Retourne un entier entre 2 et 15.'''
        return str(randint(2, 15))

    def _formater(self, expression):
        if '+' in expression or '-' in expression:
            expression = '(' + expression + ')'
        return expression.replace('*', '')

    def generer_expression(self):
        expression = re.sub('n', self.new_int, self.pattern)
        num, den = expression.split('|')
        self.numerateur = num.split(',')
        self.denominateur = den.split(',')
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
        print self.expression, self.numerateur, self.denominateur


    def dessiner_tableau(self):
        can = self.canvas

        # Les pixels et les unités correspondent:
        width, height = can.dimensions
        can.fenetre = 0, width, 0, height

        def dessiner_ligne_h(y, **kw):
            return can.dessiner_ligne((10, width - 10), (y, y), 'k', **kw)

        def dessiner_champ(x, y, resultat, **kw):
            va = kw.pop('va', 'center')
            ha = kw.pop('ha', 'center')
            ##Cls = Choix if 'choix' in kw else Champ
            t = Champ('', x, y, couleur='b',
                      alignement_horizontal=ha, alignement_vertical=va,
                      attendu=resultat, **kw)
            self.feuille_actuelle.objets.add(t)


        dessiner_texte = partial(can.dessiner_texte, size=18, va='center')

        facteurs_latex = OrderedDict((expr, convertir_en_latex(expr, mode=None))
                                for expr in self.numerateur + self.denominateur)
        facteurs_sols = OrderedDict((expr, solve(S(expr))[0]) for expr in facteurs_latex)
        facteurs_diff = OrderedDict((expr, S(expr).diff()) for expr in facteurs_latex)

        # --------
        # Consigne
        # --------

        expression_latex = convertir_en_latex(self.expression, mode=None)

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

        # valeurs remarquables de x
        sols = sorted(set(facteurs_sols.values()))
        print(sols)

        # -----------------
        # Tableau de signes
        # -----------------

        # Hauteur de chaque ligne
        hauteurs = []
        # Objets texte de matplotlib
        txts = []
        # Largeur de la première colonne
        largeur_max = 0
        # marge entre le bord de la case et le texte
        marge = 5
        h = 10
        # on dessine les lignes verticales et les textes de la 1ère colonne.
        for txt in chain(['x'], facteurs_latex.values(), [expression_latex]):
            dessiner_ligne_h(height - h)
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
        dessiner_ligne_h(height - h)
        hauteurs.append(h)

        tab_height = h

        # On centre les textes dans la colonne
        for txt in txts:
            txt.set_x(10 + marge + largeur_max/2)

        def dessiner_ligne_v(x, **kw):
            return can.dessiner_ligne((x, x), (height - 10, height - tab_height) , 'k', **kw)

        # Bords verticaux du tableau
        dessiner_ligne_v(10)
        dessiner_ligne_v(width - 10)
        # Trait vertical à la fin de la première colonne
        col1 = largeur_max + 10 + 2*marge
        dessiner_ligne_v(col1)

        # On dessine les cases
        n = len(sols)
        largeur_restante = width - 10 - col1 - 2*marge
        largeur_case = largeur_restante/(n + 1)
        choix = ['', '0', u'\u2551']
        for i, sol in enumerate(sols):
            x = col1 + (i + 1)*largeur_case
            dessiner_ligne_v(x, alpha=.15)
            resultat = nice_str(sol)
            dessiner_champ(x, height - .5*(10 + hauteurs[1]), resultat=resultat)
            resultat_final = '0'
            for k, expr in enumerate(facteurs_sols):
                if facteurs_sols[expr] == sol:
                    if expr in self.numerateur:
                        resultat = '0'
                    else:
                        resultat = resultat_final = u'\u2551'
                else:
                    resultat = ''
                ##signe = is sol - 1
                h = .5*(hauteurs[k + 1] + hauteurs[k + 2])
                dessiner_champ(x, height - h, resultat=resultat, choix=choix)
            h = .5*(hauteurs[-1] + hauteurs[-2])
            dessiner_champ(x, height - h, resultat=resultat_final, choix=choix)

        # On place -oo et +oo
        h = height - .5*(hauteurs[0] + hauteurs[1])
        dessiner_texte(col1 + marge, h, '$-\\infty$')
        dessiner_texte(width - 10 - marge, h, '$+\\infty$', ha='right')

        # -------------------------------
        # Équations en dessous du tableau
        # -------------------------------

        choix = ['', u'décroissante', u'croissante']

        # On écrit en dessous du tableau les équations à résoudre
        h = tab_height + 5*marge
        for expression, latex in facteurs_latex.items():
            if facteurs_diff[expression] == 0:
                continue # Fonction constante

            txt = dessiner_texte(10, height - h, r'$\bullet\,' + latex +
                                    r'\,=\,0\,\,\Longleftrightarrow\,\,x\,=\,$')
            box = can.txt_box(txt)
            resultat = nice_str(facteurs_sols[expression])
            print resultat
            dessiner_champ(18 + box.width, height - h,
                                            ha='left', resultat=resultat)
            ##dessiner_texte(220, height - h, u'\u2713', color='g') # 263A  00D8
            ##dessiner_texte(240, height - h, u'\u2639', color='r') #u'\u26A0'
            h += box.height + 2*marge

            txt = dessiner_texte(30, height - h, u'Sur $\u211D$, la fonction affine $x\\mapsto %s$ est strictement' %latex)
            box = can.txt_box(txt)
            sens = (u'décroissante' if facteurs_diff[expression] < 0 else u'croissante')
            dessiner_champ(35 + box.width, height - h, ha='left', choix=choix, resultat=sens)
            h += box.height + 4*marge

        self.feuille_actuelle.interprete.commande_executee()
        ##self.feuille_actuelle.objets._.encadrer('r')


    def autocompleter(self):
        for t in self.feuille_actuelle.objets.lister(type=Champ):
            t.texte = t.style('attendu', color='g')
        self.feuille_actuelle.interprete.commande_executee()
