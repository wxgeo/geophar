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
from random import randint, choice
from itertools import chain
from functools import partial

from PyQt4.QtGui import (QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
                         QMessageBox, QTextEdit, QColor, QToolTip, QCursor)

from sympy import S, solve, gcd, simplify
from sympy.core.sympify import SympifyError

from ...GUI import MenuBar, Panel_API_graphique
from ...GUI.proprietes_objets import Proprietes
from ...geolib import Segment, Texte, Point, Droite, Champ, TEXTE, NOM
from ...geolib.routines import nice_str, det, vect
from ...pylib import OrderedDict, print_error
from ...mathlib.parsers import convertir_en_latex, traduire_formule
from ... import param
from .barre_outils_ex_eq_dte import BarreOutilsExEqDte


# TODO:
# - ajouter un bonus substantiel si les résultats sont donnés
#   sous forme de fraction simplifiée.
# - possibilité de définir facilement les niveaux (fichier texte externe ?)
# - gestion des carrés, des nombres seuls



class TabMenuBar(MenuBar):
    def __init__(self, panel):
        MenuBar.__init__(self, panel)

        self.ajouter(u"Fichier", [u"Recommencer", u"Recommencer au niveau 0.", u"Ctrl+N", panel.reinitialiser],
                    [u"ouvrir"],
                    [u"enregistrer"], [u"enregistrer_sous"], [u"exporter"],
                    [u"exporter&sauver"], None, [u"imprimer"], [u"presse-papier"],
                    None, [u"proprietes"], None, ["fermer"], ["quitter"])
        self.ajouter(u"Editer", ["annuler"], ["refaire"], ["modifier"], ["supprimer"])
        self.ajouter(u"Affichage", ["onglet"], ["plein_ecran"], None, ["zoom_texte"], ["zoom_ligne"], ["zoom_general"])
        self.ajouter(u"Outils", [u"options"])
        self.ajouter(u"avance1")
        self.ajouter(u"?")



class ExercicesEquationsDroites(Panel_API_graphique):

    __titre__ = u"Équations de droites" # Donner un titre a chaque module

    def __init__(self, *args, **kw):
        Panel_API_graphique.__init__(self, BarreOutils = BarreOutilsExEqDte, *args, **kw)
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

        self.reinitialiser()


    def reinitialiser(self):
        if param.debug:
            print(u'Module %s: réinitialisation...' % self.nom)
        self.score = 0
        self.niveau = 0
        self.erreurs = 0
        self.niveau_suivant()


    def niveau_suivant(self, niveau=None):
        # On ferme toutes les feuilles ouvertes (inutile en principe),
        # et on en ouvre une nouvelle.
        self.fermer_feuilles()
        # Paramètres par défaut:
        self.canvas.fenetre = -8, 8, -10, 8
        self.canvas.afficher_axes = True
        self.canvas.quadrillage_defaut()
        self.canvas.ratio = None
        self.canvas.repere = ('O', 'i', 'j')
        self.afficher_barre_outils(False)
        # Ne pas éditer les champs/textes avec [Entrée]
        self.canvas.editeur.actif = False
        # Ne pas éditer les objets par un clic droit
        self.canvas.edition_par_clic_droit = False
        # Et on change de niveau...
        if niveau in (None, False):
            # None ou False (False est renvoyé par Qt via QAbstractBouton.clicked)
            self.niveau += 1
        else:
            self.niveau = niveau
        if param.debug:
            print("== Niveau %s ==" % self.niveau)
        getattr(self, 'niveau%s' % self.niveau)()

        self.btn_niveau.setEnabled(False)
        self.felicitations.setStyleSheet(
            """QLabel {background-color: white; padding: 5px; border-radius: 5px;
            color:white;}""")
        self.update_panneau()

    n = niveau_suivant

    # ------------------------------------------------------
    # Niveaux 1 à 7 : lecture graphique d'équation de droite
    # ------------------------------------------------------

    def exercice_lire_equation_AB(self, pointA, pointB):
        u"""Lire graphiquement l'équation de la droite (AB).

        C'est l'exercice à la base des niveaux 1 à 7.
        """
        xA, yA = pointA
        xB, yB = pointB
        A = Point(*pointA, fixe=True)
        B = Point(*pointB, fixe=True)
        self.feuille_actuelle.objets['A'] = A
        self.feuille_actuelle.objets['B'] = B
        # Ne pas afficher l'équation !
        d = Droite(A, B, afficher_info=False)
        self.feuille_actuelle.objets['d'] = d
        if xA == xB:
            reponse = 'x=' + str(xA)
        else:
            reponse = ('y=%s*x+%s' % self.eq_reduite(pointA, pointB))
        xmin, xmax, ymin, ymax = self.canvas.fenetre
        print 'Fenetre::', self.canvas.fenetre, '--', xmin, ymin
        champ = Champ('', xmin, ymin, fond='#ffffb5',
                    prefixe=(ur"Dans le repère $(O;\,\vec\imath,\,\vec\jmath)$, "
                             u"la droite $(AB)$ a pour équation "),
                    alignement_horizontal='left', alignement_vertical='bottom',
                    attendu=reponse)
        print 'xy::', champ.xy
        champ.valider = self.valider_eq
        champ.evt_valider = self.compter_points
        self.feuille_actuelle.objets['champ1'] = champ


    def niveau1(self):
        yA = self.relatif(7)
        if yA > 0:
            yB = yA - randint(1, 3)
        else:
            yB = yA + randint(1, 3)
        self.exercice_lire_equation_AB((0, yA), (1, yB))


    def niveau2(self):
        yA = self.relatif(7)
        if yA > 0:
            yB = yA - choice([1, 3, 5])
        else:
            yB = yA + choice([1, 3, 5])
        self.exercice_lire_equation_AB((0, yA), (-2, yB))


    def niveau3(self):
        while True:
            yA = self.relatif(7)
            yB = self.relatif(7)
            if abs(yB - yA) > 5:
                break
        while True:
            xB = self.relatif(7)
            if abs(xB) > 5:
                break
        self.exercice_lire_equation_AB((0, yA), (xB, yB))


    def niveau4(self):
        u"""Droite horizontale."""
        yA = self.relatif(7)
        while True:
            xA = self.relatif(7)
            xB = self.relatif(7)
            if abs(xB - xA) > 5:
                break
        self.exercice_lire_equation_AB((xA, yA), (xB, yA))


    def niveau5(self):
        u"""Droite verticale."""
        xA = self.relatif(7)
        while True:
            yA = self.relatif(7)
            yB = self.relatif(7)
            if abs(yB - yA) > 5:
                break
        self.exercice_lire_equation_AB((xA, yA), (xA, yB))


    def niveau6(self, n=7):
        """Droite oblique ne coupant pas l'axe des ordonnées sur une
        graduation ; il faut donc calculer (ou deviner) l'ordonnée
        à l'origine."""
        for i in xrange(1000):
            while True:
                xA = self.relatif(n)
                xB = self.relatif(n)
                if abs(xB - xA) > 5:
                    break
            while True:
                yA = self.relatif(7)
                yB = self.relatif(7)
                if abs(yB - yA) > 5:
                    break
            # On calcule l'ordonnée à l'origine (sous forme de fraction sympy).
            a, b = self.eq_reduite((xA, yA), (xB, yB))
            print b
            if b.q not in (1, 2):
                # Le dénominateur de l'ordonnée à l'origine ne doit pas être 1 ou 2.
                break
        self.exercice_lire_equation_AB((xA, yA), (xB, yB))


    def niveau7(self):
        self.canvas.ratio = 4
        self.canvas.quadrillages = (((.25, 1), ':', 0.5, 'k'),)
        self.canvas.fenetre = -4.5, 4.5, -10, 8
        print self.canvas.fenetre
        self.niveau6(n=4)
        self.feuille_actuelle.objets['champ1'].y = -9


    def valider_eq(self, reponse, attendu):
        reponse = traduire_formule(reponse)
        assert attendu.count('=') == 1
        if reponse.count('=') != 1:
            return False
        g, d = attendu.split('=')
        attendu = '%s-(%s)' %(g, d)
        g, d = reponse.split('=')
        reponse = '%s-(%s)' %(g, d)
        reponse = reponse.replace(',', '.')
        quotient = '(%s)/(%s)' % (reponse, attendu)
        try:
            # Les deux équations doivent être « proportionelles ».
            return not simplify(S(quotient)).free_symbols
        except (SympifyError, ValueError):
            pass
        except Exception:
            print_error()
        return False


    def eq_reduite(self, A, B):
        u"""Équation réduite exacte de la droite (AB).

        La droite ne doit pas être verticale."""
        xA, yA = A
        xB, yB = B
        assert xA != xB, "Droite verticale !"
        a = S(yB - yA)/(xB - xA)
        b = yA - a*xA
        return a, b


    # --------------------------------------------
    # Niveau 8 : Résoudre graphiquement un système
    # --------------------------------------------

    def niveau8(self):
        u"""Résolution graphique de système.

        Construire deux droites d'équations données.
        Lire les coordonnées du point d'intersection."""
        self.canvas.fenetre = -8, 8, -10, 11
        self.canvas.afficher_axes = True
        self.canvas.quadrillage_defaut()
        self.afficher_barre_outils(True)
        self.canvas.grille_aimantee = True
        ##self.canvas.editeur.actif = True


        # Point d'intersection
        C = self.couple()
        # On génère deux points A, et B, appartenant respectivement
        # aux droites d1 et d2.
        # Contraintes :
        # - les points A, B, C ne doivent pas être alignés ;
        # - les droites (AC) et (BC) ne doivent être ni horizontales,
        #   ni verticales.
        while True:
            A = self.couple()
            B = self.couple()
            # A, B, C non alignés
            if det(vect(A, C), vect(B, C)) == 0:
                continue
            # (AC) et (BC) ni verticales, ni horizontales
            if all((A[0] - C[0], A[1] - C[1], B[0] - C[0], B[1] - C[1])):
                break
        if param.debug:
            print 'A,B,C:', A, B, C
        # on génère les deux équations de droite
        x = S('x')
        ##def eq_latex(pt1, pt2):
            ##a, b = self.eq_reduite(pt1, pt2)
            ##a = str(a)
            ##if a in ('1', '-1'):
                ##a = a[:-1]
            ##b = str(b)
            ##return convertir_en_latex('y=%s*x+%s' % (a, b))
        def format(eq):
            eq = eq.replace('=1*x', '=x').replace('=-1*x', '=-x').replace('+0', '')
            eq = convertir_en_latex(eq)
            return eq
        a, b = self.eq_reduite(A, C)
        eq1 = format('y=%s*x+%s' % (a, b))
        c, d = self.eq_reduite(B, C)
        eq2 = format('y=%s*x+%s' % (c, d))

        xmin, xmax, ymin, ymax = self.canvas.fenetre

        txt = Texte((u"On note $d_1$ la droite d'équation %s, "
                  u"et $d_2$ la droite d'équation %s.\n"
                  u"Construire les droites $d_1$ puis $d_2$ dans le repère ci-dessous.")
                  % (eq1, eq2), xmin, ymax, fond='#ffffb5', fixe=True,
                  alignement_horizontal='left', alignement_vertical='top')
        self.feuille_actuelle.objets['txt1'] = txt
        champ = Champ('', xmin, ymin, prefixe=u"Le couple solution du système est (",
                 alignement_vertical='bottom', alignement_horizontal='left',
                 attendu=str(C), fond='#ffffb5', suffixe=')')
        self.feuille_actuelle.objets['champ1'] = champ
        champ.valider = self.valider_couple
        champ.evt_valider = self.compter_points
        ch1 = Champ('', visible=False, attendu='ok')
        self.feuille_actuelle.objets['champ_cache_d1'] = ch1
        ch1.evt_valider = self.compter_points
        ch2 = Champ('', visible=False, attendu='ok')
        ch2.evt_valider = self.compter_points
        self.feuille_actuelle.objets['champ_cache_d2'] = ch2
        self.feuille_actuelle.lier(partial(self.verifier_feuille, eq1=(a, b), eq2=(c, d)))


    def verifier_feuille(self, eq1, eq2):
        print eq1, eq2
        for nom, eq in (('d1', eq1), ('d2', eq2)):
            if nom in self.feuille_actuelle.objets.noms:
                d = self.feuille_actuelle.objets[nom]
                d.style(legende=NOM)
                champ = self.feuille_actuelle.objets['champ_cache_' + nom]
                M, N = d
                M = (int(M.x), int(M.y))
                N = (int(N.x), int(N.y))
                if self.eq_reduite(M, N) == eq:
                    d.style(couleur='g')
                    champ.texte = 'ok'
                    msg = 'La droite %s est correcte.' % nom
                    if nom == 'd1':
                        msg += ' Construisez maintenant d2.'
                else:
                    print self.eq_reduite(*d), eq
                    d.style(couleur='r')
                    # On peut mettre n'importe quoi différent de ok dans
                    # champ, l'idée étant que si la droite est fausse mais
                    # n'a pas changé, on ne perde pas de point, et par
                    # contre on perde des points en cas de changement si
                    # c'est toujours faux.
                    champ.texte = str(d.equation)
                    msg = "Attention, la droite %s est fausse." % nom
                QToolTip.showText(QCursor.pos(), msg)
                self.canvas.message(msg, temporaire=False)


    def valider_couple(self, reponse, attendu):
        reponse = reponse.replace(';', ',')
        try:
            if S(reponse) == S(attendu):
                return True
        except Exception:
            print_error()
        return False


    def ax_b(self):
        u"Générer une expression sympy de la forme ax+b, avec a, b dans Z."
        return self.relatif()*S('x') + self.relatif()


    def update_panneau(self):
        self.panneau.setStyleSheet(
            """QLabel { padding: 10px; border-width: 2px; border-style:solid;
            border-radius: 5px; border-color:%s; background-color: %s }"""
            %(QColor(30, 144, 255).name(), QColor(176, 226, 255).name())
                        )
        self.panneau.setText((u"<p><b><i>Niveau :</i> %s</b></p>" % self.niveau) +
                                 (u"<p><b><i>Points :</i> %s</b></p>" % self.score) +
                                 (u"<p><i>Erreurs :</i> %s</p>" % self.erreurs))
        champs = self.feuille_actuelle.objets.lister(type=Champ)
        if champs and all(obj.correct for obj in champs):
            if hasattr(self, 'niveau' + str(self.niveau + 1)):
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

    ##def _sauvegarder(self, fgeo, feuille = None):
        ##Panel_API_graphique._sauvegarder(self, fgeo, feuille)
        ##fgeo.contenu[u"niveau"] = [str(self.niveau)]
        ##fgeo.contenu[u"expression"] = [self.raw_expression]
        ##fgeo.contenu[u"score"] = [str(self.score)]
        ##fgeo.contenu[u"erreurs"] = [str(self.erreurs)]
##
    def _ouvrir(self, fgeo):
        pass
        ### Il ne doit y avoir qu'une seule feuille ouverte à la fois.
        ### XXX: intégrer cette fonctionnalité directement au Panel.
        ##self.fermer_feuilles()
        ##Panel_API_graphique._ouvrir(self, fgeo)
        ##if fgeo.contenu.has_key(u"expression"):
            ##self.generer_expression(expr=fgeo.contenu[u"expression"][0])
            ##self.dessiner_tableau()
        ##if fgeo.contenu.has_key(u"niveau"):
            ##self.niveau = int(fgeo.contenu[u"niveau"][0])
        ##if fgeo.contenu.has_key(u"score"):
            ##self.score = int(fgeo.contenu[u"score"][0])
        ##if fgeo.contenu.has_key(u"erreurs"):
            ##self.erreurs = int(fgeo.contenu[u"erreurs"][0])
        ##self.update_panneau()

    ##def _affiche(self):
        ##self.dessiner_tableau()


    # --------------------------------
    # Génération de nombres aléatoires
    # --------------------------------

    @staticmethod
    def signe():
        return 2*randint(0, 1) - 1

    def naturel(self, n=15):
        u'''Retourne un entier entre 2 et `n`.'''
        return randint(2, n)

    def relatif(self, n=15):
        u'''Retourne un entier entre -`n` et -2, ou entre 2 et `n`.'''
        # signe: 1 ou -1
        signe = 2*randint(0, 1) - 1
        return self.signe()*self.naturel(n)

    def rationnel(self, n=7):
        u'''Retourne un quotient d'entiers.'''
        while True:
            p = self.naturel(n)
            q = self.naturel(n)
            if p%q:
                break
        return self.signe()*S(p)/S(q)

    def couple(self, m=7, n=7):
        u"""Retourne un couple d'entiers relatifs."""
        return self.relatif(m), self.relatif(n)

    def autocompleter(self):
        ##if self.btn_niveau.isEnabled():
            ##self.niveau_suivant()
        self.btn_niveau.click()
        for t in self.feuille_actuelle.objets.lister(type=Champ):
            t.texte = t.style('attendu', color='g')
        ##self.parent.parent.ligne_commande.setFocus()

    a = property(autocompleter)

    def compter_points(self, **kw):
        if 'correct' in kw and 'correct_old' in kw and 'champ' in kw:
            if kw['correct']:
                if not kw['correct_old']:
                    if not kw['champ'].style('choix'):
                        # C'est plus dur s'il n'y a pas de choix proposé
                        self.score += 1
                    self.score += 1
            else:
                self.score -= 1
                self.erreurs += 1
        if all(obj.correct for obj in self.feuille_actuelle.objets.lister(type=Champ)):
            self.score += 10*(self.niveau + 1)
        self.update_panneau()
