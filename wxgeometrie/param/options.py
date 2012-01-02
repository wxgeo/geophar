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
# file -> s�lectionner un r�pertoire
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
        import param
        if self.key is None:
            val = getattr(param, self.nom)
        else:
            val = getattr(param, self.prefixe)[self.key]
        return self._get(val)


    def _set_val(self, val):
        import param
        val = self._set(val)
        if self.key is None:
            setattr(param, self.nom, val)
        else:
            getattr(param, self.prefixe)[self.key] = val

    valeur = property(_get_val, _set_val)


P = Parametre

options = Options(u'Pr�f�rences')

## GENERAL
general = options.add(Theme(u'G�n�ral'))
general.add(P(u'Utilisateur', utilisateur = str))
general.add(P(u"Nombre maximal d'annulations", nbr_annulations = (0, 1000)))

fermeture = general.add(Section(u'� la fermeture'))
fermeture.add(P(u'Demander confirmation avant de quitter.', confirmer_quitter = bool))
fermeture.add(P(u'Sauvegarder les pr�f�rences.', sauver_preferences = bool))
fermeture.add(P(u'Sauvegarder la session en cours.', sauver_session = bool))
auto = general.add(Section(u'Sauvegarde automatique'))
auto.add(P(u'Intervalle entre deux sauvegardes', sauvegarde_automatique = (0, 10000)))
auto.add(u'Temps (en dizaine de s) entre deux sauvegardes automatiques.')
auto.add(u'La valeur 0 d�sactive la sauvegarde automatique.')


## MODULES
modules = options.add(Theme(u'Modules'))
liste = modules.add(Section(u'Activer les modules suivants'))
for nom in _modules:
    d = {'modules_actifs__' + nom: bool}
    liste.add(P(descriptions_modules[nom]['titre'], **d))

modules.add(u'Nota: les modules non activ�s par d�faut peuvent �tre non document�s\net/ou encore exp�rimentaux.')

#modules.add(P(u'Activer les modules suivants', modules_actifs = dict))

## FORMAT
format = options.add(Theme(u'Format'))
format.add(P(u'D�cimales affich�es', decimales = (0, 10)))

format.add(P(u'Unit� d\'angle', _get = (lambda k:{'d':u'degr�', 'r':'radian', 'g':'grade'}[k]),
                               _set = (lambda s:s[0]),
                               unite_angle = [u'degr�', 'radian', 'grade']
                               ))


## AVANC�
avance = options.add(Theme(u'Avanc�'))
export = avance.add(Section(u"Export"))
export.add(P(u"R�solution des images PNG", dpi_export = (10, 10000)))

sauvegarde = avance.add(Section(u"Sauvegarde"))
sauvegarde.add(P(u"Compresser les fichiers .geo par d�faut.", compresser_geo = bool))

empl_pref = avance.add(Section(u"R�pertoires d'enregistrement"))
empl_pref.add(P(u"Pr�f�rences", emplacements__preferences = file))
empl_pref.add(P(u"Session", emplacements__session = file))
empl_pref.add(P(u"Rapports d'erreur", emplacements__log = file))
