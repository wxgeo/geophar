# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

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

from PyQt4.QtGui import QDialog, QDialogButtonBox

from .reperage_ui import Ui_DialogReperage
from .calibrage_ui import Ui_DialogCalibrage

from .. import param




class DialogCalibrage(QDialog, Ui_DialogCalibrage):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        # Set up the user interface from Designer.
        self.setupUi(self)
        self.parent = parent

    def accept(self):
        longueur = float(self.longueur.text().replace(param.separateur_decimal, '.'))
        # La barre étalon mesure 300 pixels.
        # 1 inch = 2,54 cm
        self.parent.resolution.setText(str(2.54*300/longueur).replace('.', param.separateur_decimal))
        self.close()



class DialogReperage(QDialog, Ui_DialogReperage):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        # Set up the user interface from Designer.
        self.setupUi(self)
        self.canvas = canvas = parent
        gradu = canvas.gradu
        repere = canvas.repere
        # Dimensions en pixels.
        width, height = canvas.dimensions
        # Fenêtre, en coordonnées cette fois.
        xmin, xmax, ymin, ymax = canvas.fenetre
        # Résolution de l'écran (pixels per inch)
        dpi = canvas.dpi_ecran
        # Mesure en pixels d'une unité
        pixels_per_unit_x = width/(xmax - xmin)
        pixels_per_unit_y = height/(ymax - ymin)
        # Mesure en cm d'une unité
        # 1 inch = 2.54 cm
        cm_per_unit_x = 2.54*pixels_per_unit_x/dpi
        cm_per_unit_y = 2.54*pixels_per_unit_y/dpi

        # Valeurs initiales des champs de texte.
        self.remplir_champs(repere_O=repere[0],
                            repere_I=repere[1],
                            repere_J=repere[2],
                            gradu_x=gradu[0],
                            gradu_y=gradu[1],
                            echelle_x=cm_per_unit_x,
                            echelle_y=cm_per_unit_y,
                            resolution=dpi,
                            )

        self.rapport.setChecked(canvas.ratio is not None)

        self.boutons.button(QDialogButtonBox.Reset).clicked.connect(self.restaurer)
        self.boutons.button(QDialogButtonBox.Apply).clicked.connect(self.appliquer)
        self.calibrage.clicked.connect(self.calibrer)


    def remplir_champs(self, **champs):
        for nom, valeur in champs.iteritems():
            string = (str(valeur) if not isinstance(valeur, basestring) else valeur)
            if isinstance(valeur, float):
                if string.endswith('.0'):
                    string = string[:-2]
                string = string.replace('.', param.separateur_decimal)
            getattr(self, nom).setText(string)


    def accept(self):
        self.appliquer()
        self.close()

    def appliquer(self):
        canvas = self.canvas

        def str2num(string):
            string = string.replace(param.separateur_decimal, '.').strip()
            if string.endswith('.0'):
                string = string[:-2]
            return (float(string) if '.' in string else int(string))

        repere = (self.repere_O.text().strip(),
                  self.repere_I.text().strip(),
                  self.repere_J.text().strip(),
                  )
        gradu = (str2num(self.gradu_x.text()),
                 str2num(self.gradu_y.text()),
                 )

        canvas.dpi_ecran = dpi = str2num(self.resolution.text())

        # Nouvelle fenêtre d'affichage.
        # À partir de l'échelle en abscisse et en ordonnée, on détermine
        # quelles dimensions (en coordonnées) doit avoir la fenêtre d'affichage,
        # et donc les coefficients d'agrandissement en abscisse et en ordonnée.
        # Reste à choisir le point fixe de la transformation, par exemple le centre
        # de la fenêtre précédente.

        # Centre de la fenêtre précédente.
        xmin, xmax, ymin, ymax = canvas.fenetre
        x_centre = (xmin + xmax)/2
        y_centre = (ymin + ymax)/2

        cm_per_unit_x = str2num(self.echelle_x.text())
        cm_per_unit_y = str2num(self.echelle_y.text())
        dpcm = dpi/2.54
        pixels_per_unit_x = cm_per_unit_x*dpcm
        pixels_per_unit_y = cm_per_unit_y*dpcm
        # Dimensions en pixels
        width, height = canvas.dimensions
        # Dimensions en unités (coordonnées) divisées par 2.
        demi_largeur = width/(2*pixels_per_unit_x)
        demi_hauteur = height/(2*pixels_per_unit_y)
        fenetre = (x_centre - demi_largeur,
                   x_centre + demi_largeur,
                   y_centre - demi_hauteur,
                   y_centre + demi_hauteur,
                   )

        ratio = (cm_per_unit_x/cm_per_unit_y if self.rapport.isChecked() else None)

        commande = (u"repere = %s\n"
                    u"gradu = %s\n"
                    u"fenetre = %s\n"
                    u"ratio = %s"
                    ) % (repere, gradu, fenetre, ratio)

        self.canvas.executer(commande)


    def restaurer(self):
        u"Remet les valeurs par défaut dans les champs."
        self.remplir_champs(repere_O=param.repere[0],
                            repere_I=param.repere[1],
                            repere_J=param.repere[2],
                            gradu_x=param.gradu[0],
                            gradu_y=param.gradu[1],
                            #~ echelle_x=cm_per_unit_x,
                            #~ echelle_y=cm_per_unit_y,
                            resolution=param.dpi_ecran,
                            )
        self.rapport.setChecked(param.ratio is not None)


    def calibrer(self):
        DialogCalibrage(self).exec_()
