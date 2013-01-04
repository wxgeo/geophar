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

from PyQt4.QtGui import (QMainWindow, QApplication, QPlainTextEdit, QIcon, QColor, QPalette,
                        QLabel, QWidget, QVBoxLayout, QMessageBox, QTextCursor)
from PyQt4.QtCore import QSize, Qt, pyqtSignal

from ..pylib import uu, print_error, path2, debug, warning
from ..API.console import Console
from ..API.sauvegarde import FichierSession
from ..API.parametres import sauvegarder_module
from .ligne_commande import LigneCommande
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
        self.moveCursor(QTextCursor.End)
        self.insertPlainText(s.decode(param.encodage)) # again assuming QPlainTextEdit



class FenetrePrincipale(QMainWindow):

    def __init__(self, app, fichier_log=None):
        QMainWindow.__init__(self, None)
        self.setWindowTitle(NOMPROG)
        self.setStyleSheet(".QWidget {background:white}")
#        palette = QPalette()
#        white = QColor(Qt.white)
#        palette.setColor(QPalette.Window, white)
#        palette.setColor(QPalette.AlternateBase, white)
#        self.setPalette(palette)

        self.application = app # pour acceder a l'application en interne
        # Pour que toutes les fenêtres puissent simplement retrouver la
        # fenêtre principale:
        app.fenetre_principale = self


        # À créer avant les onglets
        self.fenetre_sortie = PyOnDemandOutputWindow(title=u"%s - messages."
                                                             % NOMPROG)
        self.fenetre_sortie.setWindowIcon(
                            QIcon(path2(u"%/wxgeometrie/images/icone_log.svg")))
        self.fichier_log = fichier_log

        self.setWindowIcon(QIcon(path2(u"%/wxgeometrie/images/icone.svg")))
        self.barre = self.statusBar()
        self.barre_dte = QLabel(self)
#        self.barre_dte.setText(
        self.barre.addPermanentWidget(self.barre_dte)



        self.message(u"  Bienvenue !", 1)
        self.message(NOMPROG + u" version " + param.version)

        #Ligne de commande de débogage
        self.ligne_commande = LigneCommande(self, 300, action=self.executer_commande,
                        afficher_bouton=False, legende='Ligne de commande :')
        self.ligne_commande.setVisible(param.ligne_commande)

        # Creation des onglets et de leur contenu
        self.onglets = Onglets(self)

        self.mainWidget=QWidget(self) # dummy widget to contain the
                                      # layout manager
        self.setCentralWidget(self.mainWidget)
        self.mainLayout = QVBoxLayout(self.mainWidget)
        self.mainLayout.setSpacing(0)
        self.mainLayout.addWidget(self.ligne_commande, 0)
        self.mainLayout.addWidget(self.onglets)

        self.setMinimumSize(*param.dimensions_fenetre)

        self.console = Console(self)

        self.setAcceptDrops(True)
        self.setFocus()

        # closing == True si l'application est en train d'être fermée
        self.closing = False

        self.gestion = GestionnaireSession(self.onglets)


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            if any(url.path().endswith('.geo') or url.path().endswith('.geoz')
                    for url in event.mimeData().urls()):
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event):
        assert event.mimeData().hasUrls()
        for url in event.mimeData().urls():
            if url.path().endswith('.geo') or url.path().endswith('.geoz'):
                self.onglets.ouvrir(unicode(url.path()))

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
            titre += ' - ' + uu(texte)
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

    def plein_ecran(self):
        u"Bascule en mode plein écran <-> mode normal."
        self.setWindowState(self.windowState()^Qt.WindowFullScreen)

    def closeEvent(self, event):
        self.activateWindow()
        self.showNormal()
        self.raise_()
        self.closing = True
        if not param.fermeture_instantanee: # pour des tests rapides
            try:
                if param.confirmer_quitter and not param._restart:
                    panel = self.onglets.onglet_actuel
                    test = hasattr(panel, 'canvas') and hasattr(panel.canvas, 'setUpdatesEnabled')
                    if test:
                        panel.canvas.setUpdatesEnabled(False)
                    reponse = QMessageBox.question(self, u'Quitter %s ?' %NOMPROG,
                                               u'Voulez-vous quitter %s ?' %NOMPROG,
                                               QMessageBox.Yes | QMessageBox.No,
                                               QMessageBox.Yes)
                    if test:
                        panel.canvas.setUpdatesEnabled(True)
                    if reponse != QMessageBox.Yes:
                        self.closing = False
                        event.ignore()
                        return

                self.gestion.sauver_preferences()
                # Enregistre sous le nom 'session-precedente', et non 'session'
                # (nom par défaut) pour pouvoir ouvrir la session précédente
                # même après le démarrage de WxGéométrie (session.tar.gz a alors
                # été remplacé par la sauvegarde automatique de la nouvelle session).
                self.gestion.sauver_session(nom='session-precedente')

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
                    QMessageBox.warning(self, u"Erreur lors de la fermeture du programme", "Impossible d'afficher l'erreur.")
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        if hasattr(self, "fenetre_sortie"):
            self.fenetre_sortie.close()
        print "On ferme !"


    def restart(self):
        param._restart = True
        self.close()