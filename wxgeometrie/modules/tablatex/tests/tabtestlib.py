# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

def assert_tableau(func, chaine, code_latex):
    code = func(chaine)
    if code != code_latex:
        print "-------"
        print "ERREUR:"
        print "Actually result is:"
        print code
        print "While expected output was:"
        print code_latex
        for i, car in enumerate(code):
            if i >= len(code_latex):
                print 'Output too long:'
                print code[i:]
                break
            elif code_latex[i] != car:
                print 'Difference:'
                print 'char number:', i
                print 'result:', repr(code[i:i+10])
                print 'expected:', repr(code_latex[i:i+10])
                break
        print "-------"
    assert (code == code_latex)
