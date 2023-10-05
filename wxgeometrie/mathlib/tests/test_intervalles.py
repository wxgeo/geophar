# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

from sympy import sqrt, pi

import wxgeometrie.mathlib.intervalles as intervalles
from wxgeometrie.mathlib.intervalles import Intervalle, Ensemble, \
                                            conversion_chaine_ensemble

import wx_unittest

class MathlibTest(wx_unittest.TestCase):

    def assert_intervalle_preformater(self, x, y):
        y_ = intervalles.preformatage_ensemble(x)
        if y_ != y:
            print("/!\\ Formule: ", x)
            print("ERREUR: ",  y_, " != ", y)
        self.assertEqual(y_, y)

    def test_preformater(self):
        self.assert_intervalle_preformater("R", "]-oo;+oo[")
        self.assert_intervalle_preformater("R+", "[0;+oo[")
        self.assert_intervalle_preformater("R+*", "]0;+oo[")
        self.assert_intervalle_preformater("R*-", "]-oo;0[")
        self.assert_intervalle_preformater("R*", "]-oo;+oo[-{0}")
        self.assert_intervalle_preformater("R-U{3}", "]-oo;0]+{3}")
        self.assert_intervalle_preformater("R-{3}", "]-oo;+oo[-{3}")
        self.assert_intervalle_preformater("R-{3}", "]-oo;+oo[-{3}")
        self.assert_intervalle_preformater("[0,1]U]1,2]", "[0;1]+]1;2]")
        # LaTeX
        self.assert_intervalle_preformater(r'[0\,;\,+\oo[', '[0;+oo[')

    def test_preformatage_geolib_ensemble(self):
        p = intervalles.preformatage_geolib_ensemble
        self.assertEqual(p('{2}'), ('{2}', ([],)))
        self.assertEqual(p(']-3;4'), (']-3;4[', (['4'],)))
        self.assertEqual(p('-5;'), (']-5;oo[', (['-5'],)))
        self.assertEqual(p('R*'), (']-oo;+oo[-{0}', ([],)))
        self.assertEqual(p('R+*'), (']0;+oo[', ([],)))
        self.assertEqual(p('{2;5}'), ('{2;5}', ([],)))
        self.assertEqual(p(']-1;1|2;3[U]4;6'), (']-1;1[|]2;3[+]4;6[', (['1'], ['2', '6'])))
        self.assertEqual(p(']1;2[+]1;2['), (']1;2[+]1;2[', ([],)))
        self.assertEqual(p('R-{1;2}'), (']-oo;+oo[-{1;2}', ([],)))


    def test_intervalle(self):
        self.assertEqual(str(Intervalle(8) + Intervalle(9)), '[8;+oo[')
        self.assertEqual(str(Intervalle("{0}")), '{0}')
        # Remplacement automatique de la virgule par un point si possible
        # FIXME: supprimer les décimales inutiles (zéros)
        self.assertEqual(str(Intervalle("[2,5;3,5]")), '[2.5;3.5]')
        # En cas d'ambiguité, la virgule reste un séparateur entre deux nombres
        self.assertEqual(str(Intervalle("R-{2,3}")), ']-oo;2[U]2;3[U]3;+oo[')

    def test_evalf(self):
        i = intervalles.conversion_chaine_ensemble(']-oo;-2]U[1/4;1/2[')
        self.assertEqual(str(i.evalf()), ']-oo;-2.0]U[0.25;0.5[')
        i = Intervalle(-sqrt(2), pi)
        self.assertEqual(str(i.evalf()), '[-1.4142135623731;3.14159265358979]')
        self.assertEqual(str(i.evalf(n = 3)), '[-1.41;3.14]')

    def test_asarray(self):
        i = intervalles.Ensemble('{2}')
        self.assertEqual(tuple(i.asarray(-10,10,.1)[0]), (2,))

    def test_conversion_chaine_ensemble(self):
        chaine = '{-(-216*2^(2/3)+4*(-3616+64*sqrt(8113))^(1/3)+2^(1/3)' \
                 '*(-3616+64*sqrt(8113))^(2/3))/(16*(-3616+64*sqrt(8113))^(1/3))}'
        attendu = "Ensemble('{(-2^(1/3)*(-3616 + 64*sqrt(8113))^(2/3) " \
                   "- 4*(-3616 + 64*sqrt(8113))^(1/3) + 216*2^(2/3))" \
                   "/(16*(-3616 + 64*sqrt(8113))^(1/3))}')"
        resultat = repr(conversion_chaine_ensemble(chaine, utiliser_sympy=True))
        self.assertEqual(resultat, attendu)

    def test_operations(self):
        I = Ensemble('[2;4]')
        J = Ensemble('[3;5[')
        self.assertEqual(I & J, Ensemble('[3;4]'))
        self.assertEqual(I*J, Ensemble('[3;4]'))
        self.assertEqual(I | J, Ensemble('[2;5['))
        self.assertEqual(I + J, Ensemble('[2;5['))
        self.assertEqual(I - J, Ensemble('[2;3['))
        self.assertEqual(J - I, Ensemble(']4;5['))
        self.assertEqual(-I, Ensemble(']-oo;2[U]4;+oo['))
        self.assertEqual(-J, Ensemble(']-oo;3[U[5;+oo['))
