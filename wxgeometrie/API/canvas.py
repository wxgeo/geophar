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


import numpy
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from .moteur_graphique import Moteur_graphique
from ..pylib import decorator, property2, print_error, WeakList, str2, no_argument
from ..geolib import Feuille
from .. import param


class GelAffichage(object):
    def __init__(self, canvas, geler=True, actualiser=False, seulement_en_apparence=False, sablier=False):
        self.sablier = sablier
        self.canvas = canvas
        self.geler = geler
        self.actualiser = actualiser
        self.attribut = ('_affichage_gele_en_apparence' if seulement_en_apparence else '_affichage_gele')

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
        s = "%s - Args: %s, %s" % (meth.func_name, args, kw)
        self.parent.action_effectuee(s)
    return meth(self, *args, **kw)

# Garde une trace dans les logs de chaque appel *isolé* de la méthode pour débogage.
# Par exemple, en cas de zoom avec la roulette de souris, seul le dernier zoom
# sera enregistré, pour ne pas saturer le fichier .log
@decorator
def partial_track(meth, self, *args, **kw):
    if param.debug:
        s = "%s - Args: %s, %s" % (meth.func_name, args, kw)
        self.parent.action_effectuee(s, signature = meth.func_name)
    return meth(self, *args, **kw)












class Canvas(FigureCanvasAgg):
    u'Partie du canvas indépendante de la librairie graphique (Wx actuellement).'

    def __init__(self, couleur_fond = 'w', dimensions = None, feuille = None):
        self.figure = Figure(dpi = param.dpi_ecran, frameon=True, facecolor = couleur_fond)
        FigureCanvasAgg.__init__(self, self.figure)
        self.axes = self.figure.add_axes([0, 0, 1, 1], frameon=False)
        self._dimensions = dimensions
        self.__feuille_actuelle = feuille
        self.axes.set_xticks([])
        self.axes.set_yticks([])

        # Ces paramètres ne sont utiles que pour les sur-classes s'intégrant dans un GUI.
        self.editeur = None
        self.select = None             # objet couramment sélectionné

        #if self.param("transformation_affine") is not None:
        #    self.transformation = matplotlib.transforms.Affine(*self.param("transformation_affine"))
        #    self.figure.set_transform(self.transformation)
        #    self.axes.set_transform(self.transformation)
        #else:
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
        # Cela permet d'effectuer un certain nombre d'actions sans que l'utilisateur s'en apercoive (pas de clignotement de l'affichage).
        # Par contre, le gain de temps est négligeable par rapport à un vrai gel de l'affichage.
        # En particulier, cela sert pour exporter une figure.


        self.graph = Moteur_graphique(self)
        self.parametres = [u"taille", u"gradu", u"afficher_axes", u"afficher_quadrillage", u"afficher_fleches", u"repere", u"resolution", u"origine_axes", u"utiliser_repere", u"quadrillages", u"couleur_papier_millimetre", u"liste_axes", u"orthonorme", u"grille_aimantee", u"zoom_texte", "zoom_ligne"]
        self.liste_objets_en_gras = WeakList()
        self.initialiser()


    @property2
    def feuille_actuelle(self, val = None):
        if val is None:
            return self.__feuille_actuelle
        self.__feuille_actuelle = val

    def initialiser(self):
        # actions a effectuer avant de rééxecuter l'historique
        for parametre in self.parametres:
            setattr(self, parametre, self.param(parametre))


    def exporter(self, nom, dpi = None, zone = None, echelle = None):
        u"""Export de la feuille sous forme d'un fichier (png, eps, ...).
        dpi : résolution souhaitée (en dot par inch)
        zone = (xmin, xmax, ymin, ymax) : pour n'exporter qu'une partie de la feuille (png seulement).
        echelle = (x, y) : nombre de cm pour une unité en abscisse ; en ordonnée"""

        nom = str2(nom) # la méthode savefig ne gère pas l'unicode
        dpi = dpi or param.dpi_export

        if self.editeur is not None:
            # Evite d'exporter la feuille avec un nom d'objet en cours d'édition
            self.editeur.close()
        # De même, aucun objet ne doit être en gras
        self.feuille_actuelle.objets_en_gras()
        # Les objets invisibles ne doivent pas apparaitre
        afficher_objets_caches = self.afficher_objets_caches
        self.afficher_objets_caches = False

        self.graph.exporter(nom = nom, dpi = dpi, zone = zone, echelle = echelle)

        self.afficher_objets_caches = afficher_objets_caches
        self.selection_en_gras()



    def selection_en_gras(self):
        self.feuille_actuelle.objets_en_gras(self.select, *self.liste_objets_en_gras)

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

    def polygone(self,  *args, **kw):
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

    def pas(self):
        #print 'pas:', self.fenetre, self.resolution
        return (self.fenetre[1] - self.fenetre[0])/(self.resolution)

    ## <DESUET> ##
    def coeff(self, i): # DESUET
#        warning("Desuet. Utiliser dpix2coo (*coeff) et dcoo2pix (/coeff)")
        return (self.fenetre[1+2*i] - self.fenetre[2*i])/self.dimensions[i]
        # Rq: une ZeroDivisionError se produit juste après avoir beaucoup réduit une fenêtre,
        # wxpython renvoit parfois (0,0) pour la taille.
        # le plus simple serait de laisser l'erreur, mais ça innonde le débugueur de messages... :-/

    def coeffs(self): # DESUET
#        warning("Desuet. Utiliser dpix2coo et dcoo2pix")
        return self.coeff(0), self.coeff(1)
    ## </DESUET> ##


    def coo2pix(self, x, y):
        u"""Convertit des coordonnées en pixel."""
        if isinstance(x, (list, tuple)):
            x = numpy.array(x)
        if isinstance(y, (list, tuple)):
            y = numpy.array(y)
        l, h = self.dimensions
        px = l*(x - self.fenetre[0])/(self.fenetre[1] - self.fenetre[0])
        py = h*(self.fenetre[3] - y)/(self.fenetre[3] - self.fenetre[2])
        return px, py

    def pix2coo(self, px, py):
        u"""Convertit un pixel en coordonnées."""
        if isinstance(px, (list, tuple)):
            px = numpy.array(px)
        if isinstance(py, (list, tuple)):
            py = numpy.array(py)
        l, h = self.dimensions
        x = px*(self.fenetre[1] - self.fenetre[0])/l + self.fenetre[0]
        y = py*(self.fenetre[2] - self.fenetre[3])/h + self.fenetre[3]
#        print x,  y,  -x,  -y
        return x, y

    def dcoo2pix(self, dx, dy):
        u"""Convertit un déplacement exprimé en coordonnées en un déplacement en pixels."""
        l, h = self.dimensions
        dpx = l*dx/(self.fenetre[1] - self.fenetre[0])
        dpy = h*dy/(self.fenetre[2] - self.fenetre[3])
        return dpx, dpy

    def dpix2coo(self, dpx, dpy):
        u"""Convertit un déplacement exprimé en pixels en un déplacement exprimé en coordonnées."""
        l, h = self.dimensions
        dx = dpx*(self.fenetre[1] - self.fenetre[0])/l
        dy = dpy*(self.fenetre[3] - self.fenetre[2])/h
        return dx, dy


    def _affiche_module(self):
        u"Affichage spécifique au module en cours. (À surclasser.)"
        pass

    def geler_affichage(self, geler=True, actualiser=False, seulement_en_apparence=False, sablier=False):
        u"""À utiliser au sein d'un contexte 'with':
        with self.geler_affichage():
            ...
        Si actualiser = True, l'affichage est rafraichi au dégel.
        Si seulement_en_apparence = True, l'affichage n'est pas gelé en interne, mais les modifications
        ne s'affichent pas à l'écran (le gain de vitesse est alors négligeable, mais esthétiquement ça évite
        que des modifications successives apparaissent à l'écran).

        Si sablier = True, le pointeur de la souris est remplacé temporairement par un sablier.
        """
        return GelAffichage(self, geler=geler, actualiser=actualiser, sablier=sablier)

    def _curseur(self, sablier):
        u"""Changer le curseur en sablier.

        À surclasser."""
        raise NotImplementedError

    @property
    def affichage_gele(self):
        return self._affichage_gele

    @property
    def affichage_gele_en_apparence(self):
        return self._affichage_gele_en_apparence

    def saturation(self, i):
        return self.zoom_ligne*self.coeff(i)/self.gradu[i]


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
    ('afficher_axes', u"Afficher ou non les axes."),
    ('afficher_quadrillage', u"Afficher ou non le(s) quadrillage(s)."),
    ('orthonorme', u"Afficher la figure dans un repère toujours orthonormé."),
    ('afficher_objets_caches', u"Indique si les objets cachés sont affichés ou non."),
    ('grille_aimantee', u"Indique si les points doivent se placer sur le quadrillage."),
    ):
        exec('''@track
def gerer_parametre_%(_nom_)s(self, afficher = None):
    """%(_doc_)s"""
    if afficher is not None:
        if isinstance(afficher, bool):
            self.%(_nom_)s = afficher
        else:
            self.%(_nom_)s = not self.%(_nom_)s
        self.rafraichir_affichage()
    assert isinstance(self.%(_nom_)s, bool), '%(_nom_)s: ' + repr(self.%(_nom_)s)
    return self.%(_nom_)s''' %locals(), globals(), locals())

    # Paramètres gérés directement par la feuille
    for _nom_ in Feuille._parametres_repere:
        exec('''assert "%(_nom_)s" not in locals(), "Erreur: %(_nom_)s est deja defini !"
@property2
def %(_nom_)s(self, valeur = no_argument):
    if valeur is no_argument:
        return self.feuille_actuelle.%(_nom_)s
    self.feuille_actuelle.%(_nom_)s = valeur''' %locals(), globals(), locals())

    del _nom_, _doc_



#      Gestion du zoom, etc...
########################################




    def _get_fenetre(self):
        if self.orthonorme:
            w, h = self.dimensions
            fenetre = self.feuille_actuelle.fenetre
            coeff0 = (fenetre[1] - fenetre[0])/w
            coeff1 = (fenetre[3] - fenetre[2])/h
            xmin, xmax, ymin, ymax = fenetre
            xcoeff = (coeff1/coeff0 if coeff0 < coeff1 else 1)
            ycoeff = (1 if coeff0 < coeff1 else coeff0/coeff1)
            x, y, rx, ry = (xmin+xmax)/2., (ymin+ymax)/2., (xmax-xmin)/2., (ymax-ymin)/2.
            return x - xcoeff*rx, x + xcoeff*rx, y - ycoeff*ry, y + ycoeff*ry
        return self.feuille_actuelle.fenetre
##        if hasattr(self, 'ratio'): # À ÉCRIRE
##            if self.ratio is not None: # ratio est le
##                xcoeff = (self.coeff(1)/(self.ratio*self.coeff(0)) if self.ratio*self.coeff(0) < self.coeff(1) else 1)
##                ycoeff = (1 if (self.ratio*self.coeff(0)) < self.coeff(1) else (self.ratio*self.coeff(0))/self.coeff(1))
##                xmin, xmax, ymin, ymax = self.fenetre
##                x, y, rx, ry = (xmin+xmax)/2., (ymin+ymax)/2., (xmax-xmin)/2., (ymax-ymin)/2.
##                self._changer_fenetre(x - xcoeff*rx, x + xcoeff*rx, y - ycoeff*ry, y + ycoeff*ry)


    def _set_fenetre(self, xmin_xmax_ymin_ymax):
        self.feuille_actuelle.fenetre = xmin_xmax_ymin_ymax

    fenetre = property(_get_fenetre, _set_fenetre)

    @property
    def dimensions_fenetre(self):
        xmin, xmax, ymin, ymax = self.fenetre
        return xmax - xmin, ymax - ymin

    def synchroniser_fenetre(self):
        u"""Détecte la fenêtre d'affichage et l'enregistre.
        Ce peut être utile si l'on utilise une commande de haut niveau de matplolib,
        qui calcule automatiquement la meilleure fenêtre d'affichage."""
        xmin, xmax = self.axes.viewLim.intervalx
        ymin, ymax = self.axes.viewLim.intervaly
        self.fenetre = xmin, xmax, ymin, ymax

    def zoomer(self, coeff):
        xmin, xmax, ymin, ymax = self.fenetre
        x, y, rx, ry = (xmin+xmax)/2., (ymin+ymax)/2., (xmax-xmin)/2., (ymax-ymin)/2.
        self.fenetre = x - rx/coeff, x + rx/coeff, y - ry/coeff, y + ry/coeff

    def zoom_in(self, event = None):
        self.zoomer(param.zoom_in)

    def zoom_out(self, event = None):
        self.zoomer(param.zoom_out)





    @track
    def zoom_auto(self, event = None):
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
            condition = erreur_x/self.coeff(0) > 1 or erreur_y/self.coeff(1) > 1
            if compteur > 25:
                self.message(u"Échec du zoom automatique.")
                self.fenetre = fenetre_initiale
                break

    def _zoom_auto(self):
        actuelle = self.feuille_actuelle
        xxyy = zip(*([obj.espace_vital for obj in actuelle.liste_objets(False)
                      if obj.espace_vital is not None]
                      + [obj.etiquette.espace_vital for obj in actuelle.liste_objets(False)
                         if obj.etiquette is not None and obj.etiquette.espace_vital is not None]))
        print 'xxyy', xxyy
        if xxyy:
            # 'None' indique que l'objet ne fournit pas d'indication de dimension
            # pour les abscisses ou pour les ordonnées.
            _ajuster_xmin = _ajuster_xmax = True
            xmins = [x for x in xxyy[0] if x is not None]
            if xmins:
                xmin = min(xmins)
            else:
                xmin = self.fenetre[0]
                _ajuster_xmin = False
            xmaxs = [x for x in xxyy[1] if x is not None]
            if xmaxs:
                xmax = max(xmaxs)
            else:
                xmax = self.fenetre[1]
                _ajuster_xmax = False
            ymin = min(y for y in xxyy[2] if y is not None)
            ymax = max(y for y in xxyy[3] if y is not None)
            dx = xmax - xmin
            dy = ymax - ymin
            # des valeurs trop proches pour xmin et xmax risquent de faire planter l'affichage.
            if dx < 100*param.tolerance:
                r = (self.fenetre[1] - self.fenetre[0])/2
                xmin -= r
                xmax += r
            else:
                if _ajuster_xmin:
                    xmin -= .05*dx
                if _ajuster_xmax:
                    xmax += .05*dx

            if dy < 100*param.tolerance: # idem pour ymin et ymax
                r = abs(self.fenetre[3] - self.fenetre[2])/2
                ymin -= r
                ymax += r
            else:
                ymin -= .05*dy
                ymax += .05*dy

            self.fenetre = xmin, xmax, ymin, ymax
            if param.debug:
                print "ZOOM AUTO :", xmin, xmax, ymin, ymax,  xxyy


    @track
    def orthonormer(self, event = None, mode = 1):
        u"""
        mode 0 : on orthonormalise le repère en restreignant la vue.
        mode 1 : on orthonormalise le repère en élargissant la vue."""
        if mode:
            xcoeff = self.coeff(1)/self.coeff(0) if self.coeff(0) < self.coeff(1) else 1
            ycoeff = 1 if self.coeff(0) < self.coeff(1) else self.coeff(0)/self.coeff(1)
        else:
            xcoeff = self.coeff(1)/self.coeff(0) if self.coeff(0) > self.coeff(1) else 1
            ycoeff = 1 if self.coeff(0) > self.coeff(1) else self.coeff(0)/self.coeff(1)
        xmin, xmax, ymin, ymax = self.fenetre
        x, y, rx, ry = (xmin+xmax)/2., (ymin+ymax)/2., (xmax-xmin)/2., (ymax-ymin)/2.
        self.fenetre = x - xcoeff*rx, x + xcoeff*rx, y - ycoeff*ry, y + ycoeff*ry

    # < Zooms concernant uniquement la taille des objets >

    def zoom_text(self, event = None, valeur = 100):
        self.zoom_texte = valeur/100
##        self.rafraichir_affichage()

    def zoom_line(self, event = None, valeur = 100):
        self.zoom_ligne = valeur/100
##        self.rafraichir_affichage()

    def zoom_normal(self, event = None):
        self.zoom_texte = 1
        self.zoom_ligne = 1
##        self.rafraichir_affichage()

    def zoom_large(self, event = None):
        self.zoom_texte = 1.2
        self.zoom_ligne = 1.4
##        self.rafraichir_affichage()

    def zoom_videoprojecteur(self, event = None):
        self.zoom_texte = 1.6
        self.zoom_ligne = 2
##        self.rafraichir_affichage()

    def zoom_videoprojecteur_large(self, event = None):
        self.zoom_texte = 2.2
        self.zoom_ligne = 3
##        self.rafraichir_affichage()

    # </ Fin des zooms sur la taille des objets >


    @track
    def repere_Oij(self, event = None):
        self.repere = ('O', 'i', 'j')

    @track
    def repere_OIJ(self, event = None):
        self.repere = ('O', 'I', 'J')

    @track
    def repere_011(self, event = None):
        ux, uy = self.gradu
        self.repere = ('0', str(ux), str(uy))


    @track
    def quadrillage_millimetre(self, event = None):
        self.quadrillages = (  ((1, 1), ':', 1, 'k'),
                            ((0.5, 0.5), '-', 0.25, 'k'),
                            ((0.1, 0.1), '-', 0.1, 'k'),
                            )

    @track
    def quadrillage_millimetre_colore(self, event = None, couleur = None):
        if couleur is None:
            couleur = self.couleur_papier_millimetre
        self.quadrillages = (  ((1, 1), ':', 1, couleur),
                                    ((0.5, 0.5), '-', 0.25, couleur),
                                    ((0.1, 0.1), '-', 0.1, couleur),
                                    )

    @track
    def quadrillage_demigraduation(self, event = None):
        ux, uy = self.gradu
        self.quadrillages = (  ((ux, uy), ':', 1, 'k'),
                                    ((ux/2, uy/2), '-', 0.25, 'k'),
                                    )

    @track
    def quadrillage_demigraduation_colore(self, event = None, couleur = None):
        ux, uy = self.gradu
        if couleur is None:
            couleur = self.couleur_papier_millimetre
        self.quadrillages = (  ((ux, uy), ':', 1, couleur),
                                    ((ux/2, uy/2), '-', 0.25, couleur),
                                    )

    @track
    def quadrillage_defaut(self, event = None):
        self.quadrillages = self.param("quadrillages", defaut = True)


# Evenements concernant directement la feuille
################################

    def coder(self, event):
        self.executer(u"coder()")

    def decoder(self, event):
        self.executer(u"effacer_codage()")

    def nettoyer_feuille(self, event):
        self.executer(u"nettoyer()")

    def effacer_traces(self, event):
        self.feuille_actuelle.effacer_traces()

    def executer(self, commande, parser = False):
        u"""Exécute une commande dans la feuille.

        NB: le parser n'est *PAS* activé par défaut, par souci de rapidité."""
        self.feuille_actuelle.executer(commande, parser = parser)


#    Gestion de l'affichage
#################################




    def rafraichir_affichage(self, dessin_temporaire = False, rafraichir_axes = None):
        if rafraichir_axes is not None:
            self.feuille_actuelle._repere_modifie = rafraichir_axes
        self.feuille_actuelle.affichage_perime()
        self._dessin_temporaire = dessin_temporaire

    def _actualiser_si_necessaire(self, event = None, _n=[0]):
#        _n[0] += 1
        if self.feuille_actuelle._affichage_a_actualiser:
#            print _n[0], u"Affichage actualisé."
            self._actualiser()

    def _actualiser(self, _n = [0]):
        # Le code suivant est à activer uniquement pour le débogage de l'affichage:
        # <DEBUG>
        if param.debug:
            s = "Actualisation"
            if self.feuille_actuelle._repere_modifie:
                s += " complete"
            print s + str(_n) + ": " + self.parent.__titre__
            _n[0] += 1
        # </DEBUG>
        try:
            self.graph.dessiner(dessin_temporaire = self._dessin_temporaire,
                        rafraichir_axes = self.feuille_actuelle._repere_modifie)
        except Exception:
            # Ne pas bloquer le logiciel par des rafraichissements successifs en cas de problème.
            print_error()
        self.feuille_actuelle._repere_modifie = False
        self.feuille_actuelle._affichage_a_actualiser = False
        self._dessin_temporaire = False



    def param(self, key, **kw):
        return getattr(param, key)
