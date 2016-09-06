# -*- coding: utf-8 -*-

#    WxGeometrie
#    Dynamic geometry, graph plotter, and more for french mathematic teachers.
#    Copyright (C) 2005-2013  Nicolas Pourcelot
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


import webbrowser
from urllib.request import urlopen

from PyQt4.QtCore import QObject, pyqtSignal
from PyQt4.QtGui import QMessageBox

from ..pylib import print_error
from .. import param
from .qtlib import GenericThread
from .app import app


class Gestionnaire_mises_a_jour(QObject):
    url_version = "http://wxgeo.free.fr/wordpress/version_geophar"
    url_telechargement = "http://sourceforge.net/projects/geophar/files/latest/download"

    def __init__(self, parent):
        QObject.__init__(self)
        self.parent = parent
        self.derniere_version = None
        self.sent.connect(self.termine)

    sent = pyqtSignal(bool, bool, str, str)


    def termine(self, success, update, version, msg):
        if success:
            if update:
                self.derniere_version = version
                QMessageBox.information(self.parent, "Une mise à jour a été trouvée.",
                        ("La version %s de %s est sortie.\n"
                        "Vous allez être redirigé vers la page de téléchargement.")
                        % (version, param.NOMPROG))
                webbrowser.open(self.url_telechargement)
            else:
                QMessageBox.information(self.parent, "Aucune mise à jour trouvée.",
                        "Aucune mise à jour n'est disponible actuellement.<br>"
                        "Consultez <a href='http://wxgeo.free.fr/wordpress/'>"
                        "http://wxgeo.free.fr</a> pour plus d'informations.")
        else:
            print('Connexion impossible à ' + self.url_version + ' : ' + msg)
            QMessageBox.warning(self.parent, "Connexion impossible",
                    "Impossible de vérifier si une nouvelle version existe.<br>"
                    "Consultez <a href='http://wxgeo.free.fr/wordpress/'>"
                    "http://wxgeo.free.fr</a> pour plus d'informations.")


    def verifier_version(self, event=None):
        self.thread = GenericThread(self._verifier_version)
        self.thread.start()


    def _verifier_version(self):
        # /!\ Ne **JAMAIS** utiliser `print()` depuis une autre thread que la principale !
        # Utiliser `app.safe_print()` à la place.
        version = '?'
        success = False
        update = False
        msg = 'Unknown error.'
        try:
            if param.debug:
                app.safe_print("Checking %s..." % self.url_version)
            with urlopen(self.url_version) as f:
                version = f.read(60).decode('utf8')
            if len(version) > 50 or not version.replace(" ", "").replace(".", "").isalnum():
                raise Exception("Incorrect file format, unable to find current version.")
            success = True
            if version.split(".") > param.version.split('.'):
                update = True
            else:
                update = False
        except Exception as e:
            # /!\ print_error() is not thread safe.
            app.safe_print_error()
            msg = str(e)

        self.sent.emit(success, update, version, msg)
