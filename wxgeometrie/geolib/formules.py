# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                  Formule                    #
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

import re
from weakref import ref

from .routines import nice_display

from ..pylib import uu
from .. import param

class Formule(object):

    # Le caractère d'erreur doit être accepté par le parser de matplotlib en mode normal *ET* en mode math.
    _caractere_erreur = "<.>"

    def _get_feuille(self):
        return self.__feuille

    def _set_feuille(self, value):
        self.__feuille = value
        liste = self._contenu[:]
        for i in xrange(1, len(liste), 2):
            self._contenu[i].__feuille__ = value

    __feuille__ = property(_get_feuille, _set_feuille)

    def __init__(self, parent, chaine = ""):
        from .variables import Variable
        if isinstance(chaine, Formule):
            chaine = eval(repr(chaine))
##        print "Initialisation formule:", chaine, type(chaine)
        self._parent = ref(parent) # self._parent est une fonction qui renvoit parent si il existe encore. Cela permet de ne pas le maintenir en vie artificiellement (pas de référence circulaire).
        #~ self._cache_repr = chaine
        #~ self._cache_str = "<?>".join()
        if "{" not in chaine:
            liste = ["", "{" + chaine + "}", ""]
        else:
            liste = re.split("([{][^}]+[}])", chaine)
        for i in xrange(1, len(liste), 2):
            cache = liste[i][1:-1] # "{A.x}" -> "A.x"
            var = liste[i] = Variable(cache)
            var._cache_formule = cache
##            # on va maintenant redéfinir la méthode affiche de toutes les variables de la formule : au lieu d'être inactive, la méthode affiche va actualiser l'affichage de l'objet contenant la formule.
##            def affiche(self, actualiser = False, formule = self):
##                formule.parent.creer_figure()
##            var.affiche = new.instancemethod(affiche, var, var.__class__)
        self._contenu = liste

        # il faut faire un système de cache pour chaque variable :
        # - si la variable est calculable, on renvoie la valeur de la variable (et on met à jour son cache)
        # - sinon, on renvoie le cache s'il s'agit de repr, et <?> s'il s'agit de str.

        self.__feuille__ = self.parent.__feuille__


    @property
    def parent(self):
        return self._parent()

    def supprimer(self):
        for i in xrange(1, len(self._contenu), 2):
            self._contenu[i].supprimer()


    def __repr__(self):
        liste = self._contenu[:]
        for i in xrange(1, len(liste), 2):
            if liste[i].val is not None:
                liste[i]._cache_formule = str(liste[i])
            liste[i] = "{" + liste[i]._cache_formule + "}"
        return repr(uu("".join(liste)))
        #~ return uu("".join(liste))


    def __unicode__(self):
        liste = self._contenu[:]
        for i in xrange(1, len(liste), 2):
            if liste[i].val is None:
                s = self._caractere_erreur
            else:
                s = nice_display(liste[i])
            #~ if s == "None":
                #~ s = "<?>"
            liste[i] = s
        return uu("".join(liste))


    def __str__(self):
        return unicode(self).encode(param.encodage)
