# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

import re
from os import walk, listdir
from os.path import isfile, join

from pytest import XFAIL

from tools.testlib import WXGEODIR
from wxgeometrie.geolib import G, objet

def lister_classes():
    classes = set(key.rsplit(".")[-1] for key, value in G.__dict__.iteritems()
                  if type(value) is type and issubclass(value, G.Objet)
                                                  and not key.endswith("_generique")
                  )
    classes_de_base = set(key.rsplit(".")[-1] for key, value in objet.__dict__.iteritems()
                          if type(value) is type and issubclass(value, G.Objet)
                          )
    classes.difference_update(classes_de_base)
    return classes


def test_toutes_classes():
    u"On vérifie que toutes les classes de geolib soient bien testées."
    classes = lister_classes()
    classes_testees = set()
    path = join(WXGEODIR, 'geolib', 'tests')
    for name in listdir(path):
        if name.endswith('.py'):
            with open(join(path, name)) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('def test_'):
                        classes_testees.add(line[9:-3])
    assert 'Carre' in classes_testees, str(classes_testees)

    #TODO: tester ces classes restantes.
    skip_test = set(['Texte_translation', 'Tangente_courbe', 'Texte_rotation', 'Extremite', 'Point_tangence', 'NuageFonction', 'Mul', 'Cube', 'Cote', 'Sommet_triangle_isocele', 'Axe', 'Courbe', 'Sommet', 'Glisseur_vecteur', 'Add', 'Arete', 'Variable', 'Texte_homothetie', 'Label_vecteur', 'Sommet_polyedre', 'Sommet_rectangle', 'Nuage', 'Point_pondere', 'Sommet_triangle_rectangle', 'PrevisualisationPolygone', 'Texte_reflexion', 'Point_droite', 'Sommet_cube', 'Tetraedre'])

    non_testees = classes.difference(classes_testees, skip_test)
    if non_testees:
        print("\n" + 58*"-" + u"\nErreur: Certaines classes de `geolib` ne sont pas testées")
        print('    * ' + '\n    * '.join(non_testees) + "\n" + 58*"-" + "\n")
    assert not non_testees

    a_maj = skip_test.intersection(classes_testees)
    if a_maj:
        print("\n" + 47*"-" + u"\nErreur: `skip_test` n'est pas à jour.")
        print(u'Ces classes sont désormais testées:')
        print('    * ' + '\n    * '.join(a_maj) + "\n" + 47*"-" + "\n")
    assert not a_maj

    a_suppr = skip_test.difference(classes)
    if a_suppr:
        print("\n" + 47*"-" + u"\nErreur: `skip_test` n'est pas à jour.")
        print(u"Ces classes n'existent plus:")
        print('    * ' + '\n    * '.join(a_suppr) + "\n" + 47*"-" + "\n")
    assert not a_suppr


def assert_heritage(classe, classe_parente):
    test = issubclass(classe, classe_parente)
    if not test:
        raise TypeError, "ERREUR: la classe %s N'herite PAS de %s" %(classe, classe_parente)

def assert_not_heritage(classe, classe_parente):
    test = issubclass(classe, classe_parente)
    if test:
        raise TypeError, "ERREUR: la classe %s herite de %s" %(classe, classe_parente)


def test_heritages():
    u"""On vérifie que les objets ont une méthode '_get_coordonnees' ssi ils descendent de la classe 'Objet_avec_coordonnees'.

    De même, les objets ont une méthode '_get_equation' et '_get_val' ssi ils descendent respectivement des classes
    'Objet_avec_equation' et 'Objet_avec_valeur'."""

    for classe in  G.__dict__.itervalues():
        if isinstance(classe, type) and issubclass(classe, G.Objet):
#            print classe
            if hasattr(classe, "_get_equation"):
                assert_heritage(classe, G.Objet_avec_equation)
#                 assert("exact" in classe._get_equation.func_code.co_varnames)
            else:
                assert_not_heritage(classe, G.Objet_avec_equation)
            if hasattr(classe, "_get_coordonnees"):
                assert_heritage(classe, G.Objet_avec_coordonnees)
#                 assert("exact" in classe._get_coordonnees.func_code.co_varnames)
            else:
                assert_not_heritage(classe, G.Objet_avec_coordonnees)
            if hasattr(classe, "_get_valeur"):
                assert_heritage(classe, G.Objet_avec_valeur)
#                 assert("exact" in classe._get_valeur.func_code.co_varnames)
            else:
                assert_not_heritage(classe, G.Objet_avec_valeur)

@XFAIL
def test_methode_image_par():
    classes = lister_classes()
    non_transformable = (G.Variable, G.Label_generique, G.Angle_libre, G.Angle_vectoriel, G.Point_pondere, G.Vecteur_libre, G.Vecteur_unitaire, G.Somme_vecteurs, G.Transformation_generique)
    non_transformable_actuellement = (G.Widget, G.Courbe, G.Interpolation_generique, G.Fonction, G.Texte)
    for classe in G.__dict__.itervalues():
        if (isinstance(classe, type) and issubclass(classe, G.Objet)
                and classe.__name__.rsplit(".")[-1] in classes
                and not hasattr(classe, "image_par")):
            if not issubclass(classe, non_transformable) and not issubclass(classe, non_transformable_actuellement):
                raise AttributeError, "ATTENTION: " + str(classe) + " n'a pas d'attribut 'image_par' !"



def test_arguments():
    u"""On vérifie que l'attribut '.nom' des arguments correspondent bien à leur noms réels.

    Le nom doit être de la forme '_nomClasse__nomArgument'."""

    for classe in G.__dict__.itervalues():
        if isinstance(classe, type) and issubclass(classe, G.Objet):
            for key, value in vars(classe).iteritems():
                if isinstance(value, G.BaseArgument) and key[0] == "_":
                    assert(key == value.nom)

@XFAIL
def test_imports():
    u"""Vérifie qu'il n'existe pas d'imports relatifs implicites."""
    # On liste les modules locaux
    locaux = set()
    def test(line):
        assert not re.search('(from|import) (' + '|'.join(locaux) + ')[. ]', line)

    for root, dirs, files in walk(WXGEODIR):
        if 'sympy' in dirs:
            dirs.remove('sympy')
        if 'sympy_OLD' in dirs:
            dirs.remove('sympy_OLD')
        for name in files:
            if name.endswith('.py'):
                locaux.add(name[:-3])
        for name in dirs:
            if isfile(join(root, name, '__init__.py')):
                locaux.add(name)
    assert 'sympy' not in locaux and 'trigonometry' not in locaux
    # on teste les imports
    for root, dirs, files in walk(WXGEODIR):
        for name in files:
            if name.endswith('.py'):
                with open(join(root, name)) as f:
                    for n, line in enumerate(f):
                        if 'from ' in line or 'import ' in line:
                            assert test(line), join(root, name) + ' L' + str(n + 1)



#def test_presence_methodes():
#    attributs_ou_methodes_obligatoires = [
#                             ]
#    for classe in G.__dict__.itervalues():
#        if isinstance(classe, type) and issubclass(classe, G.Objet):
#            for attr in attributs_ou_methodes_obligatoires:
#                if not hasattr(classe, attr):
#                    print u"ERREUR: La classe %s doit posséder l'attribut ou la méthode '%s' !" %(classe, attr)
#                    assert(hasattr(classe, attr))
