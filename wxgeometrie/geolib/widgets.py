# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                  Feuille                                  #
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

##from sympy import S
from random import normalvariate

from .objet import Objet_avec_coordonnees_modifiables, Argument, Ref
from .textes import Texte_generique, Texte
from ..pylib import uu, print_error
from .. import param


class Bouton(Texte_generique, Objet_avec_coordonnees_modifiables):
    u"""Un bouton cliquable.

    Un bouton avec texte. Typiquement, on lui associe une action
    lorsque l'on clique dessus, via la méthode `onLeftClick`.
    """

    _style_defaut = param.boutons

    texte = __texte = Argument("basestring")
    abscisse = x = __x = Argument("Variable_generique", defaut=0)
    ordonnee = y = __y = Argument("Variable_generique", defaut=0)

    def __init__(self, texte=' ', x=None, y=None, **styles):
        x, y, styles = self._recuperer_x_y(x, y, styles)
        texte = uu(texte)

        if texte != "":
            styles["label"] = texte

        self.__texte = texte = Ref(texte)
        self.__x = x = Ref(x)
        self.__y = y = Ref(y)

        Objet_avec_coordonnees_modifiables.__init__(self, x, y, **styles)

    def _creer_figure(self):
        x, y = self.coordonnees
        if not self._representation:
            self._representation = [self.rendu.texte(), self.rendu.polygone(), self.rendu.ligne()]
        Texte_generique._creer_figure(self)
        text, fill, plot = self._representation
        fill.set_visible(True)
        can = self.canvas
        box = can.txt_box(text)
        w, h = can.dpix2coo(.5*box.width, -.5*box.height)
        niveau = self.style("niveau")
        ##if av == "left":
            ##x += w
        ##elif av == "right":
            ##x -= w
        ##if ah == "top":
            ##y -= h
        ##elif ah == "bottom":
            ##y += h
        mx, my = can.dpix2coo(10, -10) # marge verticale et horizontale (en pixels)
        w += mx
        h += my
        xy = [(x - w, y - h), (x - w, y + h), (x + w, y + h), (x + w, y - h)]
        fill.xy = xy
        fond = self.style('couleur_fond')
        fill.set(facecolor=fond, edgecolor=self._foncer(fond))
        fill.zorder = niveau
        xy.append(xy[0])
        plot.set_data(*zip(*xy))
        plot.set(color='k')
        # TODO : utiliser FancyBboxPatch
        # http://matplotlib.sourceforge.net/examples/pylab_examples/fancybox_demo.html

    def _creer_figure(self):
        x, y = self.coordonnees
        if not self._representation:
            self._representation = [self.rendu.texte(), self.rendu.rectangle()]
        Texte_generique._creer_figure(self)
        text, rect = self._representation
        rect.set_visible(True)
        can = self.canvas
        box = can.txt_box(text)
        w, h = can.dpix2coo(box.width, -box.height)
        niveau = self.style("niveau")
        marge = self.style("marge")
        ##if av == "left":
            ##x += w
        ##elif av == "right":
            ##x -= w
        ##if ah == "top":
            ##y -= h
        ##elif ah == "bottom":
            ##y += h
        mx, my = can.dpix2coo(marge, -marge) # marge verticale et horizontale (en pixels)
        rect.set_width(w + 2*mx)
        rect.set_height(h + 2*my)
        rect.set_x(self.x - .5*w - mx)
        rect.set_y(self.y - .5*h - my)
        fond = self.style('couleur_fond')
        rect.set(facecolor=fond, edgecolor=self._foncer(fond))
        rect.zorder = niveau
        # TODO : utiliser FancyBboxPatch
        # http://matplotlib.sourceforge.net/examples/pylab_examples/fancybox_demo.html


    ##def _distance_inf(self, x, y, d):
        ##d += self.style("marge")
        ##xmin, xmax, ymin, ymax = self._boite()
        ##return xmin - d - 3 < x < xmax + d + 3 and ymin - d < y < ymax + d

    def _boite(self):
        # Note : ymin et ymax "permutent" souvent car les transformations appliquées inversent l'orientation.
        can = self.canvas
        l, h = can.dimensions
        box = can.txt_box(self.figure[1])
        xmin = box.xmin
        ymax = h - box.ymin
        xmax = box.xmax
        ymin = h - box.ymax
        return xmin, xmax, ymin, ymax

    def _distance_inf(self, x, y, d):
        # Pour cliquer sur un bouton, il faut que la distance soit nulle.
        return Texte_generique._distance_inf(self, x, y, 0)

        ##d += self.style("marge")
        ##xmin, xmax, ymin, ymax = self._boite()
        ##return xmin - d - 3 < x < xmax + d + 3 and ymin - d < y < ymax + d


    def _en_gras(self, booleen):
        fond = self.style('couleur_fond')
        if booleen:
            self._representation[1].set_facecolor(self._claircir(fond))
        else:
            self._representation[1].set_facecolor(fond)

    @staticmethod
    def _claircir(couleur):
        r, g, b = couleur
        r = 1 - .5*(1 - r)
        g = 1 - .5*(1 - g)
        b = 1 - .5*(1 - b)
        return r, g, b

    @staticmethod
    def _foncer(couleur):
        r, g, b = couleur
        r = .75*r
        g = .75*g
        b = .75*b
        return r, g, b



class Champ(Texte):
    u"""Un champ de texte.

    Un champ de texte éditable en double-cliquant dessus.

    Le champ peut être encadré par du texte, via les mots-clefs `prefixe`
    (texte à gauche) et `suffixe` (texte à droite).
    On peut également lui associer un résultat attendu,
    via le mot-clef `attendu`::

        >>> from wxgeometrie import Champ
        >>> c = Champ('modifiez moi', 10, 5, prefixe="1+1=", attendu="2",
        ...                                  suffixe=" (entrer le resultat)")
        >>> c.style("attendu")
        '2'
        >>> c.texte = '?'
        >>> print(c.label())
        1+1=\$?\$ (entrer le resultat)

    Si un résultat est attendu, alors le texte rentré par l'utilisateur passera
    un test de validation. Si le résultat passe le test, un check vert est
    affiché à côté, sinon, un smiley :-( rouge est affiché.

    Par défaut, pour être validé, il faut que le résultat soit exactement
    conforme au texte attendu::

        >>> c.texte = "2.0"
        >>> c.correct
        False
        >>> c.texte = "2"
        >>> c.correct
        True

    Cependant, il est possible de définir un test de validation personnalisé::

        >>> def test(reponse, attendu):
        ...     return float(reponse) == float(attendu)
        >>> c.valider = test
        >>> c.texte = "2.0"
        >>> c.correct
        True

    On peut aussi associer une action à la validation::

        >>> def action(**kw):
        ...     if kw['correct']:
        ...         if not kw['correct_old']:
        ...             # Ce n'était pas correct avant
        ...             print('Bravo !')
        ...         else:
        ...             # C'était déjà correct
        ...             print("Oui, c'est bon aussi !")
        ...     else:
        ...         print('Essaie encore...')
        >>> c.evt_valider = action
        >>> c.texte = "3"
        Essaie encore...
        >>> c.texte = "2"
        Bravo !
        >>> c.texte = "2.0"
        Oui, c'est bon aussi !

    Cet action sera effectuée lorsque le texte du champ est modifié, si
    celui-ci passe le test de validation.

    Enfin, une liste des propositions peut être passée via le mot-clef `choix`::

        >>> c = Champ('', 10, 5, choix=['oui', 'non', 'sans opinion'])
        >>> c.style('choix')
        ['oui', 'non', 'sans opinion']
    """
    _style_defaut = param.champs

    texte = __texte = Argument("basestring", Texte._get_texte, Texte._set_texte)
    abscisse = x = __x = Argument("Variable_generique", defaut = lambda: normalvariate(0,10))
    ordonnee = y = __y = Argument("Variable_generique", defaut = lambda: normalvariate(0,10))

    # Il est possible d'attacher un test de validation personnalisé à l'objet.
    valider = None
    # Par ailleurs, on peut attacher à l'objet une action qui sera appelée après
    # chaque test de validation.
    evt_valider = None
    # Indique si le contenu du champ est conforme aux attentes
    correct = None

    def __init__(self, texte="", x=None, y=None, **styles):
        self.__texte = texte = Ref(texte)
        self.__x = x = Ref(x)
        self.__y = y = Ref(y)

        Texte.__init__(self, texte, x, y, **styles)

        # Permet de conserver la valeur precedente de `self.correct`.
        # Lorsque l'utilisateur entre un nouveau résultat, on peut ainsi
        # savoir si celui-ci était déjà correct, ou si le résultat est
        # devenu correct (il peut y avoir plusieurs résultats corrects).
        self._correct_old = self.correct = self._test_correct()
        ##self.__label_old = self.style('label')


    def label(self, *args, **kw):
        txt = Texte.label(self, *args, **kw)
        if not txt.strip('$\n'):
            txt = '...' # u'\u20DB'
        prefixe = self.style('prefixe')
        suffixe = self.style('suffixe')
        return (prefixe or '') + txt + (suffixe or '')


    def style(self, *args, **kw):
        label_change = ('label' in kw and kw['label'] != self._style['label'])
        val = Texte.style(self, *args, **kw)
        if label_change:
            self._correct_old = self.correct
            self.correct = self._test_correct()
            if getattr(self, 'evt_valider', None) is not None:
                self.evt_valider(champ=self, correct=self.correct,
                             correct_old=self._correct_old)
        return val



    def _creer_figure(self):
        ##print 'champ-label::', self.label()
        if not self._representation:
            self._representation = [self.rendu.texte(), self.rendu.decoration_texte(), self.rendu.texte()]
        Texte._creer_figure(self)
        can = self.canvas
        box = can.txt_box(self._representation[0])
        px, py = box.max
        x, y = can.pix2coo(px + 5, can.hauteur - py)
        txt = self._representation[2]
        lbl = self.style('label').replace(' ', '').replace(',', '.')
        attendu = self.style('attendu')
        if attendu is None or not lbl:
            txt.set(visible=False)
        else:
            txt.set(visible=True, x=x, y=y, va='top', ha='left')
            if self.correct:
                txt.set(text=u'\u2713', color='g') # 263A  00D8
            else:
                txt.set(text=u'\u2639', color='r') #u'\u26A0'
            ##if getattr(self, 'evt_valider', None) is not None and lbl != self.__label_old:
                ##self.evt_valider(champ=self, correct=correct,
                                 ##correct_old=self.__correct_old)
                ##self.__correct_old = correct
                ##self.__label_old = lbl


    def _test_correct(self):
        attendu = self.style('attendu')
        if attendu is None:
            return
        if self.valider is None:
            # Validation basique par défaut
            return (self.texte == attendu)
        else:
            # Méthode de validation personnalisée
            return self.valider(self.texte, attendu)
