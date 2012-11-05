# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

#    WxGeometrie
#    Dynamic geometry, graph plotter, and more for french mathematic teachers.
#    Copyright (C) 2005-2010  Nicolas Pourcelot
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
#
######################################


# bool -> CheckBox
# file -> sélectionner un répertoire
# str -> TextCtrl
# (min, max) -> SpinCtrl
# [bool] -> CheckListBox
# ['item1', 'blabla2', ...] -> Choice

from copy import deepcopy

from .modules import modules as _modules, descriptions_modules


class Rubrique(list):
    def __init__(self, titre):
        self.titre = titre
        list.__init__(self)

    def add(self, value):
        list.append(self, value)
        return value


class Options(Rubrique):
    pass

class Theme(Rubrique):
    pass

class Section(Rubrique):
    pass

class Parametre(object):
    def __init__(self, _texte, _get = (lambda x:x), _set = (lambda x:x), **kw):
        assert len(kw) == 1
        self.nom, self.type = kw.popitem()
        if '__' in self.nom:
            self.prefixe, self.key = self.nom.split('__', 1)
        else:
            self.prefixe = self.nom
            self.key = None
        self._get = _get
        self._set = _set
        self.defaut = deepcopy(self.valeur)
        self.texte = _texte

    def _get_val(self):
        from .. import param
        if self.key is None:
            val = getattr(param, self.nom)
        else:
            val = getattr(param, self.prefixe)[self.key]
        return self._get(val)


    def _set_val(self, val):
        from .. import param
        val = self._set(val)
        if self.key is None:
            setattr(param, self.nom, val)
        else:
            getattr(param, self.prefixe)[self.key] = val

    valeur = property(_get_val, _set_val)


P = Parametre

options = Options(u'Préférences')

## GENERAL
general = options.add(Theme(u'Général'))
general.add(P(u'Utilisateur', utilisateur = str))
general.add(P(u"Nombre maximal d'annulations", nbr_annulations = (0, 1000)))

fermeture = general.add(Section(u'À la fermeture'))
fermeture.add(P(u'Demander confirmation avant de quitter.', confirmer_quitter = bool))
fermeture.add(P(u'Sauvegarder les préférences.', sauver_preferences = bool))
fermeture.add(P(u'Sauvegarder la session en cours.', sauver_session = bool))
auto = general.add(Section(u'Sauvegarde automatique'))
auto.add(P(u'Intervalle entre deux sauvegardes', sauvegarde_automatique = (0, 10000)))
auto.add(u'Temps (en dizaine de s) entre deux sauvegardes automatiques.')
auto.add(u'La valeur 0 désactive la sauvegarde automatique.')


## MODULES
modules = options.add(Theme(u'Modules'))
liste = modules.add(Section(u'Activer les modules suivants'))
for nom in _modules:
    d = {'modules_actifs__' + nom: bool}
    liste.add(P(descriptions_modules[nom]['titre'], **d))

modules.add(u'Nota: les modules non activés par défaut peuvent être non documentés\net/ou encore expérimentaux.')

#modules.add(P(u'Activer les modules suivants', modules_actifs = dict))

## FORMAT
format = options.add(Theme(u'Format'))
format.add(P(u'Décimales affichées', decimales = (0, 10)))

format.add(P(u'Unité d\'angle',
             _get = (lambda k: {'d': u'degré', 'r': 'radian', 'g':' grade'}[k]),
             _set = (lambda s: s[0]),
             unite_angle = [u'degré', 'radian', 'grade']
             ))
format.add(P(u'Séparateur décimal',
             _get = (lambda k: {',': u'virgule', '.': 'point'}[k]),
             _set = (lambda k: {'virgule': ',', 'point': '.'}[k]),
             separateur_decimal = ['virgule', 'point']
             ))



## AVANCÉ
avance = options.add(Theme(u'Avancé'))
export = avance.add(Section(u"Export"))
export.add(P(u"Résolution des images PNG", dpi_export = (10, 10000)))

sauvegarde = avance.add(Section(u"Sauvegarde"))
sauvegarde.add(P(u"Compresser les fichiers .geo par défaut.", compresser_geo = bool))

empl_pref = avance.add(Section(u"Répertoires d'enregistrement"))
empl_pref.add(P(u"Préférences", emplacements__preferences = file))
empl_pref.add(P(u"Session", emplacements__session = file))
empl_pref.add(P(u"Rapports d'erreur", emplacements__log = file))
