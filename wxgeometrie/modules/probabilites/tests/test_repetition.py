# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../../.."))
sys.path.insert(0, TOPDIR)

from functools import partial

from wxgeometrie.modules.probabilites.repetition import repetition_experiences as rep

import wx_unittest

class ModulesProbabilitesTest(wx_unittest.TestCase):
    def test_repetition_un_niveau(self):
        rep1 = partial(rep, 1)
        s = rep1(evts=['A'], probas=['0,3'])
        self.assertEqual(s, '>A_1:0,3\n>&A_1:0,7')
        s = rep1(evts=['A', 'B', 'C'], probas=['0,3', '0,5', '0,2'])
        self.assertEqual(s, '>A_1:0,3\n>B_1:0,5\n>C_1:0,2')
        s = rep1(evts=['A', 'B', 'C'], probas=['0,1', '0,6'])
        self.assertEqual(s, '>A_1:0,1\n>B_1:0,6\n>C_1:0,3')


    def test_repetition_plusieurs_niveaux(self):
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
        self.assertEqual(s, resultat)


    def test_repetition_sans_numeroter(self):
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
        self.assertEqual(s, resultat)

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
        self.assertEqual(s, resultat)
