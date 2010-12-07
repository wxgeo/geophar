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

# version unicode

from LIB import *
import sauvegarde
#import types, param, time, securite
types_supportes = (int, long, str, unicode, float, bool, types.NoneType, list, tuple, dict)
# TO DO :
# - rajouter le support des types array et complex dans securite.eval_safe
# - gérer correctement l'encodage dans save.py
#   (tout convertir en unicode, puis en utf-8)


#~ def __sauvegarder_module_old(module, nom = "main"):
    #~ u"Renvoie le contenu d'un module sous forme d'un fichier XML."
    #~ dico = module.__dict__.copy()
    #~ dico.pop("__builtins__", None)
    #~ xml  = "<?xml version='1.0' encoding='utf-8'?>\n"
    #~ xml += "<Document type='Options WxGeometrie' version='%s' module='%s'>\n" %(param.version, nom)
    #~ xml += "<Meta>\n<notes>\n</notes>\n<date>\n%s\n</date>\n</Meta>\n<Parametres>\n" %time.strftime("%d/%m/%Y - %H:%M:%S",time.localtime())
    #~ for key in dico:
        #~ if key not in wxgeo.__dict__.keys() and not key.startswith("_") and isinstance(dico[key], types_supportes):
            #~ xml += "<%s>\n%s\n</%s>\n " %(key, uu(dico[key]).encode("utf-8").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), key)
    #~ xml += "</Parametres>\n</Document>"

    #~ return xml


def sauvegarder_module(module, nom = "main"):
    u"Renvoie le contenu d'un module sous forme d'un fichier XML."
    dico = module.__dict__.copy()
    for key in param.valeurs_a_ne_pas_sauver:
        dico.pop(key, None)
    #for key in wxgeo.__dict__.keys():
    #    dico.pop(key, None)
    f = sauvegarde.FichierGEO(type = 'Options WxGeometrie', module = nom)
    m = f.ajouter("Meta")
    #~ f.ajouter("notes", m, "")
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
                setattr(module, key, securite.eval_safe(parametres[key][-1]))
        except:
            print module, key
            print_error()

#def sauvegarder_session(*fichiers):
#    u"""Crée un fichier XML contenant tout le contenu de la session courante,
#    à partir de la liste des fichiers ouverts."""
#    fgeo = sauvegarde.FichierGEO(type = 'Session WxGeometrie', module = 'main')
#    #~ M = fgeo.ajouter("Meta")
#    #~ fgeo.ajouter("notes", M, "")
#    #~ fgeo.ajouter("date", M, time.strftime("%d/%m/%Y - %H:%M:%S",time.localtime()))
#    F = fgeo.ajouter('Fichiers')
#    for fichier in fichiers:
#        f = fgeo.ajouter('fichier', F, fichier.contenu)
#        i = fgeo.ajouter('infos', f)
#        for info, val in fichier.infos.items():
#            i[info] = [val]
#    return fgeo

#def ouvrir_session(fichier):
#    u"""Crée une liste de fichiers à ouvrir à partir du fichier de sauvegarde de la session courante.
#    """
#    if not isinstance(fichier, sauvegarde.FichierGEO):
#        fichier, message = sauvegarde.ouvrir_fichierGEO(fichier)
#    liste_fichiers = []
#    try:
#        for contenu in fichier.contenu['Fichiers'][0]['fichier']:
#            infos = contenu.pop('infos')
#            module = infos[0]['module'][0]
#            fgeo = sauvegarde.FichierGEO(module = module)
#            fgeo.contenu = contenu
#            liste_fichiers.append(fgeo)
#    except (KeyError, IndexError):
#        #TODO: message d'erreur indiquant que le format de fichier de session est incorrect
#        raise
#    return liste_fichiers
