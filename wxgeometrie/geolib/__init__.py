# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

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


from .angles import Angle_generique, Secteur_angulaire, Angle_oriente, Angle, Angle_libre, Angle_vectoriel
from .cercles import Cercle_Arc_generique, Arc_generique, Arc_cercle, Arc_points, Arc_oriente, Demicercle, Cercle_generique, Cercle_rayon, Cercle, Cercle_diametre, Cercle_points, Cercle_equation, Disque
from .classeur import Classeur
from .constantes import RIEN, TEXTE, NOM, FORMULE, MILIEU, DEBUT, MILIEU, FIN
from .contexte import Contexte, contexte
from .courbes import Courbe_generique, Courbe
from .feuille import MethodesObjets, Liste_objets, ModeTolerant, Dictionnaire_objets, Interprete_feuille, Historique_feuille, Feuille
from .formules import Formule
from .fonctions import Fonction
from .interpolations import Interpolation_generique, Interpolation_lineaire, Interpolation_quadratique, Interpolation_cubique
from .intersections import Intersection_generique, Intersection_droites, Intersection_droite_cercle, Intersection_cercles, Intersection
from .labels import Label_generique, Label_point, Label_segment, Label_vecteur, Label_droite, Label_demidroite, Label_cercle, Label_arc_cercle, Label_polygone, Label_angle
from .lignes import Ligne_generique, Segment, Demidroite, Droite_generique, Droite, Point_droite, Droite_vectorielle, Parallele, Perpendiculaire, Mediatrice, Droite_equation, Bissectrice, Point_tangence, Tangente, DemiPlan, Axe, Tangente_courbe
from .objet import Nom, Rendu, Cache, Ref, BaseArgument, Argument, ArgumentNonModifiable, Arguments, TupleObjets, DescripteurFeuille, Objet, Objet_avec_coordonnees, Objet_avec_coordonnees_modifiables, Objet_avec_equation, Objet_avec_valeur, Objet_numerique, G, TYPES_NUMERIQUES
from .points import Point_generique, Point, Point_pondere, Barycentre, Milieu, Point_final, Point_translation, Point_rotation, Point_homothetie, Point_reflexion, Projete_generique, Projete_droite, Projete_cercle, Projete_arc_cercle, Projete_segment, Projete_demidroite, Centre_polygone_generique, Centre_gravite, Orthocentre, Centre_cercle_circonscrit, Centre_cercle_inscrit, Centre, Point_equidistant, Glisseur_generique, Glisseur_vecteur, Glisseur_ligne_generique, Glisseur_droite, Glisseur_segment, Glisseur_demidroite, Glisseur_cercle, Glisseur_arc_cercle, Nuage_generique, Nuage, NuageFonction
from .polyedres import Arete, Sommet_polyedre, Polyedre_generique, Tetraedre, Sommet_cube, Cube
from .polygones import Cote, Sommet, Polygone_generique, Polygone, Triangle, Quadrilatere, Pentagone, Hexagone, Heptagone, Octogone, Parallelogramme, Sommet_rectangle, Rectangle, Losange, Polygone_regulier_centre, Triangle_equilateral_centre, Carre_centre, Polygone_regulier, Triangle_equilateral, Carre, Sommet_triangle_isocele, Triangle_isocele, Sommet_triangle_rectangle, Triangle_rectangle, Triangle_isocele_rectangle, PrevisualisationPolygone
#from .pseudo_canvas import PseudoContexte, PseudoCanvas
from .textes import Texte_generique, Texte, Texte_transformation_generique, Texte_rotation, Texte_translation, Texte_homothetie, Texte_reflexion
from .transformations import Transformation_generique, Rotation, Translation, Reflexion, Homothetie, Symetrie_centrale
from .variables import Variable_generique, Variable, Rayon, Mul, Add
from .vecteurs import Vecteur_generique, Vecteur, Vecteur_libre, Vecteur_unitaire, Somme_vecteurs, Extremite, Representant
#from .wxwidgets import Widget


for _obj in vars().values():
    if isinstance(_obj, type) and issubclass(_obj, Objet):
        prefixe = "_" + _obj.__name__ + "__"
        __arguments__ = []
        for key, value in vars(_obj).iteritems():
            if isinstance(value, BaseArgument) and key.startswith(prefixe):
                # Chaque argument récupère son nom...
                value.nom = key
                # ...et sa classe de rattachement :
                value.rattachement = _obj
                # Chaque classe recupère la liste de ses arguments... (en évitant d'utiliser 'inspect', qui n'est pas compatible avec psycho)
                # On cherche les entrées de la classe 'MaClasse' qui soient de type 'Argument' ou 'Arguments',
                # et qui commencent par '_MaClasse__'.
                # Exemple : '_MaClasse__monargument' qui est stocké comme 'monargument' (on enlève le préfixe).
                __arguments__.append((value.__compteur__, key[len(prefixe):]))
        # on trie les arguments par ordre de déclaration dans la classe
        __arguments__.sort()
        _obj.__arguments__ = tuple(key for compteur, key in __arguments__) # tuple pour éviter des bugs (partage d'1 même liste entre plusieurs classes par ex.)

del _obj

G.__dict__.update(locals())
vecteur_unite = G.vecteur_unite = Vecteur_libre(1, 0)
feuille_par_defaut = G.feuille_par_defaut = Feuille()
