from sympy import symbols, sin, exp, cos, Derivative, Integral, Basic, \
                  count_ops, S

x, y, z = symbols('xyz')

def test_count_ops_non_visual():
    assert x.count_ops(visual=False) == 0
    assert y.count_ops(visual=False) == 0
    assert Derivative(x, x).count_ops(visual=False) == 2
    assert (Integral(x, x) + 2*x/(1 + x)).count_ops(visual=False) == 7
    assert Basic().count_ops(visual=False) == 0
    assert (x + 1).count_ops(visual=False) == 1
    assert (y + x + 1).count_ops(visual=False) == 2
    assert (z + y + x + 1).count_ops(visual=False) == 3
    assert (2*z + y + x + 1).count_ops(visual=False) == 4
    assert (2*z + y**17 + x + 1).count_ops(visual=False) == 5
    assert (2*z + y**17 + x + sin(x)).count_ops(visual=False) == 6
    assert (2*z + y**17 + x + sin(x**2)).count_ops(visual=False) == 7
    assert (2*z + y**17 + x + sin(x**2) + exp(cos(x))).count_ops(visual=False) == 10
    assert count_ops({x + 1: sin(x)}) == 2
    assert count_ops([x + 1, sin(x) + y]) == 3

def test_count_ops_visual():
    ADD, MUL, POW, SIN, COS = symbols('ADD MUL POW SIN COS')
    def count(val):
        return count_ops(val, visual=True)
    assert count(x) is S.Zero
    assert count(7) is S.Zero
    assert count(x + y) == ADD
    assert count(1 + x**y) == ADD + POW
    assert count(1 + x**y + 2*x*y + y**2) == 3*ADD + 2*POW + 2*MUL
    assert count({x + 1: sin(x), y: cos(x) + 1}) == SIN + COS + 2*ADD
    assert count({}) is S.Zero
    assert count([x + 1, sin(x)*y]) == SIN + ADD + MUL
    assert count([]) is S.Zero
