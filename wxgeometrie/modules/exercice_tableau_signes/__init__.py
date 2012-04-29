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

from PyQt4.QtGui import (QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
                         QMessageBox, QTextEdit, QColor)

from sympy import S, solve, gcd

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
        ##"(nx+n)(nx+n)|nx+n"
        # numerateur|denominateur
        # facteur1, facteur2,...|facteur1, facteur2,...
        # n: entier, q: fraction, d: decimal
        self.canvas.fixe = True

        self.entrees = QVBoxLayout()
        self.entrees.addSpacing(30)

        self.panneau = QLabel('')
        self.entrees.addWidget(self.panneau)

        self.entrees.addStretch()
        self.felicitations = QLabel('')
        self.entrees.addWidget(self.felicitations)

        self.entrees.addSpacing(30)
        self.btn_niveau = QPushButton(u"Niveau suivant", self)
        self.btn_niveau.clicked.connect(self.niveau_suivant)
        self.entrees.addWidget(self.btn_niveau)
        self.entrees.addSpacing(50)

        self.sizer = QHBoxLayout()
        self.sizer.addWidget(self.canvas, 1)
        self.sizer.addLayout(self.entrees, 0.2)
        self.finaliser(contenu=self.sizer)

        self.points = 0
        self.niveau = -1
        self.erreurs = 0
        self.niveaux = ["n*x+z", "-n*x+q", "1|q*x+z", "z*x+z,z*x+z", "z*x+q|z*x+z",
                        "z*x+z,z*x+z|z*x+z", "z*x+z,z*x+z|z*x+z,z*x+z"]

        self.niveau_suivant()


    def niveau_suivant(self):
        self.btn_niveau.setEnabled(False)
        self.felicitations.setStyleSheet(
            """QLabel {background-color: white; padding: 5px; border-radius: 5px;
            color:white;}""")
        self.fermer_feuille()
        self.niveau += 1
        self.update_panneau()
        self.pattern = self.niveaux[self.niveau]
        self.generer_expression()

    def update_panneau(self):
        self.panneau.setStyleSheet(
"""QLabel { padding: 10px; border-width: 2px; border-style:solid;
border-radius: 5px; border-color:%s; background-color: %s }"""
%(QColor(30, 144, 255).name(), QColor(176, 226, 255).name())
                        )
        self.panneau.setText((u"<p><b><i>Niveau :</i> %s</b></p>" % self.niveau) +
                                 (u"<p><b><i>Points :</i> %s</b></p>" % self.points) +
                                 (u"<p><i>Erreurs :</i> %s</p>" % self.erreurs))

    def _sauvegarder(self, fgeo, feuille = None):
        Panel_API_graphique._sauvegarder(self, fgeo, feuille)
        ##fgeo.contenu[u"Instructions"] = [self.instructions.toPlainText()]

    def _ouvrir(self, fgeo):
        Panel_API_graphique._ouvrir(self, fgeo)
        if fgeo.contenu.has_key(u"Instructions"):
            self.instructions.setPlainText(fgeo.contenu[u"Instructions"][0])

    def _affiche(self):
        self.dessiner_tableau()

    def naturel(self, m=None):
        u'''Retourne un entier entre 2 et 15.'''
        return str(randint(2, 15))

    def relatif(self, m=None):
        u'''Retourne un entier entre -15 et -2, ou entre 2 et 15.'''
        # signe: 1 ou -1
        signe = 2*randint(0, 1) - 1
        return str(signe*randint(2, 15))

    def decimal(self, m=None):
        u'''Retourne un nombre décimal à deux chiffres.'''
        return self.relatif() + '.' + self.naturel()

    def rationnel(self, m=None):
        u'''Retourne un quotient d'entiers.'''
        while True:
            p = randint(2, 7)
            q = randint(2, 7)
            if p%q:
                break
        signe = 2*randint(0, 1) - 1
        return str(S(signe*p)/S(q))

    def _formater(self, expression):
        if '+' in expression or '-' in expression:
            expression = '(' + expression + ')'
        return expression.replace('*', '')

    def generer_expression(self):
        # Génération de l'expression:
        x = S('x')
        k = 0
        while True:
            k += 1
            # 10000 essais au maximum
            assert k < 10000
            expression = re.sub('n', self.naturel, self.pattern)
            expression = re.sub('z', self.relatif, expression)
            expression = re.sub('d', self.decimal, expression)
            expression = re.sub('q', self.rationnel, expression)
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
            if not any(gcd(S(P), S(Q)).has(x) for P in self.numerateur for Q in self.denominateur):
                # Il ne faut pas qu'un facteur apparaisse à la fois
                # au numérateur et au dénominateur.
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
        print self.expression, self.numerateur, self.denominateur


    def dessiner_tableau(self):
        ##self.fermer_feuille()
        can = self.canvas

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
                t.on_validate = (lambda correct: self.compter_points(correct=correct))
                self.feuille_actuelle.objets[nom] = t
            else:
                t = self.feuille_actuelle.objets[nom]
                t.x = x
                t.y = height - y
                t.style(couleur='b',
                       alignement_horizontal=ha, alignement_vertical=va,
                       attendu=resultat, taille=size, **kw)
            # Compteur qui s'incrémente à chaque nouveau champ.
            # Le but est que chaque champ ait un identifiant unique.
            compteur[0] += 1


        def dessiner_texte(x, y, texte, **kw):
            va = kw.pop('va', 'center')
            size = kw.pop('size', 16)
            return can.dessiner_texte(x, height - y, texte, size=size, va=va, **kw)

        expression_latex = convertir_en_latex(self.expression, mode=None)
        num = '*'.join('(' + s + ')' for s in self.numerateur)
        den = '*'.join('(' + s + ')' for s in self.denominateur)
        if den and num:
            expression_sympy = S('(%s)/(%s)' %(num, den))
        elif num:
            expression_sympy = S('(%s)' %num)
        else:
            assert den
            expression_sympy = S('1/(%s)' %den)

        facteurs_latex = OrderedDict((expr, convertir_en_latex(expr, mode=None))
                                for expr in self.numerateur + self.denominateur)
        facteurs_sympy = OrderedDict((expr, S(expr)) for expr in facteurs_latex)
        facteurs_sols = OrderedDict((expr, solve(facteurs_sympy[expr])[0]) for expr in facteurs_latex)
        facteurs_diff = OrderedDict((expr, facteurs_sympy[expr].diff()) for expr in facteurs_latex)

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

        # On écrit en dessous du tableau les équations à résoudre
        for expression, latex in facteurs_latex.items():
            if facteurs_diff[expression] == 0:
                continue # Fonction constante

            txt = dessiner_texte(10, h, r'$\bullet\,' + latex +
                                    r'\,=\,0\,\,\Longleftrightarrow\,\,x\,=\,$')
            box = can.txt_box(txt)
            resultat = nice_str(facteurs_sols[expression])
            print resultat
            dessiner_champ(18 + box.width, h, ha='left', resultat=resultat)
            ##dessiner_texte(220, height - h, u'\u2713', color='g') # 263A  00D8
            ##dessiner_texte(240, height - h, u'\u2639', color='r') #u'\u26A0'
            h += box.height + 2*marge

            if not facteurs_diff[expression].has('x'):
                # C'est une fonction affine.
                txt = dessiner_texte(30, h, u'Sur $\u211D$, la fonction affine $x\\mapsto %s$ est strictement' %latex)
                box = can.txt_box(txt)
                sens = (u'décroissante' if facteurs_diff[expression] < 0 else u'croissante')
                dessiner_champ(35 + box.width, h, ha='left', choix=choix, resultat=sens)
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

        # valeurs remarquables de x
        sols = sorted(set(facteurs_sols.values()))
        print(sols)

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
                if facteurs_sols[expr] == sol:
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

        self.feuille_actuelle.interprete.commande_executee()
        ##self.feuille_actuelle.objets._.encadrer('r')

    def autocompleter(self):
        for t in self.feuille_actuelle.objets.lister(type=Champ):
            t.texte = t.style('attendu', color='g')
        self.feuille_actuelle.interprete.commande_executee()

    a = property(autocompleter)

    def compter_points(self, **kw):
        if 'correct' in kw:
            if kw['correct']:
                self.points += 1
            else:
                self.points -= 1
                self.erreurs += 1
        if all(obj.correct for obj in self.feuille_actuelle.objets.lister(type=Champ)):
            self.points += 10*self.niveau
            if self.niveau + 1 < len(self.niveaux):
                self.btn_niveau.setEnabled(True)
                self.btn_niveau.setFocus(True)
                self.felicitations.setText(u'<p><b>Félicitations !</b></p>' +
                                           u'<p>Passer au niveau %s</p>' %(self.niveau + 1))
                self.felicitations.setStyleSheet(
                    """QLabel {background-color: %s; padding: 5px;
                       border-radius: 5px;
                       color:white;}""" %QColor(255, 153, 0).name())

            else:
                self.felicitations.setText(u'<p><b>Félicitations !</b></p>' +
                                           u'<p>Dernier niveau terminé !</p>')
                self.felicitations.setStyleSheet(
                    """QLabel {background-color: %s; padding: 5px; border-radius: 5px;
                    color:white;}""" %QColor(102, 205, 0).name())
            ##self.fermer_feuille()
        self.update_panneau()
