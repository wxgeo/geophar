# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from pytest import XFAIL

#from tools.testlib import assertAlmostEqual
from wxgeometrie.geolib.tests.geotestlib import rand_pt
from tools.testlib import assertEqual
from wxgeometrie.geolib import Feuille, Segment

def test_Label_point():
    A = rand_pt()
    B = rand_pt()
    A.label("Position de l'hirondelle d'Afrique.")
    B.label(u"Position de l'hirondelle européenne.")
    assert(A.label() == "Position de l'hirondelle d'Afrique.")
    assert(B.label() == u"Position de l'hirondelle européenne.")
    A.label(mode='nom')
    assert A.mode_affichage == 'nom'
    assert(A.label() == '')
    f = Feuille()
    f.objets.A = A
    assert A.feuille is f
    assert A.etiquette.feuille is f
    assertEqual(A.nom_latex, '$A$')
    assertEqual(A.label(), '$A$')
    A.renommer("A'")
    assertEqual(A.label(), "$A'$")
    A.renommer("A''")
    assertEqual(A.label(), "$A''$")
    f.objets["B'"] = (1, 2)
    assertEqual(f.objets["B'"].label(), "$B'$")


def test_Label_segment():
    f = Feuille()
    s = f.objets.s = Segment()
    assert s.label() == ''
    s.label('bonjour !')
    assert s.label() == 'bonjour !'
    s.label(mode='nom')
    assertEqual(s.label(), r'$\mathscr{s}$')


@XFAIL
def test_Label_droite():
    raise NotImplementedError

@XFAIL
def test_Label_demidroite():
    raise NotImplementedError

@XFAIL
def test_Label_cercle():
    raise NotImplementedError

@XFAIL
def test_Label_arc_cercle():
    raise NotImplementedError

@XFAIL
def test_Label_polygone():
    raise NotImplementedError

@XFAIL
def test_Label_angle():
    raise NotImplementedError

def test_latex_incorrect():
    u"On teste le comportement en cas de code LaTeX incorrect."
    A = rand_pt()
    A.label('2$')
    assertEqual(A.label(), r'2\$')
    A.label('US$2.50')
    assertEqual(A.label(), r'US\$2.50')
    A.label('$M__i$')
    assertEqual(A.label(), r'\$M__i\$')
    A.label('2$')

def test_changement_mode():
    u"Test pour les issues FS#240 et FS#266."
    A = rand_pt()
    f = Feuille()
    f.objets.A = A
    A.label('-6', 'formule')
    assertEqual(A.label(), '-6')
    assertEqual(A.legende, '{-6}')
    A.label('-3', 'texte')
    assertEqual(A.legende, '-3')
    A.x = -7
    A.label('A.x', 'formule')
    assertEqual(A.legende, '{A.x}')
    assertEqual(A.label(), '-7')
    # Il ne doit pas y avoir d'erreur : le changement de mode doit être
    # effectué **avant** le changement de texte.
    A.label('-----', 'texte')
    assertEqual(A.legende, '-----')
    assertEqual(A.label(), '-----')
