# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------##
#              WxGeometrie               #
##--------------------------------------##
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


from PyQt4.QtGui import QApplication, QPalette, QColor, QPixmap, QSplashScreen
from PyQt4.QtCore import QLocale, QTranslator, QLibraryInfo, Qt

from ..pylib import path2
import param


class App(QApplication):
    def __init__(self, args=[], **kw):
        QApplication.__init__(self, args)
        locale = QLocale.system().name()
        translator=QTranslator ()
        translator.load("qt_" + locale,
                      QLibraryInfo.location(QLibraryInfo.TranslationsPath))
        self.installTranslator(translator)
        if param.style_Qt:
            self.setStyle(param.style_Qt)

    def boucle(self):
        self.exec_()

    def nom(self, nom=''):
        self.setApplicationName(nom)

    def vers_presse_papier(self, texte):
        self.clipboard().setText(texte)
        return True

    # La fenêtre principale s'enregistre au lancement,
    # afin qu'on puisse facilement la retrouver.
    fenetre_principale = None

app = App()

white_palette = QPalette()
white = QColor(Qt.white)
white_palette.setColor(QPalette.Window, white)
white_palette.setColor(QPalette.AlternateBase, white)

def splash(path):
    u"Create and display the splash screen. Credits: Eli Bendersky (eliben@gmail.com)"
    splash_pix = QPixmap(path2(path))
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    ##splash.setAttribute(Qt.WA_TranslucentBackground)
    # XXX: Doesn't work currently: https://bugreports.qt.nokia.com//browse/QTBUG-12820
    # See also http://developer.qt.nokia.com/wiki/QSplashScreen_replacement_for_semitransparent_images
    splash.show()
    return splash


#app.setStyleSheet("background-color:white")
#palette = app.palette()
#palette.setColor(QPalette.Active, QPalette.Window, QColor('white'))
#palette.setColor(QPalette.Inactive, QPalette.Window, QColor('white'))
