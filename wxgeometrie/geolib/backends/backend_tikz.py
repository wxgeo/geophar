# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

##---------------------------------------#######
#                  Backends                    #
##---------------------------------------#######
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
from re import sub, compile

from ...mathlib.intervalles import conversion_chaine_ensemble
from ...mathlib.parsers import traduire_formule, NBR_SIGNE_OR_VAR


# \usetikzlibrary{arrows.meta}

class BackendTikz(object):

    _arrow = '-{Stealth[scale=1.7]}'

    _dict_styles_traits = {':': 'dotted', '--': 'dashed', '-': 'solid',
                           '.-': 'dashdotted', '-.': 'dashdotted'}

    _dict_couleurs = {'g': 'green', 'r': 'red', 'b': 'blue', 'y': 'yellow',
                     'k': 'black', 'c': 'cyan', 'm': 'magenta', 'w': 'white'}

    def _style_trait(self, style):
        return self._dict_styles_traits.get(style, '')

    def _epaisseur(self, value):
        u'Convertit la largeur de ligne.'
        return str(value/2) + 'pt'

    def _couleur(self, couleur):
        if isinstance(couleur, tuple):
            r, g, b, a = couleur
            return '{rgb:red,%s;green,%s;blue,%s}' % (r, g, b)
        else:
            return self._dict_couleurs.get(couleur, couleur)

    def _add(self, commande):
        self._lignes.append(commande)

    def _draw(self, path, options=[], arrow=False, node='', **style):
        options = options[:] # Attention à bien recréer une nouvelle liste !
        if isinstance(path, (list, tuple)):
            path = ' -- '.join('(%s, %s)' % (x, y) for x, y in path)
        if 'couleur' in style:
            options.append('color=' + self._couleur(style['couleur']))
        if 'style' in style:
            options.append(self._style_trait(style['style']))
        if 'epaisseur' in style:
            options.append('line width=' + self._epaisseur(style['epaisseur']))
        if arrow:
            options.append(self._arrow)
        if node:
            node = ' node ' + node
        self._add(r'\draw[%s] %s%s;' % (', '.join(filter(None, options)), path, node))

    def exporter(self, feuille, **options):
        deb = r'\begin{tikzpicture}'
        if options.get('echelle') is not None:
            deb += '[scale=%s]' % options['echelle']
        self._lignes = [deb]
        self._export_repere(feuille)
        for objet in feuille.liste_objets(objets_caches=False, etiquettes=False):
            for classe in objet.__class__.__mro__:
                methode = '_export_' + classe.__name__
                if hasattr(self, methode):
                    getattr(self, methode)(objet, **options)
                    break
        self._lignes.append(r'\end{tikzpicture}')
        return '\n'.join(self._lignes)

    def _export_repere(self, feuille, **options):
        xmin, xmax, ymin, ymax = feuille.fenetre_reellement_affichee()
        xgradu, ygradu = feuille.gradu
        origine, abscisse, ordonnee = feuille.repere
        self._add(r'\clip (%s, %s) rectangle (%s, %s);' % (xmin, ymin, xmax, ymax))

        if feuille.afficher_quadrillage:
            # TODO: style, epaisseur, couleur
            # Créer des dictionnaires convertir style et epaisseur.

            for (xpas, ypas), style, epaisseur, couleur in feuille.quadrillages:
                xpas = xpas or xgradu
                ypas = ypas or ygradu
                self._draw('(%s, %s) grid (%s, %s)' % (xmin, ymin, xmax, ymax),
                            options=['xstep=%s' % xpas, 'ystep=%s' % ypas,
                                     self._style_trait(style),
                                    'color=%s' % self._couleur(couleur),
                                    'line width=%s' % self._epaisseur(epaisseur)])
        if feuille.afficher_axes:
            self._draw([(xmin, 0), (xmax, 0)], arrow=True)
            self._draw([(0, ymin), (0, ymax)], arrow=True)
            # TODO: support des vecteurs i et j
            options = ['thick']
            self._draw('(0, 0) node[below left] {$%s$}' % origine, options)
            self._draw('(%s, 2pt) -- (%s, -2pt)' % (xgradu, xgradu), options,
                        node='[below] {$%s$}' % abscisse)
            self._draw('(2pt, %s) -- (-2pt, %s)' % (ygradu, ygradu), options,
                        node='[left] {$%s$}' % ordonnee)

    def _export_Objet(self, objet, **options):
        print(u"Warning: type d'objet non supporté pour l'instant : "
              + str(objet.__class__.__name__))
        return ''

    def _export_Point_generique(self, P, **options):
        # 1.8 : coefficient purement empirique...!
        r = 1.8*P.etiquette.style('_rayon_')
        a = P.etiquette.style('_angle_')*180/pi
        # TODO: gérer style du point
        self._draw([P], node=r'(%s) {\small $\bullet$}' % P.nom)
        self._add(r'\path (%s) ++(%s:%s pt) node (%s_etiquette) {%s};'
                    % (P.nom, a, r, P.nom, P.label()))
        #~ \path (A) ++(30:2) node (B) [draw,fill=blue!20] {B};
        #~ \node at (1,0) [label={[shift={(1.0,0.3)}]label}] {Node};

    def _export_Texte_generique(self, txt, **options):
        self._draw([txt], node='{%s}' % txt.label())

    def _export_Cercle_generique(self, cercle, **options):
        x, y = cercle.centre
        self._draw('(%s, %s) circle (%s)' % (x, y, cercle.rayon), **cercle.style())

    def _export_Polygone_generique(self, poly, **options):
        self._draw(poly.points, **poly.style())

    def _export_Segment(self, segment, **options):
        self._draw(segment.extremites, **segment.style())

    def _export_Droite(self, droite, **options):
        points = droite._points_extremes()
        if len(points) == 2:
            # Sinon, la droite ne coupe pas la fenêtre (ou seulement en un point)
            self._draw(points, **droite.style())

    def _export_Courbe(self, courbe, **options):
        # TODO: gérer les extrémités de courbe (points, arc de cercle)
        xmin, xmax, ymin, ymax = courbe.feuille.fenetre_reellement_affichee()
        fonction = courbe.fonction
        x = fonction.variable
        liste_fx = fonction.expression.split('|')
        liste_Df = fonction.ensemble.split('|')

        RE_VAR = compile(r'(?<!\w)(%s)(?!\w)' % x)
        x_ = '\\' + x
        for (fx, Df) in zip(liste_fx, liste_Df):
            Df = conversion_chaine_ensemble(Df)
            fx = traduire_formule(fx)
            if '**' in fx or '^' in fx:
                # TODO: gérer les parenthèses imbriquées : (x(x+1))**2
                def conv(m):
                    return 'pow(%s, %s)' % (m.group('a') or m.group('A'), m.group('b') or m.group('B'))
                RE_POW = r'((?P<a>%s)|(?P<A>\([^)]+\)))(\^|\*\*)((?P<b>%s)|\((?P<B>[^)]+)\))' \
                        % (NBR_SIGNE_OR_VAR, NBR_SIGNE_OR_VAR)
                fx = sub(RE_POW, conv, fx)
            fx = sub(RE_VAR, x_, fx)
            for I in Df.intervalles:
                xm = float(max(xmin, I.inf))
                xM = float(min(xmax, I.sup))
                self._draw(r'plot ({%s}, {%s})' % (x_, fx),
                                options=['domain=%s:%s,smooth,samples=500,variable=%s' % (xm, xM, x_)],
                                **courbe.style())
            for val, symb in Df.extremites(xmin, xmax):
                if symb == '.':
                    self._draw(r'(%s, %s) node {\small$\bullet$}', **courbe.style())
                else:
                    print(u"Warning: extrémité de courbe non générée\n"
                          u"(extrémité de type %s non géré pour l'instant)." % repr(symb))

    def _export_Vecteur(self, vecteur, **options):
        A, B = vecteur.extremites
        self._draw(vecteur.extremites, node='[midway] {%s}' % vecteur.label(),
                  options=['auto=right'], arrow=True, **vecteur.style())
