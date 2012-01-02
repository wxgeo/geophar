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

from PyQt4.QtGui import QMenu, QMenuBar, QKeySequence



#-----------------------
#       Menus
#-----------------------



class RSSMenu(QMenu): # parent : wxgeometrie (Frame principal)
    u"Menu dynamique."
    def __init__(self, titre='', liste=None, fonction=None, aide=''):
        QMenu.__init__(self, titre)
#        self.parent = parent
        self.fonction = None
#        self.titre = titre
#        self.setTitle(titre)
        self.update(liste, fonction, aide)

    def update(self, liste=None, fonction=None, aide=None):
        if fonction is not None:
            self.fonction = fonction
        if aide is not None:
            self.aide = aide
        self.liste = liste or []

        self.clear()

        for i, name in enumerate(self.liste):
            action = self.addAction(name, partial(self.fonction, i))
            action.setStatusTip(self.aide)



class Menu(QMenu):
    u"Remplace la classe QMenu."

    def __init__(self, menubar, titre, liste):
        QMenu.__init__(self, titre, menubar)
        IDEM = True
#        self.parent = menubar.parent
        self.aboutToShow.connect(self.actualiser)
        for contenu in liste:
            if not contenu:
                self.addSeparator()

            elif isinstance(contenu, RSSMenu):
                self.addMenu(contenu)

            else:

                if len(contenu) == 1: # menus predefinis
                    contenu = menubar.menus[contenu[0]]

                if isinstance(contenu[1], (list, tuple)): # le menu contient un sous-menu
                    menu = Menu(menubar, contenu[0], contenu[1:])
                    self.addMenu(menu)

                else:
                    if not contenu[1]:
                        contenu[1] = ''
                    # 0->titre, 1->description, 2->raccourci, 3->fonction associee[, 4->cocher ou non]
                    titre = contenu[0]
                    shortcut = (QKeySequence(contenu[2]) if contenu[2] else 0)
                    if contenu[3]:
                        ##action = self.addAction(titre, partial(contenu[3], contenu[0]), shortcut)
                        action = self.addAction(titre, contenu[3], shortcut)
                    else:
                        action = self.addAction(titre)
                    action.setStatusTip(contenu[1])
                    if len(contenu) == 5:   # le menu contient une case a cocher
                        if contenu[4] == IDEM:
                            contenu[4] = contenu[3]
                        action.setCheckable(True)
                        action.setChecked(contenu[4]())
                        action._test = contenu[4]

    def actualiser(self):
        for action in self.actions():
            if action.isCheckable():
                action.setChecked(action._test())



class MenuBar(QMenuBar):
    u"""Remplace la classe QMenuBar pour cr�er une barre de menu propre � chaque module.

    La m�thode de base est ``ajouter(self, *menu)``, o� menu est une liste.
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
    L'etat (coch� ou non coch�) est d�termin� par la valeur renvoy�e par la fonction 'fonction2'.

    Note: Pour un menu moins standard, on peut toujours utiliser directement QMenuBar.
    """

    def ajouter(self, *contenu):
        if isinstance(contenu, RSSMenu):
            contenu.setParent(self)
            self.addMenu(contenu)
        else:
            if len(contenu) == 1: # menus predefinis
                contenu = self.menus[contenu[0]]
            menu = Menu(self, contenu[0], contenu[1:])
            self.addMenu(menu)


    def __init__(self, panel = None, *contenu): # parent : wxgeometrie (Frame principal)
        QMenuBar.__init__(self)
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

"nouveau":  [u"Nouveau", u"Cr�er un nouveau fichier.", u"Ctrl+N", self.parent.NewFile],
"ouvrir":   [u"Ouvrir", u"Ouvrir un fichier.", u"Ctrl+O", self.parent.OpenFile],
"ouvrir ici":   [u"Ouvrir ici", u"Essayer d'ouvrir le fichier dans le module courant.", u"Alt+Ctrl+O", self.parent.OpenFileHere],
"enregistrer":  [u"Enregistrer", u"Enregistrer le document.", u"Ctrl+S", self.parent.SaveFile],
"enregistrer_sous":  [u"Enregistrer sous...", u"Enregistrer le document sous un nouveau nom.", u"Alt+Ctrl+S", self.parent.SaveFileAs],
"exporter": [u"Exporter...", u"Exporter l'image.", u"Ctrl+E", self.parent.ExportFile],
"exporter&sauver": [u"Exporter et sauver", u"Exporter l'image, et sauvegarder le document.", u"Alt+Ctrl+E", self.parent.ExportAndSaveFile],
"mise en page": [u"Param�tres d'impression", u"R�gler les param�tres d'impression.", None, self.parent.PageSetup],
"imprimer": [u"Imprimer", u"Imprimer la figure g�om�trique courante.", u"Ctrl+P", self.parent.Printout],
"proprietes": [u"Propri�t�s", u"Modifier les informations relatives au document", None, self.parent.Proprietes],
"fermer":   [u"Fermer", u"Fermer la feuille courante.", u"Ctrl+W", self.parent.CloseFile],
"quitter":  [u"Quitter", u"Fermer le programme.", u"Alt+F4", self.parent.parent.close],



"onglet":   [u"Onglet suivant", u"Changer d'onglet.", u"Ctrl+TAB", self.parent.onglet_suivant],
"plein_ecran": [u"Plein �cran", u"Passer en mode plein �cran ou revenir en mode normal.", u"F11", self.parent.parent.plein_ecran],
"debug":    [u"D�boguer", u"D�boguer le programme (afficher les erreurs, ...).", None, self.fenetre.mode_debug, self.fenetre.mode_debug],
"ligne_commande":    [u"Afficher la ligne de commande", u"Afficher la ligne de commande.", None, self.fenetre.afficher_ligne_commande, self.fenetre.afficher_ligne_commande],
"options":  [u"Options", u"Param�tres du programme.", None, self.parent.Options],

"aide":     [u"Aide", u"Obtenir de l'aide sur le programme.", None, self.parent.Aide],
"notes":    [u"Notes de version", u"Consulter l'historique du projet.", None, self.parent.Notes],
"licence":    [u"Licence", u"Licence.", None, self.parent.Licence],
"infos":    [u"Configuration", u"Visualiser la configuration actuelle du syst�me.", None, self.parent.Informations],
"contact":  [u"Signaler un probl�me", u"Envoyer un rapport de bug.", None, self.parent.Contacter],
"versions":    [u"Rechercher des mises � jour", u"V�rifier si une nouvelle version est disponible.", None, self.parent.gestionnaire_de_mises_a_jour.verifier_version],
"about":    [u"A propos...", u"WxGeometrie (c) 2005-2007 Nicolas Pourcelot - License : GPL version 2", None, self.parent.About],

        }


        self.menus["fichier"] = ["Fichier", ["nouveau"], ["ouvrir"], ["ouvrir ici"], ["enregistrer"], ["enregistrer_sous"], ["exporter"], ["exporter&sauver"], None, ["mise en page"], ["imprimer"], None, ["fermer"], ["quitter"]]


        self.menus["avance1"] = [u"Avanc�", [u"historique"], [u"ligne_commande"], [u"debug"]]
        self.menus["avance2"] = [u"Avanc�", [u"ligne_commande"], ["debug"]]

        self.menus["?"] = ["?", ["aide"], ["notes"], ["licence"], ["infos"], ["contact"], None, ["versions"], None, ["about"]]



        if self.canvas:
            self.menus.update({
"annuler":  [u"Annuler", u"Annuler la derni�re action.", u"Ctrl+Z", self.panel.annuler],
"refaire":  [u"Refaire", u"Refait la derni�re action annul�e.", u"Ctrl+Y", self.panel.retablir],
"historique":   [u"Contenu interne de la feuille", u"�dition du contenu interne de la feuille.", u"Ctrl+H", self.parent.Histo],
"presse-papier": [u"Copier dans le presse-papier", u"Copier l'image dans le presse-papier.", None, self.canvas.Copy_to_Clipboard],
"barre_outils": [u"Afficher la barre d'outils", u"Afficher la barre d'outils de dessin en haut de la fen�tre.", None, self.panel.afficher_barre_outils, IDEM],
"console_geolib": [u"Afficher la ligne de commande", u"Afficher la ligne de commande en bas de la fen�tre.", None, self.panel.afficher_console_geolib, IDEM],
"repere":   [u"Afficher le rep�re", u"Afficher le rep�re et les axes.", None, self.canvas.gerer_parametre_afficher_axes, canparam("afficher_axes")],
"quadrillage":      [u"Afficher le quadrillage", u"Afficher le quadrillage.", None, self.canvas.gerer_parametre_afficher_quadrillage, canparam('afficher_quadrillage')],
"orthonorme":      [u"Rep�re orthonorm�", u"Garder un rep�re toujours orthonorm�.", None, self.canvas.gerer_parametre_orthonorme, canparam('orthonorme')],
"aimanter":      [u"Aimanter la grille", u"Forcer les points � se placer sur la grille.", None, self.canvas.gerer_parametre_grille_aimantee, canparam('grille_aimantee')],

"reperage": [u"Rep�rage",
                [u"par des points", u"Rep�rage par l'origine et 2 points.", None, self.canvas.repere_OIJ],
                [u"par des vecteurs", u"Rep�rage par l'origine et les 2 vecteurs de base.", None, self.canvas.repere_Oij],
                [u"par des valeurs num�riques", u"Graduation num�rique des axes", None, self.canvas.repere_011],
                [u"Personnaliser le rep�re", u"Personnaliser l'affichage du rep�re, et les graduations", "Ctrl+Alt+R", self.parent.creer["Reperage"]],
            ],

"quadrillages":  [u"Quadrillage",
                    [u"Par d�faut", u"R�tablir le quadrillage par d�faut.", None, self.canvas.quadrillage_defaut],
                    [u"Graduations interm�diaires", u"Ajouter un quadrillage interm�diaire entre deux graduations.", None, self.canvas.quadrillage_demigraduation],
                    [u"Graduations interm�diaires (color�)", u"jouter un quadrillage interm�diaire entre deux graduations (version color�e).", None, self.canvas.quadrillage_demigraduation_colore],
                    [u"Papier millim�tr�", u"Cr�er un papier millim�tr�.", None, self.canvas.quadrillage_millimetre],
                    [u"Papier millim�tr� color�", u"Cr�er un papier millim�tr� color�.", None, self.canvas.quadrillage_millimetre_colore],
                ],

"zoom_texte": [u"Zoom texte",
                    [u"100 %", u"Afficher les textes � leur taille par d�faut.", None, partial(self.canvas.zoom_text, valeur=100)],
                    None,
                    [u"50 %", u"R�duire les textes � 50 % de leur taille.", None, partial(self.canvas.zoom_text, valeur=50)],
                    [u"60 %", u"R�duire les textes � 60 % de leur taille.", None, partial(self.canvas.zoom_text, valeur=60)],
                    [u"70 %", u"R�duire les textes � 70 % de leur taille.", None, partial(self.canvas.zoom_text, valeur=70)],
                    [u"80 %", u"R�duire les textes � 80 % de leur taille.", None, partial(self.canvas.zoom_text, valeur=80)],
                    [u"90 %", u"R�duire les textes � 90 % de leur taille.", None, partial(self.canvas.zoom_text, valeur=90)],
                    None,
                    [u"120 %", u"Agrandir les textes � 120 % de leur taille.", None, partial(self.canvas.zoom_text, valeur=120)],
                    [u"140 %", u"Agrandir les textes � 140 % de leur taille.", None, partial(self.canvas.zoom_text, valeur=140)],
                    [u"160 %", u"Agrandir les textes � 160 % de leur taille.", None, partial(self.canvas.zoom_text, valeur=160)],
                    [u"180 %", u"Agrandir les textes � 180 % de leur taille.", None, partial(self.canvas.zoom_text, valeur=180)],
                    [u"200 %", u"Agrandir les textes � 200 % de leur taille.", None, partial(self.canvas.zoom_text, valeur=200)],
               ],

"zoom_ligne": [u"Zoom ligne",
                    [u"100 %", u"Afficher les lignes � leur taille par d�faut.", None, partial(self.canvas.zoom_line, valeur=100)],
                    None,
                    [u"50 %", u"R�duire les lignes � 50 % de leur taille.", None, partial(self.canvas.zoom_line, valeur=50)],
                    [u"60 %", u"R�duire les lignes � 60 % de leur taille.", None, partial(self.canvas.zoom_line, valeur=60)],
                    [u"70 %", u"R�duire les lignes � 70 % de leur taille.", None, partial(self.canvas.zoom_line, valeur=70)],
                    [u"80 %", u"R�duire les lignes � 80 % de leur taille.", None, partial(self.canvas.zoom_line, valeur=80)],
                    [u"90 %", u"R�duire les lignes � 90 % de leur taille.", None, partial(self.canvas.zoom_line, valeur=90)],
                    None,
                    [u"120 %", u"Agrandir les lignes � 120 % de leur taille.", None, partial(self.canvas.zoom_line, valeur=120)],
                    [u"140 %", u"Agrandir les lignes � 140 % de leur taille.", None, partial(self.canvas.zoom_line, valeur=140)],
                    [u"160 %", u"Agrandir les lignes � 160 % de leur taille.", None, partial(self.canvas.zoom_line, valeur=160)],
                    [u"180 %", u"Agrandir les lignes � 180 % de leur taille.", None, partial(self.canvas.zoom_line, valeur=180)],
                    [u"200 %", u"Agrandir les lignes � 200 % de leur taille.", None, partial(self.canvas.zoom_line, valeur=200)],
               ],

"zoom_general": [u"Zoom g�n�ral",
                    [u"Mode normal", u"Affichage par d�faut.", None, self.canvas.zoom_normal],
                    [u"L�ger grossissement", u"Textes et lignes (un peu) grossis.", None, self.canvas.zoom_large],
                    None,
                    [u"Mode vid�oprojecteur (grossissement)", u"R�glage adapt� � la vid�oprojection (textes et lignes grossis).", None, self.canvas. zoom_videoprojecteur],
                    [u"Mode vid�oprojecteur accentu�", u"Grossissement tr�s important des objets.", None, self.canvas. zoom_videoprojecteur_large],
               ],

"fenetre":  [u"R�glage de la fen�tre", u"R�glage de la fen�tre d'affichage.", u"Alt+Ctrl+F", self.parent.creer["Fenetre"]],
"zoomer":   [u"Zoomer", u"Se rapprocher de la figure.", u"Ctrl+PGUP", self.canvas.zoom_in],
"dezoomer": [u"D�zoomer", u"S'�loigner de la figure.", u"Ctrl+PGDN", self.canvas.zoom_out],
"orthonormaliser":  [u"Orthonormaliser", u"Obtenir un rep�re orthonormal.", u"Alt+Ctrl+O", self.canvas.orthonormer],
"zoom_auto":  [u"Zoom intelligent", u"R�glage automatique de la fen�tre d'affichage.", u"Alt+Ctrl+A", self.canvas.zoom_auto],

"modifier": [u"Modifier", u"Editer les propri�tes d'un ou plusieurs objets g�om�triques.", u"Ctrl+M", self.parent.editer],
"supprimer":[u"Supprimer", u"Supprime un ou plusieurs objets g�om�triques.", u"Ctrl+DEL", self.parent.supprimer],

"coder":    [u"Codage automatique", u"Codage automatique de la figure.", u"Alt+Ctrl+C", self.canvas.coder],
"decoder":  [u"Effacer le codage", u"Supprimer le codage de la figure.", u"Alt+Ctrl+D", self.canvas.decoder],
"traces":   [u"Effacer les traces", u"Supprimer toutes les traces de la figure (laisse les objets en mode Trace).", None, self.canvas.effacer_traces],
##"detecter": [u"D�tecter les objets cach�s", u"Signaler la pr�sence des objets cach�s au passage du pointeur.", None, self.canvas.detecter_caches, self.canvas.detecter_caches],
"detecter": [u"Afficher les objets cach�s", u"Afficher en semi-transparent les objets cach�s.", None, self.canvas.gerer_parametre_afficher_objets_caches, canparam('afficher_objets_caches')],
"nettoyer": [u"Supprimer les objets inutiles", u"Supprimer les objets cach�s qui ne servent pas pour la construction.", None, self.canvas.nettoyer_feuille],
"animer":   [u"Cr�er une animation", u"Faire varier automatiquement une valeur.", None, self.parent.Animer],




"affichage": [u"Affichage", ["onglet"], ["plein_ecran"], None, ["barre_outils"], ["console_geolib"], None, ["repere"], ["quadrillage"], ["orthonorme"], ["reperage"], ["quadrillages"], None, ["zoom_texte"], ["zoom_ligne"], ["zoom_general"], None, ["fenetre"], ["zoomer"], ["dezoomer"], ["orthonormaliser"], [u"zoom_auto"]],

"autres":    [u"Autres actions", [u"coder"], [u"decoder"], [u"traces"], None, [u"detecter"], [u"nettoyer"], None, [u"animer"], [u"aimanter"]],


"creer":    [u"Cr�er",
                [u"Points",
                    [u"Point libre", u"Point quelconque.", u"Ctrl+L", self.parent.creer["Point"]],
                    [u"Milieu", u"Milieu d'un segment.", None, self.parent.creer["Milieu"]],
                    [u"Barycentre", u"Barycentre de n points.", u"Ctrl+B", self.parent.creer["Barycentre"]],
                    [u"Point final", u"Point d�fini par une relation vectorielle.", u"Ctrl+F", self.parent.creer["PointFinal"]],
                    [u"Point sur droite", u"Point appartenant � une droite.", None, self.parent.creer["GlisseurDroite"]],
                    [u"Point sur segment", u"Point appartenant � un segment.", None, self.parent.creer["GlisseurSegment"]],
                    [u"Point sur cercle", u"Point appartenant � un cercle.", None, self.parent.creer["GlisseurCercle"]],
                ],
                [u"Intersections",
                    [u"Intersection de deux droites", u"Point d�fini par l'intersection de deux droites (ou demi-droites, ou segments).", u"Ctrl+I", self.parent.creer["InterDroites"]],
                    [u"Intersection d'une droite et d'un cercle", u"Point d�fini par l'intersection d'une droite et d'un cercle.", u"Alt+Ctrl+I", self.parent.creer["InterDroiteCercle"]],
                    [u"Intersection de deux cercles", u"Point d�fini par l'intersection de deux cercles (ou arcs de cercles).", None,  self.parent.creer["InterCercles"]],
                ],
                [u"Centres",
                    [u"Centre d'un cercle", u"Centre d'un cercle.", None, self.parent.creer["Centre"]],
                    [u"Centre de gravit�", u"Centre de gravite d'un triangle (intersection des m�dianes).", None, self.parent.creer["CentreGravite"]],
                    [u"Orthocentre", u"Orthocentre d'un triangle (intersection des hauteurs).", None, self.parent.creer["Orthocentre"]],
                    [u"Centre du cercle circonscrit", u"Centre du cercle circonscrit d'un triangle (intersection des m�diatrices).", None, self.parent.creer["CentreCercleCirconscrit"]],
                    [u"Centre du cercle inscrit", u"Centre du cercle inscrit d'un triangle (intersection des bissectrices).", None, self.parent.creer["CentreCercleInscrit"]],
                ],
                [u"Lignes",
                    [u"Segment", u"Segment d�fini par deux points.", u"Ctrl+G", self.parent.creer["Segment"]],
                    None,
                    [u"Droite", u"Droite d�finie par deux points.", u"Ctrl+D", self.parent.creer["Droite"]],
                    [u"Demi-droite", u"Demi-droite d�finie par son origine et un autre point.", None, self.parent.creer["Demidroite"]],
                    None,
                    [u"Vecteur", u"Vecteur d�fini par deux points.", u"Ctrl+U", self.parent.creer["Vecteur"]],
                    [u"Vecteur libre", u"Vecteur d�fini par ses coordonn�es.", None, self.parent.creer["VecteurLibre"]],
                    [u"Representant", u"Repr�sentant d'origine donn�e d'un vecteur.", None, self.parent.creer["Representant"]],
                    None,
                    [u"Parall�le", u"Parall�le � une droite passant par un point.", None, self.parent.creer["Parallele"]],
                    [u"Perpendiculaire", u"Perpendiculaire � une droite passant par un point.", None, self.parent.creer["Perpendiculaire"]],
                    [u"M�diatrice", u"M�diatrice d'un segment.", None, self.parent.creer["Mediatrice"]],
                    [u"Bissectrice", u"Bissectrice d'un angle.", None, self.parent.creer["Bissectrice"]],
                    [u"Tangente", u"Tangente � un cercle.", None, self.parent.creer["Tangente"]],
                ],
                [u"Cercles",
                    [u"Cercle d�fini par son centre et un point", u"Cercle d�fini par son centre et un autre point.", u"Ctrl+K", self.parent.creer["Cercle"]],
                    [u"Cercle d�fini par son centre et son rayon", u"Cercle d�fini par son centre et la valeur de son rayon.", u"Ctrl+R", self.parent.creer["CercleRayon"]],
                    [u"Cercle d�fini par un diam�tre", u"Cercle d�fini par deux points diam�tralement oppos�s.", None, self.parent.creer["CercleDiametre"]],
                    [u"Cercle d�fini par 3 points", u"Cercle d�fini par trois points.", None, self.parent.creer["CerclePoints"]],
                    None,
                    [u"Arc de centre donn�", u"Arc de sens direct, d�fini par son centre, son origine, et un autre point.", None, self.parent.creer["ArcCercle"]],
                    [u"Arc d�fini par 3 points", u"Arc d�fini par ses extr�mit�s, et un point interm�diaire.", None, self.parent.creer["ArcPoints"]],
                    [u"Arc orient�", u"Arc orient�, d�fini par ses extr�mit�s, et un point interm�diaire.", None, self.parent.creer["ArcOriente"]],
                    [u"Demi-cercle", u"Demi-cercle de diam�tre donn�, de sens direct.", None, self.parent.creer["DemiCercle"]],
                    None,
                    [u"Disque", u"Disque circonscrit par un cercle donn�.", None, self.parent.creer["Disque"]],
                ],
                [u"Polygones",
                    [u"Triangle", u"Triangle d�fini par ses sommets.", None, self.parent.creer["Triangle"]],
                    [u"Polygone quelconque", u"Polygone quelconque, d�fini par ses sommets.", None, self.parent.creer["Polygone"]],
                    [u"Parall�logramme", u"Parall�logramme de sens direct d�fini par 3 sommets.", None, self.parent.creer["Parallelogramme"]],
                    [u"Polygone r�gulier", u"Polygone r�gulier de sens direct d�fini par 2 sommets cons�cutifs.", None, self.parent.creer["PolygoneRegulier"]],
                    [u"Polygone r�gulier de centre donn�", u"Polygone r�gulier d�fini son centre et un sommet.", None, self.parent.creer["PolygoneRegulierCentre"]],
                ],
                [u"Interpolation",
                    [u"Interpolation lin�aire", u"Lign� bris�e reliant les points d�sign�s.", None, self.parent.creer["InterpolationLineaire"]],
                    [u"Interpolation quadratique", u"Courbe lisse (ie. de classe C1) reliant les points d�sign�s.", None, self.parent.creer["InterpolationQuadratique"]],
                ],
                [u"Angles",
                    [u"Angle", u"Angle non orient� d�fini par trois points.", None, self.parent.creer["Angle"]],
                    [u"Angle orient�", u"Angle orient� d�fini par trois points.", None, self.parent.creer["AngleOriente"]],
                    [u"Angle orient� (non affich�)", u"Angle orient� (non affich�) d�fini par 2 vecteurs.", None, self.parent.creer["AngleVectoriel"]],
                    [u"Angle libre (non affich�)", u"Angle orient� (non affich�) d�fini par 2 vecteurs.", None, self.parent.creer["AngleLibre"]],

                ],
                [u"Transformations",
                    [u"Translation", u"Translation de vecteur donn�.", None, self.parent.creer["Translation"]],
                    [u"Sym�trie centrale", u"Sym�trie par rapport � un point.", None, self.parent.creer["SymetrieCentrale"]],
                    [u"Sym�trie axiale", u"Sym�trie par rapport � une droite.", None, self.parent.creer["Reflexion"]],
                    [u"Rotation", u"Rotation de centre et d'angle donn�s.", None, self.parent.creer["Rotation"]],
                    [u"Homoth�tie", u"Translation de vecteur donn�.", None, self.parent.creer["Homothetie"]],
                    None,
                    [u"Image par transformation", u"Cr�er l'image d'un objet par une transformation g�om�trique.", None, self.parent.creer["Image"]],
                ],
                [u"Divers",
                    [u"Texte", u"Champ de texte.", None, self.parent.creer["Texte"]],
                    [u"Variable", u"Variable li�e ou non.", None, self.parent.creer["Variable"]],
                ],
            ]

            })


        for item in contenu:
            self.ajouter(*item)
