# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                   Objets                    #
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

from random import uniform
from math import pi
from sympy import pi as PI

from .labels import Label_angle
from .objet import Objet_numerique, Objet, Ref, Argument, issympy, contexte, pi_, FILL_STYLES
from .points import Point
from .routines import nice_display, angle_vectoriel
from .variables import Variable
from .vecteurs import Vecteur_libre, Vecteur
from .. import param



class Angle_generique(Objet_numerique):
    u"""Un angle générique (en radian).

    Classe mère des angles orientés ou non."""

    _prefixe_nom = "a"

    def __init__(self, **styles):
        Objet.__init__(self, **styles)

    @property
    def radian(self):
        return self.val
    rad = radian

    @property
    def degre(self):
        if self.existe:
            return self.val*180/pi_()
    deg = degre

    @property
    def grad(self):
        if self.existe:
            return self.val*200/pi_()

    @property
    def info(self):
        unite = contexte['unite_angle']
        if unite == 'd':
            val = nice_display(self.degre) + u'\u00B0'
        elif unite == 'g':
            val = nice_display(self.grad) + " g"
        else:
            val = nice_display(self.rad)
        return self.nom_complet + u" de valeur "+ val

##    def sin(self):
##        return math.sin(self.radian)
##
##    def cos(self):
##        return math.cos(self.radian)
##
##    def tan(self):
##        return math.tan(self.radian)


##    def _changer_unite(self, unite = None):
##        u"Change l'unité de l'angle en effectuant les adaptations nécessaires."
##        if unite is not None:
##            self._recalculer = True
##            for objet in self.heritiers():
##                objet._recalculer = True
##                if objet.etiquette:
##                    objet.etiquette._recalculer = True
##            self.__unite = self._choix_unite(unite)
##        else:
##            return self.__unite

##    unite = property(_changer_unite, _changer_unite)


##    _conversion = {  "r": {"r":1., "d":180./pi, "g":200./pi},
##                    "g": {"r":pi/200., "d":180./200., "g":1.},
##                    "d": {"r":pi/180., "d":1., "g":200./180.}}
##    # utilisation: t*conversation["r"]["d"] pour convertir t de radian en degré.

    @staticmethod
    def _convertir(objet):
        unite = contexte['unite_angle']
        if isinstance(objet, basestring) and objet[-1]  == u'\u00B0':
            objet = objet[:-1]
            unite = 'd'
        if not isinstance(objet, Variable):
            objet = Variable._convertir(objet)
        return Angle_libre(objet, unite = unite)
##        raise TypeError, "%s must be of type 'Variable'" %objet

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%##
######################### REPRENDRE ICI (FIN DE TRAVAUX) ############################
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%##





class Secteur_angulaire(Angle_generique):
    u"Classe mère de tous les angles 'affichables'."

    _style_defaut = param.angles
    _affichage_depend_de_la_fenetre = True

    point = __point = Argument("Point_generique", defaut = Point)
    vecteur1 = __vecteur1 = Argument("Vecteur_generique", defaut = Vecteur_libre)
    vecteur2 = __vecteur2 = Argument("Vecteur_generique", defaut = Vecteur_libre)

    def __init__(self, point = None, vecteur1 = None, vecteur2 = None, **styles):
        self.__point = point = Ref(point)
        self.__vecteur1 = vecteur1 = Ref(vecteur1)
        self.__vecteur2 = vecteur2 = Ref(vecteur2)
        Angle_generique.__init__(self, **styles)
        self.etiquette = Label_angle(self)

    def _get_valeur(self):
        return angle_vectoriel(self.__vecteur1, self.__vecteur2)

    def _sens(self):
        x1, y1 = self.__vecteur1
        x2, y2 = self.__vecteur2
        return cmp(x1*y2 - x2*y1, 0)

    @property
    def sens(self):
        if self._sens() < 0:
            return "indirect"
        return "direct"

    def _creer_figure(self):
        codage = self.style("codage")
        niveau = self.style("niveau")
        style = self.style("style")
        if param.codage_automatique_angle_droits and not codage:
            if abs(abs(self.radian) - pi/2) < contexte['tolerance']:
                codage = "^"
        if not self._representation:
            ang = self.rendu.angle()
            self._representation = [ang, self.rendu.codage_angle(angle_associe=ang)]

        u = self.__canvas__.dcoo2pix(*self.__vecteur1)
        v = self.__canvas__.dcoo2pix(*self.__vecteur2)
        i = (1, 0)
        a = angle_vectoriel(i, v)
        b = angle_vectoriel(i, u)
        if isinstance(self, Angle) and self._sens() < 0:
            a, b = b, a
        if b < a:
            b += 2*pi

        angle, codage_angle = self._representation

        angle.set(rayon=param.codage['rayon'], position=self.__point.xy,
                  taille=param.codage['taille'], intervalle=(a, b),
                  angle=param.codage['angle'], style=codage,
                  zorder=niveau - 0.01, alpha=self.style('alpha'),
                  linewidth=self.style('epaisseur'), facecolor=self.style('couleur'),
                  linestyle = FILL_STYLES.get(style, 'solid'),
                  )

        codage_angle.set(visible=bool(codage), linewidth=self.style('epaisseur'),
                         linestyle = FILL_STYLES.get(style, 'solid'),
                        )



    def _espace_vital(self):
        x, y = self.__point.coordonnees
        x1, y1, = self.__vecteur1.coordonnees
        x2, y2 = self.__vecteur2.coordonnees
        xmin = min(x, x + x1, x + x2)
        xmax = max(x, x + x1, x + x2)
        ymin = min(y, y + y1, y + y2)
        ymax = max(y, y + y1, y + y2)
        return xmin, xmax, ymin, ymax




    def _distance_inf(self, x, y, d):
        x0, y0 = self._pixel(self.__point)
        #print (x - x0)**2 + (y - y0)**2
        if (x - x0)**2 + (y - y0)**2 > (param.codage["rayon"] + d)**2:
            return False
        x, y = self.__canvas__.pix2coo(x, y)
        x0, y0 = self.__point.coordonnees
        u = (x - x0, y - y0)
        if abs(u[0]) + abs(u[1]) < contexte['tolerance']:
            # Vecteur inexistant (le pointeur de la souris est au sommet de l'angle)
            return True
        elif isinstance(self, Angle) and self._sens() < 0:
            a = angle_vectoriel(self.__vecteur2, self.__vecteur1)
            b = angle_vectoriel(self.__vecteur2, u)
        else:
            a = angle_vectoriel(self.__vecteur1, self.__vecteur2)
            b = angle_vectoriel(self.__vecteur1, u)
        #print a, b
        if a < 0:
            return not a < b < 0
        else:
            return 0 <= b <= a


    def _conditions_existence(self):
        return self.__vecteur1.norme > contexte['tolerance'] and self.__vecteur2.norme > contexte['tolerance']


    def image_par(self, transformation):
        return Secteur_angulaire(self.__point.image_par(transformation), self.__vecteur1.image_par(transformation), self.__vecteur2.image_par(transformation))




class Angle_oriente(Secteur_angulaire):
    u"""Un angle orienté.

    Un angle orienté défini par 3 points A, B, C -> angle (BA>, BC>)."""

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)
    point3 = __point3 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, point3 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__point3 = point3 = Ref(point3)
        Secteur_angulaire.__init__(self, point2, Vecteur(point2, point1), Vecteur(point2, point3), **styles)








class Angle(Secteur_angulaire):
    u"""Un angle.

    Un angle non orienté, défini par 3 points A, B, C -> angle /ABC\."""

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)
    point3 = __point3 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, point3 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__point3 = point3 = Ref(point3)
        Secteur_angulaire.__init__(self, point2, Vecteur(point2, point1), Vecteur(point2, point3), **styles)

    def _get_valeur(self):
        return abs(Secteur_angulaire._get_valeur(self))


    @property
    def sens(self):
        return u"non défini" # attention en cas de modification : cette valeur est utilisée dans la classe Label_angle

    def image_par(self, transformation):
        return Angle(self.__point1.image_par(transformation), self.__point2.image_par(transformation), self.__point3.image_par(transformation))





class Angle_libre(Angle_generique):
    u"""Un angle libre.

    Un angle défini par sa valeur numérique (en radian)."""

    variable = __variable = Argument("Variable_generique", defaut = lambda: uniform(0, 2*pi))

    def __init__(self, variable = None, unite = None, **styles):

        # Gestion des unités d'angle (degré et grad)
        if unite is None:
            unite = contexte['unite_angle']
        else:
            if unite == u'\u00B0' or unite.startswith('deg'):
                unite = 'd'
            elif unite.startswith('gr'):
                unite = 'g'

        if isinstance(variable, basestring):
            variable = variable.strip()
            if variable[-1]  == u'\u00B0':
                unite = 'd'
                variable = variable[:-1]

        if unite in ('d', 'g'):
            coeff = 180 if unite == 'd' else 200
            if isinstance(variable, Variable):
                variable = variable.contenu
            if isinstance(variable, basestring):
                variable = '(' + variable + ')*pi/%s' %coeff
            elif issympy(variable):
                variable *= PI/coeff
            else:
                variable *= pi/coeff

        self.__variable = variable = Ref(variable)
        Angle_generique.__init__(self)

    def _creer_figure(self):
        pass  # les angles libres ne sont pas affichés.

    def _set_valeur(self, val = None):
       self.__variable = val

    def _get_valeur(self):
        return self.__variable.valeur




class Angle_vectoriel(Angle_generique):
    u"""Un angle défini par des vecteurs.

    Un angle orienté défini par deux vecteurs (non affiché)."""
    vecteur1 = __vecteur1 = Argument("Vecteur_generique", defaut = Vecteur_libre)
    vecteur2 = __vecteur2 = Argument("Vecteur_generique", defaut = Vecteur_libre)

    def __init__(self, vecteur1 = None, vecteur2 = None, **styles):
        self.__vecteur1 = vecteur1 = Ref(vecteur1)
        self.__vecteur2 = vecteur2 = Ref(vecteur2)
        Angle_generique.__init__(self)


    def _conditions_existence(self):
        return self.__vecteur1.norme > contexte['tolerance'] and self.__vecteur2.norme > contexte['tolerance']


    def _get_valeur(self):
        return angle_vectoriel(self.__vecteur1, self.__vecteur2)
