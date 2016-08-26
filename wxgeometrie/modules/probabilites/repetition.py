# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

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


def repetition_experiences(_profondeur=3, _numeroter=True, evts=[], probas=[]):
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
    if not evts:
        evts = ['A']
    if len(evts) == 1:
        # On rajoute automatiquement l'évènement contraire.
        evt = evts[0]
        evts.append(evt[1:] if evt.startswith('&') else '&' + evt)

    # On complète pour que la liste des évènements et celle des probabilités
    # aient la même taille.
    if len(probas) > len(evts):
        evts += (len(probas) - len(evts))*['']
    else:
        if len(probas) == len(evts) - 1:
            try:
                probas.append(nice_str(1 - sum(S(proba.replace(',', '.')) for proba in probas)))
            except SympifyError:
                pass
        if len(probas) < len(evts):
            probas += (len(evts) - len(probas))*['']

    # On génère le code.
    lines = ['']
    for niveau in range(1, _profondeur + 1):
        prefixe = niveau*'>'
        suffixe = ('_' + str(niveau) if _numeroter else '')
        for i in range(len(lines), 0, -1):
            if lines[i - 1].startswith((niveau - 1)*'>'):
                for evt, proba in reversed(zip(evts, probas)):
                    #~ proba = nice_str(proba) if proba != '' else ''
                    lines.insert(i, prefixe + evt + suffixe + ':' + proba)
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
        evts = [evt.strip() for evt in self.evenements.text().split(';')]
        probas = [proba.strip() for proba in self.probas.text().split(';')]

        code = repetition_experiences(n, num, evts, probas)
        self.parent().instructions.setPlainText(code)
        self.parent().appliquer.click()
