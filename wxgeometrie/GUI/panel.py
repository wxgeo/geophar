# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

##--------------------------------------#######
#                   Panel                     #
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

import os, time, thread
import wx

from .barre_outils import BarreOutils
from .menu import RSSMenu
from .console_geolib import ConsoleGeolib
from .wxlib import BusyCursor
from .wxcanvas import WxCanvas
from ..API.sauvegarde import ouvrir_fichierGEO, FichierGEO
from ..API.parametres import sauvegarder_module

from .. import param
from ..pylib import debug, path2, print_error, property2, removeend, no_argument,\
                    eval_safe
from ..pylib.rapport import Rapport
from ..geolib.classeur import Classeur
from ..geolib.feuille import Feuille

#-----------------------
#       Panels
#-----------------------



#class Canvas_vide:
#    """Canvas bidon, qui sert pour l'initialisation des classes menu."""
#    def __getattr__(self, nom):
#        return None
#
#    def __nonzero__(self):
#        return False
#
#    def __repr__(self):
#        return "<Canvas Vide>"
#
#    def __str__(self):
#        return "<Canvas Vide>"





class Panel_simple(wx.Panel):
    u"""Remplace la classe la classe wx.Panel pour les différents modules.
    Pour les modules ayant besoin des fonctions graphiques evoluées de WxGéométrie, mieux vaut utiliser
    la classe Panel_API_graphique, plus evoluée que celle-ci."""

    feuille_actuelle = None # pas de feuille
    # Indique si des modifications ont eu lieu (et s'il faudra donc sauvegarder la session)
    modifie = False

    def __init__(self, parent, module, couleur = None, menu = True, style = wx.TAB_TRAVERSAL|wx.WANTS_CHARS):
        wx.Panel.__init__(self, parent, -1, style = style)

        self.module = module
        # wx.NamedColor ne peut pas être appelé avant que wx.App existe.
        couleur = couleur if couleur else wx.NamedColor(u"WHITE")
        self.SetBackgroundColour(couleur)
        self.parent = parent
        self.nom = self.__class__.__name__.lower()
        self.canvas = None
        path = path2(param.emplacements['log'] + "/" + self.nom + u"_historique.log")
        self.log = Rapport(path)
        # ._derniere_signature : sert pour les logs (en cas de zoom de souris essentiellement).
        # (cf. geolib/feuille.py pour plus de détails.)
        self._derniere_signature = None
        if menu:
            # Création de la barre de menus associée au panel
            self.menu = self.module._menu_(self)

    def message(self, texte = ''):
        self.parent.parent.barre.SetStatusText(texte, 0)

    def changer_titre(self, texte = ''):
        self.parent.parent.titre(texte)


    def ouvrir(self, fichier):
        u"""Ouvre un  un fichier .geo.

        'fichier' est soit l'adresse d'un fichier .geo, soit une instance de FichierGEO.
        """
        with BusyCursor():
            if not isinstance(fichier, FichierGEO):
                fichier, message = ouvrir_fichierGEO(fichier)
                self.message(message)
            self._ouvrir(fichier) # instance de FichierGEO


    def sauvegarder(self, nom_fichier = 'sauvegarde', **kw):
        if nom_fichier:
            if nom_fichier.endswith(".geoz"):
                nom_fichier = removeend(nom_fichier.strip(), ".geo", ".geoz") + ".geoz"     # le nom par defaut sera ainsi [nom_de_la_feuille].geo"
            else:
                nom_fichier = removeend(nom_fichier.strip(), ".geo", ".geoz") + ".geo"     # le nom par defaut sera ainsi [nom_de_la_feuille].geo"
        try:
            fgeo = FichierGEO(module = self.nom)
            self._sauvegarder(fgeo, **kw)
            if nom_fichier is None:
                return fgeo
            fgeo.ecrire(nom_fichier, zip = nom_fichier.endswith(".geoz"))
            self.message(u"Sauvegarde effectuée.")
        except Exception:
            self.message(u"Echec de la sauvegarde.")
            if param.debug: raise


    def _fichiers_ouverts(self):
        return [self.sauvegarder(None)]



    def _ouvrir(self, fgeo):
        u"""Ouverture d'un fichier.

        À surclasser pour chaque module."""


    def _sauvegarder(self, fgeo):
        u"""Sauvegarde dans un fichier.

        À surclasser pour chaque module."""


    def _changement_feuille(self):
        u"""Après tout changement de feuille.

        À surclasser pour chaque module."""


    def param(self, parametre, valeur = no_argument, defaut = False):
        u"""Recherche la valeur d'un paramètre d'abord dans les paramètres du module (paramètres locaux), puis dans ceux de wxgéométrie.

        Si defaut vaut True, la valeur par défaut du paramètre est renvoyée."""
        if valeur is not no_argument:
            setattr(self._param_, parametre, valeur)
        if self._param_ is not None and hasattr(self._param_, parametre):
            if defaut:
                if self._param_._parametres_par_defaut.has_key(parametre):
                    return self._param_._parametres_par_defaut[parametre]
                elif param._parametres_par_defaut.has_key(parametre):
                    return param._parametres_par_defaut[parametre]
            return getattr(self._param_, parametre)

        elif hasattr(param, parametre):
            if defaut and param._parametres_par_defaut.has_key(parametre):
                return param._parametres_par_defaut[parametre]
            return getattr(param, parametre)
        else:
            debug(u"Module %s: Paramètre %s introuvable." %(self.__titre__, parametre))


    def sauver_preferences(self, lieu = None):
        if self._param_ is not None:
            try:
                if lieu is None:
                    lieu = path2(param.emplacements['preferences'] + "/" + self.nom + "/parametres.xml")
                fgeo = sauvegarder_module(self._param_, self.nom)
                fgeo.ecrire(lieu)
            except:
                self.message(u"Impossible de sauvegarder les préférences.")
                print_error()


    def action_effectuee(self, log, signature = None):
        if self.log is not None:
            if signature is not None and signature == self._derniere_signature and self.log:
                self.log[-1] = ('ACTION EFFECTUEE: ' + log)
            else:
                self.log.append('ACTION EFFECTUEE: ' + log)
            self._derniere_signature = signature


    def activer(self, event = None):
        u"Actions à effectuer lorsque l'onglet du module est sélectionné. À surclasser."
        pass

    def reinitialiser(self):
        u"""Réinitialise le module (ferme les travaux en cours, etc.).

        À surclasser."""
        pass


    @staticmethod
    def vers_presse_papier(texte):
        u"""Copie le texte dans le presse-papier.

        Retourne True si la copie a réussi, False sinon."""
        clipBoard=wx.TheClipboard
        if clipBoard.Open():
            clipBoard.AddData(wx.TextDataObject(texte))
            clipBoard.Close()
            return True
        return False



class Panel_API_graphique(Panel_simple):
    u"""Pour les modules ayant besoin de TOUTE l'API de WxGéométrie (canvas, historique, gestion des commandes, etc...)
    et pas seulement des bibliothèques, mieux vaut utiliser cette classe.
    Cela concerne essentiellement les modules qui ont besoin de tracer des objets géométriques."""

    def __init__(self, parent, module, couleur = None, BarreOutils = BarreOutils):
        # wx.NamedColor ne peut pas être appelé avant que wx.App existe.
        couleur = couleur if couleur else wx.NamedColor(u"WHITE")
        extra = {'style': wx.WANTS_CHARS} if param.plateforme == "Windows" else {}
        Panel_simple.__init__(self, parent, module, couleur = couleur, menu = False, **extra)

        # IMPORTANT: contruire toujours dans cet ordre.
        self.feuilles = Classeur(self, log = self.log)
        # En particulier, l'initialisation du canvas nécessite qu'il y ait déjà une feuille ouverte.
        self.canvas = WxCanvas(self)
        # La construction du menu nécessite que self.canvas et self.log
        # soient définis, ainsi que self.doc_ouverts.
        self.doc_ouverts = RSSMenu(parent, u"Documents ouverts", [], self.charger_feuille, u"Documents ouverts.")
        self.menu = self.module._menu_(self)

        self.barre_outils = BarreOutils(self, couleur = couleur)
        self.console_geolib = ConsoleGeolib(self, couleur = couleur)
        self.barre_outils.Show(self.param("afficher_barre_outils"))
        self.console_geolib.Show(self.param("afficher_console_geolib"))

##        self.creer_feuille()
        self.canvas.initialiser()
        self.__sizer_principal = wx.BoxSizer(wx.VERTICAL)
        self.__sizer_principal.Add(self.barre_outils, 0, wx.ALL, 5)


    @property2
    def modifie(self, val = None):
        if val is None:
            return self.feuilles.modifie
        self.feuilles.modifie = val

    def changer_titre(self, texte = None):
        texte = self.feuille_actuelle.nom_complet if (texte is None) else texte
        self.parent.parent.titre(texte)

    def ouvrir(self, fichier):
        Panel_simple.ouvrir(self, fichier)
        self.feuille_actuelle.modifiee = False
        if isinstance(fichier, FichierGEO):
            self.feuille_actuelle.sauvegarde["nom"] = fichier.nom
            self.feuille_actuelle.sauvegarde["repertoire"] = fichier.repertoire
        else:
            rep, fich = os.path.split(fichier)
            self.feuille_actuelle.sauvegarde["repertoire"] = rep
            self.feuille_actuelle.sauvegarde["nom"] = removeend(fich, ".geo", ".geoz") # nom sans l'extension
        self.rafraichir_titre()




    def sauvegarder(self, nom_fichier = '', feuille = None):
        if feuille is None:
            feuille = self.feuille_actuelle
        if nom_fichier == '':
            if feuille.sauvegarde["nom"]:
                nom_fichier = os.path.join(feuille.sauvegarde["repertoire"], feuille.sauvegarde["nom"])
            else:
                nom_fichier = "sauvegarde"
        if nom_fichier is None:
            return Panel_simple.sauvegarder(self, nom_fichier, feuille = feuille)
        Panel_simple.sauvegarder(self, nom_fichier, feuille = feuille)
        feuille.modifiee = False
        rep, fich = os.path.split(nom_fichier)
        feuille.sauvegarde["repertoire"] = rep
        feuille.sauvegarde["nom"] = removeend(fich, ".geo") # nom sans l'extension
        self.rafraichir_titre()


    def _fichiers_ouverts(self):
        u"Retourne la liste des fichiers ouverts (feuilles vierges exceptées)."
        return [self.sauvegarder(None, feuille) for feuille in self.feuilles if not feuille.vierge]


    def finaliser(self, contenu = None):
        if contenu is None:
            contenu = self.canvas
        self.__sizer_principal.Add(contenu, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.__sizer_principal.Add(self.console_geolib, 0, wx.ALL, 5)
        self.SetSizer(self.__sizer_principal)
        self.Fit()



    def action_effectuee(self, log, signature = None):
        Panel_simple.action_effectuee(self, log, signature = signature)
        self.feuille_actuelle.interprete.commande_executee(signature = signature)

    def _get_actuelle(self):
        return self.feuilles.feuille_actuelle

    def _set_actuelle(self, feuille):
        self.feuilles.feuille_actuelle = feuille
        self.update()

    def _del_actuelle(self):
        del self.feuilles.feuille_actuelle
        self.update()

    feuille_actuelle = property(_get_actuelle, _set_actuelle, _del_actuelle)



    def creer_feuille(self, nom = None):
        if not (self.feuille_actuelle.vierge and nom is None):
            self.feuilles.nouvelle_feuille(nom)
            self.update()
        return self.feuille_actuelle
##        self.canvas.fenetre = self.param("fenetre") # sert en particulier à orthonormaliser le repère au besoin

    def charger_feuille(self, feuille):
        # Utilisé par la classe API.menu.RSSMenu
        if isinstance(feuille, wx.Event):
            feuille = feuille.numero
        if not isinstance(feuille, Feuille):
            feuille = self.feuilles[feuille]
        self.feuille_actuelle = feuille

    def fermer_feuille(self, feuille = None):
        if feuille is None:
            del self.feuille_actuelle
        else:
            if not isinstance(feuille, Feuille):
                feuille = self.feuilles[feuille]
            self.feuilles.remove(feuille)
            self.update()

    def fermer_feuilles(self):
        u"Ferme toute les feuilles."
        self.feuilles.vider()
        self.update()

    def rafraichir_titre(self):
        u"Actualise le titre de la fenêtre, et la liste des feuilles ouvertes dans le menu."
        self.changer_titre()
        self.doc_ouverts.update(self.feuilles.noms)
        # Évite les conflits lors de l'initialisation:
        if getattr(self, "barre_outils", None) is not None:
            self.barre_outils.rafraichir()

    def update(self):
        u"Fait les actualisations nécessaires quand la feuille courante change."
        self.rafraichir_titre()
##        self.canvas.rafraichir_axes = True
        self.affiche()




    def _sauvegarder(self, fgeo, feuille = None):
        if feuille is None:
            feuille = self.feuille_actuelle

        fgeo.contenu["Figure"] = [feuille.sauvegarder()]

        fgeo.contenu["Affichage"] = [{}]
        for parametre in self.canvas.parametres:
            fgeo.contenu["Affichage"][0][parametre] = [repr(getattr(self.canvas, parametre))]

        fgeo.contenu["Meta"] = [{}]
        feuille.infos(modification = time.strftime("%d/%m/%Y - %H:%M:%S",time.localtime()))
        for nom, info in feuille.infos().items():
            fgeo.contenu["Meta"][0][nom] = [info]
        #fgeo.contenu["Meta"][0]["modification"] = [time.strftime("%d/%m/%Y - %H:%M:%S",time.localtime())]




    def _ouvrir(self, fgeo):
        if fgeo.contenu.has_key("Affichage"):
            if fgeo.contenu["Affichage"]:
                parametres = fgeo.contenu["Affichage"][0]
                for parametre in parametres.keys():
                    setattr(self.canvas, parametre, eval_safe(parametres[parametre][0]))

        if fgeo.contenu.has_key("Figure"):
            for figure in fgeo.contenu["Figure"]:
                feuille = self.creer_feuille()
                feuille.charger(figure, mode_tolerant = True)

        if fgeo.contenu.has_key("Meta"): # obligatoirement APRES la creation du document, donc après "Figure"
            infos = fgeo.contenu["Meta"][0]
            for key, value in infos.items():
                self.feuille_actuelle.infos(key = value[0])


        for macro in fgeo.contenu.get("Macro", []):
            code = macro["code"][0]
            autostart = (macro["autostart"][0].strip().capitalize() == "True")
            mode_avance = (macro["mode_avance"][0].strip().capitalize() == "True")
            print "mode avance", mode_avance
            nom = macro["nom"][0]
            self.feuille_actuelle.macros[nom] = {"code": code, "autostart": autostart, "mode_avance": mode_avance}
            if autostart:
                self.executer_macro(nom = nom, **self.feuille_actuelle.macros[nom])


    def executer_macro(self, **kw):
        code = kw.get("code", "")
        if kw.get("mode_avance", False):
            code = ":" + code
        else:
            # On va maintenant rajouter des lignes "pause()" au début de chaque boucle "for" ou "while".
            # l'instruction pause() permet d'interrompre la boucle au besoin.
            lignes = code.splitlines()
            rajouter_pause = False
            for i in xrange(len(lignes)):
                if rajouter_pause:
                    lignes[i] = (len(lignes[i]) - len(lignes[i].lstrip()))*" " + "pause()\n" + lignes[i] # on insere "pause()" avant la ligne l, en respectant son indentation.
                    rajouter_pause = False
                if (lignes[i].startswith("for") or lignes[i].startswith("while")) and lignes[i].endswith(":"):
                    rajouter_pause = True
            code = "\n".join(lignes)

        if param.multi_threading:
            thread.start_new_thread(self.canvas.executer, (code + "\nwx.Yield()",))
        else:
            self.canvas.executer(code)



    def exporter(self, path):
        self.canvas.exporter(path)
        self.feuille_actuelle.sauvegarde["export"] = path


    def annuler(self, event = None):
        self.feuille_actuelle.historique.annuler()
        self.rafraichir_titre()


    def retablir(self, event = None):
        self.feuille_actuelle.historique.refaire()
        self.rafraichir_titre()

    def affiche(self, event = None):
        self.canvas.rafraichir_affichage(rafraichir_axes = True)
##        try:
##            self.canvas.actualiser()
##        except ZeroDivisionError:
##            # se produit après avoir réduit la fenêtre, en dessous d'une certaine taille.
##            print_error(u"Warning: Fenêtrage incorrect.")
##            # Il semble que WxPython mette du temps à determiner la nouvelle taille
##            # de la fenêtre, et GetSize() renvoit alors temporairement des valeurs nulles.
##        except:
##            print_error()
##            self.message(u"Erreur d'affichage !")


    def _affiche(self):
        u"Méthode à surclasser."


    def reinitialiser(self):
        u"""Réinitialise le module (ferme les travaux en cours, etc.).

        À surclasser dans la majorité des cas."""
        self.fermer_feuilles()


    def sauver_preferences(self, lieu = None):
        if self._param_ is not None:
            for parametre in self.canvas.parametres: # Permet de sauvegarder les paramètres du moteur d'affichage pour chaque module de manière indépendante.
                setattr(self._param_, parametre, getattr(self.canvas, parametre))
            Panel_simple.sauver_preferences(self, lieu)


    def afficher_barre_outils(self, afficher = None):
        u"Afficher ou non la barre d'outils."
        if afficher is not None:
            if isinstance(afficher, bool):
                self._param_.afficher_barre_outils = afficher
            else:
                self._param_.afficher_barre_outils = not self.param("afficher_barre_outils")
            with self.canvas.geler_affichage(actualiser = True):
                self.barre_outils.Show(self.param("afficher_barre_outils"))
                self.Fit()
        return self.param("afficher_barre_outils")

    def afficher_console_geolib(self, afficher = None):
        u"Afficher ou non la ligne de commande de la feuille."
        if afficher is not None:
            if isinstance(afficher, bool):
                self._param_.afficher_console_geolib = afficher
            else:
                self._param_.afficher_console_geolib = not self.param("afficher_console_geolib")
            with self.canvas.geler_affichage(actualiser = True):
                self.console_geolib.Show(self.param("afficher_console_geolib"))
                if self.param("afficher_console_geolib"):
                    self.console_geolib.ligne_commande.SetFocus()
                self.Fit()
        return self.param("afficher_console_geolib")


    def activer(self, event = None):
        u"Actions à effectuer lorsque l'onglet du module est sélectionné. À surclasser."
        if self.param("afficher_console_geolib"):
        #if gettattr(self._param_, "afficher_console_geolib", False):
            self.console_geolib.SetFocus()
