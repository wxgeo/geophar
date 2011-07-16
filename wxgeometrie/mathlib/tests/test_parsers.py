# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

#from tools.testlib import *

import re
from wxgeometrie.mathlib import universal_functions
from wxgeometrie.mathlib.parsers import (traduire_formule, NBR, NBR_SIGNE, VAR,
                                        VAR_NOT_ATTR, NBR_OR_VAR, _arguments_latex)

liste_fonctions = [key for key in universal_functions.__dict__.keys() if "_" not in key]
liste_fonctions.append("limite")
liste_fonctions.append("log10")
liste_fonctions.append("mat")

def assert_formule(x, y, OOo, LaTeX):
    y_ = traduire_formule(x, fonctions = liste_fonctions, OOo = OOo, LaTeX = LaTeX, verbose = False)
    if y_ != y:
        print "/!\\ Formule: ", x
        traduire_formule(x, fonctions = liste_fonctions, OOo = OOo, LaTeX = LaTeX, verbose = True)
        print "ERREUR: ",  y_, " != ", y
    assert (y_ == y)

def assert_arg_latex(x, *y):
    x = _arguments_latex(x, 2)
    y = list(y)
    if x != y:
        print "ERREUR (_arguments_latex): ", x, " != ",  y
    assert (x == y)

def assert_all(x, y):
    assert_formule(x, y, OOo = True, LaTeX = False)
    assert_formule(x, y, OOo = True, LaTeX = False)
    assert_formule(x, y, OOo = False, LaTeX = True)
    assert_formule(x, y, OOo = True, LaTeX = True)

def assert_OOo(x, y):
    assert_formule(x, y, OOo = True, LaTeX = False)
    assert_formule(x, y, OOo = True, LaTeX = True)

def assert_latex(x, y):
    assert_formule(x, y, OOo = False, LaTeX = True)
    assert_formule(x, y, OOo = True, LaTeX = True)

def assert_match(pattern, chaine):
    u"""Teste si la chaine correspond entièrement au pattern."""
    assert (re.match(pattern + "$", chaine))

def assert_not_match(pattern, chaine):
    u"""Teste si la chaine ne correspond pas entièrement au pattern."""
    assert (not re.match(pattern + "$", chaine))

def assert_VAR(chaine):
    assert_match(VAR, chaine)
    assert_match(NBR_OR_VAR, chaine)

def assert_not_VAR(chaine):
    assert_not_match(VAR, chaine)

#def assert_NBR(chaine):
#    assert_match(NBR, chaine)
#    assert_match(NBR_OR_VAR, chaine)

def assert_NBR(chaine):
    assert_match(NBR, chaine)
    assert_match(NBR_SIGNE, chaine)
    assert_match(NBR_OR_VAR, chaine)

def assert_NBR_SIGNE(chaine):
    assert_match(NBR_SIGNE, chaine)
    assert_not_match(NBR_OR_VAR, chaine)

def assert_find_VAR_NOT_ATTR(chaine):
    assert (re.search(VAR_NOT_ATTR, chaine))

def assert_not_find_VAR_NOT_ATTR(chaine):
    assert (not re.search(VAR_NOT_ATTR, chaine))

def assert_not_NBR(chaine):
    assert_not_match(NBR, chaine)

def test_tous_modes():
    assert_all('a z', 'a*z')
    assert_all("2x+3", "2*x+3")
    assert_all("2(x+3)", "2*(x+3)")
    assert_all("(x+1)x(x+3)", "(x+1)*x*(x+3)")
    assert_all("sin(x+1)x(x+3)", "sin(x+1)*x*(x+3)")
    assert_all("(x+1)cos(x+3)", "(x+1)*cos(x+3)")
    assert_all("-1.5x^(-2)+ab+3ab(2x+y)+x(y(z+1)))2(x)", "-1.5*x**(-2)+ab+3*ab*(2*x+y)+x*(y*(z+1)))*2*(x)")
    assert_all(u"3x³-2x²y-2x==5y", "3*x**3-2*x**2*y-2*x==5*y")
    assert_all(u"25%*12 mod 5", "25/100*12%5")
    assert_all(u"(25%*12)mod 5", "(25/100*12)%5")
    assert_all(u"limite(1/x^3,x,1+)", "limite(1/x**3,x,1,'+')")
    assert_all(u"limite(1/x^3,x, 1-  )", "limite(1/x**3,x,1,'-')")
    assert_all(u"x sin x+1", "x*sin(x)+1")
    assert_all(u"log10 ab y sin 2x+1", "log10(ab)*y*sin(2*x)+1")
    assert_all(u"cos 3.5x(x+1)", "cos(3.5*x)*(x+1)")
    assert_all(u"cos 2", "cos(2)")
    # Cas particulier :
    assert_all(u"cos -3", "cos-3")
    # Développement décimal infini périodique
    assert_all(u"17.03[45]", u"((1703+45/99)/100)")
    assert_all(u"17.[045]", u"((17+45/999)/1)")
    assert_all(u"17.1[0]", u"((171+0/9)/10)")
    # Ne pas rajouter de * devant les parenthèses d'une méthode
    assert_all(u"A.transpose()", u"A.transpose()")
    assert_all(u"[j for j in liste]", u"[j for j in liste]")
    # Texte entre guillemets "texte" ou """texte""" inchangé.
    assert_all('"ok"', '"ok"')
    assert_all('"x(x+1)" x(x+1) """x(x+1) " """', '"x(x+1)"x*(x+1)"""x(x+1) " """')
    assert_all(r'"\""', r'"\""')
    assert_all(r'"""\"+1\" ici, et non \"+n\""""', r'"""\"+1\" ici, et non \"+n\""""')
    # Caractères unicode
    assert_all(u"\u2013x\u22123", "-x-3")





def test_mode_OOo():
    assert_OOo("2 times 3", "2*3")
    assert_OOo("2 over 3", "2/3")
    assert_OOo("{2+5x} over {3-x}", "(2+5*x)/(3-x)")
    assert_OOo("{2-.5x}over{3-x}", "(2-.5*x)/(3-x)")
    assert_OOo("0.85 sup {1 over 7} - 1", "0.85**(1/7)-1")


def test_mode_LaTeX():
    assert_latex("2\\times3", "2*3")
    assert_latex("\\cos x\\sin x\\exp x", "cos(x)*sin(x)*exp(x)")
    assert_latex("\\frac{2}{3}", "((2)/(3))")
    assert_latex("\\frac{2+x}{3}", "((2+x)/(3))")
    assert_latex("\\dfrac{2+x}{1-3}", "((2+x)/(1-3))")
    assert_latex("\\tfrac{2+x}{3}", "((2+x)/(3))")
    assert_latex("\\dfrac{2x^2+x-7}{6-4x}", "((2*x**2+x-7)/(6-4*x))")
    assert_latex("-\\frac12-\\dfrac4{(6-4x)^2}", "-(1/2)-(4/((6-4*x)**2))")
    assert_latex("\\left((1+10~\\%)(1+5~\\%)(1-7~\\%)\\right)^{\\frac{1}{3} }", "((1+10/100)*(1+5/100)*(1-7/100))**(((1)/(3)))")
    assert_latex("\\text{0.7}\\times (-50)^2-9\\times (-50)+200", "(0.7)*(-50)**2-9*(-50)+200")
    assert_latex("\\ln(2)+\\exp(3)+\\log(\\pi+1)", "ln(2)+exp(3)+log(pi+1)")
    assert_latex("x\ge1\le3", "x>=1<=3")
    assert_latex(r"100\left(\left(1+\dfrac{50}{100}\right)^\frac{1}{10}-1\right)", "100*((1+((50)/(100)))**((1)/(10))-1)")
    assert_latex("M = \\begin{pmatrix}\n0,6 & 0,4\\\\\n0,75& 0,25\\\\\n\\end{pmatrix}", 'M=mat([[0,6,0,4],[0,75,0,25]])')

def test_NBR():
    assert_NBR_SIGNE("-2.56")
    assert_NBR_SIGNE("-.56")
    assert_NBR_SIGNE("+5.")
    assert_NBR_SIGNE("+5.056")
    assert_NBR("56")
    assert_NBR(".46")
    assert_NBR("752.")
    assert_NBR("740.54")
    assert_not_NBR("5-6")
    assert_not_NBR(".")

def test_VAR():
    assert_VAR("Arertytre")
    assert_VAR("a")
    assert_VAR("_")
    assert_VAR("_45ui")
    assert_VAR("A13")
    assert_not_VAR("1A")
    assert_not_VAR("2")

def test_search_VAR_NOT_ATTR():
    assert_find_VAR_NOT_ATTR("a")
    assert_find_VAR_NOT_ATTR("1+_arrt9876")
    assert_find_VAR_NOT_ATTR("5*t_566")
    assert_find_VAR_NOT_ATTR("(_.t)/3")
    assert_not_find_VAR_NOT_ATTR(".aert")
    assert_not_find_VAR_NOT_ATTR("4.tyu+4")
    assert_not_find_VAR_NOT_ATTR("89eeazt")
    assert_not_find_VAR_NOT_ATTR("2-._ez")

def test_arguments_LaTeX():
    assert_arg_latex('2{x+1}+4', '2', '{x+1}', '+4')
    assert_arg_latex('{x+2}5+4x-17^{2+x}', '{x+2}', '5', '+4x-17^{2+x}')
