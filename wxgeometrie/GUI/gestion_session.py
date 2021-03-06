# -*- coding: utf-8 -*-

##--------------------------------------##
#              WxGeometrie               #
#        gestionnaire de session         #
##--------------------------------------##
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

import os, re
from time import sleep

from PyQt5.QtCore import pyqtSignal, QObject

from ..pylib import print_error, path2, debug, warning
from ..API.sauvegarde import FichierSession
from ..API.parametres import sauvegarder_module
from .. import param
from .qtlib import GenericThread


class GestionnaireSession(QObject):

    session_a_sauver = pyqtSignal()

    def __init__(self, onglets):
        super(GestionnaireSession, self).__init__()
        self.onglets = onglets
        self.__run = True
        self.thread = GenericThread(function=self._autosave_timer)
        self.thread.start()
        self.session_a_sauver.connect(self.sauver_session)

    def _autosave_timer(self):
        try:
            while self.__run:
                if param.sauvegarde_automatique:
                    self.session_a_sauver.emit()
                sleep(max(10*param.sauvegarde_automatique, 2))
        except AttributeError:
            print('Warning: closing thread...')
            # Si le programme est en train d'être fermé, param peut ne
            # plus exister.

    def _session_path(self, name):
        return os.path.join(path2(param.emplacements['session']), name)

    def _fichier_preferences(self):
        return path2(param.emplacements['preferences'] + "/parametres.xml")

    def liste_sessions(self):
        path = path2(param.emplacements['session'])
        return sorted(name for name in os.listdir(path)
                                if re.match(r'session-\d+-\d+\.geos$', name))


    def sauver_session(self, lieu=None, force=False):
        fichiers_ouverts = []
        if not force and not any(onglet.modifie for onglet in self.onglets):
            return
        for onglet in self.onglets:
            fichiers_ouverts.extend(onglet._fichiers_ouverts())
        if self.onglets.onglet_actuel is None:
            print("Warning: Aucun onglet ouvert ; impossible de sauver la session !")
            return
        kw = {'onglet_actif': self.onglets.onglet_actuel.nom}
        session = FichierSession(*fichiers_ouverts, **kw)
        if lieu is None:
            lieu = self._session_path('session-%s.geos' % param.ID)
            for onglet in self.onglets:
                onglet.modifie = False
        session.ecrire(lieu, compresser = True)
        print("Session sauvée : (%s)" % lieu)


    def charger_session(self, lieu=None, reinitialiser=True, activer_modules=True):
        if reinitialiser:
            self.reinitialiser_session()
        if lieu is None:
            names = self.liste_sessions()
            try:
                name = names[-1]
                if name == 'session-%s.geos' % param.ID:
                    # Le dernier fichier correspond à la session courante.
                    name = names[-2]
            except IndexError:
                print("Warning: impossible de trouver la session précédente !")
                return
            lieu = self._session_path(name)
        session = FichierSession().ouvrir(lieu)
        for fichier in session:
            if activer_modules or param.modules_actifs[fichier.module]:
                self.onglets.ouvrir(fichier, en_arriere_plan = True)
        try:
            self.onglets.changer_onglet(session.infos['onglet_actif'])
        except (IndexError, AttributeError):
            warning("Impossible de restaurer l'onglet actif (%s)." %session.infos['onglet_actif'])


    def reinitialiser_session(self):
        for onglet in self.onglets:
            onglet.reinitialiser()


    def fermer(self):
        """Ferme proprement le gestionnaire de session.

        * La session en cours et les préférences sont sauvegardées.
        * Les anciens fichiers de sessions sont supprimés s'ils deviennent trop
          nombreux.
          Le nombre maximal de fichiers de session automatiquement sauvegardés
          est déterminé par ``param.nbr_sessions``.
        """
        self.__run = False
        self.sauver_preferences()
        # On force la sauvegarde de session, même si aucun module ne signale
        # de modification non sauvegardée, ne serait-ce que pour enregistrer
        # l'onglet courant.
        self.sauver_session(force=True)
        for name in self.liste_sessions()[:-param.nbr_sessions]:
            os.remove(self._session_path(name))


    def sauver_preferences(self, forcer=True):
        if param.sauver_preferences or forcer:
            fgeo = sauvegarder_module(param)
            fgeo.ecrire(self._fichier_preferences())
            for onglet in self.onglets:
                try:
                    onglet.sauver_preferences()
                except:
                    debug("Fermeture incorrecte de l'onglet : ", str(onglet))
                    raise
        else:
            # La préférence 'sauver_preferences' doit être sauvée dans tous les cas,
            # sinon il ne serait jamais possible de désactiver les préférences depuis WxGéométrie !
            fgeo = sauvegarder_module({'sauver_preferences': False})
            fgeo.ecrire(self._fichier_preferences())
