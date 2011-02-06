# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                   Cercles                   #
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


from objet import *




##########################################################################################




# Cercles


class Cercle_Arc_generique(Objet_avec_equation):
    u"""La classe mère de tous les cercles et arcs de cercles."""

    _affichage_depend_de_la_fenetre = True
    _enregistrer_sur_la_feuille_par_defaut = True
    # à cause du codage des longueurs (arcs), et du nombre de points variable des cercles

    centre = __centre = Argument("Point_generique")

    def __init__(self, centre, **styles):
        self.__centre = centre = Ref(centre)
        Objet.__init__(self, **styles)

    def _get_equation(self):
        u"""Retourne un triplet (a,b,c) tel que x**2 + y**2 + ax + by + c = 0
        soit une équation du cercle."""
        xO, yO = self.__centre.coordonnees
        r = self.rayon
        return (-2*xO, -2*yO, xO**2 + yO**2 - r**2)


    @property
    def rayon(self):
        raise NotImplementedError

    @property
    def diametre(self):
        return 2*self.rayon

    def _distance_inf(self, x, y, d): # à surclasser pour les arcs
        x0, y0 = self._pixel(self.__centre)
        rx, ry = self.__canvas__.dcoo2pix(self.rayon, self.rayon)
        rx = abs(rx) ; ry = abs(ry)
        if x0 - rx - d < x < x0 + rx + d and y0 - ry - d < y < y0 + ry + d:
            return carre_distance_point_ellipse((x0, y0), rx, ry, (x, y), epsilon = .000001) < d**2
        return False





class Arc_generique(Cercle_Arc_generique):
    u"""La classe mère de tous les arcs de cercles."""

    _style_defaut = param.arcs
    _prefixe_nom = "a"

    centre = __centre = Argument("Point_generique")
    point = __point = Argument("Point_generique")

    def __init__(self, centre, point, **styles):
        self.__centre = centre = Ref(centre)
        self.__point = point = Ref(point)
        Cercle_Arc_generique.__init__(self, centre, **styles)
        self.etiquette = ALL.Label_arc_cercle(self)



##    @property
##    def centre(self):
##        return self.__centre

    @property
    def rayon(self):
        try:
            return distance(self.__centre, self.__point)
        except TypeError:
            return 0



    @property
    def equation_formatee(self):
        u"Equation sous forme lisible par l'utilisateur."
        eq = self.equation
        if eq is None:
            return u"L'objet n'est pas défini."
        a, b, c = (nice_display(coeff) for coeff in eq)
        # on ne garde que quelques chiffres après la virgule pour l'affichage
        xmin, xmax, ymin, ymax = (nice_display(extremum) for extremum in self._espace_vital())
        return formatage(u"x² + y² + %s x + %s y + %s = 0 avec %s<x<%s et %s<y<%s" %(a, b, c, xmin, xmax, ymin, ymax))

    #~ def _distance_inf(self, x, y, d):
        #~ x0, y0 = self._pixel(self.__centre)
        #~ a, b = self._intervalle()
        #~ t = numpy.arange(a, b, .003)
        #~ rx, ry = self.__canvas__.dcoo2pix(self.rayon, self.rayon)
        #~ u = x - x0 - rx*numpy.cos(t)
        #~ v = y - y0 - ry*numpy.sin(t)
        #~ m = min(u*u + v*v) # u*u est beaucoup plus rapide que u**2 (sic!)
        #~ return m < d**2


    def _distance_inf(self, x, y, d):
        # On travaille avec les coordonnées de la feuille
        a, b = self._intervalle()
        z0 = self.__centre.z
        xM, yM = self.__canvas__.pix2coo(x, y)
        zM = xM + 1j*yM
        if abs(zM - z0) > 10*contexte['tolerance']:
            phi = cmath.phase(zM - z0)
            if not (a <= trigshift(phi, a) <= b):
                # on est au niveau de "l'ouverture" de l'arc
                # NB: le code n'est pas parfait ; en particulier, si le repère n'est pas orthonormal,
                # et que l'ellipse qui porte le cercle est *très* allongée,
                # le calcul de distance est passablement faux à *l'intérieur* de l'ellipse
                zA = z0 + cmath.rect(self.rayon, a)
                zB = z0 + cmath.rect(self.rayon, b)
                # On travaille maintenant avec les coordonnées en pixel
                _xA, _yA = self.__canvas__.coo2pix(zA.real, zA.imag)
                _xB, _yB = self.__canvas__.coo2pix(zB.real, zB.imag)
                return min((_xA - x)**2 + (_yA - y)**2, (_xB - x)**2 + (_yB - y)**2) < d**2
        return Cercle_Arc_generique._distance_inf(self, x, y, d)


    def _intervalle(self):
        u"Renvoie deux nombres a < b. L'arc est l'ensemble des points (r*cos(t), r*sin(t)) pour t apartenant à [a, b]."
        raise NotImplementedError

    def _sens(self):
        return 1

    def _longueur(self):
        a, b = self._intervalle()
        return (b - a)*self.rayon

    @property
    def longueur(self):
        try:
            return self._longueur()
        except TypeError:
            return 0

    @property
    def extremites(self):
        u"Extrémités de l'arc."
        raise NotImplementedError

    @property
    def info(self):
        return self.nom_complet + u' de longueur ' + nice_display(self.longueur)


    def _t(self):
        u, v = self._intervalle()
        x, y = self.__centre.coordonnees
        xmin, xmax, ymin, ymax = self.__feuille__.fenetre
        w = 3*(xmax - xmin)
        h = 3*(ymax - ymin)
        if xmin - w < x < xmax + w and ymin - h < y < ymax + h:
            return [fullrange(u, v, self.__canvas__.pas())]
        else:
            # Optimisation dans le cas où le centre est très loin de la fenêtre.
            A = xmin + 1j*ymin
            B = xmax + 1j*ymin
            C = xmax + 1j*ymax
            D = xmin + 1j*ymax
            O = x + 1j*y
            a = cmath.phase(A - O)
            b = cmath.phase(B - O)
            c = cmath.phase(C - O)
            d = cmath.phase(D - O)
            if x >= xmax and ymin <= y <= ymax:
                assert (a <= 0 and b <= 0 and c >= 0 and d >= 0)
                a += 2*pi
                b += 2*pi
            # On récupère la portion du cercle à afficher :
            a, b = min(a, b, c, d), max(a, b, c, d)
            # Maintenant, il faut trouver l'intersection entre cette portion de cercle, et l'arc.
            # On s'arrange pour que a appartienne à l'intervalle [u; u + 2pi[ :
            k = trigshift(a, u) - a
            a += k
            b += k
            # L'intersection est constituée d'un ou deux morceaux
            intersection = []
            if a < v:
                c = min(b, v)
                print a, c
                intersection.append(fullrange(a, c, self.__canvas__.pas()))
            u += 2*math.pi
            v += 2*math.pi
            if b > u:
                c = min(b, v)
                intersection.append(fullrange(u, c, self.__canvas__.pas()))
            return intersection



    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.ligne()]

        plot = self._representation[0]
        x, y = self.__centre.coordonnees
        r = self.rayon
        t = self._t()
        plot.set_data(x + r*numpy.cos(t), y + r*numpy.sin(t))
        plot._color = self.style("couleur")
        plot._linestyle = self.style("style")
        plot._linewidth = self.style("epaisseur")
        plot.zorder = self.style("niveau")



    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.ligne(), self.rendu.ligne(), self.rendu.ligne(), self.rendu.ligne(), self.rendu.ligne()]
            # les 2 premières lignes servent à afficher l'arc lui-même ; les autres servent pour le codage.

        #~ plot = self._representation[0]
        #~ x, y = self._Arc_generique__centre.coordonnees
        #~ r = self.rayon
        #~ a, b = self._intervalle()
        #~ t = numpy.concatenate((numpy.arange(a, b, self.__canvas__.pas()), [b]))
        #~ plot.set_data(x + r*numpy.cos(t), y + r*numpy.sin(t))
        #~ plot._color = self.style("couleur")
        #~ plot._linestyle = self.style("style")
        #~ plot._linewidth = self.style("epaisseur")
        #~ niveau = self.style("niveau")
        #~ plot.zorder = niveau

        for plot in self._representation[1:]:
            plot._visible = False

        x, y = self._Arc_generique__centre.coordonnees
        r = self.rayon
        niveau, couleur, style, epaisseur, codage = self.style(('niveau', 'couleur', 'style', 'epaisseur', 'codage'))
        taille = param.codage["taille"]
        a = param.codage["angle"]



        for i, t in enumerate(self._t()):
            plot = self._representation[i]
            plot.set_data(x + r*numpy.cos(t), y + r*numpy.sin(t))
            plot.set(color = couleur, linestyle = style, linewidth = epaisseur, zorder = niveau, visible = True)


        # Gestion du codage des arcs de cercle (utilisé pour indiquer les arcs de cercles de même longeur)
        if codage:
            c = .5*(a + b)
            x0 = x + r*math.cos(c); y0 = y + r*math.sin(c)
            for plot in self._representation[2:]:
                plot.zorder = niveau + 0.01

            plot1, plot2, plot3 = self._representation[2:]

            if codage == "o":
                plot1.set(marker = "o", markersize = taille, markerfacecolor = None, markeredgecolor = couleur, \
                            markeredgewidth = epaisseur, visible = True)
                plot1.set_data([x0], [y0])

            else:
                r = taille*param.zoom_ligne
                G = numpy.array(self.__canvas__.coo2pix(x0, y0))
                coeff0, coeff1 = self.__canvas__.coeffs()
                vecteur = numpy.array(((y0 - y)/coeff0, (x0 - x)/coeff1)) # vecteur orthogonal au rayon
                vec = vecteur/math.hypot(*vecteur)
                C = G + r*vec

                if codage == "x":
                    M = (numpy.dot([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]],
                            numpy.transpose([C - G])) + numpy.transpose([G]))[:,0]
                    N = (numpy.dot([[math.cos(a), math.sin(a)], [-math.sin(a), math.cos(a)]],
                            numpy.transpose([C - G])) + numpy.transpose([G]))[:,0]
                    plot1.set_data(*self.__canvas__.pix2coo(*array_zip(M, 2*G-M)))
                    plot1.set(marker = 'None', color = couleur, linewidth = epaisseur, visible = True)
                    plot2.set_data(*self.__canvas__.pix2coo(*array_zip(N, 2*G-N)))
                    plot2.set(marker = 'None', color = couleur, linewidth = epaisseur, visible = True)

                elif codage == "/":
                    M = (numpy.dot([[math.cos(a), math.sin(a)], [-math.sin(a), math.cos(a)]],
                            numpy.transpose([C - G])) + numpy.transpose([G]))[:,0]
                    plot1.set_data(*self.__canvas__.pix2coo(*array_zip(M, 2*G - M)))
                    plot1.set(marker = 'None', color = couleur, linewidth = epaisseur, visible = True)

                elif codage == "//":
                    M = (numpy.dot([[math.cos(a), math.sin(a)], [-math.sin(a), math.cos(a)]],
                            numpy.transpose([C - G])) + numpy.transpose([G]))[:,0]
                    vec = 2*vec
                    plot1.set_data(*self.__canvas__.pix2coo(*array_zip(M + vec, 2*G - M + vec)))
                    plot2.set_data(*self.__canvas__.pix2coo(*array_zip(M - vec, 2*G - M - vec)))
                    plot1.set(marker = 'None', color = couleur, linewidth = epaisseur, visible = True)
                    plot2.set(marker = 'None', color = couleur, linewidth = epaisseur, visible = True)

                elif codage == "///":
                    M = (numpy.dot([[math.cos(a), math.sin(a)], [-math.sin(a), math.cos(a)]],
                            numpy.transpose([C - G])) + numpy.transpose([G]))[:,0]
                    vec = 3*vec
                    plot1.set_data(*self.__canvas__.pix2coo(*array_zip(M, 2*G - M)))
                    plot2.set_data(*self.__canvas__.pix2coo(*array_zip(M + vec, 2*G - M + vec)))
                    plot3.set_data(*self.__canvas__.pix2coo(*array_zip(M - vec, 2*G - M - vec)))
                    plot1.set(marker = 'None', color = couleur, linewidth = epaisseur, visible = True)
                    plot2.set(marker = 'None', color = couleur, linewidth = epaisseur, visible = True)
                    plot3.set(marker = 'None', color = couleur, linewidth = epaisseur, visible = True)


    def _espace_vital(self):
        x0, y0 = self.__centre.coordonnees
        a, b = self._intervalle()
        t = numpy.arange(a, b, .003)
        r = self.rayon
        u = x0 + r*numpy.cos(t)
        v = y0 + r*numpy.sin(t)
        return min(u), max(u), min(v), max(v)


    def _contains(self, M):
        O = self.__centre
        a, b = self._intervalle()
        vec = vect(O, M)
        if math.hypot(*vec) < contexte['tolerance']: # M et O sont (quasi) confondus
            return self.rayon < contexte['tolerance'] # alors M appartient (quasiment) à l'arc ssi l'arc est de rayon (quasi) nul
        else:
            c = angle_vectoriel(ALL._vecteur_unite, vec)
            if c < a:
                c += 2*math.pi
    #        print "Test tolerance arc cercle",  abs(distance(O, M) - self.rayon),  a < c < b
            return abs(distance(O, M) - self.rayon) < contexte['tolerance'] and a - contexte['tolerance'] < c < b + contexte['tolerance']






class Arc_cercle(Arc_generique):
    u"""Un arc de cercle.

    Un arc de cercle orienté, défini par son centre et ses extremités(*), dans le sens direct.

    (*) note : le troisième point n'appartient pas forcément à l'arc de cercle, mais sert à en délimiter l'angle au centre."""


    centre = __centre = Argument("Point_generique", defaut = ALL.Point)
    point1 = __point1 = Argument("Point_generique", defaut = ALL.Point)
    point2 = __point2 = Argument("Point_generique", defaut = ALL.Point)

    def __init__(self, centre = None, point1 = None, point2 = None, **styles):
        self.__centre = centre = Ref(centre)
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        Arc_generique.__init__(self, centre,  point1, **styles)
        self._angle1 = ALL.Angle_vectoriel(ALL._vecteur_unite, ALL.Vecteur(centre, point1))
        self._angle2 = ALL.Angle_vectoriel(ALL._vecteur_unite, ALL.Vecteur(centre, point2))

    def image_par(self, transformation):
        return Arc_cercle(self.__centre.image_par(transformation), self.__point1.image_par(transformation), self.__point2.image_par(transformation))

    def _intervalle(self):
        a = self._angle1.valeur
        b = self._angle2.valeur
        if b < a:
            b += 2*(sympy.pi if issympy(b) else math.pi)
        return a, b

    @property
    def extremites(self):
        return self.__point1, self.__point2







class Arc_points(Arc_generique):
    u"""Un arc défini par 3 points.

    Un arc de cercle, défini par ses extrémités, et un autre point."""


    point1 = __point1 = Argument("Point_generique", defaut = ALL.Point)
    point2 = __point2 = Argument("Point_generique", defaut = ALL.Point)
    point3 = __point3 = Argument("Point_generique", defaut = ALL.Point)

    def __init__(self, point1 = None, point2 = None, point3 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__point3 = point3 = Ref(point3)
        Arc_generique.__init__(self, ALL.Point_equidistant(point1, point2, point3), point1, **styles)
#        self.centre = centre = self._Arc_generique__centre
        centre = self._Arc_generique__centre
        self._angle1 = ALL.Angle_vectoriel(ALL._vecteur_unite, ALL.Vecteur(centre, point1))
        self._angle2 = ALL.Angle_vectoriel(ALL._vecteur_unite, ALL.Vecteur(centre, point2))
        self._angle3 = ALL.Angle_vectoriel(ALL._vecteur_unite, ALL.Vecteur(centre, point3))


    def image_par(self, transformation):
        return Arc_points(self.__point1.image_par(transformation), self.__point2.image_par(transformation), self.__point3.image_par(transformation))

    def _intervalle(self):
        # mesure des angles dans ]-pi;pi]
        a = self._angle1.valeur
        b = self._angle2.valeur
        c = self._angle3.valeur
        if b < a:
            b += 2*(sympy.pi if issympy(b) else math.pi)
        if c < a:
            c += 2*(sympy.pi if issympy(c) else math.pi)
        if b < c:
            return a, c
        return c, a + 2*(sympy.pi if issympy(a) else math.pi)

    def _sens(self):
        u"Sens de parcours de l'arc : direct (1) ou indirect (-1)"
        # mesure des angles dans ]-pi;pi]
        a = float(self._angle1)
        b = float(self._angle2)
        c = float(self._angle3)
        if b < a:
            b += 2*math.pi
        if c < a:
            c += 2*math.pi
        if b < c:
            return 1
        return -1


    def _conditions_existence(self):
        return self._Arc_generique__centre.existe

    @property
    def extremites(self):
        return self.__point1, self.__point3



class Arc_oriente(Arc_points):
    u"""Un arc de cercle orienté.

    Un arc de cercle orienté, défini par ses extrémités, et un autre point."""

    _style_defaut = param.arcs_orientes

    point1 = __point1 = Argument("Point_generique", defaut = ALL.Point)
    point2 = __point2 = Argument("Point_generique", defaut = ALL.Point)
    point3 = __point3 = Argument("Point_generique", defaut = ALL.Point)

    def __init__(self, point1 = None, point2 = None, point3 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__point3 = point3 = Ref(point3)
        # on ne peut pas utiliser le mot-clef "defaut", car le style par défaut est déjà défini (param.arcs)
        Arc_points.__init__(self, point1, point2, point3, **styles)

    def image_par(self, transformation):
        return Arc_oriente(self.__point1.image_par(transformation), self.__point2.image_par(transformation), self.__point3.image_par(transformation))

    @property
    def sens(self):
        if self._sens() is 1:
            return "direct"
        return "indirect"

    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.ligne(), self.rendu.ligne(), self.rendu.ligne()]
        plot1, plot2, plot3 = self._representation

        x, y = self._Arc_generique__centre.coordonnees
        r = self.rayon
        a, b = self._intervalle()
        t = fullrange(a, b, self.__canvas__.pas())
        plot1.set_data(x + r*numpy.cos(t), y + r*numpy.sin(t))

        # Dessin de la flêche (cf. le code pour la classe Vecteur, et les explications qui y sont données)
        k = self.style("position")
        coeff0, coeff1 = self.__canvas__.coeffs()
        if self._sens() is 1: # vecteur donnant le sens de la flêche (orthogonal au rayon)
            c = k*b + (1-k)*a
            x0 = x + r*math.cos(c); y0 = y + r*math.sin(c)
            vec = numpy.array(((y0 - y)/coeff0, (x0 - x)/coeff1))
        else:
            c = (1-k)*b + k*a
            x0 = x + r*math.cos(c); y0 = y + r*math.sin(c)
            vec = numpy.array(((y - y0)/coeff0, (x - x0)/coeff1))

        taille = self.style("taille")
        ang = self.style("angle")*math.pi/360
        G = numpy.array(self.__canvas__.coo2pix(x0, y0))
        C = G + taille*vec/math.hypot(*vec)
        M = (numpy.dot([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]], numpy.transpose([C - G])) + numpy.transpose([G]))[:,0]
        N = (numpy.dot([[math.cos(ang), math.sin(ang)], [-math.sin(ang), math.cos(ang)]], numpy.transpose([C - G])) + numpy.transpose([G]))[:,0]
        xx, yy = self.__canvas__.pix2coo(*array_zip(M, G, N))
        plot2.set_data(numpy.array(xx), numpy.array(yy))

        if self.style("double_fleche"):
            plot3._visible = True
            if self._sens() is 1: # vecteur donnant le sens de la flêche (orthogonal au rayon)
                c = (1-k)*b + k*a
                x0 = x + r*math.cos(c); y0 = y + r*math.sin(c)
                vec = numpy.array(((y - y0)/coeff0, (x - x0)/coeff1))
            else:
                c = k*b + (1-k)*a
                x0 = x + r*math.cos(c); y0 = y + r*math.sin(c)
                vec = numpy.array(((y0 - y)/coeff0, (x0 - x)/coeff1))

            G = numpy.array(self.__canvas__.coo2pix(x0, y0))
            C = G + taille*vec/math.hypot(*vec)
            M = (numpy.dot([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]], numpy.transpose([C - G])) + numpy.transpose([G]))[:,0]
            N = (numpy.dot([[math.cos(ang), math.sin(ang)], [-math.sin(ang), math.cos(ang)]], numpy.transpose([C - G])) + numpy.transpose([G]))[:,0]
            xx, yy = self.__canvas__.pix2coo(*array_zip(M, G, N))
            plot3.set_data(numpy.array(xx), numpy.array(yy))
        else:
            plot3._visible = False

        plot1._color = plot2._color = plot3._color = self.style("couleur")
        plot1._linestyle = plot2._linestyle = plot3._linestyle = self.style("style")
        plot1._linewidth = plot2._linewidth = plot3._linewidth = self.style("epaisseur")
        plot1.zorder = plot2.zorder = plot3.zorder = self.style("niveau")










class Demicercle(Arc_cercle):
    u"""Un demi-cercle.

    Un demi-cercle orienté, défini par ses extrémités, dans le sens direct."""


    point1 = __point1 = Argument("Point_generique", defaut = ALL.Point)
    point2 = __point2 = Argument("Point_generique", defaut = ALL.Point)

    def __init__(self, point1 = None, point2 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        Arc_cercle.__init__(self, ALL.Milieu(point1, point2), point1, point2, **styles)
#        self.centre = centre = self._Arc_generique__centre








class Cercle_generique(Cercle_Arc_generique):
    u"""Un cercle générique.

    Usage interne : la classe mère pour tous les types de cercles."""

    _style_defaut = param.cercles
    _prefixe_nom = "c"

    centre = __centre = Argument("Point_generique")

    def __init__(self, centre, **styles):
        self.__centre = centre = Ref(centre)
        Cercle_Arc_generique.__init__(self, centre, **styles)
        self.etiquette = ALL.Label_cercle(self)

##    @property
##    def centre(self):
##        return self.__centre


    def _t(self):
        x, y = self.__centre.coordonnees
        xmin, xmax, ymin, ymax = self.__feuille__.fenetre
        w = 3*(xmax - xmin)
        h = 3*(ymax - ymin)
        if xmin - w < x < xmax + w and ymin - h < y < ymax + h:
            return fullrange(0, 2*math.pi, self.__canvas__.pas())
        else:
            # Optimisation dans le cas où le centre est très loin de la fenêtre.
            A = xmin + 1j*ymin
            B = xmax + 1j*ymin
            C = xmax + 1j*ymax
            D = xmin + 1j*ymax
            O = x + 1j*y
            a = cmath.phase(A - O)
            b = cmath.phase(B - O)
            c = cmath.phase(C - O)
            d = cmath.phase(D - O)
            if x >= xmax and ymin <= y <= ymax:
                assert (a <= 0 and b <= 0 and c >= 0 and d >= 0)
                a += 2*pi
                b += 2*pi
            return numpy.arange(min(a, b, c, d), max(a, b, c, d), self.__canvas__.pas())




    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.ligne()]

        plot = self._representation[0]
        x, y = self.__centre.coordonnees
        r = self.rayon
        t = self._t()
        plot.set_data(x + r*numpy.cos(t), y + r*numpy.sin(t))
        plot._color = self.style("couleur")
        plot._linestyle = self.style("style")
        plot._linewidth = self.style("epaisseur")
        plot.zorder = self.style("niveau")


#    def _creer_figure(self):
#        if not self._representation:
#            self._representation = [self.rendu.cercle()]

#        cercle = self._representation[0]
#        cercle.center = self.__centre.coordonnees
#        cercle.radius = self.rayon
#        cercle.set_edgecolor(self.style("couleur"))
#        plot._linestyle = self.style("style")
#        plot._linewidth = self.style("epaisseur")
#        plot.zorder = self.style("niveau")


    def _longueur(self):
        rayon = self.rayon
        return 2*rayon*pi_()

    perimetre = property(_longueur)





##    def _distance_inf(self, x, y, d):
##        x0, y0 = self._pixel(self.__centre)
##        t = numpy.arange(0, 2*math.pi, .003)
##        rx, ry = self.__canvas__.dcoo2pix(self.rayon, self.rayon)
##        u = x - x0 - rx*numpy.sin(t)
##        v = y - y0 + ry*numpy.cos(t)
##        m = min(u*u + v*v) # u*u est beaucoup plus rapide que u**2 (sic!)
##        return m < d**2

    def _contains(self, M):
        O = self.__centre
        return abs(distance(O, M) - self.rayon) < contexte['tolerance']


    def _espace_vital(self):
        x, y = self.__centre.coordonnees
        r = self.rayon
        return (x - r, x + r, y - r, y + r)


    @property
    def equation_formatee(self):
        u"Equation sous forme lisible par l'utilisateur."
        eq = self.equation
        if eq is None:
            return u"L'objet n'est pas défini."
        a, b, c = (nice_display(coeff) for coeff in eq)
        # on ne garde que quelques chiffres après la virgule pour l'affichage
        return formatage(u"x² + y² + %s x + %s y + %s = 0" %(a, b, c))


    def _creer_nom_latex(self):
        u"""Crée le nom formaté en LaTeX. Ex: M1 -> $M_1$."""
        Objet._creer_nom_latex(self)
        nom = self.latex_police_cursive(self.nom_latex[1:-1])
        self.nom_latex = "$" + nom + "$"

    @property
    def info(self):
        return self.nom_complet + u' de rayon ' + nice_display(self.rayon)






class Cercle_rayon(Cercle_generique):
    u"""Un cercle de rayon fixé.

    Un cercle défini par son centre et son rayon."""


    centre = __centre = Argument("Point_generique", defaut = ALL.Point)
    rayon = __rayon = Argument("Variable", defaut = 1)

    def __init__(self, centre = None, rayon = None, **styles):
        self.__centre = centre = Ref(centre)
        self.__rayon = rayon = Ref(rayon)
        Cercle_generique.__init__(self, centre, **styles)

    def image_par(self, transformation):
        return Cercle(self.__centre.image_par(transformation), ALL.Glisseur_cercle(self).image_par(transformation))

    def _conditions_existence(self):
        return self.__rayon >= 0

    def _set_feuille(self):
        if "_Cercle__rayon" in self._valeurs_par_defaut:
            xmin, xmax, ymin, ymax = self.__feuille__.fenetre
            self.__rayon = .5*module_random.uniform(0, min(abs(xmin - xmax), abs(ymin - ymax)))
#            self._valeurs_par_defaut.discard("_Cercle__rayon")
        if "_Cercle__centre" in self._valeurs_par_defaut:
            xmin, xmax, ymin, ymax = self.__feuille__.fenetre
            r = self.__rayon
            self.__centre.coordonnees = module_random.uniform(xmin + r, xmax - r), module_random.uniform(ymin + r, ymax - r)
#            self._valeurs_par_defaut.discard("_Cercle__centre")
        Objet._set_feuille(self)



class Cercle(Cercle_generique):
    u"""Un cercle.

    Un cercle défini par son centre et un point du cercle."""

    centre = __centre = Argument("Point_generique", defaut = ALL.Point)
    point = __point = Argument("Point_generique", defaut = ALL.Point)

    def __new__(cls, *args, **kw):
        if len(args) == 1 and isinstance(args[0], basestring):
            newclass = Cercle_equation
        elif len(args) == 1 and isinstance(args[0], ALL.Segment):
            newclass = Cercle_diametre
        elif len(args) == 2 and (isinstance(args[1], ALL.TYPES_REELS)
                                or isinstance(args[1], basestring)):
            newclass = Cercle_rayon
        elif len(args) == 3 and isinstance(args[0], ALL.Point_generique) \
                                      and isinstance(args[1], ALL.Point_generique) \
                                      and isinstance(args[2], ALL.Point_generique):
            newclass = Cercle_points
        else:
            return object.__new__(cls)
        objet = newclass.__new__(newclass, *args, **kw)
        objet.__init__(*args, **kw)
        return objet

    def __init__(self, centre = None, point = None, **styles):
        self.__centre = centre = Ref(centre)
        self.__point = point = Ref(point)
        Cercle_generique.__init__(self, centre, **styles)

    @property
    def rayon(self):
        return distance(self.__centre, self.__point)


    def image_par(self, transformation):
        return Cercle(self.__centre.image_par(transformation), self.__point.image_par(transformation))




class Cercle_diametre(Cercle_generique):
    u"""Un cercle défini par un diamètre.

    Un cercle défini par un diamètre [AB]."""

    point1 = __point1 = Argument("Point_generique", defaut = ALL.Point)
    point2 = __point2 = Argument("Point_generique", defaut = ALL.Point)

    def __init__(self, point1 = None, point2 = None, **styles):
        if isinstance(point1, ALL.Segment) and point2 is None:
            point2 = point1.point2
            point1 = point1.point1
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        Cercle_generique.__init__(self, ALL.Milieu(point1, point2), **styles)

    @property
    def rayon(self):
        return distance(self._Cercle_generique__centre, self.__point1)

    def image_par(self, transformation):
        return Cercle_diametre(self.__point1.image_par(transformation), self.__point2.image_par(transformation))





class Cercle_points(Cercle_generique):
    u"""Un cercle défini par 3 points.

    Un cercle défini par la donnée de 3 points du cercle."""

    point1 = __point1 = Argument("Point_generique", defaut = ALL.Point)
    point2 = __point2 = Argument("Point_generique", defaut = ALL.Point)
    point3 = __point3 = Argument("Point_generique", defaut = ALL.Point)

    def __init__(self, point1 = None, point2 = None, point3 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__point3 = point3 = Ref(point3)
        Cercle_generique.__init__(self, ALL.Point_equidistant(point1, point2, point3), **styles)

    @property
    def rayon(self):
        try:
            return distance(self._Cercle_generique__centre, self.__point1)
        except TypeError:
            return 0

    def _conditions_existence(self):
        return self._Cercle_generique__centre.existe

    def image_par(self, transformation):
        return Cercle_points(self.__point1.image_par(transformation), self.__point2.image_par(transformation), self.__point3.image_par(transformation))






class Cercle_equation(Cercle_generique):
    u"""Un cercle défini par une équation.

    Un cercle d'équation donnée sous forme d'un triplet (a, b, c). (x**2 + y**2 + ax + by + c = 0)"""

    a = __a = Argument("Variable")
    b = __b = Argument("Variable")
    c = __c = Argument("Variable")

    def __init__(self, a = 0, b = 0, c = -1, **styles):
        self.__a = a = Ref(a)
        self.__b = b = Ref(b)
        self.__c = c = Ref(c)
        Objet.__init__(self) # pour pouvoir utiliser 'ALL.Centre(self)', l'objet doit déjà être initialisé
        Cercle_generique.__init__(self, ALL.Centre(self), **styles)



    @property
    def rayon(self):
        return math.sqrt((self.__a**2 + self.__b**2)/4 - self.__c)


    def _get_equation(self):
        u"Retourne un triplet (a, b, c), tel que x**2 + y**2 + ax + by + c = 0 soit une équation du cercle."
        return self.__a, self.__b, self.__c

    def _set_equation(self, a = None, b = 0, c = -1):
        if a is not None:
            self.__a = a
            self.__b = b
            self.__c = c

    def _conditions_existence(self):
        return self.__a**2 + self.__b**2 - 4*self.__c >= 0

##    def a(self, valeur = None):
##        return self.__a(valeur)
##
##    a = property(a,  a)
##
##    def b(self, valeur = None):
##        return self.__b(valeur)
##
##    b = property(b,  b)
##
##    def c(self, valeur = None):
##        return self.__c(valeur)
##
##    c = property(c,  c)

    def image_par(self, transformation):
        return Cercle_rayon(ALL.Centre(self).image_par(transformation), ALL.Glisseur_cercle(self).image_par(transformation))




class Disque(Cercle_generique):
    u"""Un disque.

    Un disque défini par le cercle le délimitant."""

    _style_defaut = param.polygones
    _prefixe_nom = "d"

    cercle = __cercle = Argument("Cercle_generique", defaut = Cercle)

    def __init__(self, cercle = None, **styles):
        self.__cercle = cercle = Ref(cercle)
        Cercle_generique.__init__(self, ALL.Centre(cercle), **styles)

    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.polygone()]

        fill = self._representation[0]
        x, y = self._Cercle_generique__centre.coordonnees
        r = self.rayon
        t = fullrange(0, 2*math.pi , self.__canvas__.pas())
        fill.xy = zip(x + r*numpy.cos(t), y + r*numpy.sin(t))
        fill._alpha = self.style("alpha")
        fill._color = self.style("couleur")
        fill._linestyle = ALL.FILL_STYLES.get(self.style("style"), "solid")
        fill._linewidth = self.style("epaisseur")
        fill.zorder = self.style("niveau")


    @property
    def rayon(self):
        return self.__cercle.rayon

    def _distance_inf(self, x, y, d):
        x, y = self.__canvas__.pix2coo(x, y)
        return distance(self._Cercle_generique__centre, (x, y)) <= self.rayon

    def _contains(self, M):
        return distance(self._Cercle_generique__centre, M) - self.rayon <= contexte['tolerance']

    @property
    def aire(self):
        return self.rayon**2*pi_()

    @property
    def info(self):
        return self.nom_complet + u" d'aire " + nice_display(self.aire)


    @property
    def equation_formatee(self):
        u"Equation sous forme lisible par l'utilisateur."
        eq = self.equation
        if eq is None:
            return u"L'objet n'est pas défini."
        a, b, c = (nice_display(coeff) for coeff in eq)  # on ne garde que quelques chiffres après la virgule pour l'affichage
        return formatage(u"x² + y² + %s x + %s y + %s <= 0" %(a, b, c))

    def image_par(self, transformation):
        return Disque(self.__cercle.image_par(transformation))
