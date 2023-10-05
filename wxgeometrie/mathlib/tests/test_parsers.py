# -*- coding: utf-8 -*-

#from tools.testlib import *
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

import re

from wxgeometrie.mathlib import universal_functions
from wxgeometrie.mathlib.parsers import (
    traduire_formule, NBR, NBR_SIGNE, VAR,
    VAR_NOT_ATTR, NBR_OR_VAR, _arguments_latex,
    convertir_en_latex, _fast_closing_bracket_search,
    _fast_opening_bracket_search, mathtext_parser,
    _rechercher_numerateur, _rechercher_denominateur,
)

liste_fonctions = [
    key for key in universal_functions.__dict__ if "_" not in key]
liste_fonctions.append("limite")
liste_fonctions.append("log10")
liste_fonctions.append("mat")
liste_fonctions.append('range')

import tools.unittest

class MathlibTest(tools.unittest.TestCase):

    def assert_formule(self, x, y, OOo, LaTeX):
        y_ = traduire_formule(x, fonctions = liste_fonctions, OOo = OOo, LaTeX = LaTeX, verbose = False)
        self.assertEqual(y_, y)
        ##if y_ != y:
            ##print "/!\\ Formule: ", x
            ##traduire_formule(x, fonctions = liste_fonctions, OOo = OOo, LaTeX = LaTeX, verbose = True)
            ##print "ERREUR: ",  y_, " != ", y
        ##self.assertEqual(y_, y)

    def assert_arg_latex(self, x, *y):
        x = _arguments_latex(x, 2)
        y = list(y)
        ##if x != y:
            ##print "ERREUR (_arguments_latex): ", x, " != ",  y
        self.assertEqual(x, y)

    def assert_all(self, x, y):
        self.assert_formule(x, y, OOo = True, LaTeX = False)
        self.assert_formule(x, y, OOo = True, LaTeX = False)
        self.assert_formule(x, y, OOo = False, LaTeX = True)
        self.assert_formule(x, y, OOo = True, LaTeX = True)

    def assert_OOo(self, x, y):
        self.assert_formule(x, y, OOo = True, LaTeX = False)
        self.assert_formule(x, y, OOo = True, LaTeX = True)

    def assert_latex(self, x, y):
        self.assert_formule(x, y, OOo = False, LaTeX = True)
        self.assert_formule(x, y, OOo = True, LaTeX = True)

    def assert_match(self, pattern, chaine):
        """Teste si la chaine correspond entièrement au pattern."""
        self.assertTrue(re.match(pattern + "$", chaine))

    def assert_not_match(self, pattern, chaine):
        """Teste si la chaine ne correspond pas entièrement au pattern."""
        self.assertFalse(re.match(pattern + "$", chaine))

    def assert_VAR(self, chaine):
        self.assert_match(VAR, chaine)
        self.assert_match(NBR_OR_VAR, chaine)

    def assert_not_VAR(self, chaine):
        self.assert_not_match(VAR, chaine)

    #def assert_NBR(self, chaine):
    #    self.assert_match(NBR, chaine)
    #    self.assert_match(NBR_OR_VAR, chaine)

    def assert_NBR(self, chaine):
        self.assert_match(NBR, chaine)
        self.assert_match(NBR_SIGNE, chaine)
        self.assert_match(NBR_OR_VAR, chaine)

    def assert_NBR_SIGNE(self, chaine):
        self.assert_match(NBR_SIGNE, chaine)
        self.assert_not_match(NBR_OR_VAR, chaine)

    def assert_find_VAR_NOT_ATTR(self, chaine):
        self.assertTrue(re.search(VAR_NOT_ATTR, chaine))

    def assert_not_find_VAR_NOT_ATTR(self, chaine):
        self.assertFalse(re.search(VAR_NOT_ATTR, chaine))

    def assert_not_NBR(self, chaine):
        self.assert_not_match(NBR, chaine)

    def test_tous_modes(self):
        self.assert_all('a z', 'a*z')
        self.assert_all("2x+3", "2*x+3")
        self.assert_all("2(x+3)", "2*(x+3)")
        self.assert_all("(x+1)x(x+3)", "(x+1)*x*(x+3)")
        self.assert_all("sin(x+1)x(x+3)", "sin(x+1)*x*(x+3)")
        self.assert_all("(x+1)cos(x+3)", "(x+1)*cos(x+3)")
        self.assert_all("-1.5x^(-2)+ab+3ab(2x+y)+x(y(z+1)))2(x)",
                   "-1.5*x**(-2)+ab+3*ab*(2*x+y)+x*(y*(z+1)))*2*(x)")
        self.assert_all("3x³-2x²y-2x==5y", "3*x**3-2*x**2*y-2*x==5*y")
        self.assert_all("25%*12 mod 5", "25/100*12%5")
        self.assert_all("(25%*12)mod 5", "(25/100*12)%5")
        self.assert_all("limite(1/x^3,x,1+)", "limite(1/x**3,x,1,'+')")
        self.assert_all("limite(1/x^3,x, 1-  )", "limite(1/x**3,x,1,'-')")
        self.assert_all("x sin x+1", "x*sin(x)+1")
        self.assert_all("log10 ab y sin 2x+1", "log10(ab)*y*sin(2*x)+1")
        self.assert_all("cos 3.5x(x+1)", "cos(3.5*x)*(x+1)")
        self.assert_all("cos 2", "cos(2)")
        # Cas particulier :
        self.assert_all("cos -3", "cos-3")
        # Développement décimal infini périodique
        self.assert_all("17.03[45]", "((1703+45/99)/100)")
        self.assert_all("17.[045]", "((17+45/999)/1)")
        self.assert_all("17.1[0]", "((171+0/9)/10)")
        # Ne pas rajouter de * devant les parenthèses d'une méthode
        self.assert_all("A.transpose()", "A.transpose()")
        self.assert_all("[j for j in liste]", "[j for j in liste]")
        # Caractères unicode
        self.assert_all("\u2013x\u22123\u00D7y\u00F7z²", "-x-3*y/z**2")
        # * entre un flottant et une parenthese
        self.assert_all(".015(x-50)^2-20", ".015*(x-50)**2-20")
        self.assert_all("-1.015 (x-50)", "-1.015*(x-50)")
        self.assert_all('5|x+3|+1-|2x|', '5*abs(x+3)+1-abs(2*x)')
        self.assert_all('[f for j in range(1, 11)]', '[f for j in range(1,11)]')

    def test_texte(self):
        # Texte entre guillemets "texte" ou """texte""" inchangé.
        self.assert_all("'1.2345'", "'1.2345'")
        self.assert_all('"ok"', '"ok"')
        self.assert_all('"x(x+1)" x(x+1) """x(x+1) " """', '"x(x+1)"x*(x+1)"""x(x+1) " """')
        self.assert_all(r'"\""', r'"\""')
        self.assert_all(r'"""\"+1\" ici, et non \"+n\""""', r'"""\"+1\" ici, et non \"+n\""""')

    def test_matrice(self):
        # Rajouter mat() quand il n'y est pas.
        self.assert_all("[[1, 2], [3, 4]]", "mat([[1,2],[3,4]])")
        self.assert_all("[ [1,2;2,5] ; [-3,4;4,2] ]", "mat([[1.2,2.5],[-3.4,4.2]])")
        # Ne pas rajouter mat() quand il y est déjà.
        self.assert_all("mat([[1, 2], [3, 4]])", "mat([[1,2],[3,4]])")
        self.assert_all("mat( [[1, 2], [3, 4]] )", "mat([[1,2],[3,4]])")


    def test_mode_OOo(self):
        self.assert_OOo("2 times 3", "2*3")
        self.assert_OOo("2 over 3", "2/3")
        self.assert_OOo("{2+5x} over {3-x}", "(2+5*x)/(3-x)")
        self.assert_OOo("{2-.5x}over{3-x}", "(2-.5*x)/(3-x)")
        self.assert_OOo("0.85 sup {1 over 7} - 1", "0.85**(1/7)-1")


    def test_mode_LaTeX(self):
        self.assert_latex("2\\times3", "2*3")
        self.assert_latex("\\cos x\\sin x\\exp x", "cos(x)*sin(x)*exp(x)")
        self.assert_latex("\\frac{2}{3}", "((2)/(3))")
        self.assert_latex("\\frac{2+x}{3}", "((2+x)/(3))")
        self.assert_latex("\\dfrac{2+x}{1-3}", "((2+x)/(1-3))")
        self.assert_latex("\\tfrac{2+x}{3}", "((2+x)/(3))")
        self.assert_latex("\\dfrac{2x^2+x-7}{6-4x}", "((2*x**2+x-7)/(6-4*x))")
        self.assert_latex("-\\frac12-\\dfrac4{(6-4x)^2}", "-(1/2)-(4/((6-4*x)**2))")
        self.assert_latex("\\left((1+10~\\%)(1+5~\\%)(1-7~\\%)\\right)^{\\frac{1}{3} }",
                     "((1+10/100)*(1+5/100)*(1-7/100))**(((1)/(3)))")
        self.assert_latex("\\text{0.7}\\times (-50)^2-9\\times (-50)+200", "(0.7)*(-50)**2-9*(-50)+200")
        self.assert_latex("\\ln(2)+\\exp(3)+\\log(\\pi+1)", "ln(2)+exp(3)+log(pi+1)")
        self.assert_latex("x\ge1\le3", "x>=1<=3")
        self.assert_latex(r"100\left(\left(1+\dfrac{50}{100}\right)^\frac{1}{10}-1\right)",
                     "100*((1+((50)/(100)))**((1)/(10))-1)")
        self.assert_latex("M = \\begin{pmatrix}\n0,6 & 0,4\\\\\n0,75& 0,25\\\\\n\\end{pmatrix}",
                     'M=mat([[0.6,0.4],[0.75,0.25]])')
        self.assert_latex(r"\begin{pmatrix}0.65& 0.35\end{pmatrix}\begin{pmatrix}0.55 & 0.45\\0.3 & 0.7\end{pmatrix}",
                     "mat([[0.65,0.35]])*mat([[0.55,0.45],[0.3,0.7]])")

    def test_NBR(self):
        self.assert_NBR_SIGNE("-2.56")
        self.assert_NBR_SIGNE("-.56")
        self.assert_NBR_SIGNE("+5.")
        self.assert_NBR_SIGNE("+5.056")
        self.assert_NBR("56")
        self.assert_NBR(".46")
        self.assert_NBR(".015")
        self.assert_NBR("752.")
        self.assert_NBR("740.54")
        self.assert_not_NBR("5-6")
        self.assert_not_NBR(".")
        # Regression test for issue FS#252
        self.assert_match('\(' + NBR_SIGNE, "(-2.3")

    def test_VAR(self):
        self.assert_VAR("Arertytre")
        self.assert_VAR("a")
        self.assert_VAR("_")
        self.assert_VAR("_45ui")
        self.assert_VAR("A13")
        self.assert_not_VAR("1A")
        self.assert_not_VAR("2")

    def test_search_VAR_NOT_ATTR(self):
        self.assert_find_VAR_NOT_ATTR("a")
        self.assert_find_VAR_NOT_ATTR("1+_arrt9876")
        self.assert_find_VAR_NOT_ATTR("5*t_566")
        self.assert_find_VAR_NOT_ATTR("(_.t)/3")
        self.assert_not_find_VAR_NOT_ATTR(".aert")
        self.assert_not_find_VAR_NOT_ATTR("4.tyu+4")
        self.assert_not_find_VAR_NOT_ATTR("89eeazt")
        self.assert_not_find_VAR_NOT_ATTR("2-._ez")

    def test_arguments_LaTeX(self):
        self.assert_arg_latex('2{x+1}+4', '2', '{x+1}', '+4')
        self.assert_arg_latex('{x+2}5+4x-17^{2+x}', '{x+2}', '5', '+4x-17^{2+x}')



    # -----------------------------------------------------------
    # Tests conversion chaines : calcul au format Python -> LaTeX
    # -----------------------------------------------------------


    def assert_conv(self, input, output):
        self.assertEqual(convertir_en_latex(input), '$%s$' %output)

    def test_convertir_en_LaTeX(self):
        self.assert_conv('2*x', '2 x')
        self.assert_conv('2*3', r'2\times 3')
        #TODO: retourner 0.005 au lieu de .005
        self.assert_conv('2*.005', r'2\times .005')
        self.assert_conv('2*x+3', '2 x+3')
        self.assert_conv('x**-3.5+x**2*y-x**(2*y)+8', 'x^{-3.5}+x^{2} y-x^{2 y}+8')
        self.assert_conv('--x+-----3--y', 'x-3+y')
        self.assert_conv('sqrt(x) + exp(-y)', r'\sqrt{x}+\exp(-y)')
        self.assert_conv('+oo', r'+\infty')

    def test_convertir_en_LaTeX_mode_dollars(self):
        self.assertEqual(convertir_en_latex('-1', mode='$'), '$-1$')
        self.assertEqual(convertir_en_latex('', mode='$'), '') # '' et non '$$' !

    def test_convertir_en_LaTeX_fractions(self):
        self.assert_conv('2/3', r'\frac{2}{3}')
        self.assert_conv('-2/3', r'-\frac{2}{3}')
        self.assert_conv('x**(2/3)', r'x^{\frac{2}{3}}')
        self.assert_conv('(x+1)/(2*x)', r'\frac{x+1}{2 x}')
        self.assert_conv('(x(x+1))/(2*x*(x+2)*(x**25+7*x+5))*(x+3)',
                    r'\frac{x(x+1)}{2 x (x+2) (x^{25}+7 x+5)} (x+3)')
        self.assert_conv('2/3x', r'\frac{2}{3}x')
        self.assert_conv('2/0.4', r'\frac{2}{0.4}')

    def test_convertir_en_LaTeX_fractions_imbriquees(self):
        self.assert_conv('(9*x+3/7)/(-8*x-6)', r'\frac{9 x+\frac{3}{7}}{-8 x-6}')
        self.assert_conv('2/3/4', r'\frac{\frac{2}{3}}{4}')
        self.assert_conv('25/(4/7)+8/pi', r'\frac{25}{\frac{4}{7}}+\frac{8}{\pi}')
        self.assert_conv('(2/3)/(25/(4/7)+8/pi)',
                    r'\frac{\frac{2}{3}}{\frac{25}{\frac{4}{7}}+\frac{8}{\pi}}')


    def test_convertir_en_LaTeX_bad_expression(self):
        # XXX: Par défaut, quand l'expression n'est pas valide, la valeur
        # retournée doit être la valeur entrée ??
        # Pour l'instant, aucun comportement clair n'est défini lorsqu'une
        # expression mathématiques invalide est entrée.
        # Simplement, le parser ne doit pas planter.
        self.assert_conv('2/', '2/')
        self.assert_conv('/', '/')
        self.assert_conv('-+', '-')
        # Un signe plus ou un signe moins isolé peuvent être utiles
        self.assert_conv('+', '+')


    def test_parentheses_inutiles(self):
        self.assert_conv('(x+1)', 'x+1')
        self.assert_conv('(x(x+1))', 'x(x+1)')
        self.assert_conv('(((x)))', 'x')

    def test_convertir_en_LaTeX_mode_None(self):
        self.assertEqual(convertir_en_latex('2*x', mode=None), '2 x')

    def assert_search(self, input, expected):
        i = _fast_closing_bracket_search(input)
        self.assertEqual(input[:i], expected)

    def test_fast_closing_bracket_search(self):
        self.assert_search('(ok)', '(ok)')
        self.assert_search('(ok)+3', '(ok)')
        self.assert_search('(x+(x-3(x-4))+(x-7))-x(x+8)', '(x+(x-3(x-4))+(x-7))')

    def assert_backsearch(self, input, expected):
        i = _fast_opening_bracket_search(input)
        self.assertEqual(input[i:], expected)

    def test_fast_opening_bracket_search(self):
        self.assert_backsearch('(ok)', '(ok)')
        self.assert_backsearch('3+(ok)', '(ok)')
        self.assert_backsearch('x(x+8)-(x+(x-3(x-4))+(x-7))', '(x+(x-3(x-4))+(x-7))')

    def assert_numerateur(self, input, expected):
        i = _rechercher_numerateur(input)
        self.assertIsNotNone(i)
        self.assertEqual(input[i:], expected)

    def test_rechercher_numerateur(self):
        self.assert_numerateur('2', '2')
        self.assert_numerateur('-2', '2')
        self.assert_numerateur('1+2', '2')
        self.assert_numerateur('cos(x)', 'cos(x)')
        self.assert_numerateur('x-2^cos(x)', '2^cos(x)')
        self.assert_numerateur('3-(x+1)^(x-2^cos(x))', '(x+1)^(x-2^cos(x))')
        self.assert_numerateur('3-@', '@')
        self.assert_numerateur('(4/7)+8', '8')
        self.assert_numerateur('@+8', '8')

    def assert_denominateur(self, input, expected):
        i = _rechercher_denominateur(input)
        self.assertIsNotNone(i)
        self.assertEqual(input[:i], expected)

    def test_rechercher_denominateur(self):
        self.assert_denominateur('2', '2')
        self.assert_denominateur('-2', '-2')
        self.assert_denominateur('1+2', '1')
        self.assert_denominateur('cos(x)-x', 'cos(x)')
        self.assert_denominateur('2^cos(x)-x', '2^cos(x)')
        self.assert_denominateur('(x+1)^(x-2^cos(x))-3', '(x+1)^(x-2^cos(x))')

    def test_mathtext_parser(self):
        "On teste simplement qu'aucune erreur n'est renvoyée."
        # Bug matplotlib 1.1.1
        mathtext_parser("$A'$")
        mathtext_parser("$A'$")
        mathtext_parser("$f'$ est la dérivée")
        mathtext_parser("$1^{er}$ dé")
        mathtext_parser(r"$\left]-\infty;\frac{1}{3}\right]\cup\left[2;5\right[$")
