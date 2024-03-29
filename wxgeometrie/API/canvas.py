# -*- coding: utf-8 -*-

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

from math import isinf, isnan
from weakref import WeakSet

import numpy
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from .moteur_graphique import Moteur_graphique
from ..pylib import decorator, property2, print_error, no_argument
from ..geolib import Feuille
from .. import param


class GelAffichage(object):
    def __init__(
        self,
        canvas,
        geler=True,
        actualiser=False,
        seulement_en_apparence=False,
        sablier=False,
    ):
        self.sablier = sablier
        self.canvas = canvas
        self.geler = geler
        self.actualiser = actualiser
        self.attribut = (
            "_affichage_gele_en_apparence"
            if seulement_en_apparence
            else "_affichage_gele"
        )

    def __enter__(self):
        self._ancienne_valeur = getattr(self.canvas, self.attribut)
        if self.geler is not None:
            setattr(self.canvas, self.attribut, self.geler)
        if self.sablier:
            self.canvas._curseur(sablier=True)

    def __exit__(self, type, value, traceback):
        setattr(self.canvas, self.attribut, self._ancienne_valeur)
        if self.actualiser:
            self.canvas.rafraichir_affichage()
        if self.sablier:
            self.canvas._curseur(sablier=False)


# Garde une trace dans les logs de chaque appel de la méthode pour débogage.
@decorator
def track(meth, self, *args, **kw):
    if param.debug:
        s = "%s - Args: %s, %s" % (meth.__name__, args, kw)
        self.parent.action_effectuee(s)
    return meth(self, *args, **kw)


# Garde une trace dans les logs de chaque appel *isolé* de la méthode pour débogage.
# Par exemple, en cas de zoom avec la roulette de souris, seul le dernier zoom
# sera enregistré, pour ne pas saturer le fichier .log
@decorator
def partial_track(meth, self, *args, **kw):
    if param.debug:
        s = "%s - Args: %s, %s" % (meth.__name__, args, kw)
        self.parent.action_effectuee(s, signature=meth.__name__)
    return meth(self, *args, **kw)


class Canvas(FigureCanvasAgg):
    "Partie du canvas indépendante de la librairie graphique (Wx actuellement)."

    def __init__(self, couleur_fond="w", dimensions=None, feuille=None):
        self.figure = Figure(dpi=param.dpi_ecran, frameon=True, facecolor=couleur_fond)
        FigureCanvasAgg.__init__(self, self.figure)
        self.axes = self.figure.add_axes([0, 0, 1, 1], frameon=False)
        self._dimensions = dimensions
        self.__feuille_actuelle = feuille
        self.axes.set_xticks([])
        self.axes.set_yticks([])

        # Ces paramètres ne sont utiles que pour les sur-classes s'intégrant dans un GUI.
        self.editeur = None
        self.select = None  # objet couramment sélectionné

        # if self.param("transformation_affine") is not None:
        #    self.transformation = matplotlib.transforms.Affine(*self.param("transformation_affine"))
        #    self.figure.set_transform(self.transformation)
        #    self.axes.set_transform(self.transformation)
        # else:
        #    self.transformation = None
        if self.param("transformation") is not None:
            a, b, c, d = self.param("transformation")
            # CODE À RÉÉCRIRE et À ADAPTER
            self.transformation = numpy.matrix([[a, b], [c, d]])
        else:
            self.transformation = None

        self._affichage_gele = False
        # Ne pas utiliser directement.
        # Si on met la valeur a True, self.rafraichir_affichage() ne fait plus rien.
        # Cela permet d'effectuer un certain nombre d'actions rapidement,
        # et de n'actualiser qu'à la fin.
        # En particulier, cela sert pour charger une figure depuis un fichier .geo
        self._affichage_gele_en_apparence = False
        # Ne pas utiliser directement.
        # Si on met la valeur a True, self.rafraichir_affichage() fonctionne toujours,
        # mais les changements ne s'affichent pas à l'écran.
        # Cela permet d'effectuer un certain nombre d'actions sans que l'utilisateur s'en apercoive
        # (pas de clignotement de l'affichage).
        # Par contre, le gain de temps est négligeable par rapport à un vrai gel de l'affichage.
        # En particulier, cela sert pour exporter une figure.

        self.graph = Moteur_graphique(self)
        self.parametres = [
            "taille",
            "gradu",
            "afficher_axes",
            "afficher_quadrillage",
            "afficher_fleches",
            "repere",
            "resolution",
            "origine_axes",
            "utiliser_repere",
            "quadrillages",
            "couleur_papier_millimetre",
            "liste_axes",
            "ratio",
            "grille_aimantee",
            "zoom_texte",
            "zoom_ligne",
            "dpi_ecran",
        ]
        self.objets_en_gras = WeakSet()
        self.initialiser()

    @property2
    def feuille_actuelle(self, val=None):
        if val is None:
            return self.__feuille_actuelle
        self.__feuille_actuelle = val

    def initialiser(self):
        # actions a effectuer avant de rééxecuter l'historique
        for parametre in self.parametres:
            setattr(self, parametre, self.param(parametre))

    def exporter(
        self,
        fichier,
        format=None,
        dpi=None,
        zone=None,
        echelle=None,
        taille=None,
        keep_ratio=False,
    ):
        """Export de la feuille sous forme d'un fichier (png, eps, ...).

        :param string,file fichier: le fichier lui-même, ou son emplacement.
        :param format: le format de l'image (PNG, SVG, ...).
                       Inutile si le nom du fichier est donné avec une extension connue.
        :param int,float dpi: résolution souhaitée (en dot par inch)
        :param tuple zone: (xmin, xmax, ymin, ymax) : pour n'exporter qu'une partie de la feuille (png seulement).
        :param tuple echelle: (x, y) : nombre de cm pour une unité en abscisse ; en ordonnée
        :param tuple taille: (largeur, hauteur) : taille de l'image en cm.
        :param bool keep_ratio: indique si le ratio doit être préservé en cas de redimensionnement.

        Les paramètres `echelle` et `taille` ne peuvent être fournis simultanément.
        """

        dpi = dpi or param.dpi_export

        if self.editeur is not None:
            # Evite d'exporter la feuille avec un nom d'objet en cours d'édition
            self.editeur.close()
        # De même, aucun objet ne doit être en gras
        self.feuille_actuelle.met_objets_en_gras()
        # Les objets invisibles ne doivent pas apparaitre
        afficher_objets_caches = self.afficher_objets_caches
        self.afficher_objets_caches = False

        self.graph.exporter(
            fichier=fichier,
            format=format,
            dpi=dpi,
            zone=zone,
            echelle=echelle,
            taille=taille,
            keep_ratio=keep_ratio,
        )

        self.afficher_objets_caches = afficher_objets_caches
        self.selection_en_gras()

    def selection_en_gras(self):
        self.feuille_actuelle.met_objets_en_gras(self.select, *self.objets_en_gras)

    #   Alias
    ######################

    def dessiner_ligne(self, *args, **kw):
        return self.graph.ajouter_ligne(*args, **kw)

    def dessiner_polygone(self, *args, **kw):
        return self.graph.ajouter_polygone(*args, **kw)

    def dessiner_texte(self, *args, **kw):
        return self.graph.ajouter_texte(*args, **kw)

    def dessiner_arc(self, *args, **kw):
        return self.graph.ajouter_arc(*args, **kw)

    def dessiner_point(self, *args, **kw):
        return self.graph.ajouter_point(*args, **kw)

    def ligne(self, *args, **kw):
        return self.graph.ligne(*args, **kw)

    def polygone(self, *args, **kw):
        return self.graph.polygone(*args, **kw)

    def texte(self, *args, **kw):
        return self.graph.texte(*args, **kw)

    def arc(self, *args, **kw):
        return self.graph.arc(*args, **kw)

    def point(self, *args, **kw):
        return self.graph.point(*args, **kw)

    def fleche(self, *args, **kw):
        return self.graph.fleche(*args, **kw)

    def fleche_courbe(self, **kw):
        return self.graph.fleche_courbe(**kw)

    def codage(self, **kw):
        return self.graph.codage(**kw)

    def angle(self, **kw):
        return self.graph.angle(**kw)

    def codage_angle(self, **kw):
        return self.graph.codage_angle(**kw)

    def rectangle(self, **kw):
        return self.graph.rectangle(**kw)

    def decoration_texte(self, **kw):
        return self.graph.decoration_texte(**kw)

    def lignes(self, *args, **kw):
        return self.graph.lignes(*args, **kw)

    def dessiner(self, objet):
        self.graph.ajouter(objet)

    ##################################
    # Les fonctions suivantes assurent la conversion pixel <-> coordonnees
    ##################################
    # en multipliant m par coeff(0), on convertit un ecart en abcisses de m pixels en coordonnees.
    # en multipliant n par coeff(1), on convertit un ecart en ordonnees de n pixels en coordonnees.
    # Les fonctions qui suivent permettent la conversion d'un couple de coordonnees en pixels, et reciproquement.
    # Si le mode est fixe a 1, le pixel (0,0) sera le coin inferieur gauche (plus intuitif).
    # Si le mode est fixe a -1, le pixel (0,0) sera le coin superieur gauche (convention, respectee par WxPython).

    @property
    def dimensions(self):
        return self._dimensions

    @property
    def largeur(self):
        return self.dimensions[0]

    @property
    def hauteur(self):
        return self.dimensions[1]

    def pas(self):
        # print 'pas:', self.fenetre, self.resolution
        return (self.fenetre[1] - self.fenetre[0]) / (self.resolution)

    ## <DESUET> ##
    def _coeff(self, i):  # DESUET
        #        warning("Desuet. Utiliser dpix2coo (*coeff) et dcoo2pix (/coeff)")
        return (self.fenetre[1 + 2 * i] - self.fenetre[2 * i]) / self.dimensions[i]
        # Rq: une ZeroDivisionError se produit juste après avoir beaucoup réduit une fenêtre,
        # wxpython renvoit parfois (0,0) pour la taille.
        # le plus simple serait de laisser l'erreur, mais ça innonde le débugueur de messages... :-/

    def txt_box(self, matplotlib_text):
        """Retourne l'espace (rectangulaire) occupé par le texte.

        Retourne un objet Bbox, possédant des attributs xmin, xmax, ymin,
        ymax, height et width. (En pixels)."""
        matplotlib_text.figure = self.figure
        size = matplotlib_text.get_size()
        matplotlib_text.set_size(size * self.zoom_texte)
        box = matplotlib_text.get_window_extent(self.get_renderer())
        matplotlib_text.set_size(size)
        return box

    def coo2pix(self, x, y):
        """Convertit des coordonnées en pixel."""
        return self.feuille_actuelle.coo2pix(x, y)

    def pix2coo(self, px, py):
        """Convertit un pixel en coordonnées."""
        return self.feuille_actuelle.pix2coo(px, py)

    def dcoo2pix(self, dx, dy):
        """Convertit un déplacement exprimé en coordonnées en un déplacement en pixels."""
        return self.feuille_actuelle.dcoo2pix(dx, dy)

    def dpix2coo(self, dpx, dpy):
        """Convertit un déplacement exprimé en pixels en un déplacement exprimé en coordonnées."""
        return self.feuille_actuelle.dpix2coo(dpx, dpy)

    def _affiche_module(self):
        "Affichage spécifique au module en cours. (À surclasser.)"
        pass

    def geler_affichage(
        self, geler=True, actualiser=False, seulement_en_apparence=False, sablier=False
    ):
        """À utiliser au sein d'un contexte 'with':

            .. sourcecode:: python

            with self.geler_affichage():
                # some action

        Si actualiser = True, l'affichage est rafraichi au dégel.
        Si seulement_en_apparence = True, l'affichage n'est pas gelé en interne, mais les modifications
        ne s'affichent pas à l'écran (le gain de vitesse est alors négligeable, mais esthétiquement ça évite
        que des modifications successives apparaissent à l'écran).

        Si sablier = True, le pointeur de la souris est remplacé temporairement par un sablier.
        """
        return GelAffichage(self, geler=geler, actualiser=actualiser, sablier=sablier)

    def _curseur(self, sablier):
        """Changer le curseur en sablier.

        À surclasser."""
        raise NotImplementedError

    @property
    def affichage_gele(self):
        return self._affichage_gele

    @property
    def affichage_gele_en_apparence(self):
        return self._affichage_gele_en_apparence

    def saturation(self, i):
        return self.zoom_ligne * self._coeff(i) / self.gradu[i]

    #    Reglage des parametres d'affichage
    ##########################################
    # Gestion des variables d'environnement liées à l'affichage.
    # A standardiser.

    ##    _liste_parametres_repere = ("quadrillages", "affiche_quadrillage", "affiche_axes",
    ##                                    "affiche_fleches", "repere", "gradu", "utiliser_repere",
    ##                                    "liste_axes", "orthonorme", "fenetre",
    ##                                    )

    # Parametres booléens gérés par une entrée du menu
    for _nom_, _doc_ in (
        ("afficher_axes", "Afficher ou non les axes."),
        ("afficher_quadrillage", "Afficher ou non le(s) quadrillage(s)."),
        ("orthonorme", "Afficher la figure dans un repère toujours orthonormé."),
        (
            "afficher_objets_caches",
            "Indique si les objets cachés sont affichés ou non.",
        ),
        (
            "grille_aimantee",
            "Indique si les points doivent se placer sur le quadrillage.",
        ),
    ):
        exec(
            '''@track
def gerer_parametre_%(_nom_)s(self, afficher = None):
    """%(_doc_)s"""
    if afficher is not None:
        if isinstance(afficher, bool):
            self.%(_nom_)s = afficher
        else:
            self.%(_nom_)s = not self.%(_nom_)s
        self.rafraichir_affichage()
    assert isinstance(self.%(_nom_)s, bool), '%(_nom_)s: ' + repr(self.%(_nom_)s)
    return self.%(_nom_)s'''
            % locals(),
            globals(),
            locals(),
        )

    # Paramètres gérés directement par la feuille
    for _nom_ in Feuille._parametres_repere:
        exec(
            """assert "%(_nom_)s" not in locals(), "Erreur: %(_nom_)s est deja defini !"
@property2
def %(_nom_)s(self, valeur = no_argument):
    if valeur is no_argument:
        return self.feuille_actuelle.%(_nom_)s
    self.feuille_actuelle.%(_nom_)s = valeur"""
            % locals(),
            globals(),
            locals(),
        )

    del _nom_, _doc_

    #      Gestion du zoom, etc...
    ########################################

    def _get_fenetre(self):
        return self.feuille_actuelle.fenetre_reellement_affichee()

    def _set_fenetre(self, xmin_xmax_ymin_ymax):
        self.feuille_actuelle.fenetre = xmin_xmax_ymin_ymax

    fenetre = property(_get_fenetre, _set_fenetre)

    @property
    def xmin(self):
        return self.fenetre[0]

    @property
    def xmax(self):
        return self.fenetre[1]

    @property
    def ymin(self):
        return self.fenetre[2]

    @property
    def ymax(self):
        return self.fenetre[3]

    @property
    def dimensions_fenetre(self):
        xmin, xmax, ymin, ymax = self.fenetre
        return xmax - xmin, ymax - ymin

    def synchroniser_fenetre(self):
        """Détecte la fenêtre d'affichage et l'enregistre.
        Ce peut être utile si l'on utilise une commande de haut niveau de matplolib,
        qui calcule automatiquement la meilleure fenêtre d'affichage."""
        xmin, xmax = self.axes.viewLim.intervalx
        ymin, ymax = self.axes.viewLim.intervaly
        self.fenetre = xmin, xmax, ymin, ymax

    def zoomer(self, coeff):
        xmin, xmax, ymin, ymax = self.fenetre
        x, y, rx, ry = (
            (xmin + xmax) / 2.0,
            (ymin + ymax) / 2.0,
            (xmax - xmin) / 2.0,
            (ymax - ymin) / 2.0,
        )
        self.fenetre = x - rx / coeff, x + rx / coeff, y - ry / coeff, y + ry / coeff

    def zoom_in(self, event=None):
        self.zoomer(param.zoom_in)

    def zoom_out(self, event=None):
        self.zoomer(param.zoom_out)

    @track
    def zoom_auto(self, event=None):
        fenetre_initiale = a = self.fenetre
        compteur = 0
        condition = True
        while condition:
            self.graph._regler_fenetre()
            compteur += 1
            self._zoom_auto()
            # à cause du texte dont la taille est indépendante de l'échelle, les calculs sont faussés.
            # Mais en réitérant le procédé, l'affichage converge rapidement (A OPTIMISER ?).
            b = a
            a = self.fenetre
            erreur_x = abs(a[0] - b[0]) + abs(a[1] - b[1])
            erreur_y = abs(a[2] - b[2]) + abs(a[3] - b[3])
            # l'erreur doit être inférieure à 1 pixel:
            condition = erreur_x / self._coeff(0) > 1 or erreur_y / self._coeff(1) > 1
            if compteur > 25:
                self.message("Échec du zoom automatique.")
                self.fenetre = fenetre_initiale
                break

    def _zoom_auto(self):
        objets = self.feuille_actuelle.liste_objets(
            objets_caches=False, etiquettes=True
        )
        xxyy = list(zip(*(obj.espace_vital for obj in objets if obj.espace_vital)))
        print("xxyy", xxyy)

        if xxyy:

            def num_only(item):
                # 'None' indique que l'objet ne fournit pas d'indication de dimension
                # pour les abscisses ou pour les ordonnées.
                return not (item is None or isinf(item) or isnan(item))

            noms = ("xmin", "xmax", "ymin", "ymax")
            # Listes brutes des extremas obtenus pour chaque objet.
            listes_extremas = list(zip(noms, xxyy, self.fenetre))
            # Synthèse : valeurs retenues pour l'ensemble de la feuille.
            extremas = {}
            # 'False' si le paramètre ne doit *pas* être modifié.
            ajuster = {"xmin": True, "xmax": True, "ymin": True, "ymax": True}

            for nom, liste, defaut in listes_extremas:
                liste_filtree = list(filter(num_only, liste))
                if param.debug:
                    print("zoom_auto - valeurs obtenues:", nom, liste_filtree)
                if liste_filtree:
                    if nom.endswith("min"):
                        extremas[nom] = min(liste_filtree)
                    else:
                        extremas[nom] = max(liste_filtree)
                else:
                    extremas[nom] = defaut
                    ajuster[nom] = False

            if param.debug:
                print("zoom_auto - propositions:", extremas)

            for axe in "xy":
                nom_min = axe + "min"
                nom_max = axe + "max"
                ecart = extremas[nom_max] - extremas[nom_min]
                assert ecart > 0
                # Des valeurs trop proches pour xmin et xmax (ou pour ymin et ymax)
                # risqueraient de faire planter l'affichage.
                if ecart < 100 * param.tolerance:
                    rayon = 0.5 * (getattr(self, nom_max) - getattr(self, nom_min))
                    extremas[nom_min] -= rayon
                    extremas[nom_max] += rayon
                else:
                    # On prévoit 5% de marge (de manière à ce qu'un point
                    # ne se retrouve pas collé au bord de la fenêtre par exemple).
                    if ajuster[nom_min]:
                        extremas[nom_min] -= 0.05 * ecart
                    if ajuster[nom_max]:
                        extremas[nom_max] += 0.05 * ecart

            self.fenetre = tuple(extremas[nom] for nom in noms)
            if param.debug:
                print("ZOOM AUTO :", self.fenetre)

    @track
    def orthonormer(self, event=None, mode=1):
        """
        mode 0 : on orthonormalise le repère en restreignant la vue.
        mode 1 : on orthonormalise le repère en élargissant la vue."""
        if mode:
            xcoeff = (
                self._coeff(1) / self._coeff(0)
                if self._coeff(0) < self._coeff(1)
                else 1
            )
            ycoeff = (
                1
                if self._coeff(0) < self._coeff(1)
                else self._coeff(0) / self._coeff(1)
            )
        else:
            xcoeff = (
                self._coeff(1) / self._coeff(0)
                if self._coeff(0) > self._coeff(1)
                else 1
            )
            ycoeff = (
                1
                if self._coeff(0) > self._coeff(1)
                else self._coeff(0) / self._coeff(1)
            )
        xmin, xmax, ymin, ymax = self.fenetre
        x, y, rx, ry = (
            (xmin + xmax) / 2.0,
            (ymin + ymax) / 2.0,
            (xmax - xmin) / 2.0,
            (ymax - ymin) / 2.0,
        )
        self.fenetre = (
            x - xcoeff * rx,
            x + xcoeff * rx,
            y - ycoeff * ry,
            y + ycoeff * ry,
        )

    @property2
    def orthonorme(self, value=None):
        if value is None:
            return self.ratio == 1
        elif value:
            self.ratio = 1
        else:
            self.ratio = None

    # < Zooms concernant uniquement la taille des objets >

    def zoom_text(self, event=None, valeur=100):
        self.zoom_texte = valeur / 100

    ##        self.rafraichir_affichage()

    def zoom_line(self, event=None, valeur=100):
        self.zoom_ligne = valeur / 100

    ##        self.rafraichir_affichage()

    def zoom_normal(self, event=None):
        self.zoom_texte = 1
        self.zoom_ligne = 1

    ##        self.rafraichir_affichage()

    def zoom_large(self, event=None):
        self.zoom_texte = 1.2
        self.zoom_ligne = 1.4

    ##        self.rafraichir_affichage()

    def zoom_videoprojecteur(self, event=None):
        self.zoom_texte = 1.6
        self.zoom_ligne = 2

    ##        self.rafraichir_affichage()

    def zoom_videoprojecteur_large(self, event=None):
        self.zoom_texte = 2.2
        self.zoom_ligne = 3

    ##        self.rafraichir_affichage()

    # </ Fin des zooms sur la taille des objets >

    @track
    def repere_Oij(self, event=None):
        self.repere = ("O", "i", "j")
        self.gerer_parametre_afficher_axes(True)

    @track
    def repere_OIJ(self, event=None):
        self.repere = ("O", "I", "J")
        self.gerer_parametre_afficher_axes(True)

    @track
    def repere_011(self, event=None):
        ux, uy = self.gradu
        self.repere = ("0", str(ux), str(uy))
        self.gerer_parametre_afficher_axes(True)

    @track
    def quadrillage_millimetre(self, event=None):
        self.quadrillages = (
            ((1, 1), ":", 1, "k"),
            ((0.5, 0.5), "-", 0.25, "darkgray"),
            ((0.1, 0.1), "-", 0.1, "gray"),
        )
        self.gerer_parametre_afficher_quadrillage(True)

    @track
    def quadrillage_millimetre_colore(self, event=None, couleur=None):
        if couleur is None:
            couleur = self.couleur_papier_millimetre
        self.quadrillages = (
            ((1, 1), ":", 1, couleur),
            ((0.5, 0.5), "-", 0.25, couleur),
            ((0.1, 0.1), "-", 0.1, couleur),
        )
        self.gerer_parametre_afficher_quadrillage(True)

    @track
    def quadrillage_demigraduation(self, event=None):
        ux, uy = self.gradu
        self.quadrillages = (
            ((ux, uy), ":", 1, "k"),
            ((ux / 2, uy / 2), "-", 0.25, "darkgray"),
        )
        self.gerer_parametre_afficher_quadrillage(True)

    @track
    def quadrillage_demigraduation_colore(self, event=None, couleur=None):
        ux, uy = self.gradu
        if couleur is None:
            couleur = self.couleur_papier_millimetre
        self.quadrillages = (
            ((ux, uy), ":", 1, couleur),
            ((ux / 2, uy / 2), "-", 0.25, couleur),
        )
        self.gerer_parametre_afficher_quadrillage(True)

    @track
    def quadrillage_defaut(self, event=None):
        self.quadrillages = self.param("quadrillages", defaut=True)
        self.gerer_parametre_afficher_quadrillage(True)

    # Sélection d'une zone
    ######################

    def _rectangle_selection(
        self,
        xy0,
        xy1,
        linestyle="-",
        facecolor="y",
        edgecolor="y",
        respect_ratio=False,
        coins=False,
        coin_actif=None,
    ):
        """Dessine un rectangle de sélection au dessus de la figure actuelle.

        L'option `coins` sert à afficher des poignées aux 4 coins du rectangle
        pour indiquer que la sélection est redimensionnable.
        """
        x0, y0 = xy0
        x1, y1 = xy1
        # Le rectangle de sélection ne doit pas sortir de la fenêtre.
        xmin, xmax, ymin, ymax = self.fenetre
        x0 = max(min(x0, xmax), xmin)
        y0 = max(min(y0, ymax), ymin)
        x1 = max(min(x1, xmax), xmin)
        y1 = max(min(y1, ymax), ymin)

        if respect_ratio and self.ratio is not None:
            rymax = ymax * self.ratio
            if rymax * abs(x0 - x1) > xmax * abs(y0 - y1):
                y1 = y0 + rymax / xmax * abs(x0 - x1) * (1 if y1 > y0 else -1)
            else:
                x1 = x0 + xmax / rymax * abs(y0 - y1) * (1 if x1 > x0 else -1)

        # Exceptionnellement, il faut ici effacer manuellement le graphisme.
        # En effet, il n'est pas garanti qu'il y ait un rafraichissement
        # de l'affichage à chaque fois que le rectangle de sélection change.
        # Si l'on n'efface pas manuellement l'affichage, on risque donc d'avoir
        # deux rectangles de sélection différents affichés simultanément.
        self.graph._effacer_artistes()
        self.dessiner_polygone(
            [x0, x0, x1, x1],
            [y0, y1, y1, y0],
            facecolor=facecolor,
            edgecolor=edgecolor,
            alpha=0.1,
        )
        self.dessiner_ligne(
            [x0, x0, x1, x1, x0],
            [y0, y1, y1, y0, y0],
            edgecolor,
            linestyle=linestyle,
            alpha=1,
        )
        if coins:
            for x, y in [(x0, y0), (x0, y1), (x1, y0), (x1, y1)]:
                self.dessiner_point(
                    x,
                    y,
                    color=("k" if (x, y) != coin_actif else "r"),
                    marker="s",
                    markersize=4,
                )

        # Pour ne pas tout rafraichir.
        self.rafraichir_affichage(dessin_temporaire=True)

        # On renvoie le point de fin de sélection, qui ne correspondra pas
        # toujours au point où le bouton de la souris a été relâché (même si
        # la souris sort de la fenêtre, la sélection ne dépasse pas la fenêtre).
        self.coordonnees_rectangle_selection = ((x0, y0), (x1, y1))

    def rectangle_zoom(self, xy0, xy1):
        self._rectangle_selection(
            xy0, xy1, facecolor="c", edgecolor="c", respect_ratio=True
        )

    def rectangle_selection(self, xy0, xy1, coins=False, coin_actif=None):
        self._rectangle_selection(
            xy0,
            xy1,
            facecolor="y",
            edgecolor="g",
            linestyle=":",
            coins=coins,
            coin_actif=coin_actif,
        )

    # Evenements concernant directement la feuille
    ##############################################

    def coder(self, event):
        self.executer("coder()")

    def decoder(self, event):
        self.executer("effacer_codage()")

    def nettoyer_feuille(self, event):
        self.executer("nettoyer()")

    def effacer_traces(self, event):
        self.feuille_actuelle.effacer_traces()

    def executer(self, commande, parser=False):
        """Exécute une commande dans la feuille.

        NB: le parser n'est *PAS* activé par défaut, par souci de rapidité."""
        self.feuille_actuelle.executer(commande, parser=parser)

    #    Gestion de l'affichage
    #################################

    def rafraichir_affichage(self, dessin_temporaire=False, rafraichir_axes=None):
        if rafraichir_axes is not None:
            self.feuille_actuelle._repere_modifie = rafraichir_axes
        self.feuille_actuelle.affichage_perime()
        self._dessin_temporaire = dessin_temporaire

    def _actualiser_si_necessaire(self, event=None, _n=[0]):
        #        _n[0] += 1
        if self.feuille_actuelle._affichage_a_actualiser:
            #            print _n[0], u"Affichage actualisé."
            self._actualiser()

    def _actualiser(self, _n=[0]):
        # Le code suivant est à activer uniquement pour le débogage de l'affichage:
        # <DEBUG>
        if param.debug:
            s = "Actualisation"
            if self.feuille_actuelle._repere_modifie:
                s += " complete"
            print(s + str(_n) + ": " + self.parent.titre)
            _n[0] += 1
        # </DEBUG>
        if 0 in self.dimensions:
            # Fenêtre pas encore affichée (initialisation du programme).
            if param.debug:
                print(
                    "Actualisation différée (fenêtre non chargée : "
                    + self.parent.titre
                    + ")"
                )
            return
        try:
            self.graph.dessiner(
                dessin_temporaire=self._dessin_temporaire,
                rafraichir_axes=self.feuille_actuelle._repere_modifie,
            )
        except Exception:
            # Ne pas bloquer le logiciel par des rafraichissements successifs en cas de problème.
            print_error()
        self.feuille_actuelle._repere_modifie = False
        self.feuille_actuelle._affichage_a_actualiser = False
        self._dessin_temporaire = False

    def param(self, key, **kw):
        return getattr(param, key)
