#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------##
#              WxGeometrie            #
#              mode script              #
##--------------------------------------##
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

from ..geolib.feuille import Feuille
from ..API.canvas import Canvas
from ..API.sauvegarde import ouvrir_fichierGEO
from ..pylib import print_error
from .. import param


def _err(msg, *msgs):
    msg = "== Erreur: %s ==" %msg
    if msgs:
        msg += '\n---\n' + '\n'.join(msgs) + '\n---'
    return msg


def wxgeometrie_mode_script(input = None, output = None):
    try:
        if input is None:
            input = raw_input(u'Adresse du fichier de script ou du fichier .geo :')

        if input.endswith('.geo') or input.endswith('.geoz'):
            fgeo, message = ouvrir_fichierGEO(input)
            if fgeo is None:
                return _err(message)
            try:
                commandes = fgeo.contenu["Figure"][0]
            except KeyError:
                return  _err(u"Le fichier '%s' ne comporte pas de figure." %input)

        else:
            try:
                with open(input, 'r') as f:
                    commandes = f.read()
            except IOError:
                print_error()
                return _err(u"Fichier introuvable: '%s'" % input)

        feuille = Feuille()
        canvas = Canvas(feuille = feuille)
        feuille.canvas = canvas
        try:
            feuille.charger(commandes)
        except Exception:
            print_error()
            return _err(u"Commandes incorrectes", commandes)

        if output is None:
            output = raw_input(u'Adresse du fichier de sortie (png/svg/...) :')

        try:
            print canvas.fenetre
            canvas.exporter(output, echelle = param.echelle_cm)
        except IOError:
            print_error()
            return _err(u"Impossible d'exporter dans '%s'. Vérifiez les permissions ou l'espace disque." % output)

    except Exception:
        print_error()
        return _err(u"Erreur d'exécution du mode script.")
