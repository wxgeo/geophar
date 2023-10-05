# -*- coding: utf-8 -*-

import os, sys
import chardet

TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
sys.path.insert(0, TOPDIR)

WXGEODIR = os.path.join(TOPDIR, "wxgeometrie")

START = "# -*- coding: utf-8 -*-"

EXCLURE = {
    'dirs': [
        'sympy', 'sympy_OLD', 'developpeurs', 'doc', 'exemples',
        'images', 'log', 'preferences', 'session', 'macros', 'OLD',
        'tests',
    ],
    'files': [
        'test.py', '__init__.py', 'decorator.py',
    ]
           }

CODECS = ('utf-8', 'utf8', 'ascii')

def verifier(fichier):
    """
    Vérification de l'encodage d'un fichier et sa déclaration explicite
    @param fichier un chemin
    @return un doublon : nom du fichier et message, ou None si tout va bien
    """
    # On vérifie qu'il est réellement en utf-8 (ou en ascii)
    encoding = None
    with open(fichier, 'rb') as f:
        encoding = chardet.detect(f.read()).get("encoding")
    if encoding not in CODECS:
        return fichier, f"Le codage « {encoding} » ne figure pas dans {CODECS}"
    # On vérifie que le fichier est bien déclaré en utf-8
    with open(fichier, 'r') as f:
        lines = f.readlines()
        if not lines[0].startswith(START) and not lines[0].startswith(START):
            return fichier, "Il manque : " + START
    return None

def skip(path):
    for directory in EXCLURE['dirs']:
        if ('/%s/' % directory) in path or path.endswith('/' + directory):
            return True
    return False

import tools.unittest, unittest

class Test(tools.unittest.TestCase):

    def test_entetes(self):
        "On teste que les fichiers soient bien tous declarés en utf-8."
        bad_files = {}
        for root, dirs, files in os.walk(WXGEODIR):
            if not skip(root):
                for filename in files:
                    if filename.endswith('.py') and \
                       filename not in EXCLURE['files']:
                        verif = verifier(os.path.join(root, filename))
                        if verif is not None:
                            bad_files[verif[0]] = verif[1]
        if bad_files:
            print('\n\nEn-tête ou encodage incorrect : ')
            for fichier in bad_files:
                print(f'* {fichier} : {bad_files[fichier]}')
        self.assertFalse(bad_files)
