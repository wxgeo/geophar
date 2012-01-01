# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

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
from ..pylib import uu, print_error
from .. import param

class Rapport(list):
    def __init__(self, fichier_log = None, frequence_archivage = 100):
        list.__init__(self)
        self.fichier_log = fichier_log
        self.frequence_archivage = frequence_archivage
        try:
            # Créer un fichier vierge.
            f = None
            f = open(self.fichier_log, 'w')
            f.write(time.strftime("%d/%m/%Y - %H:%M:%S") + '\n')
            f.close()
        except:
            # Impossible de créer le fichier (problème de permissions, etc.)
            self.fichier_log = None
            print_error()
        finally:
            if f is not None:
                f.close()


    def append(self, valeur):
        if param.debug:
            print ''
            print valeur
            print ''
        list.append(self, valeur)
        if len(self) > self.frequence_archivage:
            self.archiver()

    def extend(self, liste):
        list.extend(self, liste)
        if len(self) > self.frequence_archivage:
            self.archiver()

    def _contenu(self):
        u"Récupère le contenu récent (c-à-d. non archivé)."
        return '\n'.join(self) + '\n'

    def archiver(self):
        u"Copie les derniers enregistrements vers le fichier log."
        if self.fichier_log is not None:
            with open(self.fichier_log, 'a') as f:
                f.write(uu(self._contenu()).encode('utf8'))
                self[:] = []

    def contenu(self):
        u"Récupère le contenu complet, y compris ce qui a déjà été archivé."
        if self.fichier_log is None:
            return self._contenu()
        else:
            self.archiver()
            with open(self.fichier_log, 'r') as f:
                return uu(f.read())
