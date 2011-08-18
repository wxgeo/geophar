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

from PyQt4.QtGui import (QMainWindow, QApplication, QPlainTextEdit, QIcon,
                        QLabel, QWidget, QVBoxLayout, QMessageBox)
from PyQt4.QtCore import QSize

from ..pylib import uu, print_error, path2, debug, warning
from ..API.console import Console
from ..API.sauvegarde import FichierSession
from ..API.parametres import sauvegarder_module
from .compatibility import WxQt, PyOnDemandOutputWindow
from .gestion_session import GestionnaireSession
from .onglets import Onglets
from .. import param
NOMPROG = param.NOMPROG


class PyOnDemandOutputWindow(QPlainTextEdit):
    def __init__(self, title):
        QPlainTextEdit.__init__(self)
        self.setWindowTitle(title)
        self.setReadOnly(True) # assuming QPlainTextEdit
        self.hide()
        self.resize(QSize(450, 300))

    def write(self, s):
        self.show()
        self.insertPlainText(s.decode(param.encodage)) # again assuming QPlainTextEdit


#class ReceptionDeFichiers(wx.FileDropTarget):
#    def __init__(self, window):
#        wx.FileDropTarget.__init__(self)
#        self.window = window

#    def OnDropFiles(self, x, y, filenames):
#        for filename in filenames:
#            if filename.endswith(u".geo") or filename.endswith(u".geoz"):
#                self.window.onglets.ouvrir(filename)



class FenetrePrincipale(QMainWindow):
    def __init__(self, app, fichier_log=None):
        QMainWindow.__init__(self, None)
        self.setWindowTitle(NOMPROG)
#        self.setStyleSheet("background:white")

        self.application = app # pour acceder a l'application en interne

        # À créer avant les onglets
        self.fenetre_sortie = PyOnDemandOutputWindow(title = NOMPROG + u" - messages.")
        self.fichier_log = fichier_log

        self.setWindowIcon(QIcon(path2(u"%/images/icone.ico")))
        self.barre = self.statusBar()
        self.barre_dte = QLabel(self)
#        self.barre_dte.setText(
        self.barre.addPermanentWidget(self.barre_dte)


#        # Barre de statut
#        self.barre = wx.StatusBar(self, -1)
#        self.barre.SetFieldsCount(2)
#        self.barre.SetStatusWidths([-3, -2])
#        self.SetStatusBar(self.barre)

        self.message(u"  Bienvenue !", 1)
        self.message(NOMPROG + u" version " + param.version)

#        #Ligne de commande de débogage
#        self.ligne_commande = LigneCommande(self, 300, action = self.executer_commande, \
#                    afficher_bouton = False, legende = 'Ligne de commande :')
#        self.ligne_commande.setVisible(param.ligne_commande)

#        # Creation des onglets et de leur contenu
        self.onglets = Onglets(self)

        self.mainWidget=QWidget(self) # dummy widget to contain the
                                      # layout manager
        self.setCentralWidget(self.mainWidget)
        self.mainLayout = QVBoxLayout(self.mainWidget)
        self.mainLayout.addWidget(self.onglets)

#        self.__sizer_principal = wx.BoxSizer(wx.VERTICAL)
#        self.__sizer_principal.Add(self.ligne_commande, 0, wx.LEFT, 5)
#        self.__sizer_principal.Add(self.onglets, 1, wx.GROW)
#        self.SetSizer(self.__sizer_principal)
#        self.Fit()
#        x_fit, y_fit = self.GetSize()
#        x_param, y_param = param.dimensions_fenetre
#        self.SetSize(wx.Size(max(x_fit, x_param), max(y_fit, y_param)))
        self.setMinimumSize(*param.dimensions_fenetre)

#        self.console = Console(self)

#        self.Bind(wx.EVT_CLOSE, self.OnClose)

#        self.SetDropTarget(ReceptionDeFichiers(self))
        self.setFocus()

#        self.Bind (wx.EVT_IDLE, self.OnIdle)

        # closing == True si l'application est en train d'être fermée
        self.closing = False

        self.gestion = GestionnaireSession(self.onglets)


    def OnIdle(self, evt):
        self.gestion.autosave()


    def afficher_ligne_commande(self, afficher=None):
        u"Afficher ou non la ligne de commande."
        if afficher is not None:
            if isinstance(afficher, bool):
                param.ligne_commande = afficher
            else:
                param.ligne_commande = not param.ligne_commande
            self.ligne_commande.setVisible(param.ligne_commande)
            if param.ligne_commande:
                self.ligne_commande.setFocus()
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
        if lieu == 0:
            self.barre.showMessage(texte)
        else:
            assert lieu == 1
            self.barre_dte.setText(texte)


    def titre(self, texte=None):
        titre = NOMPROG
        if texte:
            titre += '-' + uu(texte)
        self.setWindowTitle(titre)


    def executer_commande(self, commande, **kw):
        try:
            self.console.executer(commande)
            self.message(u"Commande interne exécutée.")
            self.ligne_commande.clear()
        except Exception:
            self.message(u"Commande incorrecte.")
            if param.debug:
                raise


    def closeEvent(self, event):
        self.closing = True
        if not param.fermeture_instantanee: # pour des tests rapides
            try:
                if param.confirmer_quitter:
                    panel = self.onglets.onglet_actuel
                    test = hasattr(panel, 'canvas') and hasattr(panel.canvas, 'setUpdatesEnabled')
                    if test:
                        panel.canvas.setUpdatesEnabled(False)
                    reponse = QMessageBox.question(self, u'Quitter %s ?' %NOMPROG,
                                               u'Voulez-vous quitter %s ?' %NOMPROG,
                                               QMessageBox.Yes | QMessageBox.No)
                    if test:
                        panel.canvas.setUpdatesEnabled(True)
                    if reponse != QMessageBox.Yes:
                        self.closing = False
                        event.ignore()
                        return

                self.gestion.sauver_preferences()
                self.gestion.sauver_session()

#                for onglet in self.onglets:
#                    try:
#                        if isinstance(onglet, Panel_API_graphique):
#                            if param.historique_log:
#                                onglet.log.archiver()
#                            onglet.fermer_feuilles()
#                    except:
#                        #print_error()
#                        debug(u"Fermeture incorrecte de l'onglet : ", uu(str(onglet)))
#                        raise

            except Exception:
                try:
                    print_error()
                    QMessageBox.warning(self, u"Erreur lors de la fermeture du programme", traceback.format_exc())
                except UnicodeError:
                    MessageBox.warning(self, u"Erreur lors de la fermeture du programme", "Impossible d'afficher l'erreur.")
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        if hasattr(self, "fenetre_sortie"):
            self.fenetre_sortie.close()
#        # Si le premier onglet n'est pas actif au moment de quitter, cela produit une "Segmentation fault" sous Linux.
#        # Quant à savoir pourquoi...
#        if self.onglets.GetRowCount():
#            self.onglets.ChangeSelection(0)
        print "On ferme !"
#        event.Skip()
