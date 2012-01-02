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
from PyQt4.QtGui import QWidget, QVBoxLayout, QLayout

from .barre_outils import BarreOutils
from .menu import RSSMenu
from .console_geolib import ConsoleGeolib
from .wxlib import BusyCursor
from .wxcanvas import QtCanvas
from .app import app
from ..API.sauvegarde import ouvrir_fichierGEO, FichierGEO
from ..API.parametres import sauvegarder_module

import param
from ..pylib import debug, path2, print_error, property2, removeend, no_argument,\
                    eval_safe
from ..pylib.rapport import Rapport
from ..geolib.classeur import Classeur
from ..geolib.feuille import Feuille



class Panel_simple(QWidget):
    u"""Remplace la classe la classe QWidget pour les diff�rents modules.
    Pour les modules ayant besoin des fonctions graphiques evolu�es de WxG�om�trie, mieux vaut utiliser
    la classe Panel_API_graphique, plus evolu�e que celle-ci."""

    feuille_actuelle = None # pas de feuille
    # Indique si des modifications ont eu lieu (et s'il faudra donc sauvegarder la session)
    modifie = False

    def __init__(self, parent, module, menu = True): # style = wx.TAB_TRAVERSAL|wx.WANTS_CHARS
        QWidget.__init__(self, parent)
        self.module = module
#        self.setStyleSheet("background-color:white")
        self.parent = parent
        self.nom = self.__class__.__name__.lower()
        self.canvas = None
        path = path2(param.emplacements['log'] + "/" + self.nom + u"_historique.log")
        self.log = Rapport(path)
        # ._derniere_signature : sert pour les logs (en cas de zoom de souris essentiellement).
        # (cf. geolib/feuille.py pour plus de d�tails.)
        self._derniere_signature = None
        ##if menu:
            ### Cr�ation de la barre de menus associ�e au panel
            ##self.menu = self.module._menu_(self)

    def message(self, texte = ''):
        self.parent.parent.message(texte)

    def changer_titre(self, texte = ''):
        print 'changer_titre...'
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
            self.message(u"Sauvegarde effectu�e.")
        except Exception:
            self.message(u"Echec de la sauvegarde.")
            if param.debug:
                raise


    def _fichiers_ouverts(self):
        return [self.sauvegarder(None)]



    def _ouvrir(self, fgeo):
        u"""Ouverture d'un fichier.

        � surclasser pour chaque module."""


    def _sauvegarder(self, fgeo):
        u"""Sauvegarde dans un fichier.

        � surclasser pour chaque module."""


    def _changement_feuille(self):
        u"""Apr�s tout changement de feuille.

        � surclasser pour chaque module."""


    def param(self, parametre, valeur = no_argument, defaut = False):
        u"""Recherche la valeur d'un param�tre d'abord dans les param�tres du module (param�tres locaux), puis dans ceux de wxg�om�trie.

        Si defaut vaut True, la valeur par d�faut du param�tre est renvoy�e."""
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
            debug(u"Module %s: Param�tre %s introuvable." %(self.__titre__, parametre))


    def sauver_preferences(self, lieu = None):
        if self._param_ is not None:
            try:
                if lieu is None:
                    lieu = path2(param.emplacements['preferences'] + "/" + self.nom + "/parametres.xml")
                fgeo = sauvegarder_module(self._param_, self.nom)
                fgeo.ecrire(lieu)
            except:
                self.message(u"Impossible de sauvegarder les pr�f�rences.")
                print_error()


    def action_effectuee(self, log, signature = None):
        if self.log is not None:
            if signature is not None and signature == self._derniere_signature and self.log:
                self.log[-1] = ('ACTION EFFECTUEE: ' + log)
            else:
                self.log.append('ACTION EFFECTUEE: ' + log)
            self._derniere_signature = signature


    def activer(self, event = None):
        u"Actions � effectuer lorsque l'onglet du module est s�lectionn�. � surclasser."
        pass

    def reinitialiser(self):
        u"""R�initialise le module (ferme les travaux en cours, etc.).

        � surclasser."""
        pass


    @staticmethod
    def vers_presse_papier(texte):
        u"""Copie le texte dans le presse-papier.

        Retourne True si la copie a r�ussi, False sinon."""
        return app.vers_presse_papier(texte)



class Panel_API_graphique(Panel_simple):
    u"""Pour les modules ayant besoin de TOUTE l'API de WxG�om�trie (canvas, historique, gestion des commandes, etc...)
    et pas seulement des biblioth�ques, mieux vaut utiliser cette classe.
    Cela concerne essentiellement les modules qui ont besoin de tracer des objets g�om�triques."""

    def __init__(self, parent, module, BarreOutils = BarreOutils):
        # extra = {'style': wx.WANTS_CHARS} if param.plateforme == "Windows" else {}
        Panel_simple.__init__(self, parent, module, menu=False)

        # IMPORTANT: contruire toujours dans cet ordre.
        self.feuilles = Classeur(self, log = self.log)
        # En particulier, l'initialisation du canvas n�cessite qu'il y ait d�j� une feuille ouverte.
        self.canvas = QtCanvas(self)
        # La construction du menu n�cessite que self.canvas et self.log
        # soient d�finis, ainsi que self.doc_ouverts.
        self.doc_ouverts = RSSMenu(u"Documents ouverts", [], self.charger_feuille, u"Documents ouverts.")
        ##self.menu = self.module._menu_(self)

        self.barre_outils = BarreOutils(self)
        self.console_geolib = ConsoleGeolib(self)
        self.barre_outils.setVisible(self.param("afficher_barre_outils"))
        self.console_geolib.setVisible(self.param("afficher_console_geolib"))

        self.canvas.initialiser()
        self.__sizer_principal = QVBoxLayout()
        self.__sizer_principal.addWidget(self.barre_outils)


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
        u"Retourne la liste des fichiers ouverts (feuilles vierges except�es)."
        return [self.sauvegarder(None, feuille) for feuille in self.feuilles if not feuille.vierge]


    def finaliser(self, contenu=None):
        if contenu is None:
            contenu = self.canvas
        if isinstance(contenu, QLayout):
            self.__sizer_principal.addLayout(contenu, 1)
        else:
            self.__sizer_principal.addWidget(contenu, 1)
        self.__sizer_principal.addWidget(self.console_geolib)
        self.setLayout(self.__sizer_principal)
        ##self.adjustSize()



    def action_effectuee(self, log, signature=None):
        Panel_simple.action_effectuee(self, log, signature=signature)
        self.feuille_actuelle.interprete.commande_executee(signature=signature)

    def _get_actuelle(self):
        return self.feuilles.feuille_actuelle

    def _set_actuelle(self, feuille):
        self.feuilles.feuille_actuelle=feuille
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
##        self.canvas.fenetre = self.param("fenetre") # sert en particulier � orthonormaliser le rep�re au besoin

    def charger_feuille(self, feuille):
        # Utilis� par la classe API.menu.RSSMenu
#        if isinstance(feuille, wx.Event):
#            feuille = feuille.numero
        if not isinstance(feuille, Feuille):
            feuille = self.feuilles[feuille]
        self.feuille_actuelle = feuille

    def fermer_feuille(self, feuille=None):
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
        u"Actualise le titre de la fen�tre, et la liste des feuilles ouvertes dans le menu."
        self.changer_titre()
        self.doc_ouverts.update(self.feuilles.noms)
        # �vite les conflits lors de l'initialisation:
        if getattr(self, "barre_outils", None) is not None:
            self.barre_outils.rafraichir()

    def update(self):
        u"Fait les actualisations n�cessaires quand la feuille courante change."
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

        if fgeo.contenu.has_key("Meta"): # obligatoirement APRES la creation du document, donc apr�s "Figure"
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
            # On va maintenant rajouter des lignes "pause()" au d�but de chaque boucle "for" ou "while".
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
##            # se produit apr�s avoir r�duit la fen�tre, en dessous d'une certaine taille.
##            print_error(u"Warning: Fen�trage incorrect.")
##            # Il semble que WxPython mette du temps � determiner la nouvelle taille
##            # de la fen�tre, et GetSize() renvoit alors temporairement des valeurs nulles.
##        except:
##            print_error()
##            self.message(u"Erreur d'affichage !")


    def _affiche(self):
        u"M�thode � surclasser."


    def reinitialiser(self):
        u"""R�initialise le module (ferme les travaux en cours, etc.).

        � surclasser dans la majorit� des cas."""
        self.fermer_feuilles()


    def sauver_preferences(self, lieu = None):
        if self._param_ is not None:
            for parametre in self.canvas.parametres: # Permet de sauvegarder les param�tres du moteur d'affichage pour chaque module de mani�re ind�pendante.
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
                self.barre_outils.setVisible(self.param("afficher_barre_outils"))
                self.adjustSize()
        return self.param("afficher_barre_outils")

    def afficher_console_geolib(self, afficher = None):
        u"Afficher ou non la ligne de commande de la feuille."
        if afficher is not None:
            if isinstance(afficher, bool):
                self._param_.afficher_console_geolib = afficher
            else:
                self._param_.afficher_console_geolib = not self.param("afficher_console_geolib")
            with self.canvas.geler_affichage(actualiser = True):
                self.console_geolib.setVisible(self.param("afficher_console_geolib"))
                if self.param("afficher_console_geolib"):
                    self.console_geolib.ligne_commande.setFocus()
                self.adjustSize()
        return self.param("afficher_console_geolib")


    def activer(self, event = None):
        u"Actions � effectuer lorsque l'onglet du module est s�lectionn�. � surclasser."
        if self.param("afficher_console_geolib"):
        #if gettattr(self._param_, "afficher_console_geolib", False):
            self.console_geolib.setFocus()
