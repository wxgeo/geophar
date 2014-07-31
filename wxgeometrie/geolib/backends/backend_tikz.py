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


class BackendTikz(object):

    def exporter(self, feuille, **options):
        commands = [r'\begin{tikzpicture}']
        commands.append(self._export_repere(feuille))
        for objet in feuille.liste_objets(objets_caches=False, etiquettes=True):
            for classe in objet.__class__.__mro__:
                methode = '_export_' + classe.__name__
                if hasattr(self, methode):
                    commands.append(getattr(self, methode)(objet, **options))
                    break
        return '\n'.join(commands + [r'\end{tikzpicture}'])

    def _export_repere(self, feuille, **options):
        return ''

    def _export_Objet(self, objet, **options):
        print(u"Warning: type d'objet non supporté pour l'instant : "
              + str(objet.__class__.__name__))
        return ''

    def _export_Point_generique(self, P, **options):
        return r'\draw (%s, %s) node {$\bullet$};' % (P.x, P.y)
        #~ \node at (1,0) [label={[shift={(1.0,0.3)}]label}] {Node};

    def _export_Texte_generique(self, txt, **options):
        return r'\draw (%s, %s) node {%s};' % (txt.x, txt.y, txt.label())

    def _export_Polygone_generique(self, poly, **options):
        l = ['(%s, %s)' % (P.x, P.y) for P in poly.points]
        return r'\draw %s;' % ' -- '.join(l)

    def _export_Segment(self, s, **options):
        A, B = s.extremites
        return r'\draw (%s, %s) -- (%s, %s);' % (A.x, A.y, B.x, B.y)
