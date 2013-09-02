# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

##--------------------------------------#######
#                Probabilités                 #
##--------------------------------------#######
#    WxGeometrie
#    Dynamic geometry, graph plotter, and more for french mathematic teachers.
#    Copyright (C) 2005-2013  Nicolas Pourcelot
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

from PyQt4.QtGui import QDialog

from sympy import S
from sympy.core.sympify import SympifyError

from .repetition_ui import Ui_DialogRepetition
from ...geolib.routines import nice_str


def repetition_experiences(_profondeur=3, _numeroter=True, **evenements):
    u"""Génère le code d'un arbre de probabilités correspondant à la répétition
    d'expériences aléatoires identiques et indépendantes.
    Typiquement, un schéma de Bernoulli.

    >>> from wxgeometrie.modules.probabilites import repetition_experiences
    >>> print(repetition_experiences())
    >A_1:0.5
    >>A_2:0.5
    >>>A_3:0.5
    >>>&A_3:0.5
    >>&A_2:0.5
    >>>A_3:0.5
    >>>&A_3:0.5
    >&A_1:0.5
    >>A_2:0.5
    >>>A_3:0.5
    >>>&A_3:0.5
    >>&A_2:0.5
    >>>A_3:0.5
    >>>&A_3:0.5
    """
    #FIXME: rajouter des tests unitaires.
    for key, val in evenements.iteritems():
        if isinstance(val, basestring):
            val = val.strip()
            if val:
                try:
                    evenements[key] = S(val)
                except SympifyError:
                    evenements[key] = val
            else:
                evenements[key] = ''
    if not evenements:
        evenements = {'A': S('1/2'), '&A': S('1/2')}
    elif len(evenements) == 1:
        # On rajoute l'évènement complémentaire
        nom, proba = evenements.items()[0]
        contraire = (nom[1:] if nom.startswith('&') else '&' + nom)
        try:
            proba = 1 - proba
            evenements[contraire] = proba
        except TypeError:
            evenements[contraire] = ''
    else:
        ##if abs(reste) > 0.0000000001:  # param.tolerance
            ##if reste > 0:
                ##if param.debug:
                    ##print(u'Warning: la somme des probabilités ne fait pas 1.')
            ##else:
                ##raise ValueError, "La somme des probabilites depasse 1."
        # S'il manque une seule probabilité, on peut la compléter automatiquement
        completer = None
        for key, val in evenements.iteritems():
            if val == '':
                if completer is None:
                    completer = key
                else:
                    # il manque deux probabilités, impossible de compléter
                    break
        else:
            # On complète
            if completer:
                total_probas = sum(val for val in evenements.itervalues() if val)
                reste = 1 - total_probas
                evenements[completer] = reste

    def key(nom):
        u"""Classe les évènements par ordre alphabétique, mais en plaçant les
        évènements contraires en dernier."""
        return nom.replace('&', '_')
    evenements_tries = sorted(evenements, reverse=True, key=key)
    lines = ['']
    for niveau in range(1, _profondeur + 1):
        prefixe = niveau*'>'
        suffixe = ('_' + str(niveau) if _numeroter else '')
        for i in range(len(lines), 0, -1):
            if lines[i - 1].startswith((niveau - 1)*'>'):
                for nom in evenements_tries:
                    proba = evenements[nom]
                    p = nice_str(proba) if proba != '' else ''
                    lines.insert(i, prefixe + nom + suffixe + ':' + p)
            assert len(lines) < 10000
    return '\n'.join(lines).strip()



class DialogRepetition(QDialog, Ui_DialogRepetition):
    def __init__(self, parent):
        QDialog.__init__(self, parent)

        # Set up the user interface from Designer.
        self.setupUi(self)

    def accept(self):
        n = self.niveaux.value()
        num = self.numeroter.isChecked()
        evts = self.evenements.text().split(',')
        probas = self.probas.text().split(',')
        kw = {}
        for i, evt in enumerate(evts):
            if i < len(probas):
                kw[evt] = probas[i]
            else:
                kw[evt] = ''
        code = repetition_experiences(n, num, **kw)
        self.parent().instructions.setPlainText(code)
        self.parent().appliquer.click()
