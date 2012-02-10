# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

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


import urllib, webbrowser

from PyQt4.QtCore import QObject, pyqtSignal
from PyQt4.QtGui import QMessageBox

from ..pylib import print_error
from .. import param
from .wxlib import GenericThread



class Gestionnaire_mises_a_jour(QObject):
    url = "http://wxgeo.free.fr/wordpress/version"

    def __init__(self, parent):
        QObject.__init__(self)
        self.parent = parent
        self.derniere_version = None
        self.sent.connect(self.termine)

    sent = pyqtSignal(bool, bool, unicode, unicode)


    def termine(self, success, update, version, msg):
        if success:
            if update:
                self.derniere_version = version
                QMessageBox.information(self.parent, u"Une mise à jour a été trouvée.",
                        u"La version %s de WxGéométrie est sortie.\nVous allez être redirigé vers la page de téléchargement." %version)
                webbrowser.open("http://sourceforge.net/projects/wxgeometrie/files/WxGeometrie/")
            else:
                QMessageBox.information(self.parent, u"Aucune mise à jour trouvée.",
                        u"Aucune mise à jour n'est disponible actuellement.\nConsultez http://wxgeo.free.fr pour plus d'informations.", )
        else:
            print(u'Connexion impossible à ' + self.url + ' : ' + msg)
            QMessageBox.warning(self.parent, u"Connexion impossible", u"Impossible de vérifier si une nouvelle version existe.")


    def verifier_version(self, event = None):
        self.thread = GenericThread(self._verifier_version)
        self.thread.start()


    def _verifier_version(self):
        # /!\ Ne **JAMAIS** utiliser `print()` depuis une autre thread que la principale !
        version = '?'
        success = False
        update = False
        msg = u'Unknown error.'
        try:
            filename, headers = urllib.urlretrieve(self.url)
            f = open(filename)
            version = f.read(60)
            f.close()
            if len(version) > 50 or not version.replace(" ", "").replace(".", "").isalnum():
                raise Exception, "Incorrect file format, unable to find current version."
            success = True
            if version.split(".") > param.version.split('.'):
                update = True
            else:
                update = False
        except Exception as e:
            msg = str(e)
            # XXX: print_error() is not thread safe.

        self.sent.emit(success, update, version, msg)
