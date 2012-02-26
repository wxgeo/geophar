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
                         QLabel, QPixmap, QTextEdit)
from PyQt4.QtCore import Qt

import param
from ..param import NOMPROG, LOGO
from ..pylib.infos import informations_configuration
from ..pylib import path2
from .app import app, white_palette



#class Help(wx.Frame):
#    def __init__(self, parent, path):
#        wx.Frame.__init__(self, parent, size=wx.Size(700,610))

#        self.path = path

#        self.SetBackgroundColour(wx.Colour(255, 225, 153))
#        self.html = html.HtmlWindow(self, -1, style=wx.NO_FULL_REPAINT_ON_RESIZE)
#        self.html.SetRelatedFrame(self, u" %s ")
#        #self.html.SetRelatedStatusBar(0)

#        self.printer = html.HtmlEasyPrinting()

#        self.box = QVBoxLayout()

#        subbox = QHBoxLayout()

#        icones = [(u"maison",u"Page d'accueil.", self.OnHome), (u"gauche", u"Page precedente.", self.OnBack), (u"droite", u"Page suivante.", self.OnForward), (u"print", u"Imprimer la page.", self.OnPrint)]

#        for i in range(len(icones)):
#            icone = icones[i]
#            bmp = png(icone[0])
#            bouton = wx.BitmapButton(self, -1, bmp, style=wx.NO_BORDER)
#            bouton.SetBackgroundColour(self.GetBackgroundColour())
#            subbox.Add(bouton, 0, wx.ALL,5)
#            bouton.setToolTip(icone[1])
#            bouton.Bind(wx.EVT_BUTTON, icone[2])



#        self.box.Add(subbox, 0)
#        self.box.Add(self.html, 1, wx.GROW)
#        self.setLayout(self.box)
#        self.SetAutoLayout(True)

#        self.OnHome(None)


#    def OnHome(self, event):
#        self.html.LoadPage(self.path)



#    def OnBack(self, event):
#        self.html.HistoryBack()


#    def OnForward(self, event):
#        self.html.HistoryForward()


#    def OnPrint(self, event):
#        self.printer.GetPrintData().SetPaperId(wx.PAPER_LETTER)
#        self.printer.PrintFile(self.html.GetOpenedPage())


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



class About(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setWindowTitle(u"A propos de " + NOMPROG)
        self.setPalette(white_palette)

        panel = QWidget(self)

        panelSizer = QVBoxLayout()

        global LOGO
        LOGO = path2(LOGO)
        logo = QLabel(self)
        logo.setPixmap(QPixmap(LOGO))

        panelSizer.addWidget(logo, 0, Qt.AlignCenter)

        date = "/".join(str(n) for n in reversed(param.date_version))
        textes = [u"<b>%s version %s</b>" % (NOMPROG, param.version)]
        textes.append(u"<i>Version publiée le " + date + "</i>")
        textes.append('')
        textes.append(u"De la géométrie dynamique, un traceur de courbes, et bien plus...")
        textes.append(NOMPROG + u" est un logiciel libre, vous pouvez l'utiliser et le modifier comme vous le souhaitez.")
        textes.append(u"<i>Copyright 2005-" + unicode(param.date_version[0]) + " Nicolas Pourcelot (wxgeo@users.sourceforge.net)</i>")
        textes.append('')
        textes.append(NOMPROG + u" inclut désormais SymPy : Python library for symbolic mathematics.")
        textes.append(u"<i>Copyright 2006-" + unicode(param.date_version[0]) + " The Sympy Team - http://www.sympy.org.</i>")
        textes.append('')
        textes.append(u"À Sophie.")
        textes.append(u"<i>'Le rêve est bien réel. Effleurant votre main, je peux toucher le ciel!'  Alain Ayroles</i>")
        textes.append(u"Tous mes remerciements à la communauté du logiciel libre.")
        textes.append('')

        label = QLabel('<br>'.join(textes), panel)
        panelSizer.addWidget(label, 0, Qt.AlignCenter)
        label.setAlignment(Qt.AlignCenter)


        btnOK = QPushButton(u"OK", panel)
        btnOK.clicked.connect(self.close)

        sizer = QHBoxLayout()
        sizer.addStretch(1)
        sizer.addWidget(btnOK)
        sizer.addStretch(1)
        panelSizer.addLayout(sizer)

        panel.setLayout(panelSizer)

        topSizer = QHBoxLayout()
        topSizer.addWidget(panel)

        self.setLayout(topSizer)


class WhiteScrolledMessageDialog(QDialog):
    def __init__(self, parent, title='', msg = '', width=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle(title)
        self.setPalette(white_palette)

        sizer = QVBoxLayout()
        self.setLayout(sizer)

        texte = QTextEdit(self)
        texte.setPlainText(msg)
        texte.setMinimumHeight(500)
        texte.setReadOnly(True)
        if width is None:
            texte.setLineWrapMode(QTextEdit.NoWrap)
            doc = texte.document()
            width = doc.idealWidth() + 4*doc.documentMargin()
        texte.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        texte.setMinimumWidth(width)
        sizer.addWidget(texte)

        boutons = QHBoxLayout()
        boutons.addStretch()
        ok = QPushButton('OK', clicked=self.close)
        boutons.addWidget(ok)
        boutons.addStretch()
        sizer.addLayout(boutons)


class Notes(WhiteScrolledMessageDialog):
    def __init__(self, parent):
        with open(path2("%/doc/notes.txt"), "r") as f:
            msg = f.read().decode("utf8")
        msg = msg.replace(u"WxGeometrie", u"WxGéométrie version " + param.version, 1)
        WhiteScrolledMessageDialog.__init__(self, parent, u"Notes de version", msg, 500)

class Licence(WhiteScrolledMessageDialog):
    def __init__(self, parent):
        with open(path2("%/doc/license.txt"), "r") as f:
            msg = f.read().decode("utf8")
        msg = msg.replace(u"WxGeometrie", u"WxGéométrie version " + param.version, 1)
        WhiteScrolledMessageDialog.__init__(self, parent, u"Licence", msg)
