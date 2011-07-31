# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------##
#              WxGeometrie               #
#        gestionnaire de session         #
##--------------------------------------##
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

import os

from ..pylib import uu, print_error, path2, debug, warning
from ..API.sauvegarde import FichierSession
from ..API.parametres import sauvegarder_module
from .. import param


class GestionnaireSession(object):
    def __init__(self, onglets):
        self.onglets = onglets
        # Création (si nécessaire) des répertoires /log, /macro, etc., définis dans /param/__init__.py
        for repertoire in param.emplacements:
            repertoire = path2(repertoire)
            if not os.path.isdir(repertoire):
                try:
                    os.makedirs(repertoire)
                except IOError:
                    print_error()


    def sauver_session(self, lieu=None, seulement_si_necessaire=True, forcer=False):
        if param.sauver_session or forcer:
            fichiers_ouverts = []
            if seulement_si_necessaire and not any(onglet.modifie for onglet in self.onglets):
                return
            for onglet in self.onglets:
                fichiers_ouverts.extend(onglet._fichiers_ouverts())
            if self.onglets.onglet_actuel is None:
                print("Warning: Aucun onglet ouvert ; impossible de sauver la session !")
                return
            session = FichierSession(*fichiers_ouverts, **{'onglet_actif': self.onglets.onglet_actuel.nom})
            if lieu is None:
                lieu = path2(param.emplacements['session'] + "/session.tar.gz")
                for onglet in self.onglets:
                    onglet.modifie = False
            session.ecrire(lieu, compresser = True)
            print(u"Session sauvée : (%s)" %lieu)


    def charger_session(self, lieu=None, reinitialiser=True):
        if reinitialiser:
            self.reinitialiser_session()
        if lieu is None:
            lieu = path2(param.emplacements['session'] + "/session.tar.gz")
        session = FichierSession().ouvrir(lieu)
        for fichier in session:
            self.onglets.ouvrir(fichier, en_arriere_plan = True)
        try:
            self.onglets.changer_onglet(session.infos['onglet_actif'])
        except (IndexError, AttributeError):
            warning("Impossible de restaurer l'onglet actif (%s)." %session.infos['onglet_actif'])


    def reinitialiser_session(self):
        for onglet in self.onglets:
            onglet.reinitialiser()


    def sauver_preferences(self, forcer=True):
        if param.sauver_preferences or forcer:
            fgeo = sauvegarder_module(param)
            fgeo.ecrire(path2(param.emplacements['preferences'] + "/parametres.xml"))
            for onglet in self.onglets:
                try:
                    onglet.sauver_preferences()
                except:
                    debug(u"Fermeture incorrecte de l'onglet : ", uu(str(onglet)))
                    raise
        else:
            # La préférence 'sauver_preferences' doit être sauvée dans tous les cas,
            # sinon il ne serait jamais possible de désactiver les préférences depuis WxGéométrie !
            fgeo = sauvegarder_module({'sauver_preferences': False})
            fgeo.ecrire(path2(param.emplacements['preferences'] + "/parametres.xml"))
