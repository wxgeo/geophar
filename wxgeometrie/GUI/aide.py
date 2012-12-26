# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)


##--------------------------------------#######
#                 Aide                        #
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


from PyQt4.QtGui import (QPushButton, QDialog, QWidget, QVBoxLayout, QHBoxLayout,
                         QLabel, QPixmap, QTextEdit, QTabWidget)
from PyQt4.QtCore import Qt

from .. import param
from ..param import NOMPROG, LOGO
ANNEE = param.date_version[0]
from ..pylib.infos import informations_configuration
from ..pylib import path2
from .app import app, white_palette





class Informations(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setWindowTitle(u"Configuration systeme")
        self.setPalette(white_palette)

        panel = QWidget(self)

        panelSizer = QVBoxLayout()

        textes = informations_configuration().split(u"\n")

        for i, texte in enumerate(textes):
            if texte.startswith("+ "):
                textes[i] = '<i>' + texte + '</i>'
        t = QLabel('<br>'.join(textes), panel)
        panelSizer.addWidget(t)


        btnOK = QPushButton(u"OK", panel)
        btnOK.clicked.connect(self.close)
        btnCopier = QPushButton(u"Copier", panel)
        btnCopier.clicked.connect(self.copier)

        sizer = QHBoxLayout()
        sizer.addWidget(btnOK)
        sizer.addStretch()
        sizer.addWidget(btnCopier)
        panelSizer.addLayout(sizer)

        panel.setLayout(panelSizer)

        topSizer = QHBoxLayout()
        topSizer.addWidget(panel)

        self.setLayout(topSizer)


    def copier(self):
        app.vers_presse_papier(informations_configuration())


class APropos(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.parent = parent
        sizer = QVBoxLayout()
        global LOGO
        LOGO = path2(LOGO)
        logo = QLabel(self)
        logo.setPixmap(QPixmap(LOGO))

        sizer.addWidget(logo, 0, Qt.AlignCenter)

        date = "/".join(str(n) for n in reversed(param.date_version))
        textes = [u"<b>%s version %s</b>" % (NOMPROG, param.version)]
        textes.append(u"<i>Version publiée le " + date + "</i>")
        textes.append('')
        textes.append(u"« Le couteau suisse du prof de maths »")
        textes.append('')
        textes.append("<img src='%s'> <b>%s est un \
                    <a href='http://fr.wikipedia.org/wiki/Logiciel_libre'> \
                    logiciel libre</a></b>"
                    %(path2('%/wxgeometrie/images/copyleft.png'), NOMPROG))
        textes.append(u"Vous pouvez l'utiliser et le modifier selon les termes de la GNU Public License v2.")
        textes.append(u"<i>Copyleft 2005-%s Nicolas Pourcelot (wxgeo@users.sourceforge.net)</i>"
                            % ANNEE)
        textes.append('')
        label = QLabel('<br>'.join(textes))
        label.setAlignment(Qt.AlignCenter)
        label.setOpenExternalLinks(True)

        sizer.addWidget(label, 0, Qt.AlignCenter)
        self.setLayout(sizer)


class Licence(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.parent = parent

        sizer = QVBoxLayout()

        texte = QTextEdit(self)
        with open(path2("%/wxgeometrie/doc/license.txt"), "r") as f:
            msg = f.read().decode("utf8")
        texte.setPlainText(msg)
        texte.setMinimumHeight(500)
        texte.setReadOnly(True)
        texte.setLineWrapMode(QTextEdit.NoWrap)
        doc = texte.document()
        width = doc.idealWidth() + 4*doc.documentMargin()
        texte.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        texte.setMinimumWidth(width)
        sizer.addWidget(texte)
        self.setLayout(sizer)


class Notes(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.parent = parent

        sizer = QVBoxLayout()

        texte = QTextEdit(self)
        with open(path2("%/wxgeometrie/doc/changelog.txt"), "r") as f:
            msg = f.read().decode("utf8").replace('\n', '<br>')
        titre = u"<b>Changements apportés par la version %s :</b>" % param.version
        msg = '<br>'.join((titre, '', msg))
        texte.setHtml(msg)
        texte.setMinimumHeight(500)
        texte.setReadOnly(True)
        texte.setLineWrapMode(QTextEdit.NoWrap)
        doc = texte.document()
        width = doc.idealWidth() + 4*doc.documentMargin()
        texte.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        texte.setMinimumWidth(width)
        sizer.addWidget(texte)
        self.setLayout(sizer)


class Credits(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.parent = parent

        sizer = QVBoxLayout()
        texte = \
        u"""<h3>Contributeurs :</h3>
        <p><i>Les personnes suivantes ont contribuées au code de %(NOMPROG)s</i></p>
        <ul>
        <li><i>Boris Mauricette</i> : statistiques, interpolation (2011-2012)</li>
        <li><i>Christophe Gragnic</i> : gestion de la documentation (2012)</li>
        </ul>
        <br>
        <h3>Remerciements :</h3>
        <p>
        <a href="http://wxgeo.free.fr/doc/html/help.html#remerciements">
        De nombreuses personnes</a> ont aidé ce projet, par leur retours d'expérience,<br>
        ou par leur aide à l'installation sur certaines plateformes.<br>
        Qu'elles en soient remerciées.</p>
        <p>
        Remerciements tous particuliers à <i>Jean-Pierre Garcia</i> et à <i>Georges Khaznadar</i>.</p>
        <br>
        <h3>Librairies utilisées :</h3>
        <ul>
        <li>%(NOMPROG)s inclut désormais <a href='http://www.sympy.org'> SymPy</a>
            (Python library for symbolic mathematics)<br>
            © 2006-%(ANNEE)s <i>The Sympy Team</i></li>
        <li>%(NOMPROG)s est codé en <a href="http://www.python.org">Python</a></li>
        <li><a href="http://www.numpy.org">Numpy</a> est une bibliothèque de calcul numérique</li>
        <li><a href="http://www.matplotlib.org">Matplotlib</a> est une librairie graphique scientifique</li>
        <li><a href="http://www.riverbankcomputing.co.uk/software/pyqt">PyQt</a>
        est utilisé pour l'interface graphique</li>
        </ul>

        <p>
        Plus généralement, je remercie tous les acteurs de la communauté du logiciel libre,<br>
        tous ceux qui prennent la peine de partager leur savoir et leur travail.</p>
        <p>Nous ne sommes jamais que <i>« des nains juchés sur des épaules de géants » (Bernard de Chartres)</i>.
        <br>
        <p><i>À Sophie.</i></p>
        <p><i>« Il y a des yeux qui reçoivent la lumière et il y a des yeux qui la donnent » (Paul Claudel)</i>
        </p>
        """ % globals()
        label = QLabel(texte)
        label.setOpenExternalLinks(True)

        sizer.addWidget(label)
        sizer.addStretch()
        self.setLayout(sizer)


class OngletsAbout(QTabWidget):
    def __init__(self, parent):
        QTabWidget.__init__(self, parent)
        self.addTab(APropos(parent), u'À propos')
        self.addTab(Licence(parent), u'Licence')
        self.addTab(Notes(parent), u'Notes de version')
        self.addTab(Credits(parent), u'Crédits')
        self.setTabPosition(QTabWidget.South)
        self.setStyleSheet("""
        QTabBar::tab:selected {
        background: white;
        border: 1px solid #C4C4C3;
        border-top-color: white; /* same as the pane color */
        border-bottom-left-radius: 4px;
        border-bottom-right-radius: 4px;
        border-top-left-radius: 0px;
        border-top-right-radius: 0px;
        min-width: 8ex;
        padding: 7px;
        }
        QStackedWidget {background:white}
        QTabBar QToolButton {
        background:white;
        border: 1px solid #C4C4C3;
        border-top-color: white; /* same as the pane color */
        border-bottom-left-radius: 4px;
        border-bottom-right-radius: 4px;
        border-top-left-radius: 0px;
        border-top-right-radius: 0px;
        }
        """)


class About(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setWindowTitle(u"A propos de " + NOMPROG)
        self.setPalette(white_palette)
        ##self.setWindowFlags(Qt.Dialog|Qt.FramelessWindowHint|Qt.X11BypassWindowManagerHint)
        sizer = QVBoxLayout()

        sizer.addWidget(OngletsAbout(self))

        self.setLayout(sizer)



##class WhiteScrolledMessageDialog(QDialog):
    ##def __init__(self, parent, title='', msg = '', width=None):
        ##QDialog.__init__(self, parent)
        ##self.setWindowTitle(title)
        ##self.setPalette(white_palette)
##
        ##sizer = QVBoxLayout()
        ##self.setLayout(sizer)
##
        ##texte = QTextEdit(self)
        ##texte.setPlainText(msg)
        ##texte.setMinimumHeight(500)
        ##texte.setReadOnly(True)
        ##if width is None:
            ##texte.setLineWrapMode(QTextEdit.NoWrap)
            ##doc = texte.document()
            ##width = doc.idealWidth() + 4*doc.documentMargin()
        ##texte.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        ##texte.setMinimumWidth(width)
        ##sizer.addWidget(texte)
##
        ##boutons = QHBoxLayout()
        ##boutons.addStretch()
        ##ok = QPushButton('OK', clicked=self.close)
        ##boutons.addWidget(ok)
        ##boutons.addStretch()
        ##sizer.addLayout(boutons)

