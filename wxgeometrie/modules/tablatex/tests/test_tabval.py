# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../../.."))
sys.path.insert(0, TOPDIR)


from wxgeometrie.modules.tablatex.tabval import tabval
from wxgeometrie import param

import tools.unittest

class ModuleTablatexTest(tools.unittest.TestCase):

    def assert_tabval(self, chaine, code_latex, **options):
        self.assert_tableau(tabval, chaine, code_latex, **options)


    def test_mode_manuel(self, ):
        s = "f(x)=exp(x+1): 0.25: -5, -4..0 ; 0.5 ; 1, 2..6 ; 7, 10..21"
        tab = \
r"""\begin{center}
\begin{tabular}{|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|}
\hline
$x$    & $-5$ & $-4$ & $-3$   & $-2$   & $-1$ & $0$    & $0,5$ & $1$   & $2$  & $3$    & $4$     & $5$     & $6$       & $7$    & $10$       & $13$         & $16$          & $19$          & $21$ \\
\hline
$f(x)$ & $0$  & $0$  & $0,25$ & $0,25$ & $1$  & $2,75$ & $4,5$ & $7,5$ & $20$ & $54,5$ & $148,5$ & $403,5$ & $1096,75$ & $2981$ & $59874,25$ & $1202604,25$ & $24154952,75$ & $485165195,5$ & $3584912846,25$ \\
\hline
\end{tabular}
\end{center}
% f(x)=exp(x+1): 0.25: -5, -4..0 ; 0.5 ; 1, 2..6 ; 7, 10..21
"""
        self.assert_tabval(s, tab)

        s = "f(x)=exp(x+1): [0.25]: -5,-4..0 ; 0.5 ; 1,2..6 ; 7,10..21"
        tab = \
r"""\begin{center}
\begin{tabular}{|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|}
\hline
$x$    & $-5$ & $-4$ & $-3$   & $-2$   & $-1$ & $0$    & $0,5$ & $1$   & $2$  & $3$    & $4$     & $5$     & $6$       & $7$    & $10$       & $13$         & $16$          & $19$          & $21$ \\
\hline
$f(x)$ & $0$  & $0$  & $0,25$ & $0,25$ & $1$  & $2,75$ & $4,5$ & $7,5$ & $20$ & $54,5$ & $148,5$ & $403,5$ & $1096,75$ & $2981$ & $59874,25$ & $1202604,25$ & $24154952,75$ & $485165195,5$ & $3584912846,25$ \\
\hline
\end{tabular}
\end{center}
% f(x)=exp(x+1): [0.25]: -5,-4..0 ; 0.5 ; 1,2..6 ; 7,10..21
"""
        self.assert_tabval(s, tab)


    def test_coupure(self, ):
        s = "(2x+3)^2:-10..0// 1..10"
        tab = \
r"""\begin{center}
\begin{tabular}{|c|c|c|c|c|c|c|c|c|c|c|c|}
\hline
$x$        & $-10$ & $-9$  & $-8$  & $-7$  & $-6$ & $-5$ & $-4$ & $-3$ & $-2$ & $-1$ & $0$ \\
\hline
$(2x+3)^2$ & $289$ & $225$ & $169$ & $121$ & $81$ & $49$ & $25$ & $9$  & $1$  & $1$  & $9$ \\
\hline
\end{tabular}

\begin{tabular}{|c|c|c|c|c|c|c|c|c|c|c|}
\hline
$x$        & $1$  & $2$  & $3$  & $4$   & $5$   & $6$   & $7$   & $8$   & $9$   & $10$ \\
\hline
$(2x+3)^2$ & $25$ & $49$ & $81$ & $121$ & $169$ & $225$ & $289$ & $361$ & $441$ & $529$ \\
\hline
\end{tabular}
\end{center}
% (2x+3)^2:-10..0// 1..10
"""
        self.assert_tabval(s, tab)


    def test_mode_auto(self, ):
        s = r"\frac{x^2}{2} sur [-4;4]"
        tab = \
r"""\begin{center}
\begin{tabular}{|c|c|c|c|c|c|c|c|c|c|}
\hline
$x$             & $-4$ & $-3$  & $-2$ & $-1$  & $0$ & $1$   & $2$ & $3$   & $4$ \\
\hline
$\frac{x^2}{2}$ & $8$  & $4,5$ & $2$  & $0,5$ & $0$ & $0,5$ & $2$ & $4,5$ & $8$ \\
\hline
\end{tabular}
\end{center}
% \frac{x^2}{2}:[0.01]:-4.0,-3.0..4
% \frac{x^2}{2} sur [-4;4]
"""
        self.assert_tabval(s, tab)

        s = r"\frac{x^2}{2} sur [-4;4] pas 0,5"
        tab = \
r"""\begin{center}
\begin{tabular}{|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|}
\hline
$x$             & $-4$ & $-3,5$ & $-3$  & $-2,5$ & $-2$ & $-1,5$ & $-1$  & $-0,5$ & $0$ & $0,5$  & $1$   & $1,5$  & $2$ & $2,5$  & $3$   & $3,5$  & $4$ \\
\hline
$\frac{x^2}{2}$ & $8$  & $6,13$ & $4,5$ & $3,13$ & $2$  & $1,13$ & $0,5$ & $0,13$ & $0$ & $0,13$ & $0,5$ & $1,13$ & $2$ & $3,13$ & $4,5$ & $6,13$ & $8$ \\
\hline
\end{tabular}
\end{center}
% \frac{x^2}{2}:[0.01]:-4.0,-3.5..4
% \frac{x^2}{2} sur [-4;4] pas 0,5
"""
        self.assert_tabval(s, tab)


    def test_param_separateur_decimal(self, ):
        try:
            param.separateur_decimal = '.'
            s = "f(x)=exp(x+1): 0.25: -5, -4..0 ; 0.5 ; 1, 2..6 ; 7, 10..21"
            tab = \
r"""\begin{center}
\begin{tabular}{|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|}
\hline
$x$    & $-5$ & $-4$ & $-3$   & $-2$   & $-1$ & $0$    & $0.5$ & $1$   & $2$  & $3$    & $4$     & $5$     & $6$       & $7$    & $10$       & $13$         & $16$          & $19$          & $21$ \\
\hline
$f(x)$ & $0$  & $0$  & $0.25$ & $0.25$ & $1$  & $2.75$ & $4.5$ & $7.5$ & $20$ & $54.5$ & $148.5$ & $403.5$ & $1096.75$ & $2981$ & $59874.25$ & $1202604.25$ & $24154952.75$ & $485165195.5$ & $3584912846.25$ \\
\hline
\end{tabular}
\end{center}
% f(x)=exp(x+1): 0.25: -5, -4..0 ; 0.5 ; 1, 2..6 ; 7, 10..21
"""
            self.assert_tabval(s, tab)
        finally:
            param.separateur_decimal = ','


    def test_formatage(self, ):
        s = 'x^2:-2..2'
        tab = \
r"""\begin{center}
\begin{tabular}{|c|c|c|c|c|c|}
\hline
$x$   & $\textbf{-2}$   & $\textbf{-1}$   & $\textbf{0}$    & $\textbf{1}$    & $\textbf{2}$ \\
\hline
$x^2$ & $\color{gray}4$ & $\color{gray}1$ & $\color{gray}0$ & $\color{gray}1$ & $\color{gray}4$ \\
\hline
\end{tabular}
\end{center}
% x^2:-2..2
"""
        self.assert_tabval(s, tab, formatage_antecedents=r'\textbf{VAL}',
                              formatage_images=r'\color{gray}VAL')
