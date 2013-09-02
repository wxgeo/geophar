# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------##
#              WxGeometrie               #
##--------------------------------------##
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


from PyQt4.QtGui import QApplication, QPalette, QColor, QPixmap, QSplashScreen, QIcon
from PyQt4.QtCore import QLocale, QTranslator, QLibraryInfo, Qt, pyqtSignal


class App(QApplication):

    # La fenètre principale s'enregistre au lancement,
    # afin qu'on puisse facilement la retrouver.
    fenetre_principale = None

    _print_signal = pyqtSignal(basestring)

    def __init__(self, args=[], **kw):
        QApplication.__init__(self, args)
        locale = QLocale.system().name()
        translator=QTranslator ()
        translator.load("qt_" + locale,
                      QLibraryInfo.location(QLibraryInfo.TranslationsPath))
        self.installTranslator(translator)
        self._print_signal.connect(self._print)
        # Pour Mac OS X
        self.setAttribute(Qt.AA_DontUseNativeMenuBar)

    def boucle(self):
        self.exec_()

    def nom(self, nom=''):
        self.setApplicationName(nom)

    def icone(self, path):
        from ..pylib.fonctions import path2
        self.setWindowIcon(QIcon(path2(path)))

    def vers_presse_papier(self, texte):
        self.clipboard().setText(texte)
        return True

    def safe_print(self, texte):
        u"""Thread-safe print().

        En dehors de la thread principale, il faut impérativement utiliser
        cette méthode au lieu de `print()` (notamment parce que print()
        peut provoquer des accès concurrents au fichier de log en écriture).
        """
        self._print_signal.emit(texte)

    def safe_print_error(self):
        u"""Thread-safe print_error().

        En dehors de la thread principale, il faut impérativement utiliser
        cette méthode au lieu de `print_error()`.
        """
        from ..pylib.fonctions import extract_error
        self._print_signal.emit(extract_error())

    def _print(self, texte):
        print(texte)


app = App()

white_palette = QPalette()
white = QColor(Qt.white)
white_palette.setColor(QPalette.Window, white)
white_palette.setColor(QPalette.AlternateBase, white)

def splash(path):
    u"Create and display the splash screen. Credits: Eli Bendersky (eliben@gmail.com)"
    splash_pix = QPixmap(path)
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
