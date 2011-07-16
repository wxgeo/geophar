# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                Intervalles                  #
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

import re, math
import numpy

from sympy import oo, sympify
from sympy.core.sympify import SympifyError

from ..pylib import print_error, str2
from .parsers import _convertir_latex_frac


class Ensemble(object):
    def __new__(cls, *args, **kw):
        if len(args) == 1 and isinstance(args[0], basestring):
            return conversion_chaine_ensemble(args[0], utiliser_sympy = True)
        instance = object.__new__(cls)
        instance._initialiser(*args, **kw)
        return instance


class Union(Ensemble):
    u"""Une union finie d'intervalles réels. Les valeurs numériques isolées sont converties en singletons.
    Lors de l'initialisation, elle est reecrite sous forme d'union disjointe et ordonnée.

    Les opération sur les unions d'intervalles sont :
    - l'union : symbole "A+B"
    - l'intersection : symbole "A*B"
    - la différence : symbole "A-B"
    - le complémentaire : symbole -A

    Note: l'inclusion et l'appartenance sont notées de manière identique:
    "y in A"
    "A in B".

    Note: pour des raisons pratiques, l'ensemble vide est considéré comme un intervalle (sic).
    """

    def _initialiser(self, *intervalles):
        self.intervalles = []

        if intervalles:
            for val in intervalles:
                if isinstance(val, Intervalle):
                    self.intervalles.append(val.__copy__()) # important (ne pas travailler sur les originaux) !
                elif hasattr(val,  "__iter__"):
                    self.intervalles += Union(*val).intervalles
                else:
                    self.intervalles.append(Intervalle(val, val))
            self.simplifier()
            if len(self.intervalles) == 1:
                self.inf = self.intervalles[0].inf
                self.sup = self.intervalles[0].sup
                self._inf_inclus = self.intervalles[0]._inf_inclus
                self._sup_inclus = self.intervalles[0]._sup_inclus
                # /!\ faire le changement de classe en dernier (à cause de 'self.intervalles')
                self.__class__ = Intervalle

        else: # ensemble vide
            self.inf = 0
            self.sup = 0
            self._inf_inclus = False
            self._sup_inclus = False
            self.__class__ = Intervalle

    @property
    def vide(self):
        return len(self.intervalles) == 0

    def __iter__(self):
        return iter(self.intervalles)

    def __add__(self, y):
        "union"
        if not isinstance(y, Union):
            y = Union(y)
        return Union(*(self.intervalles + y.intervalles))

    def __radd__(self, y):
        return self.__add__(y)

    def __mul__(self, y):
        "intersection"
        if not isinstance(y, Union):
            y = Union(y)
        if y.vide:
            return y
        else:
            return Union(*[i*j for i in self.intervalles for j in y.intervalles])

    def __pow__(self, y): # alias pour l'intersection (le symbole '^' rappelle vagument le symbole 'inter')
        return self.__add__(y)

    def __rmul__(self, y):
        self.__mul__(y)

    def __rpow__(self, y):
        self.__radd__(y)

    def simplifier(self):
        ints = [intervalle for intervalle in self.intervalles if not intervalle.vide]
        ints.sort()
        #print ints
        #print self.intervalles
        for i in range(len(ints) - 1):
            if float(ints[i].sup) > float(ints[i + 1].inf): # les intervalles se coupent
                if ints[i + 1].inf == ints[i].inf:
                    ints[i + 1]._inf_inclus = ints[i + 1].inf_inclus or ints[i].inf_inclus
                else:
                    ints[i + 1]._inf_inclus = ints[i].inf_inclus

                if ints[i + 1].sup == ints[i].sup:
                    ints[i + 1]._sup_inclus = ints[i + 1].sup_inclus or ints[i].sup_inclus
                elif float(ints[i + 1].sup) < float(ints[i].sup):
                    ints[i + 1].sup = ints[i].sup
                    ints[i + 1]._sup_inclus = ints[i].sup_inclus

                ints[i + 1].inf = ints[i].inf
                ints[i] = None

            elif ints[i].sup == ints[i + 1].inf and (ints[i].sup_inclus or ints[i + 1].inf_inclus):
                ints[i + 1].inf = ints[i].inf
                ints[i + 1]._inf_inclus = ints[i].inf_inclus
                ints[i] = None

        self.intervalles = [intervalle for intervalle in ints if intervalle is not None]

    def __str__(self):
        from .custom_functions import custom_str as str
        return "U".join(str(intervalle) for intervalle in self.intervalles).replace("}U{", " ; ")

    def __repr__(self):
        return "Ensemble(%s)" %repr(str(self))

    def __nonzero__(self):
        return not self.vide

    def __neg__(self):
        u"complémentaire"
        return reduce(lambda x, y: x*y, [-intervalle for intervalle in self.intervalles], Intervalle())

    def __pos__(self):
        return self

    def __sub__(self, y):
        return self*(-y) # "soustraction" peu naturelle ! ;)

    def __rsub(self, y):
        return (-self)*y

    def __eq__(self, y):
        if not isinstance(y, Union):
            if hasattr(y,  "__iter__"):
                try:
                    return self == Union(*y)
                except Exception:
                    print_error()
            return False
        elif len(self.intervalles) != len(y.intervalles):
            return False
        elif self.vide:
            return y.vide
        else:
            test = [i.inf == j.inf and i.sup == j.sup and i.inf_inclus == j.inf_inclus and i.sup_inclus == j.sup_inclus for (i, j) in zip(self.intervalles, y.intervalles)]
            return not (False in test)

    def __ne__(self, y):
        return not (self == y)

    def __contains__(self, y):
        if isinstance(y, self.__class__) and not isinstance(y, Intervalle):
            return reduce(lambda x, y: x and y, ((intervalle in self) for intervalle in y.intervalles), True)
        return reduce(lambda x, y: x or y, ((y in intervalle) for intervalle in self.intervalles))


    def extremites(self, _min, _max):
        u"""Retourne les extrémités de chaque intervalle.

        Chaque extrémité est donnée sous la forme de couples (_float, _str),
        où _str peut prendre les valeurs ".", ")", "(" ou "o".
        Exemple :
        >>> from mathlib.intervalles import conversion_chaine_ensemble
        >>> E = conversion_chaine_ensemble("]-oo;3[U]3;4]U]5;+oo[")
        >>> E.extremites(0, 10)
        [(3, 'o'), (4, '.'), (5, ')')]
        """

        extremites = []
        for intervalle in self.intervalles:
            if _min <= intervalle.inf <= _max:
                if extremites and extremites[-1][0] == intervalle.inf:
                    extremites[-1] = (intervalle.inf, "o")
                else:
                    extremites.append((intervalle.inf, intervalle.inf_inclus and "." or ")"))
            if _min <= intervalle.sup <= _max:
                extremites.append((intervalle.sup, intervalle.sup_inclus and "." or "("))
        return extremites

    @property
    def adherence(self):
        u"L'adhérence de l'ensemble (ie. le plus petit ensemble fermé qui le contienne)."
        return Union(Intervalle(intervalle.inf, intervalle.sup, True, True)
                                for intervalle in self.intervalles)

    def asarray(self, _min, _max, pas):
        u"""Génère une liste d'objets 'array', correspondant à chaque intervalle.

        On se limite à des valeurs comprises entre '_min' et '_max', avec le pas 'pas'."""
        arrays = []
        for intervalle in self.intervalles:
            inf = max(intervalle.inf, _min)
            sup = min(intervalle.sup, _max)
            a = numpy.arange(float(inf), float(sup), pas)
            # Il faut convertir inf et sup en float du fait de bugs de sympy.
            # En particulier, 1/0 == +oo (au lieu de NaN ou zoo) provoque des bugs
            # dans l'affichage de courbes style 1/x sur ]-oo;0[.
            if inf < sup or (intervalle.inf_inclus and intervalle.sup_inclus):
                a = numpy.append(a, float(sup))
            arrays.append(a)
        return arrays


    def evalf(self, n = 15, **options):
        u"Convertit les bornes de chaque intervalle en float."
        union = vide
        def evalf(nbr):
            if nbr in (-oo, +oo):
                return nbr
            elif hasattr(nbr, 'evalf'):
                return nbr.evalf(n, **options)
            return float(nbr)
        for intervalle in self.intervalles:
            union += Intervalle(evalf(intervalle.inf),
                                evalf(intervalle.sup),
                                inf_inclus = intervalle.inf_inclus,
                                sup_inclus = intervalle.sup_inclus
                                )
        return union





class Intervalle(Union):
    u"""Un intervalle réel non vide.
    Les opération sur les intervalles sont :
    - l'union : symbole "A+B"
    - l'intersection : symbole "A*B"
    - la différence : symbole "A-B"
    - le complémentaire : symbole -A
    """

    def _initialiser(self, inf = -oo, sup = oo, inf_inclus = True, sup_inclus = True):
        self.inf = inf
        self.sup = sup
        self._inf_inclus = inf_inclus
        self._sup_inclus = sup_inclus


    @property
    def inf_inclus(self):
        if self.inf == -oo:
            return False
        return self._inf_inclus

    @property
    def sup_inclus(self):
        if self.sup == oo:
            return False
        return self._sup_inclus

    @property
    def singleton(self):
        return self.sup == self.inf  and self.inf_inclus and self.sup_inclus

    @property
    def intervalles(self):
        # La conversion en 'float' est due à un bug de sympy 0.6.3
        if float(self.sup) < float(self.inf) or (self.sup == self.inf and not (self.inf_inclus and self.sup_inclus)):
            return []
        else:
            return [self]


    def __cmp__(self, y):
        c = cmp(float(self.inf), float(y.inf))
        if c:   return c
        else:   return cmp(float(self.sup), float(y.sup))


    def __mul__(self, y):
        u"intersection"
        if not isinstance(y, Union):
            y = Union(y)

        if y.vide:
            return y
        elif isinstance(y, Intervalle): # il s'agit de 2 intervalles
            if float(self.sup) < float(y.inf) or float(y.sup) < float(self.inf):
                return Union() # vide
            elif self.sup == y.inf and self.sup_inclus and y.inf_inclus:
                return Union(self.sup)
            elif self.inf == y.sup and self.inf_inclus and y.sup_inclus:
                return Union(self.inf)

            else: # les intervalles se coupent
                if float(self.inf) < float(y.inf):
                    inf = y.inf
                    inf_inclus = y.inf_inclus
                elif float(self.inf) > float(y.inf):
                    inf = self.inf
                    inf_inclus = self.inf_inclus
                else:
                    inf = self.inf
                    inf_inclus = self.inf_inclus and y.inf_inclus

                if float(y.sup) < float(self.sup):
                    sup = y.sup
                    sup_inclus = y.sup_inclus
                elif float(y.sup) > float(self.sup):
                    sup = self.sup
                    sup_inclus = self.sup_inclus
                else:
                    sup = self.sup
                    sup_inclus = self.sup_inclus and y.sup_inclus
                return Intervalle(inf, sup, inf_inclus, sup_inclus)

        else:
            return Union(*[self*i for i in y.intervalles])


    def __neg__(self):
        if self.vide:
            return Intervalle()
        return Intervalle(-oo, self.inf, False, not self.inf_inclus) + Intervalle(self.sup, oo, not self.sup_inclus)


    def __str__(self):
        from .custom_functions import custom_str as str
        if self.vide:
            return "{}"
        elif self.inf == self.sup:
            return "{%s}" %str(self.inf)
        return (self.inf_inclus and "[" or "]") + str(self.inf) + ";" + str(self.sup) + (self.sup_inclus and "]" or "[")

    def __unicode__(self):
        if self.vide:
            return u"\u00D8" # "Ø" ; u"\u2205" ne fonctionne pas sous Windows XP
        else:
            return unicode(str(self))

    def __copy__(self):
        return Intervalle(self.inf, self.sup, self._inf_inclus, self._sup_inclus)

    def __contains__(self, y):
        if self.vide:
            return isinstance(y, Union) and y.vide
        elif isinstance(y, self.__class__):
            condition_inf = float(self.inf) < float(y.inf) or (self.inf == y.inf and (self.inf_inclus or not y.inf_inclus))
            condition_sup = float(self.sup) > y.sup or (self.sup == y.sup and (self.sup_inclus or not y.sup_inclus))
            return condition_inf and condition_sup
        elif isinstance(y, Union):
            return reduce(lambda x, y: x and y, ((intervalle in self) for intervalle in y.intervalles), True)
        else:
            return float(self.inf) < float(y) < float(self.sup) or (y == self.inf and self.inf_inclus) or (y == self.sup and self.sup_inclus)





def preformatage_ensemble(chaine):
    u"""Formatage léger (qui reste humainement lisible)."""
    chaine = chaine.replace(" ", "").replace(",", ";")

    # Traduction du LaTeX
    # On enlève le \ devant les commandes latex mathématiques usuelles
    chaine = re.sub(r"\\(infty|e|pi|sin|cos|tan|ln|exp)", lambda m:m.group()[1:], chaine)
    # conversion de \frac, \dfrac et \tfrac
    chaine = _convertir_latex_frac(chaine)
    # TODO: tests unitaires pour le LaTeX

    chaine = chaine.replace('infty', 'oo').replace('inf', 'oo')

    chaine = re.sub(r"(?<![A-TV-Za-z_])(R\+\*|R\*\+)(?![A-TV-Za-z_{[(])", "]0;+oo[", chaine)
    chaine = re.sub(r"(?<![A-TV-Za-z_])(R-\*|R\*-)(?![A-TV-Za-z_{[(])", "]-oo;0[", chaine)
    chaine = re.sub(r"(?<![A-TV-Za-z_])R\+(?![A-TV-Za-z_{[(])", "[0;+oo[", chaine)
    chaine = re.sub(r"(?<![A-TV-Za-z_])R-(?![A-TV-Za-z_{[(])", "]-oo;0]", chaine)
    chaine = re.sub(r"(?<![A-TV-Za-z_])R\*(?![A-TV-Za-z_{[(])", "]-oo;+oo[-{0}", chaine)
    chaine = re.sub(r"(?<![A-TV-Za-z_])R(?![A-TV-Za-z_{[(])", "]-oo;+oo[", chaine)

    chaine = chaine.replace("\\", "-")
    chaine = chaine.replace(";[", ";oo[").replace("];", "]-oo;")

    chaine = re.sub("(?<=[][}{])U(?=[][}{])", "+", chaine)

    chaine = re.sub("(?<![A-Za-z])([Ii](nf)?)(?![A-Za-z])", "oo", chaine)
    return chaine


def preformatage_geolib_ensemble(chaine):
    u"""Cette fonction est destinée à un usage très spécifique dans geolib.

    Elle accepte une syntaxe beaucoup plus souple que la précédente,
    et indique si les extrémités des intervalles doivent être affichés ou non.
    Par exemple:
    ]1;2] -> afficher les extrémités de la courbe en 1 (arc) et en 2 (point).
    1;2] -> afficher l'extrémité en 2 (point), mais pas en 1.
    ]1;2 -> afficher l'extrémité en 1 (arc), mais pas en 2.
    """
    chaine = re.sub('[ ]+', ' ', chaine)
    chaine = chaine.replace(',', ';').replace('\\', '-')
    chaine = re.sub(r"(?<=[][])\+(?=[][])", 'U', chaine)

    extremites_cachees = []
    parties = chaine.split('|')

    for i, partie in enumerate(parties):
        extremites_cachees.append([])
        if re.match(r"R-[^][{}]+$", partie):
            partie = 'R-{' + partie[2:] + '}'
        intervalles = re.split(r'(?<=[][{} ])[U](?=[][{} ])', partie)

        for j, intervalle in enumerate(intervalles):
            intervalle = intervalle.replace(' ', '')
            appendice = ''
            if not intervalle.startswith('{'):
                # ie. intervalle != {1;2;3}
                if intervalle.startswith(';'):
                    # ]3; signifie ]3;+oo[
                    intervalle = ']' + intervalle
                if intervalle.endswith(';'):
                    # ;3[ signifie ]-oo;3[
                    intervalle += '['
                k = intervalle.find('-{')
                if k != -1:
                    appendice = intervalle[k:]
                    intervalle = intervalle[:k]
                    # ]-oo;+oo[-{1;2} est découpé en ]-oo;+oo[ (intervalle) et -{1;2} (appendice)
                if ';' in intervalle:
                    deb, fin = intervalle.split(';')
                    if deb and deb[0] not in '[]':
                        extremites_cachees[-1].append(deb)
                        intervalle = ']' + intervalle
                    if fin and fin[-1] not in '[]':
                        extremites_cachees[-1].append(fin)
                        intervalle += '['
            intervalles[j] = intervalle + appendice
        parties[i] = 'U'.join(intervalles)

    chaine = preformatage_ensemble('|'.join(parties))
    #print 'chaine, extremites cachees', chaine,  extremites_cachees
    return chaine or "]-oo;+oo[", tuple(extremites_cachees)


def formatage_ensemble(chaine, preformatage = True, utiliser_sympy = False):
    u"""Les symboles à utiliser sont 'U' pour l'union, '^' pour l'intersection, '-' ou '\\' pour la soustraction.
    R, R+, R*+, R-, R*- sont aussi acceptés."""

    if preformatage:
        chaine = preformatage_ensemble(chaine)

    def f1(matchobject): # conversion ]-2;sqrt(3)] -> Intervalle(-2, sqrt(3), False, True)
        chaine = matchobject.group()
        sep = chaine.find(";")
        return "Intervalle(%s,%s,%s,%s)" %(chaine[1:sep],chaine[sep+1:-1],chaine[0]=="[",chaine[-1]=="]")
    chaine = re.sub("[][][-+*/0-9.A-Za-z_)( ]+[;][-+*/0-9.A-Za-z_)( ]+[][]", f1, chaine)

    def f2(matchobject): # conversion {-1;2;sqrt(3)} -> Union(-1, 2, sqrt(3))
        chaine = matchobject.group()
        liste = chaine[1:-1].split(";")
        return "Union(%s)" %",".join(liste)
    chaine = re.sub("[{][-+*/0-9.A-Za-z)(;]+[}]", f2, chaine)

    return chaine





def conversion_chaine_ensemble(chaine, utiliser_sympy = False):
    chaine = formatage_ensemble(chaine)
    dico = {"__builtins__": None,
#            "Frac": Frac,
            "Intervalle": Intervalle,
            "Union": Union,
            "oo": oo,
            "False": False,
            "True": True,
            }
    dico.update(math.__dict__)
    if utiliser_sympy:
        try:
            #print str2(chaine), dico
            return sympify(str2(chaine), dico)
        except SympifyError:
            print "Warning: SympifyError in " + str2(chaine)
    return eval(str2(chaine), dico, dico)

IR = R = Intervalle()
O = vide = Union()
