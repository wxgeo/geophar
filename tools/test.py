#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
from __future__ import division, absolute_import, print_function, unicode_literals
#    WxGeometrie
#    Dynamic geometry, graph plotter, and more for french mathematic teachers.
#    Copyright (C) 2005-2010  Nicolas Pourcelot
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""Utilitaires et tests à effectuer avant de publier une nouvelle version de WxGéométrie.

    La suite de tests suivante est librement inspirée de Sympy.

    python test.py audit -> will run pyflakes checker on source code
    python test.py bench -> will run the complete benchmark suite
    python test.py clean -> will clean all trash (*.pyc and stuff)
    python test.py test -> will run the complete test suite
"""

import sys, os

#from testlib import ROOTDIR, WXGEODIR

_module_path = os.path.split(os.path.realpath(sys._getframe().f_code.co_filename))[0]
ROOTDIR = os.path.abspath(_module_path + '/..') # /.../nom_du_projet/
WXGEODIR = ROOTDIR + '/wxgeometrie'
SKIP_DIRS = ['sympy/', 'sympy_OLD/', 'sympy_old/', 'pylib/decorator.py', # already tested by sympy team.
            'modules/OLD', 'BAZAR/']

sys.path.insert(0, WXGEODIR)
sys.path.insert(0, ROOTDIR)

print(ROOTDIR)

from wxgeometrie import param

# Make sure I have the right Python version.
if sys.version_info[:2] < param.python_min:
    print("Python %d.%d or newer is required. Python %d.%d detected." % \
          (param.python_min + sys.version_info[:2]))
    sys.exit(-1)


#TODO: use argparse once python 2.6 is deprecated for WxGéométrie.

actions = {'u': 'audit', 'c': 'clean', 't': 'test', 'd': 'doc', 'a': 'all', 'h': 'help'}

args = sys.argv[1:]


def audit():
    """Audit WxGeometrie's source with PyFlakes.

    Audit WxGeometrie source code for following issues:
        - Names which are used but not defined or used before they are defined.
        - Names which are redefined without having been used.
    """
    os.chdir(WXGEODIR)
    try:
        import pyflakes.scripts.pyflakes as flakes
    except ImportError:
        print("""In order to run the audit, you need to have PyFlakes installed.""")
        sys.exit(-1)
    print('\n == Auditing files... ==')
    warns = 0
    for dirpath, dirnames, filenames in os.walk('.'):
        if not any((dirpath.startswith('./' + dir) or dir + '/' == dirpath) for dir in SKIP_DIRS):
            print('\nAuditing ' + dirpath + '...')
            print([('./' + dir, dirpath.startswith('./' + dir)) for dir in SKIP_DIRS])
            for filename in filenames:
                if filename.endswith('.py') and filename != '__init__.py':
                    warns += flakes.checkPath(os.path.join(dirpath, filename))
    if warns > 0:
        print("Audit finished with total %d warnings" % warns)
    else:
        print("Audit finished without any warning. :)")


def clean():
    """Cleans *.pyc and debian trashs."""
    os.chdir(ROOTDIR)
    os.system("py.cleanup --remove=.py~,.bak,.pyc,.txt~")


def test(*args):
    "Run all unit tests."
    os.chdir(ROOTDIR)
    param.debug = False
    param.verbose = False
    from runtests import test
    test(*args, blacklist = SKIP_DIRS)


def doctest(*args):
    "Run all doctests."
    os.chdir(WXGEODIR)
    param.debug = False
    param.verbose = False
    sys.argv = [sys.argv[0], '--defaut']
    from runtests import doctest
    doctest(*args, blacklist = SKIP_DIRS)

doc = doctest

def all(*args):
    "Run all tests and doctests."
    test(*args)
    doctest(*args)


def help():
    print(u"""\n    === Usage ===\n
    - Launch all unit tests:
        $ ./tools/test.py
    - Launch all doctests:
        $ ./tools/test.py --doctest
    - Launch all unit tests and doctests:
        $ ./tools/test.py --all
    - Clear working wxgeometrie directories:
        $ ./tools/test.py --clear
    - Audit code using PyFlakes:
        $ ./tools/test.py --audit

    Note that you may test only a few modules.
    For example:
    - Launch all unit tests concerning geolib:
        $ ./tools/test.py geolib
    - Launch all unit tests contained in geolib/test_objets.py
        $ ./tools/test.py objets
    """)
    sys.exit()

# Actions are launched
if args:
    if args[0].startswith('--'):
        action = args[0][2:]
        args = args[1:]
    elif args[0].startswith('-'):
        act = args[0][1:]
        args = args[1:]
        if act in actions:
            action = actions[act]
        else:
            help()
    else:
        action = 'test'
    if action in actions.itervalues():
        locals()[action](*args)
    else:
        help()
else:
    test()
