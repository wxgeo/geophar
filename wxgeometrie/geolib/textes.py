# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                    Texte                    #
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

# version unicode

from random import uniform, normalvariate
from math import cos, sin

from matplotlib.pyparsing import ParseFatalException

from .objet import Objet_avec_coordonnees, Argument, Ref, Objet, \
                   Objet_avec_coordonnees_modifiables
from .constantes import NOM, TEXTE, MATH, FORMULE, RIEN
from .formules import Formule

from ..pylib import uu, warning, property2, no_argument, print_error
from ..mathlib.parsers import convertir_en_latex
from ..pylib import mathtext_parser
from .. import param

################################################################################


class Texte_generique(Objet_avec_coordonnees):
    u"""Un texte générique.

    La classe mère de tous les objets Texte. (Usage interne)."""

    _style_defaut = param.textes
    _prefixe_nom = "txt"

    # Utilisé pour éditer le texte interactivement dans le canvas.
    _label_temporaire = None

    def __init__(self, **styles):
        Objet_avec_coordonnees.__init__(self, **styles)


    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.texte(), self.rendu.decoration_texte()]
        text = self._representation[0]
        rect = self._representation[1]
        texte = (self.label() if self._label_temporaire is None else self._label_temporaire + '...')
        if not texte:
            text.set_visible(False)
            rect.set_visible(False)
            return
        else:
            text.set_visible(True)
        x, y = self.coordonnees
        fond = self.style("fond")
        cadre = self.style('cadre')
        niveau = self.style("niveau")
        av = self.style("alignement_vertical")
        ah = self.style("alignement_horizontal")
        if av not in ('center', 'top', 'bottom', 'baseline'):
            av = 'bottom'
        if ah not in ('center', 'right', 'left'):
            ah = 'left'
        text.set_x(x)
        text.set_y(y)
        text.set_color(self.style("couleur"))
        text.set_alpha(self.style('alpha'))
        font = text.get_fontproperties()
        font.set_size(self.style("taille"))
        #font.set_stretch(self.style("largeur"))  # mal gere par matploltib (version 0.87)

        if param.latex:  # formatage géré par LaTeX
            style = self.style("style")
            if  style == "italic":
                texte = "\\textit{" + texte + "}"
            elif style == "oblique":
                texte = "\\textsl{" + texte + "}"
            if self.style("epaisseur") == "gras":
                texte = "\\textbf{" + texte + "}"
            famille = self.style("famille")
            if famille == "serif":
                texte = "\\rmfamily{" + texte + "}"
            elif famille == "monospace":
                texte = "\\ttfamily{" + texte + "}"
#            elif famille == "cursive":
#                texte = "\\mathscr{" + texte + "}"
            elif famille != "sans-serif":
                warning("Famille de police non disponible en mode LaTeX.")
        else: # formatage géré par matplotlib
#            font.set_weight(self.style("epaisseur") == "gras" and "bold" or "normal")
            font.set_weight(self.style("epaisseur") > 55 and "bold" or "normal")
            font.set_style(self.style("style"))
            font.set_family(self.style("famille"))
        text._text = texte

        text.set_rotation(self.style("angle"))
        text.set_verticalalignment(av)
        text.set_horizontalalignment(ah)
        text.zorder = niveau + .001
        if fond is None and cadre is None:
            rect.set_visible(False)
        else:
            # Matplotlib: None donne le style par défaut,
            # 'none' désactive l'affichage.
            if fond is None:
                fond = 'none'
            elif cadre is None:
                cadre = 'none'
            rect.set(visible=True, texte=text, facecolor=fond, edgecolor=cadre,
                     zorder=niveau, pad=self.style('pad'), alpha=self.style('alpha_fond'))

    @property2
    def label_temporaire(self, *val):
        if val:
            self._label_temporaire = val[0]
            self.figure_perimee()
        return self._label_temporaire

    def _boite(self):
        # Note : ymin et ymax "permutent" souvent car les transformations appliquées inversent l'orientation.
        can = self.canvas
        l, h = can.dimensions
        box = can.txt_box(self.figure[0])
        xmin = box.xmin
        ymax = h - box.ymin
        xmax = box.xmax
        ymin = h - box.ymax
        return xmin, xmax, ymin, ymax

    def _espace_vital(self):
        # Note : ymin et ymax "permutent" souvent car les transformations appliquées inversent l'orientation.
        if not self.label():
            return
        can = self.canvas
        _xmin, _xmax, _ymin, _ymax = self._boite()
        xmin, ymin = can.pix2coo(_xmin, _ymax)
        xmax, ymax = can.pix2coo(_xmax, _ymin)
        return xmin, xmax, ymin, ymax



    def _distance_inf(self, x, y, d):
        xmin, xmax, ymin, ymax = self._boite()
        return xmin - d < x < xmax + d and ymin - d < y < ymax + d

    def encadrer(self, couleur='k', couleur_fond=None, alpha=1):
        if not couleur:
            couleur = None
        self.style(cadre=couleur, fond=couleur_fond, alpha_fond=alpha)

################################################################################


class Texte_editable_generique(Texte_generique):
    u"""Un texte éditable générique.

    La classe mère de tous les textes éditables.
    (Usage interne).
    """

    def _get_texte(self, value):
        if self._initialise:
            formule = self.formule
            if formule is not None:
                # Dans le cas d'une formule, il faut regénérer le texte.
                # En effet, la formule peut faire référence à des objets qui ont été
                # renommés depuis. Cela permet de garder un texte correctement
                # interprétable.
                return eval(repr(formule))
        return value

    def _set_texte(self, value):
        if not isinstance(value, unicode):
            value = uu(value)
        if self._initialise and self._style['mode'] == FORMULE:
            self.formule = value
        # Il faudra vérifier que le texte ne provoque pas d'erreur
        # dans le parser LaTeX de matplotlib :
        self._label_correct = None
        return value

    texte = __texte = Argument("unicode", _get_texte, _set_texte)

    def __init__(self, texte='', **styles):
        if not isinstance(texte, (Ref, unicode)):
            texte = uu(texte)

        self.__texte = texte = Ref(texte)

        # Contiendra éventuellement une formule (si le mode formule est activé).
        self._formule = None

        Texte_generique.__init__(self, **styles)


    @property2
    def formule(self, txt=no_argument):
        if txt is no_argument:
            return self._formule
        # On supprime proprement la formule précédente.
        if self._formule is not None:
            self._formule.supprimer()
        self._formule = (Formule(self, txt) if txt else None)


    def label(self, texte=None, mode=None):
        u"""Affiche le label (ou étiquette) de l'objet.

        La chaine renvoyée dépendra de la valeur du style mode:
        - si mode = 0 (`param.RIEN`), renvoie ''
        - si mode = 1 (`param.NOM`), renvoie le nom de l'objet
        - si mode = 2 (`param.TEXTE`), renvoie le label proprement dit de l'objet
        - si mode = 3  (`param.FORMULE`), renvoie le label interprété comme une formule

        Si le paramètre label est spécifié, le label est modifié, et par défaut
        le mode est fixé à `TEXTE`."""
        if texte is not None:
            if mode is None:
                mode = TEXTE
            # Il faut changer le mode **avant** de changer le texte.
            # On utilise une commande de bas niveau, pour éviter de modifier
            # réellement la formule tant que le texte n'est pas le bon.
            self._style['mode'] = mode
            self.texte = texte

        elif mode is not None:
            self.style(mode=mode)

        else:
            mode = self.style("mode")
            if mode == NOM:
                return self.nom_latex
            elif mode == TEXTE:
                label = self.texte
            elif mode == FORMULE:
                # Retourne le texte avec les expressions évaluées
                label = unicode(self.formule)
            elif mode == RIEN:
                return ""
            else:
                print('Warning: mode inconnu (%s)' % mode)

            old_label = label

            # TODO: add support for a CUSTOM mode, to use a custom
            # formating function.
            if self.style("formatage") == MATH:
                label = convertir_en_latex(label)

            if self._label_correct is None:
                if '$' in label:
                    # on teste si l'expression LaTeX convient au parser de matplotlib
                    try:
                        mathtext_parser(label)
                        self._label_correct = True
                    except Exception:
                        if param.debug:
                            print_error()
                        self._label_correct = False
                else: # le parser ne sera pas utilisé (ce n'est pas une expression LaTeX)
                    self._label_correct = True

            # Échec du parser LaTeX, on affiche une version "brute".
            if not self._label_correct:
                label = old_label.replace('$', r'\$')

            return label


    def style(self, nom_style=None, **kw):
        u"""Renvoie le ou les styles demandés, ou modifie les styles de l'objet.

        * ``nom_style`` est un nom de style, ou une liste de noms de styles:
        La propriété correspondante est recherchée dans self._style.
        Ex: couleur, taille = A.style(('couleur', 'taille'))

        * ``**kw`` sert à modifier des styles.
        Ex: A.style(couleur = 'blue')
        """
        mode = kw.get('mode', None)
        if mode is not None and self._style['mode'] != mode:
            # On met à jour la formule si besoin est.
            if mode == FORMULE:
                self.formule = self.texte
            else:
                self.formule = None

        return Objet.style(self, nom_style, **kw)

    @property
    def mode_affichage(self):
        u"Assure une interface commune entre les objets avec étiquette et les textes."
        return self.style('mode')

_get_texte = Texte_editable_generique._get_texte
_set_texte = Texte_editable_generique._set_texte

################################################################################


class Texte(Texte_editable_generique, Objet_avec_coordonnees_modifiables):
    u"""Un texte.

    Un texte à afficher"""

    texte = __texte = Argument("unicode", _get_texte, _set_texte)
    abscisse = x = __x = Argument("Variable_generique", defaut = lambda: normalvariate(0,10))
    ordonnee = y = __y = Argument("Variable_generique", defaut = lambda: normalvariate(0,10))

    def __init__(self, texte = "", x = None, y = None, **styles):
        x, y, styles = self._recuperer_x_y(x, y, styles)

        self.__texte = texte = Ref(texte)
        self.__x = x = Ref(x)
        self.__y = y = Ref(y)

        Objet_avec_coordonnees_modifiables.__init__(self, x, y, **styles)
        Texte_editable_generique.__init__(self, texte, **styles)

        ##self.etiquette = self


    ##def style(self, *args, **kw):
        ##if kw.get("legende") == RIEN:
            ##kw["legende"] = TEXTE
            ##kw["visible"] = False
        ##return Objet_avec_coordonnees_modifiables.style(self, *args, **kw)


    @staticmethod
    def _convertir(objet):
        if isinstance(objet, basestring):
            return Texte(objet)
        if hasattr(objet, "__iter__"):
            return Texte(*objet)
        raise TypeError, "object is not iterable."


    def _update(self, objet):
        if not isinstance(objet, Texte):
            if hasattr(objet, "__iter__") and len(objet) == 1 and isinstance(objet[0], basestring):
                self.label(objet[0])
                return
            else:
                objet = self._convertir(objet)
        if isinstance(objet, Texte):
            self.label(objet.texte)
            self.coordonnees = objet.coordonnees
        else:
            raise TypeError, "l'objet n'est pas un texte."


    def _set_feuille(self):
        xmin, xmax, ymin, ymax = self.feuille.fenetre
        if "_Texte__x" in self._valeurs_par_defaut:
            self.__x = uniform(xmin, xmax)
        if "_Texte__y" in self._valeurs_par_defaut:
            self.__y = uniform(ymin, ymax)
        Objet._set_feuille(self)


    def _en_gras(self, booleen):
        figure = self.figure
        if figure:
            # La figure est vide si l'objet est masqué.
            if booleen:
                figure[0]._bbox = {'alpha': 0.5, 'linewidth': 1, 'fill': False}
            else:
                figure[0]._bbox = None


    def image_par(self, transformation):
        from .transformations import Rotation, Translation, Homothetie, Reflexion
        if isinstance(transformation, Rotation):
            return Texte_rotation(self, transformation)
        elif isinstance(transformation, Translation):
            return Texte_translation(self, transformation)
        elif isinstance(transformation, Homothetie):
            return Texte_homothetie(self, transformation)
        elif isinstance(transformation, Reflexion):
            return Texte_reflexion(self, transformation)
        raise NotImplementedError

################################################################################
# TODO: Tester et améliorer les classes suivantes.


class Texte_transformation_generique(Texte_generique):
    u"""Une image d'un texte par transformation.

    Classe mère de toutes les images de textes par transformation. (Usage interne)."""

    texte = __texte = Argument("Texte_generique")
    transformation = __transformation = Argument("Transformation_generique")

    def __init__(self, texte, transformation, **styles):
        self.__texte = texte = Ref(texte)
        self.__transformation = transformation = Ref(transformation)
        Texte_generique.__init__(self, **styles)

    def style(self, *args, **kw):
        if "visible" in args:
            return self._style["visible"]
        return self.__texte.style(*args, **kw)

################################################################################


class Texte_rotation(Texte_transformation_generique):
    u"""Une image d'un texte par rotation.

    Texte construit à partir d'un autre via une rotation d'angle et de centre donné."""

    texte = __texte = Argument("Texte_generique")
    rotation = __rotation = Argument("Rotation")

    def __init__(self, texte, rotation, **styles):
        self.__texte = texte = Ref(texte)
        self.__rotation = rotation = Ref(rotation)
        Texte_transformation_generique.__init__(self, texte, rotation, **styles)

    def _get_coordonnees(self):
        x0, y0 = self.__rotation.centre.coordonnees
        xA, yA = self.__texte.coordonnees
        a = self.__rotation.radian
        sina = sin(a) ; cosa = cos(a)
        return (-sina*(yA - y0) + x0 + cosa*(xA - x0), y0 + cosa*(yA - y0) + sina*(xA - x0))

##    def style(self, *args, **kw):
##        if "angle" in args:
##            return Texte_transformation_generique.style(self, "angle") + 180*self.__rotation._Rotation__angle/math.pi
##        return Texte_transformation_generique.style(self, *args, **kw)

################################################################################


class Texte_translation(Texte_transformation_generique):
    u"""Une image d'un texte par translation.

    Texte construit à partir d'un autre via une translation d'angle et de centre donné."""

    texte = __texte = Argument("Texte_generique")
    translation = __translation = Argument("Translation")

    def __init__(self, texte, translation, **styles):
        self.__texte = texte = Ref(texte)
        self.__translation = translation = Ref(translation)
        Texte_transformation_generique.__init__(self, texte, translation, **styles)

    def _get_coordonnees(self):
        return (self.__texte.x + self.__translation._Translation__vecteur.x,
                self.__texte.y + self.__translation._Translation__vecteur.y)

################################################################################


class Texte_homothetie(Texte_transformation_generique):
    u"""Une image d'un texte par homothetie.

    Texte construit à partir d'un autre via une homothetie d'angle et de centre donné."""

    texte = __texte = Argument("Texte_generique")
    homothetie = __homothetie = Argument("Homothetie")

    def __init__(self, texte, homothetie, **styles):
        self.__texte = texte = Ref(texte)
        self.__homothetie = homothetie = Ref(homothetie)
        Texte_transformation_generique.__init__(self, texte, homothetie, **styles)

    def _get_coordonnees(self):
        x0, y0 = self.__homothetie.centre.coordonnees
        xA, yA = self.__texte.coordonnees
        k = self.__homothetie._Homothetie__rapport
        return x0 + k*(xA-x0), y0 + k*(yA-y0)

################################################################################


class Texte_reflexion(Texte_transformation_generique):
    u"""Une image d'un texte par reflexion.

    Texte construit à partir d'un autre via une reflexion d'angle et de centre donné."""

    texte = __texte = Argument("Texte_generique")
    reflexion = __reflexion = Argument("Reflexion")

    def __init__(self, texte, reflexion, **styles):
        self.__texte = texte = Ref(texte)
        self.__reflexion = reflexion = Ref(reflexion)
        Texte_transformation_generique.__init__(self, texte, reflexion, **styles)

    def _get_coordonnees(self):
        x0, y0 = self.__reflexion._Reflexion__droite._Droite_generique__point1
        x1, y1 = self.__reflexion._Reflexion__droite._Droite_generique__point2
        x, y = self.__texte
        z = x1 - x0 + (y1 - y0)*1j
        M = (x - x0 + (y0 - y)*1j)*z/z.conjugate() + x0 + y0*1j
        return M.real, M.imag
