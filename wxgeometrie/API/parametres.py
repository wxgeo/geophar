# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##########################################################################
#
#                       Sauvegarde et chargement des paramètres
#
##########################################################################
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

import time
from types import NoneType

from . import sauvegarde
from ..pylib import print_error, eval_safe
from .. import param

types_supportes = (int, long, str, unicode, float, bool, NoneType, list, tuple, dict)

# TO DO (?) :
# - rajouter le support des types array et complex dans securite.eval_safe
# - gérer correctement l'encodage dans save.py
#   (tout convertir en unicode, puis en utf-8)


def sauvegarder_module(module, nom = "main"):
    u"""Renvoie le contenu d'un module sous forme d'un fichier XML.

    Au lieu du module lui-même, 'module' peut être un dictionnaire
    correspondant au dictionnaire du module (éventuellement modifié).
    """
    dico = module.__dict__.copy() if not isinstance(module, dict) else module
    for key in param.valeurs_a_ne_pas_sauver:
        dico.pop(key, None)
    f = sauvegarde.FichierGEO(type = 'Options WxGeometrie', module = nom)
    m = f.ajouter("Meta")
    f.ajouter("date", m, time.strftime("%d/%m/%Y - %H:%M:%S",time.localtime()))
    p = f.ajouter("Parametres")
    for key, value in dico.items():
        if not key.startswith("_") and isinstance(value, types_supportes):
            f.ajouter(key, p, repr(value))
    return f


def actualiser_module(module, fichier):
    u"Rafraichit le contenu d'un module à partir d'un fichier XML."
    if fichier:
        fgeo, msg = sauvegarde.ouvrir_fichierGEO(fichier)
    else:
        fgeo = None
    copie = module.__dict__.copy()
    copie.pop("__builtins__", None)
    setattr(module, "_parametres_par_defaut", copie)
    if fgeo is not None:
        parametres = fgeo.contenu["Parametres"][-1]
        try:
            for key in parametres:
                setattr(module, key, eval_safe(parametres[key][-1]))
        except:
            print module, key
            print_error()


#def extraire_parametre(fichier, parametre):
#    fgeo, msg = sauvegarde.ouvrir_fichierGEO(fichier)
#    parametres = fgeo.contenu["Parametres"][-1]
#    return parametres[parametre][-1]
