# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

##--------------------------------------#######
#                   Labels                    #
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

##from weakref import ref
from math import cos, sin, hypot, pi, acos

from .objet import Objet, Argument, Ref
from .textes import Texte_editable_generique, _get_texte, _set_texte
from .constantes import NOM
from .routines import angle_vectoriel, sign
from .points import (Glisseur_arc_cercle, Glisseur_segment, Glisseur_droite,
                     Glisseur_vecteur, Glisseur_cercle, Glisseur_demidroite,)
from .. import param
from ..pylib import property2


class Label_generique(Texte_editable_generique):
    u"""Un label (étiquette accolée à l'objet)

    Le label est crée automatiquement lors de la création de l'objet.
    Le label n'est pas un 'vrai' objet, il n'est pas enregistré sur la feuille."""

    _style_defaut = param.labels
    # Les coordonnées exactes n'ont aucun intérêt pour une étiquette.
    _utiliser_coordonnees_approchees = True

    __parent = parent = Argument(Objet)
    __texte = texte = Argument("unicode", _get_texte, _set_texte)

    def __init__(self, parent, texte='', **styles):
        self.__texte = texte = Ref(texte)
        self.__parent = parent = Ref(parent)
        Texte_editable_generique.__init__(self, texte, **styles)

    @property
    def nom(self):
        if self.feuille is not None:
            nom = self.__parent.nom
            if nom:
                return nom + '.etiquette'
        return ''

    def sauvegarder(self):
        nom = self.parent.nom
        return "%s.etiquette.texte = %s\n" \
               "%s.etiquette.style(**%s)\n" \
               % (nom, repr(self.texte), nom, repr(self.style()))

    @property2
    def nom_latex(self, val=None):
        if val:
            print('Warning: `.etiquette.nom_latex` est en lecture seule.')
        return self.__parent.nom_latex

    @property2
    def visible(self, val = None):
        if val is not None:
            assert isinstance(val, bool)
            self.style(visible = val)
        return self.style('visible') and self.parent.style('visible')

    def _get_coordonnees(self):
        raise NotImplementedError    # sera implemente differemment pour chaque type de label

    def _creer_trace(self):
        u"Pas de trace pour les étiquettes."
        pass

    def figure_perimee(self):
        # IMPORTANT:
        # il faut effacer manuellement le cache, car les coordonnées ne sont pas fonction
        # des arguments de l'étiquette.
        # (Pour les autres objets, les arguments sont encapsulés dans des objets Ref
        # qui vident eux-même le cache en cas de modification).
        self._cache.clear()
        Objet.figure_perimee(self)

    @property
    def existe(self):
        # C'est l'existence de l'objet qui détermine celle de son étiquette.
        return self.__parent.existe

    ##def _set_rayon(self, rayon, x, y):
        ##xmin, xmax, ymin, ymax = self._boite()
        ##rayon_max = param.distance_max_etiquette + hypot(xmin - xmax, ymin - ymax)/2
        ##self.style(_rayon_ = min(rayon, rayon_max))
        # TODO: nouvel algorithme:
        # 1. Chercher le point le plus proche parmi les 4 coins du texte.
        # 2. Adapter les coordonnées de ce point pour que la distance ne dépasse pas le maximum autorisé.
        # 3. En déduire les nouvelles coordonnées du point d'ancrage
        # 4. Conclure avec les nouvelles valeur de _rayon_ et _angle_

##    def _distance_boite(self, x, y):
##        xmin, xmax, ymin, ymax = self._boite()
##        d1 = hypot((x-xmin), (y-ymin))
##        d2 = hypot((x-xmax), (y-ymax))
##        d3 = hypot((x-xmin), (y-ymax))
##        d4 = hypot((x-xmax), (y-ymin))
##        return min(d1, d2, d3, d4)

    @property
    def __x(self):
        return self.coordonnees[0]

    x = __x

    @property
    def __y(self):
        return self.coordonnees[1]

    y = __y



class Label_point(Label_generique):
    u"L'étiquette d'un point."

    _style_defaut = {'mode': NOM}

    __parent = parent = Argument('Point_generique')
    __texte = texte = Argument("unicode", _get_texte, _set_texte)

    def __init__(self, parent, texte='', **styles):
        self.__texte = texte = Ref(texte)
        self.__parent = parent = Ref(parent)
        Label_generique.__init__(self, parent, texte, **styles)

    def _get_coordonnees(self):
        parent = self.parent
        r = self.style("_rayon_")
        a = self.style("_angle_")
        rx, ry = self.canvas.dpix2coo(r*cos(a), r*sin(a))
        x0, y0 = parent.xy
        return  x0 + rx, y0 - ry

    def _set_coordonnees(self, x = None, y = None):
        if x is not None:
            parent = self.parent
            rx, ry = self.canvas.dcoo2pix(x - parent.abscisse, y - parent.ordonnee)
            rayon = hypot(rx, ry)
            if rayon:
                self.style(_angle_ = acos(rx/rayon)*sign(-ry))
            # Distance maximale entre le point et son étiquette : 25 pixels.
            self.style(_rayon_ = min(rayon, 50))




###########################
# Les classes suivantes sont basées sur les classes Glisseur de geolib.


class Label_glisseur(Label_generique):
    u"""Classe mère de tous les labels utilisant un objet glisseur.

    `classe` doit contenir le type de glisseur utilisé.
    """

    glisseur = NotImplemented

    __parent = parent = Argument(Objet)
    __texte = texte = Argument("unicode", _get_texte, _set_texte)

    def __init__(self, parent, texte='', **styles):
        self.__texte = texte = Ref(texte)
        self.__parent = parent = Ref(parent)
        Label_generique.__init__(self, parent, texte, **styles)
        self._M = None

    def _get_coordonnees(self):
        if self._M is None:
            self._M = self.glisseur(self.parent, k = self.style("_k_"))
        x0, y0 =  self._M.coordonnees
        r = self.style("_rayon_")
        a = self.style("_angle_")
        rx, ry = self.canvas.dpix2coo(r*cos(a), r*sin(a));
        return  x0 + rx, y0 - ry

    def _set_coordonnees(self, x = None, y = None):
        if self._M is None:
            self._M = self.glisseur(self.__parent, k=self.style("_k_"))
        if x is not None:
            self._M.coordonnees = (x, y)
            x0, y0 = self._M.coordonnees # comme _M est un glisseur, ce n'est pas x0 et y0 en général
            self.style(_k_ = self._M.parametre)
            rx, ry = self.canvas.dcoo2pix(x - x0, y - y0)
            rayon = hypot(rx, ry)
            if rayon:
                self.style(_angle_ = acos(rx/rayon)*sign(-ry))
            self.style(_rayon_ = min(rayon, 50)) # distance maximale entre le point et son etiquette : 25 pixels



class Label_segment(Label_glisseur):
    u"""L'étiquette d'un segment."""

    glisseur = Glisseur_segment

    __parent = parent = Argument('Segment')
    __texte = texte = Argument("unicode", _get_texte, _set_texte)

    def __init__(self, parent, texte='', **styles):
        self.__texte = texte = Ref(texte)
        self.__parent = parent = Ref(parent)
        Label_glisseur.__init__(self, parent, texte, **styles)


class Label_vecteur(Label_glisseur):
    u"""L'étiquette d'un vecteur."""

    glisseur = Glisseur_vecteur

    __parent = parent = Argument('Vecteur_generique')
    __texte = texte = Argument("unicode", _get_texte, _set_texte)

    def __init__(self, parent, texte='', **styles):
        self.__texte = texte = Ref(texte)
        self.__parent = parent = Ref(parent)
        Label_glisseur.__init__(self, parent, texte, **styles)


class Label_droite(Label_glisseur):
    u"""L'étiquette d'une droite."""

    glisseur = Glisseur_droite

    __parent = parent = Argument('Droite_generique')
    __texte = texte = Argument("unicode", _get_texte, _set_texte)

    def __init__(self, parent, texte='', **styles):
        self.__texte = texte = Ref(texte)
        self.__parent = parent = Ref(parent)
        Label_glisseur.__init__(self, parent, texte, **styles)


class Label_demidroite(Label_glisseur):
    """L'étiquette d'une demi-droite."""

    glisseur = Glisseur_demidroite

    __parent = parent = Argument('Demidroite')
    __texte = texte = Argument("unicode", _get_texte, _set_texte)

    def __init__(self, parent, texte='', **styles):
        self.__texte = texte = Ref(texte)
        self.__parent = parent = Ref(parent)
        Label_glisseur.__init__(self, parent, texte, **styles)


class Label_cercle(Label_glisseur):
    """L'étiquette d'un cercle."""

    _style_defaut = {'_k_': 0}
    glisseur = Glisseur_cercle

    __parent = parent = Argument('Cercle_generique')
    __texte = texte = Argument("unicode", _get_texte, _set_texte)

    def __init__(self, parent, texte='', **styles):
        self.__texte = texte = Ref(texte)
        self.__parent = parent = Ref(parent)
        Label_glisseur.__init__(self, parent, texte, **styles)


class Label_arc_cercle(Label_glisseur):
    """L'étiquette d'un arc de cercle."""

    glisseur = Glisseur_arc_cercle

    __parent = parent = Argument('Arc_generique')
    __texte = texte = Argument("unicode", _get_texte, _set_texte)

    def __init__(self, parent, texte='', **styles):
        self.__texte = texte = Ref(texte)
        self.__parent = parent = Ref(parent)
        Label_glisseur.__init__(self, parent, texte, **styles)


#   Autres classes
#
###########################



class Label_polygone(Label_generique):
    u"L'étiquette d'un polygone."

    __parent = parent = Argument('Polygone_generique')

    __texte = texte = Argument("unicode", _get_texte, _set_texte)

    def __init__(self, parent, texte='', **styles):
        self.__texte = texte = Ref(texte)
        self.__parent = parent = Ref(parent)
        Label_generique.__init__(self, parent, texte, **styles)

    def _set_coordonnees(self, x = None, y = None):
        if x is not None:
            parent = self.__parent
            x1, x2, y1, y2 = parent._espace_vital()
            x = max(min(x, x2), x1)
            y = max(min(y, y2), y1)
            rx, ry = self.canvas.dcoo2pix(x - parent.centre.abscisse, y - parent.centre.ordonnee)
            rayon = hypot(rx, ry)
            if rayon:
                self.style(_angle_ = acos(rx/rayon)*sign(-ry))
            self.style(_rayon_ = rayon) # distance maximale entre le point et son étiquette : 25 pixels

    def _get_coordonnees(self):
        parent = self.__parent
        r = self.style("_rayon_")
        a = self.style("_angle_")
        rx, ry = self.canvas.dpix2coo(r*cos(a), r*sin(a))
        x0, y0 = parent.centre.xy
        return  x0 + rx, y0 - ry



class Label_angle(Label_generique):
    u"L'étiquette d'un angle."

    _style_defaut = {'_rayon_': param.codage["rayon"] + 10}

    __parent = parent = Argument("Angle_generique")
    __texte = texte = Argument("unicode", _get_texte, _set_texte)

    def __init__(self, parent, texte='', **styles):
        self.__texte = texte = Ref(texte)
        self.__parent = parent = Ref(parent)
        Label_generique.__init__(self, parent, texte, **styles)

    def _get_coordonnees(self):
        parent = self.parent
        r = self.style("_rayon_")
        k = self.style("_k_")
        u = self.canvas.dpix2coo(*parent._Secteur_angulaire__vecteur1)
        v = self.canvas.dpix2coo(*parent._Secteur_angulaire__vecteur2)
        i = (1, 0)
        a = angle_vectoriel(i, u)
        b = angle_vectoriel(i, v)
        if parent.sens == u"non défini" and parent._sens() < 0:
            a, b = b, a
        if b < a:
            b += 2*pi
        c = k*b + (1 - k)*a
        rx, ry = self.canvas.dpix2coo(r*cos(c), r*sin(c))
        x0, y0 = parent._Secteur_angulaire__point.xy
        return x0 + rx, y0 - ry


    def _set_coordonnees(self, x = None, y = None):
        if x is not None:
            parent = self.parent
            x0, y0 = parent.point.xy
            rx, ry = self.canvas.dcoo2pix(x - x0, y - y0)
            rayon = hypot(rx, ry)
            if rayon:
                u = self.canvas.dpix2coo(*parent._Secteur_angulaire__vecteur1)
                v = self.canvas.dpix2coo(*parent._Secteur_angulaire__vecteur2)
                i = (1, 0)
                a = angle_vectoriel(i, u)
                b = angle_vectoriel(i, v)
                if parent.sens == u"non défini" and parent._sens() < 0:
                    a, b = b, a
                c = angle_vectoriel(i, (rx, -ry))
                if a != b:
                    if b < a:
                        b += 2*pi
                    if c < a:
                        c += 2*pi
                    self.style(_k_ = (c - a)/(b - a))
            self.style(_rayon_ = min(rayon, param.codage["rayon"] + 25))
