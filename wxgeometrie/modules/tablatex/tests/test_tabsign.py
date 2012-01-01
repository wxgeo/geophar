# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from wxgeometrie.modules.tablatex.tests.tabtestlib import assert_tableau
from wxgeometrie.modules.tablatex.tabsign import tabsign



def assert_tabsign(chaine, code_latex):
    assert_tableau(tabsign, chaine, code_latex)


def test_mode_manuel():
    s = "x: -oo;+oo// 2x+1: -- -1/2 ++// 3-x: ++ 3 --// f(x)"
    tab = \
r"""\begin{center}
\begin{tabular}{|c|ccccccc|}
\hline
$x$    & $-\infty$ &     & $-\frac{1}{2}$ &   & $3$ &     & $+\infty$ \\
\hline
$2x+1$ &           & $-$ &       0        & + &     &  +  &           \\
\hline
$3-x$  &           &  +  &                & + &  0  & $-$ &           \\
\hline
$f(x)$ &           & $-$ &       0        & + &  0  & $-$ &           \\
\hline
\end{tabular}
\end{center}
% x: -oo;+oo// 2x+1: -- -1/2 ++// 3-x: ++ 3 --// f(x)
"""
    assert_tabsign(s, tab)



def test_mode_auto():
    s = 'g(x)=(x-7/2)(x+7/2)'
    tab = \
r'''\begin{center}
\begin{tabular}{|c|ccccccc|}
\hline
$x$             & $-\infty$ &     & $-\frac{7}{2}$ &     & $\frac{7}{2}$ &   & $+\infty$ \\
\hline
$x-\frac{7}{2}$ &           & $-$ &                & $-$ &       0       & + &           \\
\hline
$x+\frac{7}{2}$ &           & $-$ &       0        &  +  &               & + &           \\
\hline
$g(x)$          &           &  +  &       0        & $-$ &       0       & + &           \\
\hline
\end{tabular}
\end{center}
% x: -oo;+oo// x-7/2: -- 7/2 ++ // x+7/2: -- -7/2 ++ // g(x)
% g(x)=(x-7/2)(x+7/2)
'''
    assert_tabsign(s, tab)


def test_polynomes():
    s= 'f(x)=x^3-30x^2+112'
    tab = \
r"""\begin{center}
\begin{tabular}{|c|ccccccccc|}
\hline
$x$                  & $-\infty$ &     & $-6 \sqrt{7} + 14$ &   & $2$ &     & $14 + 6 \sqrt{7}$ &   & $+\infty$ \\
\hline
$f(x)$               &           & $-$ &         0          & + &  0  & $-$ &         0         & + &           \\
\hline
\end{tabular}
\end{center}
% x: -oo;+oo// x^3-30 x^2+112: -- -6*sqrt(7) + 14 ++ 2 -- 14 + 6*sqrt(7) ++ // f(x)
% f(x)=x^3-30x^2+112
"""
    assert_tabsign(s, tab)

    s = '- 6 x^{2} - 12 x + 4'
    tab = \
r'''\begin{center}
\begin{tabular}{|c|ccccccc|}
\hline
$x$                    & $-\infty$ &     & $-\frac{\sqrt{15}}{3} - 1$ &   & $-1 + \frac{\sqrt{15}}{3}$ &     & $+\infty$ \\
\hline
$- 6 x^{2} - 12 x + 4$ &           & $-$ &             0              & + &             0              & $-$ &           \\
\hline
\end{tabular}
\end{center}
% x: -oo;+oo// -6 x^(2)-12 x+4: -- -sqrt(15)/3 - 1 ++ -1 + sqrt(15)/3 -- // - 6 x^{2} - 12 x + 4
% - 6 x^{2} - 12 x + 4
'''
    assert_tabsign(s, tab)


def test_quotients():
    s = '(3x-2)/((x-1)^2)'
    tab = \
r'''\begin{center}
\begin{tabular}{|c|ccccccc|}
\hline
$x$                      & $-\infty$ &     & $\frac{2}{3}$ &   & $1$ &   & $+\infty$ \\
\hline
$3 x-2$                  &           & $-$ &       0       & + &     & + &           \\
\hline
$(x-1)^{2}$              &           &  +  &               & + &  0  & + &           \\
\hline
$\frac{3x-2}{(x-1)^{2}}$ &           & $-$ &       0       & + &  || & + &           \\
\hline
\end{tabular}
\end{center}
% x: -oo;!1: !1;+oo// 3 x-2: -- 2/3 ++ // !(x-1)^2: ++ 1 ++ // (3x-2)/((x-1)^2)
% (3x-2)/((x-1)^2)
'''
    assert_tabsign(s, tab)

    s = '(3x-2)/(x-1)^2'
    tab = \
r'''\begin{center}
\begin{tabular}{|c|ccccccc|}
\hline
$x$                      & $-\infty$ &     & $\frac{2}{3}$ &   & $1$ &   & $+\infty$ \\
\hline
$3 x-2$                  &           & $-$ &       0       & + &     & + &           \\
\hline
$(x-1)^{2}$              &           &  +  &               & + &  0  & + &           \\
\hline
$\frac{3x-2}{(x-1)^{2}}$ &           & $-$ &       0       & + &  || & + &           \\
\hline
\end{tabular}
\end{center}
% x: -oo;!1: !1;+oo// 3 x-2: -- 2/3 ++ // !(x-1)^2: ++ 1 ++ // (3x-2)/(x-1)^2
% (3x-2)/(x-1)^2
'''
    assert_tabsign(s, tab)


def test_latex():
    s = '\dfrac{3x-2}{(x-1)^2}'
    tab = \
r'''\begin{center}
\begin{tabular}{|c|ccccccc|}
\hline
$x$                       & $-\infty$ &     & $\frac{2}{3}$ &   & $1$ &   & $+\infty$ \\
\hline
$3 x-2$                   &           & $-$ &       0       & + &     & + &           \\
\hline
$(x-1)^{2}$               &           &  +  &               & + &  0  & + &           \\
\hline
$\dfrac{3x-2}{(x-1)^{2}}$ &           & $-$ &       0       & + &  || & + &           \\
\hline
\end{tabular}
\end{center}
% x: -oo;!1: !1;+oo// 3 x-2: -- 2/3 ++ // !(x-1)^2: ++ 1 ++ // \dfrac{3x-2}{(x-1)^2}
% \dfrac{3x-2}{(x-1)^2}
'''
    assert_tabsign(s, tab)

    s = "g(x)=\dfrac{-x+1}{\e^{x}}"
    tab = \
r'''\begin{center}
\begin{tabular}{|c|ccccc|}
\hline
$x$      & $-\infty$ &   & $1$ &     & $+\infty$ \\
\hline
$-x+1$   &           & + &  0  & $-$ &           \\
\hline
$\e^{x}$ &           & + &     &  +  &           \\
\hline
$g(x)$   &           & + &  0  & $-$ &           \\
\hline
\end{tabular}
\end{center}
% x: -oo;+oo// -x+1: ++ 1 -- // e^(x): ++ // g(x)
% g(x)=\dfrac{-x+1}{\e^{x}}
'''
    assert_tabsign(s, tab)

    s= "f'(x)=1-\e^{-x+2}"
    tab = \
r'''\begin{center}
\begin{tabular}{|c|ccccc|}
\hline
$x$           & $-\infty$ &     & $2$ &   & $+\infty$ \\
\hline
$f'(x)$       &           & $-$ &  0  & + &           \\
\hline
\end{tabular}
\end{center}
% x: -oo;+oo// 1-e^(-x+2): -- 2 ++ // f'(x)
% f'(x)=1-\e^{-x+2}
'''
    assert_tabsign(s, tab)


def test_intervalle():
    s = "x^2 sur [1;+oo["
    tab = \
r'''\begin{center}
\begin{tabular}{|c|ccc|}
\hline
$x$     & $1$ &   & $+\infty$ \\
\hline
$x^{2}$ &     & + &           \\
\hline
\end{tabular}
\end{center}
% x: 1;+oo// x^2: ++ // x^2
% x^2 sur [1;+\infty[
'''
    assert_tabsign(s, tab)

    s = "u(x)=1-x sur ]0;+oo["
    tab = \
r'''\begin{center}
\begin{tabular}{|c|ccccc|}
\hline
$x$    & $0$ &   & $1$ &     & $+\infty$ \\
\hline
$u(x)$ &  || & + &  0  & $-$ &           \\
\hline
\end{tabular}
\end{center}
% x: !0;+oo// 1-x: ++ 1 -- // u(x)
% u(x)=1-x sur ]0;+\infty[
'''
    assert_tabsign(s, tab)

    s = "u(x)=x(1-x) sur ]-1;0[U]0;4["
    tab = \
r'''\begin{center}
\begin{tabular}{|c|ccccccc|}
\hline
$x$    & $-1$ &     & $0$ &   & $1$ &     & $4$ \\
\hline
$x$    &      & $-$ &  0  & + &     &  +  &     \\
\hline
$1-x$  &      &  +  &     & + &  0  & $-$ &     \\
\hline
$u(x)$ &  ||  & $-$ &  || & + &  0  & $-$ &  || \\
\hline
\end{tabular}
\end{center}
% x: !-1;!0: !0;!4// !x: -- 0 ++ // 1-x: ++ 1 -- // u(x)
% u(x)=x(1-x) sur ]-1;0[U]0;4[
'''
    assert_tabsign(s, tab)


    s = "u(x)=(1+x)(1-x)/x sur ]-3;2[U]2;4]"
    tab = \
r'''\begin{center}
\begin{tabular}{|c|ccccccccccc|}
\hline
$x$    & $-3$ &     & $-1$ &     & $0$ &   & $1$ &     & $2$ &     & $4$ \\
\hline
$1+x$  &      & $-$ &  0   &  +  &     & + &     &  +  &     &  +  &     \\
\hline
$1-x$  &      &  +  &      &  +  &     & + &  0  & $-$ &     & $-$ &     \\
\hline
$x$    &      & $-$ &      & $-$ &  0  & + &     &  +  &     &  +  &     \\
\hline
$u(x)$ &  ||  &  +  &  0   & $-$ &  || & + &  0  & $-$ &  || & $-$ &     \\
\hline
\end{tabular}
\end{center}
% x: !-3;!0: !0;!2: !2;4// 1+x: -- -1 ++ // 1-x: ++ 1 -- // !x: -- 0 ++ // u(x)
% u(x)=(1+x)(1-x)/x sur ]-3;2[U]2;4]
'''
    assert_tabsign(s, tab)


def test_issue_173():
    s = "(1 - x)\e^{ 2x}"
    tab = \
r'''\begin{center}
\begin{tabular}{|c|ccccc|}
\hline
$x$               & $-\infty$ &   & $1$ &     & $+\infty$ \\
\hline
$1-x$             &           & + &  0  & $-$ &           \\
\hline
$\e^{2 x}$        &           & + &     &  +  &           \\
\hline
$(1 - x)\e^{ 2x}$ &           & + &  0  & $-$ &           \\
\hline
\end{tabular}
\end{center}
% x: -oo;+oo// 1-x: ++ 1 -- // e^(2 x): ++ // (1 - x)\e^{ 2x}
% (1 - x)\e^{ 2x}
'''
    assert_tabsign(s, tab)


def test_issue_200():
    s = 'f(x)=x^2-3'
    tab = \
r'''\begin{center}
\begin{tabular}{|c|ccccccc|}
\hline
$x$       & $-\infty$ &   & $-\sqrt{3}$ &     & $\sqrt{3}$ &   & $+\infty$ \\
\hline
$f(x)$    &           & + &      0      & $-$ &     0      & + &           \\
\hline
\end{tabular}
\end{center}
% x: -oo;+oo// x^2-3: ++ -sqrt(3) -- sqrt(3) ++ // f(x)
% f(x)=x^2-3
'''
    assert_tabsign(s, tab)
