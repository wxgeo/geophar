# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from geolib.tests.geotestlib import *
import geolib.objet as objet
import geolib.ALL as ALL

def lister_classes():
    classes = set(key.rsplit(".")[-1] for key, value in ALL.__dict__.iteritems() if type(value) == type(ALL.Objet) and issubclass(value, ALL.Objet) and not key.endswith("_generique"))
    classes_de_base = set(key.rsplit(".")[-1] for key, value in objet.__dict__.iteritems() if type(value) == type(ALL.Objet) and issubclass(value, ALL.Objet))
    classes.difference_update(classes_de_base)
    return classes

classes = lister_classes()

# TODO: à réécrire
@XFAIL
def test_toutes_classes():
    u"On vérifie que toutes les classes de geolib soient bien testées."
    classes = set(classes)
    classes_testees = set()
    for key, value in tests_unitaires.__dict__.iteritems():
        if type(value) == type(tests_unitaires.CustomTest) and issubclass(value, tests_unitaires.CustomTest):
            for nom in value.__dict__.keys():
                if nom.startswith("test_"):
                    classes_testees.add(nom[5:])


    classes.difference_update(classes_testees)

    classes.remove("Variable")

    if len(classes):
        print u"Certaines classes ne sont pas testées :"
        print classes

    classes.difference_update(set(['Widget', 'PointTangence', 'Bouton', 'Extremite', 'Cote', 'Sommet', 'Point_droite', 'Point_pondere', 'Champ', 'PrevisualisationPolygone','Variable_en_travaux']))
    # 'Variable_en_travaux' à enlever

    assert(len(classes) == 0)

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

    for classe in  ALL.__dict__.itervalues():
        if isinstance(classe, type) and issubclass(classe, ALL.Objet):
#            print classe
            if hasattr(classe, "_get_equation"):
                assert_heritage(classe, ALL.Objet_avec_equation)
#                 assert("exact" in classe._get_equation.func_code.co_varnames)
            else:
                assert_not_heritage(classe, ALL.Objet_avec_equation)
            if hasattr(classe, "_get_coordonnees"):
                assert_heritage(classe, ALL.Objet_avec_coordonnees)
#                 assert("exact" in classe._get_coordonnees.func_code.co_varnames)
            else:
                assert_not_heritage(classe, ALL.Objet_avec_coordonnees)
            if hasattr(classe, "_get_valeur"):
                assert_heritage(classe, ALL.Objet_avec_valeur)
#                 assert("exact" in classe._get_valeur.func_code.co_varnames)
            else:
                assert_not_heritage(classe, ALL.Objet_avec_valeur)

@XFAIL
def test_methode_image_par():
    noms = set(classes)
    non_transformable = (ALL.Variable, ALL.Label_generique, ALL.Angle_libre, ALL.Angle_vectoriel, ALL.Point_pondere, ALL.Vecteur_libre, ALL.Vecteur_unitaire, ALL.Somme_vecteurs, ALL.Transformation_generique)
    non_transformable_actuellement = (ALL.Widget, ALL.Courbe, ALL.Interpolation_generique, ALL.Fonction, ALL.Texte)
    for classe in ALL.__dict__.itervalues():
        if isinstance(classe, type) and issubclass(classe, ALL.Objet) and classe.__name__.rsplit(".")[-1] in noms and not hasattr(classe, "image_par"):
            if not issubclass(classe, non_transformable) and not issubclass(classe, non_transformable_actuellement):
                raise AttributeError, "ATTENTION: " + str(classe) + " n'a pas d'attribut 'image_par' !"



def test_arguments():
    u"""On vérifie que l'attribut '.nom' des arguments correspondent bien à leur noms réels.

    Le nom doit être de la forme '_nomClasse__nomArgument'."""

    for classe in ALL.__dict__.itervalues():
        if isinstance(classe, type) and issubclass(classe, ALL.Objet):
            for key, value in vars(classe).iteritems():
                if isinstance(value, ALL.BaseArgument) and key[0] == "_":
                    assert(key == value.nom)


#def test_presence_methodes():
#    attributs_ou_methodes_obligatoires = [
#                             ]
#    for classe in ALL.__dict__.itervalues():
#        if isinstance(classe, type) and issubclass(classe, ALL.Objet):
#            for attr in attributs_ou_methodes_obligatoires:
#                if not hasattr(classe, attr):
#                    print u"ERREUR: La classe %s doit posséder l'attribut ou la méthode '%s' !" %(classe, attr)
#                    assert(hasattr(classe, attr))
