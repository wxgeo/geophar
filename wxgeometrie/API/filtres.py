# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                    Filtres                    #
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

__doc__ = u"""Gère l'import de fichiers de versions antérieures de WxGéométrie.

À terme, on devrait aussi pouvoir importer ou exporter des fichiers Géogébra par exemple.
"""

import re


def filtre_versions_anterieures(fgeo):
    version = fgeo.version_interne()
    if fgeo.contenu.has_key("Affichage"):
        if fgeo.contenu["Affichage"]:
            parametres = fgeo.contenu["Affichage"][0]
            # 0.109
            if version < [0, 109]:
                parametres["taille"][0] = parametres["taille"][0][:-1] + ', "|":8}'

    if fgeo.contenu.has_key("Figure"):
        figures = fgeo.contenu["Figure"]
        for i in xrange(len(figures)):
            # 0.106
            if version < [0, 106]:
                figures[i] = figures[i].replace("'label': None, ", "'label': '', 'legende': 1, ")
                figures[i] = figures[i].replace("creer_feuille()", "")
            # 0.108
            if version < [0, 108]:
                lignes = figures[i].split("\n")
                for j in range(len(lignes)):
                    if not re.match(u"[A-Za-z_][A-Za-z_0-9]*[=](Point|Intersection|Glisseur|Projete|Barycentre|Milieu|Centre|Orthocentre)", lignes[j]):
                        lignes[j] = lignes[j].replace(u"'legende': 1", u"'legende': 2")
                figures[i] = "\n".join(lignes)

            # 0.120 alpha 1
            if version < [0, 120, -3, 1]:
                figures[i] = figures[i].replace("_prime", "_").replace("_seconde", "__").replace("_tierce", "___")
                figures[i] = figures[i].replace("set_fenetre(",  "fenetre = (")
                figures[i] = figures[i].replace(" 'noms': {'point_final'",  " '_noms_': {'extremite'")
                figures[i] = figures[i].replace(" 'noms': {'",  " '_noms_': {'")
                def corrige1(match_obj):
                    pt = match_obj.group("pt")
                    dte = match_obj.group("dte")
                    cer = match_obj.group("cer")
                    deb = match_obj.group("deb")
                    return deb + dte + "," + cer + "," + dte + ".point1 is " + pt
                figures[i] = re.sub("(?P<deb>Intersection_droite_cercle[(])(?P<dte>[a-zA-Z_]\w*)[,](?P<cer>[A-Za-z_]\w*)[,](?P<pt>[a-zA-Z_]\w*)", corrige1, figures[i])
                figures[i] = figures[i].replace(".ordonnee()", ".ordonnee")\
                                                .replace(".abscisse()", ".abscisse")\
                                                .replace(".x()", ".x")\
                                                .replace(".y()", ".y")\
                                                .replace(".rayon()", ".rayon")\
                                                .replace(".longueur()", ".longueur")\
                                                .replace(".equation()", ".equation")\
                                                .replace(".val()", ".val")\
                                                .replace(".norme()", ".norme")\
                                                .replace(".coordonnees()", ".coordonnees")
                def corrige2(match_obj): #Droite_vectorielle
                    deb = match_obj.group("deb")
                    vec = match_obj.group("vec")
                    pt = match_obj.group("pt")
                    return deb + pt + "," + vec
                figures[i] = re.sub("(?P<deb>Droite_vectorielle[(])(?P<vec>[a-zA-Z_]\w*)[,](?P<pt>[A-Za-z_]\w*)", corrige2, figures[i])
                def corrige3(match_obj): #Mediatrice
                    return match_obj.group().replace("objet1=", "point1=")\
                                                            .replace("objet2=", "point2=")\
                                                            .replace("objet1 =", "point1 =")\
                                                            .replace("objet2 =", "point2 =")
                figures[i] = re.sub("Mediatrice[(].*$", corrige3, figures[i])
                def corrige4(match_obj): #Bissectrice
                    return match_obj.group().replace("pt1==", "point1=")\
                                                            .replace("pt2=", "point2=")\
                                                            .replace("pt3=", "point3=")\
                                                            .replace("pt1 =", "pt1 =")\
                                                            .replace("pt2 =", "pt2 =")\
                                                            .replace("pt3 =", "p3 =")
                figures[i] = re.sub("Bissectrice[(].*$", corrige4, figures[i])
                def corrige5(match_obj): #Barycentre
                    s = match_obj.group().replace(" ", "")
                    if "points=" in s:
                        s = s.replace("points=", "'points':").replace("coeffs=", "'coeffs':")
                        m = re.search("(?P<deb>Barycentre[()])(?P<milieu>.*)(?P<fin>[,][*][*].*)", s)
                        return m.group("deb") + "*zip({" + m.group("milieu") + "}['points'],{" + m.group("milieu") + "}['coeffs'])" + m.group("fin")
                    else:
                        m = re.search("(?P<deb>Barycentre[()])(?P<milieu>.*)(?P<fin>[,][*][*].*)", s)
                        return m.group("deb") + "*zip(" + m.group("milieu") + ")" + m.group("fin")
                figures[i] = re.sub("Barycentre[(].*", corrige5, figures[i])

            # 0.120 beta 6
            # t, x, y sont maintenant des noms réservés pour un usage futur.
            if version < [0, 120, -2, 6]:
                lignes = figures[i].split("\n")
                for num_ligne in xrange(len(lignes)):
                    if len(lignes[num_ligne]) > 1 and lignes[num_ligne][0] in "txy" and lignes[num_ligne][1] in "=.":
                        lignes[num_ligne] = "Objet_" + lignes[num_ligne]
                figures[i] = "\n".join(lignes)

            # 0.123.1
            # Les noms Cercle et Cercle_rayon permutent.
            if version < [0, 123, 1]:
                figures[i] = figures[i].replace("Cercle_rayon(", "_Gtftqsff45ezytaezfehge(").replace("Cercle(", "Cercle_rayon(").replace("_Gtftqsff45ezytaezfehge(", "Cercle(")

            # version 0.124
            # Nouveau codage des ' et autres " dans les noms d'objets
            # Le filtre n'est pas parfait, et ne règle que les cas les plus courants
            if version < [0, 124]:
                def transformer(match_obj):
                    chaine = match_obj.group(0)
                    if chaine in ['Label_segment', 'Glisseur_arc_cercle', 'Objet_avec_coordonnees_modifiables', 'Secteur_angulaire', 'Label_angle', 'Widget', 'Perpendiculaire', 'Label_vecteur', 'Centre_cercle_inscrit', 'Texte_translation', 'Pentagone', 'Orthocentre', 'Demidroite', 'Cercle_equation', 'Cercle_points', 'Point_pondere', 'Variable', 'Point_homothetie', 'Extremite', 'Vecteur', 'Point_equidistant', 'Rotation', 'Centre_cercle_circonscrit', 'Point_final', 'Segment', 'Courbe_generique', 'Label_arc_cercle', 'Glisseur_ligne_generique', 'Courbe', 'Projete_arc_cercle', 'Tangente', 'Triangle_equilateral', 'Disque', 'Label_point', 'Somme_vecteurs', 'Label_generique', 'Cube', 'Label_demidroite', 'Vecteur_libre', 'Angle_libre', 'Ligne_generique', 'Cote', 'Glisseur_segment', 'Projete_droite', 'Glisseur_droite', 'Centre_polygone_generique', 'Sommet_polyedre', 'Demicercle', 'Heptagone', 'Quadrilatere', 'Label_polygone', 'Sommet_triangle_isocele', 'Sommet_rectangle', 'Homothetie', 'Parallelogramme', 'Transformation_generique', 'Cercle_rayon', 'Point_reflexion', 'Polygone_regulier_centre', 'Point_rotation', 'Point_droite', 'Interpolation_cubique', 'Interpolation_lineaire', 'Hexagone', 'Sommet', 'Objet_numerique', 'Centre_gravite', 'Glisseur_vecteur', 'Intersection_generique', 'PointTangence', 'Mediatrice', 'Rectangle', 'Objet', 'Bissectrice', 'Barycentre', 'Angle_oriente', 'Point_translation', 'Tetraedre', 'Projete_generique', 'Vecteur_generique', 'Representant', 'Glisseur_demidroite', 'Arete', 'Texte_transformation_generique', 'Objet_avec_valeur', 'Texte_homothetie', 'Label_cercle', 'Translation', 'Triangle_isocele_rectangle', 'Cercle_generique', 'Triangle_equilateral_centre', 'Cercle', 'Centre', 'Angle_generique', 'Octogone', 'Point_generique', 'Objet_avec_equation', 'Polygone', 'Interpolation_generique', 'Angle', 'Label_droite', 'Texte_generique', 'Milieu', 'Losange', 'Projete_segment', 'Polygone_generique', 'Glisseur_generique', 'Arc_points', 'Cercle_diametre', 'Triangle', 'Droite_vectorielle', 'Intersection_droite_cercle', 'Glisseur_cercle', 'Polyedre_generique', 'Triangle_isocele', 'Arc_oriente', 'Projete_demidroite', 'Projete_cercle', 'Parallele', 'Texte_rotation', 'Polygone_regulier', 'Droite_equation', 'Droite_generique', 'Arc_generique', 'Sommet_triangle_rectangle', 'Objet_avec_coordonnees', 'Fonction', 'Arc_cercle', 'PrevisualisationPolygone', 'Carre_centre', 'Angle_vectoriel', 'Carre', 'Interpolation_quadratique', 'Intersection_droites', 'Triangle_rectangle', 'Intersection_cercles', 'Texte', 'Texte_reflexion', 'Reflexion', 'Point', 'Droite', 'Sommet_cube', 'Symetrie_centrale', 'Vecteur_unitaire', 'creer_feuille', 'rafraichir_feuille']:
                        return chaine
                    return chaine.replace("_", "_prime")
                figures[i] = re.sub("""(?<![A-Za-z_'"])[A-Za-z][A-Za-z_]+(?![A-Za-z0-9_{'"])""", transformer, figures[i])
                if fgeo.module == 'probabilites':
                    figures[i] = figures[i].replace('$P_prime', '$P_').replace('$p_prime', '$p_')

            # version 0.125
            if version < [0, 125]:
                lignes = figures[i].split("\n")
                figures[i] = "\n".join(ligne for ligne in lignes if ligne != "rafraichir_feuille()")

            # version 0.126
            if version < [0, 126]:
                figures[i] = figures[i].replace("Variable(valeur=", "Variable(contenu=").replace("Angle_libre(valeur=", "Angle_libre(variable=")

            # version 0.129
            # (Le filtre n'est pas parfait)
            if version < [0, 129]:
                figures[i] = re.sub("(?<![A-Za-z0-9_])C?f[0-9]+(?![A-Za-z0-9_])",lambda r:r.group(0) + "_", figures[i])

            # version 0.130 bêta 1
            # (Le filtre n'est pas parfait)
            if version < [0, 130, -1, 1]:
                if fgeo.module == 'probabilites':
                    figures[i] = figures[i].replace("'$$", "'$").replace("$$'", "$'")

    if fgeo.contenu.has_key("Courbe") and fgeo.module == 'traceur':
        courbes = fgeo.contenu["Courbe"]
        figures = fgeo.contenu["Figure"]
        for i, courbe in enumerate(courbes):
            n = i + 1
            Y = courbe['Y'][0]
            intervalle = courbe['intervalle'][0]
            visible = courbe['active'][0]
            couleur = 'brgmcyk'[i%7]
            code = "\nf%(n)s = Fonction(expression=u'%(Y)s',ensemble='%(intervalle)s',variable='x')\n" %locals()
            code += "Cf%(n)s = Courbe(fonction=f%(n)s, **{'couleur': u'%(couleur)s', 'visible': %(visible)s, 'protege': True})\n" %locals()
            figures[0] += code
