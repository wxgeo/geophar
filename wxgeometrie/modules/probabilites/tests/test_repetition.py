# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from functools import partial

from tools.testlib import assertEqual
from wxgeometrie.modules.probabilites.repetition import repetition_experiences as rep


def test_repetition_un_niveau():
    rep1 = partial(rep, 1)
    s = rep1(evts=['A'], probas=['0,3'])
    assertEqual(s, '>A_1:0,3\n>&A_1:0,7')
    s = rep1(evts=['A', 'B', 'C'], probas=['0,3', '0,5', '0,2'])
    assertEqual(s, '>A_1:0,3\n>B_1:0,5\n>C_1:0,2')
    s = rep1(evts=['A', 'B', 'C'], probas=['0,1', '0,6'])
    assertEqual(s, '>A_1:0,1\n>B_1:0,6\n>C_1:0,3')


def test_repetition_plusieurs_niveaux():
    s = rep(3, evts=['S'], probas=['3/4'])
    resultat = '''>S_1:3/4
>>S_2:3/4
>>>S_3:3/4
>>>&S_3:1/4
>>&S_2:1/4
>>>S_3:3/4
>>>&S_3:1/4
>&S_1:1/4
>>S_2:3/4
>>>S_3:3/4
>>>&S_3:1/4
>>&S_2:1/4
>>>S_3:3/4
>>>&S_3:1/4'''
    assertEqual(s, resultat)


def test_repetition_sans_numeroter():
    rep2 = partial(rep, 2, False)

    s = rep2(evts=['A', 'B', 'C'], probas=['0,5', '0,3', '0,2'])
    resultat = '''>A:0,5
>>A:0,5
>>B:0,3
>>C:0,2
>B:0,3
>>A:0,5
>>B:0,3
>>C:0,2
>C:0,2
>>A:0,5
>>B:0,3
>>C:0,2'''
    assertEqual(s, resultat)

    s = rep2(evts=['&A'], probas=['0,6'])
    resultat = '''>A:0,4
>>A:0,4
>>&A:0,6
>&A:0,6
>>A:0,4
>>&A:0,6'''

    s = rep(3, False, evts=['F', 'G'], probas=['', ''])
    resultat = '''>F:
>>F:
>>>F:
>>>G:
>>G:
>>>F:
>>>G:
>G:
>>F:
>>>F:
>>>G:
>>G:
>>>F:
>>>G:'''
    assertEqual(s, resultat)
