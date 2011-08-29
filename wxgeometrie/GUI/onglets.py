# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

##--------------------------------------##
#                  Onglets               #
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
from webbrowser import open_new_tab

#from PyQt4.QtGui import (QMainWindow, QApplication, QPlainTextEdit, QIcon, QColor, QPalette,
#                        QLabel, QWidget, QVBoxLayout, QMessageBox, QTextCursor)
#from PyQt4.QtCore import QSize, Qt


from PyQt4.QtGui import QTabWidget, QToolButton, QIcon, QMessageBox, QFileDialog, QDialog
from PyQt4.QtCore import Qt
import matplotlib.backend_bases as backend_bases

from .aide import About, Informations, Notes, Licence
from .animer import DialogueAnimation
from .contact import Contact
#from .dialogues_geometrie import EditerObjet, SupprimerObjet
from .fenetre_options import FenetreOptions
from .inspecteur import FenCode
from .nouvelles_versions import Gestionnaire_mises_a_jour
from .proprietes_feuille import ProprietesFeuille
from .proprietes_objets import Proprietes
from .wxlib import png
from . import dialogues_geometrie
from ..API.sauvegarde import FichierGEO, ouvrir_fichierGEO
from .. import param, modules, geolib
from ..param import NOMPROG
from ..pylib import print_error, debug, path2
from ..param.options import options as param_options


class Onglets(QTabWidget):
    def __init__(self, parent):
        self.parent = parent
        QTabWidget.__init__(self, parent)
        self.setStyleSheet("QTabBar {background:white}, QStackedWidget {background:white}")
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self.fermer_onglet)
#        palette = QPalette()
#        white = QColor(Qt.white)
#        palette.setColor(QPalette.Window, white)
#        palette.setColor(QPalette.Button, white)
#        palette.setColor(QPalette.WindowText, white)
#        self.setPalette(palette)

        ###############################
        # Creation de fonctions associees aux entrees du menu "Creer"
        self.creer = {}
        DG = dialogues_geometrie.__dict__
        dialogues = [(nom[8:], DG[nom]) for nom in DG.keys() if nom.startswith("Dialogue")]
        for dialogue in dialogues:
            def f(event = None, self = self, dialogue = dialogue[1]):
                self.creer_objet(dialogue)
            self.creer[dialogue[0]] = f
        ###############################

        #TODO: Ajouter un bouton "New Tab"
        newTabButton = QToolButton(self)
        self.setCornerWidget(newTabButton, Qt.TopRightCorner)
        newTabButton.setCursor(Qt.ArrowCursor)
        newTabButton.setAutoRaise(True)
        newTabButton.setIcon(QIcon(path2("images/newtab3.png")))
        #newTabButton.clicked.connect(self.newTab)
        newTabButton.setToolTip(u"Add page")

        self.gestionnaire_de_mises_a_jour = Gestionnaire_mises_a_jour(self)

        self._liste = [] # liste des onglets

        # Ajoute les differentes composantes :
        self.actualiser_liste_onglets()


        # adaptation du titre de l'application et du menu.
        self.currentChanged.connect(self.changer)
#        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.changer, self)
#        import fenetre_options
#        self.Bind(fenetre_options.EVT_OPTIONS_MODIFIED, self.OnOptionsModified)
        if self._liste:
            # affiche le titre et le menu du 1er onglet
            self.actualise_onglet(self._liste[0])
            self._liste[0].activer()


    def OnOptionsModified(self):
        self.actualiser_liste_onglets()
        for parametre in ('decimales', 'unite_angle', 'tolerance'):
            geolib.contexte[parametre] = getattr(param,  parametre)


#    def deplacer_onglet(self, i, j):
#        u"Déplacer un onglet de la position 'i' à la position 'j'."
#        if i != j:
#            panel = self._liste.pop(i)
#            self._liste.insert(j, panel)
#            self.removeTab(i)
#            self.insertTab(j, panel, panel.__titre__)
    def deplacer_onglet(self, i, j):
        u"Déplacer un onglet de la position 'i' à la position 'j'."
        if i != j:
            self.moveTab(i, j)



    def nouvel_onglet(self, panel, i = None):
        u"Ajouter un nouvel onglet à la position 'i'."
        if i is None:
            self._liste.append(panel)
            self.addTab(panel, panel.__titre__)
        else:
            self._liste.insert(i, panel)
            self.insertTab(i, panel, panel.__titre__)
        setattr(self, panel.module._nom_, panel)

    def fermer_onglet(self, i):
        u"Fermer l'onglet situé en position 'i'."
        panel = self._liste.pop(i)
        delattr(self, panel.module._nom_)
        self.deleteTab(i)

    def deleteTab(self, i):
        tab = self.widget(i)
        self.removeTab(i)
        tab.close()
        tab.deleteLater()

    def changer(self, index):
        if index != -1:
            onglet = self._liste[index]
            self.actualise_onglet(onglet)
            # Actions personnalisées lors de la sélection
            onglet.activer()
    #        wx.CallLater(10, onglet.activer)


    def actualise_onglet(self, onglet):
        self.parent.setMenuBar(onglet.module._menu_(onglet)) # change le menu de la fenetre
        onglet.changer_titre() # change le titre de la fenetre
        ##bar = self.parent.menuBar()

#        if param.plateforme == "Windows":
#            if onglet.canvas is not None:
#                onglet.canvas.execute_on_idle(onglet.canvas.graph.restaurer_dessin)


    def onglet(self, nom):
        u"nom : nom ou numéro de l'onglet."
        if type(nom) == int:
            return self._liste[nom]
        return getattr(self, nom, None)


    @property
    def onglet_actuel(self):
        if self._liste:
            return self._liste[self.currentIndex()]

    def onglet_suivant(self, event):
        self.setCurrentIndex((self.currentIndex() + 1) % self.count())

    def __nonzero__(self):
        return bool(self._liste)

    def __iter__(self):
        return iter(self._liste)

    def changer_onglet(self, onglet):
        u"onglet : l'onglet proprement dit, ou son nom, ou son numéro."
        if type(onglet) in (str, unicode):
            onglet = self._liste.index(getattr(self, onglet.lower()))
        elif type(onglet) not in (int, long):
            onglet = self._liste.index(onglet)
        self.setCurrentIndex(onglet)


    def actualiser_liste_onglets(self,  evt = None):
        # Tous les onglets situés avant 'pos' sont classés
        pos = 0
        for nom in param.modules:
            module = modules.importer_module(nom)
            if module is not None:
                absent = True
                for i, panel in enumerate(self._liste[pos:]):
                    if panel.module is module:
                        # Déplacer le panel en position pos
                        self.deplacer_onglet(pos + i, pos)
                        # InsertPage(self, n, page, text, select, imageId)
                        # RemovePage(self, n)
                        # Mettre à jour la position
                        pos += 1
                        absent = False
                if absent:
                    # Créer un onglet en position pos
                    self.nouvel_onglet(module._panel_(self, module), pos)
                    # AddPage(self, page, text, select, imageId) uhk
                    # Mettre à jour la position
                    pos += 1
        # Supprimer tous les onglets qui sont situés après pos
        while pos < self.count():
            self.fermer_onglet(pos)


#####################################################################


    filtres_save = (u"Fichiers " + NOMPROG + u" (*.geo);;"
                   u"Fichiers " + NOMPROG + u" compressés (*.geoz);;"
                   u"Tous les fichiers (*.*)")

    def NewFile(self):
        self.onglet_actuel.creer_feuille()


    def SaveFile(self):
        actuelle = self.onglet_actuel.feuille_actuelle # feuille de travail courante
        if actuelle and actuelle.sauvegarde["nom"]:
            self.onglet_actuel.sauvegarder()
        else:
            self.SaveFileAs()


    def SaveFileAs(self):
        actuelle = self.onglet_actuel.feuille_actuelle # feuille de travail courante
        if actuelle and actuelle.sauvegarde["nom"]:
            fichier = actuelle.sauvegarde["nom"] # le nom par defaut est le nom précédent
            dir = actuelle.sauvegarde["repertoire"]
        else:
            fichier = ""
            if param.rep_save is None:
                dir = param.repertoire
            else:
                dir = param.rep_save
        filtre = (u"Fichiers %s compressés (*.geoz)" if param.compresser_geo else u'')
        path, filtre = QFileDialog.getSaveFileNameAndFilter(self, u"Enregistrer sous ...",
                                   os.path.join(dir, fichier), self.filtres_save, filtre)

        if path:
            # Sauvegarde le répertoire pour la prochaine fois
            param.rep_save = os.path.dirname(path)
            if param.rep_open is None:
                param.rep_open = param.rep_save
            if param.rep_export is None:
                param.rep_export = param.rep_save

            self.onglet_actuel.sauvegarder(path)


    def OpenFile(self, detecter_module=True):
        if param.rep_open is None:
            dir = param.repertoire
        else:
            dir = param.rep_open
        filtre = (u"Fichiers %s compressés (*.geoz)" if param.compresser_geo else u'')
        paths, filtre = QFileDialog.getOpenFileNamesAndFilter(self, u"Choisissez un fichier", dir,
                                             self.filtres_save, filtre)
        if paths:
            # Sauvegarde le répertoire pour la prochaine fois
            param.rep_open = os.path.dirname(paths[0])
            if param.rep_save is None:
                param.rep_save = param.rep_open
            if param.rep_export is None:
                param.rep_export = param.rep_open

            for path in paths:
                if detecter_module: # on detecte dans quel onglet le fichier doit etre ouvert
                    self.ouvrir(path)
                else: # on l'ouvre dans l'onglet actuellement ouvert
                    self.onglet_actuel.ouvrir(path) # ouvre tous les fichiers selectionnes



    def OpenFileHere(self):
        u"""Ouvrir le fichier dans le module courant.

        Par défaut, sinon, le fichier est ouvert dans le module qui l'a crée."""
        self.OpenFile(detecter_module = False)


    def ouvrir(self, fichier, en_arriere_plan = False):
        u"""Ouvre un fichier dans l'onglet adéquat.

        'fichier' est soit l'adresse d'un fichier .geo, soit une instance de FichierGEO.
        """
        if not isinstance(fichier, FichierGEO):
            fichier, message = ouvrir_fichierGEO(fichier)
            self.parent.message(message)
        module = self.onglet(fichier.module)
        if module is not None:
            if not en_arriere_plan:
                self.changer_onglet(module) # affiche cet onglet
            module.ouvrir(fichier) # charge le fichier dans le bon onglet
            #print_error()
        else:
            self.parent.message(u"Impossible de déterminer le module adéquat.")


    def ExportFile(self, lieu = None, sauvegarde = False, exporter = True):
        u"""Le paramètre sauvegarde indique qu'il faut faire une sauvegarde simultanée.
        (attention, on ne vérifie pas que le fichier .geo n'existe pas !).
        """

        actuelle = self.onglet_actuel.feuille_actuelle # feuille de travail courante
        if actuelle and actuelle.sauvegarde["export"]:
            dir, fichier = os.path.split(actuelle.sauvegarde["export"]) # on exporte sous le même nom qu'avant par défaut
        elif actuelle and actuelle.sauvegarde["nom"]:
            fichier = actuelle.sauvegarde["nom"] # le nom par defaut est le nom de sauvegarde
            dir = actuelle.sauvegarde["repertoire"]
        else:
            fichier = ""
            if param.rep_export is None:
                dir = param.repertoire
            else:
                dir = param.rep_export


        lieu = lieu or self.onglet_actuel.nom # par defaut, le lieu est l'onglet courant

        description_formats = sorted(backend_bases.FigureCanvasBase.filetypes.iteritems())
        formats_supportes = sorted(backend_bases.FigureCanvasBase.filetypes)


        def format(typ, description):
            return typ.upper() + ' - ' + description + ' (.' + typ + ')'
        filtres = ';;'.join(format(k, v) for k, v in description_formats)

        format_par_defaut = ''
        if '.' in fichier:
            format_par_defaut = fichier.split('.', 1)[1]

        if format_par_defaut not in formats_supportes:
            format_par_defaut = 'png'

        for filtre in filtres.split(';;'):
            if filtre.endswith(format_par_defaut + ')'):
                break

        filtre = u'PNG - Portable Network Graphics (.png)'
        path, filtre = QFileDialog.getSaveFileNameAndFilter(self, u"Exporter l'image",
                                           os.path.join(dir, fichier), filtres,
                                           filtre)

        if not path:
            return # Quitte sans sauvegarder.

        # Sauvegarde le répertoire pour la prochaine fois
        param.rep_export = os.path.dirname(path)
        if param.rep_save is None:
            param.rep_save = param.rep_export
        if param.rep_open is None:
            param.rep_open = param.rep_export
        if sauvegarde:
            param.rep_save = param.rep_export

        # Check for proper extension
        if not any(path.lower().endswith(extension) for extension in formats_supportes):
            i = filtre.index('(')
            ext = filtre[i + 1:-1]
            path += ext

        try:
            if sauvegarde:
                geofile_name = path.rsplit('.', 1)[0] + ('.geoz' if param.compresser_geo else '.geo')
                self.onglet(lieu).sauvegarder(geofile_name)
            # Save Bitmap
            if exporter:
                self.onglet(lieu).exporter(path)
        except:
            print_error()
            self.parent.message("Erreur lors de l'export.")
        return path


    def ExportAndSaveFile(self, lieu=None):
        self.ExportFile(lieu = lieu, sauvegarde = True)


    def CloseFile(self):
        self.onglet_actuel.fermer_feuille()


    def PageSetup(self):
        self.a_venir()

    def Printout(self):
        self.a_venir()

    def a_venir(self):
        QMessageBox.information(self, u"A venir !", u"Fonctionnalité non présente pour l'instant !")

    def supprimer(self):
        canvas = self.onglet_actuel.canvas
        dlg = SupprimerObjet(self)
        if (dlg.ShowModal() == wx.ID_OK):
            with canvas.geler_affichage(actualiser=True, sablier=True):
                for selection in dlg.GetValueString():
                    try:
                        # Il est normal que des erreurs soient renvoyées
                        # si un objet dépendant d'un autre est déjà supprimé.
                        objet = selection.split()[1]
                        canvas.feuille_actuelle.objets[objet].supprimer()
                    except Exception:
                        print_error()
                canvas.feuille_actuelle.interprete.commande_executee()
        dlg.Destroy()


    def editer(self):
        feuille = self.onglet_actuel.feuille_actuelle
        if feuille:
            objets = []
            dlg = EditerObjet(self)
            val = dlg.ShowModal()
            if val == wx.ID_OK:
                objets = [feuille.objets[selection.split()[1]] for selection in dlg.GetValueString()]
            dlg.Destroy()

            if objets:
                win = Proprietes(self, objets)
                win.show()
                def fermeture(event, win = win):
                    win.Unbind(wx.EVT_CLOSE)
                    win.close()
                    self.editer()
                win.Bind(wx.EVT_CLOSE, fermeture)
        #self.parent.Raise()


    def creer_objet(self, classe):
        canvas = self.onglet_actuel.canvas
        dl = classe(self)
        while dl.affiche() == QDialog.Accepted:
            try:
                canvas.executer(dl.commande(), parser = True)
                break
            except NameError:
                print_error()
                canvas.message(u'Erreur : nom déjà utilisé ou nom réservé.')
            except:
                print_error()
                canvas.message(u'Erreur : paramètres incorrects.')


    def Animer(self):
        d = DialogueAnimation(self)
        d.show()

    def Histo(self):
        contenu = self.onglet_actuel.feuille_actuelle.sauvegarder()
        h = FenCode(self, u"Contenu interne de la feuille", contenu, self.executer_dans_feuille_courante)
        h.show()

    def executer_dans_feuille_courante(self, instructions):
        self.onglet_actuel.creer_feuille()
        self.onglet_actuel.feuille_actuelle.charger(instructions)

    def Proprietes(self):
        actuelle = self.onglet_actuel.feuille_actuelle # feuille courante
        ProprietesFeuille(self, actuelle).show()

    def Options(self):
        FenetreOptions(self, param_options).show()


    def Aide(self):
        open_new_tab(path2("%/doc/help.htm"))
#        aide = Help(self, path2("%/doc/help.htm"))
#        aide.show()

    #~ def Verifier_version(self, event):
        #~ # from GUI.nouvelles_versions import verifier_version # à deplacer ?
        #~ # verifier_version(self)
        #~ self.gestionnaire_de_mises_a_jour.verifier_version()

    def Notes(self):
        self.notes = Notes(self)
        self.notes.show()

    def Licence(self):
        self.licence = Licence(self)
        self.licence.show()

    def Contacter(self):
        self.formulaire = Contact(self)
        self.formulaire.show()

    def About(self):
        dialog = About(self)
        dialog.exec_()

    def Informations(self):
        dialog = Informations(self)
        dialog.show()