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

from ...GUI import MenuBar, Panel_API_graphique
from ...GUI.proprietes_objets import Proprietes
from ...geolib import Segment, Texte, Point, TEXTE
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
        # n: entier, f: fraction
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
        fgeo.contenu[u"Instructions"] = [self.instructions.toPlainText()]


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
        self.expression = re.sub('n', self.new_int, self.pattern)
        num, den = self.expression.split('|')
        self.numerateur = num.split(',')
        self.denominateur = den.split(',')
        # Génération du code LaTeX:
        if len(self.numerateur) > 1:
            num = ''.join(self._formater(facteur) for facteur in self.numerateur)
        else:
            num = self.numerateur[0] if self.numerateur else '1'
        if len(self.denominateur) > 1:
            den = ''.join(self._formater(facteur) for facteur in self.denominateur)
        else:
            den = self.denominateur[0] if self.denominateur else '1'
        if den == '1':
            self.expression_latex = num
        else:
            self.expression_latex = r'\frac{%s}{%s}' %(num, den)
        print self.expression, self.numerateur, self.denominateur, self.expression_latex


    def dessiner_tableau(self, lignes=4):
        self.canvas.fenetre = 0, 10, 0, 10
        self.canvas.dessiner_ligne((1, 9, 9, 1 , 1), (1, 1, 9, 9, 1), 'k')
        for i in xrange(1, lignes):
            y = 1 + i*8/lignes
            self.canvas.dessiner_ligne((1, 9), (y, y), 'k')

    def dessiner_tableau(self):
        w, h = self.canvas.dimensions
        self.feuille_actuelle.expression = Texte(self.expression_latex, 0, 0)
        self.canvas.fenetre = 0, w, 0, h
        self.canvas.dessiner_ligne((1, 9, 9, 1 , 1), (1, 1, 9, 9, 1), 'k')
        for i in xrange(1, lignes):
            y = 1 + i*8/lignes
            self.canvas.dessiner_ligne((1, 9), (y, y), 'k')

    def dessiner_tableau(self):
        can = self.canvas

        # Les pixels et les unités correspondent:
        width, height = can.dimensions
        can.fenetre = 0, width, 0, height

        def dessiner_ligne_h(y, **kw):
            return can.dessiner_ligne((10, width - 10), (y, y), 'k', **kw)

        dessiner_texte = partial(can.dessiner_texte, size=18, va='top')

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

        # Hauteur de chaque ligne
        hauteurs = []
        # Objets texte de matplotlib
        txts = []
        # Largeur de la première colonne
        largeur_max = 0
        # marge entre le bord de la case et le texte
        marge = 5
        h = 10
        for txt in chain(['x'], self.numerateur, self.denominateur, [self.expression_latex]):
            dessiner_ligne_h(height - h)
            h += marge
            hauteurs.append(h)
            txt = dessiner_texte(10, height - h, '$%s$' %txt, ha='center')
            txts.append(txt)
            box = can.txt_box(txt)
            h += box.height + marge
            largeur_max = max(largeur_max, box.width)
        dessiner_ligne_h(height - h)

        tab_height = h

        # On centre les textes dans la colonne
        for txt in txts:
            txt.set_x(10 + marge + largeur_max/2)

        def dessiner_ligne_v(x, **kw):
            return can.dessiner_ligne((x, x), (height - 10, height - tab_height) , 'k', **kw)

        dessiner_ligne_v(10)
        dessiner_ligne_v(width - 10)
        # Trait vertical à la fin de la première colonne
        col1 = largeur_max + 10 + 2*marge
        dessiner_ligne_v(col1)

        # On dessine les cases
        n = len(self.numerateur) + len(self.denominateur)
        largeur_restante = width - 10 - col1 - 2*marge
        for i in xrange(1, n):
            dessiner_ligne_v(col1 + i/n*largeur_restante, alpha=.15)

        # On place -oo et +oo
        h = height - marge - 10
        dessiner_texte(col1 + marge, h, '$-\\infty$')
        dessiner_texte(width - 10 - marge, h, '$+\\infty$', ha='right')

        h = tab_height + 2*marge
        for expression in chain(self.numerateur, self.denominateur):
            txt = dessiner_texte(10, h, r'$\bullet\,' + expression + r'\,=\,0\,\,\Longleftrightarrow\,\,x\,=\,$')
            h += can.txt_box(txt).height + 2*marge
