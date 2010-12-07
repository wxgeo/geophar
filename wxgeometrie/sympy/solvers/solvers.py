""" This module contain solvers for all kinds of equations:

    - algebraic, use solve()

    - recurrence, use rsolve()

    - differential, use dsolve()

    - transcendental, use tsolve()

    - nonlinear (numerically), use nsolve()
      (you will need a good starting point)

"""

from sympy.core.sympify import sympify
from sympy.core import S, Mul, Add, Pow, Symbol, Wild, Equality, count_ops
from sympy.core.numbers import ilcm

from sympy.functions import log, exp, LambertW
from sympy.simplify import simplify, collect, powsimp, together
from sympy.matrices import Matrix, zeros
from sympy.polys import roots, cancel, factor
from sympy.functions.elementary.piecewise import piecewise_fold

from sympy.utilities import any, all
from sympy.utilities.iterables import iff
from sympy.utilities.lambdify import lambdify
from sympy.mpmath import findroot

from sympy.solvers.polysys import solve_poly_system

from warnings import warn

# Codes for guess solve strategy
GS_POLY = 0
GS_RATIONAL = 1
GS_POLY_CV_1 = 2 # can be converted to a polynomial equation via the change of variable y -> x**a, a real
GS_POLY_CV_2 = 3 # can be converted to a polynomial equation multiplying on both sides by x**m
                 # for example, x + 1/x == 0. Multiplying by x yields x**2 + x == 0
GS_RATIONAL_CV_1 = 4 # can be converted to a rational equation via the change of variable y -> x**n
GS_PIECEWISE = 5
GS_TRANSCENDENTAL = 6

def guess_solve_strategy(expr, symbol, denom_check=True):
    """
    Tries to guess what approach should be used to solve a specific equation

    Returns
    =======
       - -1: could not guess
       - integer > 0: code representing certain type of equation. See GS_* fields
         on this module for a complete list

    Examples
    ========
    >>> from sympy import Symbol, Rational
    >>> from sympy.solvers.solvers import guess_solve_strategy
    >>> from sympy.abc import x
    >>> guess_solve_strategy(x**2 + 1, x)
    0
    >>> guess_solve_strategy(x**Rational(1,2) + 1, x)
    2

    """
    eq_type = -1
    if not expr.has(symbol):
        return GS_POLY

    elif expr.is_Add:
        return max([guess_solve_strategy(i, symbol) for i in expr.args])

    elif expr.is_Mul:
        # check for rational functions
        if denom_check:
            num, denom = expr.as_numer_denom()
        if denom_check and denom != 1 and denom.has(symbol):
            #we have a quotient
            m = max(guess_solve_strategy(num, symbol),
                    guess_solve_strategy(denom, symbol))
            if m == GS_POLY:
                return GS_RATIONAL
            elif m == GS_POLY_CV_1:
                return GS_RATIONAL_CV_1
            elif m == GS_TRANSCENDENTAL:
                return GS_TRANSCENDENTAL
        else:
            return max([guess_solve_strategy(i, symbol) for i in expr.args])

    elif expr.is_Symbol:
        return GS_POLY

    elif expr.is_Pow:

        if expr.exp.has(symbol):
            return GS_TRANSCENDENTAL
        elif not expr.exp.has(symbol) and expr.base.has(symbol):
            if expr.base.is_Pow:
                # strategy for (3**x)**5 must be GS_TRANSCENDENTAL, and not GS_POLY
                return max(eq_type, guess_solve_strategy(expr.base, symbol))
            if expr.exp.is_Integer and expr.exp > 0:
                eq_type = max(eq_type, GS_POLY)
            elif expr.exp.is_Integer and expr.exp < 0:
                eq_type = max(eq_type, GS_POLY_CV_2)
            elif expr.exp.is_Rational:
                eq_type = max(eq_type, GS_POLY_CV_1)
            else:
                return GS_TRANSCENDENTAL

    elif expr.is_Piecewise:
        return GS_PIECEWISE

    elif expr.is_Function and expr.has(symbol):
        return GS_TRANSCENDENTAL


    return eq_type

def checksol(f, symbol, sol, **flags):
    """Checks whether sol is a solution of equation f == 0.

       >>> from sympy import symbols
       >>> from sympy.solvers import checksol
       >>> x,y = symbols('xy')
       >>> checksol(x**4-1, x, 1)
       True
       >>> checksol(x**4-1, x, 0)
       False

       None is returned if checksol() could not conclude.

       Use flag 'numerical_check=True' for a fast numerical testing,
       in case f has only one symbol.
       Use flag 'minimal_check=True' for a very fast yet minimal testing.
       Use flag 'warning=True' to print a warning if checksol() could not conclude.
       Use flag 'simplified=True' if sol was already simplified
       before, so as to avoid redundant simplification.
    """
    for attempt in xrange(8):
        if attempt == 0:
            val = f.subs(symbol, sol)
        elif attempt == 1:
            if not val.atoms(Symbol) and flags.get('numerical_check', True):
                # val is a constant, so a fast numerical test may be considered sufficient
                val = val.evalf(30)
        elif attempt == 2:
            if flags.get('minimal_check', False):
                return
            if flags.get('simplified', False):
                continue
            val = f.subs(symbol, simplify(sol))
        elif attempt == 3:
            val = powsimp(val)
        elif attempt == 4:
            val = cancel(val)
        elif attempt == 5:
            val = val.expand()
        elif attempt == 6:
            val = together(val)
        elif attempt == 7:
            val = powsimp(val)
        if val.is_zero:
            return True
        elif val.is_nonzero:
            return False
    if flags.get('warning', False):
        print("Warning: solution %s could not be verified." %sol)
    # returns None if it can't conclude
    # TODO: improve solution testing

def solve(f, *symbols, **flags):
    """Solves equations and systems of equations.

        Currently supported are univariate polynomial, transcendental
        equations, piecewise combinations thereof and systems of linear
        and polynomial equations.  Input is formed as a single expression
        or an equation,  or an iterable container in case of an equation
        system.  The type of output may vary and depends heavily on the
        input. For more details refer to more problem specific functions.

        ** Simplification **

        By default all solutions are simplified to make the output more
        readable. If this is not the expected behavior (e.g., because of
        speed issues) set simplified=False in function arguments.

        ** Hint **

        Currently, equation resolution follows these successive steps:
        1) First, a == b is converted to a - b == 0,
        2) Then, a - b is gathered and factorized,
        3) Different strategies are used according to the equation type.

        In some cases, step 2 may lead to less simplified solutions.

        To modify this step, use the 'hint' keyword.
        Avalaible 'hint' values are:

            "default":
                At first attempt, gather and factor before trying solving.
                If solving fails, try successively all other hints.

            "best":
                Try all solving hints, and return the more simplified result found.
                Note that since it will solve the equation many times before comparing
                the different results, it is also many times slower than any other hint.

            "gather_and_factor":
                Gather and factor before trying solving.

            "keep_unchanged":
                Solve unmodified equation.

            "gather":
                Gather (try to find a commun denominator), but not factorize.

            "Factor":
                Factorize, but not gather.

        ** Tips **

        To solve equations and systems of equations like recurrence relations
        or differential equations, use rsolve() or dsolve(), respectively.

        ** Examples **

       >>> from sympy import I, solve
       >>> from sympy.abc import x, y

       Solve a polynomial equation:

       >>> solve(x**4-1, x)
       [1, -1, -I, I]

       Solve a linear system:

       >>> solve((x+5*y-2, -3*x+6*y-15), x, y)
       {x: -3, y: 1}

    """
    def sympit(w):
        return map(sympify, iff(isinstance(w,(list, tuple, set)), w, [w]))
    # make f and symbols into lists of sympified quantities
    # keeping track of how f was passed since if it is a list
    # a dictionary of results will be returned.
    bare_f = not isinstance(f, (list, tuple, set))
    f, symbols = (sympit(w) for w in [f, symbols])

    for i, fi in enumerate(f):
        if isinstance(fi, Equality):
            f[i] = fi.lhs - fi.rhs

    if not symbols:
        #get symbols from equations or supply dummy symbols since
        #solve(3,x) returns []...though it seems that it should raise some sort of error TODO
        symbols = set()
        for fi in f:
            symbols |= fi.atoms(Symbol) or set([Symbol('x',dummy=True)])
        symbols = list(symbols)

    if bare_f:
        f=f[0]

    if len(symbols) == 1:
        if isinstance(symbols[0], (list, tuple, set)):
            symbols = symbols[0]

    # Begin code handling for Function and Derivative instances
    # Basic idea:  store all the passed symbols in symbols_passed, check to see
    # if any of them are Function or Derivative types, if so, use a dummy
    # symbol in their place, and set symbol_swapped = True so that other parts
    # of the code can be aware of the swap.  Once all swapping is done, the
    # continue on with regular solving as usual, and swap back at the end of
    # the routine, so that whatever was passed in symbols is what is returned.

    symbols_new = []
    symbol_swapped = False
    symbols_passed = list(symbols)

    for i, s in enumerate(symbols):
        if s.is_Symbol:
            s_new = s
        elif s.is_Function:
            symbol_swapped = True
            s_new = Symbol('F%d' % i, dummy=True)
        elif s.is_Derivative:
            symbol_swapped = True
            s_new = Symbol('D%d' % i, dummy=True)
        else:
            raise TypeError('not a Symbol or a Function')
        symbols_new.append(s_new)

        if symbol_swapped:
            swap_back_dict = dict(zip(symbols_new, symbols))
    # End code for handling of Function and Derivative instances

    if not isinstance(f, (tuple, list, set)):

        # Create a swap dictionary for storing the passed symbols to be solved
        # for, so that they may be swapped back.
        if symbol_swapped:
            swap_dict = zip(symbols, symbols_new)
            f = f.subs(swap_dict)
            symbols = symbols_new

        # Any embedded piecewise functions need to be brought out to the
        # top level so that the appropriate strategy gets selected.
        f = piecewise_fold(f)

        if len(symbols) != 1:
            result = {}
            for s in symbols:
                result[s] = list(_solve_one_equation(f, s, **flags))
            # TODO: result is now a set , which is mathematically more satisfying.
            # For now, let's convert it to a list, since all other sympy parts expect it to be a list.
            # We should adapt sympy code elsewhere, and then return result, unconverted, as a set.

        else:
            result = _solve_one_equation(f, symbols[0], **flags)

            # This symbol swap should not be necessary for the single symbol case: if you've
            # solved for the symbol the it will not appear in the solution. Right now, however
            # ode's are getting solutions for solve (even though they shouldn't be -- see the
            # swap_back test in test_solvers).
            if symbol_swapped:
                result = [ri.subs(swap_back_dict) for ri in result]

            result = list(result)
            # TODO: result is now a set , which is mathematically more satisfying.
            # For now, let's convert it to a list, since all other sympy parts expect it to be a list.
            # We should adapt sympy code elsewhere, and then return result, unconverted, as a set.

        return result

    else:
        if not f:
            return {}
        else:
            # Create a swap dictionary for storing the passed symbols to be
            # solved for, so that they may be swapped back.
            if symbol_swapped:
                swap_dict = zip(symbols, symbols_new)
                f = [fi.subs(swap_dict) for fi in f]
                symbols = symbols_new

            polys = []

            for g in f:

                poly = g.as_poly(*symbols)

                if poly is not None:
                    polys.append(poly)
                else:
                    raise NotImplementedError()

            if all(p.is_linear for p in polys):
                n, m = len(f), len(symbols)
                matrix = zeros((n, m + 1))

                for i, poly in enumerate(polys):
                    for monom, coeff in poly.terms():
                        try:
                            j = list(monom).index(1)
                            matrix[i, j] = coeff
                        except ValueError:
                            matrix[i, m] = -coeff

                soln = solve_linear_system(matrix, *symbols, **flags)
            else:
                soln = solve_poly_system(polys)

            # Use swap_dict to ensure we return the same type as what was
            # passed
            if symbol_swapped:
                if isinstance(soln, dict):
                    res = {}
                    for k in soln.keys():
                        res.update({swap_back_dict[k]: soln[k]})
                    return res
                else:
                    return soln
            else:
                return soln

def _solve_one_equation(f, symbol, **flags):
    """Solve f == 0 for symbol and return solutions as a set.

    Any solutions that are definitely not a solution to the equation
    are not reported.

    The strategy is to rationalize the expression and:

    1) if the numerator is a Mul or if the denominator is not 1 then
    treat the numerator as a Mul (i.e. f1*f2...*fn) and add solutions to
    fi == 0 as long as they don't also make the denominator 0;

    2) if the denominator is 1 and the numerator is a Pow then handle that;

    3) if the numerator is anything else, try to determine what strategy is
    best to use to solve it and then use that strategy.

    NOTE: this routine is mainly to be used as a helper to solve since none of
    the preparatory steps are taken; f is assumed to be in a form ready to
    solve.
    """

    result = set()
    hint = flags.get('hint', 'default')

    if flags.get('_solve_one_first', True):
        allhints = ('default', 'best', 'gather_and_factor', 'keep_unchanged', 'gather', 'factor')
        if hint not in allhints:
            raise ValueError("Hint not recognized: " + hint)

        if hint in ('best', 'default'):
            # We try successively all strategies:
            #     - if hint is 'default', we stop at the first successfull attempt and return it
            #     - if hint is 'best', we return the best-shaped of all the solutions sets, ie. the one with the "shortest" solutions
            results = []
            # results will be a list of sets of solutions
            for _hint in allhints:
                if _hint not in ('best', 'default'):
                    flags['hint'] = _hint
                    try:
                        res = _solve_one_equation(f, symbol, **flags)
                        if hint == 'default':
                            return res
                        results.append(res)
                    except NotImplementedError:
                        pass
            if not results:
                raise NotImplementedError, 'unable to find a successfull strategy.'
            # "Best" solution is the solution with the less operations
            return min(results, key=count_ops)

        # This bloc of code should not be executed anymore
        flags['_solve_one_first'] = False

        n, d = f.as_numer_denom()
        # In some cases, results are simplier if we keep f.
        # That's what 'not_gather' hint is for.
        if hint in ('gather', 'gather_and_factor'):
            f = n
    else:
        d = S.One

    if f.is_Add and hint in ('factor', 'gather_and_factor'):
        f = factor(f)

    if f.is_Mul or d != S.One:
        for fi in f.as_Mul():
            sols = _solve_one_equation(fi, symbol, **flags)
            if d == S.One:
                result.update(sols)
            else:
                for s in sols:
                    # By default, checksol() would simplify solution.
                    # To avoid simplifying solution twice (once in checksol(), and once before returning solution),
                    # we simplify it here before testing it with checksol().
                    if flags.get('simplified', False):
                        s = simplify(s)
                    if not checksol(d, symbol, s, **flags):
                        result.add(s)
                    # Solution is already simplified, let's set flag to False.
                    flags['simplified'] = False
        return result

    elif f.is_Pow:
        # A**r == 0 <=> (A == 0 and r > 0)
        exp_positive = f.exp.is_positive
        if exp_positive is None:
            exp_positive = simplify(f.exp).is_positive # is this ever necessary?
        if exp_positive:
            return _solve_one_equation(f.base, symbol, **flags)
        elif exp_positive is False:
            return set()

    # If none of the above, then see what strategy is best
    strategy = guess_solve_strategy(f, symbol, denom_check=False)

    if strategy == GS_POLY:
        poly = f.as_poly(symbol)
        if poly is None:
            raise NotImplementedError("Cannot solve equation " + str(f) + " for "
                + str(symbol))
        # for cubics and quartics, if the flag wasn't set, DON'T do it
        # by default since the results are quite long. Perhaps one could
        # base this decision on a certain critical length of the roots.
        if poly.degree > 2:
            flags['simplified'] = flags.get('simplified', False)
        result = set(roots(poly, cubics=True, quartics=True))

    elif strategy == GS_RATIONAL:
        P, Q = f.as_numer_denom()
        sols = _solve_one_equation(P, symbol, **flags)
        if Q != 1:
            # Check for Q != 0
            for s in sols:
                # To avoid simplifying solution twice (once in checksol(), and once before returning solution),
                # we simplify it here before testing it with checksol().
                if flags.get('simplified', False):
                    s = simplify(s)
                if not checksol(Q, symbol, s, **flags):
                    result.add(s)
                flags['simplified'] = False

    elif strategy == GS_POLY_CV_1:
        if isinstance(f, Add):
            # we must search for a suitable change of variable
            # collect exponents
            exponents_denom = list()
            for arg in f.args:
                if isinstance(arg, Pow):
                    exponents_denom.append(arg.exp.q)
                elif isinstance(arg, Mul):
                    for mul_arg in arg.args:
                        if isinstance(mul_arg, Pow):
                            exponents_denom.append(mul_arg.exp.q)
            assert len(exponents_denom) > 0
            if len(exponents_denom) == 1:
                m = exponents_denom[0]
            else:
                # get the LCM of the denominators
                m = reduce(ilcm, exponents_denom)
            # x -> y**m.
            # we assume positive for simplification purposes
            t = Symbol('t', positive=True, dummy=True)
            f_ = f.subs(symbol, t**m)
            if guess_solve_strategy(f_, t) != GS_POLY:
                raise NotImplementedError("Could not convert to a polynomial equation: %s" % f_)
            cv_sols = _solve_one_equation(f_, t)
            for s in cv_sols:
                # We might have introduced unwanted solutions,
                # so we test solutions. cf. Issue 1387
                # Note that when checksol() can not conclude (returns None),
                # we keep the potential solution.
                sol_m = s**m
                # To avoid simplifying solution twice (once in checksol(), and once before returning solution),
                # we simplify it here before testing it with checksol().
                if flags.get('simplified', False):
                    sol_m = simplify(sol_m)
                if checksol(f, symbol, sol_m, **flags) is not False: # True or None
                    result.add(sol_m)
                flags['simplified'] = False

        elif isinstance(f, Mul):
            for mul_arg in f.args:
                result.extend(solve(mul_arg, symbol))

    elif strategy == GS_POLY_CV_2:
        m = 0
        if isinstance(f, Add):
            for arg in f.args:
                if isinstance(arg, Pow):
                    m = min(m, arg.exp)
                elif isinstance(arg, Mul):
                    for mul_arg in arg.args:
                        if isinstance(mul_arg, Pow):
                            m = min(m, mul_arg.exp)
        elif isinstance(f, Mul):
            for mul_arg in f.args:
                if isinstance(mul_arg, Pow):
                    m = min(m, mul_arg.exp)
        f1 = simplify(f*symbol**(-m))
        result = _solve_one_equation(f1, symbol)
        # We might have introduced unwanted solutions
        # when expression was multiplied by x**-m
        # so we test if zero is really a solution
        if 0 in result and checksol(f, symbol, 0, **flags) is False: # not True nor None
            result.discard(0)
        #TODO: 0 may be present in a unsimplified form in some cases.
        #In that case, '0 in result' and 'result.remove(0)' would fail.
        # (cf. roots of solve(x**2 + x + sin(y)**2 + cos(y)**2 - 1, x) for example).


    elif strategy == GS_PIECEWISE:
        for expr, cond in f.args:
            candidates = _solve_one_equation(expr, symbol, **flags)
            if isinstance(cond, bool) or cond.is_Number:
                if not cond:
                    continue

                # Only include solutions that do not match the condition
                # of any of the other pieces.
                for candidate in candidates:
                    matches_other_piece = False
                    for other_expr, other_cond in f.args:
                        if isinstance(other_cond, bool) \
                           or other_cond.is_Number:
                            continue
                        if bool(other_cond.subs(symbol, candidate)):
                            matches_other_piece = True
                            break
                    if not matches_other_piece:
                        result.add(candidate)
            else:
                for candidate in candidates:
                    if bool(cond.subs(symbol, candidate)):
                        result.add(candidate)

    elif strategy == GS_TRANSCENDENTAL:
        #a, b = f.as_numer_denom()
        # Let's throw away the denominator for now. When we have robust
        # assumptions, it should be checked, that for the solution,
        # b!=0.
        result = set(tsolve(f, symbol))
        # TODO: tsolve() should return a set instead of a list.
    elif strategy == -1:
        raise ValueError('Could not parse expression %s' % f)
    else:
        raise NotImplementedError("No algorithms are implemented to solve equation %s" % f)

    if flags.get('simplified', True):
        result = set(map(simplify, result))

    assert isinstance(result, set)
    return result

def solve_linear_system(system, *symbols, **flags):
    """Solve system of N linear equations with M variables, which means
       both Cramer and over defined systems are supported. The possible
       number of solutions is zero, one or infinite. Respectively this
       procedure will return None or dictionary with solutions. In the
       case of over defined system all arbitrary parameters are skipped.
       This may cause situation in with empty dictionary is returned.
       In this case it means all symbols can be assigned arbitrary values.

       Input to this functions is a Nx(M+1) matrix, which means it has
       to be in augmented form. If you are unhappy with such setting
       use 'solve' method instead, where you can input equations
       explicitly. And don't worry about the matrix, this function
       is persistent and will make a local copy of it.

       The algorithm used here is fraction free Gaussian elimination,
       which results, after elimination, in upper-triangular matrix.
       Then solutions are found using back-substitution. This approach
       is more efficient and compact than the Gauss-Jordan method.

       >>> from sympy import Matrix, solve_linear_system
       >>> from sympy.abc import x, y

       Solve the following system:

              x + 4 y ==  2
           -2 x +   y == 14

       >>> system = Matrix(( (1, 4, 2), (-2, 1, 14)))
       >>> solve_linear_system(system, x, y)
       {x: -6, y: 2}

    """
    matrix = system[:,:]
    syms = list(symbols)

    i, m = 0, matrix.cols-1  # don't count augmentation

    while i < matrix.rows:
        if i == m:
            # an overdetermined system
            if any(matrix[i:,m]):
                return None   # no solutions
            else:
                # remove trailing rows
                matrix = matrix[:i,:]
                break

        if not matrix[i, i]:
            # there is no pivot in current column
            # so try to find one in other columns
            for k in xrange(i+1, m):
                if matrix[i, k]:
                    break
            else:
                if matrix[i, m]:
                    return None   # no solutions
                else:
                    # zero row or was a linear combination of
                    # other rows so now we can safely skip it
                    matrix.row_del(i)
                    continue

            # we want to change the order of colums so
            # the order of variables must also change
            syms[i], syms[k] = syms[k], syms[i]
            matrix.col_swap(i, k)

        pivot_inv = S.One / matrix [i, i]

        # divide all elements in the current row by the pivot
        matrix.row(i, lambda x, _: x * pivot_inv)

        for k in xrange(i+1, matrix.rows):
            if matrix[k, i]:
                coeff = matrix[k, i]

                # subtract from the current row the row containing
                # pivot and multiplied by extracted coefficient
                matrix.row(k, lambda x, j: simplify(x - matrix[i, j]*coeff))

        i += 1

    # if there weren't any problems, augmented matrix is now
    # in row-echelon form so we can check how many solutions
    # there are and extract them using back substitution

    simplified = flags.get('simplified', True)

    if len(syms) == matrix.rows:
        # this system is Cramer equivalent so there is
        # exactly one solution to this system of equations
        k, solutions = i-1, {}

        while k >= 0:
            content = matrix[k, m]

            # run back-substitution for variables
            for j in xrange(k+1, m):
                content -= matrix[k, j]*solutions[syms[j]]

            if simplified:
                solutions[syms[k]] = simplify(content)
            else:
                solutions[syms[k]] = content

            k -= 1

        return solutions
    elif len(syms) > matrix.rows:
        # this system will have infinite number of solutions
        # dependent on exactly len(syms) - i parameters
        k, solutions = i-1, {}

        while k >= 0:
            content = matrix[k, m]

            # run back-substitution for variables
            for j in xrange(k+1, i):
                content -= matrix[k, j]*solutions[syms[j]]

            # run back-substitution for parameters
            for j in xrange(i, m):
                content -= matrix[k, j]*syms[j]

            if simplified:
                solutions[syms[k]] = simplify(content)
            else:
                solutions[syms[k]] = content

            k -= 1

        return solutions
    else:
        return None   # no solutions

def solve_undetermined_coeffs(equ, coeffs, sym, **flags):
    """Solve equation of a type p(x; a_1, ..., a_k) == q(x) where both
       p, q are univariate polynomials and f depends on k parameters.
       The result of this functions is a dictionary with symbolic
       values of those parameters with respect to coefficients in q.

       This functions accepts both Equations class instances and ordinary
       SymPy expressions. Specification of parameters and variable is
       obligatory for efficiency and simplicity reason.

       >>> from sympy import Eq
       >>> from sympy.abc import a, b, c, x
       >>> from sympy.solvers import solve_undetermined_coeffs

       >>> solve_undetermined_coeffs(Eq(2*a*x + a+b, x), [a, b], x)
       {a: 1/2, b: -1/2}

       >>> solve_undetermined_coeffs(Eq(a*c*x + a+b, x), [a, b], x)
       {a: 1/c, b: -1/c}

    """
    if isinstance(equ, Equality):
        # got equation, so move all the
        # terms to the left hand side
        equ = equ.lhs - equ.rhs

    system = collect(equ.expand(), sym, evaluate=False).values()

    if not any([ equ.has(sym) for equ in system ]):
        # consecutive powers in the input expressions have
        # been successfully collected, so solve remaining
        # system using Gaussian elimination algorithm
        return solve(system, *coeffs, **flags)
    else:
        return None # no solutions

def solve_linear_system_LU(matrix, syms):
    """ LU function works for invertible only """
    assert matrix.rows == matrix.cols-1
    A = matrix[:matrix.rows,:matrix.rows]
    b = matrix[:,matrix.cols-1:]
    soln = A.LUsolve(b)
    solutions = {}
    for i in range(soln.rows):
        solutions[syms[i]] = soln[i,0]
    return solutions

x = Symbol('x', dummy=True)
a,b,c,d,e,f,g,h = [Wild(t, exclude=[x]) for t in 'abcdefgh']
patterns = None

def _generate_patterns():
    """
    Generates patterns for transcendental equations.

    This is lazily calculated (called) in the tsolve() function and stored in
    the patterns global variable.
    """

    tmp1 = f ** (h-(c*g/b))
    tmp2 = (-e*tmp1/a)**(1/d)
    global patterns
    patterns = [
        (a*(b*x+c)**d + e   , ((-(e/a))**(1/d)-c)/b),
        (    b+c*exp(d*x+e) , (log(-b/c)-e)/d),
        (a*x+b+c*exp(d*x+e) , -b/a-LambertW(c*d*exp(e-b*d/a)/a)/d),
        (    b+c*f**(d*x+e) , (log(-b/c)-e*log(f))/d/log(f)),
        (a*x+b+c*f**(d*x+e) , -b/a-LambertW(c*d*f**(e-b*d/a)*log(f)/a)/d/log(f)),
        (    b+c*log(d*x+e) , (exp(-b/c)-e)/d),
        (a*x+b+c*log(d*x+e) , -e/d+c/a*LambertW(a/c/d*exp(-b/c+a*e/c/d))),
        (a*(b*x+c)**d + e*f**(g*x+h) , -c/b-d*LambertW(-tmp2*g*log(f)/b/d)/g/log(f))
    ]

def powdenest(f):
    """
    Denests an expression that contains powers of powers.

    >>> from sympy.solvers.solvers import powdenest
    >>> from sympy.abc import x
    >>> powdenest(7 + (3**x)**5)
    7 + 3**(5*x)
    """
    if f.is_Pow:
        if f.base.is_Pow:
            return powdenest(f.base.base**(f.base.exp*f.exp))
    elif f.is_Add or f.is_Mul:
        return f.func(*(powdenest(arg) for arg in f.args))
    return f

def tsolve(eq, sym):
    """
    Solves a transcendental equation with respect to the given
    symbol. Various equations containing mixed linear terms, powers,
    and logarithms, can be solved.

    Only a single solution is returned. This solution is generally
    not unique. In some cases, a complex solution may be returned
    even though a real solution exists.

        >>> from sympy import tsolve, log
        >>> from sympy.abc import x

        >>> tsolve(3**(2*x+5)-4, x)
        [(-5*log(3) + log(4))/(2*log(3))]

        >>> tsolve(log(x) + 2*x, x)
        [LambertW(2)/2]

    """
    if patterns is None:
        _generate_patterns()
    if isinstance(eq, Equality):
        eq = eq.lhs - eq.rhs
    eq = powdenest(sympify(eq))
    sym = sympify(sym)
    eq2 = eq.subs(sym, x)
    # First see if the equation has a linear factor
    # In that case, the other factor can contain x in any way (as long as it
    # is finite), and we have a direct solution to which we add others that
    # may be found for the remaining portion.
    r = Wild('r')
    m = eq2.match((a*x+b)*r)
    if m and m[a]:
        return [(-b/a).subs(m).subs(x, sym)] + solve(m[r], x)
    for p, sol in patterns:
        m = eq2.match(p)
        if m:
            return [sol.subs(m).subs(x, sym)]

    # let's also try to inverse the equation
    lhs = eq
    rhs = S.Zero

    while True:
        indep, dep = lhs.as_independent(sym)

        # dep + indep == rhs
        if lhs.is_Add:
            # this indicates we have done it all
            if indep is S.Zero:
                break

            lhs = dep
            rhs-= indep

        # dep * indep == rhs
        else:
            # this indicates we have done it all
            if indep is S.One:
                break

            lhs = dep
            rhs/= indep

    #                    -1
    # f(x) = g  ->  x = f  (g)
    if lhs.is_Function and lhs.nargs==1 and hasattr(lhs, 'inverse'):
        rhs = lhs.inverse() (rhs)
        lhs = lhs.args[0]

        sol = solve(lhs - rhs, sym)
        return sol

    elif lhs.is_Add:
        # just a simple case - we do variable substitution for first function,
        # and if it removes all functions - let's call solve.
        #      x    -x                   -1
        # UC: e  + e   = y      ->  t + t   = y
        t = Symbol('t', dummy=True)
        terms = lhs.args

        # find first term which is Function
        for f1 in lhs.args:
            if f1.is_Function:
                break
        else:
            raise NotImplementedError("Unable to solve the equation" + \
                "(tsolve: at least one Function expected at this point")

        # perform the substitution
        lhs_ = lhs.subs(f1, t)

        # if no Functions left, we can proceed with usual solve
        if not (lhs_.is_Function or
                any(term.is_Function for term in lhs_.args)):
            cv_sols = solve(lhs_ - rhs, t)
            for sol in cv_sols:
                if sol.has(sym):
                    raise NotImplementedError("Unable to solve the equation")
            cv_inv = solve(t - f1, sym)[0]
            sols = list()
            for sol in cv_sols:
                sols.append(cv_inv.subs(t, sol))
            return sols


    raise NotImplementedError("Unable to solve the equation.")

def msolve(*args, **kwargs):
    """
    Compatibility wrapper pointing to nsolve().

    msolve() has been renamed to nsolve(), please use nsolve() directly."""
    warn('msolve() is has been renamed, please use nsolve() instead',
         DeprecationWarning)
    args[0], args[1] = args[1], args[0]
    return nsolve(*args, **kwargs)

# TODO: option for calculating J numerically
def nsolve(*args, **kwargs):
    """
    Solve a nonlinear equation system numerically.

    nsolve(f, [args,] x0, modules=['mpmath'], **kwargs)

    f is a vector function of symbolic expressions representing the system.
    args are the variables. If there is only one variable, this argument can be
    omitted.
    x0 is a starting vector close to a solution.

    Use the modules keyword to specify which modules should be used to evaluate
    the function and the Jacobian matrix. Make sure to use a module that
    supports matrices. For more information on the syntax, please see the
    docstring of lambdify.

    Overdetermined systems are supported.

    >>> from sympy import Symbol, nsolve
    >>> import sympy
    >>> sympy.mpmath.mp.dps = 15
    >>> x1 = Symbol('x1')
    >>> x2 = Symbol('x2')
    >>> f1 = 3 * x1**2 - 2 * x2**2 - 1
    >>> f2 = x1**2 - 2 * x1 + x2**2 + 2 * x2 - 8
    >>> print nsolve((f1, f2), (x1, x2), (-1, 1))
    [-1.19287309935246]
    [ 1.27844411169911]

    For one-dimensional functions the syntax is simplified:

    >>> from sympy import sin, nsolve
    >>> from sympy.abc import x
    >>> nsolve(sin(x), x, 2)
    3.14159265358979
    >>> nsolve(sin(x), 2)
    3.14159265358979

    mpmath.findroot is used, you can find there more extensive documentation,
    especially concerning keyword parameters and available solvers.
    """
    # interpret arguments
    if len(args) == 3:
        f = args[0]
        fargs = args[1]
        x0 = args[2]
    elif len(args) == 2:
        f = args[0]
        fargs = None
        x0 = args[1]
    elif len(args) < 2:
        raise TypeError('nsolve expected at least 2 arguments, got %i'
                        % len(args))
    else:
        raise TypeError('nsolve expected at most 3 arguments, got %i'
                        % len(args))
    modules = kwargs.get('modules', ['mpmath'])
    if isinstance(f,  (list,  tuple)):
        f = Matrix(f).T
    if not isinstance(f, Matrix):
        # assume it's a sympy expression
        if isinstance(f, Equality):
            f = f.lhs - f.rhs
        f = f.evalf()
        atoms = f.atoms(Symbol)
        if fargs is None:
            fargs = atoms.copy().pop()
        if not (len(atoms) == 1 and (fargs in atoms or fargs[0] in atoms)):
            raise ValueError('expected a one-dimensional and numerical function')

        # the function is much better behaved if there is no denominator
        f = f.as_numer_denom()[0]

        f = lambdify(fargs, f, modules)
        return findroot(f, x0, **kwargs)
    if len(fargs) > f.cols:
        raise NotImplementedError('need at least as many equations as variables')
    verbose = kwargs.get('verbose', False)
    if verbose:
        print 'f(x):'
        print f
    # derive Jacobian
    J = f.jacobian(fargs)
    if verbose:
        print 'J(x):'
        print J
    # create functions
    f = lambdify(fargs, f.T, modules)
    J = lambdify(fargs, J, modules)
    # solve the system numerically
    x = findroot(f, x0, J=J, **kwargs)
    return x

