# -*- coding: utf-8 -*-


def _yellow(s):
    return '\033[0;33m' + s + '\033[0m'

def _green(s):
    return '\033[0;32m' + s + '\033[0m'


def assert_tableau(func, chaine, attendu, **options):
    resultat = func(chaine, **options)
    if resultat != attendu:
        print("-------")
        for i in range(min(len(resultat), len(attendu))):
            if resultat[i] != attendu[i]:
                break
        resultat = resultat[:i] + _yellow(resultat[i:])
        attendu = attendu[:i] + _green(attendu[i:])
        print("ERREUR:")
        print("Expected output was:")
        print(attendu)
        print("While actual result is:")
        print(resultat)
        #~ if i >= len(attendu):
            #~ print('Output too long:')
            #~ print(resultat[i:])
        #~ else:
            #~ print('Difference:')
            #~ print('char number:', i)
            #~ print('result:', repr(resultat[i:i+10]))
            #~ print('expected:', repr(attendu[i:i+10]))
        print("-------")
    assert (resultat == attendu)

