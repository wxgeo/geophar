# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------##
#              WxGeometrie               #
#          fenetre principale            #
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

import sys, thread, traceback
import wx

from ..pylib import uu, print_error, path2, debug
from . import Panel_API_graphique
from .ligne_commande import LigneCommande
from .onglets import Onglets
from .gestion_session import GestionnaireSession
from ..API.console import Console
from .. import param
NOMPROG = param.NOMPROG



class ReceptionDeFichiers(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        for filename in filenames:
            if filename.endswith(u".geo") or filename.endswith(u".geoz"):
                self.window.onglets.ouvrir(filename)



class FenetrePrincipale(wx.Frame):
    def __init__(self, app, fichier_log=None):
        wx.Frame.__init__(self, parent=None, title=NOMPROG, pos=wx.DefaultPosition,
                          style=wx.DEFAULT_FRAME_STYLE)

        self.SetBackgroundColour(wx.NamedColor(u'WHITE'))

        self.application = app # pour acceder a l'application en interne

        # À créer avant les onglets
        self.fenetre_sortie = wx.PyOnDemandOutputWindow(title = NOMPROG + u" - messages.")
        self.fichier_log = fichier_log

        self.SetIcon(wx.Icon(path2(u"%/images/icone.ico"), wx.BITMAP_TYPE_ICO))

        # Barre de statut
        self.barre = wx.StatusBar(self, -1)
        self.barre.SetFieldsCount(2)
        self.barre.SetStatusWidths([-3, -2])
        self.SetStatusBar(self.barre)

        self.message(u"  Bienvenue !", 1)
        self.message(NOMPROG + u" version " + param.version)

        #Ligne de commande de débogage
        self.ligne_commande = LigneCommande(self, 300, action = self.executer_commande, \
                    afficher_bouton = False, legende = 'Ligne de commande :')
        self.ligne_commande.Show(param.ligne_commande)

        # Creation des onglets et de leur contenu
        self.onglets = Onglets(self, -1)

        self.__sizer_principal = wx.BoxSizer(wx.VERTICAL)
        self.__sizer_principal.Add(self.ligne_commande, 0, wx.LEFT, 5)
        self.__sizer_principal.Add(self.onglets, 1, wx.GROW)
        self.SetSizer(self.__sizer_principal)
        self.Fit()
        x_fit, y_fit = self.GetSize()
        x_param, y_param = param.dimensions_fenetre
        self.SetSize(wx.Size(max(x_fit, x_param), max(y_fit, y_param)))

        self.console = Console(self)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.SetDropTarget(ReceptionDeFichiers(self))
        self.SetFocus()

        self.__sauver_session = False
        self._auto_save_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._autosave)
        self.actualiser_intervalle_autosave()
        self.Bind (wx.EVT_IDLE, self.OnIdle)

        # closing == True si l'application est en train d'être fermée
        self.closing = False

        self.gestion = GestionnaireSession(self.onglets)


    def _autosave(self, evt=None):
        self.__sauver_session = True


    def OnIdle(self, evt):
        if self.__sauver_session:
            thread.start_new_thread(self.gestion.sauver_session, (), {'forcer': True})
            self.__sauver_session = False


    def actualiser_intervalle_autosave(self):
        if param.sauvegarde_automatique:
            self._auto_save_timer.Start(10000*param.sauvegarde_automatique)
        else:
            self._auto_save_timer.Stop()


    def afficher_ligne_commande(self, afficher=None):
        u"Afficher ou non la ligne de commande."
        if afficher is not None:
            if isinstance(afficher, bool):
                param.ligne_commande = afficher
            else:
                param.ligne_commande = not param.ligne_commande
            self.ligne_commande.Show(param.ligne_commande)
            if param.ligne_commande:
                self.ligne_commande.SetFocus()
            self.SendSizeEvent()
        return param.ligne_commande


    def mode_debug(self, debug=None):
        u"Passer en mode déboguage."
        if debug is not None:
            if isinstance(debug, bool):
                param.debug = debug
            else:
                param.debug = not param.debug
        if not param.debug:
            self.fenetre_sortie.close()
        return param.debug


    def message(self, texte, lieu=0):
        self.barre.SetStatusText(texte, lieu)


    def titre(self, texte=None):
        titre = NOMPROG
        if texte:
            titre += '-' + uu(texte)
        self.SetTitle(titre)


    def executer_commande(self, commande, **kw):
        try:
            self.console.executer(commande)
            self.message(u"Commande interne exécutée.")
            self.ligne_commande.Clear()
        except Exception:
            self.message(u"Commande incorrecte.")
            if param.debug:
                raise


    def OnClose(self, event):
        self.closing = True
        if not param.fermeture_instantanee: # pour des tests rapides
            try:
                if param.confirmer_quitter:
                    panel = self.onglets.onglet_actuel
                    if hasattr(panel, u"canvas") and hasattr(panel.canvas, u"Freeze"):
                        panel.canvas.Freeze()
                    dlg = wx.MessageDialog(self, u'Voulez-vous quitter %s ?' %NOMPROG,
                                           u'Quitter %s ?' %NOMPROG,
                                           wx.YES_NO | wx.ICON_QUESTION)
                    reponse = dlg.ShowModal()
                    if hasattr(panel, u"canvas") and hasattr(panel.canvas, u"Thaw"):
                        panel.canvas.Thaw()
                    dlg.Destroy()
                    if reponse != wx.ID_YES:
                        self.closing = False
                        return

                self.gestion.sauver_preferences()
                self.gestion.sauver_session()

                for onglet in self.onglets:
                    try:
                        if isinstance(onglet, Panel_API_graphique):
                            if param.historique_log:
                                onglet.log.archiver()
                            onglet.fermer_feuilles()
                    except:
                        #print_error()
                        debug(u"Fermeture incorrecte de l'onglet : ", uu(str(onglet)))
                        raise

            except Exception:
                try:
                    print_error()
                    wx.lib.dialogs.ScrolledMessageDialog(self, traceback.format_exc(), u"Erreur lors de la fermeture du programme").ShowModal()
                except UnicodeError:
                    wx.lib.dialogs.ScrolledMessageDialog(self, "Impossible d'afficher l'erreur.", u"Erreur lors de la fermeture du programme").ShowModal()
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        if hasattr(self, "fenetre_sortie"):
            self.fenetre_sortie.close()
        # Si le premier onglet n'est pas actif au moment de quitter, cela produit une "Segmentation fault" sous Linux.
        # Quant à savoir pourquoi...
        if self.onglets.GetRowCount():
            self.onglets.ChangeSelection(0)
        print "On ferme !"
        event.Skip()
