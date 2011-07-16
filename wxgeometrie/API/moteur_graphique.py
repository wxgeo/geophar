# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

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

from itertools import chain
from operator import attrgetter
from string import ascii_lowercase

from matplotlib.colors import colorConverter
from matplotlib.transforms import Bbox
from matplotlib.backends.backend_wxagg import FigureCanvasAgg
from matplotlib.lines import Line2D
from matplotlib.collections import LineCollection
from matplotlib.patches import Polygon, Circle, FancyArrowPatch
from matplotlib.text import Text
from matplotlib.axes import Axes
from numpy import array, arange, concatenate, cos as ncos, sin as nsin
from math import cos, sin, atan2, pi, hypot, sqrt, atan

from ..pylib import fullrange, is_in, uu, warning, print_error, tex
from .. import param



class LigneDecoree(LineCollection):
    taille = NotImplemented

    def __init__(self, canvas, **kw):
        LineCollection.__init__(self, ())
        self.canvas = canvas
        if kw:
            self.set(**kw)

    def set(self, **kw):
        maj = kw.pop('maj', True)
        for nom in self._parametres:
            if kw.has_key(nom):
                setattr(self, nom, kw.pop(nom))
        if kw:
            LineCollection.set(self, **kw)
        if maj:
            self._maj_data()



class FlecheGenerique(LigneDecoree):
    angle = 60
    taille = 10
    double = False
    position = 1
    angle = 60

    def _maj(self, lignes):
        self.set_segments(lignes)
        # Le style de ligne (pointillés, etc.) ne doit pas s'appliquer
        # aux décorations (pointes de flêches, etc.)
        ls = self.get_linestyles()[0]
        self.set_linestyles([ls, '-', '-'])

    def _pointe(self, xy, dxdy):
        a = self.angle*pi/360 # angle/2, puis degrés -> radians
        taille = self.taille
        #                                    M +
        #                                 C     \
        # Schéma:         A +--------------+-----+ B    --> direction
        #                                       /
        #                                    N +
        # On calcule les coordonnées de C, puis par rotation autour de B, celles de M et N.
        xB, yB = self.canvas.coo2pix(*xy)
        dpx, dpy = self.canvas.dcoo2pix(*dxdy)
        alpha = atan2(dpy, dpx)
        xM = xB + taille*cos(alpha - a)
        yM = yB + taille*sin(alpha - a)
        xN = xB + taille*cos(alpha + a)
        yN = yB + taille*sin(alpha + a)
        return self.canvas.pix2coo((xM, xB, xN), (yM, yB, yN))



class Fleche(FlecheGenerique):
    _parametres = ('xy0', 'xy1', 'taille', 'double', 'position', 'angle')
    xy0 = (0, 0)
    xy1 = (1, 1)

    def __init__(self, canvas, **kw):
        u"""Une flêche (éventuellement double).

        En plus des styles de matplotlib.collections.LineCollection,
        les styles suivants sont définis:
        - taille: la longueur de la pointe (en pixels) ;
        - double: flêche double ou non ;
        - position: position (entre 0 et 1) de la pointe sur la flêche.
          ex: 1 pour l'extrémité finale, 0.5 pour le milieu, 0 pour le début.
        - angle: l'ouverture de la pointe (en degrés)
        - xy0: début de la flêche (tuple)
        - xy1: fin de la flêche (tuple)
        """
        FlecheGenerique.__init__(self, canvas, **kw)

    def _maj_data(self):
        xy0 = array(self.xy0)
        xy1 = array(self.xy1)
        lignes = [(xy0, xy1)]
        k = self.position
        dxdy = xy1 - xy0
        lignes.append(zip(*self._pointe((1 - k)*xy0 + k*xy1, -dxdy)))
        if self.double:
            lignes.append(zip(*self._pointe(k*xy0 + (1 - k)*xy1, dxdy)))
        self._maj(lignes)



class FlecheCourbe(FlecheGenerique):
    u"""Une flêche (éventuellement double) en forme d'arc de cercle.

    En plus des styles de matplotlib.collections.LineCollection,
    les styles suivants sont définis:
    - taille: la longueur de la pointe (en pixels) ;
    - double: flêche double ou non ;
    - position: position (entre 0 et 1) de la pointe sur la flêche.
      ex: 1 pour l'extrémité finale, 0.5 pour le milieu, 0 pour le début.
    - angle: l'ouverture de la pointe (en degrés) ;
    - intervalle: angle de début et de fin de l'arc (radians) ;
    - centre: centre du cercle contenant l'arc ;
    - rayon: rayon du cercle contenant l'arc ;
    - sens: orientation de l'arc (1 ou -1).
    """

    intervalle = (0, pi)
    centre = (0, 0)
    sens = 1
    rayon = 1
    _parametres = ('taille', 'double', 'position', 'angle', 'intervalle',
                   'centre', 'rayon', 'sens')

    def _maj_data(self):
        x, y = self.centre
        r = self.rayon
        a, b = self.intervalle
        t = fullrange(a, b, self.canvas.pas())
        lignes = [zip(x + r*ncos(t), y + r*nsin(t))]

        k = self.position
        sens = self.sens
        if sens == -1:
            a, b = b, a
        c = k*b + (1 - k)*a
        # Point de l'arc
        x0 = x + r*cos(c)
        y0 = y + r*sin(c)
        # Vecteur normal au rayon
        dxdy = ((y0 - y, x - x0) if sens == 1 else (y - y0, x0 - x))
        lignes.append(zip(*self._pointe((x0, y0), dxdy)))

        if self.double:
            c = k*a + (1 - k)*b
            # Point de l'arc
            x0 = x + r*cos(c)
            y0 = y + r*sin(c)
            # Vecteur normal au rayon
            dxdy = ((y - y0, x0 - x) if sens == 1 else (y0 - y, x - x0))
            lignes.append(zip(*self._pointe((x0, y0), dxdy)))

        self._maj(lignes)



class Codage(LigneDecoree):
    u'''Objet graphique servant à coder les segments et arcs de même longueur.

    Paramètres:
    - taille: taille du symbole (en pixels).
    - angle: angle relatif au segment, en degrés, pour les symboles / et X.
    - position: position du symbole (couple de coordonnées).
    - direction: couple (dx, dy) donnant l'orientation du segment.
      Ce couple est exprimé en coordonnées (et non en pixels).
    - marge: si la longueur en pixels correspondant à (dx, dy) est inférieure
      à la marge + la taille du codage, le codage n'est pas affiché.
    '''
    style = '/'
    taille = 10
    position = (0, 0)
    direction = (1, 0)
    marge = 0
    angle = 60
    _parametres = ('style', 'taille', 'position', 'direction', 'angle')

    def set(self, **kw):
        pixel = kw.pop('pixel', False)
        if 'position' in kw:
            pos = kw.pop('position')
            self.position = (pos if pixel else self.canvas.coo2pix(*pos))
        if 'direction' in kw:
            dir = kw.pop('direction')
            self.direction = (dir if pixel else self.canvas.dcoo2pix(*dir))
            self.hyp = hypot(*self.direction)
        LigneDecoree.set(self, **kw)

    def _maj_data(self):
        self.set_segments(self._codage())

    def _codage(self):
        lignes = []
        style = self.style

        if style and self.taille:
            if style == 'o':
                # On vérifie qu'il y a assez de place sur le segment pour afficher le cercle
                if self.hyp > self.taille + self.marge:
                    x, y = self.position
                    t = fullrange(0, 2*pi, 2./self.taille)
                    r = .7*self.taille
                    lignes.append(zip(*self.canvas.pix2coo(x + r*ncos(t), y + r*nsin(t))))
            elif style.count('/') == len(style):
                lignes.extend(self._oblique(self.position, self.direction, n=len(style)))
            elif style.count('|') == len(style):
                lignes.extend(self._oblique(self.position, self.direction, n=len(style), angle=pi/2))
            elif style.count('\\') == len(style):
                lignes.extend(self._oblique(self.position, self.direction, n=len(style), sens=-1))
            elif style in ('x', 'X'):
                lignes.extend(self._oblique(self.position, self.direction))
                lignes.extend(self._oblique(self.position, self.direction, sens=-1))
        return lignes

    def _oblique(self, xy, dxdy, n=1, sens=1, angle=None):
        u'''Retourne les coordonnées de n barres obliques, à la position xy.

        dxdy définit l'orientation des barres.
        S'il y a plusieurs barres, elles seront espacées de 1 épaisseur de ligne.
        '''
        a = (sens*self.angle*pi/180 if angle is None else angle)# degrés -> radians
        r = self.taille
        #                              + M
        #                           I /
        # Schéma:         A +--------+--------+ B    --> direction
        #                           /
        #                        N +
        # On calcule les coordonnées de C, puis par rotation autour de B, celles de M et N.
        dx, dy = dxdy
        lw = self.get_linewidth()[0]
        # S'il n'y a pas assez d'espace sur le segment, on n'affiche pas le codage.
        # TODO: affiner l'algorithme (pour l'instant, on fait comme si les lignes
        # étaient verticales, et non obliques).
        if self.hyp < self.marge + lw*(2*n + 2):
            return []
        alpha = atan2(dy, dx)
        xI, yI = xy
        xM = xI + r*cos(alpha - a)
        yM = yI + r*sin(alpha - a)
        xN = 2*xI - xM
        yN = 2*yI - yM
        obliques = []
        xu = dx/self.hyp
        yu = dy/self.hyp
        for i in xrange(-n + 1, n, 2):
            k = (.5*lw + 1.5)*i
            M = self.canvas.pix2coo(xM + k*xu, yM + k*yu)
            N = self.canvas.pix2coo(xN + k*xu, yN + k*yu)
            obliques.append((M, N))
        return obliques



class Angle(Polygon):
    _parametres = ('intervalle', 'style', 'taille', 'rayon', 'angle', 'position')

    def __init__(self, canvas, **kw):
        Polygon.__init__(self, ((0,0),))
        self.canvas = canvas
        if kw:
            self.set(**kw)

    def set(self, **kw):
        maj = kw.pop('maj', True)
        for nom in self._parametres:
            if kw.has_key(nom):
                setattr(self, nom, kw.pop(nom))
        if kw:
            Polygon.set(self, **kw)
        if maj:
            self._maj_data()

    def _maj_data(self):
        xy = [self.position]
        x0, y0 = self.P = self.canvas.coo2pix(*self.position)
        a, b = self.intervalle
        t = fullrange(a, b, .3*(b - a)/self.taille)

        if self.style == '^':
            r = self.rayon
            #    P     M       Angle droit au point P(x0, y0)
            #    +-----+-------
            #    |     |
            #    |     |
            #  N +-----+ I     On a donc PM-> + PN-> = PI->
            #    |             D'où "I = M + N - P"
            #    |
            M = x0 + .5*r*cos(a), y0 + .5*r*sin(a)
            N = x0 + .5*r*cos(b), y0 + .5*r*sin(b)
            I = M[0] + N[0] - x0, M[1] + N[1] - y0
            # Pixels -> coordonnées
            xy.append(self.canvas.pix2coo(*M))
            xy.append(self.canvas.pix2coo(*I))
            xy.append(self.canvas.pix2coo(*N))
        else:
            # cost et sint sont mis en cache pour être réutilisés par CodageAngle()
            self.cost = ncos(t)
            self.sint = nsin(t)
            xy.extend(self.arc_angle(i=max(0, self.style.count(')') - 1)))
        self.xy = xy

    def arc_angle(self, i=0):
        r = self.rayon
        x0, y0 = self.P
        return zip(*self.canvas.pix2coo(x0 + (r - 3*i)*self.cost, y0 + (r - 3*i)*self.sint))



class CodageAngle(Codage):
    u'''Objet graphique servant à coder des angles de même mesure.

    L'objet CodageAngle doit être associé à un objet graphique Angle préexistant.
    Il en partage les propriétés.
    '''
    def __init__(self, canvas, angle_associe, **kw):
        self.angle_associe = angle_associe
        Codage.__init__(self, canvas, **kw)

    def _maj_data(self):
        lignes = [self.angle_associe.xy[1:]]
        a, b = self.angle_associe.intervalle
        r = self.angle_associe.rayon
        x0, y0 = self.angle_associe.P # pixels
        c = .5*(a + b)
        self.set(direction=(.5*r*(cos(b) - cos(a)), .5*r*(sin(b) - sin(a))),
                 position=(x0 + r*cos(c), y0 + r*sin(c)),
                 taille=.8*self.angle_associe.taille,
                 angle=self.angle_associe.angle,
                 style=self.angle_associe.style.replace('/', '|'), # patch temporaire
                 maj=False,
                 pixel=True,
                 )
        n = self.style.count(')')
        if n > 1:
            for i in xrange(0, n - 1):
                lignes.append(self.angle_associe.arc_angle(i=i))
        lignes.extend(self._codage())
        self.set_segments(lignes)



class ZoomArtistes(object):
    def __init__(self, axes, zoom_texte, zoom_ligne):
        self.zoom_texte = zoom_texte
        self.zoom_ligne = zoom_ligne
        self.size = {}
        self.linewidth = {}
        self.markersize = {}
        self.markeredgewidth = {}
        self.taille = {}
        self.rayon = {}
        self.artistes = list(chain(axes.artists, axes.patches, axes.lines, axes.texts, axes.tables, axes.collections))

    def __enter__(self):
        self.regler_textes = abs(self.zoom_texte - 1) > 0.05
        self.regler_lignes = abs(self.zoom_ligne - 1) > 0.05
        if self.regler_textes or self.regler_lignes:
            for artiste in self.artistes:
                if artiste._visible:
                    ID = id(artiste)
                    if self.regler_textes:
                         if isinstance(artiste, Text):
                            size = self.size[ID] = artiste.get_size()
                            artiste.set_size(size*self.zoom_texte)
                    if self.regler_lignes:
                        if isinstance(artiste, Line2D):
                            lw = self.linewidth[ID] = artiste.get_linewidth()
                            artiste.set_linewidth(lw*self.zoom_ligne)
                            ms = self.markersize[ID] = artiste.get_markersize()
                            artiste.set_markersize(ms*self.zoom_ligne)
                            mw = self.markeredgewidth[ID] = artiste.get_markeredgewidth()
                            artiste.set_markeredgewidth(mw*self.zoom_ligne)
                        elif isinstance(artiste, LineCollection):
                            lws = self.linewidth[ID] = artiste.get_linewidth()
                            artiste.set_linewidth(tuple(lw*self.zoom_ligne for lw in lws))
                            if isinstance(artiste, CodageAngle):
                                angle = artiste.angle_associe
                                taille = self.taille[ID] = angle.taille
                                rayon = self.rayon[ID] = angle.rayon
                                angle.set(taille=self.zoom_ligne*taille,
                                        rayon=self.zoom_ligne*rayon)
                                artiste._maj_data()
                            elif isinstance(artiste, LigneDecoree):
                                taille = self.taille[ID] = artiste.taille
                                artiste.set(taille=self.zoom_ligne*taille)
        return self.artistes

    def __exit__(self, type, value, traceback):
        if self.regler_textes or self.regler_lignes:
            for artiste in self.artistes:
                if artiste._visible:
                    ID = id(artiste)
                    if self.regler_textes:
                        if isinstance(artiste, Text):
                            artiste.set_size(self.size[ID])
                    if self.regler_lignes:
                        if isinstance(artiste, Line2D):
                            artiste.set_linewidth(self.linewidth[ID])
                            artiste.set_markersize(self.markersize[ID])
                            artiste.set_markeredgewidth(self.markeredgewidth[ID])
                        elif isinstance(artiste, LineCollection):
                            artiste.set_linewidth(self.linewidth[ID])
                            if isinstance(artiste, CodageAngle):
                                angle = artiste.angle_associe
                                angle.set(taille=self.taille[ID],
                                        rayon=self.rayon[ID])
                                artiste._maj_data()
                            elif isinstance(artiste, LigneDecoree):
                                artiste.set(taille=self.taille[ID])


class CollecterArtistes(object):
    def __init__(self, moteur_graphique):
        self.moteur_graphique = moteur_graphique

    def __enter__(self):
        m = self.moteur_graphique
        # On reréférence tous les artistes.
        self.dict_artistes = m._effacer_artistes()
        m.canvas._affiche_module()
        m._dessine_axes()
        artistes = m.canvas.feuille_actuelle.lister_figures()[0]
        m.axes.artists.extend(artistes)

    def __exit__(self, type, value, traceback):
        m = self.moteur_graphique
        # On remet la liste des artistes dans son état d'origine (vide en général)
        m._restaurer_artistes(self.dict_artistes)


class AjusterEchelle(object):
    def __init__(self, moteur_graphique, echelle):
        self.moteur_graphique = moteur_graphique
        self.echelle = echelle

    def __enter__(self):
        if self.echelle is not None:
            m = self.moteur_graphique
            xe, ye = self.echelle
            xmin, xmax, ymin, ymax = m.canvas.fenetre
            l, h = m.canvas.dimensions_fenetre
            # Conversion en inches : 1 inch = 2.54 cm
            x = xe*l/2.54
            y = ye*h/2.54
            self.taille_precedente = tuple(m.canvas.figure.get_size_inches()) # faire une copie !!
            m.canvas.figure.set_size_inches(x, y)
            # on redessine à cause du changement d'échelle (le ratio a pu être modifié)
            if m.canvas.dimensions is None:
                m.canvas._dimensions = 850*xe, 850*h/l*ye
            else:
                L, H = m.canvas.dimensions
                # on conserve la plus grande des dimensions
                if H < L:
                    m.canvas._dimensions = L, L*h/l
                else:
                    m.canvas._dimensions = H*l/h, H
            m.canvas.feuille_actuelle._rafraichir_figures()
            m.dessiner(rafraichir_axes = True)

    def __exit__(self, type, value, traceback):
        if self.echelle is not None:
            m = self.moteur_graphique
            m.canvas._dimensions = None
            m.canvas.feuille_actuelle._rafraichir_figures()
            m.dessiner(rafraichir_axes = True)
            # On remet la figure dans son état d'origine
            m.canvas.figure.set_size_inches(self.taille_precedente)



class Moteur_graphique(object):
    def __init__(self, canvas):
        self.canvas = canvas
        self._dernier_objet_deplace = None
        self.axes = self.canvas.axes
        self._effacer_artistes()
        # Buffer contenant la dernière image.
        self._dernier_dessin = None

#   +---------------------+
#   | Fonctions de dessin |
#   +---------------------+

    @property
    def zoom_ligne(self):
        return self.canvas.zoom_ligne

    @property
    def zoom_texte(self):
        return self.canvas.zoom_texte

    def _ajouter_objet(self, artiste):
        self.axes.add_artist(artiste)

    def _ajouter_objets(self, liste_artistes):
        for artiste in liste_artistes:
            self.axes.add_artist(artiste)

    def ajouter(self, artiste):
        u"""Ajoute un artiste (objet graphique de matplotlib) à dessiner.

        NB: 'artiste' peut aussi être une liste d'artistes, ou une liste de listes..."""
        if isinstance(artiste, (list, tuple)):
            for elt in artiste:
                self.ajouter(elt)
        else:
            self._ajouter_objet(artiste)

    def _temp_warning_color(self, kw):
        u"À supprimer après quelques temps (01/05/2011)."
        if 'couleur' in kw:
            kw['color'] = kw.pop('couleur')
            warning("Utiliser desormais 'color' au lieu de 'couleur'.", level=1)


    def ligne(self, x = (0, 1), y = (1, 0), pixel = False, **kw):
        assert isinstance(pixel, bool), str(type(pixel)) # Changement d'API
        self._temp_warning_color(kw)
        if pixel:
            x, y = self.canvas.pix2coo(x, y)
#        if self.canvas.transformation is not None:
#            x, y = zip(*(zip(x, y)*self.canvas.transformation).array)
        ligne = Line2D(x, y, **kw)
        return ligne

    def ajouter_ligne(self, x = (0, 1), y = (1, 0), color = 'b', pixel = False, **kw):
        self._ajouter_objet(self.ligne(x, y, pixel, color=color, **kw))


    def polygone(self, x = (0, 1, 1, 0), y = (1, 0, 0, 1), pixel = False, **kw):
        self._temp_warning_color(kw)
        if pixel:
            x, y = self.canvas.pix2coo(x, y)
        polygone = Polygon(zip(x, y), **kw)
#        if self.canvas.transformation is not None:
#            x, y = zip(*(zip(x, y)*self.canvas.transformation).array)
        return polygone

    def ajouter_polygone(self, x = (0, 1, 1, 0), y = (1, 0, 0, 1), facecolor = 'b', pixel = False, **kw):
##        if kw.pop('color', None):
##            warning("Utiliser desormais 'facecolor' ou 'edgecolor' au lieu de 'couleur'.")
##            facecolor = color
        self._ajouter_objet(self.polygone(x, y, pixel, facecolor=facecolor, **kw))


    def texte(self, x=0, y=0, txt=u'hello !', pixel=False, **kw):
        if pixel:
            x, y = self.canvas.pix2coo(x, y)
        if not isinstance(txt, unicode):
            txt = unicode(txt, param.encodage)
        kw.setdefault('family', 'serif')
        texte = Text(x, y, txt, **kw)
        texte.figure = self.canvas.figure # texte must have access to figure.dpi
#        if self.canvas.transformation is not None:
#            x, y = ((x, y)*self.canvas.transformation).array[0]
        return texte

    def ajouter_texte(self, x=0, y=0, txt=u'hello !', pixel=False, **kw):
        self._ajouter_objet(self.texte(x, y, txt, pixel, **kw))


    def arc(self, x, y, vecteur, **kw):
        u"""Affiche un petit demi-cercle d'orientation choisie.

        Par ex, pour le vecteur (1,0), ie. ->, l'arc est orienté comme ceci: (
        Pour le vecteur (-1,0), ie. <-, l'arc est orienté comme ceci: ).
        On travaille sur les pixels pour faire de la trigonometrie plus simplement
        (le repere devient ainsi orthonorme)"""
        self._temp_warning_color(kw)
        vecteur = self.canvas.dcoo2pix(*vecteur)
        if vecteur[0] == 0:
            if vecteur[1] > 0:
                angle = pi/2
            else:
                angle = -pi/2
        else:
            angle = atan(vecteur[1]/vecteur[0])
            if vecteur[0] < 0:
                angle += pi
        # donne l'angle d'incidence à l'extrémité
        t = arange(angle - pi/2, angle + pi/2, 0.05)
        R = self.canvas.taille["("]*self.zoom_ligne

        x, y = self.canvas.coo2pix(x, y)
        return self.ligne(x + R*(ncos(t) - cos(angle)),
                          y + R*(nsin(t) - sin(angle)),
                          pixel=True, **kw)

    def ajouter_arc(self, x, y, vecteur, color='k', **kw):
        self._ajouter_objet(self.arc(x, y, vecteur, color, **kw))



    def point(self, x, y, plein=True, **kw):
        u"Un petit cercle, vide ou plein."
        assert isinstance(plein, bool), str(type(plein)) # Changement d'API
        self._temp_warning_color(kw)
        couleur = kw.pop('color', 'k')
        kw.setdefault('zorder', 2.1)
        kw.setdefault('markeredgecolor', couleur)
        kw.setdefault('markerfacecolor', couleur if plein else 'w')
        kw.setdefault('markeredgewidth', 1)
        kw.setdefault('markersize', 2*self.canvas.taille["o"])
        kw.setdefault('marker', 'o')
        return self.ligne([x], [y], **kw)
        # Le zorder doit être supérieur à celui d'une courbe (2 par défaut),
        # et la largeur du trait doit être celle d'une courbe (1 par défaut).

    def ajouter_point(self, x, y, plein=True, **kw):
        self._ajouter_objet(self.point(x, y, plein, **kw))


#    def _fleche_matplotlib(self, x0=0, y0=0, x1=1, y1=1, **kw):
#        kw.setdefault(mutation_scale=25)
#        arrow = FancyArrowPatch((x0, y0), (x1, y1), **kw)
#        # cf. matplotlib.patches.ArrowStyle.get_styles() pour les
#        # styles de flêches.
#        # Changer coord. avec FancyArrowPatch.set_position().
#        # FIXME: il n'y a aucun moyen de changer la position de la flêche
#        # sur la ligne (au milieu, au début, au bout...)
#        return arrow

    def fleche(self, xy0=(0, 0), xy1=(1, 1), **kw):
        return Fleche(xy0=xy0, xy1=xy1, canvas=self.canvas, **kw)

    def ajouter_fleche(self, x0=0, y0=0, x1=1, y1=1, **kw):
        self._ajouter_objet(self.fleche(x0, y0, x1, y1, **kw))

    def fleche_courbe(self, **kw):
        return FlecheCourbe(canvas=self.canvas, **kw)

    def ajouter_fleche_courbe(self, **kw):
        self._ajouter_objet(self.fleche_courbe(**kw))

    def codage(self, **kw):
        return Codage(canvas=self.canvas, **kw)

    def ajouter_codage(self, **kw):
        self._ajouter_objet(self.codage(**kw))

    def cercle(self, xy=(0, 0), r=1, **kw):
        circle = Circle(xy, r, **kw)
        return circle

    def ajouter_cercle(self, xy=(0, 0), r=1, **kw):
        self._ajouter_objet(self.cercle(xy, r, **kw))

    def angle(self, **kw):
        return Angle(canvas=self.canvas, **kw)

    def ajouter_angle(self, **kw):
        self._ajouter_objet(self.angle(**kw))

    def codage_angle(self, **kw):
        return CodageAngle(canvas=self.canvas, **kw)

    def ajouter_codage_angle(self, **kw):
        self._ajouter_objet(self.codage_angle(**kw))





#   +------------------------+
#   | Gestion de l'affichage |
#   +------------------------+


    def _creer_arriere_plan(self, rafraichir_axes):
        if rafraichir_axes:
            dict_artistes = self._effacer_artistes()
            self.canvas._affiche_module()
            self._dessine_axes()
            # Les axes et légendes de matplotlib ne conviennent pas, on les désactive.
            self.axes.legend_ = None
            self.axes.axison = False
            # Synchronisation de la fenêtre de matplotlib avec celle de la feuille
            self._regler_fenetre()
            # Attention, la synchronisation de la fenêtre doit avoir lieu :
            # - APRÈS self.canvas._affiche_module(), qui peut encore modifier la fenêtre
            # - avant FigureCanvasAgg.draw(), qui dessine la figure
            with ZoomArtistes(self.axes, self.zoom_texte, self.zoom_ligne):
                FigureCanvasAgg.draw(self.canvas)
##            self.canvas.draw(repaint = False)
##            self._dessiner_artistes()
            self._mise_en_cache_axes = self._en_cache()
            # _artistes_repere sert pour déboguer. Cf. '.infos()'
            self._artistes_repere = self._restaurer_artistes(dict_artistes)
        else:
            self._restaurer(self._mise_en_cache_axes)


    def _regler_fenetre(self):
        xmin, xmax, ymin, ymax = self.canvas.fenetre
        self.axes.viewLim.set_points(array([[xmin, ymin], [xmax, ymax]]))


    def dessiner(self, dessin_temporaire = False, rafraichir_axes = False):
        # Affichage bloqué
        if self.canvas.affichage_gele:
            return
##        print 'rafraichissement'

        # Quand un objet est déplacé, on optimise en ne redessinant
        # que l'objet, et ce qui en dépend.
        objet_deplace = self.canvas.feuille_actuelle._objet_deplace

        if dessin_temporaire:
            self._restaurer(self._dernier_dessin)
        else:
            self._objets_fixes, self._objets_mobiles = self.canvas.feuille_actuelle.lister_figures()
            if objet_deplace is None or rafraichir_axes:
                # Cas par défaut : on dessine tout.
                self._creer_arriere_plan(rafraichir_axes)
                self._ajouter_objets(self._objets_fixes)
            elif objet_deplace is self._dernier_objet_deplace:
                # Un cache spécifique existe déjà : on l'utilise.
##                print "Optimisation."
                self._restaurer(self._mise_en_cache_objets_fixes)
            else:
                # On génère un cache (spécifique à l'objet déplacé).
                self._creer_arriere_plan(rafraichir_axes)
                dict_artistes = self._effacer_artistes()
                self._ajouter_objets(self._objets_fixes)
                self._dessiner_artistes()
                self._mise_en_cache_objets_fixes = self._en_cache()
                self._restaurer_artistes(dict_artistes)
            self._ajouter_objets(self._objets_mobiles)
            # Résumé du bloc de code précédent :
            # Les objets fixes ne doivent pas être redessinés,
            # mais restitués à partir d'un cache.
            # On génère le cache la première fois que objet_deplace is not None
            # et on utilise le cache les autres fois si objet_deplace
            # correspond toujours au même objet.

        # On dessine dans le buffer
        self._dessiner_artistes()
        # Affichage proprement dit (copie du buffer à l'écran)
        if not self.canvas.affichage_gele_en_apparence:
            self.canvas.blit()
        # Garde en mémoire l'affichage pour éviter de redessiner la fenêtre
        # dans certains cas (fenêtre masquée, etc.)
        if not dessin_temporaire:
            self._dernier_dessin = self._en_cache()
        self._dernier_objet_deplace = objet_deplace
        self.canvas.feuille_actuelle._objet_deplace = None
        # _artistes_dessin sert pour le débogage
        self._artistes_dessin = self._effacer_artistes()


    def _convertir_zone(self, zone):
        u"Conversion de la zone: coordonnées -> inches"
        x0, x1, y0, y1 = zone
        l, h = self.canvas.figure.get_size_inches()
        fenetre = self.canvas.fenetre
        def coo2inches(x, y):
            return (l*(x - fenetre[0])/(fenetre[1] - fenetre[0]),
                    h*(y - fenetre[2])/(fenetre[3] - fenetre[2]))

        x0, y0 = coo2inches(x0, y0)
        x1, y1 = coo2inches(x1, y1)
        x0, x1 = max(0, min(x0, x1)), min(l, max(x0, x1))
        y0, y1 = max(0, min(y0, y1)), min(h, max(y0, y1))

        if x1 <= x0 or y1 <= y0:
            raise RuntimeError, "Erreur: image de dimensions nulles !"
        return Bbox(((x0, y0), (x1, y1)))


    def exporter(self, nom, dpi = None, zone = None, echelle = None):
        u"Exporter la figure."
        with self.canvas.geler_affichage(seulement_en_apparence = True, actualiser = False):
            # (Nota: le réglage de la fenêtre ne sert en fait qu'en l'absence de GUI.)
            self._regler_fenetre()
            # NB: ajuster l'échelle *avant* de convertir la zone
            with AjusterEchelle(self, echelle):
                if zone:
                    zone = self._convertir_zone(zone)
                with CollecterArtistes(self):
                    with ZoomArtistes(self.axes, self.zoom_texte, self.zoom_ligne):
                        # Export proprement dit:
                        self.canvas.figure.savefig(nom, dpi = dpi, bbox_inches = zone)


    def exporter_tikz(self, chiffres_significatifs = 4):
        conv_tikz = ConvertisseurTikz(cs = chiffres_significatifs)

        code = '\\begin{tikzpicture}\n'
        #TODO: régler fenêtre d'affichage
        with CollecterArtistes(self):
            code += '\n'.join(conv_tikz.convertir(artiste) for artiste in self.axes.artists)
        code += '\n\\end{tikzpicture}'
        return code


    def restaurer_dessin(self):
        u'''Restaure le dernier dessin.'''
        self._restaurer(self._dernier_dessin)
        self.canvas.blit()


    def _dico_artistes(self):
        dico = {}
        for rubrique in ("lines", "patches", "texts", "tables", "artists", "images", "collections"):
            dico[rubrique] = getattr(self.axes, rubrique)
        return dico


    def _effacer_artistes(self):
        u"Supprime tous les artistes (objets graphiques de matplotlib)."
        dico = self._dico_artistes()
        self.axes.artists = []
        self.axes.lines = []
        self.axes.patches = []
        self.axes.texts = []
        self.axes.tables = []
        self.axes.images = []
        self.axes.collections = []  # collection.Collection instances
        return dico


    def _restaurer_artistes(self, dictionnaire):
        u"Restaure les artistes précédemment supprimés."
        dico = self._dico_artistes()
        self.axes.__dict__.update(dictionnaire)
        return dico


    def _dessiner_artistes(self):
        with ZoomArtistes(self.axes, self.zoom_texte, self.zoom_ligne) as artistes:
            artistes.sort(key=attrgetter('zorder'))
            for artiste in artistes:
                if artiste._visible:
                    try:
                        self.axes.draw_artist(artiste)
                    except:
                        print_error()


    def _en_cache(self):
        return self.canvas.copy_from_bbox(self.axes.bbox)


    def _restaurer(self, buffer):
        if buffer is not None:
            self.canvas.restore_region(buffer)


    def _dessine_axe(self, num = 0, nbr_axes = 1):
        u"Dessine l'axe des abscisses (num = 0) ou des ordonnées (num = 1)."

        #un = nbr_axes == 1              # un seul axe
        #x = num == 0; y = not x         # axe des abscisses / des ordonnees
        #rep = self.utiliser_repere      # repere ou non
        vect = self.canvas.utiliser_repere and self.canvas.repere[1 + num] in ascii_lowercase
        # repere defini ou non par des vecteurs
        correspondance = {"b" : "bottom", "c": "center", "l": "left", "r": "right", "t": "top"}

        def f(a, b):
            return a if num == 0 else b

        signe = f(-1, 1)
        origine = self.canvas.origine_axes[1 - num]
        fenetre = self.canvas.fenetre
        repere = self.canvas.repere

        # On cree l'axe proprement dit:
        self.ajouter_ligne(f([fenetre[0], fenetre[1]], [origine, origine]), f([origine, origine], [fenetre[2], fenetre[3]]), "k")

        if self.canvas.afficher_fleches:
            # On cree la fleche au bout de l'axe:
            x, y = self.canvas.coo2pix(f(fenetre[1], origine), f(origine, fenetre[3]))
            dx, dy = .5*self.canvas.taille[">"]*self.zoom_ligne*array([f(sqrt(3), 1), f(1, sqrt(3))])
            self.ajouter_ligne([x - dx, x, x + signe*dx], [y + dy, y, y + signe*dy], "k",  pixel = True)


        # FORMAT (_origine_ et _graduation_) : [texte, x, y, alignement horizontal, alignement vertical]
        # _origine_ : infos sur l'origine de l'axe
        # _graduation_ : infos sur le 2eme point de l'axe

        ox, oy = self.canvas.origine_axes
        ux, uy = self.canvas.gradu
        # TODO: à étendre à un repère non orthogonal
        kx, ky = self.canvas.dpix2coo(1, 1)

        x, y = self.canvas.coo2pix(f(ox + ux, ox), f(oy, oy + uy))
        if self.canvas.gradu[num] and self.canvas.saturation(num) < param.saturation:
            if vect:
                self.ajouter_ligne([x - dx, x, x + signe*dx], [y + dy, y, y + signe*dy], "k", pixel = True)
            elif self.canvas.afficher_quadrillage:
                d = .5*self.canvas.taille["|"]*self.zoom_ligne
                self.ajouter_ligne([f(x, x - d), f(x, x + d)], [f(y - d, y), f(y + d, y)], "k", pixel = True)

        def str_(val):
            s = str(val)
            if s.endswith('.0'):
                s = s[:-2]
                #TODO: remplacer le point par une virgule (selon les paramètres actifs)
            return s

        if nbr_axes == 1:                   # un seul axe
            if num:                         # axe des ordonnees
                if self.canvas.utiliser_repere:    # utiliser un repere (meme origine sur chaque axe...)
                    _origine_ = [repere[0], ox - 8*kx, oy, "r", "c"]
                    if vect:                # reperage par des vecteurs
                        _graduation_ = [r"$\tt{\vec{" + repere[2] + "}}$", ox - 8*kx, oy + .5*uy, "r", "c"]
                    else:                   # reperage par des points
                        _graduation_ = [repere[2], ox - 8*kx, oy + uy, "r", "c"]
                else:                       # pas un repere
                        _origine_ = [str_(oy), ox - 8*kx, oy, "r", "c"]
                        _graduation_ = [str_(oy + uy), ox - 8*kx, oy + uy, "r", "c"]
            else:                           # axe des abscisses
                if self.canvas.utiliser_repere:    # utiliser un repere (meme origine sur chaque axe...)
                    _origine_ = [repere[0], ox, oy - 8*ky, "c", "t"]
                    if vect:                # reperage par des vecteurs
                        _graduation_ = [r"$\tt{\vec{" + repere[1] + "}}$", ox + .5*ux, oy - 8*ky, "c", "t"]
                    else:                   # reperage par des points
                        _graduation_ = [repere[1], ox + ux, oy - 8*ky, "c", "t"]
                else:                       # pas un repere
                        _origine_ = [str_(ox), ox, oy - 8*ky, "c", "t"]
                        _graduation_ = [str_(ox + ux), ox + ux, oy - 8*ky, "c", "t"]
        else:                               # 2 axes
            if num:                         # axe des ordonnees
                if self.canvas.utiliser_repere:
                    _origine_ = None
                    if vect:                # reperage par des vecteurs
                        _graduation_ = [r"\vec{" + repere[2] + "}", ox - 8*kx, oy + .5*uy, "r", "c"]
                    else:                   # reperage par des points
                        _graduation_ = [repere[2], ox - 8*kx, oy + uy, "r", "c"]
                else:                       # pas un repere
                        _origine_ = [str_(oy), ox - 8*kx, oy + 3*ky, "r", "b"]
                        _graduation_ = [str_(oy + uy), ox - 8*kx, oy + uy, "r", "b"]
            else:                           # axe des abscisses
                if self.canvas.utiliser_repere:
                    _origine_ = [repere[0], ox - 8*kx, oy - 8*ky, "r", "t"]
                    if vect:                # reperage par des vecteurs
                        _graduation_ = [r"\vec{" + repere[1] + "}", ox + .5*ux, oy - 8*ky, "c", "t"]
                    else:                   # reperage par des points
                        _graduation_ = [repere[1], ox + ux, oy - 8*ky, "c", "t"]
                else:                       # pas un repere
                        _origine_ = [str_(ox), ox + 3*kx, oy - 8*ky, "l", "t"]
                        _graduation_ = [str_(ox + ux), ox + ux, oy - 8*ky, "l", "t"]

        if _origine_ and self.canvas.gradu[num]:
            self.ajouter_texte(_origine_[1], _origine_[2], tex(_origine_[0]), \
                horizontalalignment = correspondance[_origine_[3]], \
                verticalalignment = correspondance[_origine_[4]], size = 14)

        if _graduation_ and self.canvas.gradu[num] and self.canvas.saturation(num) < param.saturation:
            self.ajouter_texte(_graduation_[1], _graduation_[2], tex(_graduation_[0]), \
                horizontalalignment = correspondance[_graduation_[3]], \
                verticalalignment = correspondance[_graduation_[4]], size = 14)




    def _quadriller(self, hauteur = 3, pas = (None, None), style = None, epaisseur = 1, couleur = "k"):
        u"""Crée des graduations ou un quadrillage (si hauteur = None).
        Si pas[0] = 0 (respectivement, pas[1] = 0), les graduations seront
        uniquement horizontales (respectivement verticales)."""

        origine = self.canvas.origine_axes
        fenetre = self.canvas.fenetre
        pas = list(pas)
        # Je n'utilise pas des listes directement, mais des tuples.
        # Ceci afin de n'avoir jamais la MEME liste.

        if hauteur == None: # quadrillage
            xmin, xmax, ymin, ymax = fenetre
            _min = ymin, xmin ; _max = ymax, xmax
            if not style:
                style = ":"
        else:               # graduations
##            _min = [origine[i] - hauteur*self.canvas.coeff(i) for i in (1, 0)] # ymin, xmin
##            _max = [origine[i] + hauteur*self.canvas.coeff(i) for i in (1, 0)] # ymax, xmax
            # ymin, xmin:
            _min = [origine[1] - self.canvas.dpix2coo(0, hauteur)[1],
                    origine[0] - self.canvas.dpix2coo(hauteur, 0)[0]]
            # ymax, xmax:
            _max = [origine[1] + self.canvas.dpix2coo(0, hauteur)[1],
                    origine[0] + self.canvas.dpix2coo(hauteur, 0)[0]]
            if not style:
                style = "-"

##        #type_ligne = couleur + style

        # Format de 'segments': [[(x0,y0), (x1,y1), ...], [...], [...], ...]
        # cf. LineCollection
        segments = []

        for n in (0, 1):
            if pas[n] == None:  pas[n] = self.canvas.gradu[n]
            pas[n] = 1.*abs(pas[n])

            # graduations sur l'axe:
            if pas[n] and self.canvas.coeff(n)/pas[n] < param.saturation:

                maxi = fenetre[2*n + 1]
                if self.canvas.afficher_axes and (n in self.canvas.liste_axes) and hauteur:
                    # les graduations qui chevauchent les fleches, c'est pas joli
                    maxi -= .7*self.canvas.taille[">"]*self.zoom_ligne*sqrt(3)*self.canvas.coeff(n)

                valeurs = concatenate((arange(origine[n], fenetre[2*n], -pas[n]), arange(origine[n] + pas[n], maxi, pas[n])))
                for val in valeurs:
                    # si on affiche le quadrillage ou les graduations sur les axes, ca fait pas net:
                    if val != origine[n] or not self.canvas.afficher_axes or not (1 - n in self.canvas.liste_axes):
                        if n:
                            segments.append([(_min[n], val), (_max[n], val)])
                        else:
                            segments.append([(val, _min[n]), (val, _max[n])])


##        m = len(segments)
##        width = m*[epaisseur]
##        color = m*[matplotlib.colors.colorConverter.to_rgba(couleur)]
        couleur = colorConverter.to_rgba(couleur)
        style_dict = {':': 'dotted', '--': 'dashed', '-.': 'dashdot', '-': 'solid'}
        style = style_dict.get(style, style)
        collection = LineCollection(segments, linewidths = epaisseur, colors = couleur,  linestyle = style)
        self.axes.add_collection(collection)




    def _dessine_axes(self):
            if self.canvas.afficher_axes:
                for axe in self.canvas.liste_axes:
                    self._dessine_axe(axe, len(self.canvas.liste_axes))

            if self.canvas.afficher_quadrillage:   # quadrillage
                for quadrillage in self.canvas.quadrillages:
                    self._quadriller(None, *quadrillage)
            elif self.canvas.afficher_axes:
                self._quadriller()   # simples graduations


#   +---------------------+
#   |  Aides au débogage  |
#   +---------------------+


    def _info_artiste(self, artiste):
        u"""Retourne des informations permettant éventuellement de
        repérer visuellement l'artiste."""
        infos = {}
        infos['parent'] = getattr(getattr(artiste, '_cree_par', None), 'info', None)
        if isinstance(artiste, Text):
            infos['text'] = artiste.get_text()
            infos['color'] = artiste.get_color()
            infos['size'] = artiste.get_size()
        elif isinstance(artiste, Line2D):
            infos['xy'] = zip(artiste.get_xdata(), artiste.get_ydata())
            if len(infos['xy']) > 1:
                infos['color'] = artiste.get_color()
            else:
                infos['edge-color'] = artiste.get_markeredgecolor()
                infos['face-color'] = artiste.get_markerfacecolor()
        elif isinstance(artiste, LineCollection):
            infos['color'] = artiste.get_color()
        elif isinstance(artiste, Polygon):
            infos['xy'] = artiste.get_verts()
            infos['edge-color'] = artiste.get_edgecolor()
            infos['face-color'] = artiste.get_edgecolor()
        infos_as_str = ', '.join([key + '=' + uu(val) for key, val in infos.iteritems()])
        return artiste.__class__.__name__ + ' (' + str(id(artiste)) + '):\n' + infos_as_str

    def infos(self):
        u"Informations utiles pour le débogage."
        print "---------------"
        print("+ Repere")
        for rubrique in self._artistes_repere:
            print " -> " + rubrique
            for artiste in self._artistes_repere[rubrique]:
                print '  * ' + self._info_artiste(artiste)
        print("+ Objet deplace ?")
        print getattr(self._dernier_objet_deplace, 'info', 'None')
        print "+ Objets fixes:"
        for artiste in self._objets_fixes:
            print '  * ' + self._info_artiste(artiste)
        print "+ Objets mobiles:"
        for artiste in self._objets_mobiles:
            print '  * ' + self._info_artiste(artiste)
        print "+ Autres artistes:"
        for rubrique in self._artistes_dessin:
            print " -> " + rubrique
            for artiste in self._artistes_dessin[rubrique]:
                if not is_in(artiste, self._objets_mobiles) \
                        and not is_in(artiste, self._objets_fixes)\
                        and not any(is_in(artiste, liste) for liste in self._artistes_repere.itervalues()):
                    print '  * ' + self._info_artiste(artiste)
        print "---------------"

    # TESTS pour débogage
    # TODO: avoir une image de référence pour comparer

    def _test(self):
        u"""Test 1.

        Barre rouge en travers reliant 2 croix (+)."""
        self.axes.viewLim.set_points(array([[0, 0], [1, 1]]))
        Axes.clear(self.canvas.axes)
        Axes.plot(self.canvas.axes, [0.1, 0.9], [0.1, 0.9], 'r+-')
        self.canvas.draw()

    def _test2(self):
        u"""Test 2.

        Barre bleue en travers. Un point vert et un rouge (croix +).
        Un point vert en forme de rond (plein).
        """
        self.axes.viewLim.set_points(array([[0, 0], [1, 1]]))
        Axes.clear(self.canvas.axes)
        pt = self.point(.5, .5, couleur="g")
        pt2 = self.ligne([.4], [.5], couleur="g")
        pt2._marker = "+"
        pt3 = self.ligne([.4], [.6], couleur="r")
        pt3.set_marker("+")
        l = self.ligne([0.1, 0.9], [0.1, 0.9], couleur="b")
        self.canvas.axes.lines.extend([pt, l, pt2, pt3])
        self.canvas.draw()

    def _test3(self):
        u"""Test les flêches de matplotlib.

        Une flêche verte, et une flêche double rouge, croisées.
        """
        self.canvas.fenetre = 0, 1, 0, 1
        #self.axes.viewLim.set_points(array([[0, 0], [1, 1]]))
        Axes.clear(self.canvas.axes)
        f1 = self.fleche((0.2, 0.2), (0.6, 0.6), double=False, color='g')
        f2 = FancyArrowPatch((0.6, 0.2), (0.2, 0.6), arrowstyle='<->', mutation_scale=25, color='r')
        #f2.set_figure(self.canvas.figure)
        #f2.set_axes(self.canvas.axes)
        #f2.set_clip_path(self.axes.patch)
        self.canvas.axes.add_artist(f2)
        #self.canvas.axes.add_patch(f2)
        #self.canvas.axes.collections.extend([f1])
        self.axes.add_collection(f1)
        self.canvas.draw()



class ConvertisseurBase(object):
    u"""Classe générique dont dérivent tous les convertisseurs d'objets matplotlib."""


    def convertir(self, obj, chiffres_significatifs = None):
        u"Appelle la méthode spécifique à l'objet matplotlib."
        return getattr(self, obj.__class__.__name__)(obj)


class ConvertisseurTikz(ConvertisseurBase):
    u"""Convertit un objet matplotlib en instruction Tikz.

    'cs': nombre de chiffres significatifs à afficher."""

    def __init__(self, fenetre, resolution = 1000):
        xmin, xmax, ymin, ymax = fenetre
        self.nx = (xmax - xmin)/resolution# number of digits for x
        self.ny = (ymax - ymin)/resolution# number of digits for y

    def Text(self, t):
        x, y = t.get_position()
        x = self._xstr(x)
        y = self._ystr(y)
        txt = t.get_text()
        pos = self._position(t)
        if pos:
            pos += ','
        chaine = self._couleur(t)
        chaine += '\\draw (%(x)s,%(y)s) node[%(pos)scolor=currentcol]{%(txt)s};' %locals()
        return chaine

    def Line2D(self, l):
        def _strc(x, y):
            x = self._xstr(x)
            y = self._ystr(y)
            return '(%(x)s,%(y)s)' %locals()
        chaine = self._couleur(l)
        ls = self._ls(l)
        if ls:
            ls += ','
        chaine += '\\draw [%(col)s] plot [smooth] coordinates {' %locals()
        chaine += ' '.join(_strc(*couple) for couple in l.get_xydata())
        return chaine + '};'

    def LineCollection(self, lc):
        _str = self._str
        chaine = ''
        return chaine

    def Polygon(self, p):
        _str = self._str
        chaine = ''
        return chaine

    def _couleur(self, obj):
        _colstr = self._colstr
        color = colorConverter.to_rgb(obj.get_color())
        #TODO: conversion incorrecte. Se documenter sur la question.
        R = _colstr(color[0])
        V = _colstr(color[1])
        B = _colstr(color[2])
        return "\\definecolor{currentcol}{rgb}{%(R)s,%(V)s,%(B)s};\n" %locals()

    _ha_tikz = {'left': 'left', 'right': 'right', 'center': ''}
    _va_tikz = {'top': 'above', 'bottom': 'below', 'center': ''}

    def _position(self, t):
        ha = self._ha_tikz[t.get_horizontalalignment()]
        va = self._va_tikz[t.get_verticalalignment()]
        return (va + ' ' + ha) if (va or ha) else ''

    def _lw(self, obj):
        lw = obj.get_linewidth()
        return "line width=%(lw)spt" %locals()

    _ls_tikz = {'--': (2, 2), '-.': (2, 2, 1, 2), ':': (1, 2)}

    def _ls(self, obj):
        ls = _ls_tikz.get(obj.get_linestyle(), None)
        if ls:
            on_off = ''
            for i, val in enumerate(ls):
                on_off += 'off' if i%2 else 'on'
                on_off += ' %(val)s pt ' %locals()
            return 'dash pattern=' + on_off
        return ''

    _mk_tikz = {'+': '+', '*': '$\\star$', '.': '$\\bullet$', 'o': '$\\circle$',
    'x': '$\\mul$', '<': '$\\blacktriangleleft$', '>': '$\\blacktriangleright',
    '^': '$\\blacktriangle', 'v': '$\\blacktriangledown'}

    def _mk(self, obj):
        pass

    def _xstr(self, val):
        return self._str(val, self.nx)

    def _ystr(self, val):
        return self._str(val, self.ny)

    def _colstr(self, val):
        return self._str(val, 1)

    def _str(self, val, n):
        val = round(val, n)
        s = str(val)
        if s.endswith('.0'):
            s = s[:-2]
        return s
