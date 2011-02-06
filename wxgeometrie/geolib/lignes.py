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


from points import *






##########################################################################################

## LIGNES






class Ligne_generique(Objet_avec_equation):
    u"""Une ligne générique.

    Usage interne : la classe mère pour les droites, segments, demi-droites."""

    _affichage_depend_de_la_fenetre = True
    _enregistrer_sur_la_feuille_par_defaut = True
    _marqueurs = "()"

    point1 = __point1 = Argument("Point_generique")
    point2 = __point2 = Argument("Point_generique")

    def __init__(self, point1, point2, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        Objet.__init__(self, **styles)
        #~ self._initialiser(point1 = Point_generique, point2 = Point_generique)


    def _longueur(self):
        return norme(self.__point2.x - self.__point1.x, self.__point2.y - self.__point1.y)


    def _espace_vital(self):
        x1, y1 = self.__point1.coordonnees
        x2, y2 = self.__point2.coordonnees
        return (min(x1, x2), max(x1, x2), min(y1, y2), max(y1, y2))


    def _get_equation(self):
        u"Retourne un triplet (a, b, c), tel que ax + by + c = 0 soit une équation de droite de la ligne."
        xA, yA = self.__point1.coordonnees
        xB, yB = self.__point2.coordonnees
        a, b, c = yA - yB, xB - xA, xA*yB - yA*xB
        while -1 < a < 1 and -1 < b < 1:
            a *= 10
            b *= 10
            c *= 10
        return (a, b, c)

    @property
    def equation_reduite(self):
        u"""Retourne (a, b) si la droite a une équation de la forme y=ax+b ; et (c,) si la droite a une équation de la forme x=c.

        Ceci permet de comparer facilement deux droites, ce qui n'est pas le cas avec la propriété .équation (puisqu'une droite a une infinité d'équations) : si d1._equation_reduite() ~ d2._equation_reduite, d1 et d2 sont (à peu près) confondues.
        """
        eq = self.equation
        if eq is None:
            return
        a, b, c = eq
        if abs(b) > contexte['tolerance'] :
            return (-a/b, -c/b)
        else:
            return (-c/a, )

    def _parallele(self, ligne):
        u"Indique si la ligne est parallèle à une autre ligne."
        if not isinstance(ligne, Ligne_generique):
            raise TypeError, "L'objet doit etre une ligne."
        a, b, c = self.equation
        a0, b0, c0 = ligne.equation
        return abs(a*b0 - b*a0) < contexte['tolerance']

    def _perpendiculaire(self, ligne):
        u"Indique si la ligne est perpendiculaire à une autre ligne."
        if not isinstance(ligne, Ligne_generique):
            raise TypeError, "L'objet doit etre une ligne."
        a, b, c = self.equation
        a0, b0, c0 = ligne.equation
        return abs(a*a0 + b*b0) < contexte['tolerance']

    def __iter__(self):
        return iter((self.__point1, self.__point2))


    def _creer_nom_latex(self):
        u"""Crée le nom formaté en LaTeX. Ex: M1 -> $M_1$."""
        Objet._creer_nom_latex(self)
        nom = self.nom_latex[1:-1]
        if re.match("(" + ALL.RE_NOM_DE_POINT + "){2}",  nom):
            self.nom_latex = "$" + self._marqueurs[0] + nom + self._marqueurs[1] + "$"
        else:
            nom = self.latex_police_cursive(nom)
            self.nom_latex = "$" + nom + "$"

    def pente(self, _type = False):
         # si flag = 1, retourne la "tendance" de la pente (verticale : 0, horizontale : 1)
        x1, y1 = self.__point1.coordonnees
        x2, y2 = self.__point2.coordonnees
        if _type:
            return 1 if (abs(x2 - x1) > abs(y2 - y1)) else 0
        try:
            return (y2 - y1)/(x2 - x1)
        except ZeroDivisionError:
            return

    def _x_y(self, nbr = 0, _flag = 1):
        # si flag = 1, donne le point (x,y) sur la droite en fonction de x.
        # si flag = 0, donne le point (x,y) sur la droite en fonction de y.
        [x1, y1], [x2, y2] = self.__point1.coordonnees, self.__point2.coordonnees

        # si la pente est presque verticale et que flag = 1, ou presque horizontale et que flag = 0, le calcul peut exploser... l'option flag = 2 adapte flag a la pente.
        if _flag == 2:
            _flag = self.pente(1)

        # dans le cas d'une droite horizontale ou verticale, flag est ignore et prend la seule valeur correcte :
        _flag = not (y1 - y2) and 1 or ((x1 - x2) and _flag or 0)

        if _flag:
            return (nbr,((y1-y2)*(nbr-x1)+(x1-x2)*y1)/(x1-x2))
        else:
            return (((x1-x2)*(nbr-y1)+(y1-y2)*x1)/(y1-y2),nbr)

    def _points(self):
        p = self.pente(1) # "tendance" de la pente (verticale : 0, horizontale : 1)
        fen = self.__canvas__.fenetre # il faut tracer depuis le bord de fenetre
        # Attention, la fenetre doit être récupérée depuis le canevas, et pas depuis la feuille (si le repère est orthonormé)
        x1, y1 = self._x_y((fen[2], fen[0])[p], p)
        x2, y2 = self._x_y((fen[3], fen[1])[p], p)
        return (x1, y1), (x2, y2)



class Segment(Ligne_generique):
    u"""Un segment.

    Un segment défini par deux points"""

    _affichage_depend_de_la_fenetre = False
    _style_defaut = param.segments
    _prefixe_nom = "s"
    _marqueurs = "[]"

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        Ligne_generique.__init__(self, point1 = point1, point2 = point2, **styles)
        self.etiquette = ALL.Label_segment(self)


    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.ligne(), self.rendu.ligne(), self.rendu.ligne(), self.rendu.ligne()]
        x1, y1 = self.__point1.coordonnees
        x2, y2 = self.__point2.coordonnees

        for elt_graphique in self._representation:
            elt_graphique._visible = True

        plot = self._representation[0]
        plot.set_data(numpy.array([x1, x2]), numpy.array([y1, y2]))
        plot._color = self.style("couleur")
        plot._linestyle = self.style("style")
        plot._linewidth = self.style("epaisseur")
        niveau = self.style("niveau")
        plot.zorder = niveau

        # Toute la suite concerne les codages utilisés pour indiquer les segments de même longueur
        if not self.style("codage"):
            for plot in self._representation[1:]:
                plot._visible = False
                plot.zorder = niveau + 0.01

        elif self.style("codage") == "o":
            plot = self._representation[1]
            plot._marker = "o"
            plot._markersize = param.codage["taille"]
            plot._markerfacecolor = 'None' # matplotlib 0.91.2
            plot._markeredgecolor = self.style("couleur")
            plot._markeredgewidth = self.style("epaisseur")
            plot.set_data([.5*(x1 + x2)], [.5*(y1 + y2)])
            for plot in self._representation[2:]:
                plot._visible = False

        else:
            A = numpy.array(self.__canvas__.coo2pix(x1, y1))
            B = numpy.array(self.__canvas__.coo2pix(x2, y2))
            G = .5*(B + A)
            r = param.codage["taille"]*param.zoom_ligne
            a = param.codage["angle"]
            vec = (A - B)/math.hypot(*(A - B))
            C = G + r*vec
            if self.style("codage") == "x":
                M = (numpy.dot([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]], numpy.transpose([C - G])) + numpy.transpose([G]))[:,0]
                N = (numpy.dot([[math.cos(a), math.sin(a)], [-math.sin(a), math.cos(a)]], numpy.transpose([C - G])) + numpy.transpose([G]))[:,0]
                plot1 = self._representation[1]
                plot2 = self._representation[2]
                plot1.set_data(*self.__canvas__.pix2coo(*array_zip(M, 2*G-M)))
                plot2.set_data(*self.__canvas__.pix2coo(*array_zip(N, 2*G-N)))
                plot1._marker = plot2._marker = 'None'
                plot1._color = plot2._color = self.style("couleur")
                plot1._linewidth = plot2._linewidth = self.style("epaisseur")
                self._representation[3]._visible = False

            elif self.style("codage") == "/":
                M = (numpy.dot([[math.cos(a), math.sin(a)], [-math.sin(a), math.cos(a)]], numpy.transpose([C - G])) + numpy.transpose([G]))[:,0]
                plot1 = self._representation[1]
                plot1.set_data(*self.__canvas__.pix2coo(*array_zip(M, 2*G-M)))
                plot1._marker = 'None'
                plot1._color = self.style("couleur")
                plot1._linewidth = self.style("epaisseur")
                for plot in self._representation[2:]:
                    plot._visible = False

            elif self.style("codage") == "//":
                M = (numpy.dot([[math.cos(a), math.sin(a)], [-math.sin(a), math.cos(a)]], numpy.transpose([C - G])) + numpy.transpose([G]))[:,0]
                plot1 = self._representation[1]
                plot2 = self._representation[2]
                vec = 2*vec
                plot1.set_data(*self.__canvas__.pix2coo(*array_zip(M + vec, 2*G - M + vec)))
                plot2.set_data(*self.__canvas__.pix2coo(*array_zip(M - vec, 2*G - M - vec)))
                plot1._marker = plot2._marker = 'None'
                plot1._color = plot2._color = self.style("couleur")
                plot1._linewidth = plot2._linewidth = self.style("epaisseur")
                self._representation[3]._visible = False

            elif self.style("codage") == "///":
                M = (numpy.dot([[math.cos(a), math.sin(a)], [-math.sin(a), math.cos(a)]], numpy.transpose([C - G])) + numpy.transpose([G]))[:,0]
                plot1 = self._representation[1]
                plot2 = self._representation[2]
                plot3 = self._representation[3]
                vec = 3*vec
                plot1.set_data(*self.__canvas__.pix2coo(*array_zip(M, 2*G - M)))
                plot2.set_data(*self.__canvas__.pix2coo(*array_zip(M + vec, 2*G - M + vec)))
                plot3.set_data(*self.__canvas__.pix2coo(*array_zip(M - vec, 2*G - M - vec)))
                plot1._marker = plot2._marker = plot3._marker = 'None'
                plot1._color = plot2._color = plot3._color = self.style("couleur")
                plot1._linewidth = plot2._linewidth = plot3._linewidth = self.style("epaisseur")



    def image_par(self, transformation):
        return Segment(self.__point1.image_par(transformation), self.__point2.image_par(transformation))


    def _distance_inf(self, x, y, d):
        return distance_segment((x, y), self._pixel(self.__point1), self._pixel(self.__point2), d)


    def _contains(self, M):
        #if not isinstance(M, Point_generique):
        #    return False
        A = self.__point1
        B = self.__point2
        xu, yu = vect(A, B)
        xv, yv = vect(A, M)
        if abs(xu*yv-xv*yu) > contexte['tolerance']:
            return False
        if abs(xu)  > abs(yu):
            k = xv/xu
        elif yu:
            k = yv/yu
        else:  # A == B
            return M == A
        return 0 <= k <= 1

    @property
    def longueur(self):
        u"""Longueur du segment.

        Alias de _longueur, disponible pour indiquer que l'objet a vraiment une longueur au sens mathématique du terme (pas comme une droite !)"""
        return self._longueur()

    @property
    def extremites(self):
        return self.__point1, self.__point2

    @property
    def info(self):
        return self.nom_complet + u' de longueur ' + nice_display(self.longueur)

    @staticmethod
    def _convertir(objet):
        if hasattr(objet,  "__iter__"):
            return Segment(*objet)
        raise TypeError, "'" + str(type(objet)) + "' object is not iterable"



class Demidroite(Ligne_generique):
    u"""Une demi-droite.

    Une demi-droite définie par son origine et un deuxième point"""

    _style_defaut = param.droites
    _prefixe_nom = "d"
    _marqueurs = "[)"

    origine = __origine = Argument("Point_generique", defaut = Point)
    point = __point = Argument("Point_generique", defaut = Point)

    def __init__(self, origine = None, point = None, **styles):
        self.__origine = origine = Ref(origine)
        self.__point = point = Ref(point)
        Ligne_generique.__init__(self, point1 = origine, point2 = point, **styles)
        self.etiquette = ALL.Label_demidroite(self)

    def image_par(self, transformation):
        return Demidroite(self.__point1.image_par(transformation), self.__point2.image_par(transformation))

    def _conditions_existence(self):
        return carre_distance(self.__origine, self.__point) > contexte['tolerance']**2
        # EDIT: les conditions d'existence en amont sont désormais bien définies (ou devraient l'être !!)
        # return [self.point1.coo is not None and self.point2.coo is not None and sum(abs(self.point1.coo - self.point2.coo)) > contexte['tolerance']]
        # si les conditions d'existence en amont sont mal definies, il se peut que les coordonnees d'un point valent None





    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.ligne()]

        x, y = self.__origine.coordonnees
        x0, y0 = self.__point.coordonnees
        (x1, y1), (x2, y2) = self._points()
        plot = self._representation[0]

        if produit_scalaire((x1 - x, y1 - y), (x0 - x, y0 - y)) > produit_scalaire((x2 - x, y2 - y), (x0 - x, y0 - y)):
            plot.set_data((x1, x), (y1, y))
        else:
            plot.set_data((x, x2), (y, y2))
        plot.set(color = self.style("couleur"), linestyle = self.style("style"), linewidth = self.style("epaisseur"), zorder = self.style("niveau"))


    def _distance_inf(self, x, y, d):
        # cf. "distance_point_segment.odt" dans "doc/developpeurs/maths/"
        xA, yA = self._pixel(self.__origine)
        xB, yB = self._pixel(self.__point)
        x1 = min(xA, xB); x2 = max(xA, xB)
        y1 = min(yA, yB); y2 = max(yA, yB)
        if (xA == x1 and x>x1-d or xA == x2 and x<x2+d) and (yA == y1 and y>y1-d or yA == y2 and y<y2+d):
            return ((yA - yB)*(x - xA)+(xB - xA)*(y - yA))**2/((xB - xA)**2+(yB - yA)**2) < d**2
        else:
            return False


    def _contains(self, M):
        #if not isinstance(M, Point_generique):
        #    return False
        A = self.__origine
        B = self.__point
        xu, yu = vect(A, B)
        xv, yv = vect(A, M)
        if abs(xu*yv - xv*yu) > contexte['tolerance']:
            return False
        if abs(xu) > abs(yu): # (AB) est plutôt horizontale
            k = xv/xu
        elif yu: # (AB) est plutôt verticale
            k = yv/yu
        else:  # A == B
            return M == A
        return 0 <= k


    @property
    def equation_formatee(self):
        u"Equation sous forme lisible par l'utilisateur."
        eq = self.equation
        if eq is None:
            return u"L'objet n'est pas défini."
        a, b, c = (nice_display(coeff) for coeff in eq)
        # on ne garde que quelques chiffres après la virgule
        pente = self.pente(1) # "tendance" de la pente (verticale : 0, horizontale : 1)
        if pente:
            if (self.__point.ordonnee - self.__origine.ordonnee) > contexte['tolerance']:
                ajout = "y > " + nice_display(self.__origine.ordonnee)
            elif (self.__point.ordonnee - self.__origine.ordonnee) < contexte['tolerance']:
                ajout = "y < " + nice_display(self.__origine.ordonnee)
            else:
                return u"Précision insuffisante."
        else:
            if (self.__point.abscisse - self.__origine.abscisse) > contexte['tolerance']:
                ajout = "x > " + nice_display(self.__origine.abscisse)
            elif (self.__point.abscisse - self.__origine.abscisse) < contexte['tolerance']:
                ajout = "x < " + nice_display(self.__origine.abscisse)
            else:
                return u"Précision insuffisante."
        return formatage("%s x + %s y + %s = 0 et %s" %(a, b, c, ajout))


    @staticmethod
    def _convertir(objet):
        if hasattr(objet,  "__iter__"):
            return Demidroite(*objet)
        raise TypeError, "'" + str(type(objet)) + "' object is not iterable"


class Droite_generique(Ligne_generique):
    u"""Une droite générique.

    Usage interne : la classe mère pour toutes les droites."""

    _style_defaut = param.droites
    _prefixe_nom = "d"

    parallele = Ligne_generique._parallele
    perpendiculaire = Ligne_generique._perpendiculaire

    point1 = __point1 = Argument("Point_generique")
    point2 = __point2 = Argument("Point_generique")

    def __init__(self, point1, point2, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        Ligne_generique.__init__(self, point1 = point1, point2 = point2, **styles)
        self.etiquette = ALL.Label_droite(self)

    def image_par(self, transformation):
        return Droite(self.__point1.image_par(transformation), self.__point2.image_par(transformation))

    def _conditions_existence(self):
        return carre_distance(self.__point1, self.__point2) > contexte['tolerance']**2




    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.ligne()]
        (x1, y1), (x2, y2) = self._points()
        plot = self._representation[0]
        plot.set_data((x1, x2), (y1, y2))
        plot.set(color = self.style("couleur"), linestyle = self.style("style"), linewidth = self.style("epaisseur"), zorder = self.style("niveau"))




#    def _creer_figure(self):
#        fen = self.__canvas__.fenetre # il faut tracer depuis le bord de fenetre
#        p = self.pente(1)
#        A, B = self.x_y((fen[2], fen[0])[p],p), self.x_y((fen[3], fen[1])[p],p)
#        self.__canvas__.Ligne(A, B, self.style("couleur"))

    def _distance_inf(self, x, y, d):
        # cf. "distance_point_segment.odt" dans "doc/developpeurs/maths/"
        xA, yA = self._pixel(self.__point1)
        xB, yB = self._pixel(self.__point2)
        return ((yA-yB)*(x-xA)+(xB-xA)*(y-yA))**2/((xB-xA)**2+(yB-yA)**2) < d**2



    def _contains(self, M):
        #if not isinstance(M, Point_generique):
        #    return False
        A = self.__point1
        B = self.__point2
        xu, yu = vect(A, B)
        xv, yv = vect(A, M)
        return abs(xu*yv-xv*yu) < contexte['tolerance']

    @property
    def equation_formatee(self):
        u"Equation sous forme lisible par l'utilisateur."
        eq = self.equation
        if eq is None:
            return u"L'objet n'est pas défini."
        a, b, c = (nice_display(coeff) for coeff in eq) # on ne garde que quelques chiffres après la virgule pour l'affichage
        return formatage("%s x + %s y + %s = 0" %(a, b, c))

    @property
    def info(self):
        return self.nom_complet + u" d'équation " + self.equation_formatee

    def __eq__(self,  y):
        if self.existe and isinstance(y, Droite_generique) and y.existe:
            eq1 = self.equation_reduite
            eq2 = y.equation_reduite
            if len(eq1) == len(eq2) == 1:
                return abs(eq1[0] - eq2[0]) < contexte['tolerance']
            elif len(eq1) == len(eq2) == 2:
                return abs(eq1[0] - eq2[0]) < contexte['tolerance'] and abs(eq1[1] - eq2[1]) < contexte['tolerance']
        return False

    def __ne__(self, y):
        return not self == y


    @staticmethod
    def _convertir(objet):
        if hasattr(objet,  "__iter__"):
            return Droite(*objet)
        raise TypeError, "'" + str(type(objet)) + "' object is not iterable"



class Droite(Droite_generique):
    u"""Une droite.

    Une droite définie par deux points"""


    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)

    def __new__(cls, *args, **kw):
        if len(args) == 1  and isinstance(args[0], basestring):
            newclass = Droite_equation
        elif len(args) == 2  and isinstance(args[1], ALL.Vecteur_generique):
            newclass = Droite_vectorielle
        else:
            return object.__new__(cls)
        droite = newclass.__new__(newclass, *args, **kw)
        droite.__init__(*args, **kw)
        return droite

    def __init__(self, point1 = None, point2 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        Droite_generique.__init__(self, point1 = point1, point2 = point2, **styles)



class Point_droite(Point_generique):
    u"""Un des deux points servant à construire une droite d'équation donnée.

    Usage interne.
    Ceci sert pour les droites qui ne sont pas définies à l'aide de points, mais directement à l'aide d'une équation.
    Comme l'implémentation actuelle des droites exige que la droite soit définie par 2 points,
    on génère deux points de la droite à partir de son équation."""

    droite = __droite = Argument("Droite_generique")
    premier = __premier = ArgumentNonModifiable("bool")

    def __init__(self, droite, premier, **styles):
        self.__droite = droite = Ref(droite)
        self.__premier = premier
        Point_generique.__init__(self, **styles)

    def _get_coordonnees(self):
        a, b, c = self.__droite.equation
        if b:
            if self.__premier:
                return 0, -c/b
            else:
                return 1, -a/b - c/b
        else:
            if self.__premier:
                return -c/a, 0
            else:
                return -c/a, 1



class Droite_vectorielle(Droite_generique):
    u"""Une droite dirigée par un vecteur.

    Une droite définie par un point et un vecteur directeur."""

    point = __point = Argument("Point_generique", defaut = Point)
    vecteur = __vecteur = Argument("Vecteur_generique", defaut = lambda:ALL.Vecteur_libre())

    def __init__(self, point = None, vecteur = None, **styles):
        self.__point = point = Ref(point)
        self.__vecteur = vecteur = Ref(vecteur)
        Objet.__init__(self) # pour pouvoir utiliser 'Point_droite(self, True)', l'objet doit déjà être initialisé
        Droite_generique.__init__(self, Point_droite(self, True), Point_droite(self, False), **styles)

    def _get_equation(self):
        a, b = self.__vecteur.coordonnees
        x, y = self.__point.coordonnees
        return -b, a, b*x - a*y

    def _conditions_existence(self):
        return self.__vecteur.x**2 + self.__vecteur.x**2 > contexte['tolerance']**2




class Parallele(Droite_generique):
    u"""Une parallèle.

    La parallèle à une droite passant par un point."""

    droite = __droite = Argument("Droite_generique")
    point = __point = Argument("Point_generique", defaut = Point)

    def __init__(self, droite, point = None, **styles):
        self.__droite = droite = Ref(droite)
        self.__point = point = Ref(point)
        Objet.__init__(self) # pour pouvoir utiliser 'Point_droite(self, True)', l'objet doit déjà être initialisé
        Droite_generique.__init__(self, Point_droite(self, True), Point_droite(self, False), **styles)

    def _get_equation(self):
        a, b, c = self.__droite.equation
        x, y = self.__point.coordonnees
        return a, b, -a*x-b*y

    def _conditions_existence(self):
        return True




##class Droite_rotation(Droite): # À REDÉFINIR
##    u"""Une image d'une droite par rotation.
##
##    Une droite obtenue par rotation d'une autre droite, ou d'un bipoint, ou..."""
##
##    droite = __droite = Argument("Droite")
##    rotation = __rotation = Argument("Rotation")
##
##    def __init__(self, droite, rotation, **styles):
##        self.__droite = droite = Ref(droite)
##        self.__rotation = rotation = Ref(rotation)
##        warning("A redefinir, voir commentaires dans le code.")
##        Droite.__init__(self, point1 = Point_rotation(droite._Droite__point1, rotation), point2 = Point_rotation(droite._Droite__point2, rotation), **styles)
##    # BUG : droite._Droite__point1 ne va pas, car si l'argument droite est modifié, la modification ne va pas se répercuter sur les arguments de Point_rotation
##
##    def  _get_coordonnees(self):
##         raise NotImplementedError
##


class Perpendiculaire(Droite_generique):
    u"""Une perpendiculaire.

    Une droite perpendiculaire à une autre passant par un point."""

    droite = __droite = Argument("Ligne_generique")
    point = __point = Argument("Point_generique", defaut = Point)

    def __init__(self, droite, point = None, **styles):
        self.__droite = droite = Ref(droite)
        self.__point = point = Ref(point)
        Objet.__init__(self) # pour pouvoir utiliser 'Point_droite(self, True)', l'objet doit déjà être initialisé
        Droite_generique.__init__(self, Point_droite(self, True), Point_droite(self, False), **styles)

    def _get_equation(self):
        a, b, c = self.__droite.equation
        x, y = self.__point.coordonnees
        return -b, a, b*x - a*y

    def _conditions_existence(self):
        return True


class Mediatrice(Perpendiculaire):
    u"""Une médiatrice.

    La médiatrice d'un segment (ou d'un bipoint, ...)

    >>> A=Point(1,2); B=Point(3,4); Mediatrice(A,B)
    >>> A=Point(1,2); B=Point(3,4); s=Segment(A,B); Mediatrice(s)
    """

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, **styles):
        if isinstance(point1, ALL.Segment):
            point2 = point1._Segment__point2
            point1 = point1._Segment__point1
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        Perpendiculaire.__init__(self, Droite(point1, point2), Milieu(point1, point2), **styles)


    def _conditions_existence(self):
        return carre_distance(self.__point1, self.__point2) > contexte['tolerance']**2








class Droite_equation(Droite_generique):
    u"""Une droite définie par une équation.

    Une droite d'équation donnée sous forme d'un triplet (a, b, c). (ax + by + c = 0)"""

    a = __a = Argument("Variable")
    b = __b = Argument("Variable")
    c = __c = Argument("Variable")

    @staticmethod
    def __coeff(match_object):
        if match_object is None:
            return 0
        chaine = match_object.group()
        if chaine == "-":
            return -1
        elif chaine == "+" or not chaine:
            return 1
        elif chaine[-1] == "*":
            chaine = chaine[:-1]
        return securite.eval_restricted(chaine)

    @classmethod
    def __extraire_coeffs(cls, chaine):
        a = cls.__coeff(re.search("[-+]*[^-+xy]*(?=x)", chaine))
        b = cls.__coeff(re.search("[-+]*[^-+xy]*(?=y)", chaine))
        c = cls.__coeff(re.search("[-+]*[^-+xy]+(?=$|[-+])", chaine))
        return a, b, c

    def __init__(self, a = 1,  b = -1,  c = 0, **styles):
        if isinstance(a, basestring):
            membre_gauche, membre_droite = a.replace(" ", "").split("=")
            a, b, c = self.__extraire_coeffs(membre_gauche)
            a_, b_, c_ = self.__extraire_coeffs(membre_droite)
            a -= a_
            b -= b_
            c -= c_
        self.__a = a = Ref(a)
        self.__b = b = Ref(b)
        self.__c = c = Ref(c)
        Objet.__init__(self) # pour pouvoir utiliser 'Point_droite(self, True)', l'objet doit déjà être initialisé
        Droite_generique.__init__(self, point1 = Point_droite(self, True), point2 = Point_droite(self, False), **styles)
#        self.equation = self.__a,  self.__b, self.__c


##    def verifier_coeffs(self, a,  b,  c):
##        if a == b == 0:
##            self.erreur(u"les deux premiers coefficients sont nuls.")

    def _conditions_existence(self):
        return not self.__a == self.__b == 0

#    def _get_equation(self):
#        # Retourne un triplet (a, b, c), tel que ax + by + c = 0 soit une equation de droite de la ligne.
#        # On peut aussi modifier l'equation de la droite.
#        xA, yA = self.__point1.coordonnees
#        xB, yB = self.__point2.coordonnees
#        return (yA - yB, xB - xA, xA*yB - yA*xB)

    def _set_equation(self, a = None,  b = -1,  c = 0):
        if a is not None:
#            self.verifier_coeffs(a, b, c)
            self.__a = a
            self.__b = b
            self.__c = c

    def _get_equation(self):
        return self.__a, self.__b, self.__c

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





class Bissectrice(Droite_vectorielle):
    u"""Une bissectrice.

    La bissectrice d'un angle défini par 3 points.
    On peut, au choix, entrer un angle ou 3 points comme argument."""

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)
    point3 = __point3 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, point3 = None, **styles):
        if isinstance(point1, ALL.Secteur_angulaire): # Au lieu de 3 points, on peut entrer un angle.
            point2 = point1._Secteur_angulaire__point
            point1 = Point_translation(point2, ALL.Translation(point1._Secteur_angulaire__vecteur1))
            point3 = Point_translation(point2, ALL.Translation(point1._Secteur_angulaire__vecteur2))
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__point3 = point3 = Ref(point3)

        v = ALL.Vecteur_unitaire(ALL.Vecteur(point2, point1)) + ALL.Vecteur_unitaire(ALL.Vecteur(point2, point3))
        Droite_vectorielle.__init__(self, point2, v, **styles)

    def _conditions_existence(self):
        return carre_distance(self.__point1, self.__point2) > contexte['tolerance']**2 and \
                    carre_distance(self.__point2, self.__point3) > contexte['tolerance']**2




class Point_tangence(Point_generique):
    u"""Un point de tangence.

    Le point de tangence d'un cercle et d'une droite tangente au cercle passant par un point donné.
    Usage interne."""

    cercle = __cercle = Argument("Cercle_generique")
    point = __point = Argument("Point_generique")

    def __init__(self, cercle, point, angle_positif = None, **styles):
        self.__cercle = cercle = Ref(cercle)
        self.__point = point = Ref(point)
        self.__angle_positif = angle_positif = Ref(angle_positif)
        self.__intersection = ALL.Intersection_cercles(cercle, ALL.Cercle_diametre(ALL.Centre(cercle), point), angle_positif)
        Point_generique.__init__(self, **styles)

    def _get_coordonnees(self):
        # on a deux cas :
        # si le point est sur le cercle, on prend le point
        # si le point n'est pas sur le cercle, on construit une intersection de cercles
        if self.__point in self.__cercle:
            return self.__point.coordonnees
        return self.__intersection.coordonnees

    def _conditions_existence(self):
        return self.__intersection.existe or self.__point in self.__cercle



class Tangente(Perpendiculaire):    # À REDÉFINIR ?
    u"""Une tangente.

    Une des deux tangentes à un cercle passant par un point extérieur au cercle.
    Le dernier paramètre (True/False) sert à distinguer les deux tangentes.
    (Voir la classe Intersection_cercles pour plus d'infos)."""

    cercle = __cercle = Argument("Cercle_generique", defaut = lambda: ALL.Cercle())
    point = __point = Argument("Point_generique", defaut = Point)
    angle_positif = __angle_positif = Argument("bool", defaut = True)

    def __init__(self, cercle = None, point = None, angle_positif = None, **styles):
        self.__cercle = cercle = Ref(cercle)
        self.__point = point = Ref(point)
        self.__angle_positif = angle_positif = Ref(angle_positif)
        self.point_tangence = self.__point_tangence = Point_tangence(cercle, point, angle_positif)
        Perpendiculaire.__init__(self, ALL.Droite(ALL.Centre(cercle), self.__point_tangence), self.__point_tangence, **styles)


    def _conditions_existence(self):
        return self.__point_tangence.existe


    def _set_feuille(self):
        # si l'on crée 2 fois de suite un tangente de mêmes cercle et point,
        # alors on doit obtenir les deux tangentes différentes possibles.
        if "_Tangente__angle_positif" in self._valeurs_par_defaut:
            for objet in self.__feuille__.objets.lister(type = Tangente):
                if objet._Tangente__cercle is self.__cercle and objet._Tangente__point is self.__point:
                    # on crée l'autre tangente
                    self.__angle_positif = not objet._Tangente__angle_positif
                    break
        if "_Tangente__point" in self._valeurs_par_defaut:
            if distance(self.__cercle.centre, self.__point) < self.__cercle.rayon:
                r = self.__cercle.rayon*module_random.uniform(1, 2)
                a = module_random.uniform(0, 2*math.pi)
                self.__point.coordonnees = self.__cercle.centre.x + r*math.cos(a), self.__cercle.centre.y + r*math.sin(a)
        Objet._set_feuille(self)








class DemiPlan(Objet_avec_equation):
    u"""Un demi-plan.

    Le demi-plan délimité par la droite d et contenant le point M."""

    _affichage_depend_de_la_fenetre = True
    _enregistrer_sur_la_feuille_par_defaut = True
    _marqueurs = "()"
    _style_defaut = param.polygones
    _prefixe_nom = "P"

    droite = __droite = Argument('Ligne_generique', defaut = Droite)
    point = __point = Argument('Point_generique', defaut = Point)
    droite_incluse = __droite_incluse = Argument(bool, defaut = True)

    def __init__(self, droite = None, point = None, droite_incluse = None, **styles):
        self.__droite = droite = Ref(droite)
        self.__point = point = Ref(point)
        self.__droite_incluse = droite_incluse = Ref(droite_incluse)
        Objet_avec_equation.__init__(self, **styles)


    def _get_equation(self):
        return self.__droite.equation


    @property
    def equation_formatee(self):
        u"Equation sous forme lisible par l'utilisateur."
        eq = self.equation
        if eq is None:
            return u"Le demi-plan n'est pas défini."
        test = self._signe()
        if test < 0:
            symbole = '<'
        elif test > 0:
            symbole = '>'
        else:
            return u"Le demi-plan n'est pas défini."
        a, b, c = (nice_display(coeff) for coeff in eq)
        # on ne garde que quelques chiffres après la virgule pour l'affichage
        if self.__droite_incluse:
            symbole += '='
        return formatage("%s x + %s y + %s %s 0" %(a, b, c, symbole))

    def _signe(self, xy = None):
        x, y = (xy if xy else self.__point.xy)
        a, b, c = self.equation
        return cmp(a*x + b*y + c, 0)

    def _contains(self, M):
        signe = self._signe(M)
        return  signe == self._signe() or (self.__droite_incluse and abs(signe) < contexte['tolerance'])

    def _conditions_existence(self):
        return self.__point not in self.__droite


    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.ligne(), self.rendu.polygone()]
        plot, fill = self._representation
        (x1, y1), (x2, y2) = self.__droite._points()
        plot.set_data((x1, x2), (y1, y2))
        couleur, niveau = self.style(('couleur', 'niveau'))
        plot.set(color = couleur, linestyle = self.style("style"), linewidth = self.style("epaisseur"), zorder = niveau + 0.01)
        xmin, xmax, ymin, ymax = self.__canvas__.fenetre
        fill.set(edgecolor = couleur, facecolor = couleur, alpha = self.style('alpha'), zorder = niveau)
        coins = [(xmin, ymin), (xmin, ymax), (xmax, ymin), (xmax, ymax)]
        sommets = [coin for coin in coins if (coin in self)]
        sommets.extend([(x1, y1), (x2, y2)])
        x0, y0 = (x1 + x2)/2, (y1 + y2)/2
        sommets.sort(key = lambda xy: math.atan2(xy[0] - x0, xy[1] - y0))
        fill.xy = sommets




##########################################################################################
## EN TRAVAUX :


class Tangente_courbe(Droite_generique):
    u"""Une tangente à une courbe.

    Une tangente à une courbe de fonction."""
    def __init__(self, courbe, point):
        Droite_generique.__init__(self, )
