# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

##-------------------------------------------#######
#                   Statistiques                   #
##-------------------------------------------#######
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
from math import isnan, sqrt, ceil, floor

from PyQt4.QtGui import QVBoxLayout, QLabel, QGroupBox, QHBoxLayout, QComboBox

from numpy import array

from ...GUI.menu import MenuBar
from ...GUI.panel import Panel_API_graphique
from .experience import LancerDes, Sondage, ExperienceFrame, DIC
from .onglets_internes import OngletsStatistiques
from ...geolib.routines import nice_display, arrondir_1_2_5 as arrondir
from ...pylib import property2, uu, regsub, advanced_split, print_error, eval_restricted
from ... import param

__doc__ = u"""
Module Statistiques:
Calculs de moyenne, variance, quantiles sur des séries de données avec modèle
 linéaire si besoin.
"""


def catch_errors(function):
    def new_function(*args, **kw):
        try:
            result = function(*args, **kw)
            if isinstance(result, float) and isnan(result):
                result = "Calcul impossible."
        except Exception:
            #~ if param.debug:
                #~ print_error()
            result = "Calcul impossible."
        return result
    return new_function


class Classe(tuple):
    u"""Un intervalle de type [a;b[.

    Pour les calculs, les classes sont approximées par leur centre de classe.
    """
    def milieu(self):
        return float(sum(self))/len(self)

    def __str__(self):         return "[%s ; %s[" % (self[0], self[-1])
    def __repr__(self):        return str(self)
    def __unicode__(self):     return uu(str(self))
    def __int__(self):         return int(self.milieu())
    def __add__(self, y):      return self.milieu() + y
    def __mul__(self, y):      return self.milieu()*y
    def __div__(self, y):      return self.milieu()/y
    def __rdiv__(self, y):     return y/self.milieu()
    def __truediv__(self, y):  return self.__div__(y)
    def __rtruediv__(self, y): return self.__rdiv__(y)
    def __neg__(self):         return -self.milieu()
    def __sub__(self, y):      return self.milieu() - y
    def __rsub__(self, y):     return y - self.milieu()
    def __pow__(self, y):      return self.milieu()**y
    def __rpow__(self, y):     return y**self.milieu()
    def __abs__(self):         return abs(self.milieu())
    def __eq__(self, y):       return self.milieu() == y
    def __ne__(self, y):       return self.milieu() != y
    def __gt__(self, y):       return self.milieu() > y
    def __ge__(self, y):       return self.milieu() >= y
    def __lt__(self, y):       return self.milieu() < y
    def __le__(self, y):       return self.milieu() <= y
    def __nonzero__(self):     return self.milieu() != 0


    def amplitude(self):
        return self[1] - self[0]

    __radd__ = __add__; __rmul__ = __mul__
    __float__ = milieu



class StatMenuBar(MenuBar):
    def __init__(self, panel):
        MenuBar.__init__(self, panel)

        self.ajouter("Fichier", ["nouveau"], ["ouvrir"], ["ouvrir ici"], None,
                    ["enregistrer"], ["enregistrer_sous"], ["exporter"], None,
                    ['session'], None,
                    ["imprimer"], [u"presse-papier"], None, ["proprietes"], None,
                    self.panel.doc_ouverts, None, ["fermer"], ["quitter"])
        self.ajouter("Editer", ["annuler"], ["refaire"], ["modifier"], ["supprimer"])
        self.ajouter("creer")
        self.ajouter("Affichage", ["onglet"], ["plein_ecran"], None, ["barre_outils"],
                     ["console_geolib"], None, ["zoom_texte"], ["zoom_ligne"],
                     ["zoom_general"])
        self.ajouter("Outils", [u"Expérience", u"Simuler une expérience.",
                                "Alt+Ctrl+E", self.panel.creer_experience],
                [u"Lancers de dés", u"Simuler des lancers d'un ou de plusieurs dés.",
                 "Ctrl+Shift+D", self.panel.creer_lancer_des],
                [u"Sondage", u"Simuler un sondage simple.", "Ctrl+Shift+S",
                 self.panel.creer_sondage], None, ["options"])
        self.ajouter(u"avance1")
        self.ajouter("?")




class Statistiques(Panel_API_graphique):

    titre = u"Statistiques" # Donner un titre a chaque module

    types_diagrammes = ('barres', 'batons', 'histogramme', 'cumul_croissant',
                        'cumul_decroissant', 'bandes', 'circulaire',
                        'semi-circulaire', 'boite')
    noms_diagrammes = [u"diagramme en barres", u"diagramme en batons",
                       u"histogramme", u"effectifs cumulés croissants",
                       u"effectifs cumulés décroissants", u"diagramme en bandes",
                       u"diagramme circulaire", u"diagramme semi-circulaire",
                       u"diagramme en boite"]
    _graph = None

    def __init__(self, *args, **kw):
        Panel_API_graphique.__init__(self, *args, **kw)

        self.couleurs = "bgrmcy"
        self.hachures = ('/', '*', 'o', '\\', '//', 'xx', '.', 'x', 'O', '..', '\\\\\\')

        self._donnees = []
        self._classes = []
        # Numéro de la série actuellement sélectionnée
        self.index_serie = 0
        self.legende_x = '' # axe des abscisses
        self.legende_y = '' # axe des ordonnees
        self.legende_a = '' # unite d'aire (histogramme)
        self.gradu_x = ''
        self.gradu_y = ''
        self.gradu_a = ''
        self.origine_x = ''
        self.origine_y = ''
        self.intervalle_fluctuation = None

        self.entrees = QVBoxLayout()

        self.entrees.addStretch()

        self.entrees.addWidget(QLabel(u" Mode graphique :"))

        self.choix = QComboBox()
        self.choix.addItems(self.noms_diagrammes)
        self.graph = 'barres' # *APRES* que self.choix soit défini.

        self.choix.currentIndexChanged.connect(self.EvtChoice)
        self.entrees.addWidget(self.choix)

        self.entrees.addStretch()

        #self.entrees.Add(wx.StaticText(self, -1, ""))

        box = QGroupBox(u"Mesures")
        bsizer = QVBoxLayout()
        box.setLayout(bsizer)

        #self.entrees.Add(bsizer, 1, wx.EXPAND|wx.ALL, 5)
        self.entrees.addWidget(box)
        self.entrees.addStretch()

        self._effectif_total = QLabel()
        self._moyenne = QLabel()
        self._decile1 = QLabel()
        self._quartile1 = QLabel()
        self._mediane = QLabel()
        self._quartile3 = QLabel()
        self._decile9 = QLabel()
        self._interquartile = QLabel()
        self._mode = QLabel()
        self._etendue = QLabel()
        self._variance = QLabel()
        self._ecart_type = QLabel()
        self._ecart_type.setMinimumWidth(100)

        bsizer.addWidget(self._effectif_total)
        bsizer.addWidget(QLabel(u"<b>Tendance centrale</b>"))
        bsizer.addWidget(self._moyenne)
        bsizer.addWidget(self._mediane)
        bsizer.addWidget(self._mode)
        bsizer.addWidget(QLabel(u"<b>Dispersion</b>"))
        bsizer.addWidget(self._decile1)
        bsizer.addWidget(self._quartile1)
        bsizer.addWidget(self._quartile3)
        bsizer.addWidget(self._decile9)
        bsizer.addWidget(self._interquartile)
        bsizer.addWidget(self._etendue)
        bsizer.addWidget(self._variance)
        bsizer.addWidget(self._ecart_type)
        # Initialise le contenu des différents labels.
        self.calculer()

        haut = QHBoxLayout()
        haut.addWidget(self.canvas, 1)
        haut.addLayout(self.entrees)

        self.onglets_bas = OngletsStatistiques(self)

        self.sizer = QVBoxLayout()
        self.sizer.addLayout(haut, 1)
        self.sizer.addWidget(self.onglets_bas, 0)
        self.finaliser(contenu = self.sizer)


        #################
        #  Debugage
        #################
        #~ self.donnees_valeurs = '55 67 68 72 72 72.5 74 75.5 78 78.5 79 81.5 86 91 94.5'
        #~ self.donnees_classes = '[40;60[ [60;70[ [70;75[ [75;90[ [90;120['
        #~ self.legende_x  = "calibre des bananes (g)"
        #~ self.legende_y = "nombre de bananes"
        #~ self.legende_a = "bananes"
        #~ self.actualiser()
        #################

    @property2
    def graph(self, val=None):
        if val is not None:
            assert val in self.types_diagrammes, "Type de diagramme incorrect."
            self._graph = val
            self.choix.setCurrentIndex(self.types_diagrammes.index(self._graph))
        return self._graph


    def EvtChoice(self, index):
        self._graph = self.types_diagrammes[index]
        self.actualiser()


    def EvtCheck(self, state):
        self.param('hachures', self.onglets_bas.tab_reglages.hachures.isChecked())
        self.param('mode_effectifs', self.onglets_bas.tab_reglages.mode.currentIndex())
        self.param('reglage_auto_fenetre', self.onglets_bas.tab_reglages.auto.isChecked())
        self.actualiser()

    def _recuperer_classes(self):
        u"Récupère la liste des classes depuis le champ de texte correspondant."
        self._classes = []
        classes = self.onglets_bas.tab_donnees.classes.text()
        if param.separateur_decimal == ',':
            classes = classes.replace(',', '.')
        classes = classes.replace(";", ",")

        if not classes.strip():
            return

        for serie in advanced_split(classes, "|", symbols = "({})"):
            self._classes.append([])
            for classe in advanced_split(serie, " ", symbols = "({})"):
                if classe.endswith("["):
                    classe = classe[:-1] + "]"
                self.ajouter_classes(Classe(eval_restricted(classe)), serie=-1)


    def _recuperer_valeurs(self):
        u"Récupère le dictionnaire des valeurs et des effectifs associés depuis le champ de texte correspondant."
        # On peut saisir plusieurs séries (pour les comparer).
        # self._donnees est une liste de dictionnaire de valeurs (un par série).
        self._donnees = []
        valeurs = self.onglets_bas.tab_donnees.valeurs.text()
        # La chaine va être découpée au niveau des espaces.
        # On commence par la préparer : on supprime les espaces inutiles, et en
        # particulier les espaces autour des '*'.
        valeurs = regsub("[ ]*[*][ ]*", valeurs, "*")
        valeurs = regsub("[ ]*[|][ ]*", valeurs, "|")
        # une expression du style "[i for i in range(7)]" ne doit pas être découpée au niveau des espaces.
        valeurs = regsub("[[][^]]*for[^]]*in[^]]*[]]", valeurs, lambda s:s.replace(' ','<@>'))

        if param.separateur_decimal == ',':
            valeurs = valeurs.replace(',', '.')
        valeurs = valeurs.replace(";", ",")

        if not valeurs.strip():
            return

        # Les séries sont séparées par le symbole |.
        for serie in advanced_split(valeurs, "|", symbols = "({})"):
            self._donnees.append({})
            for val in advanced_split(serie, " ", symbols = "({})"):
                if val.endswith("["):
                    val = val[:-1] + "]"

                if re.match("[[][^]]*for[^]]*in[^]]*[]]", val):
                    val = eval_restricted(val.replace('<@>',' '))
                    for v in val:
                        if type(v) in (list, tuple):
                            _effectif, _valeur = v
                            # syntaxe style "[(3,i) for i in range(7)]" où 3 est l'effectif
                            self.ajouter_valeur(_valeur, _effectif, serie=-1)
                        else:
                            # syntaxe style "[i for i in range(7)]"
                            self.ajouter_valeur(v, serie=-1)
                else:
                    val = [eval_restricted(x) for x in advanced_split(val, "*")]
                    val.reverse()
                    self.ajouter_valeur(*val, serie=-1)


    def actualiser(self, afficher = True):
        try:
            onglets = self.onglets_bas
            self.legende_x = onglets.tab_legende.x.text()
            self.legende_y = onglets.tab_legende.y.text()
            self.legende_a = onglets.tab_legende.a.text()
            self.gradu_x = onglets.tab_graduation.x.text()
            self.gradu_y = onglets.tab_graduation.y.text()
            self.gradu_a = onglets.tab_graduation.a.text()
            self.origine_x = onglets.tab_graduation.origine_x.text()
            self.origine_y = onglets.tab_graduation.origine_y.text()


            # test choix quantiles
            self.param("quantiles")["mediane"][0] = onglets.tab_quantiles.mediane.isChecked()
            self.param("quantiles")["quartiles"][0] = onglets.tab_quantiles.quartiles.isChecked()
            self.param("quantiles")["deciles"][0] = onglets.tab_quantiles.deciles.isChecked()

            # On récupère la liste des classes et les données de la série statistique.
            self._recuperer_classes()
            self._recuperer_valeurs()

            self.calculer()
            if afficher:
                self.affiche()
            self.canvas.message(u"Graphique fini.")

        except:
            self.canvas.message(u"Impossible de construire le graphique.")
            print_error()


    def calculer(self):
        e = self.effectif_total()
        if isinstance(e, float) and e == int(e):
            e = int(e)
        self._effectif_total.setText(u"<i>Effectif total: %s</i>" % e)
        self._moyenne.setText(u"Moyenne: %s" % self.moyenne())
        self._mediane.setText(u"Médiane: %s" % self.mediane())
        self._mode.setText(u"Mode: %s" % self.mode())
        self._decile1.setText(u"D<sub>1</sub>: %s" % self.tile(10, 1))
        Q1 = self.quartile(1)
        self._quartile1.setText(u"Q<sub>1</sub>: %s" % Q1)
        Q3 = self.quartile(3)
        self._quartile3.setText(u"Q<sub>3</sub>: %s" % Q3)
        self._decile9.setText(u"D<sub>9</sub>: %s" % self.tile(10, 9))
        ecart = ('Calcul impossible.' if isinstance(Q1, basestring) else Q3 - Q1)
        self._interquartile.setText(u"Q<sub>3</sub> - Q<sub>1</sub>: %s" % ecart)
        self._etendue.setText(u"Étendue: %s" % self.etendue())
        self._variance.setText(u"Variance: %s" % self.variance())
        self._ecart_type.setText(u"Écart-type: %s" % self.ecart_type())

    def ajouter_classes(self, *classes, **kw):
        if not self._classes:
            self._classes.append([])
        serie = kw.get('serie', 0)
        self._classes[serie] += classes
        self._classes.sort()

    def ajouter_valeurs(self, *valeurs, **kw):
        serie = kw.get('serie', 0)
        for val in valeurs:
            self.ajouter_valeur(val, serie=serie)


    def ajouter_valeur(self, valeur, effectif = 1, serie=0):
        if not self._donnees:
            self._donnees.append({})
        if type(valeur) in (list, tuple):
            valeur = Classe(valeur)
        donnees = self._donnees[serie]
        donnees[valeur] = donnees.get(valeur, 0) + effectif

    # TODO: renommer classes en classes_serie
    @property
    def classes(self):
        u"Les classes de la série courante."
        index = self.index_serie
        if not self._classes or len(self._classes) < index:
            if self._donnees:
                # Par défaut, si toutes les valeurs entrées sont des classes,
                # le découpage en classes suit les classes entrées.
                donnees = self._donnees[index].keys()
                if all(isinstance(x, Classe) for x in donnees):
                    return donnees
            return None
        return self._classes[index]

    # TODO: renommer donnees en donnees_serie
    @property
    def donnees(self):
        u"Les données de la série courante."
        if not self._donnees:
            return None
        mode = self.param('mode_effectifs')
        donnees = self._donnees[self.index_serie]
        # mode = 0: valeurs
        # mode = 1: fréquences
        # mode = 2: pourcentages
        if mode:
            k = (100 if mode == 1 else 1)
            donnees = donnees.copy()
            total = sum(donnees.itervalues())
            for val in donnees:
                donnees[val] *= k/total
        return donnees

    @property
    def donnees_brutes(self):
        if not self._donnees:
            return None
        return self._donnees[self.index_serie]



    def intervalle_classes(self):
        return min([classe[0] for classe in self.classes]), max([classe[1] for classe in self.classes])

    def effectif_classe(self, classe):
        a, b = classe
        return sum(effectif for valeur, effectif in self.donnees.iteritems() if a <= valeur < b)

    def densite_classe(self, classe):
        return self.effectif_classe(classe)/classe.amplitude()


    def experience(self, formule, n, val_possibles = ()):
        u"""Réalise 'n' fois l'expérience décrite par 'formule'.
        Exemple: self.experience('int(6*rand())+1', 100) simule 100 lancers de dés."""

        self.actualiser(False)
        self.ajouter_valeurs(*[eval(formule, DIC) for i in xrange(n)])
        for val in val_possibles:
            self.ajouter_valeur(val, 0)
        self.calculer()
        self.affiche()



    def graduations(self, x, y):
        if x and self.gradu_x.strip():
            x = float(self.gradu_x)
        if y and self.gradu_y.strip():
            y = float(self.gradu_y)
        self.canvas.gradu = (x, y)


    def origine(self, x, y):
        if self.origine_x.strip():
            x = float(self.origine_x)
        if self.origine_y.strip():
            y = float(self.origine_y)
        self.canvas.origine_axes = (x, y)

    def fenetre(self, *args):
        if self.param('reglage_auto_fenetre'):
            self.canvas.fenetre = args



    def axes(self, x=False, y=False, a=False, classes=False, legende_x=False):

        self.onglets_bas.enable(x, y, a, classes, legende_x)
        vide = self.effectif_total() == 0 or (classes and not self.classes)
        if vide:
            x = y = a = 0
        self.canvas.afficher_axes = True
        self.canvas.utiliser_repere = False
        liste_axes = []
        if x:
            liste_axes.append(0)
        if y:
            liste_axes.append(1)

        n = len(liste_axes)
        if n < 2:
            self.canvas.afficher_quadrillage = False
            if n < 1:
                self.canvas.afficher_axes = False
        self.canvas.liste_axes = tuple(liste_axes)
        return vide


    def _affiche(self):
        # ('barres', 'batons', 'histogramme', 'cumul_croissant', 'cumul_decroissant', 'bandes', 'circulaire', 'semi-circulaire', 'boite')
        if self.donnees is None:
            self.afficher_message('Rentrez des données.')
            return
        msg = ''
        if self.graph == 'barres':
            msg = self.diagramme_barre()
        elif self.graph == 'bandes':
            msg = self.diagramme_bande()
        elif self.graph == 'batons':
            msg = self.diagramme_baton(2)
        elif self.graph == 'circulaire':
            msg = self.diagramme_circulaire()
        elif self.graph == 'semi-circulaire':
            msg = self.diagramme_circulaire(180)
        elif self.graph == 'boite':
            msg = self.diagramme_boite(True)

        # Graphiques utilisant les classes :
        elif self.graph == 'histogramme':
            msg = self.histogramme()
        elif self.graph == 'cumul_croissant':
            msg = self.courbe_effectifs()
        elif self.graph == 'cumul_decroissant':
            msg = self.courbe_effectifs(-1)
        if msg:
            self.afficher_message(msg)


    def creer_experience(self, event = None):
        win = ExperienceFrame(self)
        win.show()

    def creer_lancer_des(self, event = None):
        win = LancerDes(self)
        win.show()


    def creer_sondage(self, event = None):
        win = Sondage(self)
        win.show()




    def dessiner_intervalle_fluctuation(self):
        n = self.intervalle_fluctuation
        if n is None:
            return
        m = self.moyenne(); f = m/100.
        e = 200*sqrt(f*(1-f)/n)
        x0 = m - e; x1 = m + e
        y0 = self.canvas.fenetre[2] + 4*self.canvas.coeff(1)
        y1 = self.canvas.fenetre[3] - 6*self.canvas.coeff(1)
        if self.param('hachures'):
            self.canvas.dessiner_polygone([x0, x0, x1, x1], [y0, y1, y1, y0], facecolor='w', edgecolor='k',alpha = .3, hatch = '/')
            self.canvas.dessiner_ligne([x0, x0, x1, x1, x0], [y0, y1, y1, y0, y0], 'k', alpha = 1)
        else:
            self.canvas.dessiner_polygone([x0, x0, x1, x1], [y0, y1, y1, y0], facecolor='y', edgecolor='y',alpha = .3)
            self.canvas.dessiner_ligne([x0, x0, x1, x1, x0], [y0, y1, y1, y0, y0], 'y', alpha = 1)


    def afficher_message(self, msg):
        u"Affichage un message précisant pourquoi le graphique ne s'affiche pas."
        self.axes(x=False, y=False, classes=None)
        self.canvas.dessiner_texte(0, 0, msg, va='center', ha='center', size=16)
        self.fenetre(-1, 1, -1, 1)

#------------------------------------
#   Differents types de diagrammes.
#------------------------------------



    def histogramme(self):
        u"Construit un histogramme (à ne pas confondre avec le diagramme en barres !)"

        if self.axes(x=True, a=True, classes=True):
            return u"Définissez des classes.\nExemple : [0;10[ [10;20["

        m, M = self.intervalle_classes()
        l = min([classe[1] - classe[0] for classe in self.classes])
        hmax = max([self.densite_classe(classe) for classe in self.classes])

        if hmax == 0:
            return u"Les classes choisies ne contiennent aucune valeur."

        # Réglage de la fenêtre d'affichage
        self.fenetre(m - 0.1*(M-m), M + 0.4*(M-m), -0.1*hmax, 1.1*hmax)
        self.origine(m, 0)
        self.graduations(l, 0)

        i = 0
        for classe in sorted(self.classes):
            h = self.densite_classe(classe)
            xx = [classe[0], classe[0], classe[1], classe[1]]
            yy = [0, h, h, 0]
            if self.param('hachures'):
                self.canvas.dessiner_polygone(xx, yy, 'w', hatch = self.hachures[i%len(self.hachures)])
            else:
                self.canvas.dessiner_polygone(xx, yy, self.couleurs[i%len(self.couleurs)])
            i += 1

        self.canvas.dessiner_texte(M + 0.3*(M-m)-5*self.canvas.coeff(0),
                        -18*self.canvas.coeff(1), self.legende_x, ha = "right")

        if 'x' in self.gradu_a:
            lu, hu_ = (float(c) for c in self.gradu_a.split('x'))
            effectif = lu*hu_
            lu *= l
            hu = effectif/lu
        elif '*' in self.gradu_a:
            lu, hu = (float(c) for c in self.gradu_a.split('*'))
            effectif = lu*hu
            lu *= l
            hu = effectif/lu
        else:
            # l'effectif que represente le carre
            effectif = (float(self.gradu_a) if self.gradu_a else arrondir(self.total()/20))
            # cote du carre en pixels
            cote = sqrt(effectif/(self.canvas.coeff(0)*self.canvas.coeff(1)))
            lu = cote*self.canvas.coeff(0)
            hu = cote*self.canvas.coeff(1)

        x = M + 0.1*(M-m)
        col = '0.85' if self.param('hachures') else 'b'
        self.canvas.dessiner_polygone([x, x + lu, x + lu, x, x],
                    [.5*hmax, .5*hmax, .5*hmax + hu, .5*hmax + hu, .5*hmax], col)

        legende = nice_display(effectif) + " " + (self.legende_a or u"unité")

        if effectif > 1 and not self.legende_a:
            legende += "s"

        self.canvas.dessiner_texte(x, .5*hmax - 15*self.canvas.coeff(1), legende, va = "top")


    def courbe_effectifs(self, mode=1):
        u"""
        Courbe des effectifs cumulés croissants si mode = 1, décroissants si mode = -1.
        """
        if self.axes(x=True, y=True, classes=True):
            return u"Définissez des classes.\nExemple : [0;10[ [10;20["

        donnees_triees = sorted(self.donnees.iteritems())

        l = min([classe[1] - classe[0] for classe in self.classes])
        m, M = self.intervalle_classes()
        hmax = self.total()
        self.fenetre(m - 0.1*(M - m), M + 0.2*(M - m), -0.1*hmax, 1.1*hmax)
        self.graduations(l, arrondir(hmax/10))
        self.origine(m, 0)

        # Classe with cumulatives eff or freq 2-uple list: y_cum
        y_cum = []
        couleur = 'k' if self.param('hachures') else 'b'
        for classe in self.classes:
            if mode == 1:
                y_value = [sum([effectif for valeur, effectif in donnees_triees
                            if valeur < classe[i]]) for i in (0, 1)]
            else:
                y_value = [sum([effectif for valeur, effectif in donnees_triees
                            if valeur >= classe[i]]) for i in (0, 1)]
            self.canvas.dessiner_ligne(classe, y_value, color = couleur)
            y_cum.append((classe, y_value))
        dx, dy = self.canvas.dpix2coo(-5, 18)
        self.canvas.dessiner_texte(M + 0.2*(M - m) + dx, -dy, self.legende_x, ha = "right")
        dx, dy = self.canvas.dpix2coo(15, -5)
        # Ajout des quantiles
        for q in ["mediane", "quartiles", "deciles"]:
            # tracer si les quantiles sont activés
            if self.param("quantiles")[q][0]:
                freq = self.param("quantiles")[q][1]
                for a in freq:
                    try:
                        (c, y) = self.select_classe(y_cum, a, mode)
                        self.quantile_plot(c, y, a, couleur=self.param("quantiles")[q][2],
                                style=self.param("quantiles")[q][3])
                    except TypeError:
                        # c peut être vide si les classes commencent à une
                        # fcc trop grande.
                        pass
        # Legende
        legende_y = self.legende_y
        if not legende_y:
            mode = self.param('mode_effectifs')
            if mode == 0:
                legende_y = u"Effectifs cumulés"
            elif mode == 1:
                legende_y = u"Pourcentages cumulés"
            else:
                legende_y = u"Fréquences cumulées"
        self.canvas.dessiner_texte(m + dx, 1.1*hmax - dy, legende_y, va='top')


    def quantile_plot(self, classe, y, a, couleur='r', style='-'):
        u"""
        Trace le a-quantile

        @type classe: classe
        @param classe: la classe dans laquelle tombe le a-quantile.
        @type y: list
        @param y: bornes des eff ou freq cumulés de classe.
        @type couleur: char
        @param couleur: couleur du tracé, rouge par défaut
        @type style: char
        @param style: style de ligne réglé en cas de N&B

        @rtype: None
        """
        a_reel = a*self.total()
        m = (y[1] - y[0])/(classe[1] - classe[0])
        x_reg = (a_reel - y[0])/m + classe[0]
        # coordonnées de l'origine
        x0, y0 = self.canvas.origine_axes
        dx, dy = self.canvas.dpix2coo(-5, 18)
        # tenir compte du mode N&B
        col = 'k' if self.param('hachures') else couleur

        self.canvas.dessiner_ligne([x0, x_reg], [a_reel, a_reel], color = col, linestyle = style)
        self.canvas.dessiner_ligne([x_reg, x_reg], [a_reel, y0], color = col, linestyle = style)
        self.canvas.dessiner_texte(x_reg, y0 + dy, format(x_reg, ".4g"), color = col)


    def select_classe(self, liste, a, mode=1):
        u"""
        selectionne la classe contenant le a-quantile

        @type a: real

        @param a: le paramètre dans [0.1[. Ne pas mettre a=1.0 pour éviter un
        dépassement
        @type liste: list of 2-uple classe, list
        @param liste: contient les classes couplées à leurs effectifs cumulés.
        @type mode: int
        @param mode: 1 or -1 for increasing or decreasing cumulative eff/freq

        @rtype: 2-uple
        renvoie un 2-uple:  classe, [y_0, y_1] ou **None** si la recherche échoue.
        """
        eff_total = self.total()
        if mode == 1:
            # chosen_s = [(c,v) for (c,v) in liste if \
            # v[0]/eff_total <= a < v[1]/eff_total]
            for (c, v) in liste:
                if v[0]/eff_total <= a < v[1]/eff_total:
                    return (c, v)
        elif mode == -1:
            # chosen_s = [(c,v) for (c,v) in liste if v[1]/eff_total \
            # <= a < v[0]/eff_total]
            for (c, v) in liste:
                if v[1]/eff_total <= a < v[0]/eff_total:
                    return (c, v)

    def diagramme_barre(self, ratio=.7):
        u"""Diagramme en barres.

        Essentiellement pertinent pour des séries qualitatives.

        `ratio` est un nombre décimal entre 0 et 1.
        Il mesure le quotient (largeur d'une barre)/(largeur maximale possible).
        """

        if self.axes(y=True, legende_x=True):
            return

        donnees_triees = sorted(self.donnees.iteritems())

        lmax = 100./len(donnees_triees)
        l = ratio*lmax
        e = .5*(lmax - l)
        hmax = max(self.donnees.values())
        self.fenetre(-10, 110, -.15*hmax, 1.15*hmax)
        self.canvas.dessiner_ligne((0, 110), (0, 0), 'k')

        self.graduations(0, arrondir(hmax/10))
        self.origine(0, 0)

        n = 0
        for valeur, effectif in donnees_triees:
            x0, x1 = (2*n + 1)*e + n*l, (2*n + 1)*e + (n+1)*l
            xx = [x0, x0, x1, x1]
            yy = [0, effectif, effectif, 0]
            if self.param('hachures'):
                self.canvas.dessiner_polygone(xx, yy, 'w', hatch=self.hachures[(n - 1)%len(self.hachures)])
            else:
                self.canvas.dessiner_polygone(xx, yy, self.couleurs[(n - 1)%len(self.couleurs)])
            self.canvas.dessiner_texte((x0 + x1)/2., - 18*self.canvas.coeff(1), str(valeur), ha='center')
            n += 1

        self.canvas.dessiner_texte(110 - 5*self.canvas.coeff(0), -35*self.canvas.coeff(1), self.legende_x, ha='right')
        legende_y = self.legende_y
        if not legende_y:
            mode = self.param('mode_effectifs')
            if mode == 0:
                legende_y = u"Effectifs"
            elif mode == 1:
                legende_y = u"Pourcentages"
            else:
                legende_y = u"Fréquences"
        self.canvas.dessiner_texte(15*self.canvas.coeff(0), 1.15*hmax - 5*self.canvas.coeff(1), legende_y, va = "top")

        # les donnees sont affichees entre 0 et 100 en abscisse



    def diagramme_baton(self, largeur=1):
        u"""Diagramme en batons (séries quantitatives discrètes).

        `largeur` est la demi-largeur d'un bâton, en pixels."""

        if not all(hasattr(val, '__float__') for val in self.donnees):
            return u"La série doit être à valeurs numériques."

        if self.axes(x=True, y=True):
            return

        m, M = min(self.donnees), max(self.donnees)
        if m == M:
            l = 1
            M += 1
            m -= 1
        else:
            l = arrondir((M - m)/20)   # on evite d'avoir des valeurs trop fantaisistes pour le pas !
            m = l*int(m/l) - l


        hmax = max(self.donnees.values())

        # reglage de la fenetre d'affichage
        self.fenetre(m - 0.1*(M-m), M + 0.1*(M-m), -0.1*hmax, 1.1*hmax)
        if int(m) == m:
            m = int(m) # pour des raisons esthetiques

        self.origine(m, 0)
        self.graduations(l, arrondir(hmax/10))

        e = largeur*self.canvas.coeff(0)

        i = 0
        for val, eff in self.donnees.iteritems():
            couleur = 'k' if self.param('hachures') else self.couleurs[(i - 1)%len(self.couleurs)]
            self.canvas.dessiner_polygone([val - e, val - e, val + e, val + e], [0, eff, eff, 0], couleur)
            i+=1


        self.canvas.dessiner_texte(M + 0.1*(M - m) - 5*self.canvas.coeff(0),
                                    -18*self.canvas.coeff(1),
                                    self.legende_x, ha = "right")
        legende_y = self.legende_y
        if not legende_y:
            mode = self.param('mode_effectifs')
            if mode == 0:
                legende_y = u"Effectifs"
            elif mode == 1:
                legende_y = u"Pourcentages"
            else:
                legende_y = u"Fréquences"
        self.canvas.dessiner_texte(m + 15*self.canvas.coeff(0), 1.1*hmax - 5*self.canvas.coeff(1),
                                    legende_y, va = "top")

        self.dessiner_intervalle_fluctuation()


    def diagramme_bande(self):
        u"""Diagramme en bande."""

        if self.axes():
            return

        l_unite = 100./self.total()
        n = 0
        x = 0

        self.fenetre(-10, 110, -1, 2)
        self.graduations(0, 0)


        for valeur, effectif in sorted(self.donnees.iteritems()):
            l = effectif*l_unite
            if self.param('hachures'):
                self.canvas.dessiner_polygone([x, x, x + l, x + l, x], [0, 1, 1, 0, 0],
                        'w', hatch = self.hachures[(n - 1)%len(self.hachures)])
            else:
                self.canvas.dessiner_polygone([x, x, x + l, x + l, x], [0, 1, 1, 0, 0],
                        self.couleurs[(n - 1)%len(self.couleurs)])
            self.canvas.dessiner_texte(x+l/2., - 18*self.canvas.coeff(1),
                    str(valeur),  ha="center")
            n += 1
            x += l



    def diagramme_circulaire(self, angle = 360):
        if self.axes():
            return

        valeurs, effectifs = zip(*self.donnees.items())

        # petit raffinement pour eviter que 2 couleurs identiques se suivent
        n = len(effectifs)
        l = len(self.couleurs)
        if n%l == 1:
            couleurs =  tuple(((n-1)//l)*self.couleurs + self.couleurs[1])
        else:
            couleurs = tuple(self.couleurs)

        effectifs = angle/360.*array(effectifs)/sum(effectifs)
        labels = [str(valeur) for valeur in valeurs]
        patches, texts = self.canvas.axes.pie(effectifs, labels=labels, labeldistance=1.16,
                                              shadow=False, colors=couleurs)
        if self.param('hachures'):
            for i, patch in enumerate(patches):
                patch.set_fc('w')
                patch.set_hatch(self.hachures[i%len(self.hachures)])
        self.canvas.synchroniser_fenetre() # pour profiter du reglage effectue par matplotlib
        self.canvas.orthonormer() # pour avoir un vrai cercle
        # rafraichir produirait une recursion infinie !


    def diagramme_boite(self, afficher_extrema = True):
        try:
            xmin = float('+inf')
            xmax = float('-inf')
            for i in range(len(self._donnees)):
                self.index_serie = i
                m = self.minimum()
                if isinstance(m, Classe):
                    m = m[0]
                M = self.maximum()
                if isinstance(M, Classe):
                    M = M[1]
                xmin = min(xmin, m)
                xmax = max(xmax, M)
            for i in range(len(self._donnees)):
                self.index_serie = i
                self._diagramme_boite(xmin, xmax, afficher_extrema)
        finally:
            self.index_serie = 0

    def _diagramme_boite(self, xmin, xmax, afficher_extrema=True):
        u"Appelé aussi diagramme à moustache."

        if not all(hasattr(val, '__float__') for val in self.donnees):
            return u"La série doit être à valeurs numériques."

        if self.axes(x=True):
            return

        med = self.mediane()
        q1 = self.quartile(1)
        q3 = self.quartile(3)
        d1 = self.decile(1)
        d9 = self.decile(9)
        m = self.minimum()
        if isinstance(m, Classe):
            m = m[0]
        M = self.maximum()
        if isinstance(M, Classe):
            M = M[1]
        if str in [type(i) for i in (med, q1, q3, d1, d9)]:
            # self.mediane() ou self.decile() ou... renvoie "calcul impossible."
            return

        largeur = xmax - xmin

        l = arrondir(largeur/20)
        self.graduations(l, 0)
        origine = floor(xmin/(2*l))*2*l
        if origine <= xmin - 0.05*largeur:
            origine = ceil(xmin/(2*l))*2*l
        if int(origine) == origine:
            origine = int(origine) # pour des raisons esthetiques
        self.origine(origine, 0)
        N = len(self._donnees)
        if xmin != xmax:
            self.fenetre(xmin - 0.1*largeur, xmax + 0.1*largeur, -0.1*N, N + .1)
        else:
            self.fenetre(xmin - 0.1, xmax + 0.1, -0.1, 1.1)

        def col(val):
            return 'k' if self.param('hachures') else val

        w = 1 if self.param('hachures') else 1.5

        i = self.index_serie

        # Quartiles
        self.canvas.dessiner_ligne([q1, q1], [.2 + i, .8 + i], linewidth = w, color = col('b'))
        self.canvas.dessiner_ligne([q3, q3], [.2 + i, .8 + i], linewidth = w, color = col('b'))
        # Médiane
        if self.param("quantiles")['mediane'][0]:
            # Si la médiane est confondue avec les quartiles, on la trace un peu plus large.
            med_width = (w if med not in [q1, q3] else 2)
            self.canvas.dessiner_ligne([med, med], [.2 + i, .8 + i], linewidth= med_width, color = col('r'))
        # "Moustaches"
        if self.param("quantiles")['deciles'][0]:
            # Les "moustaches" du diagramme correspondent au 1er et 9e décile
            self.canvas.dessiner_ligne([m, M], [.5 + i, .5 + i], linestyle="None", marker="o", color="k", markerfacecolor="w")
            self.canvas.dessiner_ligne([d1, q1], [.5 + i, .5 + i], color="k")
            self.canvas.dessiner_ligne([q3, d9], [.5 + i, .5 + i], color="k")
            self.canvas.dessiner_ligne([d1, d1], [.4 + i, .6 + i], linewidth=w, color=col('g'))
            self.canvas.dessiner_ligne([d9, d9], [.4 + i, .6 + i], linewidth=w, color=col('g'))
        else:
            # Les "moustaches" du diagramme correspondent au minimum et maximum
            self.canvas.dessiner_ligne([m, q1], [.5 + i, .5 + i], color="k")
            self.canvas.dessiner_ligne([q3, M], [.5 + i, .5 + i], color="k")
            self.canvas.dessiner_ligne([m, m], [.4 + i, .6 + i], linewidth=w, color='k')
            self.canvas.dessiner_ligne([M, M], [.4 + i, .6 + i], linewidth=w, color='k')
        # Boîte
        self.canvas.dessiner_ligne([q3, q1], [.2 + i, .2 + i], color="k")
        self.canvas.dessiner_ligne([q3, q1], [.8 + i, .8 + i], color="k")

        if i == 0:
            self.canvas.dessiner_texte(xmax + 0.1*largeur - 5*self.canvas.coeff(0),
                                    -18*self.canvas.coeff(1),
                                    self.legende_x, ha = "right")

#------------------------------------------------------------
#   Infos sur la serie.
#   (Mesures de tendance centrales, de dispersion, etc...)
#------------------------------------------------------------


    @catch_errors
    def effectif_total(self):
        # Effectifs bruts (non convertis en fréquences, quel que soit le mode).
        return sum(self.donnees_brutes.itervalues())

    def total(self):
        u"Retourne soit l'effectif total, soit 100, soit 1, selon les paramètres en cours."
        return sum(self.donnees.itervalues())

    @catch_errors
    def mode(self):
        m = max(self.donnees.values())
        v = [str(val) for val, effectif in self.donnees.iteritems() if effectif == m]
        if len(v) > 2:
            v = v[:2] + ["..."]
        return " ; ".join(v)

    @catch_errors
    def moyenne(self):
        u"""Moyenne de la série.

        Si les données de la série sont regroupées par classes, chaque classe
        est remplacée par son centre de classe, pour calculer une approximation
        de la moyenne.
        """
        return sum(eff*val for val, eff in self.donnees.items())/self.total()

    @catch_errors
    def minimum(self):
        return min(val for val, eff in self.donnees.items() if eff)

    @catch_errors
    def maximum(self):
        return max(val for val, eff in self.donnees.items() if eff)

    @catch_errors
    def etendue(self):
        return self.maximum() - self.minimum()

    @catch_errors
    def variance(self):
        moyenne_des_carres = sum(eff*val**2 for val, eff in self.donnees.items())/self.total()
        return moyenne_des_carres - self.moyenne()**2

    @catch_errors
    def ecart_type(self):
        return sqrt(self.variance())

    @catch_errors
    def mediane(self):
        u"""Correspond à la 'valeur du milieu' quand on ordonne les données.

        Précisement, la définition retenue ici est la suivante :
        * si l'effectif total est impair, la médiane est la valeur centrale ;
        * sinon (effectif total pair), la médiane est la demi-somme des deux
        valeurs centrales.

        Une bonne manière de visualiser la médiane pour des effectifs non entiers
        est de tracer un diagramme en bande."""
        somme = 0
        old_val = None
        objectif = self.effectif_total()/2
        for val, effectif in sorted(self.donnees_brutes.iteritems()):
            somme += effectif
            if somme > objectif:
                if isinstance(val, Classe):
                    # On estime la valeur de la médiane au sein de la classe,
                    # en l'assimilant au 2e quartile, et en estimant sa
                    # valeur au prorata de sa position dans la classe.
                    a, b = val
                    x = (somme - objectif)/effectif
                    return x*a + (1 - x)*b
                else:
                    if somme - effectif == objectif:
                        # la mediane est à cheval sur 2 valeurs
                        try:
                            return (old_val + val)/2
                        except TypeError:
                            print_error()
                            return u"Calcul impossible."
                return val
            old_val = val
        return u"Calcul impossible."

    @catch_errors
    def tile(self, k = 4, i = 1):
        u"""
        Renvoie la valeur x de la série telle que au moins i/k des données de la série
        soient inférieures ou égales à x.

        Exemple :   tile(4,1) -> premier quartile.
                    tile(10,2) -> deuxième décile.
        """

        somme = 0
        objectif = i/k*self.effectif_total()
        # objectif : position du quartile au sein de la série.
        for val, effectif in sorted(self.donnees_brutes.iteritems()):
            somme += effectif
            if somme >= objectif:
                if isinstance(val, Classe):
                    assert effectif
                    # On estime la valeur du quartile au sein de la classe,
                    # au prorata de la position du quartile dans la classe.
                    a, b = val
                    x = (somme - objectif)/effectif
                    return x*a + (1 - x)*b
                else:
                    return val


    def quartile(self, i = 1):
        u"""
        Donne Qi, le ième quartile.
        Qi est le plus petit element de la serie statistique tel qu'au moins
        i*25% des données soient inférieures ou égales à Qi.

        Note: si l'effectif de la série est pair,
        le 2ème quartile ne correspond pas toujours à la médiane."""

        return self.tile(4, i)


    def decile(self, i = 1):
        u"""
        Donne Di, le ième décile.
        Di est le plus petit element de la serie statistique tel qu'au moins
        i*10% des données soient inférieures ou égales à Di.

        Note: si l'effectif de la série est pair,
        le 5ème décile ne correspond pas toujours à la médiane."""

        return self.tile(10, i)



    def centile(self, i = 1):
        u"""
        Donne Ci, le ième centile.
        Ci est le plus petit element de la serie statistique tel qu'au moins
        i% des données soient inférieures ou égales à Ci.

        Note: si l'effectif de la série est pair,
        le 50ème centile ne correspond pas toujours à la médiane."""

        return self.tile(100, i)



    def _sauvegarder(self, fgeo, feuille = None):
        Panel_API_graphique._sauvegarder(self, fgeo, feuille)
        fgeo.contenu["Diagramme"] = [{
            "serie" : [{
            "valeurs" : [self.onglets_bas.tab_donnees.valeurs.text()],
            "classes" : [self.onglets_bas.tab_donnees.classes.text()]}],
            "legende" : [{"x" : [self.legende_x], "y" : [self.legende_y], "a" : [self.legende_a]}],
            "graduation": [{"x" : [self.gradu_x], "y" : [self.gradu_y], "a" : [self.gradu_a]}],
            "origine": [{"x" : [self.origine_x], "y": [self.origine_y]}],
            "mode_graphique" : [self.graph]
            }]


    def _ouvrir(self, fgeo):
        Panel_API_graphique._ouvrir(self, fgeo)
        if fgeo.contenu.has_key("Diagramme"):
            diagramme = fgeo.contenu["Diagramme"][0]
            serie = diagramme["serie"][0]
            valeurs = serie["valeurs"][0]
            classes = serie["classes"][0]
            legende = diagramme["legende"][0]
            legende_x = legende["x"][0]
            legende_y = legende["y"][0]
            legende_a = legende["a"][0]
            gradu = diagramme["graduation"][0]
            gradu_x = gradu['x'][0]
            gradu_y = gradu['y'][0]
            gradu_a = gradu['a'][0]
            origine = diagramme["origine"][0]
            origine_x = origine['x'][0]
            origine_y = origine['y'][0]
            mode_graphique = diagramme["mode_graphique"][0]

            self.onglets_bas.tab_legende.x.setText(legende_x)
            self.onglets_bas.tab_legende.y.setText(legende_y)
            self.onglets_bas.tab_legende.a.setText(legende_a)
            self.onglets_bas.tab_graduation.x.setText(gradu_x)
            self.onglets_bas.tab_graduation.y.setText(gradu_y)
            self.onglets_bas.tab_graduation.a.setText(gradu_a)
            self.onglets_bas.tab_graduation.origine_x.setText(origine_x)
            self.onglets_bas.tab_graduation.origine_y.setText(origine_y)
            self.onglets_bas.tab_donnees.valeurs.setText(valeurs)
            self.onglets_bas.tab_donnees.classes.setText(classes)
            print('mode_graphique', mode_graphique)
            self.graph = mode_graphique

        self.actualiser()
