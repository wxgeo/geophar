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
import wx
import matplotlib.backend_bases as backend_bases

from .inspecteur import FenCode
from .aide import Help, About, Informations
from .dialogues_geometrie import EditerObjet, SupprimerObjet
from .nouvelles_versions import Gestionnaire_mises_a_jour
from . import dialogues_geometrie
from ..API.sauvegarde import FichierGEO, ouvrir_fichierGEO
from .proprietes_objets import Proprietes
from .. import param, modules, geolib
from ..pylib import print_error, debug, path2
from .animer import DialogueAnimation
from .proprietes_feuille import ProprietesFeuille
from ..param.options import options as param_options
from .fenetre_options import FenetreOptions
from .contact import Contact

class Onglets(wx.Notebook):
    def __init__(self, parent, id):
        self.parent = parent
        wx.Notebook.__init__(self, parent, id, style=wx.NB_TOP)

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

        self.gestionnaire_de_mises_a_jour = Gestionnaire_mises_a_jour(self)

        self._liste = [] # liste des onglets

        # Ajoute les differentes composantes :
        self.actualiser_liste_onglets()
##        for nom in param.modules:
##            module = modules.importer_module(nom)
##            if module is not None:
##                panel = module._panel_(self)  # ex: panel = Geometre(self)
##                setattr(self, nom, panel)       #     self.geometre = panel
##                panel.menu = module._menu_(panel)   #     menu = GeometreMenuBar(panel)
##                module._menu_(panel)   #     menu = GeometreMenuBar(panel)
##                self.nouvel_onglet(panel)


        # adaptation du titre de l'application et du menu.
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.changer, self)
        import fenetre_options
        self.Bind(fenetre_options.EVT_OPTIONS_MODIFIED, self.OnOptionsModified)
        if self._liste:
            # affiche le titre et le menu du 1er onglet
            self.actualise_onglet(self._liste[0])
            self._liste[0].activer()


    def OnOptionsModified(self, evt = None):
        self.actualiser_liste_onglets()
        for parametre in ('decimales', 'unite_angle', 'tolerance'):
            geolib.contexte[parametre] = getattr(param,  parametre)
        self.parent.actualiser_intervalle_autosave()


    def deplacer_onglet(self, i, j):
        u"Déplacer un onglet de la position 'i' à la position 'j'."
        if i != j:
            panel = self._liste.pop(i)
            self._liste.insert(j, panel)
            self.RemovePage(i)
            self.InsertPage(j, panel, panel.__titre__)

    def nouvel_onglet(self, panel, i = None):
        u"Ajouter un nouvel onglet à la position 'i'."
        if i is None:
            self._liste.append(panel)
            self.AddPage(panel, panel.__titre__)
        else:
            self._liste.insert(i, panel)
            self.InsertPage(i, panel, panel.__titre__)
        setattr(self, panel.module._nom_, panel)

    def fermer_onglet(self, i):
        u"Fermer l'onglet situé en position 'i'."
        panel = self._liste.pop(i)
        delattr(self, panel.module._nom_)
        self.DeletePage(i)

    def changer(self, event):
        event.Skip()
        # onglet selectionné:
        onglet = self._liste[event.GetSelection()]
        self.actualise_onglet(onglet)
        # Actions personnalisées lors de la sélection
        wx.CallLater(10, onglet.activer)



    def actualise_onglet(self, onglet):
        self.parent.SetMenuBar(onglet.menu) # change le menu de la fenetre
        onglet.changer_titre() # change le titre de la fenetre
        if param.plateforme == "Windows":
            if onglet.canvas is not None:
                onglet.canvas.execute_on_idle(onglet.canvas.graph.restaurer_dessin)


    def onglet(self, nom):
        u"nom : nom ou numéro de l'onglet."
        if type(nom) == int:
            return self._liste[nom]
        return getattr(self, nom, None)


    @property
    def onglet_actuel(self):
        if self._liste:
            return self._liste[self.GetSelection()]

    def onglet_suivant(self, event):
        self.AdvanceSelection()

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
        self.SetSelection(onglet)


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
        while pos < self.GetPageCount():
            self.fermer_onglet(pos)


#####################################################################




    def NewFile(self, event = None):
        self.onglet_actuel.creer_feuille()


    def SaveFile(self, event = None):
        actuelle = self.onglet_actuel.feuille_actuelle # feuille de travail courante
        if actuelle and actuelle.sauvegarde["nom"]:
            self.onglet_actuel.sauvegarder()
        else:
            self.SaveFileAs(event)


    def SaveFileAs(self, event = None):
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
        if param.compresser_geo:
            wildcard = u"Fichiers WxGéométrie compressés(*.geoz)|*.geoz|Fichiers WxGéométrie (*.geo)|*.geo|Tous les fichiers (*.*)|*.*"
        else:
            wildcard = u"Fichiers WxGéométrie (*.geo)|*.geo|Fichiers WxGéométrie compressés(*.geoz)|*.geoz|Tous les fichiers (*.*)|*.*"
        dlg = wx.FileDialog(
            self, message = u"Enregistrer sous ...", defaultDir=dir,
            defaultFile=fichier, wildcard = wildcard, style=wx.SAVE | wx.OVERWRITE_PROMPT | wx.CHANGE_DIR
            )
        # dlg.SetFilterIndex(0)   # inutile (par defaut, la valeur est 0).

        if dlg.ShowModal() == wx.ID_OK:
            param.rep_save = os.getcwd()
            if param.rep_open is None:
                param.rep_open = param.rep_save
            if param.rep_export is None:
                param.rep_export = param.rep_save
            os.chdir(param.repertoire)
            path = dlg.GetPath()
            self.onglet_actuel.sauvegarder(path)

        dlg.Destroy()



    def OpenFile(self, event = None, detecter_module = True):
        # Attention :
        # "This dialog is set up to change the current working directory to the path chosen."
        # on enregistre donc le nouveau getcwd() - "repertoire_ouverture_fichiers = os.getcwd()", pour restaurer ensuite l'ancien
        if param.rep_open is None:
            dir = param.repertoire
        else:
            dir = param.rep_open
        dlg = wx.FileDialog(
            self, message = u"Choisissez un fichier", defaultDir=dir,
            defaultFile="", wildcard = u"Fichiers WxGéométrie (*.geo)|*.geo|Fichiers WxGéométrie compressés(*.geoz)|*.geoz|Tous les fichiers (*.*)|*.*", style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )

        # Show the dialog and retrieve the user response. If it is the OK response,
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            param.rep_open = os.getcwd()
            if param.rep_save is None:
                param.rep_save = param.rep_open
            if param.rep_export is None:
                param.rep_export = param.rep_open
            os.chdir(param.repertoire)
            # This returns a Python list of files that were selected.
            paths = dlg.GetPaths()
            for path in paths:
                if detecter_module: # on detecte dans quel onglet le fichier doit etre ouvert
                    self.ouvrir(path)
                else: # on l'ouvre dans l'onglet actuellement ouvert
                    self.onglet_actuel.ouvrir(path) # ouvre tous les fichiers selectionnes

        dlg.Destroy()



    def OpenFileHere(self, event = None):
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


    def ExportFile(self, event = None, lieu = None, sauvegarde = False, exporter = True):
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

        format_par_defaut = ''
        if '.' in fichier:
            format_par_defaut = fichier.split('.', 1)[1]

        if format_par_defaut not in formats_supportes:
            format_par_defaut = 'png'

        def format(typ, description):
            return typ.upper() + ' - ' + description + ' (.' + typ + ')|*.' + typ
        filtre = '|'.join(format(k, v) for k, v in description_formats)

        dlg1 = wx.FileDialog(
                self,
                u"Exporter l'image", dir, fichier,
                filtre,
                wx.SAVE | wx.OVERWRITE_PROMPT | wx.CHANGE_DIR
                )

        dlg1.SetFilterIndex(formats_supportes.index(format_par_defaut))
        # print formats_supportes.index(format_par_defaut), format_par_defaut, fichier

        if "." in fichier:
            ext = fichier.rsplit(".",1)[1]
            try:
                dlg1.SetFilterIndex(formats_supportes.index(ext))
            except ValueError:
                debug("L'extension n'est pas dans la liste.")
        try:
            while 1:
                if dlg1.ShowModal() == wx.ID_OK:
                    param.rep_export = os.getcwd()
                    if param.rep_save is None:
                        param.rep_save = param.rep_export
                    if param.rep_open is None:
                        param.rep_open = param.rep_export
                    if sauvegarde:
                        param.rep_save = param.rep_export
                    os.chdir(param.repertoire)
                    FileName = dlg1.GetPath()
                    filename = FileName.lower()
                    # Check for proper exension
                    if not any(filename.endswith(extension) for extension in formats_supportes):
                        FileName += "." + formats_supportes[dlg1.GetFilterIndex()]
                        filename = FileName.lower()

                        #~ dlg2 = wx.MessageDialog(self, u"L'extension du fichier\n"
                        #~ u'doit être\n'
                        #~ u'png, svg, ps, jpg, bmp, xpm ou eps',
                          #~ u'Nom de fichier incorrect', wx.OK | wx.ICON_ERROR)
                        #~ try:
                            #~ dlg2.ShowModal()
                        #~ finally:
                            #~ dlg2.Destroy()
                    #~ else:
                        #~ break # now save file
                    break
                else: # exit without saving
                    return False
        finally:
            dlg1.Destroy()

        try:
            if sauvegarde:
                GeoFileName = '.'.join(FileName.split('.')[:-1]) + ('.geoz' if param.compresser_geo else '.geo')
                self.onglet(lieu).sauvegarder(GeoFileName)
            # Save Bitmap
            if exporter:
                self.onglet(lieu).exporter(FileName)
        except:
            print_error()
            self.parent.message("Erreur lors de l'export.")
        return FileName

        #return self.onglet(lieu).exporter(FileName)


    def ExportAndSaveFile(self, event = None, lieu = None):
        self.ExportFile(event = event, lieu = lieu, sauvegarde = True)


    def CloseFile(self, event = None):
        self.onglet_actuel.fermer_feuille()


    def PageSetup(self, event = None):
        self.a_venir()

    def Printout(self, event = None):
        self.a_venir()

    def a_venir(self, event = None):
        dlg = wx.MessageDialog(self, u"Fonctionnalité non présente pour l'instant !", u"A venir !", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()



    def CloseWindow(self, event):
        self.parent.Close(True)





    def supprimer(self, event = None):
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


    def editer(self, event = None):
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
                win.Show(True)
                def fermeture(event, win = win):
                    win.Unbind(wx.EVT_CLOSE)
                    win.Close()
                    self.editer()
                win.Bind(wx.EVT_CLOSE, fermeture)
        #self.parent.Raise()


    def creer_objet(self, classe):
        dl = classe(self)
        # this does not return until the dialog is closed.
        while 1:
            canvas = self.onglet_actuel.canvas
            resultat = dl.affiche()
            if resultat == wx.ID_OK:
                try:
                    canvas.executer(dl.commande(), parser = True)
                    break
                except NameError:
                    print_error()
                    canvas.message(u'Erreur : nom déjà utilisé ou nom réservé.')
                except:
                    print_error()
                    canvas.message(u'Erreur : paramètres incorrects.')
            else:
                break
        dl.Destroy()

    def Animer(self, event):
        d = DialogueAnimation(self)
        d.CenterOnParent(wx.BOTH)
        d.Show(True)

    def Histo(self, event):
        contenu = self.onglet_actuel.feuille_actuelle.sauvegarder()
        h = FenCode(self, u"Contenu interne de la feuille", contenu, self.executer_dans_feuille_courante)
        h.Show(True)

    def executer_dans_feuille_courante(self, instructions):
        self.onglet_actuel.creer_feuille()
        self.onglet_actuel.feuille_actuelle.charger(instructions)

    def Proprietes(self, event):
        actuelle = self.onglet_actuel.feuille_actuelle # feuille courante
        ProprietesFeuille(self, actuelle).Show()

    def Options(self, evt = None):
        FenetreOptions(self, param_options).Show()


    def Aide(self, event):
        aide = Help(self, path2("%/doc/help.htm"))
        aide.Show(True)

    #~ def Verifier_version(self, event):
        #~ # from GUI.nouvelles_versions import verifier_version # à deplacer ?
        #~ # verifier_version(self)
        #~ self.gestionnaire_de_mises_a_jour.verifier_version()

    def Notes(self, event):
        f = open(path2("%/doc/notes.txt"), "r")
        msg = f.read().decode("utf8")
        f.close()
        msg = msg.replace(u"WxGeometrie", u"WxGéométrie version " + param.version, 1)
        dlg = wx.lib.dialogs.ScrolledMessageDialog(self, msg, "Notes de version")
        dlg.ShowModal()

    def Licence(self, event):
        f = open(path2("%/doc/license.txt"), "r")
        msg = f.read().decode("utf8")
        f.close()
        msg = msg.replace(u"WxGeometrie", u"WxGéométrie version " + param.version, 1)
        dlg = wx.lib.dialogs.ScrolledMessageDialog(self, msg, "Licence")
        dlg.ShowModal()

    def Contacter(self, event):
        formulaire = Contact(self)
        formulaire.Show()
        #~ val = dialog.ShowModal()
        #~ if val == wx.ID_OK:
            #~ dialog.rapporter()
        #~ dialog.Destroy()


    def About(self, event):
        dialog = About(self)
        dialog.ShowModal()
        dialog.Destroy()

    def Informations(self, event):
        dialog = Informations(self)
        dialog.ShowModal()
        dialog.Destroy()
