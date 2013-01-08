"""Implicit plotting module for SymPy

The module implements a data series called ImplicitSeries which is used by
``Plot`` class to plot implicit plots for different backends. The module,
by default, implements plotting using interval arithmetic. It switches to a
fall back algorithm if the expression cannot be plotted used interval
interval arithmetic. It is also possible to specify to use the fall back
algorithm for all plots.

Boolean combinations of expressions cannot be plotted by the fall back
algorithm.

See Also
========
sympy.plotting.plot

References
==========
- Jeffrey Allen Tupper. Reliable Two-Dimensional Graphing Methods for
Mathematical Formulae with Two Free Variables.

- Jeffrey Allen Tupper. Graphing Equations with Generalized Interval
Arithmetic. Master's thesis. University of Toronto, 1996

"""

from plot import BaseSeries, Plot
from experimental_lambdify import experimental_lambdify, vectorized_lambdify
from intervalmath import interval
from sympy.core.relational import (Equality, GreaterThan, LessThan,
                Relational, StrictLessThan, StrictGreaterThan)
from sympy import Eq, Tuple, sympify, Expr, Dummy
from sympy.external import import_module
from sympy.core.compatibility import set_union
from sympy.logic.boolalg import BooleanFunction
import warnings

np = import_module('numpy')


class ImplicitSeries(BaseSeries):
    """ Representation for Implicit plot """
    is_implicit = True

    def __init__(self, expr, var_start_end_x, var_start_end_y,
            has_equality, use_interval_math, depth, nb_of_points):
        super(ImplicitSeries, self).__init__()
        self.expr = sympify(expr)
        self.var_x = sympify(var_start_end_x[0])
        self.start_x = float(var_start_end_x[1])
        self.end_x = float(var_start_end_x[2])
        self.var_y = sympify(var_start_end_y[0])
        self.start_y = float(var_start_end_y[1])
        self.end_y = float(var_start_end_y[2])
        self.get_points = self.get_raster
        self.has_equality = has_equality  # If the expression has equality, i.e.
                                         #Eq, Greaterthan, LessThan.
        self.nb_of_points = nb_of_points
        self.use_interval_math = use_interval_math
        self.depth = 4 + depth

    def __str__(self):
        return ('Implicit equation: %s for '
                '%s over %s and %s over %s') % (
                    str(self.expr),
                    str(self.var_x),
                    str((self.start_x, self.end_x)),
                    str(self.var_y),
                    str((self.start_y, self.end_y)))

    def get_raster(self):
        func = experimental_lambdify((self.var_x, self.var_y), self.expr,
                                    use_interval=True)
        xinterval = interval(self.start_x, self.end_x)
        yinterval = interval(self.start_y, self.end_y)
        try:
            temp = func(xinterval, yinterval)
        except AttributeError:
            if self.use_interval_math:
                warnings.warn("Adaptive meshing could not be applied to the"
                            " expression. Using uniform meshing.")
            self.use_interval_math = False

        if self.use_interval_math:
            return self._get_raster_interval(func)
        else:
            return self._get_meshes_grid()

    def _get_raster_interval(self, func):
        """ Uses interval math to adaptively mesh and obtain the plot"""
        k = self.depth
        interval_list = []
        #Create initial 32 divisions
        xsample = np.linspace(self.start_x, self.end_x, 33)
        ysample = np.linspace(self.start_y, self.end_y, 33)

        #Add a small jitter so that there are no false positives for equality.
        # Ex: y==x becomes True for x interval(1, 2) and y interval(1, 2)
        #which will draw a rectangle.
        jitterx = (np.random.rand(
            len(xsample)) * 2 - 1) * (self.end_x - self.start_x) / 2**20
        jittery = (np.random.rand(
            len(ysample)) * 2 - 1) * (self.end_y - self.start_y) / 2**20
        xsample += jitterx
        ysample += jittery

        xinter = [interval(x1, x2) for x1, x2 in zip(xsample[:-1],
                           xsample[1:])]
        yinter = [interval(y1, y2) for y1, y2 in zip(ysample[:-1],
                           ysample[1:])]
        interval_list = [[x, y] for x in xinter for y in yinter]
        plot_list = []

        #recursive call refinepixels which subdivides the intervals which are
        #neither True nor False according to the expression.
        def refine_pixels(interval_list):
            """ Evaluates the intervals and subdivides the interval if the
            expression is partially satisfied."""
            temp_interval_list = []
            plot_list = []
            for intervals in interval_list:

                #Convert the array indices to x and y values
                intervalx = intervals[0]
                intervaly = intervals[1]
                func_eval = func(intervalx, intervaly)
                #The expression is valid in the interval. Change the contour
                #array values to 1.
                if func_eval[1] is False or func_eval[0] is False:
                    pass
                elif func_eval == (True, True):
                    plot_list.append([intervalx, intervaly])
                elif func_eval[1] is None or func_eval[0] is None:
                    #Subdivide
                    avgx = intervalx.mid
                    avgy = intervaly.mid
                    a = interval(intervalx.start, avgx)
                    b = interval(avgx, intervalx.end)
                    c = interval(intervaly.start, avgy)
                    d = interval(avgy, intervaly.end)
                    temp_interval_list.append([a, c])
                    temp_interval_list.append([a, d])
                    temp_interval_list.append([b, c])
                    temp_interval_list.append([b, d])
            return temp_interval_list, plot_list

        while k >= 0 and len(interval_list):
            interval_list, plot_list_temp = refine_pixels(interval_list)
            plot_list.extend(plot_list_temp)
            k = k - 1
        #Check whether the expression represents an equality
        #If it represents an equality, then none of the intervals
        #would have satisfied the expression due to floating point
        #differences. Add all the undecided values to the plot.
        if self.has_equality:
            for intervals in interval_list:
                intervalx = intervals[0]
                intervaly = intervals[1]
                func_eval = func(intervalx, intervaly)
                if func_eval[1] and func_eval[0] is not False:
                    plot_list.append([intervalx, intervaly])
        return plot_list, 'fill'

    def _get_meshes_grid(self):
        """Generates the mesh for generating a contour.

        In the case of equality, ``contour`` function of matplotlib can
        be used. In other cases, matplotlib's ``contourf`` is used.
        """
        equal = False
        if isinstance(self.expr, Equality):
            expr = self.expr.lhs - self.expr.rhs
            equal = True

        elif isinstance(self.expr, (GreaterThan, StrictGreaterThan)):
            expr = self.expr.lhs - self.expr.rhs

        elif isinstance(self.expr, (LessThan, StrictLessThan)):
            expr = self.expr.rhs - self.expr.lhs
        else:
            raise NotImplementedError("The expression is not supported for"
                                    "plotting in uniform meshed plot.")
        xarray = np.linspace(self.start_x, self.end_x, self.nb_of_points)
        yarray = np.linspace(self.start_y, self.end_y, self.nb_of_points)
        x_grid, y_grid = np.meshgrid(xarray, yarray)

        func = vectorized_lambdify((self.var_x, self.var_y), expr)
        z_grid = func(x_grid, y_grid)
        z_grid[np.ma.where(z_grid < 0)] = -1
        z_grid[np.ma.where(z_grid > 0)] = 1
        if equal:
            return xarray, yarray, z_grid, 'contour'
        else:
            return xarray, yarray, z_grid, 'contourf'


def plot_implicit(expr, *args, **kwargs):
    """A plot function to plot implicit equations / inequalities.

    Arguments
    =========

    - ``expr`` : The equation / inequality that is to be plotted.
    - ``(x, xmin, xmax)`` optional, 3-tuple denoting the range of symbol
      ``x``
    - ``(y, ymin, ymax)`` optional, 3-tuple denoting the range of symbol
      ``y``

    The following arguments can be passed as named parameters.

    - ``adaptive``. Boolean. The default value is set to True. It has to be
        set to False if you want to use a mesh grid.

    - ``depth`` integer. The depth of recursion for adaptive mesh grid.
        Default value is 0. Takes value in the range (0, 4).

    - ``points`` integer. The number of points if adaptive mesh grid is not
        used. Default value is 200.

    - ``title`` string .The title for the plot.

    - ``xlabel`` string. The label for the x - axis

    - ``ylabel`` string. The label for the y - axis

    plot_implicit, by default, uses interval arithmetic to plot functions. If
    the expression cannot be plotted using interval arithmetic, it defaults to
    a generating a contour using a mesh grid of fixed number of points. By
    setting adaptive to False, you can force plot_implicit to use the mesh
    grid. The mesh grid method can be effective when adaptive plotting using
    interval arithmetic, fails to plot with small line width.

    Examples:
    =========

    Plot expressions:

    >>> from sympy import plot_implicit, cos, sin, symbols, Eq
    >>> x, y = symbols('x y')

    Without any ranges for the symbols in the expression

    >>> p1 = plot_implicit(Eq(x**2 + y**2, 5))  # doctest: +SKIP

    With the range for the symbols

    >>> p2 = plot_implicit(Eq(x**2 + y**2, 3),
    ...         (x, -3, 3), (y, -3, 3))  # doctest: +SKIP

    With depth of recursion as argument.

    >>> p3 = plot_implicit(Eq(x**2 + y**2, 5),
    ...         (x, -4, 4), (y, -4, 4), depth = 2)  # doctest: +SKIP

    Using mesh grid and not using adaptive meshing.

    >>> p4 = plot_implicit(Eq(x**2 + y**2, 5),
    ...         (x, -5, 5), (y, -2, 2), adaptive=False)  # doctest: +SKIP

    Using mesh grid with number of points as input.

    >>> p5 = plot_implicit(Eq(x**2 + y**2, 5),
    ...         (x, -5, 5), (y, -2, 2),
    ...         adaptive=False, points=400)  # doctest: +SKIP

    Plotting regions.

    >>> p6 = plot_implicit(y > x**2)  # doctest: +SKIP

    Plotting Using boolean conjunctions.

    >>> p7 = plot_implicit(And(y > x, y > -x))  # doctest: +SKIP
    """
    has_equality = False  # Represents whether the expression contains an Equality,
                     #GreaterThan or LessThan

    def arg_expand(bool_expr):
        """
        Recursively expands the arguments of an Boolean Function
        """
        for arg in bool_expr.args:
            if isinstance(arg, BooleanFunction):
                arg_expand(arg)
            elif isinstance(arg, Relational):
                arg_list.append(arg)

    arg_list = []
    if isinstance(expr, BooleanFunction):
        arg_expand(expr)

    #Check whether there is an equality in the expression provided.
        if any(isinstance(e, (Equality, GreaterThan, LessThan))
               for e in arg_list):
            has_equality = True

    elif not isinstance(expr, Relational):
        expr = Eq(expr, 0)
        has_equality = True
    elif isinstance(expr, (Equality, GreaterThan, LessThan)):
        has_equality = True

    free_symbols = set(expr.free_symbols)
    range_symbols = set([t[0] for t in args])
    symbols = set_union(free_symbols, range_symbols)
    if len(symbols) > 2:
        raise NotImplementedError("Implicit plotting is not implemented for "
                                  "more than 2 variables")

    #Create default ranges if the range is not provided.
    default_range = Tuple(-5, 5)
    if len(args) == 2:
        var_start_end_x = args[0]
        var_start_end_y = args[1]
    elif len(args) == 1:
        if len(free_symbols) == 2:
            var_start_end_x = args[0]
            var_start_end_y, = (Tuple(e) + default_range
                                for e in (free_symbols - range_symbols))
        else:
            var_start_end_x, = (Tuple(e) + default_range for e in free_symbols)
            #Create a random symbol
            var_start_end_y = Tuple(Dummy()) + default_range

    elif len(args) == 0:
        if len(free_symbols) == 1:
            var_start_end_x, = (Tuple(e) + default_range for e in free_symbols)
            #create a random symbol
            var_start_end_y = Tuple(Dummy()) + default_range
        else:
            var_start_end_x, var_start_end_y = (Tuple(e) + default_range
                                                for e in free_symbols)

    use_interval = kwargs.pop('adaptive', True)
    nb_of_points = kwargs.pop('points', 300)
    depth = kwargs.pop('depth', 0)
    #Check whether the depth is greater than 4 or less than 0.
    if depth > 4:
        depth = 4
    elif depth < 0:
        depth = 0

    series_argument = ImplicitSeries(expr, var_start_end_x, var_start_end_y,
                                    has_equality, use_interval, depth,
                                    nb_of_points)
    show = kwargs.pop('show', True)

    #set the x and y limits
    kwargs['xlim'] = tuple(float(x) for x in var_start_end_x[1:])
    kwargs['ylim'] = tuple(float(y) for y in var_start_end_y[1:])
    p = Plot(series_argument, **kwargs)
    if show:
        p.show()
    return p
