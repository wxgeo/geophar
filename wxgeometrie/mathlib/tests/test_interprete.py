# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

import re

from sympy import S

from wxgeometrie.mathlib.interprete import Interprete
from wxgeometrie.mathlib.printers import custom_str

VERBOSE = False

import tools.unittest, unittest

class MathlibTest(tools.unittest.TestCase):

    def assert_resultat(self, s, resultat, latex = None, **parametres):
        i = Interprete(verbose=VERBOSE, **parametres)
        r, l = i.evaluer(s)
        if r != resultat:
            i = Interprete(verbose = True, **parametres)
            r, l = i.evaluer(s)
            print("\nERREUR (" + s + "):\n", r, "\n!=\n",  resultat, '\n')
        self.assertEqual(r, resultat)
        if latex is not None:
            latex = "$" + latex + "$"
            if l != latex:
                print("\nERREUR (" + s + "):\n", l, "\n!=\n",  latex, '\n')
            self.assertEqual(l, latex)

    def assert_resoudre(self, s, *args, **kw):
        self.assert_resultat("resoudre(" + s + ")", *args, **kw)

    def assert_approche(self, s, resultat, latex = None, **parametres):
        self.assert_resultat(s, resultat, latex, calcul_exact = False, **parametres)

    def assert_ecriture_scientifique(self, s, resultat, latex=None, decimales=3, **parametres):
        self.assert_resultat(s, resultat, latex,
                        calcul_exact=False, ecriture_scientifique=True,
                        ecriture_scientifique_decimales=decimales, **parametres)

    #~ def assertEqual(self, x, y):
        #~ if x != y:
            #~ print "ERREUR:", repr(x), "!=", repr(y)
        #~ self.assertEqual(x, y)

    def assertDernier(self, i, s):
        self.assertEqual(custom_str(i.derniers_resultats[-1]), s)

    def test_exemples_de_base_nombres(self):
        self.assert_resultat('2+2', '4', '4')
        self.assert_resultat('0,1^10', '1,0*10^-10', r'10^{-10}')

    def test_exemples_de_base_symboles(self):
        self.assert_resultat('pi+1+2pi', '1 + 3 pi', '1 + 3 \\pi')
        self.assert_resultat('oo+5*oo', '+oo')
        self.assert_resultat('i**2-i', '-1 - i', '-1 - \\mathrm{i}')
        self.assert_resultat('5e-3', '-3 + 5 e', '-3 + 5 \\mathrm{e}')

    def test_exemples_de_base_analyse(self):
        self.assert_resultat('limite(x^2-x+3, +oo)', '+oo', '+\\infty')
        self.assert_resultat('derive(x^2+2x-3)', '2 x + 2', '2 x + 2')
        self.assert_resultat('integre(2x+7)', 'x^2 + 7 x', 'x^{2} + 7 x')
        self.assert_resultat('integre(x+1, (x, -1, 1))', '2', '2')
        self.assert_resultat('integre(x+1, x, -1, 1)', '2', '2')
        self.assert_resultat('taylor(sin x, x, 0, 4)', 'x - x^3/6 + O(x^4)', \
                    r'x - \frac{x^{3}}{6} + \mathcal{O}\left(x^{4}\right)')
        self.assert_resultat('cos x>>taylor', \
                    '1 - x^2/2 + x^4/24 + O(x^5)', \
                   r'1 - \frac{x^{2}}{2} + \frac{x^{4}}{24} + \mathcal{O}\left(x^{5}\right)')
        self.assert_resultat('limit(x^2-x, oo)', '+oo', '+\infty')

    def test_exemples_de_base_algebre(self):
        self.assert_resultat('developpe((x-3)(x+7)(2y+x+5))', \
                                        'x^3 + 2 x^2 y + 9 x^2 + 8 x y - x - 42 y - 105', \
                                        'x^{3} + 2 x^{2} y + 9 x^{2} + 8 x y - x - 42 y - 105')
        self.assert_resultat('factorise(x^2-7x+3)', \
                     '(x - 7/2 - sqrt(37)/2)(x - 7/2 + sqrt(37)/2)',
                    r'\left(x - \frac{7}{2} - \frac{\sqrt{37}}{2}\right) '
                    r'\left(x - \frac{7}{2} + \frac{\sqrt{37}}{2}\right)')
        self.assert_resultat('factorise(x^2+x)', 'x(x + 1)',  'x \\left(x + 1\\right)')
        self.assert_resultat('factor(exp(x)x^2+5/2x*exp(x)+exp(x))', '(x + 1/2)(x + 2)exp(x)')
        ##self.assert_resultat('factor(exp(x)x^2+2.5x*exp(x)+exp(x))', '(x + 0,5)(x + 2)exp(x)')
        self.assert_resultat('factor(exp(x)x^2+2.5x*exp(x)+exp(x))', '(x + 1/2)(x + 2)exp(x)')
        self.assert_resultat('factorise(exp(2x)*x^2+x*exp(x))', \
                                        'x(x exp(x) + 1)exp(x)',  \
                                        'x \\left(x \\mathrm{e}^{x} + 1\\right) \\mathrm{e}^{x}')
        self.assert_resultat('factorise(x^2+7x+53)', 'x^2 + 7 x + 53', 'x^{2} + 7 x + 53')
        self.assert_resultat('factor(exp(x)x^2+2x*exp(x)+exp(x))', \
                                        '(x + 1)^2 exp(x)', \
                                        '\left(x + 1\\right)^{2} \\mathrm{e}^{x}')
        self.assert_resultat('evalue(pi-1)', '2,14159265358979324', '2,14159265358979324')
        self.assert_resultat('somme(x^2, (x, 1, 7))', '140', '140')
        self.assert_resultat('somme(x^2, x, 1, 7)', '140', '140')
        self.assert_resultat('product(x^2, (x, 1, 7))', '25401600', '25401600')
        self.assert_resultat('product(x^2;x;1;7)', '25401600', '25401600')

    def test_exemples_de_base_supplementaires(self):
        self.assert_resultat('abs(pi-5)', '5 - pi', r'5 - \pi')
        self.assert_resultat('abs(x-5)', 'abs(x - 5)', r'\left|{x - 5}\right|')
        self.assert_resultat('i(1+i)', r'-1 + i',  r'-1 + \mathrm{i}')
        self.assert_resultat('i sqrt(3)', r'sqrt(3)i',  r'\sqrt{3} \mathrm{i}')
        self.assert_resultat('pi sqrt(3)', r'sqrt(3)pi',  r'\sqrt{3} \pi')
        self.assert_resultat('sqrt(1+e)', r'sqrt(1 + e)',  r'\sqrt{1 + \mathrm{e}}')
        self.assert_resultat('(5-2i)(5+2i)', r'29',  r'29')
        self.assert_resultat('resous(2x=1)', r'{1/2}',  r'\left\{\frac{1}{2}\right\}')
        self.assert_resultat('jhms(250000)', r'2 j 21 h 26 min 40 s',
                        r'2 \mathrm{j}\, 21 \mathrm{h}\, 26 \mathrm{min}\, 40 \mathrm{s}')
        self.assert_resultat(r'pi\approx', r'3,14159265358979324',  r'3,14159265358979324',
                        formatage_LaTeX=True)
        self.assert_resultat('rassemble(1/x+1/(x*(x+1)))', '(x + 2)/(x^2 + x)', r'\frac{x + 2}{x^{2} + x}')
        self.assert_resultat('factorise(-2 exp(-x) - (3 - 2 x)exp(-x))', '(2 x - 5)exp(-x)',
                        r'\left(2 x - 5\right) \mathrm{e}^{- x}')
        self.assert_resultat('-x^2+2x-3>>factor', '-x^2 + 2 x - 3')
        self.assert_resultat('abs(-24/5 - 2 i/5)', '2 sqrt(145)/5')
        self.assert_resultat('+oo - 2,5', '+oo', r'+\infty')

    @unittest.expectedFailure
    def test_exemples_de_base_canonique(self):
        """
        canonique ne fonctionne pas comme prévu ci-dessous
        """
        self.assert_resultat('canonique(x**2+5*x)', '(x + 5/2)^2 - 25/4', r'\left(x + \frac{5}{2}\right)^{2} - \frac{25}{4}')

    def test_ecriture_decimale_periodique(self):
        self.assert_resultat('0,[3]', '1/3', r'\frac{1}{3}')
        self.assert_resultat('0,1783[3]', '107/600', r'\frac{107}{600}')

    @unittest.expectedFailure
    def test_issue_270(self):
        """Bug 270: les décimaux s'affichent parfois en écriture scientifique.

        Exemple avec 3 chiffres significatifs:

            Calcul n°59 : 160000000000700,4
            Résultat : 160000000000700

            Calcul n°60 : 16000000000700,4
            Résultat : 1,6*10^13
        """
        i = Interprete(precision_affichage=3)
        r, l = i.evaluer("160000000000700,4")
        self.assertEqual(r, "160000000000700") # 1,6*10^14 environ
        r, l = i.evaluer("16000000000700,4")
        self.assertEqual(r, "16000000000700") # 1,6*10^13 environ

    def test_ensemble_complexe(self):
        i = Interprete(verbose=VERBOSE, ensemble='C')
        r, l = i.evaluer("resoudre(x^2=-1")
        self.assertIn(r, ('{i ; -i}', '{-i ; i}'))
        self.assertIn(l, (r'$\left\{- \mathrm{i}\,;\,\mathrm{i}\right\}$',
                     r'$\left\{\mathrm{i}\,;\,- \mathrm{i}\right\}$'))
        r, l = i.evaluer("resoudre(2+\i=\dfrac{2\i z}{z-1}")
        self.assertEqual(r, '{3/5 + 4 i/5}')
        self.assertEqual(l, r'$\left\{\frac{3}{5} + \frac{4}{5} \mathrm{i}\right\}$')
        r, l = i.evaluer("resoudre(x^2=-1 et 2x=-2i")
        self.assertEqual(r, '{-i}')
        self.assertEqual(l, r'$\left\{- \mathrm{i}\right\}$')
        r, l = i.evaluer('factorise(x^2+7x+53)')
        self.assertEqual(r, '(x + 7/2 - sqrt(163)i/2)(x + 7/2 + sqrt(163)i/2)')
        self.assertEqual(l, r'$\left(x + \frac{7}{2} - \frac{\sqrt{163} \mathrm{i}}{2}\right) '
                       r'\left(x + \frac{7}{2} + \frac{\sqrt{163} \mathrm{i}}{2}\right)$')



    def test_fonctions_avances(self):
        pass

    def test_frac(self):
        self.assert_resultat('frac(0,25)', '1/4', r'\frac{1}{4}')
        self.assert_resultat('frac(0,333333333333333)', '1/3', r'\frac{1}{3}')

    def test_resoudre(self):
        self.assert_resoudre('2x+3>5x-4 et 3x+1>=4x-4', r']-oo ; 7/3[')
        self.assert_resoudre('2=-a+b et -1=3a+b', r'{a: -3/4 ; b: 5/4}')
        self.assert_resoudre(r'3-x\ge 1+2x\\\text{et}\\4x<2+10x', ']-1/3 ; 2/3]',
                        r'\left]- \frac{1}{3};\frac{2}{3}\right]', formatage_LaTeX=True)
        self.assert_resoudre('2exp(x)>3', ']-ln(2) + ln(3) ; +oo[')
        #TODO: Rassembler les ln: ]ln(3/2);+oo[
        self.assert_resoudre('x^3-30x^2+112=0', '{14 - 6 sqrt(7) ; 2 ; 14 + 6 sqrt(7)}',
                    r'\left\{14 - 6 \sqrt{7}\,;\, 2\,;\, 14 + 6 \sqrt{7}\right\}')
        # self.assert_resoudre(r'ln(x^2)-ln(x+1)>1', ']-1;e/2 - sqrt(4 e + exp(2))/2[U]e/2 + sqrt(4 e + exp(2))/2;+oo[')
        self.assert_resoudre('0.5 exp(-0.5 x + 0.4)=0.5', '{4/5}')
        self.assert_resoudre('x > 9 et x < 9', '{}', r'\varnothing')


    #TODO: @SLOW wrapper should be defined, and the test only run in some circonstances
    # (for ex, a 'slow' keyword in tools/tests.py arguments)
    def test_longs(self):
        # NB: Tests relativement longs (> 5 secondes environ)
        self.assert_resoudre(r'ln(x^2)-ln(x+1)>1', ']-1 ; -sqrt(e + 4)exp(1/2)/2 + e/2[U]e/2 + sqrt(e + 4)exp(1/2)/2 ; +oo[')

    def test_approches(self):
        self.assert_approche('pi-1', '2,14159265358979324', '2,14159265358979324')
        self.assert_approche('factor(x^2+2.5x+1)', '(x + 0,5)(x + 2)')
        self.assert_approche('factor(exp(x)x^2+2.5x*exp(x)+exp(x))', '(x + 0,5)(x + 2)exp(x)')
        self.assert_approche('ln(2.5)', '0,916290731874155065')
        self.assert_approche('ln(2,5)', '0,916290731874155065')
        self.assert_approche('resoudre(x^3-30x^2+112=0)',
                        '{-1,87450786638754354 ; 2 ; 29,8745078663875435}',
                        r'\left\{-1,87450786638754354\,;\, 2\,;\, 29,8745078663875435\right\}')

    def test_ecriture_scientifique(self):
        self.assert_ecriture_scientifique('25470', '2,55*10^4', r'2,55 \times 10^{4}', decimales=2)
        self.assert_ecriture_scientifique('pi/1000', '3,14159265*10^-3', r'3,14159265 \times 10^{-3}', decimales=8)

    def test_session(self):
        i = Interprete(verbose=VERBOSE)
        i.evaluer("1+7")
        i.evaluer("x-3")
        i.evaluer("ans()+ans(1)")
        self.assertDernier(i, "x + 5")
        i.evaluer("f(x, y, z)=2x+3y-z")
        i.evaluer("f(-1, 5, a)")
        self.assertDernier(i, "13 - a")
        i.evaluer("f(x)=x^2-7x+3")
        i.evaluer("f'(x)")
        self.assertDernier(i, "2*x - 7")

        # Noms réservés
        self.assertRaises(NameError, i.evaluer, "e=3")
        self.assertRaises(NameError, i.evaluer, "pi=3")
        self.assertRaises(NameError, i.evaluer, "i=3")
        self.assertRaises(NameError, i.evaluer, "oo=3")
        self.assertRaises(NameError, i.evaluer, "factorise=3")
        # Etc.

        # Test des générateurs
        i.evaluer('f(x)=x+3')
        # La ligne suivante doit simplement s'exécuter sans erreur.
        i.evaluer('[f for j in range(1, 11)]')
        i.evaluer('[f(j) for j in range(1, 11)]')
        self.assertDernier(i, '[4, 5, 6, 7, 8, 9, 10, 11, 12, 13]')
        i.evaluer('tuple(i for i in range(7))')
        self.assertDernier(i, '(0, 1, 2, 3, 4, 5, 6)')
        i.evaluer('[j for j in range(7)]')
        self.assertDernier(i, '[0, 1, 2, 3, 4, 5, 6]')

        # _12 is an alias for ans(12)
        i.evaluer('_12 == _')
        self.assertDernier(i, 'True')
        i.evaluer('_7')
        self.assertDernier(i, "2*x - 7")
        # _ is an alias for ans(-1), __ is an alias for ans(-2), and so on.
        i.evaluer('_ == -7 + 2*x')
        self.assertDernier(i, 'True')
        i.evaluer('__')
        self.assertDernier(i, "2*x - 7")
        i.evaluer('______') # ans(-6)
        self.assertDernier(i, '(0, 1, 2, 3, 4, 5, 6)')

        # Affichage des chaînes en mode text (et non math)
        i.evaluer('"Bonjour !"')
        self.assertEqual(i.latex_dernier_resultat, '\u201CBonjour !\u201D')

        # Virgule comme séparateur décimal
        resultat, latex = i.evaluer('1,2')
        self.assertEqual(resultat, '1,2')
        self.assertAlmostEqual(i.derniers_resultats[-1], 1.2)
        # Avec un espace, c'est une liste (tuple) par contre
        resultat, latex = i.evaluer('1, 2')
        self.assertEqual(resultat, '(1 ; 2)')
        resultat, latex = i.evaluer('"1.2"')
        self.assertEqual(resultat, '"1.2"')
        i.evaluer('?aide')
        i.evaluer('aide?')
        i.evaluer('aide(aide)')
        msg_aide = "\n== Aide sur aide ==\nRetourne (si possible) de l'aide sur la fonction saisie."
        resultats = i.derniers_resultats
        self.assertEqual(resultats[-3:], [msg_aide, msg_aide, msg_aide])

        # LaTeX
        latex = i.evaluer("gamma(x)")[1]
        self.assertEqual(latex, r'$\Gamma\left(x\right)$')

        # Vérifier qu'on ait bien ln(x) et non log(x) qui s'affiche
        resultat, latex = i.evaluer('f(x)=(ln(x)+5)**2')
        self.assertEqual(resultat, 'x -> (ln(x) + 5)^2')
        self.assertEqual(latex, r'$x\mapsto \left(\ln(x) + 5\right)^{2}$')


    def test_matrix_special_syntax(self):
        i = Interprete(verbose=VERBOSE)
        i.evaluer("mat A = 1 2 3  4 5 6  7 8 9")
        i.evaluer(" mat  B=  1   0   0  ")
        resultat, latex = i.evaluer("C=A*B")
        self.assertEqual(resultat, 'Matrix([\n[1] ; \n[4] ; \n[7]])')

    def test_matrix_special_syntax_latex(self):
        i = Interprete(verbose=VERBOSE)
        i.evaluer("mat A = 1&2&3\\4&5&6\\7&8&9")
        i.evaluer("mat B = 1\\0\\0")
        resultat, latex = i.evaluer("C=A*B")
        self.assertEqual(resultat, 'Matrix([\n[1] ; \n[4] ; \n[7]])')

    def test_issue_sialle1(self):
        # Problème : Si on tape 1/(1-sqrt(2)), on obtient le résultat 1/-sqrt(2)+1,
        # qui est faux (il manque les parenthèses...).
        self.assert_resultat("1/(1-sqrt(2))", "1/(1 - sqrt(2))")

    def test_1_pas_en_facteur(self):
        self.assert_resultat("together(1/x-.5)", "(2 - x)/(2 x)", r"\frac{2 - x}{2 x}")

    def test_issue_129(self):
        self.assert_resultat('"x(x+1)" + """x!"""', '"x(x+1)x!"')
        self.assert_resultat(r'""" "" """ + " \"\"\" "', r'" \"\"  \"\"\" "')

    def test_issue_129bis(self):
        self.assert_resultat("'1.2345'", '"1.2345"')
        self.assert_resultat("'x(x+1)'", '"x(x+1)"')


    def test_issue_185(self):
        i = Interprete(verbose=VERBOSE)
        i.evaluer("a=1+I")
        i.evaluer("a z")
        self.assertDernier(i, 'z*(1 + i)')


    def test_issue_206(self):
        i = Interprete(verbose=VERBOSE)
        etat_interne = \
"""_ = 0

@derniers_resultats = [
    're(x)',
    ]"""
        i.load_state(etat_interne)
        i.evaluer("-1+\i\sqrt{3}")
        self.assertDernier(i, '-1 + sqrt(3)*i')
        i.evaluer('-x**2 + 2*x - 3>>factor')
        self.assertDernier(i, '-x^2 + 2*x - 3')


    def test_issue_206_bis(self):
        i = Interprete(verbose=VERBOSE)
        etat_interne = \
"""_ = 0

@derniers_resultats = [
    'Abs(x)',
    ]"""
        i.load_state(etat_interne)
        i.evaluer('abs(-24/5 - 2 i/5)')
        self.assertDernier(i, '2*sqrt(145)/5')


    def test_issue_206_ter(self):
        i = Interprete(verbose=VERBOSE)
        etat_interne = \
"""_ = 0

@derniers_resultats = [
    'atan2(x, y)',
    ]"""
        i.load_state(etat_interne)
        i.evaluer('ln(9)-2ln(3)')
        self.assertDernier(i, '0')


    def test_load_state(self):
        i = Interprete(verbose=VERBOSE)
        etat_interne = \
"""_ = '2.56'

@derniers_resultats = [
    "'2.56'",
    ]"""
        i.load_state(etat_interne)
        i.evaluer('_')
        self.assertDernier(i, '"2.56"')
        i.evaluer('_1')
        self.assertDernier(i, '"2.56"')


    def test_load_state2(self):
        i = Interprete(verbose=VERBOSE)
        etat_interne = \
"""_ = '2.56'

@derniers_resultats = [
    "'2.56'",
    ]"""
        i.load_state(etat_interne)
        i.evaluer('_')
        self.assertDernier(i, '"2.56"')


    def test_resolution_avec_fonction(self):
        i = Interprete(verbose=VERBOSE)
        i.evaluer("f(x)=a*x+1")
        i.evaluer("resoudre(f(3)=7)")
        res = i.derniers_resultats[-1]
        # Le type du résultat est actuellement un ensemble, mais cela pourrait changer à l'avenir.
        self.assertEqual(res, {S(2)})


    def test_systeme(self):
        i = Interprete(verbose=VERBOSE)
        i.evaluer("g(x)=a x^3+b x^2 + c x + d")
        i.evaluer("resoudre(g(-3)=2 et g(1)=6 et g(5)=3 et g'(1)=0)")
        res = i.derniers_resultats[-1]
        # Le type du résultat est actuellement un dictionnaire, mais cela pourrait changer à l'avenir.
        self.assertIsInstance(res, dict)
        self.assertEqual(res, {S('a'): S(1)/128, S('b'): -S(31)/128, S('c'): S(59)/128, S('d'): S(739)/128})


    def test_ecriture_fraction_decimaux(self):
        # En interne, les décimaux sont remplacés par des fractions.
        # Cela évite la perte de précision inhérente aux calculs avec flottants.
        # Ce remplacement doit être autant que possible transparent pour l'utilisateur,
        # qui, s'il rentre des décimaux, doit voir des décimaux s'afficher.
        i = Interprete(verbose=VERBOSE)
        r, l = i.evaluer('0,3+0,8')
        self.assertEqual(r, '1,1')
        r, l = i.evaluer('a=1,7')
        self.assertEqual(r, '1,7')
        r, l = i.evaluer("f(x)=0,3x+0,7")
        self.assertEqual(r, 'x -> 0,3 x + 0,7')
        # Le calcul suivant ne fonctionne pas en utilisant en interne des flottants
        # (le coefficient devant le x^2 n'est pas tout à fait nul lorsqu'on développe).
        # En utilisant en interne des fractions, par contre, le calcul est exact.
        i.evaluer("C(x)=0,003 x^2 + 60 x + 48000")
        r, l = i.evaluer("expand(C(x+1)-C(x))")
        self.assertEqual(r, '3 x/500 + 60,003')
        r, l = i.evaluer('frac(0,5)')
        self.assertEqual(r, '1/2')
        r, l = i.evaluer('frac(0,166666666666666667)')
        self.assertEqual(r, '1/6')
        r, l = i.evaluer('frac(0,5x+0.3333333333333333)')
        self.assertEqual(r, 'x/2 + 1/3')


    def test_issue_258(self):
        # Issue: "Le mode approché ne fonctionne pas pour une liste."
        i = Interprete(verbose=VERBOSE)
        i.evaluer("v(p,n) = (p-1.96*sqrt(p*(1-p))/sqrt(n), p+1.96*sqrt(p*(1-p))/sqrt(n))")
        r, l = i.evaluer("v(0.28, 50)", calcul_exact=False)
        self.assertEqual(r, "(0,155543858327521659 ; 0,404456141672478341)")
        self.assertEqual(l, r"$\left(0,155543858327521659;\,0,404456141672478341\right)$")


    def test_issue_263(self):
        i = Interprete(verbose=VERBOSE)
        i.evaluer("A = mat([[1;2];[3;4]])")
        i.evaluer("B = mat(2)")
        i.evaluer("C = A*B")
        self.assertIn('C', i.vars)
        r, l = i.evaluer("C")
        self.assertEqual(r, "Matrix([\n[1 ; 2] ; \n[3 ; 4]])")
        etat_interne = i.save_state()
        i.clear_state()
        self.assertNotIn('C', i.vars)
        i.load_state(etat_interne)
        self.assertIn('C', i.vars)
        r, l = i.evaluer("C")
        self.assertEqual(r, "Matrix([\n[1 ; 2] ; \n[3 ; 4]])")
        i.evaluer("A=[[0,1 ; 0,8]; [0,5; 0,5]]")
        r, l = i.evaluer("[[0,3 ; 0,4]]*A")
        self.assertEqual(r, "Matrix([[23/100 ; 11/25]])")
        # ou encore [0,23 ; 0,44]
        self.assertEqual(l, r"$\begin{pmatrix}\frac{23}{100} & \frac{11}{25}\end{pmatrix}$")

    def test_issue_259(self):
        i = Interprete(verbose=VERBOSE)
        # First part.
        r, l = i.evaluer("normal(140,1 ; 150,3 ; 100 ; 5)")
        # sympy 1.0 : '5,28725822993202*10^-16'
        # Wofram Alpha (01/05/2016) : 5/9007199254740992~~5.55112×10^-16
        # On teste que ce soit en gros correct, sans se focaliser sur les décimales.
        self.assertTrue(re.match("5,[0-9]+\*10\^\-16$", r))
        self.assertTrue(re.match(r"\$5,[0-9]+[ ]\\cdot[ ]10\^{-16}\$$", l))
        # Second part of the issue (scientific notation handling).
        i.calcul_exact = False
        r, l = i.evaluer("10,0^-125,0")
        self.assertEqual(r, "1,0*10^-125")
        self.assertEqual(l, r"$10^{-125}$")

    def test_issue_278(self):
        i = Interprete(verbose=VERBOSE)
        i.evaluer("delta = 25")
        r, l = i.evaluer('delta')
        self.assertEqual(r, '25')
        i.evaluer('del delta')
        r, l = i.evaluer('delta')
        self.assertEqual(r, 'delta')

    def test_sous_chaines_intactes(self):
        i = Interprete(verbose=VERBOSE)
        sous_chaine = '1.25;2.36,45'
        i.evaluer("a='%s'" % sous_chaine)
        self.assertEqual(i.vars['_'], sous_chaine)


    def test_proba_stats_basic_API(self):
        self.assert_resultat("inv_normal(.975)", "1,95996398612019")
        self.assert_resultat("normal(-1.96, 1.96)", "0,950004209703559")
        self.assert_resultat("normal(-1, 5, 7, 4)", "0,285787406777808")
        self.assert_resultat("normal(5, oo, 5, 3)", "0,5")
        self.assert_resultat("normal(-oo, 5, 5, 3)", "0,5")
        self.assert_resultat("normal(-oo, oo, 5, 3)", "1")
        self.assert_resultat("binomial(2, 5, 7, 0.3)", "0,666792")
        self.assert_resultat("fluctu(0.54, 150)", "(0,460239799398447 ; 0,619760200601553)")
        self.assert_resultat("confiance(0.27, 800)", "(0,234644660940673 ; 0,305355339059327)")


    @unittest.expectedFailure
    def test_proba_stats_advanced_API(self):
        i = Interprete(verbose=VERBOSE)
        r, l = i.evaluer('X = normal()')
        r, l = i.evaluer('P(-1 < X < 1)')
        r, l = i.evaluer('P(X >= 2)')
        r, l = i.evaluer('P(X = 2)')
