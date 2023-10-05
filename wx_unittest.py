# -*- coding: utf-8 -*-

from unittest import TestCase as _TestCase
from wxgeometrie.mathlib.solvers import resoudre, positif, ensemble_definition

def _yellow(s):
    return '\033[0;33m' + s + '\033[0m'

def _green(s):
    return '\033[0;32m' + s + '\033[0m'

class TestCase(_TestCase):

    def __init__(self, *args, **kw):
        _TestCase.__init__(self, *args, **kw)

    def assertAlmostEqual(self, x, y, **kw):
        """
        extension récursive
        """
        if type(x) == type(y) and isinstance(x, (tuple, list)):
            for x_elt, y_elt in zip(x, y):
                self.assertAlmostEqual(x_elt, y_elt, **kw)
        else:
            _TestCase.assertAlmostEqual(self, x, y, **kw)

    # utiles au moins dans mathlib.test_solvers
    def assertEqualAny(self,result, list_of_acceptable_results):
        l = list_of_acceptable_results
        if all((result != r) for r in l):
            print('Other accepted results: %s' % l[1:] if len(l) > 1 else None)
            return self.assertEqual(result, l[0])
        return True

    # utiles au moins dans mathlib.test_solvers
    def assert_resoudre(self,x, y):
        if not isinstance(y, (list, tuple, set)):
            y = [y]
        if not self.assertEqualAny(str(resoudre(x)), y):
            print(_red('-> Test failed for %s' % repr(x)))
            self.assertFalse(True)

    # utiles au moins dans mathlib.test_solvers
    def assert_positif(self,x, y):
        self.assertEqual(str(positif(x)), y)

    # utiles au moins dans mathlib.test_solvers
    def assert_ens_def(self,x, y):
        self.assertEqual(str(ensemble_definition(x)), y)

    def assert_tableau(self, func, chaine, attendu, **options):
        resultat = func(chaine, **options)
        if resultat != attendu:
            print("-------")
            for i in range(min(len(resultat), len(attendu))):
                if resultat[i] != attendu[i]:
                    break
            resultat = resultat[:i] + _yellow(resultat[i:])
            attendu = attendu[:i] + _green(attendu[i:])
            print("ERREUR:")
            print("Expected output was:")
            print(attendu)
            print("While actual result is:")
            print(resultat)
            print("-------")
        self.assertEqual(resultat, attendu)

