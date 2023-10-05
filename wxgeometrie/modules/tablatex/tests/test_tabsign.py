# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../../../.."))
sys.path.insert(0, TOPDIR)


from wxgeometrie.modules.tablatex.tabsign import tabsign

import wx_unittest

class ModulesTablatexTest(wx_unittest.TestCase):

    def assert_tabsign(self, chaine, code_latex, **options):
        self.assert_tableau(tabsign, chaine, code_latex, **options)


    def test_mode_manuel(self, ):
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
        self.assert_tabsign(s, tab)



    def test_mode_auto(self, ):
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
        self.assert_tabsign(s, tab)


    def test_polynomes(self, ):
        s= 'f(x)=x^3-30x^2+112'
        tab = \
r"""\begin{center}
\begin{tabular}{|c|ccccccccc|}
\hline
$x$                  & $-\infty$ &     & $14-6 \sqrt{7}$ &   & $2$ &     & $14+6 \sqrt{7}$ &   & $+\infty$ \\
\hline
$f(x)$               &           & $-$ &        0        & + &  0  & $-$ &        0        & + &           \\
\hline
\end{tabular}
\end{center}
% x: -oo;+oo// x^3-30 x^2+112: -- 14 - 6*sqrt(7) ++ 2 -- 14 + 6*sqrt(7) ++ // f(x)
% f(x)=x^3-30x^2+112
"""
        self.assert_tabsign(s, tab)

        s = '- 6 x^{2} - 12 x + 4'
        tab = \
r'''\begin{center}
\begin{tabular}{|c|ccccccc|}
\hline
$x$               & $-\infty$ &     & $-\frac{\sqrt{15}}{3}-1$ &   & $-1+\frac{\sqrt{15}}{3}$ &     & $+\infty$ \\
\hline
$-6 x^{2}-12 x+4$ &           & $-$ &            0             & + &            0             & $-$ &           \\
\hline
\end{tabular}
\end{center}
% x: -oo;+oo// -6 x^(2)-12 x+4: -- -sqrt(15)/3 - 1 ++ -1 + sqrt(15)/3 -- // - 6 x^{2} - 12 x + 4
% - 6 x^{2} - 12 x + 4
'''
        self.assert_tabsign(s, tab)


    def test_quotients(self, ):
        s = '(3x-2)/((x-1)^2)'
        tab = \
r'''\providecommand{\geopharDB}[1]{$\left|\vphantom{\text{#1}}\right|$}
\begin{center}
\begin{tabular}{|c|ccccccc|}
\hline
$x$                      & $-\infty$ &     & $\frac{2}{3}$ &   &                 $1$                  &   & $+\infty$ \\
\hline
$3 x-2$                  &           & $-$ &       0       & + &                                      & + &           \\
\hline
$(x-1)^{2}$              &           &  +  &               & + &                  0                   & + &           \\
\hline
$\frac{3x-2}{(x-1)^{2}}$ &           & $-$ &       0       & + & \geopharDB{$\frac{3x-2}{(x-1)^{2}}$} & + &           \\
\hline
\end{tabular}
\end{center}
% x: -oo;!1: !1;+oo// 3 x-2: -- 2/3 ++ // !(x-1)^2: ++ 1 ++ // (3x-2)/((x-1)^2)
% (3x-2)/((x-1)^2)
'''
        self.assert_tabsign(s, tab)

        s = '(3x-2)/(x-1)^2'
        tab = \
r'''\providecommand{\geopharDB}[1]{$\left|\vphantom{\text{#1}}\right|$}
\begin{center}
\begin{tabular}{|c|ccccccc|}
\hline
$x$                      & $-\infty$ &     & $\frac{2}{3}$ &   &                 $1$                  &   & $+\infty$ \\
\hline
$3 x-2$                  &           & $-$ &       0       & + &                                      & + &           \\
\hline
$(x-1)^{2}$              &           &  +  &               & + &                  0                   & + &           \\
\hline
$\frac{3x-2}{(x-1)^{2}}$ &           & $-$ &       0       & + & \geopharDB{$\frac{3x-2}{(x-1)^{2}}$} & + &           \\
\hline
\end{tabular}
\end{center}
% x: -oo;!1: !1;+oo// 3 x-2: -- 2/3 ++ // !(x-1)^2: ++ 1 ++ // (3x-2)/(x-1)^2
% (3x-2)/(x-1)^2
'''
        self.assert_tabsign(s, tab)


    def test_latex(self, ):
        s = '\dfrac{3x-2}{(x-1)^2}'
        tab = \
r'''\providecommand{\geopharDB}[1]{$\left|\vphantom{\text{#1}}\right|$}
\begin{center}
\begin{tabular}{|c|ccccccc|}
\hline
$x$                       & $-\infty$ &     & $\frac{2}{3}$ &   &                  $1$                  &   & $+\infty$ \\
\hline
$3 x-2$                   &           & $-$ &       0       & + &                                       & + &           \\
\hline
$(x-1)^{2}$               &           &  +  &               & + &                   0                   & + &           \\
\hline
$\dfrac{3x-2}{(x-1)^{2}}$ &           & $-$ &       0       & + & \geopharDB{$\dfrac{3x-2}{(x-1)^{2}}$} & + &           \\
\hline
\end{tabular}
\end{center}
% x: -oo;!1: !1;+oo// 3 x-2: -- 2/3 ++ // !(x-1)^2: ++ 1 ++ // \dfrac{3x-2}{(x-1)^2}
% \dfrac{3x-2}{(x-1)^2}
'''
        self.assert_tabsign(s, tab)

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
        self.assert_tabsign(s, tab)

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
        self.assert_tabsign(s, tab)


    def test_intervalle(self, ):
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
        self.assert_tabsign(s, tab)

        s = "u(x)=1-x sur ]0;+oo["
        tab = \
r'''\providecommand{\geopharDB}[1]{$\left|\vphantom{\text{#1}}\right|$}
\begin{center}
\begin{tabular}{|c|ccccc|}
\hline
$x$    &        $0$         &   & $1$ &     & $+\infty$ \\
\hline
$u(x)$ & \geopharDB{$u(x)$} & + &  0  & $-$ &           \\
\hline
\end{tabular}
\end{center}
% x: !0;+oo// 1-x: ++ 1 -- // u(x)
% u(x)=1-x sur ]0;+\infty[
'''
        self.assert_tabsign(s, tab)

        s = "u(x)=x(1-x) sur ]-1;0[U]0;4["
        tab = \
r'''\providecommand{\geopharDB}[1]{$\left|\vphantom{\text{#1}}\right|$}
\begin{center}
\begin{tabular}{|c|ccccccc|}
\hline
$x$    &        $-1$        &     &        $0$         &   & $1$ &     &        $4$         \\
\hline
$x$    &                    & $-$ &         0          & + &     &  +  &                    \\
\hline
$1-x$  &                    &  +  &                    & + &  0  & $-$ &                    \\
\hline
$u(x)$ & \geopharDB{$u(x)$} & $-$ & \geopharDB{$u(x)$} & + &  0  & $-$ & \geopharDB{$u(x)$} \\
\hline
\end{tabular}
\end{center}
% x: !-1;!0: !0;!4// !x: -- 0 ++ // 1-x: ++ 1 -- // u(x)
% u(x)=x(1-x) sur ]-1;0[U]0;4[
'''
        self.assert_tabsign(s, tab)


        s = "u(x)=(1+x)(1-x)/x sur ]-3;2[U]2;4]"
        tab = \
r'''\providecommand{\geopharDB}[1]{$\left|\vphantom{\text{#1}}\right|$}
\begin{center}
\begin{tabular}{|c|ccccccccccc|}
\hline
$x$    &        $-3$        &     & $-1$ &     &        $0$         &   & $1$ &     &        $2$         &     & $4$ \\
\hline
$1+x$  &                    & $-$ &  0   &  +  &                    & + &     &  +  &                    &  +  &     \\
\hline
$1-x$  &                    &  +  &      &  +  &                    & + &  0  & $-$ &                    & $-$ &     \\
\hline
$x$    &                    & $-$ &      & $-$ &         0          & + &     &  +  &                    &  +  &     \\
\hline
$u(x)$ & \geopharDB{$u(x)$} &  +  &  0   & $-$ & \geopharDB{$u(x)$} & + &  0  & $-$ & \geopharDB{$u(x)$} & $-$ &     \\
\hline
\end{tabular}
\end{center}
% x: !-3;!0: !0;!2: !2;4// 1+x: -- -1 ++ // 1-x: ++ 1 -- // !x: -- 0 ++ // u(x)
% u(x)=(1+x)(1-x)/x sur ]-3;2[U]2;4]
'''
        self.assert_tabsign(s, tab)


    def test_issue_173(self, ):
        s = "(1 - x)\e^{ 2x}"
        tab = \
r'''\begin{center}
\begin{tabular}{|c|ccccc|}
\hline
$x$             & $-\infty$ &   & $1$ &     & $+\infty$ \\
\hline
$1-x$           &           & + &  0  & $-$ &           \\
\hline
$\e^{2 x}$      &           & + &     &  +  &           \\
\hline
$(1-x)\e^{ 2x}$ &           & + &  0  & $-$ &           \\
\hline
\end{tabular}
\end{center}
% x: -oo;+oo// 1-x: ++ 1 -- // e^(2 x): ++ // (1 - x)\e^{ 2x}
% (1 - x)\e^{ 2x}
'''
        self.assert_tabsign(s, tab)


    def test_issue_200(self, ):
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
        self.assert_tabsign(s, tab)


    def test_issue_189(self, ):
        # Tableaux de signes et de variation avec des decimaux
        s = '2-0.25x'
        options = {'cellspace': True}
        tab = \
r'''\begin{center}
\begin{tabular}{|Sc|ScScScScSc|}
\hline
$x$        & $-\infty$ &   & $8$ &     & $+\infty$ \\
\hline
$2-0.25x$  &           & + &  0  & $-$ &           \\
\hline
\end{tabular}
\end{center}
% x: -oo;+oo// 2-0.25 x: ++ 8 -- // 2-0.25x
% 2-0.25x
'''
        self.assert_tabsign(s, tab, **options)


    def test_intervalle_virgule(self, ):
        s = 'h(x)=x^2-x/2-3 sur [-2,5;3,5]'
        options = {'cellspace': True}
        tab = \
r'''\begin{center}
\begin{tabular}{|Sc|ScScScScScScSc|}
\hline
$x$                   & $-2,5$ &   & $-\frac{3}{2}$ &     & $2$ &   & $3,5$ \\
\hline
$h(x)$                &        & + &       0        & $-$ &  0  & + &       \\
\hline
\end{tabular}
\end{center}
% x: -2,5;3,5// x^2-x/2-3: ++ -3/2 -- 2 ++ // h(x)
% h(x)=x^2-x/2-3 sur [-2,5;3,5]
'''
        self.assert_tabsign(s, tab, **options)


    def test_constante(self, ):
        s = 'f(x)=5'
        tab = \
r'''\begin{center}
\begin{tabular}{|c|ccc|}
\hline
$x$    & $-\infty$ &   & $+\infty$ \\
\hline
$f(x)$ &           & + &           \\
\hline
\end{tabular}
\end{center}
% x: -oo;+oo// 5: ++ // f(x)
% f(x)=5
'''
        self.assert_tabsign(s, tab)


    def test_issue_247(self, ):
        "FS#247 - Accepter la syntaxe suivant : 'f(x): -- -8 ++ -2 -- 5 ++'."
        s = "f(x): -- -8 ++ -2 -- 5 ++"
        tab = \
r'''\begin{center}
\begin{tabular}{|c|ccccccccc|}
\hline
$x$    & $-\infty$ &     & $-8$ &   & $-2$ &     & $5$ &   & $+\infty$ \\
\hline
$f(x)$ &           & $-$ &  0   & + &  0   & $-$ &  0  & + &           \\
\hline
\end{tabular}
\end{center}
% f(x): -- -8 ++ -2 -- 5 ++
'''
        self.assert_tabsign(s, tab)

    def test_mix_numeric_and_symbolic_values(self, ):
        s = 'f(x): -- x_1 ++ 5 ++ x_2 -- 7 --'
        tab = \
r'''\begin{center}
\begin{tabular}{|c|ccccccccccc|}
\hline
$x$    & $-\infty$ &     & $x_1$ &   & $5$ &   & $x_2$ &     & $7$ &     & $+\infty$ \\
\hline
$f(x)$ &           & $-$ &   0   & + &  0  & + &   0   & $-$ &  0  & $-$ &           \\
\hline
\end{tabular}
\end{center}
% f(x): -- x_1 ++ 5 ++ x_2 -- 7 --
'''
        self.assert_tabsign(s, tab)

        s = r'x:-oo;+oo // f(x): -- 5 ++ // g(x): ++ \alpha=2,1 --'
        tab = \
r'''\begin{center}
\begin{tabular}{|c|ccccccc|}
\hline
$x$        & $-\infty$ &     & $\alpha$ &     & $5$ &     & $+\infty$ \\
\hline
$f(x)$     &           & $-$ &          & $-$ &  0  &  +  &           \\
\hline
$g(x)$     &           &  +  &    0     & $-$ &     & $-$ &           \\
\hline
$f(x)g(x)$ &           & $-$ &    0     &  +  &  0  & $-$ &           \\
\hline
\end{tabular}
\end{center}
% x:-oo;+oo // f(x): -- 5 ++ // g(x): ++ \alpha=2,1 --
'''
        self.assert_tabsign(s, tab)

    def test_approche(self, ):
        s = "f(x)=x^2-3x-5"
        tab = \
r'''\begin{center}
\begin{tabular}{|c|ccccccc|}
\hline
$x$           & $-\infty$ &   & $\frac{3}{2}-\frac{\sqrt{29}}{2}$ &     & $\frac{3}{2}+\frac{\sqrt{29}}{2}$ &   & $+\infty$ \\
\hline
$f(x)$        &           & + &                 0                 & $-$ &                 0                 & + &           \\
\hline
\end{tabular}
\end{center}
% x: -oo;+oo// x^2-3 x-5: ++ 3/2 - sqrt(29)/2 -- 3/2 + sqrt(29)/2 ++ // f(x)
% f(x)=x^2-3x-5
'''
        self.assert_tabsign(s, tab)

        options = {'approche': True, "decimales": 2}
        tab = \
r'''\begin{center}
\begin{tabular}{|c|ccccccc|}
\hline
$x$           & $-\infty$ &   & $-1,19$ &     & $4,19$ &   & $+\infty$ \\
\hline
$f(x)$        &           & + &    0    & $-$ &   0    & + &           \\
\hline
\end{tabular}
\end{center}
% x: -oo;+oo// x^2-3 x-5: ++ -1,19 -- 4,19 ++ // f(x)
% f(x)=x^2-3x-5
'''
        self.assert_tabsign(s, tab, **options)
