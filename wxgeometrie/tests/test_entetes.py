# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os, sys, subprocess

from pytest import XFAIL

_module_path = os.path.split(os.path.realpath(sys._getframe().f_code.co_filename))[0]
WXGEODIR = os.path.abspath(_module_path + '/..')

from tools.testlib import *


#~ START = '''
#~ # -*- coding: utf-8 -*-
#~ from __future__ import division, absolute_import, print_function, unicode_literals
#~ #    WxGeometrie
#~ #    Dynamic geometry, graph plotter, and more for french mathematic teachers.
#~ #    Copyright (C) 2005-2013  Nicolas Pourcelot
#~ '''


START = '''# -*- coding: utf-8 -*-
'''

EXCLURE = {'dirs': ['sympy', 'sympy_OLD', 'developpeurs', 'doc', 'exemples',
                    'images', 'log', 'preferences', 'session', 'macros', 'OLD'],
           'files': ['test.py', '__init__.py']
           }

CODECS = ('utf-8', 'utf8', 'ascii')

def command(string, quiet=True):
    u"Execute command in shell."
    out = subprocess.Popen(string, shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT).stdout
    output = out.read()
    if not quiet:
        sys.stdout.write(output)
    out.close()
    if not quiet:
        print("Commande '%s' executee." % string)
    return output

def verifier(fichier):
    # On vérifie que le fichier est bien déclaré en utf-8
    with open(fichier, 'rU') as f:
        s = f.read(1000)
        pos = (22 if s.startswith('#!/usr/bin/env python') else 0)
        if not s.startswith(START, pos):
            return [fichier]
    # On vérifie qu'il est réellement en utf-8 (ou en ascii)
    mimeinfo = command('file --mime-encoding "%s"' % fichier).strip()
    if not any(mimeinfo.endswith(codec) for codec in CODECS):
        return [fichier]
    return []

def skip(path):
    for directory in EXCLURE['dirs']:
        if ('/%s/' % directory) in path or path.endswith('/' + directory):
            return True
    return False


#@XFAIL
def test_entetes():
    u"On teste que les fichiers soient bien tous declarés en utf-8."
    bad_files = []
    for root, dirs, files in os.walk(WXGEODIR):
        if not skip(root):
            for filename in files:
                if filename.endswith('.py') and filename not in EXCLURE['files']:
                    bad_files.extend(verifier(os.path.join(root, filename)))
    if bad_files:
        print(u'\n\nEn-tête ou encodage incorrect : ')
        for fichier in bad_files:
            print('* ' + fichier)
    assert not bad_files
