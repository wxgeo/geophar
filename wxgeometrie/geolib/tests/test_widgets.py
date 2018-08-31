# -*- coding: utf-8 -*-

from pytest import XFAIL

from tools.testlib import rand
from wxgeometrie.geolib import Champ, Bouton


def test_Champ():
    champ = Champ('', 4, 3, couleur_fond='#ffffb5',
                    prefixe=(r"Combien vaut 1+1 ? "),
                    alignement_horizontal='left', alignement_vertical='bottom',
                    attendu='2')
    points = 0

    def valider(reponse, attendu):
        return reponse.strip() == attendu

    def evt_valider(**kw):
        nonlocal points
        points = (5 if kw['correct'] else 1)

    champ.valider = valider
    champ.evt_valider = evt_valider

    champ.texte = '3'
    assert champ.label() == "Combien vaut 1+1 ? $3$", champ.label()
    assert not champ.correct
    assert points == 1
    champ.texte = '2'
    assert champ.label() == "Combien vaut 1+1 ? $2$"
    assert champ.correct
    assert points == 5
    champ.texte = ' 3 '
    assert not champ.correct
    assert points == 1
    champ.texte = ' 2   '
    assert champ.correct
    assert points == 5

@XFAIL
def test_Bouton():
    raise NotImplementedError
