# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from wxgeometrie.modules.tablatex.tests.tabtestlib import assert_tableau
from wxgeometrie.modules.tablatex.tabvar import tabvar

from pytest import XFAIL

def assert_tabvar(chaine, code_latex, **options):
    assert_tableau(tabvar, chaine, code_latex, **options)


def test_mode_manuel():
    s = "x;f(x);f'(x):0;2;|>>1;0;1<<2;3;0"
    options = {"stretch": False}
    tab = \
r"""\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCCCCCC|}
\hline
\,\,x\,\,                            & &0&             &        &1&      &2\\
\hline
f'(x)                                &&\dbarre&        &-       &1&+     &0\\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f(x)$}&\niveau{2}{2} &2&&\decroit&0&\croit&3\\
\hline
\end{tabvar}\]
% x;f(x);f'(x):0;2;|>>1;0;1<<2;3;0
"""
    assert_tabvar(s, tab, **options)

    s = "x;f(x);f'(x):(0;2;|) >> (1;0;1) << (2;3;0)"
    tab = \
r"""\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCCCCCC|}
\hline
\,\,x\,\,                            & &0&             &        &1&      &2\\
\hline
f'(x)                                &&\dbarre&        &-       &1&+     &0\\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f(x)$}&\niveau{2}{2} &2&&\decroit&0&\croit&3\\
\hline
\end{tabvar}\]
% x;f(x);f'(x):(0;2;|) >> (1;0;1) << (2;3;0)
"""
    assert_tabvar(s, tab, **options)

    s = "x;f(x):-oo;+oo>>0;-oo|+oo>>+oo;-oo"
    tab = \
r"""\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCCCCCC|}
\hline
\,\,x\,\,                            &-\infty             &        & &0&                                &        &+\infty\\
\hline
f'(x)                                &                    &-       &&\dbarre&                           &-       & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f(x)$}&\niveau{2}{2}+\infty&\decroit&-\infty&\dbarre&\niveau{2}{2}+\infty&\decroit&-\infty\\
\hline
\end{tabvar}\]
% x;f(x):-oo;+oo>>0;-oo|+oo>>+oo;-oo
"""
    assert_tabvar(s, tab, **options)

    s = "x;f(x): (-oo;+oo)>>(0;-oo|+oo)>>(+oo;-oo)"
    tab = \
r"""\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCCCCCC|}
\hline
\,\,x\,\,                            &-\infty             &        & &0&                                &        &+\infty\\
\hline
f'(x)                                &                    &-       &&\dbarre&                           &-       & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f(x)$}&\niveau{2}{2}+\infty&\decroit&-\infty&\dbarre&\niveau{2}{2}+\infty&\decroit&-\infty\\
\hline
\end{tabvar}\]
% x;f(x): (-oo;+oo)>>(0;-oo|+oo)>>(+oo;-oo)
"""
    assert_tabvar(s, tab, **options)

def test_manuel_zone_interdite():
    options = {"stretch": False}
    s = "x;f(x);f'(x):(0;2;|) >> (1;-oo) || (2;+oo) << (+oo;3)"
    tab = \
r"""\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCCCCUCCC|}
\hline
\,\,x\,\,                            & &0&             &        &1      &\hspace*{15mm}&2      &      &+\infty\\
\hline
f'(x)                                &&\dbarre&        &-       &0      &              &0      &+     & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f(x)$}&\niveau{2}{2} &2&&\decroit&-\infty&              &+\infty&\croit&3\\
\hline
\end{tabvar}\]
% x;f(x);f'(x):(0;2;|) >> (1;-oo) || (2;+oo) << (+oo;3)
"""
    assert_tabvar(s, tab, **options)
    # Syntaxe alternative : XX au lieu de ||.
    s = "x;f(x);f'(x):(0;2;|) >> (1;-oo) XX (2;+oo) << (+oo;3)"
    tab = \
r"""\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCCCCUCCC|}
\hline
\,\,x\,\,                            & &0&             &        &1      &\hspace*{15mm}&2      &      &+\infty\\
\hline
f'(x)                                &&\dbarre&        &-       &0      &              &0      &+     & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f(x)$}&\niveau{2}{2} &2&&\decroit&-\infty&              &+\infty&\croit&3\\
\hline
\end{tabvar}\]
% x;f(x);f'(x):(0;2;|) >> (1;-oo) XX (2;+oo) << (+oo;3)
"""
    assert_tabvar(s, tab, **options)



def test_mode_auto():
    options = {"stretch": False}
    s = 'f(x)=(x+1)/(3x-2)'
    tab = \
r"""\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCCCCCC|}
\hline
\,\,x\,\,                            &-\infty                 &        & &\frac{2}{3}&                      &        &+\infty\\
\hline
f'(x)                                &                        &-       &&\dbarre&                           &-       & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f(x)$}&\niveau{2}{2}\frac{1}{3}&\decroit&-\infty&\dbarre&\niveau{2}{2}+\infty&\decroit&\frac{1}{3}\\
\hline
\end{tabvar}\]
% x;f(x):(-oo;1/3) >> (2/3;-oo|+oo;|) >> (+oo;1/3)
% f(x)=(x+1)/(3x-2)
"""
    assert_tabvar(s, tab, **options)

    s = "(x+1)(x+2)"
    tab = \
r"""\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCCCC|}
\hline
\,\,x\,\,                         &-\infty             &        &-\frac{3}{2}&      &+\infty\\
\hline
f'(x)                             &                    &-       &0           &+     & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f$}&\niveau{2}{2}+\infty&\decroit&-\frac{1}{4}&\croit&+\infty\\
\hline
\end{tabvar}\]
% x;f:(-oo;+oo) >> (-3/2;-1/4;0) << (+oo;+oo)
% (x+1)(x+2)
"""
    assert_tabvar(s, tab, **options)

    s = "f(x)=5*ln(x)/x+3"
    tab = \
r"""\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCCCCCC|}
\hline
\,\,x\,\,                            & &0&                                      &      &\e          &        &+\infty\\
\hline
f'(x)                                &&\dbarre&                                 &+     &0           &-       & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f(x)$}&\niveau{1}{2}&\dbarre&\niveau{1}{2}-\infty&\croit&5 \exp(-1)+3&\decroit&3\\
\hline
\end{tabvar}\]
% x;f(x):(0;|-oo;|) << (e;5*exp(-1) + 3;0) >> (+oo;3)
% f(x)=5*ln(x)/x+3
"""
    assert_tabvar(s, tab, **options)


def test_intervalle():
    s = "x^2 sur [1;+oo["
    tab = \
r"""\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCC|}
\hline
\,\,x\,\,                         &1             &      &+\infty\\
\hline
f'(x)                             &              &+     & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f$}&\niveau{1}{2}1&\croit&+\infty\\
\hline
\end{tabvar}\]
% x;f:(1;1) << (+oo;+oo)
% x^2 sur [1;+oo[
"""
    assert_tabvar(s, tab)


def test_latex():
    s = "f(x)=3e^{2x}-12e^{x}+5"
    tab = \
r"""\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCCCC|}
\hline
\,\,x\,\,                            &-\infty       &        &\ln(2)&      &+\infty\\
\hline
f'(x)                                &              &-       &0     &+     & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f(x)$}&\niveau{2}{2}5&\decroit&-7    &\croit&+\infty\\
\hline
\end{tabvar}\]
% x;f(x):(-oo;5) >> (ln(2);-7;0) << (+oo;+oo)
% f(x)=3e^{2x}-12e^{x}+5
"""
    assert_tabvar(s, tab)

    s = "$f(x)=(2x+3)\e^x$ sur $[0\,;\,+\oo[$"
    tab = \
r'''\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCC|}
\hline
\,\,x\,\,                            &0             &      &+\infty\\
\hline
f'(x)                                &              &+     & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f(x)$}&\niveau{1}{2}3&\croit&+\infty\\
\hline
\end{tabvar}\]
% x;f(x):(0;3) << (+oo;+oo)
% $f(x)=(2x+3)\e^x$ sur $[0\,;\,+\oo[$
'''
    assert_tabvar(s, tab)



def test_issue_194():
    s = "<< -1/ln(2) >>"
    tab = \
r"""\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCCCC|}
\hline
\,\,x\,\,                         &-\infty      &      &-\frac{1}{\ln(2)}&        &+\infty\\
\hline
f'(x)                             &             &+     &0                &-       & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f$}&\niveau{1}{2}&\croit&                 &\decroit&\\
\hline
\end{tabvar}\]
% << -1/ln(2) >>
"""
    assert_tabvar(s, tab)


def test_issue_pi():
    s = 'sin(x) sur [-pi;pi]'
    tab = \
r'''\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCCCC|}
\hline
\,\,x\,\,                         &-\pi          &      &\frac{\pi}{2}&        &\pi\\
\hline
f'(x)                             &              &+     &0            &-       & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f$}&\niveau{1}{2}0&\croit&1            &\decroit&0\\
\hline
\end{tabvar}\]
% x;f:(-pi;0) << (pi/2;1;0) >> (pi;0)
% sin(x) sur [-pi;pi]
'''
    assert_tabvar(s, tab)


def test_options():
    s = 'f(x)=4 x^{2} - 24 x + 11'
    options = {'derivee': False, 'limites': False, 'stretch': False}
    tab = \
r'''\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCCCC|}
\hline
\,\,x\,\,                            &-\infty      &        &3  &      &+\infty\\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f(x)$}&\niveau{2}{2}&\decroit&-25&\croit&\\
\hline
\end{tabvar}\]
% x;f(x):(-oo;) >> (3;-25) << (+oo;)
% f(x)=4 x^{2} - 24 x + 11
'''
    assert_tabvar(s, tab, **options)


def test_issue_189():
    # Tableaux de signes et de variation avec des décimaux
    s = 'f(x) = (x -4)\e^{-0,25x+5} sur [4;20]'
    options = {'derivee': False, 'decimales': 3, 'stretch': False}
    tab = \
r'''\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCCCC|}
\hline
\,\,x\,\,                            &4             &      &8        &        &20\\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f(x)$}&\niveau{1}{2}0&\croit&4 \exp(3)&\decroit&16\\
\hline
\end{tabvar}\]
% x;f(x):(4;0) << (8;4*exp(3)) >> (20;16)
% f(x) = (x -4)\e^{-0,25x+5} sur [4;20]
'''
    assert_tabvar(s, tab, **options)
    options = {'derivee': False, 'decimales': 2, 'stretch': False}
    tab = \
r'''\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCCCC|}
\hline
\,\,x\,\,                            &4             &      &8        &        &20\\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f(x)$}&\niveau{1}{2}0&\croit&4 \exp(3)&\decroit&16\\
\hline
\end{tabvar}\]
% x;f(x):(4;0) << (8;4*exp(3)) >> (20;16)
% f(x) = (x -4)\e^{-0,25x+5} sur [4;20]
'''
    assert_tabvar(s, tab, **options)

def test_valeur_approchee():
    s = "f(x)=1/x sur [4;6]"
    options = {'derivee': True, 'decimales': 4, 'approche': True, 'stretch': False}
    tab = \
r'''\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCC|}
\hline
\,\,x\,\,                            &4                &        &6\\
\hline
f'(x)                                &                 &-       & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f(x)$}&\niveau{2}{2}0,25&\decroit&0,1667\\
\hline
\end{tabvar}\]
% x;f(x):(4;0,25) >> (6;0,1667)
% f(x)=1/x sur [4;6]
'''
    assert_tabvar(s, tab, **options)


def test_issue_187():
    s = "5x+31+(1500x+100)/(x^2)"
    options = {'derivee': True, 'decimales': 2, 'approche': True, 'stretch': False}
    tab = \
r'''\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCCCCCCCCCCCC|}
\hline
\,\,x\,\,                         &-\infty             &      &-17,25 &        &-0,13   &      & &0&                                &        &17,39 &      &+\infty\\
\hline
f'(x)                             &                    &+     &0      &-       &0       &+     &&\dbarre&                           &-       &0     &+     & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f$}&\niveau{1}{2}-\infty&\croit&-141,87&\decroit&-5594,67&\croit&+\infty&\dbarre&\niveau{2}{2}+\infty&\decroit&204,54&\croit&+\infty\\
\hline
\end{tabvar}\]
% x;f:(-oo;-oo) << (-17,25;-141,87;0) >> (-0,13;-5594,67;0) << (0;+oo|+oo;|) >> (17,39;204,54;0) << (+oo;+oo)
% 5x+31+(1500x+100)/(x^2)
'''
    assert_tabvar(s, tab, **options)


def test_issue_249():
    s = r"f(x) = 0,5x + \text{e}^{-0,5x + 0,4}"
    options = {'derivee': True, 'decimales': 2, 'approche': True, 'stretch': False}
    tab = \
r'''\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCCCC|}
\hline
\,\,x\,\,                            &-\infty             &        &0,8&      &+\infty\\
\hline
f'(x)                                &                    &-       &0  &+     & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f(x)$}&\niveau{2}{2}+\infty&\decroit&1,4&\croit&+\infty\\
\hline
\end{tabvar}\]
% x;f(x):(-oo;+oo) >> (0,8;1,4;0) << (+oo;+oo)
% f(x) = 0,5x + \text{e}^{-0,5x + 0,4}
'''
    assert_tabvar(s, tab, **options)


def test_constante():
    s = "g(x)=5"
    options = {'derivee': True, 'stretch': False}
    tab = \
r'''\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCC|}
\hline
\,\,x\,\,        &-\infty       &          &+\infty\\
\hline
g'(x)            &              &0         & \\
\hline
\niveau{1}{1}g(x)&\niveau{1}{1}5&\constante&5\\
\hline
\end{tabvar}\]
% x;g(x):(-oo;5) == (+oo;5)
% g(x)=5
'''
    assert_tabvar(s, tab, **options)


def test_abs():
    s = "abs(x**2-5)"
    options = {'derivee': True, 'limites':True, 'stretch': False}
    tab = \
r'''\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCCCCCCCCCCCC|}
\hline
\,\,x\,\,                         &-\infty             &        & &-\sqrt{5}& &      &0&        & &\sqrt{5}& &      &+\infty\\
\hline
f'(x)                             &                    &-       &&\dbarre&    &+     &0&-       &&\dbarre&   &+     & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f$}&\niveau{2}{2}+\infty&\decroit& &0&         &\croit&5&\decroit& &0&        &\croit&+\infty\\
\hline
\end{tabvar}\]
% x;f:(-oo;+oo) >> (-sqrt(5);0;|) << (0;5;0) >> (sqrt(5);0;|) << (+oo;+oo)
% abs(x**2-5)
'''
    assert_tabvar(s, tab, **options)


def test_issue_286():
    s = 'sqrt{x^2 - 1}'
    options = {'derivee': True, 'stretch': False}
    tab = \
r'''\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCCCCUCCCCC|}
\hline
\,\,x\,\,                         &-\infty             &        & &-1&    &\hspace*{15mm}& &1&     &      &+\infty\\
\hline
f'(x)                             &                    &-       &&\dbarre&&              &&\dbarre&&+     & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f$}&\niveau{2}{2}+\infty&\decroit& &0&     &              & &0&     &\croit&+\infty\\
\hline
\end{tabvar}\]
% x;f:(-oo;+oo) >> (-1;0;|) XX (1;0;|) << (+oo;+oo)
% sqrt{x^2 - 1}
'''
    assert_tabvar(s, tab, **options)

def test_zeros_derivee():
    s = 'f(x)=x^3'
    options = {'derivee': True, 'stretch': False}
    tab = \
r'''\setlength{\TVextraheight}{\baselineskip}
\[\begin{tabvar}{|C|CCCCC|}
\hline
\,\,x\,\,        &-\infty             &      &0&      &+\infty\\
\hline
f'(x)            &                    &+     &0&+     &\\
\hline
\niveau{2}{3}f(x)&\niveau{1}{3}-\infty&\croit&0&\croit&+\infty\\
\hline
\end{tabvar}\]
% x;f(x):(-oo;-oo;) << (0;0;0) << (+oo;+oo;)
% f(x)=x^3
'''
