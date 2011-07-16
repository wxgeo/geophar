# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                   Menu                                   #
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


from operator import attrgetter
from functools import partial

import wx



#-----------------------
#       Menus
#-----------------------


class RSSMenu(wx.Menu): # parent : wxgeometrie (Frame principal)
    u"Menu dynamique."
    def __init__(self, parent, titre = "", liste = None, fonction = None, aide = ""):
        wx.Menu.__init__(self)
        self.parent = parent
        self.table_ids = {}
        self.fonction = None
        self.titre = titre
        self.update(liste, fonction, aide)

    def update(self, liste = None, fonction = None, aide = None):
        if fonction is not None:
            self.fonction = fonction
        if aide is not None:
            self.aide = aide
        self.liste = liste or []

        for id in self.table_ids.keys():
            if self.fonction: # bof: pas super precis (si on rajoute une fonction entre temps, erreur)
                self.parent.parent.Unbind(wx.EVT_MENU, id = id)
            self.Delete(id)
        self.table_ids = {}

        for i in xrange(len(self.liste)):
            id = wx.NewId()
            self.table_ids[id] = i
            self.Append(id, self.liste[i], self.aide)
            if self.fonction:
                self.parent.parent.Bind(wx.EVT_MENU, self.gerer_evenement, id = id)


    def gerer_evenement(self, event): # rajoute a l'evenement la propriete nom_menu, avant de le rediriger.
        event.numero = self.table_ids[event.GetId()]
        self.fonction(event)




class Menu(wx.Menu):
    u"Remplace la classe wx.Menu."

    def __init__(self, menubar, liste):
        wx.Menu.__init__(self)
        IDEM = True
        self.parent = menubar.parent
        self.table_ids = {}
        for contenu in liste:
            id = wx.NewId() # pour être sûr que 2 menus (dans 2 modules différents) n'auront pas le même id.

            if not contenu:
                self.AppendSeparator()

            elif isinstance(contenu, RSSMenu):
                self.AppendMenu(id, "&" + contenu.titre, contenu)

            else:

                if len(contenu) == 1: # menus predefinis
                    contenu = menubar.menus[contenu[0]]

                self.table_ids[id] = contenu
                if isinstance(contenu[1], (list, tuple)): # le menu contient un sous-menu
                    menu = Menu(menubar, contenu[1:])
                    self.AppendMenu(id, "&" + contenu[0], menu)

                else:
                    if not contenu[1]:
                        contenu[1] = ""
                    # 0->titre, 1->description, 2->raccourci, 3->fonction associee[, 4->cocher ou non]
                    titre = "&" + contenu[0]
                    if contenu[2]:
                        titre += "\t" + contenu[2]
                    if len(contenu) == 5:   # le menu contient une case a cocher
                        self.Append(id, titre, contenu[1], wx.ITEM_CHECK)
                        if contenu[4] == IDEM:
                            contenu[4] = contenu[3]
                        #elif isinstance(contenu[4], basestring):
                        #    def f(self = menubar):
                        #        return getattr(self.canvas
                        #    contenu[4] = f
                        self.Check(id, contenu[4]())
                    else:                   # cas classique
                        self.Append(id, titre, contenu[1])
                    if contenu[3]:
                        self.parent.parent.Bind(wx.EVT_MENU, self.gerer_evenement, id = id)


    def gerer_evenement(self, event): # rajoute a l'evenement la propriete nom_menu, avant de le rediriger.
        contenu = self.table_ids[event.GetId()]
        event.nom_menu = contenu[0]
        contenu[3](event)





class MenuBar(wx.MenuBar):
    u"""Remplace la classe wx.MenuBar pour créer une barre de menu propre à chaque module.

    La méthode de base est 'ajouter(self, *menu)', où menu est une liste.
    Exemple1:
    menu =  ["Outils",
                ["Options", "Parametres du programme", "Ctrl+O", fonction1],
                ["Memoriser le resultat", "Copie le resultat du calcul dans le presse-papier", None, fonction2],
                None,
                ["Autres",
                    ["Rubrique 1", None, "Alt+Ctrl+R", fonction3],
                    ["Rubrique 2", "Rubrique non active pour l'instant", None, None]]]
    Exemple2: ["Infos", ["Afficher les infos", "Affichage des infos en temps reel", "Ctrl+I", fonction1, fonction2]]
    La presence de deux fonctions (eventuellement identiques) indique qu'il s'agit d'un menu "cochable".
    L'etat (coché ou non coché) est déterminé par la valeur renvoyée par la fonction 'fonction2'.

    Note: Pour un menu moins standard, on peut toujours utiliser directement wx.MenuBar.
    """

    def ajouter(self, *contenu):
        if isinstance(contenu, RSSMenu):
            self.Append(contenu, "&" + contenu.titre)
        else:
            if len(contenu) == 1: # menus predefinis
                contenu = self.menus[contenu[0]]
            menu = Menu(self, contenu[1:])
            self.Append(menu, "&" + contenu[0])


    def actualiser(self, event):
        u"Met à jour le menu en actualisant l'état des menus contenant une case à cocher."
        menu = event.GetMenu()
        if hasattr(menu, "table_ids"):
            for item in menu.GetMenuItems():
                if item.IsCheckable():
                    item.Check(menu.table_ids[item.GetId()][4]())


    def __init__(self, panel = None, *contenu): # parent : wxgeometrie (Frame principal)
        wx.MenuBar.__init__(self)
        self.panel = panel
        self.parent = panel.parent
        self.canvas = panel.canvas
        self.fenetre = self.parent.parent
##        self.historique = panel.historique
##        self.commande = panel.commande

        def canparam(parametre):
            return partial(attrgetter(parametre), self.canvas)
        IDEM = True
        # Menus predefinis:
        self.menus = {

"nouveau":  [u"Nouveau", u"Créer un nouveau fichier.", u"Ctrl+N", self.parent.NewFile],
"ouvrir":   [u"Ouvrir", u"Ouvrir un fichier.", u"Ctrl+O", self.parent.OpenFile],
"ouvrir ici":   [u"Ouvrir ici", u"Essayer d'ouvrir le fichier dans le module courant.", u"Alt+Ctrl+O", self.parent.OpenFileHere],
"enregistrer":  [u"Enregistrer", u"Enregistrer le document.", u"Ctrl+S", self.parent.SaveFile],
"enregistrer_sous":  [u"Enregistrer sous...", u"Enregistrer le document sous un nouveau nom.", u"Alt+Ctrl+S", self.parent.SaveFileAs],
"exporter": [u"Exporter...", u"Exporter l'image.", u"Ctrl+E", self.parent.ExportFile],
"exporter&sauver": [u"Exporter et sauver", u"Exporter l'image, et sauvegarder le document.", u"Alt+Ctrl+E", self.parent.ExportAndSaveFile],
"mise en page": [u"Paramètres d'impression", u"Régler les paramètres d'impression.", None, self.parent.PageSetup],
"imprimer": [u"Imprimer", u"Imprimer la figure géométrique courante.", u"Ctrl+P", self.parent.Printout],
"proprietes": [u"Propriétés", u"Modifier les informations relatives au document", None, self.parent.Proprietes],
"fermer":   [u"Fermer", u"Fermer la feuille courante.", u"Ctrl+W", self.parent.CloseFile],
"quitter":  [u"Quitter", u"Fermer le programme.", u"Alt+F4", self.parent.CloseWindow],



"onglet":   [u"Onglet suivant", u"Changer d'onglet.", u"Ctrl+TAB", self.parent.onglet_suivant],
"debug":    [u"Déboguer", u"Déboguer le programme (afficher les erreurs, ...).", None, self.fenetre.mode_debug, self.fenetre.mode_debug],
"ligne_commande":    [u"Afficher la ligne de commande", u"Afficher la ligne de commande.", None, self.fenetre.afficher_ligne_commande, self.fenetre.afficher_ligne_commande],
"options":  [u"Options", u"Paramètres du programme.", None, self.parent.Options],

"aide":     [u"Aide", u"Obtenir de l'aide sur le programme.", None, self.parent.Aide],
"notes":    [u"Notes de version", u"Consulter l'historique du projet.", None, self.parent.Notes],
"licence":    [u"Licence", u"Licence.", None, self.parent.Licence],
"infos":    [u"Configuration", u"Visualiser la configuration actuelle du système.", None, self.parent.Informations],
"contact":  [u"Signaler un problème", u"Envoyer un rapport de bug.", None, self.parent.Contacter],
"versions":    [u"Rechercher des mises à jour", u"Vérifier si une nouvelle version est disponible.", None, self.parent.gestionnaire_de_mises_a_jour.verifier_version],
"about":    [u"A propos...", u"WxGeometrie (c) 2005-2007 Nicolas Pourcelot - License : GPL version 2", None, self.parent.About],

        }


        self.menus["fichier"] = ["Fichier", ["nouveau"], ["ouvrir"], ["ouvrir ici"], ["enregistrer"], ["enregistrer_sous"], ["exporter"], ["exporter&sauver"], None, ["mise en page"], ["imprimer"], None, ["fermer"], ["quitter"]]


        self.menus["avance1"] = [u"Avancé", [u"historique"], [u"ligne_commande"], [u"debug"]]
        self.menus["avance2"] = [u"Avancé", [u"ligne_commande"], ["debug"]]

        self.menus["?"] = ["?", ["aide"], ["notes"], ["licence"], ["infos"], ["contact"], None, ["versions"], None, ["about"]]



        if self.canvas:
            self.menus.update({
"annuler":  [u"Annuler", u"Annuler la dernière action.", u"Ctrl+Z", self.panel.annuler],
"refaire":  [u"Refaire", u"Refait la dernière action annulée.", u"Ctrl+Y", self.panel.retablir],
"historique":   [u"Contenu interne de la feuille", u"Édition du contenu interne de la feuille.", u"Ctrl+H", self.parent.Histo],
"presse-papier": [u"Copier dans le presse-papier", u"Copier l'image dans le presse-papier.", None, self.canvas.Copy_to_Clipboard],
"barre_outils": [u"Afficher la barre d'outils", u"Afficher la barre d'outils de dessin en haut de la fenêtre.", None, self.panel.afficher_barre_outils, IDEM],
"console_geolib": [u"Afficher la ligne de commande", u"Afficher la ligne de commande en bas de la fenêtre.", None, self.panel.afficher_console_geolib, IDEM],
"repere":   [u"Afficher le repère", u"Afficher le repère et les axes.", None, self.canvas.gerer_parametre_afficher_axes, canparam("afficher_axes")],
"quadrillage":      [u"Afficher le quadrillage", u"Afficher le quadrillage.", None, self.canvas.gerer_parametre_afficher_quadrillage, canparam('afficher_quadrillage')],
"orthonorme":      [u"Repère orthonormé", u"Garder un repère toujours orthonormé.", None, self.canvas.gerer_parametre_orthonorme, canparam('orthonorme')],
"aimanter":      [u"Aimanter la grille", u"Forcer les points à se placer sur la grille.", None, self.canvas.gerer_parametre_grille_aimantee, canparam('grille_aimantee')],

"reperage": [u"Repérage",
                [u"par des points", u"Repérage par l'origine et 2 points.", None, self.canvas.repere_OIJ],
                [u"par des vecteurs", u"Repérage par l'origine et les 2 vecteurs de base.", None, self.canvas.repere_Oij],
                [u"par des valeurs numériques", u"Graduation numérique des axes", None, self.canvas.repere_011],
                [u"Personnaliser le repère", u"Personnaliser l'affichage du repère, et les graduations", "Ctrl+Alt+R", self.parent.creer["Reperage"]],
            ],

"quadrillages":  [u"Quadrillage",
                    [u"Par défaut", u"Rétablir le quadrillage par défaut.", None, self.canvas.quadrillage_defaut],
                    [u"Graduations intermédiaires", u"Ajouter un quadrillage intermédiaire entre deux graduations.", None, self.canvas.quadrillage_demigraduation],
                    [u"Graduations intermédiaires (coloré)", u"jouter un quadrillage intermédiaire entre deux graduations (version colorée).", None, self.canvas.quadrillage_demigraduation_colore],
                    [u"Papier millimétré", u"Créer un papier millimétré.", None, self.canvas.quadrillage_millimetre],
                    [u"Papier millimétré coloré", u"Créer un papier millimétré coloré.", None, self.canvas.quadrillage_millimetre_colore],
                ],

"zoom_texte": [u"Zoom texte",
                    [u"100 %", u"Afficher les textes à leur taille par défaut.", None, lambda event, self=self: self.canvas.zoom_text(event, 100)],
                    None,
                    [u"50 %", u"Réduire les textes à 50 % de leur taille.", None, lambda event, self=self: self.canvas.zoom_text(event, 50)],
                    [u"60 %", u"Réduire les textes à 60 % de leur taille.", None, lambda event, self=self: self.canvas.zoom_text(event, 60)],
                    [u"70 %", u"Réduire les textes à 70 % de leur taille.", None, lambda event, self=self: self.canvas.zoom_text(event, 70)],
                    [u"80 %", u"Réduire les textes à 80 % de leur taille.", None, lambda event, self=self: self.canvas.zoom_text(event, 80)],
                    [u"90 %", u"Réduire les textes à 90 % de leur taille.", None, lambda event, self=self: self.canvas.zoom_text(event, 90)],
                    None,
                    [u"120 %", u"Agrandir les textes à 120 % de leur taille.", None, lambda event, self=self: self.canvas.zoom_text(event, 120)],
                    [u"140 %", u"Agrandir les textes à 140 % de leur taille.", None, lambda event, self=self: self.canvas.zoom_text(event, 140)],
                    [u"160 %", u"Agrandir les textes à 160 % de leur taille.", None, lambda event, self=self: self.canvas.zoom_text(event, 160)],
                    [u"180 %", u"Agrandir les textes à 180 % de leur taille.", None, lambda event, self=self: self.canvas.zoom_text(event, 180)],
                    [u"200 %", u"Agrandir les textes à 200 % de leur taille.", None, lambda event, self=self: self.canvas.zoom_text(event, 200)],
               ],

"zoom_ligne": [u"Zoom ligne",
                    [u"100 %", u"Afficher les lignes à leur taille par défaut.", None, lambda event, self=self: self.canvas.zoom_line(event, 100)],
                    None,
                    [u"50 %", u"Réduire les lignes à 50 % de leur taille.", None, lambda event, self=self: self.canvas.zoom_line(event, 50)],
                    [u"60 %", u"Réduire les lignes à 60 % de leur taille.", None, lambda event, self=self: self.canvas.zoom_line(event, 60)],
                    [u"70 %", u"Réduire les lignes à 70 % de leur taille.", None, lambda event, self=self: self.canvas.zoom_line(event, 70)],
                    [u"80 %", u"Réduire les lignes à 80 % de leur taille.", None, lambda event, self=self: self.canvas.zoom_line(event, 80)],
                    [u"90 %", u"Réduire les lignes à 90 % de leur taille.", None, lambda event, self=self: self.canvas.zoom_line(event, 90)],
                    None,
                    [u"120 %", u"Agrandir les lignes à 120 % de leur taille.", None, lambda event, self=self: self.canvas.zoom_line(event, 120)],
                    [u"140 %", u"Agrandir les lignes à 140 % de leur taille.", None, lambda event, self=self: self.canvas.zoom_line(event, 140)],
                    [u"160 %", u"Agrandir les lignes à 160 % de leur taille.", None, lambda event, self=self: self.canvas.zoom_line(event, 160)],
                    [u"180 %", u"Agrandir les lignes à 180 % de leur taille.", None, lambda event, self=self: self.canvas.zoom_line(event, 180)],
                    [u"200 %", u"Agrandir les lignes à 200 % de leur taille.", None, lambda event, self=self: self.canvas.zoom_line(event, 200)],
               ],

"zoom_general": [u"Zoom général",
                    [u"Mode normal", u"Affichage par défaut.", None, self.canvas.zoom_normal],
                    [u"Léger grossissement", u"Textes et lignes (un peu) grossis.", None, self.canvas.zoom_large],
                    None,
                    [u"Mode vidéoprojecteur (grossissement)", u"Réglage adapté à la vidéoprojection (textes et lignes grossis).", None, self.canvas. zoom_videoprojecteur],
                    [u"Mode vidéoprojecteur accentué", u"Grossissement très important des objets.", None, self.canvas. zoom_videoprojecteur_large],
               ],

"fenetre":  [u"Réglage de la fenêtre", u"Réglage de la fenêtre d'affichage.", u"Alt+Ctrl+F", self.parent.creer["Fenetre"]],
"zoomer":   [u"Zoomer", u"Se rapprocher de la figure.", u"Ctrl+PGUP", self.canvas.zoom_in],
"dezoomer": [u"Dézoomer", u"S'éloigner de la figure.", u"Ctrl+PGDN", self.canvas.zoom_out],
"orthonormaliser":  [u"Orthonormaliser", u"Obtenir un repère orthonormal.", u"Alt+Ctrl+O", self.canvas.orthonormer],
"zoom_auto":  [u"Zoom intelligent", u"Réglage automatique de la fenêtre d'affichage.", u"Alt+Ctrl+A", self.canvas.zoom_auto],

"modifier": [u"Modifier", u"Editer les propriétes d'un ou plusieurs objets géométriques.", u"Ctrl+M", self.parent.editer],
"supprimer":[u"Supprimer", u"Supprime un ou plusieurs objets géométriques.", u"Ctrl+DEL", self.parent.supprimer],

"coder":    [u"Codage automatique", u"Codage automatique de la figure.", u"Alt+Ctrl+C", self.canvas.coder],
"decoder":  [u"Effacer le codage", u"Supprimer le codage de la figure.", u"Alt+Ctrl+D", self.canvas.decoder],
"traces":   [u"Effacer les traces", u"Supprimer toutes les traces de la figure (laisse les objets en mode Trace).", None, self.canvas.effacer_traces],
##"detecter": [u"Détecter les objets cachés", u"Signaler la présence des objets cachés au passage du pointeur.", None, self.canvas.detecter_caches, self.canvas.detecter_caches],
"detecter": [u"Afficher les objets cachés", u"Afficher en semi-transparent les objets cachés.", None, self.canvas.gerer_parametre_afficher_objets_caches, canparam('afficher_objets_caches')],
"nettoyer": [u"Supprimer les objets inutiles", u"Supprimer les objets cachés qui ne servent pas pour la construction.", None, self.canvas.nettoyer_feuille],
"animer":   [u"Créer une animation", u"Faire varier automatiquement une valeur.", None, self.parent.Animer],




"affichage": [u"Affichage", ["onglet"], None, ["barre_outils"], ["console_geolib"], None, ["repere"], ["quadrillage"], ["orthonorme"], ["reperage"], ["quadrillages"], None, ["zoom_texte"], ["zoom_ligne"], ["zoom_general"], None, ["fenetre"], ["zoomer"], ["dezoomer"], ["orthonormaliser"], [u"zoom_auto"]],

"autres":    [u"Autres actions", [u"coder"], [u"decoder"], [u"traces"], None, [u"detecter"], [u"nettoyer"], None, [u"animer"], [u"aimanter"]],


"creer":    [u"Créer",
                [u"Points",
                    [u"Point libre", u"Point quelconque.", u"Ctrl+L", self.parent.creer["Point"]],
                    [u"Milieu", u"Milieu d'un segment.", None, self.parent.creer["Milieu"]],
                    [u"Barycentre", u"Barycentre de n points.", u"Ctrl+B", self.parent.creer["Barycentre"]],
                    [u"Point final", u"Point défini par une relation vectorielle.", u"Ctrl+F", self.parent.creer["PointFinal"]],
                    [u"Point sur droite", u"Point appartenant à une droite.", None, self.parent.creer["GlisseurDroite"]],
                    [u"Point sur segment", u"Point appartenant à un segment.", None, self.parent.creer["GlisseurSegment"]],
                    [u"Point sur cercle", u"Point appartenant à un cercle.", None, self.parent.creer["GlisseurCercle"]],
                ],
                [u"Intersections",
                    [u"Intersection de deux droites", u"Point défini par l'intersection de deux droites (ou demi-droites, ou segments).", u"Ctrl+I", self.parent.creer["InterDroites"]],
                    [u"Intersection d'une droite et d'un cercle", u"Point défini par l'intersection d'une droite et d'un cercle.", u"Alt+Ctrl+I", self.parent.creer["InterDroiteCercle"]],
                    [u"Intersection de deux cercles", u"Point défini par l'intersection de deux cercles (ou arcs de cercles).", None,  self.parent.creer["InterCercles"]],
                ],
                [u"Centres",
                    [u"Centre d'un cercle", u"Centre d'un cercle.", None, self.parent.creer["Centre"]],
                    [u"Centre de gravité", u"Centre de gravite d'un triangle (intersection des médianes).", None, self.parent.creer["CentreGravite"]],
                    [u"Orthocentre", u"Orthocentre d'un triangle (intersection des hauteurs).", None, self.parent.creer["Orthocentre"]],
                    [u"Centre du cercle circonscrit", u"Centre du cercle circonscrit d'un triangle (intersection des médiatrices).", None, self.parent.creer["CentreCercleCirconscrit"]],
                    [u"Centre du cercle inscrit", u"Centre du cercle inscrit d'un triangle (intersection des bissectrices).", None, self.parent.creer["CentreCercleInscrit"]],
                ],
                [u"Lignes",
                    [u"Segment", u"Segment défini par deux points.", u"Ctrl+G", self.parent.creer["Segment"]],
                    None,
                    [u"Droite", u"Droite définie par deux points.", u"Ctrl+D", self.parent.creer["Droite"]],
                    [u"Demi-droite", u"Demi-droite définie par son origine et un autre point.", None, self.parent.creer["Demidroite"]],
                    None,
                    [u"Vecteur", u"Vecteur défini par deux points.", u"Ctrl+U", self.parent.creer["Vecteur"]],
                    [u"Vecteur libre", u"Vecteur défini par ses coordonnées.", None, self.parent.creer["VecteurLibre"]],
                    [u"Representant", u"Représentant d'origine donnée d'un vecteur.", None, self.parent.creer["Representant"]],
                    None,
                    [u"Parallèle", u"Parallèle à une droite passant par un point.", None, self.parent.creer["Parallele"]],
                    [u"Perpendiculaire", u"Perpendiculaire à une droite passant par un point.", None, self.parent.creer["Perpendiculaire"]],
                    [u"Médiatrice", u"Médiatrice d'un segment.", None, self.parent.creer["Mediatrice"]],
                    [u"Bissectrice", u"Bissectrice d'un angle.", None, self.parent.creer["Bissectrice"]],
                    [u"Tangente", u"Tangente à un cercle.", None, self.parent.creer["Tangente"]],
                ],
                [u"Cercles",
                    [u"Cercle défini par son centre et un point", u"Cercle défini par son centre et un autre point.", u"Ctrl+K", self.parent.creer["Cercle"]],
                    [u"Cercle défini par son centre et son rayon", u"Cercle défini par son centre et la valeur de son rayon.", u"Ctrl+R", self.parent.creer["CercleRayon"]],
                    [u"Cercle défini par un diamètre", u"Cercle défini par deux points diamétralement opposés.", None, self.parent.creer["CercleDiametre"]],
                    [u"Cercle défini par 3 points", u"Cercle défini par trois points.", None, self.parent.creer["CerclePoints"]],
                    None,
                    [u"Arc de centre donné", u"Arc de sens direct, défini par son centre, son origine, et un autre point.", None, self.parent.creer["ArcCercle"]],
                    [u"Arc défini par 3 points", u"Arc défini par ses extrémités, et un point intermédiaire.", None, self.parent.creer["ArcPoints"]],
                    [u"Arc orienté", u"Arc orienté, défini par ses extrémités, et un point intermédiaire.", None, self.parent.creer["ArcOriente"]],
                    [u"Demi-cercle", u"Demi-cercle de diamètre donné, de sens direct.", None, self.parent.creer["DemiCercle"]],
                    None,
                    [u"Disque", u"Disque circonscrit par un cercle donné.", None, self.parent.creer["Disque"]],
                ],
                [u"Polygones",
                    [u"Triangle", u"Triangle défini par ses sommets.", None, self.parent.creer["Triangle"]],
                    [u"Polygone quelconque", u"Polygone quelconque, défini par ses sommets.", None, self.parent.creer["Polygone"]],
                    [u"Parallélogramme", u"Parallélogramme de sens direct défini par 3 sommets.", None, self.parent.creer["Parallelogramme"]],
                    [u"Polygone régulier", u"Polygone régulier de sens direct défini par 2 sommets consécutifs.", None, self.parent.creer["PolygoneRegulier"]],
                    [u"Polygone régulier de centre donné", u"Polygone régulier défini son centre et un sommet.", None, self.parent.creer["PolygoneRegulierCentre"]],
                ],
                [u"Interpolation",
                    [u"Interpolation linéaire", u"Ligné brisée reliant les points désignés.", None, self.parent.creer["InterpolationLineaire"]],
                    [u"Interpolation quadratique", u"Courbe lisse (ie. de classe C1) reliant les points désignés.", None, self.parent.creer["InterpolationQuadratique"]],
                ],
                [u"Angles",
                    [u"Angle", u"Angle non orienté défini par trois points.", None, self.parent.creer["Angle"]],
                    [u"Angle orienté", u"Angle orienté défini par trois points.", None, self.parent.creer["AngleOriente"]],
                    [u"Angle orienté (non affiché)", u"Angle orienté (non affiché) défini par 2 vecteurs.", None, self.parent.creer["AngleVectoriel"]],
                    [u"Angle libre (non affiché)", u"Angle orienté (non affiché) défini par 2 vecteurs.", None, self.parent.creer["AngleLibre"]],

                ],
                [u"Transformations",
                    [u"Translation", u"Translation de vecteur donné.", None, self.parent.creer["Translation"]],
                    [u"Symétrie centrale", u"Symétrie par rapport à un point.", None, self.parent.creer["SymetrieCentrale"]],
                    [u"Symétrie axiale", u"Symétrie par rapport à une droite.", None, self.parent.creer["Reflexion"]],
                    [u"Rotation", u"Rotation de centre et d'angle donnés.", None, self.parent.creer["Rotation"]],
                    [u"Homothétie", u"Translation de vecteur donné.", None, self.parent.creer["Homothetie"]],
                    None,
                    [u"Image par transformation", u"Créer l'image d'un objet par une transformation géométrique.", None, self.parent.creer["Image"]],
                ],
                [u"Divers",
                    [u"Texte", u"Champ de texte.", None, self.parent.creer["Texte"]],
                    [u"Variable", u"Variable liée ou non.", None, self.parent.creer["Variable"]],
                ],
            ]

            })


        for item in contenu:
            self.ajouter(*item)

        self.parent.parent.Bind(wx.EVT_MENU_OPEN, self.actualiser)
