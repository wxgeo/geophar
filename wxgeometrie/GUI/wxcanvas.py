# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

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

import re
from cStringIO import StringIO

from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import QMenu, QCursor, QImage
from numpy import array
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg

from ..API.canvas import Canvas
from .app import app
from .menu_objet import MenuActionsObjet
from .proprietes_objets import Proprietes
from .wxlib import (BusyCursor, shift_down, alt_down, ctrl_down, left_down,
                   right_down, lieu)
from .. import param
from ..pylib import print_error, debug
from ..geolib.textes import Texte
from ..geolib.objet import Objet
from ..geolib.constantes import NOM

class MiniEditeur:
    def __init__(self, parent):
        self.parent = parent
        self.objet = None


    def init(self, objet, mode = 0):
        u"""Edition d'un nouvel objet.
        mode = 0: édition du nom de l'objet
        mode = 1: édition de l'étiquette de l'objet"""
        self.close() # finalise l'éventuelle édition en cours
        self.texte = ""
        self.objet = objet
#        self.old_label = objet.label()
        self.mode = mode #
        self.display()

    def display(self):
        self.objet.label_temporaire = self.texte

    def cancel(self):
        self.objet.label_temporaire = None
        self.objet = None


    def ok(self):
        canvas = self.parent
        panel = canvas.parent
        # NB: si aucun nom n'est rentré, [ENTREE] est un équivalent de [ECHAP].
        if self.texte:
            try: # si possible, on change le nom de l'objet ; sinon, on change son label.
                nom = self.objet.nom
                if isinstance(self.objet, Texte) or not re.match("""[A-Za-z_][A-Za-z0-9_'"`]*$""", self.texte):
                    self.mode = 1 # label
                if self.mode:
                    self.objet.label(self.texte)
                    panel.action_effectuee(u"%s.label(%s)" %(nom, repr(self.texte)))
                else:
                    self.objet.renommer(self.texte, legende = NOM)
                    panel.action_effectuee(u"%s.renommer(%s, legende = %s)" %(nom, repr(self.texte), NOM))
            except RuntimeError: # on reste en mode edition
                if not param.nom_multiple:
                    self.display()
                    raise
                self.objet.label(self.texte) # par défaut, si A est réattribué à un point, il sera traité comme étiquette.
                panel.action_effectuee(u"%s.label(%s)" %(nom, repr(self.texte)))
                canvas.message(u"Attention : ce nom est déjà attribué.")
            except:
                self.display()
                raise
        self.cancel()


    def key(self, key, txt, modifiers):
        if self:
            if key == Qt.Key_BackSpace:
                self.texte = self.texte[:-1]
                self.display()
            elif key == Qt.Key_Escape:
                self.cancel()
            elif key in (Qt.Key_Enter, Qt.Key_Return):
                if Qt.ControlModifier & modifiers:
                    self.texte += "\n"
                    self.display()
                else:
                    self.ok()
            ##elif key == 10: # Ctrl + Entree (à tester sous Linux !)
                ### XXX: Technique non portable, à modifier !
            elif 32 <= key <= 255:
                self.texte += txt
                self.display()
            else:
                return False
            return True
        # return None si non actif

    def close(self):
        u"Ferme l'éditeur. Ne renvoie pas d'erreur s'il est déjà fermé."
        if self:
            try:
                self.ok()
            except:
                self.cancel()
                print_error()


    def __nonzero__(self):
        return self.objet is not None






class QtCanvas(FigureCanvasQTAgg, Canvas):
    def __init__(self, parent, fixe = False):
        u"Si fixe = True, l'utilisateur ne peut pas zoomer ou recadrer la fenêtre d'affichage avec la souris."

        self.parent = parent
        # initialisation dans cet ordre (self.figure doit être défini pour initialiser FigureCanvas)
        Canvas.__init__(self, couleur_fond = self.param("couleur_fond"))
        FigureCanvasQTAgg.__init__(self, self.figure)

        ##if param.plateforme == "Linux":
            ##self.SetSize(wx.Size(10, 10))
        ##elif param.plateforme == "Windows":
            ##self.SetWindowStyle(wx.WANTS_CHARS)
            ##self.Refresh()

        self.debut_zoom = None
        # Utilisé pour zoomer avec Ctrl + Clic gauche (contiendra la position initiale)
        self.debut_select = None
        # Utilisé pour sélectionner simultanément plusieurs objets avec Alt + Clic gauche (pos. initiale)
        self.debut_shift = None
        # Utilisé pour translater le contenu de la fenêtre (position initiale)
        self.redetecter = True
        # Rechercher les objets à proximité du pointeur

        self.select_memoire = None
        # Objet devant être prochainement sélectionné (en cas de "litige" entre 2 objets)
        self.etiquette_selectionnee = None # étiquette couramment séléctionnée
        self.fixe = fixe
        self.interaction = None
        # Fonction à lancer au prochain clic de souris (au lieu des actions par défaut)
        self.interaction_deplacement = None
        # Fonction à lancer au prochain déplacement de souris (au lieu des actions par défaut)
        self.editeur = MiniEditeur(self) # edite les noms et etiquettes des points, textes, etc.

        # Paramètres temporaires d'affichage
        self._dessin_temporaire = False


        self.sel = []
        # Liste ordonnée (pour la détection) des objets de la feuille actuelle.
        self.motion_event = None
        self.wheel_event_count = 0
        self.wheel_ctrl_event_count = 0

        ##self.Bind(wx.EVT_MOUSEWHEEL, self.EventOnWheel)
        ##self.Bind(wx.EVT_MOTION, self.EventOnMotion)
        ##self.Bind(wx.EVT_IDLE, self.OnIdle)

        timer = QTimer(self)
        timer.timeout.connect(self._actualiser_si_necessaire)
        timer.start(150)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)



    @property
    def feuille_actuelle(self):
        return self.parent.feuille_actuelle

    def param(self, *args, **kw):
        return self.parent.param(*args, **kw)

    def message(self, txt, lieu = 0):
        self.window().message(txt, lieu) # cf. geometrie.py

    def _curseur(self, sablier):
        if sablier:
            app.setOverrideCursor(Qt.WaitCursor)
        else:
            app.restoreOverrideCursor()

    @property
    def dimensions(self):
        if self._dimensions is None:
            s = self.size()
            return s.width(), s.height()
        return self._dimensions


    def _affiche_module(self):
        u"Affichage spécifique au module en cours."
        self.parent._affiche()

    def exporter(self, *args, **kw):
        with BusyCursor():
            Canvas.exporter(self, *args, **kw)

    def Copy_to_Clipboard(self):
        output = StringIO()
        self.figure.savefig(output, format='png')
        img = QImage()
        img.loadFromData(output.getvalue(), 'PNG')
        app.clipboard().setImage(img)


#    Gestion des evenements (essentiellement la souris).
###############################

    def coordonnees(self, event, dx = 0, dy = 0):
        u"""Renvoie les coordonnées correspondant à l'évènement, converties en coordonnées de la feuille.
        Si [Maj] est enfoncée, les coordonnées sont arrondies à la graduation la plus proche.
        dx et dy correspondent au décalage entre les coordonnées de l'objet, et le point où on l'a saisit.
        (Par exemple, un texte n'est pas forcément saisi au niveau de son point d'ancrage).
        """
        x, y = self.pix2coo(*lieu(event))
        if shift_down(event) or self.grille_aimantee:
            a, b = self.gradu
            return a*round((x + dx)/a), b*round((y + dy)/b)
        else:
            return float(x + dx), float(y + dy)



    def interagir(self, fonction, aide = None, fonction_bis = None):
        u"""Permet l'interaction du canevas avec un module externe.

        A chaque clic de souris, la fonction indiquée est appelée, avec
        un certains nombre de paramètres comme arguments :
        objet(s) à proximité, position en coordonnées et en pixels...

        Une aide est éventuellement affichée dans la barre d'état de la fenêtre principale.

        fonction_bis est éventuellement utilisée lors de chaque déplacement de la souris.
        Elle reçoit en argument la position en pixels uniquement (pour ne pas alourdir le traitement).

        Exemple de récupération des arguments :
        si un module appelle self.canvas.interagir(ma_fonction, u"Cliquez n'importe où.", ma_2eme_fonction),
        le module doit définir :

        def ma_fonction(self, **kw):
            pixel = kw["pixel"]
            position = kw["position"]
            objet_selectionne = kw["selection"]
            autres_objets_a_proximite = kw["autres"]
            print u"clic!"

        def ma_2eme_fonction(self, **kw):
            pixel = kw["pixel"]
            print u"ça bouge !"

        """

        self.interaction = fonction
        self.interaction_deplacement = fonction_bis
        if fonction:
            self.setCursor(Qt.WhatsThisCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        if aide is not None:
            self.message(aide)


    def signal(self, event = None):
        if self.interaction:
            pixel = lieu(event)
            self.detecter(pixel)
            self.interaction(selection = self.select, autres = self.selections, position = self.coordonnees(event), pixel = pixel)
            self.detecter(pixel) # XXX: toujours utile ?


    def deplacable(self, obj): # indique si un objet est deplacable
        return isinstance(obj, Objet) and obj._deplacable

    def pointable(self, obj): # indique si un objet possede des coordonnees
        return isinstance(obj, Objet) and obj._pointable


    def infos(self):
        self.message(self.select.info if self.select is not None else '')


    def detecter(self, position = None):
        u"""Détecte les objets à proximité de la position indiquée.
        Typiquement, on utilise self.detecter(lieu(event))."""

        self.redetecter = False
        self.debut_zoom = None
        actuelle = self.feuille_actuelle # feuille courante

        if not self.affichage_gele:
            if position is None:
                position = lieu(self)
            if param.afficher_coordonnees: # affichage des coordonnees dans la barre d'etat
                self.message(str(self.pix2coo(*position)), 1)
            elif param.afficher_pixels:
                # pour débogage
                self.message(str(position) + ' -> ' + str(self.pix2coo(*position)), 1)
            x, y = position
            # on place les objets 'modifiables' en premier (points libres, glisseurs, textes)
            self.sel = actuelle.liste_objets(tri = True)
            # liste des objets pres du pointeur de la souris :
            self.selections = []
            for obj in self.sel:
                try:
                    if obj.distance_inf(x, y, param.precision_selection):
                        self.selections.append(obj)
                except:
                    print_error()
                    self.message(u"Erreur: les coordonnées de %s sont incalculables." %obj.nom)
            proximite = len(self.selections)
            if proximite:
                self.select = self.selections[0]
                if self.select_memoire and self.select_memoire in self.selections:
                    self.select = self.select_memoire
                if self.interaction:
                    self.setCursor(Qt.WhatsThisCursor)
                else:
                    if self.deplacable(self.select):
                        self.setCursor(Qt.PointingHandCursor)
                    else:
                        self.setCursor(Qt.ArrowCursor)
                self.infos()
            else:
                if self.interaction:
                    self.setCursor(Qt.WhatsThisCursor)
                else:
                    self.setCursor(Qt.ArrowCursor)
                self.message("")
                self.select = None
            self.selection_en_gras()


    def wheelEvent(self, event):
        u"Gestion du zoom par la roulette de la souris."
        pas = event.delta()/120.
        if ctrl_down(event):
            # Grossir textes et lignes (ne pas changer la fenêtre).
            if pas > 0:
                self.zoom_texte *= param.zoom_texte_in**pas
                self.zoom_ligne *= param.zoom_ligne_in**pas
            else:
                self.zoom_texte *= param.zoom_texte_out**(-pas)
                self.zoom_ligne *= param.zoom_ligne_out**(-pas)
        else:
            if self.fixe: # Zoom interdit
                return
            # Changer la fenêtre.
            if pas > 0:
                self.zoomer(param.zoom_in**pas)
                self.parent.action_effectuee("zoom_in", signature = 'zoom_in')
            else:
                self.zoomer(param.zoom_out**(-pas))
                self.parent.action_effectuee("zoom_out", signature = 'zoom_out')

    def mouseMoveEvent(self, event):
        #if self.FindFocus() in (self.parent, self.parent.parent, self.parent.parent.parent):
        if self.window().isActiveWindow() and (left_down(event) or right_down(event)):
            self.setFocus()
        if self.redetecter:
            self.detecter()
        actuelle = self.feuille_actuelle

        if actuelle.objet_temporaire(): # Utilisé pour la prévisualisation d'objets, avant leur construction avec la souris
            actuelle.point_temporaire().coordonnees = self.coordonnees(event)

        if left_down(event):# or self.interaction:
            self.editeur.close()
            if ctrl_down(event): # selection d'un zone pour zoomer
                if alt_down(event): # selection simultanée de tous les objets d'une zone
                    self.selection_zone(lieu(event))

                elif not self.fixe:
                    self.gestion_zoombox(lieu(event))

            elif alt_down(event): # deplacement de l'etiquette d'un objet
                self.debut_zoom = None
                x, y = lieu(event)
                if self.etiquette_selectionnee is None:
                    for objet in actuelle.liste_objets(False):
                        if objet.etiquette is not None:
                            try:
                                if objet.etiquette.distance_inf(x, y, param.precision_selection):
                                    self.etiquette_selectionnee = objet.etiquette
                                    x, y = self.etiquette_selectionnee.coordonnees
                                    x1, y1 = self.coordonnees(event)
                                    self.decalage_coordonnees = x - x1, y - y1
                                    break
                            except:
                                print_error()
                                self.message(u"Erreur: impossible de trouver l'étiquette de %s.." %objet.nom)
                if self.etiquette_selectionnee:
                    self.setCursor(Qt.PointingHandCursor)
                    self.etiquette_selectionnee(*self.coordonnees(event, *self.decalage_coordonnees))


            elif self.select is not None and not self.interaction: # deplacement d'un objet avec la souris
                self.debut_zoom = None
                if self.deplacable(self.select):
                    self.select(*self.coordonnees(event, *self.decalage_coordonnees))
                self.infos()

        elif right_down(event) and self.debut_shift and not self.fixe: # deplacement de la feuille
            self.setCursor(Qt.SizeAllCursor)
            self.fin_shift = self.pix2coo(*lieu(event))
            translation = array(self.fin_shift) - array(self.debut_shift)
            self.fenetre = (self.fenetre[0] - translation[0], self.fenetre[1] - translation[0],
                            self.fenetre[2] - translation[1], self.fenetre[3] - translation[1])
            if self.select is not None:
                self.select = None
                self.selection_en_gras()

        elif self.interaction_deplacement is not None:
            self.interaction_deplacement(pixel = lieu(event))

        elif not ctrl_down(event):   # detection des objets a proximite du pointeur
            self.detecter(lieu(event))



    def gestion_zoombox(self, pixel):
        x, y = pixel
        xmax, ymax = self.dimensions # en pixels
        x = max(min(x, xmax), 0)
        y = max(min(y, ymax), 0)
        self.fin_zoom = self.pix2coo(x, y)
        self.debut_zoom = self.debut_zoom or self.fin_zoom
        (x0, y0), (x1, y1) = self.debut_zoom, self.fin_zoom
        if self.orthonorme:
            if ymax*abs(x0 - x1) > xmax*abs(y0 - y1):
                y1 = y0 + ymax/xmax*abs(x0 - x1)*cmp(y1, y0)
            else:
                x1 = x0 + xmax/ymax*abs(y0 - y1)*cmp(x1, x0)
            self.fin_zoom = (x1, y1)
        self.dessiner_polygone([x0,x0,x1,x1], [y0,y1,y1,y0], facecolor='c', edgecolor='c', alpha = .1)
        self.dessiner_ligne([x0,x0,x1,x1,x0], [y0,y1,y1,y0,y0], 'c', alpha = 1)

        self.rafraichir_affichage(dessin_temporaire = True) # pour ne pas tout rafraichir


    def selection_zone(self, pixel):
        x, y = pixel
        xmax, ymax = self.GetSize()
        x = max(min(x, xmax), 0)
        y = max(min(y, ymax), 0)
        self.fin_select = self.pix2coo(x, y)
        self.debut_select = self.debut_select or self.fin_select
        (x0, y0), (x1, y1) = self.debut_select, self.fin_select
        self.dessiner_polygone([x0,x0,x1,x1], [y0,y1,y1,y0], facecolor='y', edgecolor='y',alpha = .1)
        self.dessiner_ligne([x0,x0,x1,x1,x0], [y0,y1,y1,y0,y0], 'g', linestyle = ":", alpha = 1)

        self.rafraichir_affichage(dessin_temporaire = True) # pour ne pas tout rafraichir







    def OnSelect(self, x0, x1, y0, y1):
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        objets_dans_la_zone = []
        for objet in self.feuille_actuelle.liste_objets():
            espace = objet.espace_vital
            if espace is not None:
                xmin, xmax, ymin, ymax = espace
                if x0 <= xmin <= xmax <= x1 and y0 <= ymin <= ymax <= y1:
                    objets_dans_la_zone.append(objet)
        self.feuille_actuelle.objets_en_gras(*objets_dans_la_zone)

        def exporte():
            actuelle = self.feuille_actuelle # feuille de travail courante
##            if actuelle.sauvegarde["export"]:
##                dir, fichier = os.path.split(actuelle.sauvegarde["export"]) # on exporte sous le même nom qu'avant par défaut
##            elif actuelle.sauvegarde["nom"]:
##                fichier = actuelle.sauvegarde["nom"] # le nom par defaut est le nom de sauvegarde
##                dir = actuelle.sauvegarde["repertoire"]
##            else:
##                if param.rep_export is None:
##                    dir = param.repertoire
##                else:
##                    dir = param.rep_export

            filename = self.parent.parent.ExportFile(exporter = False)
            # ne pas faire l'export, mais récupérer juste le nom

            if filename:
                self.exporter(nom = filename, zone = (x0, x1, y0, y1))
                actuelle.sauvegarde["export"] = filename

        menu = QMenu(self)
        menu.addTitle(u"Zone sélectionnée")
        action = menu.addAction(u'Exporter la zone comme image')
        action.triggered.connect(exporte)

        if objets_dans_la_zone:
            action = menu.addAction(u"Supprimer les objets")
            def supprimer():
                noms = ','.join(obj.nom for obj in objets_dans_la_zone)
                self.executer(u'supprimer(%s)' %noms)
            action.triggered.connect(supprimer)

            action = menu.addAction(u'Masquer les objets')
            def masquer():
                with self.geler_affichage(actualiser=True):
                    for objet in objets_dans_la_zone:
                        self.executer(u"%s.cacher()" % objet.nom)
            action.triggered.connect(masquer)

            action = menu.addAction(u'Éditer les objets')
            def editer():
                win = Proprietes(self, objets_dans_la_zone)
                win.show()
            action.triggered.connect(editer)

        menu.show()

        with self.geler_affichage(): # ?
            self.selection_en_gras()
        self.rafraichir_affichage()


    def mousePressEvent(self, event):
        button = event.button()
        if button == Qt.LeftButton:
            self.left_down(event)
        elif button == Qt.RightButton:
            self.right_down(event)
        else:
            FigureCanvasQTAgg.mousePressEvent(self, event)


    def left_down(self, event):
        # Patch pour l'utilisation avec un dispositif de pointage absolu (tablette graphique ou TNI)
        self.detecter(lieu(event))
        ##if self.HasCapture():
            ##self.ReleaseMouse()
        self.setFocus()
        if self.deplacable(self.select):
            x, y = self.select.coordonnees
            x1, y1 = self.coordonnees(event)
            self.decalage_coordonnees = x - x1, y - y1


    def right_down(self, event):
        self.editeur.close()
        self.detecter(lieu(event))

        if self.select is not None and not ctrl_down(event):
            menu = MenuActionsObjet(self)
            menu.exec_()
            if self.select is not None:
                self.select = None
                self.selection_en_gras()
            self.setCursor(Qt.ArrowCursor)
        elif not self.fixe:
            self.debut_shift = self.pix2coo(*lieu(event))
            self.setCursor(Qt.SizeAllCursor)
            ##if not self.HasCapture():
                ##self.CaptureMouse()


    def mouseReleaseEvent(self, event):
        button = event.button()
        if button == Qt.LeftButton:
            self.left_up(event)
        elif button == Qt.RightButton:
            self.right_up(event)
        else:
            FigureCanvasQTAgg.mouseReleaseEvent(self, event)


    def left_up(self, event):
        ##if self.HasCapture():
            ##self.ReleaseMouse()

        if self.etiquette_selectionnee:
            x, y = self.etiquette_selectionnee.coordonnees
            self.parent.action_effectuee(u"%s.etiquette(%s, %s)" %(self.etiquette_selectionnee.parent.nom, x, y))
            self.etiquette_selectionnee = None
            return

        if self.debut_zoom and not self.fixe:
            try:
                if ctrl_down(event):
                    (x0, y0), (x1, y1) = self.debut_zoom, self.fin_zoom
                    self.executer("fenetre = " + str((x0, x1, y0, y1)))
                else:
                    self.rafraichir_affichage()
            finally:
                self.debut_zoom = None

        elif self.debut_select and not self.fixe:
            try:
                if ctrl_down(event) and alt_down(event):
                    (x0, y0), (x1, y1) = self.debut_select, self.fin_select
                    self.OnSelect(x0, x1, y0, y1)
                else:
                    self.rafraichir_affichage()
            finally:
                self.debut_select = None

        elif self.interaction:
            self.signal(event)
            self.setCursor(Qt.ArrowCursor)

        elif self.deplacable(self.select):
            self.parent.action_effectuee(self.select.nom + str(self.select.coordonnees))
            # pas super precis : il se peut qu'on relache le bouton sans avoir deplace le point.
            # ca fait un enregistrement inutile dans l'historique...


    def right_up(self, event):
        ##if self.HasCapture():
            ##self.ReleaseMouse()

        if self.fixe: return

        self.setCursor(Qt.ArrowCursor)

        if self.debut_shift:
            self.debut_shift= None
            self.parent.action_effectuee(u"fenetre = " + str(self.fenetre))


    def editer(self, mode = 0):
        if self.select is not None:
            self.editeur.init(self.select, mode)
        else:
            self.editeur.close()


    def keyPressEvent(self, event):
        if self.redetecter:
            self.detecter()

        key = event.key()
        txt = event.text()
        modifiers = event.modifiers()
        accept = True
        debug(u"key: ", key)
        if key == Qt.Key_Delete and self.select:
            if shift_down(event):
                self.executer(u"%s.cacher()" %self.select.nom)
            else:
                self.executer(u"%s.supprimer()" %self.select.nom)
        elif key in (Qt.Key_Return, Qt.Key_Enter) and self.editeur.objet is not self.select:
            self.editer(shift_down(event))
        elif self.editeur and not self.editeur.key(key, txt, modifiers):
            accept = False

        if key == Qt.Key_Escape and self.interaction:
            print "ESCAPE !"
            self.interaction(special="ESC")
            accept = True

        if not accept:
            FigureCanvasQTAgg.keyPressEvent(self, event)


    def paintEvent(self, event):
        self.graph.restaurer_dessin()
        FigureCanvasQTAgg.paintEvent(self, event)

    def resizeEvent(self, event):
        self.feuille_actuelle._rafraichir_figures()
        self.rafraichir_affichage(rafraichir_axes = True)
        FigureCanvasQTAgg.resizeEvent(self, event)

    def leaveEvent(self, event):
        # self.execute_on_idle(
        self.feuille_actuelle.objets_en_gras
        FigureCanvasQTAgg.leaveEvent(self, event)
