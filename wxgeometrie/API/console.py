# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

##########################################
#            CONSOLE
##########################################
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

# NOTES :
# Un fichier .geo est essentiellement un fichier python (structure par du XML).
# C'est potentiellement dangereux (en particulier sous Windows), car certains modules python (comme os, sys, ...), et certaines fonctions (write...) peuvent endommager le systeme d'exploitation.
# Une bonne partie du travail de ce module consiste donc a securiser l'environnement d'execution.
# Comme je suis loin d'etre un expert, il est possible (voire probable) que des failles subsistent neanmoins.
# Merci de m'en informer.



#  Il faudra donner a l'utilisateur la possibilite d'autoriser la macro ponctuellement, ou meme de changer le parametre de securite

from .. import param



class Console:
    def __init__(self, parent):
        self.parent = parent
        self.locals = {'main': self.parent,
                  'onglets': self.parent.onglets,
                  'param': param}

    def executer(self, commande):
        u"La commande est exécutée dans l'espace de nom du panel."
        commande = commande.strip()

        # & est un raccourci pour print
        if commande[0] == '&':
            commande = 'print(' + commande[1:] + ')'

        # Les racourcis suivants sont utilisables :
        # Panel actuel :
        commande = commande.replace(u"!p.", u"panel.")
        # Canvas actuel :
        commande = commande.replace(u"!c.", u"canvas.")
        # Feuille utilisée actuellement :
        commande = commande.replace(u"!f.", u"feuille.")
        # Objets de la feuille :
        commande = commande.replace(u"!o.", u"objets.")
        commande = commande.replace(u"!g.", u"moteur_graphique.")
        # Fenêtre principale :
        commande = commande.replace(u"!m.", u"main.")


#        if param.debug:
#            self.parent.onglets.onglet_actuel.action_effectuee(u"REQUETE CONSOLE:" + commande)
#            print u"REQUETE CONSOLE:" + commande
        print(u"REQUETE CONSOLE [" + self.parent.onglets.onglet_actuel.__titre__ + "]:\n>>> " + commande)

        self.locals.update({'panel': self.parent.onglets.onglet_actuel,
                  'canvas': self.parent.onglets.onglet_actuel.canvas,
                  'feuille': self.parent.onglets.onglet_actuel.feuille_actuelle,
                  })
        for nom in param.modules:
            if param.modules_actifs[nom]:
                self.locals[nom] = getattr(self.parent.onglets, nom)
        if self.parent.onglets.onglet_actuel.canvas is not None:
            self.locals['objets'] = self.parent.onglets.onglet_actuel.feuille_actuelle.objets
            self.locals['moteur_graphique'] = self.parent.onglets.onglet_actuel.canvas.graph
        exec(commande, self.parent.__dict__, self.locals)
