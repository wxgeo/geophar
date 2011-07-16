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

import sys, os, thread, traceback
import wx

from ..pylib import uu, print_error, path2, debug, warning
from . import Panel_API_graphique
from .ligne_commande import LigneCommande
from .onglets import Onglets
from ..API.console import Console
from ..API.sauvegarde import FichierSession
from ..API.parametres import sauvegarder_module
from .. import param

######################################################


class ReceptionDeFichiers(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        for filename in filenames:
            if filename.endswith(u".geo") or filename.endswith(u".geoz"):
                self.window.onglets.ouvrir(filename)



class WxGeometrie(wx.Frame):
    def __init__(self, app, fichier_log = None):
        wx.Frame.__init__(self, parent = None, title = u"WxGéométrie", pos=wx.DefaultPosition, style=wx.DEFAULT_FRAME_STYLE)

        self.SetBackgroundColour(wx.NamedColor(u"WHITE"))

        self.application = app # pour acceder a l'application en interne

        # À créer avant les onglets
        self.fenetre_sortie = wx.PyOnDemandOutputWindow(title = u"WxGéométrie - messages.")
        self.fichier_log = fichier_log

        self.SetIcon(wx.Icon(path2(u"%/images/icone.ico"), wx.BITMAP_TYPE_ICO))

        # Barre de statut
        self.barre = wx.StatusBar(self, -1)
        self.barre.SetFieldsCount(2)
        self.barre.SetStatusWidths([-3, -2])
        self.barre.SetStatusText(u"  Bienvenue !", 1)
        self.barre.SetStatusText(u"WxGéométrie version " + param.version, 0)
        self.SetStatusBar(self.barre)

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

#        self._auto_save_timer=wx.Timer(self)
#        self.Bind(wx.EVT_TIMER, self._auto_save)
#        self._auto_save_timer.Start(150)
        self.__sauver_session = False
        self._auto_save_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._autosave)
        self.actualiser_intervalle_autosave()
        self.Bind (wx.EVT_IDLE, self.OnIdle)

        # closing == True si l'application est en train d'être fermée
        self.closing = False

        #self.DragAcceptFiles(True)
        #self.Bind(wx.EVT_DROP_FILES, self.OnDrop)

        # Création (si nécessaire) des répertoires /log, /macro, etc., définis dans /param/__init__.py
        for repertoire in param.emplacements:
            repertoire = path2(repertoire)
            if not os.path.isdir(repertoire):
                try:
                    os.makedirs(repertoire)
                except IOError:
                    print_error()

    def _autosave(self, evt = None):
        self.__sauver_session = True

    def OnIdle(self, evt):
        if self.__sauver_session:
            thread.start_new_thread(self.sauver_session, ())
            self.__sauver_session = False

    def actualiser_intervalle_autosave(self):
        if param.sauvegarde_automatique:
            self._auto_save_timer.Start(10000*param.sauvegarde_automatique)
        else:
            self._auto_save_timer.Stop()



    def afficher_ligne_commande(self, afficher = None):
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


    def mode_debug(self, debug = None):
        u"Passer en mode déboguage."
        if debug is not None:
            if isinstance(debug, bool):
                param.debug = debug
            else:
                param.debug = not param.debug
        if not param.debug:
            self.fenetre_sortie.close()
        return param.debug


#####################################################################



    #def recharger(self, event):
    #    reload(param)
    #
    #    self.onglets.onglet_actuel.historique.rafraichir()
    #    self.barre.SetStatusText("Parametres et figure recharges.", 0)

    def message(self, texte, lieu = 0):
        self.barre.SetStatusText(texte, lieu)

    def titre(self, texte = u""):
        if texte:
            self.SetTitle(u"WxGéométrie - " + uu(texte))
        else:
            self.SetTitle(u"WxGéométrie")



#    # <PERIME>
#    def sauver_session(self, lieu = None):
#        fichiers_ouverts = []
#        for onglet in self.onglets:
#            fichiers_ouverts.extend(onglet._fichiers_ouverts())
#        fgeo = sauvegarder_session(*fichiers_ouverts)
#        if lieu is None:
#            lieu = path2(param.emplacements['session'] + "/session.xml.gz")
#        fgeo.ecrire(lieu, zip = True)


#    def charger_session(self, lieu = None, reinitialiser = True):
#        if reinitialiser:
#            self.reinitialiser_session()
#        if lieu is None:
#            lieu = path2(param.emplacements['session'] + "/session.xml.gz")
#        for fichier in ouvrir_session(lieu):
#            self.onglets.ouvrir(fichier, en_arriere_plan = True)
#    # </PERIME>


    def reinitialiser_session(self):
        for onglet in self.onglets:
            onglet.reinitialiser()


    def sauver_session(self, lieu = None, seulement_si_necessaire = True):
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


    def charger_session(self, lieu = None, reinitialiser = True):
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

#    def _auto_save(self, evt = None):
#        self.sauver_session()

    def executer_commande(self, commande, **kw):
        try:
            self.console.executer(commande)
            self.barre.SetStatusText(u"Commande interne exécutée.", 0)
            self.ligne_commande.Clear()
        except Exception:
            self.barre.SetStatusText(u"Commande incorrecte.", 0)
            if param.debug:
                raise


    def _old_EvtChar(self, event):    # gere la ligne de commandes
        commande = self.commande.GetValue()
        code = event.GetKeyCode()

        if self.commande_en_cours_a_sauvegarder and commande.strip():
            self.commande_en_cours = commande
            self.commande_en_cours_a_sauvegarder = False

        if code == wx.WXK_RETURN or code == wx.WXK_NUMPAD_ENTER:
            try:
                self.console.executer(commande)
                self.barre.SetStatusText(u"Commande interne exécutée.", 0)
                self.historique.append(commande)
                self.commande_en_cours = ""
                self.position = len(self.historique) - 1
                self.commande.Clear()
            except:
                self.barre.SetStatusText(u"Commande incorrecte.", 0)
                if param.debug:
                    raise

        elif code == wx.WXK_UP:   # on remonte dans l'historique des commandes
            if self.position >= 0:
                if self.position == len(self.historique):
                    self.commande.SetValue(self.commande_en_cours)
                else:
                    self.commande.SetValue(self.historique[self.position])
                self.position = self.position - 1

        elif code == wx.WXK_DOWN:   # on redescend dans l'historique vers les commandes recentes
            if self.position < len(self.historique) -1 or (self.position == len(self.historique) -1 and self.commande_en_cours):
                if self.position == (len(self.historique) - 2):
                    self.commande.SetValue(self.commande_en_cours)
                elif self.position == (len(self.historique) - 1):
                    self.commande.Clear()
                else:
                    self.commande.SetValue(self.historique[self.position + 2])
                self.position += 1
        else:
            event.Skip()
            self.commande_en_cours_a_sauvegarder = True


    def OnClose(self, event):
        self.closing = True
        if not param.fermeture_instantanee: # pour des tests rapides
            try:
                if param.confirmer_quitter:
                    panel = self.onglets.onglet_actuel
                    if hasattr(panel, u"canvas") and hasattr(panel.canvas, u"Freeze"):
                        panel.canvas.Freeze()
                    dlg = wx.MessageDialog(self, u'Voulez-vous quitter WxGéométrie ?', u'Quitter WxGéométrie ?', wx.YES_NO | wx.ICON_QUESTION)
                    reponse = dlg.ShowModal()
                    if hasattr(panel, u"canvas") and hasattr(panel.canvas, u"Thaw"):
                        panel.canvas.Thaw()
                    dlg.Destroy()
                    if reponse != wx.ID_YES:
                        self.closing = False
                        return

                if param.sauver_preferences:
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


                if param.sauver_session:
                    self.sauver_session()

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
