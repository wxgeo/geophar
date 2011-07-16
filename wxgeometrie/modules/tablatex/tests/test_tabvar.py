# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from wxgeometrie.modules.tablatex.tests.tabtestlib import assert_tableau
from wxgeometrie.modules.tablatex.tabvar import tabvar


def assert_tabvar(chaine, code_latex):
    assert_tableau(tabvar, chaine, code_latex)


def test_mode_manuel():
    s = "x;f(x);f'(x):0;2;|>>1;0;1<<2;3;0"
    tab = \
r"""\[\begin{tabvar}{|C|CCCCCCC|}
\hline
x                                    & &0&             &        &1&      &2\\
\hline
f'(x)                                &&\dbarre&        &-       &1&+     &0\\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f(x)$}&\niveau{2}{2} &2&&\decroit&0&\croit&3\\
\hline
\end{tabvar}\]
% x;f(x);f'(x):0;2;|>>1;0;1<<2;3;0
"""
    assert_tabvar(s, tab)

    s = "x;f(x);f'(x):(0;2;|) >> (1;0;1) << (2;3;0)"
    tab = \
r"""\[\begin{tabvar}{|C|CCCCCCC|}
\hline
x                                    & &0&             &        &1&      &2\\
\hline
f'(x)                                &&\dbarre&        &-       &1&+     &0\\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f(x)$}&\niveau{2}{2} &2&&\decroit&0&\croit&3\\
\hline
\end{tabvar}\]
% x;f(x);f'(x):(0;2;|) >> (1;0;1) << (2;3;0)
"""
    assert_tabvar(s, tab)

    s = "x;f(x):-oo;+oo>>0;-oo|+oo>>+oo;-oo"
    tab = \
r"""\[\begin{tabvar}{|C|CCCCCCC|}
\hline
x                                    &-\infty             &        & &0&                                &        &+\infty\\
\hline
f'(x)                                &                    &-       &&\dbarre&                           &-       & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f(x)$}&\niveau{2}{2}+\infty&\decroit&-\infty&\dbarre&\niveau{2}{2}+\infty&\decroit&-\infty\\
\hline
\end{tabvar}\]
% x;f(x):-oo;+oo>>0;-oo|+oo>>+oo;-oo
"""
    assert_tabvar(s, tab)

    s = "x;f(x): (-oo;+oo)>>(0;-oo|+oo)>>(+oo;-oo)"
    tab = \
r"""\[\begin{tabvar}{|C|CCCCCCC|}
\hline
x                                    &-\infty             &        & &0&                                &        &+\infty\\
\hline
f'(x)                                &                    &-       &&\dbarre&                           &-       & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f(x)$}&\niveau{2}{2}+\infty&\decroit&-\infty&\dbarre&\niveau{2}{2}+\infty&\decroit&-\infty\\
\hline
\end{tabvar}\]
% x;f(x): (-oo;+oo)>>(0;-oo|+oo)>>(+oo;-oo)
"""
    assert_tabvar(s, tab)

    s = "x;f(x);f'(x):(0;2;|) >> (1;-oo) || (2;+oo) << (+oo;3)"
    tab = \
r"""\[\begin{tabvar}{|C|CCCCCNCCC|}
\hline
x                                    & &0&             &        &1      &\hspace*{15mm}&2      &      &+\infty\\
\hline
f'(x)                                &&\dbarre&        &-       &0      &              &0      &+     & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f(x)$}&\niveau{2}{2} &2&&\decroit&-\infty&              &+\infty&\croit&3\\
\hline
\end{tabvar}\]
% x;f(x);f'(x):(0;2;|) >> (1;-oo) || (2;+oo) << (+oo;3)
"""
    assert_tabvar(s, tab)




def test_mode_auto():
    s = 'f(x)=(x+1)/(3x-2)'
    tab = \
r"""\[\begin{tabvar}{|C|CCCCCCC|}
\hline
x                                    &-\infty                 &        & &\frac{2}{3}&                      &        &+\infty\\
\hline
f'(x)                                &                        &-       &&\dbarre&                           &-       & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f(x)$}&\niveau{2}{2}\frac{1}{3}&\decroit&-\infty&\dbarre&\niveau{2}{2}+\infty&\decroit&\frac{1}{3}\\
\hline
\end{tabvar}\]
% x;f(x):(-oo;1/3) >> (2/3;-oo|+oo;|) >> (+oo;1/3)
% f(x)=(x+1)/(3x-2)
"""
    assert_tabvar(s, tab)

    s = "(x+1)(x+2)"
    tab = \
r"""\[\begin{tabvar}{|C|CCCCC|}
\hline
x                                 &-\infty             &        &-\frac{3}{2}&      &+\infty\\
\hline
f'(x)                             &                    &-       &0           &+     & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f$}&\niveau{2}{2}+\infty&\decroit&-\frac{1}{4}&\croit&+\infty\\
\hline
\end{tabvar}\]
% x;f:(-oo;+oo) >> (-3/2;-1/4) << (+oo;+oo)
% (x+1)(x+2)
"""
    assert_tabvar(s, tab)

    s = "f(x)=5*ln(x)/x+3"
    tab = \
r"""\[\begin{tabvar}{|C|CCCCCCC|}
\hline
x                                    & &0&                                      &      &\e            &        &+\infty\\
\hline
f'(x)                                &&\dbarre&                                 &+     &0             &-       & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f(x)$}&\niveau{1}{2}&\dbarre&\niveau{1}{2}-\infty&\croit&5 \exp{-1} + 3&\decroit&3\\
\hline
\end{tabvar}\]
% x;f(x):(0;|-oo;|) << (e;5*exp(-1) + 3) >> (+oo;3)
% f(x)=5*ln(x)/x+3
"""
    assert_tabvar(s, tab)


def test_intervalle():
    s = "x^2 sur [1;+oo["
    tab = \
r"""\[\begin{tabvar}{|C|CCC|}
\hline
x                                 &1             &      &+\infty\\
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
r"""\[\begin{tabvar}{|C|CCCCC|}
\hline
x                                    &-\infty       &        &\ln{2}&      &+\infty\\
\hline
f'(x)                                &              &-       &0     &+     & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f(x)$}&\niveau{2}{2}5&\decroit&-7    &\croit&+\infty\\
\hline
\end{tabvar}\]
% x;f(x):(-oo;5) >> (ln(2);-7) << (+oo;+oo)
% f(x)=3e^{2x}-12e^{x}+5
"""
    assert_tabvar(s, tab)


def test_issue_194():
    s = "<< -1/ln(2) >>"
    tab = \
r"""\[\begin{tabvar}{|C|CCCCC|}
\hline
x                                 &-\infty      &      &-\frac{1}{\ln{2}}&        &+\infty\\
\hline
f'(x)                             &             &+     &0                &-       & \\
\hline
\niveau{1}{2}\raisebox{0.5em}{$f$}&\niveau{1}{2}&\croit&                 &\decroit&\\
\hline
\end{tabvar}\]
% << -1/ln(2) >>
"""
    assert_tabvar(s, tab)
