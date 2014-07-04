# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

# o-----------------------------------------------------------o
# |              Barre d'outils pour la géométrie             |
# o-----------------------------------------------------------o
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

from math import pi
from functools import partial

from PyQt4.QtGui import (QWidget, QToolButton, QInputDialog, QLineEdit, QHBoxLayout,
                         QIcon, QMenu, QShortcut)
##from PyQt4.QtCore import Qt

from .qtlib import png
from ..pylib import is_in
from ..geolib.routines import distance
from ..geolib.textes import Texte_generique
from ..geolib.points import Point_generique, Barycentre, Milieu, Point
from ..geolib.cercles import Arc_generique, Cercle_generique, Cercle, Arc_points,\
                             Arc_oriente, Cercle_diametre, Cercle_points, Demicercle,\
                             Arc_cercle
from ..geolib.lignes import Droite_generique, Segment, Demidroite, Ligne_generique,\
                            Droite, Tangente, Parallele, Perpendiculaire, Bissectrice,\
                            Mediatrice, Demiplan, Axe
from ..geolib.polygones import Polygone_generique, PrevisualisationPolygone
from ..geolib.angles import Angle_generique, Angle, Angle_oriente, Secteur_angulaire
from ..geolib.transformations import Rotation, Homothetie, Translation
from ..geolib.vecteurs import Vecteur_generique, Vecteur
from ..geolib.intersections import Intersection_cercles, Intersection_droite_cercle
from ..geolib.objet import Objet, contexte

from .. import geolib



class MultiButton(QToolButton):
    u"""Un bouton possédant plusieurs fonctionnalités, que l'utilisateur
    peut choisir avec un clic de la souris."""

    def __init__(self, parent, raccourci, selectionnable, *fonctionnalites):
        QToolButton.__init__(self, parent)
        self.setAutoRaise(True)

        self.parent = parent
        self.selectionnable = selectionnable

        # Raccourci clavier pour sélectionner le bouton:
        self.raccourci = raccourci
        if self.raccourci:
            sh = self.shortcut = QShortcut(self)
            sh.setKey(raccourci)
            sh.setAutoRepeat(not self.selectionnable)
            # NB: `selected=True` est obligatoire ici (mais je ne sais pas pourquoi...)
            sh.activated.connect(partial(self.select, selected=True))

        # Liste des différentes fonctionnalités possibles:
        self.liste = list(fonctionnalites)
        # Menu à afficher pour changer de fonctionnalité:
        self.menu = None
        # Index de la fonctionnalité choisie dans la liste:
        self.index = 0

        ##self.SetBackgroundColour(self.parent.GetBackgroundColour())
        self.select(False, 0)
        # NB: `selected=True` est obligatoire ici (mais je ne sais pas pourquoi...)
        self.clicked.connect(partial(self.select, selected=True))


    def update_menu(self):
        if self.menu is None:
            #self.setPopupMode(QToolButton.MenuButtonPopup)
            self.menu = menu = QMenu(self)
            self.setMenu(menu)
        else:
            menu = self.menu
            menu.clear()
        for i, entree in enumerate(self.liste):
            if entree is None:
                menu.addSeparator()
            else:
                titre, image, aide, action = entree
                action = menu.addAction(self.img2icon(image), titre)
                action.setIconVisibleInMenu(True)
                # NB: `selected=True` est obligatoire ici (sinon, c'est l'argument du
                # signal `.triggered` qui est passé comme argument ?)
                action.triggered.connect(partial(self.select, selected=True, i=i))

    @staticmethod
    def img2icon(image):
        return QIcon(png(image))

    @property
    def selected(self):
        return self.parent._selected_button is self

    def select(self, selected=True, i=None):
        u"""(Dé)sélectionne le bouton.

        Si `i` est différent de `None`, la i-ème fonctionnalité associée
        au bouton est activée.

        L'icône est automatiquement mise à jour.
        """
        if i is not None:
            self.index = i

            titre, image, aide, action = self.liste[i]
            if self.raccourci:
                aide += " (" + self.raccourci.replace("Shift", "Maj") + ")"
            self.setToolTip(aide)
        if self.selectionnable:
            if selected:
                previous = self.parent._selected_button
                self.parent._selected_button = self
                if previous is not None:
                    previous.update_display()
                action = self.liste[self.index][3]
                action(True)
            elif self.selected:
                # NB: ne pas déselectionner un autre bouton.
                self.parent._selected_button = None
            if len(self.liste) > 1:
                self.update_menu()
        elif selected:
            self.liste[0][3]()
        self.update_display()

    def update_display(self, as_selected=None):
        u"""Change l'icône du bouton, selon la fonction sélectionnée, et le fait
            que le bouton soit activé ou non.

            Il est possible de forcer l'affichage du bouton comme s'il était
            sélectionné, en passant l'option `as_selected=True`.
            Cela sert pour le bouton sauvegarde par exemple.
            """
        image = self.liste[self.index][1]
        if self.selected or as_selected:
            image += '_'
        pix = png(image)
        self.setIcon(QIcon(pix))
        self.setIconSize(pix.size())



class BarreOutils(QWidget):
    def __init__(self, parent):
        self.parent = parent
        QWidget.__init__(self, parent)
        self._selected_button = None

        self.sizer = QHBoxLayout()

        self.add2(u"ouvrir", u"Ouvrir un fichier .geo.", self.parent.parent.OpenFile)
        self.btn_sauver = self.add2(u"sauvegarde", u"Enregistrer le document.", self.parent.parent.SaveFile)
        self.add2(u"image", u"Exporter comme image.", self.parent.parent.ExportFile)
        self.add2(u"annuler3", u"Annuler l'action précédente.", self.parent.annuler)
        self.add2(u"retablir3", u"Rétablir une action annulée.", self.parent.retablir)

        if self.parent.param('afficher_boutons'):
            self.creer_boutons()

        self.sizer.addStretch()
        self.setLayout(self.sizer)
        self.adjustSize()


    def add(self, racc, *liste):
        u"""Ajoute des boutons multiples, sélectionnables.

        `racc` est un raccourci. Ex: "Control+F1", "Shift+F2", "Meta+F3", "Alt+F12".
        `liste` est une liste de tuples, ayant le format suivant:
        (titre, nom de l'image, aide, action)
        `liste` peut également contenir `None`, qui sert de séparateur.
        """
        button = MultiButton(self, racc, True, *liste)
        self.sizer.addWidget(button)
        return button


    def add2(self, *args):
        u"""Ajoute des boutons simples, non sélectionnables.


        `args` possède le format suivant:
        nom de l'image, aide, action
        """
        button = MultiButton(self, None, False, ("",) + args)
        self.sizer.addWidget(button)
        return button


    def creer_boutons(self):
        self.add("F1", (u"Pointeur", u"fleche4", u"Déplacer ou modifier un objet.", self.curseur),
                  (u"Zoomer", u"zoombox2", u"Recentrer la zone d'affichage.", self.zoombox),
                  (u"Sélectionner", u"selection", u"Sélectionner une partie de la feuille.",
                  self.selectionner)).select()
        self.add("F2", (u"Point", u"point2",u"Créer un point.", self.point))
        self.add("F3", (u"Milieu", u"milieu2", u"Créer un milieu ou un centre.", self.milieu))
        self.add("F4", (u"Segment", u"segment2", u"Créer un segment.", self.segment),
                    None,
                    (u"Vecteur", u"vecteur", u"Créer un vecteur.", self.vecteur),
                    (u"Représentant d'un vecteur", u"representant",
                    u"Créer un représentant d'un vecteur.", self.representant),
                    )
        self.add("F5", (u"Droite", u"droite2", u"Créer une droite.", self.droite),
                    (u"Demi-droite", u"demidroite", u"Créer une demi-droite.", self.demidroite),
                    None,
                    (u"Parallèle", u"parallele", u"Créer une parallèle.", self.parallele),
                    (u"Perpendiculaire", u"perpendiculaire",
                    u"Créer une perpendiculaire.", self.perpendiculaire),
                    (u"Tangente", u"tangente", u"Créer une tangente.", self.tangente),
                    None,
                    (u"Médiatrice", u"mediatrice", u"Créer une médiatrice.", self.mediatrice),
                    (u"Bissectrice", u"bissectrice", u"Créer une bissectrice.", self.bissectrice),
                    None,
                    (u"Demi-plan", 'demiplan', u"Créer un demi-plan", self.demiplan),
                    None,
                    (u"Axe", u"axe", u"Créer un axe.", self.axe),
                    )
        self.add("F6", (u"Cercle", u"cercle", u"Créer un cercle.", self.cercle),
                    (u"Cercle défini par son diamètre", u"cerclediametre",
                    u"Créer un cercle défini par son diamètre.", self.cercle_diametre),
                    (u"Cercle passant par 3 points", u"cercle3points",
                    u"Créer un cercle passant par 3 points.", self.cercle_points),
                    None,
                    (u"Arc de cercle", u"arc", u"Créer un arc de cercle de centre donné.", self.arc),
                    (u"Arc passant par 3 points", u"arc_points",
                    u"Créer un arc de cercle passant par 3 points.", self.arc_points),
                    (u"Arc de cercle orienté", u"arc_oriente",
                    u"Créer un arc de cercle orienté.", self.arc_oriente),
                    (u"Demi-cercle", u"demicercle", u"Créer un demi-cercle.", self.demicercle),
                    None,
                    (u"Disque", u"disque", u"Créer un disque.", self.disque),
                    )
        self.add("F7", (u"Polygone", u"polygone", u"Créer un polygone.", self.polygone),
                    None,
                    (u"Triangle", u"triangle", u"Créer un triangle.", self.triangle),
                    (u"Triangle rectangle", u"triangle_rectangle",
                    u"Créer un triangle rectangle d'hypothénuse donnée.", self.triangle_rectangle),
                    (u"Triangle isocèle", u"triangle_isocele",
                    u"Créer un triangle isocèle.", self.triangle_isocele),
                    (u"Triangle isocèle rectangle", u"triangle_rectangle_isocele",
                    u"Créer un triangle isocèle rectangle d'hypothénuse donnée.",
                    self.triangle_isocele_rectangle),
                    (u"Triangle équilatéral", u"triangle_equilateral",
                    u"Créer un triangle équilatéral.", self.triangle_equilateral),
                    None,
                    (u"Parallélogramme", u"parallelogramme", u"Créer un parallélogramme.",
                    self.parallelogramme),
                    (u"Rectangle", u"rectangle", u"Créer un rectangle.", self.rectangle),
                    (u"Losange", u"losange", u"Créer un losange.", self.losange),
                    (u"Carré", u"carre", u"Créer un carré.", self.carre),
                    )
        self.add("F8", (u"Intersection", u"intersection", u"Créer une intersection.", self.intersection))
        self.add("F9", (u"Angle", u"angle", u"Créer un angle non orienté.", self.angle),
                    (u"Angle orienté", u"angle_oriente", u"Créer un angle orienté.",
                    self.angle_oriente),
                    )
        self.add("Shift+F1", (u"Symétrie centrale", u"symetrie_centrale",
                    u"Créer l'image d'un objet par symétrie par rapport à un point.", self.symetrie),
                    (u"Réflexion", u"reflexion",
                    u"Créer l'image d'un objet par symétrie axiale.", self.reflexion),
                    (u"Translation", u"translation",
                    u"Créer l'image d'un objet par translation.", self.translation),
                    (u"Rotation", u"rotation",
                    u"Créer l'image d'un objet par rotation autour d'un point.", self.rotation),
                    (u"Homothétie", u"homothetie",
                    u"Créer l'image d'un objet par homothétie.", self.homothetie),
                    )
        self.add("Shift+F2", (u"Texte", u"texte", u"Créer un texte.", self.texte))
        self.add("Shift+F3", (u"Masquer", u"masquer", u"Masquer des objets.", self.masque))
        self.add("Shift+F4", (u"Gommer", u"gomme", u"Supprimer des objets.", self.gomme))
        self.add("Shift+F5", (u"Copier", u"pinceau", u"Copier le style d'un objet.", self.pinceau))


    @property
    def feuille_actuelle(self):
        return self.parent.feuille_actuelle

    @property
    def canvas(self):
        return self.parent.canvas


    def rafraichir(self):
        u"Appelé par le parent pour rafraichir la barre d'outils."
        self.btn_sauver.update_display(as_selected=(not self.feuille_actuelle.modifiee))


    def initialiser(self):
        self.cache = [] # objets en memoire
        # S'il n'y a pas de feuille, on la crée.
        self.feuille_actuelle.objet_temporaire(None)
        self.canvas.liste_objets_en_gras.clear()
        self.canvas.selection_en_gras()


    def dialogue(self, titre, question, defaut=""):
        u"""Certaines constructions ont besoin d'une valeur numérique (rotations, homothéties...)
        Cette boîte de dialogue permet à l'utilisateur de saisir cette valeur.
        Retourne 'None' si l'utilisateur a annulé."""
        valeur, ok = QInputDialog.getText(self, titre, question, QLineEdit.Normal, defaut)
        return valeur if ok else None


    def executer(self, instruction, editer = "defaut", init = True):
        u"""Exécute une instruction dans la console.
        Si editer != None, le nom de l'objet est édité (par défaut, seulement les points, droites et textes),
        afin de permettre de le renommer dans la foulee.
        Si init = True, le cache des selections est initialise."""
        with contexte(unite_angle='r'):
            self.canvas.executer("_ = " + instruction)
        if init:
            self.initialiser()
        if editer == "defaut":
            if isinstance(self.feuille_actuelle.objets["_"], (Texte_generique, Point_generique,
                    Droite_generique, Cercle_generique)):
                editer = self.feuille_actuelle.objets["_"]
            else:
                editer = None
        if editer:
            self.canvas.select = editer
            self.canvas.editer()


    def interagir(self, *args, **kw):
        u"Marque le bouton n comme sélectionné (et initialise le cache des sélections)."
        self.initialiser()
        self.canvas.interagir(*args, **kw)


    def test(self, doublons_interdits = True, **kw):
        u"""On vérifie qu'il y ait encore une feuille, et que le cache ne contienne que des objets
        de la feuille (la feuille a pu changer, ou un objet être supprimé)."""
        if kw.get("special", None) == "ESC":
            self.initialiser()
            return False
        else:
            self.canvas.editeur.close()
##                objets_feuille = self.feuille_actuelle.objets()
            objets_feuille = self.feuille_actuelle.liste_objets(True)
            for obj in self.cache:
                if not is_in(obj, objets_feuille):
                    self.cache.remove(obj)
            # Utiliser l'objet set pour faire l'intersection entre self.cache et self.feuille_actuelle.objets.__dict__.values() ??
            if doublons_interdits and self.cache and kw.get("selection", None) is self.cache[-1]:
                # on évite de rentrer 2 fois de suite le même objet dans le cache (évite de se retrouver avec qqch du style Segment(A,A) par ex.)
                # depuis la version 0.101.3, recliquer sur un objet le supprime du cache.
                self.cache.pop()
                return False
            return True


    def style(self, type_objet):
        u"Retourne le style d'objet défini éventuellement dans les paramètres du module."
        print 'coucou', type_objet
        if not type_objet:
            return {}
        val = getattr(self.parent._param_, type_objet, {})
        assert isinstance(val, dict)
        print val
        return val


#----------------------------------------------------------
#      Fonctions interactives de creation d'objets
#----------------------------------------------------------


    def curseur(self, event = None):
        u"Revenir en mode standard (flêche simple)."
        self.interagir(None, u"Sélectionnez ou déplacez un objet.")
        self.canvas.mode = "defaut"


    def zoombox(self, event = False, **kw):
        u"Mode zoom."
        self.interagir(None, u"Sélectionnez une zone pour zoomer dessus.")
        self.canvas.mode = "zoom"


    def selectionner(self, event = False, **kw):
        u"Sélectionner une zone."
        self.interagir(None, u"Sélectionnez une zone.")
        self.canvas.mode = "select"


    def point(self, event = False, nom_style='points', editer='defaut', **kw):
        if event is not False:
            self.interagir(self.point, u"Cliquez sur un objet, ou dans l'espace vierge.")
        else:
            if kw.get("special", None) == "ESC":
                self.initialiser()
            else:
                selection = kw["selection"]
                position = kw["position"]

                if not selection:
                    self.executer(u"Point(*%s, **%s)" % (position, self.style(nom_style)), editer=editer, init = False)
                else:
                    snom = selection.nom
                    # On regarde si le point peut être construit sur l'objet sélectionné.
                    # Par exemple, si l'objet sélectionné est une droite, on construit
                    # un glisseur sur la droite, au lieu d'un point 'normal'.
                    # Par contre, si l'objet sélectionné est un texte, il n'y a pas de
                    # glisseur correspondant, donc on ne tient pas compte de l'objet
                    # sélectionné, et on construit simplement un point 'normal'.
                    for type_objet, type_glisseur in Point._glisseurs.iteritems():
                        if isinstance(selection, getattr(geolib, type_objet)):
                            self.executer(u"%s(%s, %s)" %(type_glisseur, snom, position), editer=editer, init = False)
                            break
                    else:
                        self.executer(u"Point(%s, %s)" % position, editer=editer, init = False)
                # On retourne le nom de l'objet créé
                # ('_' fait référence au dernier objet créé de la feuille),
                # afin de pouvoir utiliser cette méthode 'point()' comme routine ailleurs.
                return self.feuille_actuelle.objets["_"]



    def milieu(self, event = False, **kw):
        if event is not False:
            self.interagir(self.milieu, u"Choisissez deux points, ou un segment, un cercle, un polygone...")
        elif self.test(True, **kw):
            selection = kw["selection"]
            if isinstance(selection, Point_generique):
                self.cache.append(selection)
            elif isinstance(selection, Polygone_generique):
                self.executer(u"Centre_gravite(%s)" %(selection.nom))
            elif isinstance(selection, Cercle_generique) and not self.cache:
                self.executer(u"Centre(%s)" %(selection.nom))
            elif isinstance(selection, Segment) and not self.cache:
                self.executer(u"Milieu(%s.point1, %s.point2)" %(selection.nom, selection.nom))
            else:
                self.cache.append(self.point(**kw))

            if len(self.cache) == 1:
                self.feuille_actuelle.objet_temporaire(Milieu(self.cache[0], self.feuille_actuelle.point_temporaire()))

            if len(self.cache) == 2:
                self.feuille_actuelle.objet_temporaire(None)
                self.executer(u"Milieu(%s, %s)" %(self.cache[0].nom, self.cache[1].nom))

            if len(self.cache) > 2: # ne se produit que si l'execution a plante...
                self.initialiser()

        elif self.cache:
            self.feuille_actuelle.objet_temporaire(Milieu(self.cache[0], self.feuille_actuelle.point_temporaire()))
        else:
            self.feuille_actuelle.objet_temporaire(None)



    # NB: event doit recevoir par defaut False et non None,
    # car event vaut déjà None par défaut dans MultiButton.action().

    def segment(self, event=False, **kw):
        if event is False:
            self.npoints(Segment, nom_style='segments', **kw)
        else:
            self.interagir(self.segment, u"Choisissez ou cr\xe9ez deux points.")


    def vecteur(self, event=False, **kw):
        if event is False:
            self.npoints(Vecteur, nom_style='vecteurs', **kw)
        else:
            self.interagir(self.vecteur, u"Choisissez ou cr\xe9ez deux points.")

    def axe(self, event = False, **kw):
        if event is False:
            self.npoints(Axe, **kw)
        else:
            self.interagir(self.axe, u"Choisissez ou cr\xe9ez deux points.")

    def droite(self, event = False, **kw):
        if event is False:
            self.npoints(Droite, **kw)
        else:
            self.interagir(self.droite, u"Choisissez ou cr\xe9ez deux points.")

    def demidroite(self, event = False, **kw):
        if event is False:
            self.npoints(Demidroite, **kw)
        else:
            self.interagir(self.demidroite, u"Choisissez ou cr\xe9ez deux points.")

    def mediatrice(self, event = False, **kw):
        if event is not False:
            self.interagir(self.mediatrice, u"Choisissez un segment ou deux points.")
        elif self.test(**kw):
            selection = kw["selection"]

            if isinstance(selection, Point_generique):
                self.cache.append(selection)
                if len(self.cache) == 1:
                    self.feuille_actuelle.objet_temporaire(Mediatrice(selection, self.feuille_actuelle.point_temporaire()))
            elif isinstance(selection, Segment):
                self.executer("Mediatrice(%s.point1, %s.point2)" %(selection.nom, selection.nom))
            else:
                self.cache.append(self.point(**kw))
                if len(self.cache) == 1:
                    self.feuille_actuelle.objet_temporaire(Mediatrice(self.cache[0], self.feuille_actuelle.point_temporaire()))

            if len(self.cache) == 2:
                self.feuille_actuelle.objet_temporaire(None)
                self.executer("Mediatrice(%s, %s)" %(self.cache[0].nom, self.cache[1].nom))

            if len(self.cache) > 2: # ne se produit que si l'execution a plante...
                self.initialiser()



    def bissectrice(self, event = False, **kw): # A REVOIR
        if event is not False:
            self.interagir(self.bissectrice, u"Choisissez un angle ou trois points.")
        elif self.test(**kw):
            selection = kw["selection"]

            if isinstance(selection, Point_generique):
                self.cache.append(selection)
                if len(self.cache) == 2:
                    self.feuille_actuelle.objet_temporaire(Bissectrice(self.cache[0], self.cache[1], self.feuille_actuelle.point_temporaire()))
            elif isinstance(selection, Secteur_angulaire):
                self.executer("Bissectrice(%s.point1, %s.point2, %s.point3)" %(selection.nom, selection.nom, selection.nom))
            else:
                self.cache.append(self.point(**kw))
                if len(self.cache) == 2:
                    self.feuille_actuelle.objet_temporaire(Bissectrice(self.cache[0], self.cache[1], self.feuille_actuelle.point_temporaire()))

            if len(self.cache) == 3:
                self.feuille_actuelle.objet_temporaire(None)
                self.executer("Bissectrice(%s, %s, %s)" %(self.cache[0].nom, self.cache[1].nom,  self.cache[2].nom))

            if len(self.cache) > 3: # ne se produit que si l'execution a plante...
                self.initialiser()


    def perpendiculaire(self, event = False, **kw):
        if event is not False:
            self.interagir(self.perpendiculaire, u"Choisissez ou créez un point et une droite.")
        elif self.test(**kw):
            selection = kw["selection"]
            if len(self.cache) == 0:
                if isinstance(selection, Point_generique):
                    self.cache.append(selection)
                elif isinstance(selection, Ligne_generique):
                    self.cache.append(selection)
                    self.feuille_actuelle.objet_temporaire(Perpendiculaire(selection, self.feuille_actuelle.point_temporaire()))
                else:
                    self.cache.append(self.point(**kw))
            elif len(self.cache) == 1:
                if isinstance(self.cache[0], Ligne_generique):
                    if isinstance(selection, Point_generique):
                        self.cache.append(selection)
                    else:
                        self.cache.append(self.point(**kw))
                elif isinstance(selection, Ligne_generique):
                    self.cache.append(selection)


            if len(self.cache) == 2:
                self.feuille_actuelle.objet_temporaire(None)
                if isinstance(self.cache[0], Point_generique):
                    self.cache.reverse()
                self.executer("Perpendiculaire(%s, %s)" %(self.cache[0].nom, self.cache[1].nom))

            if len(self.cache) > 2: # ne se produit que si l'execution a plante...
                self.initialiser()


    def parallele(self, event = False, **kw):
        if event is not False:
            self.interagir(self.parallele, u"Choisissez ou créez un point et une droite.")
        elif self.test(**kw):
            selection = kw["selection"]
            if len(self.cache) == 0:
                if isinstance(selection, Point_generique):
                    self.cache.append(selection)
                elif isinstance(selection, Ligne_generique):
                    self.cache.append(selection)
                    self.feuille_actuelle.objet_temporaire(Parallele(selection, self.feuille_actuelle.point_temporaire()))
                else:
                    self.cache.append(self.point(**kw))
            elif len(self.cache) == 1:
                if isinstance(self.cache[0], Ligne_generique):
                    if isinstance(selection, Point_generique):
                        self.cache.append(selection)
                    else:
                        self.cache.append(self.point(**kw))
                elif isinstance(selection, Ligne_generique):
                    self.cache.append(selection)


            if len(self.cache) == 2:
                self.feuille_actuelle.objet_temporaire(None)
                if isinstance(self.cache[0], Point_generique):
                    self.cache.reverse()
                self.executer(u"Parallele(%s, %s)" %(self.cache[0].nom, self.cache[1].nom))

            if len(self.cache) > 2: # ne se produit que si l'execution a plante...
                self.initialiser()


    def demiplan(self, event = False, **kw):
        if event is not False:
            self.interagir(self.demiplan, u"Choisissez ou créez un point et une droite.")
        elif self.test(**kw):
            selection = kw["selection"]
            if len(self.cache) == 0:
                if isinstance(selection, Point_generique):
                    self.cache.append(selection)
                elif isinstance(selection, Ligne_generique):
                    self.cache.append(selection)
                    self.feuille_actuelle.objet_temporaire(Demiplan(selection, self.feuille_actuelle.point_temporaire()))
                else:
                    self.cache.append(self.point(**kw))
            elif len(self.cache) == 1:
                if isinstance(self.cache[0], Ligne_generique):
                    if isinstance(selection, Point_generique):
                        self.cache.append(selection)
                    else:
                        self.cache.append(self.point(**kw))
                elif isinstance(selection, Ligne_generique):
                    self.cache.append(selection)


            if len(self.cache) == 2:
                self.feuille_actuelle.objet_temporaire(None)
                if isinstance(self.cache[0], Point_generique):
                    self.cache.reverse()
                self.executer(u"Demiplan(%s, %s)" %(self.cache[0].nom, self.cache[1].nom))

            if len(self.cache) > 2: # ne se produit que si l'execution a plante...
                self.initialiser()


    def tangente(self, event = False, **kw):
        if event is not False:
            self.interagir(self.tangente, u"Choisissez ou cr\u00e9ez un point et un cercle.")
        elif self.test(**kw):
            selection = kw["selection"]
            position = kw["position"]
            if len(self.cache) == 0:
                if isinstance(selection, Point_generique):
                    self.cache.append(selection)
                    self.feuille_actuelle.objet_temporaire(Droite(selection, self.feuille_actuelle.point_temporaire()))
                elif isinstance(selection, Cercle_generique):
                    self.memoire_position = position
                    self.cache.append(selection)
                    self.feuille_actuelle.objet_temporaire(Tangente(selection, self.feuille_actuelle.point_temporaire()))
                else:
                    self.cache.append(self.point(**kw))
                    self.feuille_actuelle.objet_temporaire(Droite(self.cache[0], self.feuille_actuelle.point_temporaire()))
            elif len(self.cache) == 1:
                if isinstance(self.cache[0], Cercle_generique):
                    if isinstance(selection, Point_generique):
                        self.cache.append(selection)
                    else:
                        self.cache.append(self.point(**kw))
                elif isinstance(selection, Cercle_generique):
                    self.cache.append(selection)


            if len(self.cache) == 2:
                self.feuille_actuelle.objet_temporaire(None)
                if isinstance(self.cache[0], Point_generique):
                    self.cache.reverse()
                else:
                    position = self.memoire_position
                x1, y1 = self.cache[0].centre   # on choisit la tangente qui passe le plus près du point du cercle sélectionné
                x, y = position
                x2, y2 = self.cache[1]
                det = (x1 - x)*(y2 - y) - (x2 - x)*(y1 - y)

                self.executer(u"Tangente(%s, %s, %s)" %(self.cache[0].nom, self.cache[1].nom, det>0))

            if len(self.cache) > 2: # ne se produit que si l'exécution a plantée...
                self.initialiser()


    def representant(self, event = False, **kw):
        if event is not False:
            self.interagir(self.representant, u"Choisissez ou créez un point et un vecteur.")
        elif self.test(**kw):
            selection = kw["selection"]
            if len(self.cache) == 0:
                if isinstance(selection, Point_generique):
                    self.cache.append(selection)
                elif isinstance(selection, Vecteur):
                    self.cache.append(selection)
                    M = self.feuille_actuelle.point_temporaire()
                    self.feuille_actuelle.objet_temporaire(Vecteur(M, Translation(selection)(M)))
                else:
                    self.cache.append(self.point(**kw))
            elif len(self.cache) == 1:
                if isinstance(self.cache[0], Vecteur):
                    if isinstance(selection, Point_generique):
                        self.cache.append(selection)
                    else:
                        self.cache.append(self.point(**kw))
                elif isinstance(selection, Vecteur):
                    self.cache.append(selection)


            if len(self.cache) == 2:
                self.feuille_actuelle.objet_temporaire(None)
                if isinstance(self.cache[0], Point_generique):
                    self.cache.reverse()
                self.executer(u"Representant(%s, %s)" %(self.cache[0].nom, self.cache[1].nom))

            if len(self.cache) > 2: # ne se produit que si l'execution a plante...
                self.initialiser()




    def translation(self, event = False, **kw):
        if event is not False:
            self.interagir(self.translation, u"Choisissez ou créez un objet, puis indiquez le vecteur de la translation.")
        elif self.test(**kw):
            selection = kw["selection"]
            if len(self.cache) == 0:
                if isinstance(selection, Objet):
                    self.cache.append(selection)
                else:
                    self.cache.append(self.point(**kw))
            elif len(self.cache) == 1:
                if isinstance(selection, Vecteur_generique):
                    self.cache.append(selection)

            if len(self.cache) == 2:
                self.executer(u"Translation(%s)(%s)" %(self.cache[1].nom, self.cache[0].nom))

            if len(self.cache) > 2: # ne se produit que si l'execution a plante...
                self.initialiser()


    def symetrie(self, event = False, **kw):
        if event is not False:
            self.interagir(self.symetrie, u"Choisissez ou créez un objet, puis indiquez ou créez le centre de symétrie.")
        elif self.test(**kw):
            selection = kw["selection"]
            if len(self.cache) == 0:
                if isinstance(selection, Objet):
                    self.cache.append(selection)
                else:
                    self.cache.append(self.point(**kw))
            elif len(self.cache) == 1:
                if isinstance(selection, Point_generique):
                    self.cache.append(selection)
                else:
                    self.cache.append(self.point(**kw))

            if len(self.cache) == 2:
                self.executer(u"Symetrie_centrale(%s)(%s)" %(self.cache[1].nom, self.cache[0].nom))

            if len(self.cache) > 2: # ne se produit que si l'execution a plante...
                self.initialiser()


    def reflexion(self, event = False, **kw):
        if event is not False:
            self.interagir(self.reflexion, u"Choisissez ou créez un objet, puis indiquez l'axe de la réflexion.")
        elif self.test(**kw):
            selection = kw["selection"]
            if len(self.cache) == 0:
                if isinstance(selection, Objet):
                    self.cache.append(selection)
                else:
                    self.cache.append(self.point(**kw))
            elif len(self.cache) == 1:
                if isinstance(selection, Ligne_generique):
                    self.cache.append(selection)

            if len(self.cache) == 2:
                self.executer(u"Reflexion(%s)(%s)" %(self.cache[1].nom, self.cache[0].nom))

            if len(self.cache) > 2: # ne se produit que si l'execution a plante...
                self.initialiser()


    def rotation(self, event = False, **kw):
        if event is not False:
            self.interagir(self.rotation, u"Choisissez ou créez un objet, puis indiquez le centre de la rotation, et l'angle.")
        elif self.test(**kw):
            selection = kw["selection"]
            if len(self.cache) == 0:
                if isinstance(selection, Objet):
                    self.cache.append(selection)
                else:
                    self.cache.append(self.point(**kw))
            elif len(self.cache) == 1:
                if isinstance(selection, (Point_generique, Angle_generique)):
                    self.cache.append(selection)
                else:
                    self.cache.append(self.point(**kw))
                if not isinstance(selection, Angle_generique):
                    angle = self.dialogue(u"Angle", u"Indiquez l'angle de la rotation.", u"45°")
                    if angle is None:
                        self.initialiser()
                    else:
                        self.executer(u"Rotation(%s,%s)(%s)" %(self.cache[1].nom, repr(angle), self.cache[0].nom))

            elif len(self.cache) == 2:
                if isinstance(selection, Point_generique):
                    self.cache.append(selection)
                else:
                    self.cache.append(self.point(**kw))
                self.executer(u"Rotation(%s,%s)(%s)" %(self.cache[2].nom, self.cache[1].nom, self.cache[0].nom))

            if len(self.cache) > 2: # ne se produit que si l'execution a plante...
                self.initialiser()


    def homothetie(self, event = False, **kw):
        if event is not False:
            self.interagir(self.homothetie, u"Choisissez ou créez un objet, puis indiquez le centre de l'homothétie, et son rapport.")
        elif self.test(**kw):
            selection = kw["selection"]
            if len(self.cache) == 0:
                if isinstance(selection, Objet):
                    self.cache.append(selection)
                else:
                    self.cache.append(self.point(**kw))
            elif len(self.cache) == 1:
                if isinstance(selection, Point_generique):
                    self.cache.append(selection)
                else:
                    self.cache.append(self.point(**kw))

                k = self.dialogue(u"Rapport", u"Indiquez le rapport de l'homothétie.", u"2")
                if k is None:
                    self.initialiser()
                else:
                    self.executer(u"Homothetie(%s,%s)(%s)" %(self.cache[1].nom, repr(k), self.cache[0].nom))

            if len(self.cache) > 2: # ne se produit que si l'execution a plante...
                self.initialiser()


    def cercle(self, event = False, **kw):
        if event is False:
            self.npoints(Cercle, **kw)
        else:
            self.interagir(self.cercle, u"Choisissez ou créez deux points.")

    def cercle_diametre(self, event = False, **kw):
        if event is False:
            self.npoints(Cercle_diametre, **kw)
        else:
            self.interagir(self.cercle_diametre, u"Choisissez ou créez deux points.")

    def cercle_points(self, event = False, **kw):
        if event is False:
            self.npoints(Cercle_points, 3, **kw)
        else:
            self.interagir(self.cercle_points, u"Choisissez ou créez 3 points.")

    def arc(self, event = False, **kw):
        if event is False:
            self.npoints(Arc_cercle, 3, **kw)
        else:
            self.interagir(self.arc, u"Choisissez ou créez 3 points.")

    def demicercle(self, event = False, **kw):
        if event is False:
            self.npoints(Demicercle, **kw)
        else:
            self.interagir(self.demicercle, u"Choisissez ou créez deux points.")

    def arc_points(self, event = False, **kw):
        if event is False:
            self.npoints(Arc_points, 3, **kw)
        else:
            self.interagir(self.arc_points, u"Choisissez ou créez 3 points.")

    def arc_oriente(self, event = False, **kw):
        if event is False:
            self.npoints(Arc_oriente, 3, nom_style="arcs_orientes", **kw)
        else:
            self.interagir(self.arc_oriente, u"Choisissez ou créez 3 points.")

    def disque(self, event = False, **kw):
        if event is not False:
            self.interagir(self.disque, u"Choisissez un cercle.")
        elif self.test(**kw):
            selection = kw["selection"]
            if isinstance(selection, Cercle_generique):
                self.executer(u"Disque(%s)" %selection.nom)


    def angle(self, event = False, **kw):
        if event is False:
            self.npoints(Angle, 3, **kw)
        else:
            self.interagir(self.angle, u"Choisissez ou créez trois points.")


    def angle_oriente(self, event = False, **kw):
        if event is False:
            self.npoints(Angle_oriente, 3, **kw)
        else:
            self.interagir(self.angle_oriente, u"Choisissez ou créez trois points.")



    def triangle_rectangle(self, event = False, **kw):
        if event is not False:
            self.interagir(self.triangle_rectangle, u"Choisissez ou créez deux points.")
        elif self.test(True, **kw):
            selection = kw["selection"]

            if isinstance(selection, Point_generique):
                self.cache.append(selection)
            else:
                self.cache.append(self.point(**kw))

            if len(self.cache) == 1:
                A = self.cache[0]
                B = self.feuille_actuelle.point_temporaire()
                I = Milieu(A, B)
                C = Rotation(I, pi/3, unite='r')(B)
                self.feuille_actuelle.objet_temporaire(PrevisualisationPolygone(A, B, C, A))
            elif len(self.cache) == 2:
                self.feuille_actuelle.objet_temporaire(None)
                self.executer(u"Triangle_rectangle(%s,%s, pi/6)" %(self.cache[0].nom, self.cache[1].nom))
        else:
            self.feuille_actuelle.objet_temporaire(None)


    def triangle_isocele(self, event = False, **kw):
        if event is not False:
            self.interagir(self.triangle_isocele, u"Choisissez ou créez deux points.")
        elif self.test(True, **kw):
            selection = kw["selection"]

            if isinstance(selection, Point_generique):
                self.cache.append(selection)
            else:
                self.cache.append(self.point(**kw))

            if len(self.cache) == 1:
                A = self.cache[0]
                B = self.feuille_actuelle.point_temporaire()
                C = Rotation(A, pi/5, unite='r')(B)
                self.feuille_actuelle.objet_temporaire(PrevisualisationPolygone(A, B, C, A))
            elif len(self.cache) == 2:
                self.feuille_actuelle.objet_temporaire(None)
                self.executer(u"Triangle_isocele(%s,%s, pi/5)" %(self.cache[0].nom, self.cache[1].nom))
        else:
            self.feuille_actuelle.objet_temporaire(None)


    def triangle_isocele_rectangle(self, event = False, **kw):
        if event is not False:
            self.interagir(self.triangle_isocele_rectangle, u"Choisissez ou créez deux points.")
        elif self.test(True, **kw):
            selection = kw["selection"]

            if isinstance(selection, Point_generique):
                self.cache.append(selection)
            else:
                self.cache.append(self.point(**kw))

            if len(self.cache) == 1:
                A = self.cache[0]
                B = self.feuille_actuelle.point_temporaire()
                I = Milieu(A, B)
                C = Rotation(I, pi/2, unite='r')(B)
                self.feuille_actuelle.objet_temporaire(PrevisualisationPolygone(A, B, C, A))
            elif len(self.cache) == 2:
                self.feuille_actuelle.objet_temporaire(None)
                self.executer(u"Triangle_isocele_rectangle(%s,%s)" %(self.cache[0].nom, self.cache[1].nom))
        else:
            self.feuille_actuelle.objet_temporaire(None)


    def triangle_equilateral(self, event = False, **kw):
        if event is not False:
            self.interagir(self.triangle_equilateral, u"Choisissez ou créez deux points.")
        elif self.test(True, **kw):
            selection = kw["selection"]

            if isinstance(selection, Point_generique):
                self.cache.append(selection)
            else:
                self.cache.append(self.point(**kw))

            if len(self.cache) == 1:
                A = self.cache[0]
                B = self.feuille_actuelle.point_temporaire()
                C = Rotation(A, pi/3, unite='r')(B)
                self.feuille_actuelle.objet_temporaire(PrevisualisationPolygone(A, B, C, A))
            elif len(self.cache) == 2:
                self.feuille_actuelle.objet_temporaire(None)
                self.executer(u"Triangle_equilateral(%s,%s)" %(self.cache[0].nom, self.cache[1].nom))
        else:
            self.feuille_actuelle.objet_temporaire(None)


    def rectangle(self, event = False, **kw):
        if event is not False:
            self.interagir(self.rectangle, u"Choisissez ou créez deux points.")
        elif self.test(True, **kw):
            selection = kw["selection"]

            if isinstance(selection, Point_generique):
                self.cache.append(selection)
            else:
                self.cache.append(self.point(**kw))

            if len(self.cache) == 1:
                A = self.cache[0]
                B = self.feuille_actuelle.point_temporaire()
                C = Homothetie(B, 1.4)(Rotation(B, -pi/2, unite='r')(A))
                D = Barycentre((A, 1), (B, -1), (C, 1))
                self.feuille_actuelle.objet_temporaire(PrevisualisationPolygone(A, B, C, D, A))
            elif len(self.cache) == 2:
                self.feuille_actuelle.objet_temporaire(None)
                self.executer(u"Rectangle(%s,%s,1.4)" %(self.cache[0].nom, self.cache[1].nom))
        else:
            self.feuille_actuelle.objet_temporaire(None)


    def losange(self, event = False, **kw):
        if event is not False:
            self.interagir(self.losange, u"Choisissez ou créez deux points.")
        elif self.test(True, **kw):
            selection = kw["selection"]

            if isinstance(selection, Point_generique):
                self.cache.append(selection)
            else:
                self.cache.append(self.point(**kw))

            if len(self.cache) == 1:
                B = self.cache[0]
                C = self.feuille_actuelle.point_temporaire()
                A = Rotation(B, pi/5, unite='r')(C)
                D = Barycentre((A, 1), (B, -1), (C, 1))
                self.feuille_actuelle.objet_temporaire(PrevisualisationPolygone(A, B, C, D, A))
            elif len(self.cache) == 2:
                self.feuille_actuelle.objet_temporaire(None)
                self.executer(u"Losange(%s,%s,pi/5)" %(self.cache[0].nom, self.cache[1].nom))
        else:
            self.feuille_actuelle.objet_temporaire(None)


    def carre(self, event = False, **kw):
        if event is not False:
            self.interagir(self.carre, u"Choisissez ou créez deux points.")
        elif self.test(True, **kw):
            selection = kw["selection"]

            if isinstance(selection, Point_generique):
                self.cache.append(selection)
            else:
                self.cache.append(self.point(**kw))

            if len(self.cache) == 1:
                A = self.cache[0]
                B = self.feuille_actuelle.point_temporaire()
                C = Rotation(B, -pi/2, unite='r')(A)
                D = Rotation(A, pi/2, unite='r')(B)
                self.feuille_actuelle.objet_temporaire(PrevisualisationPolygone(A, B, C, D, A))
            elif len(self.cache) == 2:
                self.feuille_actuelle.objet_temporaire(None)
                self.executer(u"Carre(%s,%s)" %(self.cache[0].nom, self.cache[1].nom))
        else:
            self.feuille_actuelle.objet_temporaire(None)


    def triangle(self, event = False, **kw):
        if event is not False:
            self.interagir(self.triangle, u"Choisissez ou créez trois points.")
        elif self.test(True, **kw):
            selection = kw["selection"]

            if isinstance(selection, Point_generique):
                self.cache.append(selection)
            else:
                self.cache.append(self.point(**kw))

            if 1 <= len(self.cache) <= 2:
                points = self.cache + [self.feuille_actuelle.point_temporaire()]
                self.feuille_actuelle.objet_temporaire(PrevisualisationPolygone(*points))
            elif len(self.cache) == 3:
                self.executer(u"Triangle(" + ",".join(obj.nom for obj in self.cache) + ")")
        elif len(self.cache):
            points = self.cache + [self.feuille_actuelle.point_temporaire()]
            self.feuille_actuelle.objet_temporaire(PrevisualisationPolygone(*points))
        else:
            self.feuille_actuelle.objet_temporaire(None)



    def parallelogramme(self, event = False, **kw):
        if event is not False:
            self.interagir(self.parallelogramme, u"Choisissez ou créez trois points.")
        elif self.test(True, **kw):
            selection = kw["selection"]

            if isinstance(selection, Point_generique):
                self.cache.append(selection)
            else:
                self.cache.append(self.point(**kw))

            if len(self.cache) == 2:
                A, B = self.cache
                C = self.feuille_actuelle.point_temporaire()
                D = Barycentre((A, 1), (B, -1), (C, 1))
                self.feuille_actuelle.objet_temporaire(PrevisualisationPolygone(A, B, C, D))
            elif len(self.cache) == 3:
                self.executer(u"Parallelogramme(" + ",".join(obj.nom for obj in self.cache) + ")")


    def polygone(self, event = False, **kw):
        if event is not False:
            self.interagir(self.polygone, u"Indiquez les sommets, puis cliquez sur le 1er sommet.")
        elif self.test(True, **kw):
            #self.cache = [obj for obj in self.cache if obj.nom and obj.__feuille__ == self.feuille_actuelle]
            selection = kw["selection"]

            if isinstance(selection, Point_generique):
                self.cache.append(selection)
            else:
                self.cache.append(self.point(**kw))

            if len(self.cache) >= 1:
                self.canvas.liste_objets_en_gras.append(self.cache[0])
                self.canvas.selection_en_gras()
##                self.cache[0].affiche_en_gras(True)

            if len(self.cache) > 2 and self.cache[0] is self.cache[-1]:
                # On crée le polygone
                self.feuille_actuelle.objet_temporaire(None)
#                cache = self.cache
#                self.initialiser()
                self.executer(u"Polygone(" + ",".join(obj.nom for obj in self.cache[:-1]) + ")")
            elif len(self.cache) >= 1:
                # Le polygone n'est pas encore complet
                tmp = self.feuille_actuelle.objet_temporaire() # liste des objets temporaires
                if tmp and isinstance(tmp[-1], PrevisualisationPolygone): # on ne recrée pas la prévisualisation, on se contente d'ajouter un sommet
                    tmp = tmp[-1]
                    tmp.points = tmp.points[:-1] + (self.cache[-1], self.feuille_actuelle.point_temporaire())
                else:
                    points = self.cache + [self.feuille_actuelle.point_temporaire()]
                    self.feuille_actuelle.objet_temporaire(PrevisualisationPolygone(*points))
        elif self.cache:
            # Recliquer sur un objet le supprime du cache (cf. self.test())
            tmp = self.feuille_actuelle.objet_temporaire()[-1]
            tmp.points = tmp.points[:-2] + (self.feuille_actuelle.point_temporaire(),) # on supprime un sommet
        else:
            self.feuille_actuelle.objet_temporaire(None)






    def intersection(self, event = False, **kw):
        def inter_dte_cer(dte, cer, position):
            u"Sert à detecter l'intersection la plus proche du pointeur."
            intersections = Intersection_droite_cercle(dte, cer, True).intersections
            if len(intersections) == 2:
                # 2 points d'intersection -> on regarde le plus proche du pointeur
                xy0, xy1 = intersections
                xy0 = self.canvas.coo2pix(*xy0)
                xy1 = self.canvas.coo2pix(*xy1)
                position = self.canvas.coo2pix(*position)
                test = distance(position, xy0) < distance(position, xy1)
            else:
                test = True
            self.executer(u"Intersection_droite_cercle(%s, %s, %s)" %(dte.nom, cer.nom, test))

        if event is not False:
            self.interagir(self.intersection, u"Indiquez deux objets, ou le lieu de l'intersection.")
        elif self.test(**kw):
            selection = kw["selection"]
            autres = kw["autres"] # autres objets a proximite
            position = kw["position"]

            if isinstance(selection, (Segment, Demidroite, Droite_generique, Cercle_generique, Arc_generique)):
                self.cache.append(selection)

            if len(self.cache) == 1:  # permet de construire une intersection en 1 clic.
                objets = [obj for obj in autres if obj is not selection and isinstance(obj,(Segment, Demidroite, Droite_generique, Cercle_generique, Arc_generique))]
                if len(objets) == 1:  # il n'y a pas d'ambiguite sur le 2eme objet.
                    self.cache += objets


            if len(self.cache) == 2:
                obj1, obj2 = self.cache
                #self.initialiser() #inutile
                if isinstance(obj1, (Droite_generique, Segment, Demidroite)) \
                        and isinstance(obj2, (Droite_generique, Segment, Demidroite)):
                    self.executer(u"Intersection_droites(%s, %s)" %(obj1.nom, obj2.nom))
                elif isinstance(obj1, (Cercle_generique, Arc_generique)) \
                        and isinstance(obj2, (Cercle_generique, Arc_generique)):
                    M = Intersection_cercles(obj1, obj2)
                    if len(M.intersections) == 2:
                        xy0, xy1 = M.intersections
                        xy0 = self.canvas.coo2pix(*xy0)
                        xy1 = self.canvas.coo2pix(*xy1)
                        position = self.canvas.coo2pix(*position)
                        if distance(position, xy0) < distance(position, xy1):
                            # M est bien l'intersection la plus proche
                            angle = M.angle_positif
                        else:
                            angle = not M.angle_positif
                    else:
                        angle = M.angle_positif
                    self.executer(u"Intersection_cercles(%s, %s, %s)" %(obj1.nom, obj2.nom, angle))
                elif isinstance(obj1, (Droite_generique, Segment, Demidroite)) and isinstance(obj2, (Cercle_generique, Arc_generique)):
                    inter_dte_cer(obj1, obj2, position)
                else:
                    inter_dte_cer(obj2, obj1, position)

            if len(self.cache) > 2: # ne se produit que si l'execution a plante...
                self.initialiser()




    def texte(self, event = False, **kw):
        if event is not False:
            self.interagir(self.texte, u"Cliquez à l'emplacement souhaité.")
        elif self.test(**kw):
            position = kw["position"]
            self.executer(u"Texte('', %s, %s)" % position, init = False)



    def masque(self, event = False, **kw):
        if event is False:
            selection = kw["selection"]
            if selection is not None:
                self.canvas.executer("%s.cacher()" %selection.nom)
        else:
            self.interagir(self.masque)



    def gomme(self, event = False, **kw):
        if event is False:
            selection = kw["selection"]
            if selection is not None:
                self.canvas.executer("%s.supprimer()" %selection.nom)
        else:
            self.interagir(self.gomme)

    def pinceau(self, event = False, **kw):
        if event is not False:
            self.interagir(self.pinceau, u"Sélectionnez un objet pour en copier le style.")
        elif self.test(**kw):
            selection = kw["selection"]
            if selection is not None:
                if len(self.cache) == 0:
                    self.cache.append(selection)
                else:
                    self.canvas.executer("%s.copier_style(%s)" %(selection.nom, self.cache[0].nom))
            if len(self.cache):
                self.canvas.liste_objets_en_gras.append(self.cache[0])
                self.canvas.selection_en_gras()




    def npoints(self, classe, n=2, nom_style='', **kw):
        u"Création d'un objet de classe 'classe' ayant 'n' points comme arguments. Le nom de l'objet sera composé de 'prefixe' + 1 numéro."
        if self.test(True, **kw):
            self.cache = [obj for obj in self.cache if obj.nom and obj.feuille is self.feuille_actuelle]
            selection = kw["selection"]

            if isinstance(selection, Point_generique):
                self.cache.append(selection)
                nouveau_point = False
            else:
                self.cache.append(self.point(**kw))
                nouveau_point = True

            if len(self.cache) == n - 1:
                style = self.style(nom_style)
                style["previsualisation"] = True
                self.feuille_actuelle.objet_temporaire(classe(*(tuple(self.cache) + (self.feuille_actuelle.point_temporaire(),)), **style))

            elif len(self.cache) == n:
                self.feuille_actuelle.objet_temporaire(None)
                code = classe.__name__ + "(" + ",".join(obj.nom for obj in self.cache) + ", **%s)" %self.style(nom_style)
                if nouveau_point: # on edite le nom du nouveau point (dernier parametre de self.executer)
                    self.executer(code, editer = self.cache[-1])
                else: # si c'est un vieux point, pas besoin d'editer son nom
                    self.executer(code)

            elif len(self.cache) > n: # ne se produit que si l'execution a plante...
                self.initialiser()

        elif self.cache:
            style = self.style(nom_style)
            style["previsualisation"] = True
            self.feuille_actuelle.objet_temporaire(classe(*(tuple(self.cache) + (self.feuille_actuelle.point_temporaire(),)), **style))
        else:
            self.feuille_actuelle.objet_temporaire(None)
