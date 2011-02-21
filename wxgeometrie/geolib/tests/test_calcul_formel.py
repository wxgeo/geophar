# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from geolib.tests.geotestlib import *
from geolib import (Point, Vecteur, Droite, Intersection, Cercle, Segment, Disque,
                    Homothetie, Rotation, Translation, Reflexion, Vecteur, Variable,
                    Variable_generique,
                    contexte, TYPES_NUMERIQUES
                    )
from sympy import S, Expr
from numpy import array

l = locals

def allsym(val):
    return (isinstance(val, Expr) or (isinstance(val, Variable_generique) and allsym(val.val))
            or all(isinstance(x, Expr) for x in val))

def allnum(val):
    return (isinstance(val, TYPES_NUMERIQUES) or (isinstance(val, Variable_generique) and allnum(val.val))
            or all(isinstance(x, TYPES_NUMERIQUES) for x in val))

def assert_eq_num(*vals):
    for val in vals:
        assert allnum(val)
    assert vals.count(vals[0]) == len(vals)

def tofloat(x):
    if hasattr(x, '__iter__'):
        return x.__class__(tofloat(x) for x in x)
    else:
        return float(x)

def eq(x, y):
    if contexte['exact']:
        return x == y
    else:
        if hasattr(x, '__iter__') and hasattr(y, '__iter__'):
            return all(eq(i, j) for i, j in zip(x, y))
        else:
            return abs(x - y) < contexte['tolerance']




def assert_eq(*args):
    assert len(args) > 2
    locals_ = args[-1]
    expected = S(args[-2])
    args = args[:-2]
    for exact in (True, False):
        if not exact:
            expected = tofloat(expected)
        with contexte(exact=exact):
            for arg in args:
                val = eval(arg, locals_)
                TEST = (allsym(val) if exact else allnum(val))
                if not TEST:
                    print(repr(val) + ' should only contain %s.' %('exact values' if exact else 'floats'))
                assert TEST
                TEST = eq(val, expected)
                if not TEST:
                    print("'%s' equals to '%s', not '%s'." %(arg, repr(val), repr(expected)))
                assert TEST



def test_Segment():
    A = Point('1/2', '3/4')
    B = Point('pi', 'pi')
    C = Point(S('1/2'), S('3/4'))
    assert_eq("A.coordonnees", "C.coordonnees", "(1/2, 3/4)", l())
    assert_eq('B.coordonnees', '(pi, pi)', l())
    s = Segment(A, B)
    assert_eq('s.longueur', '((1/2 - pi)**2 + (3/4 - pi)**2)**(1/2)', l())


def test_eqn_formatee():
    c = Cercle(('1/2', '2/3'), 'sqrt(2)')
    assert c.equation_formatee == u'x\xb2 + y\xb2 - x - 4/3 y - 47/36 = 0'
    d = Droite(('0','0'),('1','1'))
    assert d.equation_formatee == '-x + y = 0'
    e=Droite(('1', '0'), ('2/3','1'))
    assert e.equation_formatee == '-x - 1/3 y + 1 = 0'


def test_Intersection():
    c = Cercle(('1/2', '2/3'), 'sqrt(2)')
    assert_eq('c.diametre', '2*2**(1/2)', l())
    d = Droite(('0','0'),('1','1'))
    assert_eq('d._longueur()', '2**(1/2)', l())
    e=Droite(('1', '0'), ('2/3','1'))
    assert_eq('e._longueur()', '10**(1/2)/3', l())
    c1 = Cercle(('1/3', '3'), 'pi')
    assert_eq('c1.diametre', '2*pi', l())
    assert_eq('c1.perimetre', '2*pi**2', l())
    d1 = Disque(c1)
    assert_eq('d1.aire', 'pi**3', l())
    # Droite/droite
    M = Intersection(d, e)
    assert_eq('M.coordonnees', '(3/4, 3/4)', l())
    # Cercle/droite
    I = Intersection(c, d)
    assert_eq('I.coordonnees', '(7/12 - 143**(1/2)/12, 7/12 - 143**(1/2)/12)', l())
    assert_eq_num(I.coordonnees_approchees, (-0.41318839525844997, -0.41318839525844997))
    # Cercle/cercle
    J = Intersection(c, c1)
    assert_eq('J.coordonnees', '(913/2364 - 98*(212563/12348 + (913/1176 + 3*pi**2/98)**2'
                            '- 394*pi**2/343 - 197*(125/56 - 3*pi**2/14)**2/49)**(1/2)/197'
                             '+ 3*pi**2/197,'
                             '2671/1182 - 7*(212563/12348 + (913/1176 + 3*pi**2/98)**2'
                             '- 394*pi**2/343 - 197*(125/56 - 3*pi**2/14)**2/49)**(1/2)/197'
                             '- 42*pi**2/197)', l())

def test_transformation():
    c = Cercle(('1/5', '4/5'), '1/3')
    h = Homothetie(('1', '1'), '5/7')
    v = Vecteur(c.centre, h.centre)
    c1 = h(c)
    v1 = Vecteur(c1.centre, h.centre)
    assert v1.coordonnees == tuple(h.rapport*array(v.coordonnees))
    assert_eq('c1.centre.coordonnees', '(3/7, 6/7)', l())
    assert_eq('c1.rayon', '5/21', l())
    c.rayon = '2'
    assert_eq('c1.rayon', '10/7', l())
