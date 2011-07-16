# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                 Sauvegarde                  #
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

from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError
import tarfile, os, zipfile, re
from cStringIO import StringIO

from .filtres import filtre_versions_anterieures
from ..pylib import print_error, eval_safe, removeend
from .. import param

#----------------------------------
#     DOM pour lire un fichier
#----------------------------------



class FichierGEO(object):
    u"""Classe utilisée pour manipuler un fichier .geo.

    On peut aussi utiliser le DOM XML, mais les spécifications du format de fichier .geo
    sont plus restreintes, et cette classe offre une surcouche au DOM XML pour un accès plus simple."""

    defaut = {"type": "Fichier WxGeometrie", "version": param.version, "module": '', "nom": '', "repertoire": ''}

    def __init__(self, texte = "", encoding = "utf-8", **args):
        self.infos = self.defaut.copy()
        self.infos.update(args)
        self.encoding = encoding
        self.contenu = {}

        if texte: self.importer(texte)


    @property
    def nom(self):    return self.infos['nom']
    @property
    def repertoire(self):    return self.infos['repertoire']
    @property
    def module(self):    return self.infos['module']
    @property
    def type(self):    return self.infos['type']
    @property
    def version(self):    return self.infos['version']
    @property
    def data(self):     return self.exporter().encode(self.encoding)


    def importer(self, texte):
        def contenu_node(node):
            # Le contenu d'une node (contenu entre 2 balises) est soit du texte, soit (ou exclusif!) d'autres balises.
            # Le contenu autorise est ainsi passablement plus restreint que dans la specification XML.
            # Pour plus de detail, lire la doc sur le format de fichier.

            # 1er cas: contenu vide -> assimile a du texte.
            if not node.childNodes:
                return ""

            # 2eme cas: le contenu est purement du texte.
            if not "Element" in [subnode.__class__.__name__ for subnode in node.childNodes]:
                return node.childNodes[0].nodeValue.strip("\n").replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").encode(param.encodage) # un certain nombres de fonctions python supportent encore mal l'unicode (par exemple, f(**{u"a":3}) ne fonctionne pas)

            # 3eme cas: le contenu est un ensemble de balises -> regroupees dans un dictionnaire.
            # ce qui n'est pas entre deux balises est ignore.
            dico = {}
            for elt in node.childNodes:
                if elt.__class__.__name__ == "Element":
                    contenu = contenu_node(elt)
                    if dico.has_key(elt.nodeName):
                        dico[elt.nodeName] += [contenu]
                    else:
                        dico[elt.nodeName] = [contenu]
            return dico


        xml = parseString(texte)
        self.encoding = xml.encoding
        self.document = xml.childNodes[0]
        self.infos = self.defaut.copy() # contient tous les attributs du document
        for attribut in self.document._attrs.keys():
            self.infos[attribut] = self.document._attrs[attribut].value

        self.contenu = contenu_node(self.document)
        return self





    def exporter(self):
        def convertir_contenu(dictionnaire):
            texte = ""
            for balise in dictionnaire.keys():
                for elt in dictionnaire[balise]:
                    texte += "<%s>\n" %balise
                    if isinstance(elt, (str, unicode)):
                        texte += elt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").strip("\n") + "\n"
                    elif isinstance(elt, dict):
                        texte += convertir_contenu(elt)
                    texte += "</%s>\n" %balise

            return texte

        texte = u"<?xml version='1.0' encoding='%s'?>\n" %self.encoding
        texte += u"<Document type='%s' version='%s' module='%s'>\n" %(self.type, self.version, self.module)
        texte += convertir_contenu(self.contenu)
        texte += u"</Document>"
        return texte


    def ajouter(self, nom, racine = None, contenu = None):
        u"""Ajoute une ou plusieurs nouvelle(s) node(s) nommée(s) 'nom' à 'racine', leur contenu étant donné par 'contenu'.
        Renvoie le contenu, ou la nouvelle racine crée (si le contenu était vide)."""
        if racine is None:
            racine = self.contenu
        if contenu is None:
            contenu = {}

        if not racine.has_key(nom):
            racine[nom] = []
        racine[nom].append(contenu)
        return contenu


    def ecrire(self, path, zip = False):
        u"""Ecrit dans un fichier dont l'adresse est donnée par 'path'.

        L'encodage est fixé par 'self.encoding'.
        Eventuellement, le contenu peut-être compressé au format zip."""

        contenu = self.data
        f = None
        rep = os.path.split(path)[0]
        if not os.path.exists(rep):
            os.makedirs(rep)
        try:
            if zip:
                f = zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED)
                f.writestr("content.geo", contenu)
            else:
                f = open(path, "w")
                f.write(contenu)
        finally:
            if f is not None:
                f.close()


    def ouvrir(self, path, zip = None):
        u"""Retourne un objet FichierGEO à partir du fichier dont l'adresse est donnée par 'path'.

        Si l'attribut 'zip' n'est pas fixé, la détection est automatique."""

        f = None
        if not os.path.exists(path):
            return None, u"Le fichier n'existe pas."
        try:
            f = open(path, "rU")
        except IOError:
            print_error()
            return None, u"L'accès au fichier a été refusé."
        except UnicodeError:
            print_error()
            return None, u"Caractères non reconnus."
        except Exception:
            print_error()
            return None, u"Impossible d'ouvrir le fichier."
        try:
            texte = f.read()
        finally:
            f.close()
        try:
            parseString(texte)
        except ExpatError:
            try:
                f = zipfile.ZipFile(path, "r")
                texte = f.read("content.geo")
            finally:
                f.close()
        self.importer(texte)

        # Filtre d'import pour les versions antérieures
        if self.version_interne() < self.version_interne(param.version):
            filtre_versions_anterieures(self)

        rep, fich = os.path.split(path)
        self.infos['repertoire'] = rep
        self.infos['nom'] = removeend(fich, ".geo", ".geoz") # nom sans l'extension

        return self, u"Le fichier %s a bien été ouvert." %path


    def version_interne(self, version = None):
        if version is None:
            version = self.version
        version = version.strip().lower()
        version = version.replace("alpha", "a").replace("beta", "b").replace("release candidate", "rc").replace("releasecandidate", "rc")
        version = version.replace("a", " -3 ").replace("b", " -2 ").replace("rc", " -1 ").replace(".", " ")
        return [int(n) for n in re.split("[ ]+",  version)]



##def __old__ouvrir_fichierGEO(path):
##    u"Désuet. Utiliser plutôt FichierGEO().ouvrir(path)."
##    try:
##        f=open(path,"rU")
##    except IOError:
##        return None, u"Le fichier n'existe pas, ou est inaccessible."
##    except UnicodeError:
##        return None, u"Caractères non reconnus."
##    except:
##        return None, u"Impossible d'ouvrir le fichier."
##    try:
##        texte = f.read()
##    finally:
##        f.close()
##    fgeo = FichierGEO(texte)
##    return fgeo, u"Le fichier %s a bien été ouvert." %path


def ouvrir_fichierGEO(path):
    u"Alias de 'FichierGEO().ouvrir(path)'."
    return FichierGEO().ouvrir(path)



class FichierSession(object):
    # cf. http://www.doughellmann.com/PyMOTW/tarfile/
    def __init__(self, *fichiers, **infos):
        # {nom_module : [fichierGEO,...], ...}
        self.fichiers = {}
        self.infos = infos
        self.ajouter(*fichiers)

    def ajouter(self, *fichiers):
        for fichier in fichiers:
            self._ajouter_fichier(fichier)

    def _ajouter_fichier(self, fichier):
        if fichier.module in self.fichiers:
            self.fichiers[fichier.module].append(fichier)
        else:
            self.fichiers[fichier.module] = [fichier]


    def ecrire(self, path, compresser = True):
        rep = os.path.split(path)[0]
        if not os.path.exists(rep):
            os.makedirs(rep)
        tar = tarfile.open(path, mode = 'w:' + ('gz' if compresser else ''))

        def _ajouter(titre, data):
            info = tarfile.TarInfo(titre)
            info.size = len(data)
            tar.addfile(info, StringIO(data))

        try:
            fichier_info = FichierGEO(type = 'Session WxGeometrie', module = 'main')
            for key, val in self.infos.items():
                fichier_info.ajouter(key, None, repr(val))
            _ajouter('session.info', fichier_info.data)
            for module, fichiers in self.fichiers.items():
                for i, fichier in enumerate(fichiers):
                    _ajouter(module + str(i) + '.geo', fichier.data)
        finally:
            tar.close()


    def ouvrir(self, path):
        self.fichiers = {}
        self.infos = {}
        tar = tarfile.open(path, mode = 'r')
        try:
            for member_info in tar.getmembers():
                nom = member_info.name
                f = tar.extractfile(member_info)
                data = f.read()
                f.close()
                fichier = FichierGEO().importer(data)
                if nom == 'session.info':
                    for key in fichier.contenu:
                        self.infos[key] = eval_safe(fichier.contenu[key][0])
                else:
                    self._ajouter_fichier(fichier)
        finally:
            tar.close()
        return self

    def __iter__(self):
        def gen_fichiers():
            for fichiers in self.fichiers.values():
                for fichier in fichiers:
                    yield fichier
        return gen_fichiers()
