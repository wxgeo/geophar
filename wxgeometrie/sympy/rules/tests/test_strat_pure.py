from sympy.rules.strat_pure import (null_safe, exhaust, memoize, condition,
        chain, tryit, do_one, debug, switch)

def test_null_safe():
    def rl(expr):
        if expr == 1:
            return 2
    safe_rl = null_safe(rl)
    assert rl(1) == safe_rl(1)

    assert      rl(3) == None
    assert safe_rl(3) == 3

def posdec(x):
    if x > 0:
        return x-1
    else:
        return x
def test_exhaust():
    sink = exhaust(posdec)
    assert sink(5) == 0
    assert sink(10) == 0

def test_memoize():
    rl = memoize(posdec)
    assert rl(5) == posdec(5)
    assert rl(5) == posdec(5)
    assert rl(-2) == posdec(-2)

def test_condition():
    rl = condition(lambda x: x%2 == 0, posdec)
    assert rl(5) == 5
    assert rl(4) == 3

def test_chain():
    rl = chain(posdec, posdec)
    assert rl(5) == 3
    assert rl(1) == 0

def test_tryit():
    def rl(expr):
        assert False
    safe_rl = tryit(rl)
    assert safe_rl(1) == 1

def test_do_one():
    rl = do_one(posdec, posdec)
    assert rl(5) == 4

def test_debug():
    import StringIO
    file = StringIO.StringIO()
    rl = debug(posdec, file)
    rl(5)
    log = file.getvalue()
    file.close()

    assert posdec.func_name in log
    assert '5' in log
    assert '4' in log

def test_switch():
    inc = lambda x: x + 1
    dec = lambda x: x - 1
    key = lambda x: x % 3
    rl = switch(key, {0: inc, 1: dec})

    assert rl(3) == 4
    assert rl(4) == 3
    assert rl(5) == 5
