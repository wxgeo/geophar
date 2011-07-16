# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from wxgeometrie.modules.tablatex.tests.tabtestlib import assert_tableau
from wxgeometrie.modules.tablatex.tabval import tabval


def assert_tabval(chaine, code_latex):
    assert_tableau(tabval, chaine, code_latex)




def test_mode_manuel():
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
    assert_tabval(s, tab)

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
    assert_tabval(s, tab)


def test_mode_auto():
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
    assert_tabval(s, tab)
