#!/usr/bin/env python3
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
import glob
from scriptlib import command



for filename in glob.iglob('**/*.py', recursive=True):
    if '/sympy/' in filename or filename.startswith('sympy/') or filename.endswith("/conv2to3.py"):
        continue
    output = command('2to3 %s' % filename)
    print(80*'-')
    if "RefactoringTool: No files need to be modified." in output:
        continue
    command('2to3 -w %s' % filename)
    command('meld %s.bak %s' % (filename, filename))





