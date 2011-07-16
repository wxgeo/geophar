# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

##------------------------------------------#######
#                   Satistiques                   #
##------------------------------------------#######
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
from math import isnan, sqrt

import wx
from numpy import array

from ...GUI import MenuBar, Panel_API_graphique
from .experience import LancerDes, Sondage, ExperienceFrame
from .onglets_internes import OngletsStatistiques
from ...mathlib.custom_functions import arrondir
from ...pylib import property2, uu, regsub, advanced_split, print_error, eval_restricted

def tst(result):
    if isnan(result):
        return u"Calcul impossible."
    return result


class Classe(tuple):
    lien = None

    def milieu(self):       return float(sum(self))/len(self)

    def lier(self, lien):
        self.lien = lien
        return self

    def __str__(self):      return "[%s,%s[" % (self[0], self[-1])
    def __repr__(self):     return self.__str__()
    def __unicode__(self):     return uu(self.__str__())
    def __int__(self):      return int(self.milieu())

    def __add__(self, y):   return self.milieu() + y
    def __mul__(self, y):   return self.milieu()*y
    def __div__(self, y):   return self.milieu()/y
    def __rdiv__(self, y):  return y/self.milieu()
    def __truediv__(self, y): return self.__div__(y)
    def __rtruediv__(self, y): return self.__rdiv__(y)
    def __neg__(self):   return -self.milieu()
    def __sub__(self, y):   return self.milieu() + (-y)
    def __rsub__(self, y):  return - self.milieu() + y
    def __pow__(self, y):   return self.milieu()**y
    def __rpow__(self, y):     return y**self.milieu()
    def __abs__(self):      return abs(self.milieu())
    def __eq__(self, y):    return self.milieu() == y
    def __ne__(self, y):   return not self.milieu() == y
    def __gt__(self, y):    return self.milieu() > y
    def __ge__(self, y):    return self.milieu() > y or self.milieu() == y
    def __lt__(self, y):    return self.milieu() < y
    def __le__(self, y):    return self.milieu() < y or self.milieu() == y
    def __nonzero__(self):  return self.milieu() <> 0

    def effectif(self):
        return float(sum([self.lien.valeurs[valeur] for valeur in self.lien.liste_valeurs() if self[0] <= valeur < self[1]]))

    def amplitude(self):
        return self[1] - self[0]

    def densite(self):
        return self.effectif()/self.amplitude()

    __radd__ = __add__; __rmul__ = __mul__
    __float__ = milieu



class StatMenuBar(MenuBar):
    def __init__(self, panel):
        MenuBar.__init__(self, panel)

        self.ajouter("Fichier", ["nouveau"], ["ouvrir"], ["ouvrir ici"], ["enregistrer"], ["enregistrer_sous"], ["exporter"], None, ["mise en page"], ["imprimer"], [u"presse-papier"], None, ["proprietes"], None, self.panel.doc_ouverts, None, ["fermer"], ["quitter"])
        self.ajouter("Editer", ["annuler"], ["refaire"], ["modifier"], ["supprimer"])
        self.ajouter("creer")
        self.ajouter("Affichage", ["onglet"], None, ["repere"], ["quadrillage"], ["orthonorme"], None, ["fenetre"], ["zoomer"], ["dezoomer"], ["orthonormaliser"])
        self.ajouter("Outils", [u"Expérience", u"Simuler une expérience.", "Alt+Ctrl+E", self.panel.creer_experience], [u"Lancers de dés", u"Simuler des lancers d'un ou de plusieurs dés.", "Ctrl+Shift+D", self.panel.creer_lancer_des], [u"Sondage", u"Simuler un sondage simple.", "Ctrl+Shift+S", self.panel.creer_sondage], None, ["options"])
        self.ajouter(u"avance1")
        self.ajouter("?")




class Statistiques(Panel_API_graphique):

    __titre__ = u"Statistiques" # Donner un titre a chaque module

    types_diagrammes = ('barres', 'batons', 'histogramme', 'cumul_croissant', 'cumul_decroissant', 'bandes', 'circulaire', 'semi-circulaire', 'boite')
    noms_diagrammes = [u"diagramme en barres", u"diagramme en batons", u"histogramme", u"effectifs cumulés croissants", u"effectifs cumulés décroissants", u"diagramme en bandes", u"diagramme circulaire", u"diagramme semi-circulaire", u"diagramme en boite"]
    _graph = None

    def __init__(self, *args, **kw):
        Panel_API_graphique.__init__(self, *args, **kw)

        self.couleurs = "bgrmcy"
        self.hachures = ('/', '*', 'o', '\\', '//', 'xx', '.', 'x', 'O', '..', '\\\\\\')

        self._valeurs = {}
        self.classes = []
        self.legende_x = '' # axe des abscisses
        self.legende_y = '' # axe des ordonnees
        self.legende_a = '' # unite d'aire (histogramme)
        self.gradu_x = ''
        self.gradu_y = ''
        self.gradu_a = ''
        self.origine_x = ''
        self.origine_y = ''
        self.donnees_valeurs = ''
        self.donnees_classes = ''
        self.intervalle_confiance = None
        #test dico quantiles
        self.choix_quantiles = {"mediane": [True, [0.5], 'r', '-'], \
                                    "quartiles": [True, [0.25, 0.75], 'b', '--'],\
                                    "deciles": [True, [0.1, 0.9], 'g', ':']}

        self.entrees = wx.BoxSizer(wx.VERTICAL)

        self.entrees.Add(wx.StaticText(self, -1, u" Mode graphique :"), 0, wx.ALL,5)

        self.choix = wx.Choice(self, -1, (100, 50), choices = self.noms_diagrammes)
        self.graph = 'barres' # *APRES* que self.choix soit défini.

        self.Bind(wx.EVT_CHOICE, self.EvtChoice, self.choix)
        self.entrees.Add(self.choix, 0, wx.ALL, 5)

        #self.entrees.Add(wx.StaticText(self, -1, ""))

        box = wx.StaticBox(self, -1, u"Mesures")
        bsizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        #self.entrees.Add(bsizer, 1, wx.EXPAND|wx.ALL, 5)
        self.entrees.Add(bsizer, 0, wx.ALL, 5)

        self._effectif_total = wx.StaticText(self, -1, u" Effectif total:")
        self._moyenne = wx.StaticText(self, -1, u" Moyenne:")
        self._mediane = wx.StaticText(self, -1, u" Médiane:")
        self._mode = wx.StaticText(self, -1, u" Mode:")
        self._etendue = wx.StaticText(self, -1, u" Etendue:")
        self._variance = wx.StaticText(self, -1, u" Variance:")
        self._ecart_type = wx.StaticText(self, -1, u" Ecart-type:" + 30*" ")

        bsizer.Add(self._effectif_total, 0, wx.TOP|wx.LEFT, 9)
        bsizer.Add(self._moyenne, 0, wx.TOP|wx.LEFT, 9)
        bsizer.Add(self._mediane, 0, wx.TOP|wx.LEFT, 9)
        bsizer.Add(self._mode, 0, wx.TOP|wx.LEFT, 9)
        bsizer.Add(self._etendue, 0, wx.TOP|wx.LEFT, 9)
        bsizer.Add(self._variance, 0, wx.TOP|wx.LEFT, 9)
        bsizer.Add(self._ecart_type, 0, wx.ALL, 9)

        haut = wx.BoxSizer(wx.HORIZONTAL)
        haut.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        haut.Add(self.entrees, 0, wx.ALL, 5)

        self.onglets_bas = OngletsStatistiques(self)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(haut, 1, wx.GROW)
        self.sizer.Add(self.onglets_bas, 0)
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
            self.choix.SetSelection(self.types_diagrammes.index(self._graph))
        return self._graph



    def EvtChoice(self, event):
        self._graph = self.types_diagrammes[event.GetSelection()]
        self.actualiser()


    def EvtChar(self, event):
        code = event.GetKeyCode()

        if code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.actualiser()
        else:
            event.Skip()

    def EvtCheck(self, event):
        self.param('hachures', self.onglets_bas.autres.hachures.GetValue())
        self.param('mode_effectifs', self.onglets_bas.autres.mode.GetSelection())
        self.param('reglage_auto_fenetre', self.onglets_bas.autres.auto.GetValue())
        self.actualiser()

    def actualiser(self, afficher = True):
        try:
            self.legende_x = self.onglets_bas.legende.x.GetValue()
            self.legende_y = self.onglets_bas.legende.y.GetValue()
            self.legende_a = self.onglets_bas.legende.a.GetValue()
            self.gradu_x = self.onglets_bas.graduation.x.GetValue()
            self.gradu_y = self.onglets_bas.graduation.y.GetValue()
            self.gradu_a = self.onglets_bas.graduation.a.GetValue()
            self.origine_x = self.onglets_bas.graduation.origine_x.GetValue()
            self.origine_y = self.onglets_bas.graduation.origine_y.GetValue()
            self.donnees_valeurs = self.onglets_bas.donnees.valeurs.GetValue()
            self.onglets_classes = self.onglets_bas.donnees.classes.GetValue()

            # test choix quantiles
            self.choix_quantiles["mediane"][0] = self.onglets_bas.autresq.mediane.GetValue()
            self.choix_quantiles["quartiles"][0] = self.onglets_bas.autresq.quartiles.GetValue()
            self.choix_quantiles["deciles"][0] = self.onglets_bas.autresq.deciles.GetValue()

            self.classes = []
            self._valeurs = {}

            # La chaine va être découpée au niveau des espaces ; on supprime donc les espaces inutiles
            valeurs = regsub("[ ]*[*][ ]*", self.onglets_bas.donnees.valeurs.GetValue(), "*") # on supprime les espaces autour des '*'
            valeurs = regsub("[[][^]]*for[^]]*in[^]]*[]]", valeurs, lambda s:s.replace(' ','|')) # une expression du style "[i for i in range(7)]" ne doit pas être découpée au niveau des espaces.
            classes = self.onglets_bas.donnees.classes.GetValue()


            for classe in advanced_split(classes.replace(";", ","), " ", symbols = "({})"):
                if classe.endswith("["):
                    classe = classe[:-1] + "]"
                self.ajouter_classes(Classe(eval_restricted(classe)).lier(self))

            for val in advanced_split(valeurs.replace(";", ","), " ", symbols = "({})"):
                if val.endswith("["):
                    val = val[:-1] + "]"

                if re.match("[[][^]]*for[^]]*in[^]]*[]]", val):
                    val = eval_restricted(val.replace('|',' '))
                    for v in val:
                        if type(v) in (list, tuple): # syntaxe style "[(3,i) for i in range(7)]" où 3 est l'effectif
                            self.ajouter_valeur(v[1], v[0])
                        else:
                            self.ajouter_valeur(v) # syntaxe style "[i for i in range(7)]"
                else:
                    val = [eval_restricted(x) for x in advanced_split(val, "*")]
                    val.reverse()
                    self.ajouter_valeur(*val)

            # par défaut, si toutes les valeurs entrées sont des classes, le découpage en classes suit les classes entrées.
            if not self.classes and not [x for x in self._valeurs.keys() if not isinstance(x, Classe)]:
                self.classes = self._valeurs.keys()

            self.calculer()
            if afficher:
                self.affiche()
            self.canvas.message(u"Graphique fini.")

        except:
            self.canvas.message(u"Impossible de construire le graphique.")
            print_error()


    def calculer(self):
        e = self.effectif_total()
        if e == int(e):
            e = int(e)
        self._effectif_total.SetLabel(u" Effectif total: %s" %e)
        self._moyenne.SetLabel(u" Moyenne: %s" %self.moyenne())
        self._mediane.SetLabel(u" Médiane: " + str(self.mediane()))
        self._mode.SetLabel(u" Mode: %s" %self.mode())
        self._etendue.SetLabel(u" Etendue: %s" %self.etendue())
        self._variance.SetLabel(u" Variance: %s" %self.variance())
        self._ecart_type.SetLabel(u" Ecart-type: %s" %self.ecart_type())

    def ajouter_valeurs(self, *valeurs):
        for val in valeurs:
            self.ajouter_valeur(val)


    def ajouter_valeur(self, valeur, effectif = 1):
        if type(valeur) in (list, tuple):
            valeur = Classe(valeur).lier(self)
        if self._valeurs.has_key(valeur):
            self._valeurs[valeur] += effectif
        else:
            self._valeurs[valeur] = float(effectif)

    @property
    def valeurs(self):
        mode = self.param('mode_effectifs')
        valeurs = self._valeurs
        # mode = 0: valeurs
        # mode = 1: fréquences
        # mode = 2: pourcentages
        if mode:
            k = (100 if mode == 1 else 1)
            valeurs = valeurs.copy()
            total = sum(valeurs.itervalues())
            for val in valeurs:
                valeurs[val] *= k/total
        return valeurs


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


    def ajouter_classes(self, *classes):
        self.classes += classes
        self.classes.sort()


    def liste_valeurs(self):
        valeurs = self._valeurs.keys()
        valeurs.sort()
        return valeurs

    def liste_valeurs_effectifs(self):
        valeurs_effectifs = self._valeurs.items()
        valeurs_effectifs.sort()
        return valeurs_effectifs



    def intervalle_classes(self):
        return min([classe[0] for classe in self.classes]), max([classe[1] for classe in self.classes])


    def experience(self, formule, n, val_possibles = ()):
        u"""Réalise 'n' fois l'expérience décrite par 'formule'.
        Exemple: self.experience('int(6*rand())+1', 100) simule 100 lancers de dés."""

        self.actualiser(False)
        self.ajouter_valeurs(*[eval(formule) for i in xrange(n)])
        for val in val_possibles:
            self.ajouter_valeur(val, 0)
        self.calculer()
        self.affiche()



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
        win.Show(True)

    def creer_lancer_des(self, event = None):
        win = LancerDes(self)
        win.Show(True)


    def creer_sondage(self, event = None):
        win = Sondage(self)
        win.Show(True)




    def dessiner_intervalle_confiance(self):
        n = self.intervalle_confiance
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
        self.canvas.dessiner_texte(0, 0, msg, va='center', ha='center')
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
        hmax = max([classe.densite() for classe in self.classes])

        # Réglage de la fenêtre d'affichage
        self.fenetre(m - 0.1*(M-m), M + 0.4*(M-m), -0.1*hmax, 1.1*hmax)
        self.origine(m, 0)
        self.graduations(l, 0)

        i = 0
        for classe in self.classes:
            h = classe.densite()
            xx = [classe[0], classe[0], classe[1], classe[1]]
            yy = [0, h, h, 0]
            if self.param('hachures'):
                self.canvas.dessiner_polygone(xx, yy, 'w', hatch = self.hachures[i%len(self.hachures)])
            else:
                self.canvas.dessiner_polygone(xx, yy, self.couleurs[i%len(self.couleurs)])
            i += 1

        self.canvas.dessiner_texte(M + 0.3*(M-m)-5*self.canvas.coeff(0), -18*self.canvas.coeff(1), self.legende_x, ha = "right")

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
            effectif = float(self.gradu_a) if self.gradu_a else arrondir(sum([classe.effectif() for classe in self.classes])/20)
            # cote du carre en pixels
            cote = sqrt(effectif/(self.canvas.coeff(0)*self.canvas.coeff(1)))
            lu = cote*self.canvas.coeff(0)
            hu = cote*self.canvas.coeff(1)

        x = M + 0.1*(M-m)
        col = '0.85' if self.param('hachures') else 'b'
        self.canvas.dessiner_polygone([x, x + lu, x + lu, x, x], [.5*hmax, .5*hmax, .5*hmax + hu, .5*hmax + hu, .5*hmax], col)

        eff = str(effectif).replace('.', ',')
        if eff.endswith(',0'):
            eff = eff[:-2]

        legende = eff + " " + (self.legende_a or u"unité")

        if effectif > 1 and not self.legende_a:
            legende += "s"

        self.canvas.dessiner_texte(x, .5*hmax - 15*self.canvas.coeff(1), legende, va = "top")


    def courbe_effectifs(self, mode=1):
        u"""
        Courbe des effectifs cumulés croissants si mode = 1, décroissants si mode = -1.
        """
        if self.axes(x = True, y = True, classes=True):
            return u"Définissez des classes.\nExemple : [0;10[ [10;20["

        valeurs = self.liste_valeurs()

        l = min([classe[1] - classe[0] for classe in self.classes])
        m, M = self.intervalle_classes()
        hmax = self.total()
        self.fenetre(m - 0.1*(M-m), M + 0.2*(M-m), -0.1*hmax, 1.1*hmax)
        self.graduations(l, arrondir(hmax/10))
        self.origine(m, 0)

        #classe with cumulatives eff or freq 2-uple list: y_cum
        y_cum=[]
        couleur = 'k' if self.param('hachures') else 'b'
        for classe in self.classes:
            y_value = [sum([self.valeurs[valeur] for valeur in valeurs if mode*valeur <= mode*classe[i]]) for i in (0, 1)]
            self.canvas.dessiner_ligne(classe, y_value, color = couleur)
            y_cum.append((classe, y_value))
        dx, dy = self.canvas.dpix2coo(-5, -18)
        self.canvas.dessiner_texte(M + 0.2*(M-m) + dx, dy, self.legende_x, ha = "right")
        dx, dy = self.canvas.dpix2coo(15, -5)
        #ajout des quantiles
        for  q in ["mediane", "quartiles", "deciles"]:
            # tracer si les quantiles sont activés
            if self.choix_quantiles[q][0]:
                freq = self.choix_quantiles[q][1]
                for a in freq:
                    try:
                        (c, y) = self.select_classe(y_cum, a, mode)
                        self.quantile_plot(c, y, a, couleur = self.choix_quantiles[q][2], style = self.choix_quantiles[q][3])
                    except TypeError:
                        # c peut être vide si les classes commencent à une
                        # fcc trop grande.
                        pass
        #legende
        legende_y = self.legende_y
        if not legende_y:
            mode = self.param('mode_effectifs')
            if mode == 0:
                legende_y = u"Effectifs cumulés"
            elif mode == 1:
                legende_y = u"Pourcentages cumulés"
            else:
                legende_y = u"Fréquences cumulées"
        self.canvas.dessiner_texte(m + dx, 1.1*hmax + dy, legende_y, va='top')


    def quantile_plot(self, classe, y, a, couleur ='r', style ='-'):
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
        m = (y[1]-y[0])/(classe[1]-classe[0])
        x_reg = (a_reel-y[0])/m + classe[0]
        # coordonnées de l'origine
        x0, y0 = self.canvas.origine_axes
        dx, dy = self.canvas.dpix2coo(-5, -18)
        # tenir compte du mode N&B
        col = 'k' if self.param('hachures') else couleur

        self.canvas.dessiner_ligne([x0, x_reg], [a_reel, a_reel], color = col, linestyle = style)
        self.canvas.dessiner_ligne([x_reg, x_reg], [a_reel, y0], color = col, linestyle = style)
        self.canvas.dessiner_texte(x_reg, y0+dy, format(x_reg, ".4g"), color = col)


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
        u"""Diagramme en barres ; ratio mesure le quotient largeur d'une barre sur largeur maximale possible.
         (nombre décimal entre 0 et 1).
         Essentiellement pertinent pour des séries qualitatives."""

        if self.axes(y=True, legende_x=True):
            return

        valeurs = self.liste_valeurs()

        lmax = 100./len(valeurs)
        l = ratio*lmax
        e = .5*(lmax - l)
        hmax = max(self.valeurs.values())
        self.fenetre(-10, 110, -.15*hmax, 1.15*hmax)
        self.canvas.dessiner_ligne((0, 110), (0, 0), 'k')

        self.graduations(0, arrondir(hmax/10))
        self.origine(0, 0)

        n = 0
        for valeur in valeurs:
            h = self.valeurs[valeur]
            x0, x1 = (2*n + 1)*e + n*l, (2*n + 1)*e + (n+1)*l
            xx = [x0, x0, x1, x1]
            yy = [0, h, h, 0]
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
        'largeur' est la demi-largeur en pixel."""

        if self.axes(x=True, y=True):
            return

        valeurs = self.liste_valeurs()

        m, M = valeurs[0], valeurs[-1]
        if m == M:
            l = 1
            M += 1
            m -= 1
        else:
            l = arrondir((M - m)/20)   # on evite d'avoir des valeurs trop fantaisistes pour le pas !
            m = l*int(m/l) - l


        hmax = max(self.valeurs.values())

        # reglage de la fenetre d'affichage
        self.fenetre(m - 0.1*(M-m), M + 0.1*(M-m), -0.1*hmax, 1.1*hmax)
        if int(m) == m:
            m = int(m) # pour des raisons esthetiques

        self.origine(m, 0)
        self.graduations(l, arrondir(hmax/10))

        e = largeur*self.canvas.coeff(0)

        i = 0
        for val, eff in self.valeurs.items():
            couleur = 'k' if self.param('hachures') else self.couleurs[(i - 1)%len(self.couleurs)]
            self.canvas.dessiner_polygone([val - e, val - e, val + e, val + e], [0, eff, eff, 0], couleur)
            i+=1


        self.canvas.dessiner_texte(M + 0.1*(M-m) - 5*self.canvas.coeff(0), -18*self.canvas.coeff(1), self.legende_x, ha = "right")
        legende_y = self.legende_y
        if not legende_y:
            mode = self.param('mode_effectifs')
            if mode == 0:
                legende_y = u"Effectifs"
            elif mode == 1:
                legende_y = u"Pourcentages"
            else:
                legende_y = u"Fréquences"
        self.canvas.dessiner_texte(m + 15*self.canvas.coeff(0), 1.1*hmax - 5*self.canvas.coeff(1), legende_y, va = "top")

        self.dessiner_intervalle_confiance()


    def diagramme_bande(self):
        u"""Diagramme en bande."""

        if self.axes():
            return

        valeurs = self.liste_valeurs()

        l_unite = 100./self.total()
        n = 0
        x = 0

        self.fenetre(-10, 110, -1, 2)
        self.graduations(0, 0)


        for valeur in valeurs:
            l = self.valeurs[valeur]*l_unite
            if self.param('hachures'):
                self.canvas.dessiner_polygone([x, x, x + l, x + l, x], [0, 1, 1, 0, 0], 'w', hatch = self.hachures[(n - 1)%len(self.hachures)])
            else:
                self.canvas.dessiner_polygone([x, x, x + l, x + l, x], [0, 1, 1, 0, 0], self.couleurs[(n - 1)%len(self.couleurs)])
            self.canvas.dessiner_texte(x+l/2., - 18*self.canvas.coeff(1), str(valeur),  ha="center")
            n += 1
            x += l



    def diagramme_circulaire(self, angle = 360):
        if self.axes():
            return

        valeurs = self.liste_valeurs()

        valeurs, effectifs = zip(*self.valeurs.items())

        # petit raffinement pour eviter que 2 couleurs identiques se suivent
        n = len(effectifs)
        l = len(self.couleurs)
        if n%l == 1:
            couleurs =  tuple(((n-1)//l)*self.couleurs + self.couleurs[1])
        else:
            couleurs = tuple(self.couleurs)

        effectifs = angle/360.*array(effectifs)/sum(effectifs)
        labels = [str(valeur) for valeur in valeurs]
        patches, texts = self.canvas.axes.pie(effectifs, labels = labels, labeldistance = 1.16, shadow = False, colors = couleurs)
        if self.param('hachures'):
            for i, patch in enumerate(patches):
                patch.set_fc('w')
                patch.set_hatch(self.hachures[i%len(self.hachures)])
        self.canvas.synchroniser_fenetre() # pour profiter du reglage effectue par matplotlib
        self.canvas.orthonormer() # pour avoir un vrai cercle
        # rafraichir produirait une recursion infinie !


    def diagramme_boite(self, afficher_extrema = True):
        u"Appelé aussi diagramme à moustache."

        if self.axes(x=True):
            return

        med = self.mediane()
        q1 = self.quartile(1)
        q3 = self.quartile(3)
        d1 = self.decile(1)
        d9 = self.decile(9)
        vals = self.liste_valeurs()
        m = vals[0]
        M = vals[-1]
        if str in [type(i) for i in (med, q1, q3, d1, d9)]:
            # self.mediane() ou self.decile() ou... renvoie "calcul impossible."
            return

        if int(m) == m:
            m = int(m) # pour des raisons esthetiques
        self.origine(m, 0)
        l = arrondir((M-m)/20)
        self.graduations(l, 0)
        if m <> M:
            self.fenetre(m - 0.1*(M-m), M + 0.1*(M-m), -0.1, 1.1)
        else:
            self.fenetre(m - 0.1, M + 0.1, -0.1, 1.1)

        def col(val):
            return 'k' if self.param('hachures') else val

        w = 1 if self.param('hachures') else 1.5

        self.canvas.dessiner_ligne([d1, d1], [.4, .6], linewidth = w, color = col('g'))
        self.canvas.dessiner_ligne([d9, d9], [.4, .6], linewidth = w, color = col('g'))
        self.canvas.dessiner_ligne([q1, q1], [.2, .8], linewidth = w, color = col('b'))
        self.canvas.dessiner_ligne([q3, q3], [.2, .8], linewidth = w, color = col('b'))
        self.canvas.dessiner_ligne([med, med], [.2, .8], linewidth = w, color = col('r'))
        self.canvas.dessiner_ligne([d1, q1], [.5, .5], color = "k")
        self.canvas.dessiner_ligne([q3, d9], [.5, .5], color = "k")
        self.canvas.dessiner_ligne([q3, q1], [.2, .2], color = "k")
        self.canvas.dessiner_ligne([q3, q1], [.8, .8], color = "k")
        self.canvas.dessiner_ligne([m, M], [.5, .5], linestyle = "None", marker = "o", color="k", markerfacecolor = "w")


#------------------------------------------------------------
#   Infos sur la serie.
#   (Mesures de tendance centrales, de dispersion, etc...)
#------------------------------------------------------------


    def effectif_total(self):
        # self._valeurs : effectifs bruts (non convertis en fréquences)
        return sum(self._valeurs.itervalues())

    def total(self):
        u"Retourne soit l'effectif total, soit 100, soit 1, selon les paramètres en cours."
        return sum(self.valeurs.itervalues())

    def mode(self):
        if not self.effectif_total():
            return u"Calcul impossible."
        m = max(self.valeurs.values())
        v = [str(key) for key in self.valeurs.keys() if self.valeurs[key] == m]
        if len(v) > 2:
            v = v[:2] + ["..."]
        return " ; ".join(v)

    def moyenne(self):
        try:
            return tst(1.*sum([eff*val for val, eff in self.valeurs.items()])/self.total())
        except (ZeroDivisionError, TypeError):
            return u"Calcul impossible."

    def etendue(self):
        try:
            valeurs = self.liste_valeurs()
            return valeurs[-1] - valeurs[0]
        except (TypeError, IndexError):
            return u"Calcul impossible."

    def variance(self):
        try:
            m = self.moyenne()
            if isinstance(m, basestring):
                raise TypeError
            return tst(1.*sum([eff*(val - m)**2 for val, eff in self.valeurs.items()])/self.total())
        except (ZeroDivisionError, TypeError):
            return u"Calcul impossible."

    def ecart_type(self):
        v = self.variance()
        if isinstance(v, basestring):
            return u"Calcul impossible."
        return tst(sqrt(v))

    def mediane(self):
        u"""Correspond à la 'valeur du milieu' quand on ordonne les données.
        Dans certains cas, en divisant l'effectif par 2, on tombe entre 2 valeurs.
        Dans ce cas, on convient de prendre la demi-somme de ces valeurs.
        (ex: tous les effectifs valent un et l'effectif total impair)

        Une bonne manière de visualiser la médiane pour des effectifs non entiers
        est de tracer un diagramme en bande."""
        old_somme = somme = 0
        old_val = None
        objectif = self.effectif_total()/2
        for val, effectif in self.liste_valeurs_effectifs():
            somme += effectif
            if somme > objectif:
                if old_somme == objectif: # la mediane est à cheval sur 2 valeurs
                    try:
                        return (old_val + val)/2
                    except TypeError:
                        print_error()
                        return u"Calcul impossible."
                return val
            old_val = val
            old_somme = somme
        return u"Calcul impossible."





    def tile(self, k = 4, i = 1):
        u"""
        Renvoie la valeur x de la série telle que au moins i/k des données de la série
        soient inférieures ou égales à x.

        Exemple :   tile(4,1) -> premier quartile.
                    tile(10,2) -> deuxième décile.
        """

        somme = 0
        objectif = i/k*self.effectif_total()
        for val, effectif in self.liste_valeurs_effectifs():
            somme += effectif
            if somme >= objectif:
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
            "serie" : [{"valeurs" : [self.donnees_valeurs], "classes" : [self.donnees_classes]}],
            "legende" : [{"x" : [self.legende_x], "y" : [self.legende_y], "a" : [self.legende_a]}],
            "graduation": [{"x" : [self.gradu_x], "y" : [self.gradu_y], "a" : [self.gradu_a]}],
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
            mode_graphique = diagramme["mode_graphique"][0]

            self.onglets_bas.legende.x.SetValue(legende_x)
            self.onglets_bas.legende.y.SetValue(legende_y)
            self.onglets_bas.legende.a.SetValue(legende_a)
            self.onglets_bas.graduation.x.SetValue(gradu_x)
            self.onglets_bas.graduation.y.SetValue(gradu_y)
            self.onglets_bas.graduation.a.SetValue(gradu_a)
            self.onglets_bas.donnees.valeurs.SetValue(valeurs)
            self.onglets_bas.donnees.classes.SetValue(classes)
            print('mode_graphique', mode_graphique)
            self.graph = mode_graphique

        self.actualiser()
