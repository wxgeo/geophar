# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#        Gestionnaire de feuilles             #
##--------------------------------------#######
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


from .feuille import Feuille


class Classeur(list):
    u"Gestionnaire de feuilles."

    # Indique si le contenu du classeur a été modifié depuis la dernière sauvegarde de *session*
    modifie = False

    def __init__(self, parent = None, liste = [], log = None):
        self.parent = parent
        self.log = log
        list.__init__(self, liste)
        self.nouvelle_feuille()

    def __setitem__(self, i, feuille):
        assert isinstance(feuille, Feuille)
        if feuille in self:
            self.remove(feuille)
        if i >= 0:
            list.insert(self, i, feuille)
        elif i == -1:
            list.append(self, feuille)
        else:
            list.insert(self, i + 1, feuille)
        self._classeur_modifie()

    def _get_actuelle(self):
        return self[-1]

    def _set_actuelle(self, feuille):
        self[-1] = feuille
        self._classeur_modifie()

    def _del_actuelle(self):
        self.pop()
        if not self:
            # Il faut qu'il y ait toujours une feuille pour travailler
            self.nouvelle_feuille()
        self._classeur_modifie()

    feuille_actuelle = property(_get_actuelle, _set_actuelle, _del_actuelle)


    def nouvelle_feuille(self, nom = None, parametres = None):
        # Par défaut, les paramètres sont ceux de la feuille précédente
        if parametres is None and self:
            parametres = self[-1].parametres
        if nom is None:
            noms = self.noms
            i = 1
            while ("Feuille " + str(i)) in noms:
                i += 1
            nom = "Feuille " + str(i)
        self.append(Feuille(self, titre = nom, log = self.log, parametres = parametres))
        self._classeur_modifie()
        return self[-1]

    def _classeur_modifie(self):
        self.modifie = True
        if self.parent is not None:
            self.parent._changement_feuille()

    def vider(self):
        while self:
            self.pop()
        # Il faut qu'il y ait toujours une feuille pour travailler
        self.nouvelle_feuille()

    @property
    def noms(self):
        return [feuille.nom for feuille in self]
