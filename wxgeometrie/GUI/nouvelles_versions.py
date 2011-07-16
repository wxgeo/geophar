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


import thread, urllib, webbrowser
import wx
from wxlib import TransmitEvent, EVT_TRANSMIT

from ..pylib import print_error
from .. import param


class Progression:
    def __init__(self, parent):
        self.parent = parent
        self.initialiser = True
        self.titre = u"Vérification des nouvelles versions."

    def actualiser(self, blocs_finis = None, taille_bloc = None, taille_fichier = None):
        if blocs_finis != None:
            self.fini = min(taille_bloc*blocs_finis, taille_fichier)
            #print self.fini

        # la premiere fois, on cree la fenetre de progression.
        if self.initialiser:
            self.dlg = wx.ProgressDialog(self.titre, u"Vérification en cours.",
                               maximum = taille_fichier,
                               parent = self.parent,
                               style = wx.PD_CAN_ABORT
                                | wx.PD_APP_MODAL
                                | wx.PD_ELAPSED_TIME
                                | wx.PD_AUTO_HIDE
                                | wx.PD_ESTIMATED_TIME
                                | wx.PD_REMAINING_TIME
                                )
            self.timer = wx.FutureCall(500, self.actualiser)

        # les autres fois, on l'actualise.
        else:
            if not self.dlg.Update(self.fini):
                self.fin()
                raise ValueError # de maniere a interrompre le telechargement en cours.
            self.timer.Restart(500)
        self.initialiser = False


    def fin(self):
        try:
            self.timer.Stop()
            del self.timer
            self.dlg.Destroy()

        except: pass







class Gestionnaire_mises_a_jour(wx.EvtHandler):
    def __init__(self, parent):
        self.parent = parent
        self.derniere_version = None
        wx.EvtHandler.__init__(self)
        self.Bind(EVT_TRANSMIT, self.onTransmit)



    def onTransmit(self, event):
        if event.success:
            if event.update_available:
                self.derniere_version = event.version
                wx.MessageBox(u"La version %s de WxGéométrie est sortie.\nVous allez être redirigé vers la page de téléchargement." %event.version, u"Une mise à jour a été trouvée.")
                webbrowser.open("http://sourceforge.net/projects/wxgeometrie/files/WxGeometrie/")
            else:
                wx.MessageBox(u"Aucune mise à jour n'est disponible actuellement.\nConsultez http://wxgeo.free.fr pour plus d'informations.", u"Aucune mise à jour trouvée.")
        else:
            wx.MessageBox(u"Impossible de vérifier si une nouvelle version existe.", u"Connexion impossible")


    def verifier_version(self, event = None):
        thread.start_new_thread(self._verifier_version, ())


    def _verifier_version(self, event = None):
#        progression = Progression(self.parent)
        try:
            filename, headers = urllib.urlretrieve("http://wxgeo.free.fr/wordpress/version")#, None, progression.actualiser)
            f = open(filename)
            version = f.read(60)
            f.close()
            if len(version) > 50 or not version.replace(" ", "").replace(".", "").isalnum():
                raise Exception, "Incorrect file format, unable to find current version."
            if version.split(".") > param.version.split('.'):
                wx.PostEvent(self, TransmitEvent(success = True, update_available = True, version = version))
            else:
                wx.PostEvent(self, TransmitEvent(success = True, update_available = False))
        except:
            print_error()
            wx.PostEvent(self, TransmitEvent(success = False, update_available = None))
