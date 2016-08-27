# -*- coding: utf-8 -*-

##--------------------------------------#######
#                   Menu                                   #
##--------------------------------------#######
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


from operator import attrgetter
from functools import partial

from PyQt4.QtGui import QMenu, QMenuBar, QKeySequence



#-----------------------
#       Menus
#-----------------------



class RSSMenu(QMenu): # parent : wxgeometrie (Frame principal)
    "Menu dynamique."
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
    "Remplace la classe QMenu."

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
                    action = self.addAction(titre)
                    if contenu[3]:
                        action.triggered.connect(contenu[3])
                        action.setShortcut(shortcut)
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
    """Remplace la classe QMenuBar pour créer une barre de menu propre à chaque module.

    La méthode de base est ``ajouter(self, *menu)``, où menu est une liste.

    *Exemple 1 :*

    ::

    menu =  ["Outils",
                ["Options", "Parametres du programme", "Ctrl+O", fonction1],
                ["Memoriser le resultat", "Copie le resultat du calcul dans le presse-papier", None, fonction2],
                None,
                ["Autres",
                    ["Rubrique 1", None, "Alt+Ctrl+R", fonction3],
                    ["Rubrique 2", "Rubrique non active pour l'instant", None, None]]]

    *Exemple 2 :*

    ::

    ["Infos", ["Afficher les infos", "Affichage des infos en temps reel", "Ctrl+I", fonction1, fonction2]]

    La presence de deux fonctions (eventuellement identiques) indique qu'il s'agit d'un menu "cochable".
    L'etat (coché ou non coché) est déterminé par la valeur renvoyée par la fonction 'fonction2'.

    *Note:* Pour un menu moins standard, on peut toujours utiliser directement ``QMenuBar``.
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

"nouveau":  ["Nouveau", "Créer un nouveau fichier.", "Ctrl+N", self.parent.NewFile],
"ouvrir":   ["Ouvrir", "Ouvrir un fichier.", "Ctrl+O", self.parent.OpenFile],
"ouvrir ici":   ["Ouvrir ici", "Essayer d'ouvrir le fichier dans le module courant.", "Alt+Ctrl+O", self.parent.OpenFileHere],
"enregistrer":  ["Enregistrer", "Enregistrer le document.", "Ctrl+S", self.parent.SaveFile],
"enregistrer_sous":  ["Enregistrer sous...", "Enregistrer le document sous un nouveau nom.", "Alt+Ctrl+S", self.parent.SaveFileAs],
"exporter": ["Exporter...", "Exporter l'image.", "Ctrl+E", self.parent.ExportFile],
"exporter&sauver": ["Exporter et sauver", "Exporter l'image, et sauvegarder le document.", "Alt+Ctrl+E", self.parent.ExportAndSaveFile],
##"mise en page": [u"Paramètres d'impression", u"Régler les paramètres d'impression.", None, self.parent.PageSetup],
"session":  ["Sessions",
                ['Nouvelle session', 'Réinitialiser la session.', None, self.parent.NouvelleSession],
                ['Session précédente', 'Recharger la session précédente.', None, self.parent.ChargerSessionPrecedente],
                ['Ouvrir la session...', 'Charger une autre session.', None, self.parent.ChargerSession],
                ['Enregistrer sous...', 'Enregistrer la session actuelle.', None, self.parent.SauverSession],
            ],
"imprimer": ["Imprimer", "Imprimer la figure géométrique courante.", "Ctrl+P", self.parent.Printout],
"proprietes": ["Propriétés", "Modifier les informations relatives au document", None, self.parent.Proprietes],
"fermer":   ["Fermer", "Fermer la feuille courante.", "Ctrl+W", self.parent.CloseFile],
"quitter":  ["Quitter", "Fermer le programme.", "Alt+F4", self.parent.parent.close],



"onglet":   ["Onglet suivant", "Changer d'onglet.", "Ctrl+TAB", self.parent.onglet_suivant],
"plein_ecran": ["Plein écran", "Passer en mode plein écran ou revenir en mode normal.", "F11", self.parent.parent.plein_ecran],
"debug":    ["Déboguer", "Déboguer le programme (afficher les erreurs, ...).", None, self.fenetre.mode_debug, self.fenetre.mode_debug],
"ligne_commande":    ["Afficher la ligne de commande", "Afficher la ligne de commande.", None, self.fenetre.afficher_ligne_commande, self.fenetre.afficher_ligne_commande],
"options":  ["Options", "Paramètres du programme.", None, self.parent.Options],

"aide":     ["Aide", "Obtenir de l'aide sur le programme.", None, self.parent.Aide],
"infos":    ["Configuration", "Visualiser la configuration actuelle du système.", None, self.parent.Informations],
"contact":  ["Signaler un problème", "Envoyer un rapport de bug.", None, self.parent.Contacter],
"versions":    ["Rechercher des mises à jour", "Vérifier si une nouvelle version est disponible.", None, self.parent.gestionnaire_de_mises_a_jour.verifier_version],
"about":    ["A propos...", "WxGeometrie (c) 2005-2007 Nicolas Pourcelot - License : GPL version 2", None, self.parent.About],

        }


        self.menus["fichier"] = ["Fichier", ["nouveau"], ["ouvrir"], ["ouvrir ici"],
                                None, ["enregistrer"], ["enregistrer_sous"],
                                ["exporter"], ["exporter&sauver"], None, ['session'],
                                None, ["imprimer"], None, ["fermer"], ["quitter"]]


        self.menus["avance1"] = ["Avancé", ["historique"], ["ligne_commande"], ["debug"]]
        self.menus["avance2"] = ["Avancé", ["ligne_commande"], ["debug"]]

        self.menus["?"] = ["?", ["aide"], ["infos"], ["contact"], None, ["versions"], None, ["about"]]



        if self.canvas:
            self.menus.update({
"annuler":  ["Annuler", "Annuler la dernière action.", "Ctrl+Z", self.panel.annuler],
"refaire":  ["Refaire", "Refait la dernière action annulée.", "Ctrl+Y", self.panel.retablir],
"historique":   ["Contenu interne de la feuille", "Édition du contenu interne de la feuille.", "Ctrl+H", self.parent.Histo],
"presse-papier": ["Copier dans le presse-papier", "Copier l'image dans le presse-papier.", None, self.canvas.Copy_to_Clipboard],
"barre_outils": ["Afficher la barre d'outils", "Afficher la barre d'outils de dessin en haut de la fenêtre.", None, self.panel.afficher_barre_outils, IDEM],
"console_geolib": ["Afficher la ligne de commande", "Afficher la ligne de commande en bas de la fenêtre.", None, self.panel.afficher_console_geolib, IDEM],
"repere":   ["Afficher le repère", "Afficher le repère et les axes.", None, self.canvas.gerer_parametre_afficher_axes, canparam("afficher_axes")],
"quadrillage":      ["Afficher le quadrillage", "Afficher le quadrillage.", None, self.canvas.gerer_parametre_afficher_quadrillage, canparam('afficher_quadrillage')],
"orthonorme":      ["Repère orthonormé", "Garder un repère toujours orthonormé.", None, self.canvas.gerer_parametre_orthonorme, canparam('orthonorme')],
"aimanter":      ["Aimanter la grille", "Forcer les points à se placer sur la grille.", None, self.canvas.gerer_parametre_grille_aimantee, canparam('grille_aimantee')],

"reperage": ["Repérage",
                ["par des points", "Repérage par l'origine et 2 points.", None, self.canvas.repere_OIJ],
                ["par des vecteurs", "Repérage par l'origine et les 2 vecteurs de base.", None, self.canvas.repere_Oij],
                ["par des valeurs numériques", "Graduation numérique des axes", None, self.canvas.repere_011],
                ["Personnaliser le repère", "Personnaliser l'affichage du repère, et les graduations", "Ctrl+Alt+R", self.canvas.regler_repere],
            ],

"quadrillages":  ["Quadrillage",
                    ["Par défaut", "Rétablir le quadrillage par défaut.", None, self.canvas.quadrillage_defaut],
                    ["Graduations intermédiaires", "Ajouter un quadrillage intermédiaire entre deux graduations.", None, self.canvas.quadrillage_demigraduation],
                    ["Graduations intermédiaires (coloré)", "jouter un quadrillage intermédiaire entre deux graduations (version colorée).", None, self.canvas.quadrillage_demigraduation_colore],
                    ["Papier millimétré", "Créer un papier millimétré.", None, self.canvas.quadrillage_millimetre],
                    ["Papier millimétré coloré", "Créer un papier millimétré coloré.", None, self.canvas.quadrillage_millimetre_colore],
                ],

"zoom_texte": ["Zoom texte",
                    ["100 %", "Afficher les textes à leur taille par défaut.", None, partial(self.canvas.zoom_text, valeur=100)],
                    None,
                    ["50 %", "Réduire les textes à 50 % de leur taille.", None, partial(self.canvas.zoom_text, valeur=50)],
                    ["60 %", "Réduire les textes à 60 % de leur taille.", None, partial(self.canvas.zoom_text, valeur=60)],
                    ["70 %", "Réduire les textes à 70 % de leur taille.", None, partial(self.canvas.zoom_text, valeur=70)],
                    ["80 %", "Réduire les textes à 80 % de leur taille.", None, partial(self.canvas.zoom_text, valeur=80)],
                    ["90 %", "Réduire les textes à 90 % de leur taille.", None, partial(self.canvas.zoom_text, valeur=90)],
                    None,
                    ["120 %", "Agrandir les textes à 120 % de leur taille.", None, partial(self.canvas.zoom_text, valeur=120)],
                    ["140 %", "Agrandir les textes à 140 % de leur taille.", None, partial(self.canvas.zoom_text, valeur=140)],
                    ["160 %", "Agrandir les textes à 160 % de leur taille.", None, partial(self.canvas.zoom_text, valeur=160)],
                    ["180 %", "Agrandir les textes à 180 % de leur taille.", None, partial(self.canvas.zoom_text, valeur=180)],
                    ["200 %", "Agrandir les textes à 200 % de leur taille.", None, partial(self.canvas.zoom_text, valeur=200)],
               ],

"zoom_ligne": ["Zoom ligne",
                    ["100 %", "Afficher les lignes à leur taille par défaut.", None, partial(self.canvas.zoom_line, valeur=100)],
                    None,
                    ["50 %", "Réduire les lignes à 50 % de leur taille.", None, partial(self.canvas.zoom_line, valeur=50)],
                    ["60 %", "Réduire les lignes à 60 % de leur taille.", None, partial(self.canvas.zoom_line, valeur=60)],
                    ["70 %", "Réduire les lignes à 70 % de leur taille.", None, partial(self.canvas.zoom_line, valeur=70)],
                    ["80 %", "Réduire les lignes à 80 % de leur taille.", None, partial(self.canvas.zoom_line, valeur=80)],
                    ["90 %", "Réduire les lignes à 90 % de leur taille.", None, partial(self.canvas.zoom_line, valeur=90)],
                    None,
                    ["120 %", "Agrandir les lignes à 120 % de leur taille.", None, partial(self.canvas.zoom_line, valeur=120)],
                    ["140 %", "Agrandir les lignes à 140 % de leur taille.", None, partial(self.canvas.zoom_line, valeur=140)],
                    ["160 %", "Agrandir les lignes à 160 % de leur taille.", None, partial(self.canvas.zoom_line, valeur=160)],
                    ["180 %", "Agrandir les lignes à 180 % de leur taille.", None, partial(self.canvas.zoom_line, valeur=180)],
                    ["200 %", "Agrandir les lignes à 200 % de leur taille.", None, partial(self.canvas.zoom_line, valeur=200)],
               ],

"zoom_general": ["Zoom général",
                    ["Mode normal", "Affichage par défaut.", None, self.canvas.zoom_normal],
                    ["Léger grossissement", "Textes et lignes (un peu) grossis.", None, self.canvas.zoom_large],
                    None,
                    ["Mode vidéoprojecteur (grossissement)", "Réglage adapté à la vidéoprojection (textes et lignes grossis).", None, self.canvas. zoom_videoprojecteur],
                    ["Mode vidéoprojecteur accentué", "Grossissement très important des objets.", None, self.canvas. zoom_videoprojecteur_large],
               ],

"fenetre":  ["Réglage de la fenêtre", "Réglage de la fenêtre d'affichage.", "Alt+Ctrl+F", self.parent.creer["Fenetre"]],
"zoomer":   ["Zoomer", "Se rapprocher de la figure.", "Ctrl+PGUP", self.canvas.zoom_in],
"dezoomer": ["Dézoomer", "S'éloigner de la figure.", "Ctrl+PGDOWN", self.canvas.zoom_out],
"orthonormaliser":  ["Orthonormaliser", "Obtenir un repère orthonormal.", "Alt+Ctrl+O", self.canvas.orthonormer],
"zoom_auto":  ["Zoom intelligent", "Réglage automatique de la fenêtre d'affichage.", "Alt+Ctrl+A", self.canvas.zoom_auto],

"modifier": ["Modifier", "Editer les propriétes d'un ou plusieurs objets géométriques.", "Ctrl+M", self.parent.editer],
"supprimer":["Supprimer", "Supprime un ou plusieurs objets géométriques.", "Ctrl+DEL", self.parent.supprimer],

"coder":    ["Codage automatique", "Codage automatique de la figure.", "Alt+Ctrl+C", self.canvas.coder],
"decoder":  ["Effacer le codage", "Supprimer le codage de la figure.", "Alt+Ctrl+D", self.canvas.decoder],
"traces":   ["Effacer les traces", "Supprimer toutes les traces de la figure (laisse les objets en mode Trace).", None, self.canvas.effacer_traces],
##"detecter": [u"Détecter les objets cachés", u"Signaler la présence des objets cachés au passage du pointeur.", None, self.canvas.detecter_caches, self.canvas.detecter_caches],
"detecter": ["Afficher les objets cachés", "Afficher en semi-transparent les objets cachés.", None, self.canvas.gerer_parametre_afficher_objets_caches, canparam('afficher_objets_caches')],
"nettoyer": ["Supprimer les objets inutiles", "Supprimer les objets cachés qui ne servent pas pour la construction.", None, self.canvas.nettoyer_feuille],
"animer":   ["Créer une animation", "Faire varier automatiquement une valeur.", None, self.parent.Animer],




"affichage": ["Affichage", ["onglet"], ["plein_ecran"], None, ["barre_outils"], ["console_geolib"], None, ["repere"], ["quadrillage"], ["orthonorme"], ["reperage"], ["quadrillages"], None, ["zoom_texte"], ["zoom_ligne"], ["zoom_general"], None, ["fenetre"], ["zoomer"], ["dezoomer"], ["orthonormaliser"], ["zoom_auto"]],

"autres":    ["Autres actions", ["coder"], ["decoder"], ["traces"], None, ["detecter"], ["nettoyer"], None, ["animer"], ["aimanter"]],


"creer":    ["Créer",
                ["Points",
                    ["Point libre", "Point quelconque.", "Ctrl+L", self.parent.creer["Point"]],
                    ["Milieu", "Milieu d'un segment.", None, self.parent.creer["Milieu"]],
                    ["Barycentre", "Barycentre de n points.", "Ctrl+B", self.parent.creer["Barycentre"]],
                    ["Point final", "Point défini par une relation vectorielle.", "Ctrl+F", self.parent.creer["PointFinal"]],
                    ["Point sur droite", "Point appartenant à une droite.", None, self.parent.creer["GlisseurDroite"]],
                    ["Point sur segment", "Point appartenant à un segment.", None, self.parent.creer["GlisseurSegment"]],
                    ["Point sur cercle", "Point appartenant à un cercle.", None, self.parent.creer["GlisseurCercle"]],
                ],
                ["Intersections",
                    ["Intersection de deux droites", "Point défini par l'intersection de deux droites (ou demi-droites, ou segments).", "Ctrl+I", self.parent.creer["InterDroites"]],
                    ["Intersection d'une droite et d'un cercle", "Point défini par l'intersection d'une droite et d'un cercle.", "Alt+Ctrl+I", self.parent.creer["InterDroiteCercle"]],
                    ["Intersection de deux cercles", "Point défini par l'intersection de deux cercles (ou arcs de cercles).", None,  self.parent.creer["InterCercles"]],
                ],
                ["Centres",
                    ["Centre d'un cercle", "Centre d'un cercle.", None, self.parent.creer["Centre"]],
                    ["Centre de gravité", "Centre de gravite d'un triangle (intersection des médianes).", None, self.parent.creer["CentreGravite"]],
                    ["Orthocentre", "Orthocentre d'un triangle (intersection des hauteurs).", None, self.parent.creer["Orthocentre"]],
                    ["Centre du cercle circonscrit", "Centre du cercle circonscrit d'un triangle (intersection des médiatrices).", None, self.parent.creer["CentreCercleCirconscrit"]],
                    ["Centre du cercle inscrit", "Centre du cercle inscrit d'un triangle (intersection des bissectrices).", None, self.parent.creer["CentreCercleInscrit"]],
                ],
                ["Lignes",
                    ["Segment", "Segment défini par deux points.", "Ctrl+G", self.parent.creer["Segment"]],
                    None,
                    ["Droite", "Droite définie par deux points.", "Ctrl+D", self.parent.creer["Droite"]],
                    ["Demi-droite", "Demi-droite définie par son origine et un autre point.", None, self.parent.creer["Demidroite"]],
                    None,
                    ["Vecteur", "Vecteur défini par deux points.", "Ctrl+U", self.parent.creer["Vecteur"]],
                    ["Vecteur libre", "Vecteur défini par ses coordonnées.", None, self.parent.creer["VecteurLibre"]],
                    ["Representant", "Représentant d'origine donnée d'un vecteur.", None, self.parent.creer["Representant"]],
                    None,
                    ["Parallèle", "Parallèle à une droite passant par un point.", None, self.parent.creer["Parallele"]],
                    ["Perpendiculaire", "Perpendiculaire à une droite passant par un point.", None, self.parent.creer["Perpendiculaire"]],
                    ["Médiatrice", "Médiatrice d'un segment.", None, self.parent.creer["Mediatrice"]],
                    ["Bissectrice", "Bissectrice d'un angle.", None, self.parent.creer["Bissectrice"]],
                    ["Tangente", "Tangente à un cercle.", None, self.parent.creer["Tangente"]],
                ],
                ["Cercles",
                    ["Cercle défini par son centre et un point", "Cercle défini par son centre et un autre point.", "Ctrl+K", self.parent.creer["Cercle"]],
                    ["Cercle défini par son centre et son rayon", "Cercle défini par son centre et la valeur de son rayon.", "Ctrl+R", self.parent.creer["CercleRayon"]],
                    ["Cercle défini par un diamètre", "Cercle défini par deux points diamétralement opposés.", None, self.parent.creer["CercleDiametre"]],
                    ["Cercle défini par 3 points", "Cercle défini par trois points.", None, self.parent.creer["CerclePoints"]],
                    None,
                    ["Arc de centre donné", "Arc de sens direct, défini par son centre, son origine, et un autre point.", None, self.parent.creer["ArcCercle"]],
                    ["Arc défini par 3 points", "Arc défini par ses extrémités, et un point intermédiaire.", None, self.parent.creer["ArcPoints"]],
                    ["Arc orienté", "Arc orienté, défini par ses extrémités, et un point intermédiaire.", None, self.parent.creer["ArcOriente"]],
                    ["Demi-cercle", "Demi-cercle de diamètre donné, de sens direct.", None, self.parent.creer["DemiCercle"]],
                    None,
                    ["Disque", "Disque circonscrit par un cercle donné.", None, self.parent.creer["Disque"]],
                ],
                ["Polygones",
                    ["Triangle", "Triangle défini par ses sommets.", None, self.parent.creer["Triangle"]],
                    ["Polygone quelconque", "Polygone quelconque, défini par ses sommets.", None, self.parent.creer["Polygone"]],
                    ["Parallélogramme", "Parallélogramme de sens direct défini par 3 sommets.", None, self.parent.creer["Parallelogramme"]],
                    ["Polygone régulier", "Polygone régulier de sens direct défini par 2 sommets consécutifs.", None, self.parent.creer["PolygoneRegulier"]],
                    ["Polygone régulier de centre donné", "Polygone régulier défini son centre et un sommet.", None, self.parent.creer["PolygoneRegulierCentre"]],
                ],
                ["Interpolation",
                    ["Interpolation linéaire", "Ligné brisée reliant les points désignés.", None, self.parent.creer["InterpolationLineaire"]],
                    ["Interpolation quadratique", "Courbe lisse (ie. de classe C1) reliant les points désignés.", None, self.parent.creer["InterpolationQuadratique"]],
                ],
                ["Angles",
                    ["Angle", "Angle non orienté défini par trois points.", None, self.parent.creer["Angle"]],
                    ["Angle orienté", "Angle orienté défini par trois points.", None, self.parent.creer["AngleOriente"]],
                    ["Angle orienté (non affiché)", "Angle orienté (non affiché) défini par 2 vecteurs.", None, self.parent.creer["AngleVectoriel"]],
                    ["Angle libre (non affiché)", "Angle orienté (non affiché) défini par 2 vecteurs.", None, self.parent.creer["AngleLibre"]],

                ],
                ["Transformations",
                    ["Translation", "Translation de vecteur donné.", None, self.parent.creer["Translation"]],
                    ["Symétrie centrale", "Symétrie par rapport à un point.", None, self.parent.creer["SymetrieCentrale"]],
                    ["Symétrie axiale", "Symétrie par rapport à une droite.", None, self.parent.creer["Reflexion"]],
                    ["Rotation", "Rotation de centre et d'angle donnés.", None, self.parent.creer["Rotation"]],
                    ["Homothétie", "Translation de vecteur donné.", None, self.parent.creer["Homothetie"]],
                    None,
                    ["Image par transformation", "Créer l'image d'un objet par une transformation géométrique.", None, self.parent.creer["Image"]],
                ],
                ["Divers",
                    ["Texte", "Champ de texte.", None, self.parent.creer["Texte"]],
                    ["Variable", "Variable liée ou non.", None, self.parent.creer["Variable"]],
                ],
            ]

            })


        for item in contenu:
            self.ajouter(*item)
