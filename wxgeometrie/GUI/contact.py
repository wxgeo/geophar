# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                 Contact                     #
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

import sys

from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import (QHBoxLayout, QVBoxLayout, QCheckBox, QPushButton, QDialog,
                         QTextEdit, QLineEdit, QLabel, QComboBox, QGroupBox,
                         QMessageBox, QWidget,)
from .. import param
from ..pylib import path2
from ..pylib.bugs_report import rapporter
from .app import white_palette
from .wxlib import GenericThread
from ..pylib.infos import informations_configuration


class Contact(QDialog):
    u"Formulaire utilisé pour contacter l'auteur et rapporter les bogues."

    sent = pyqtSignal(bool, unicode)

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setWindowTitle(u"Contacter l'auteur")
        #style = wx.FRAME_FLOAT_ON_PARENT|wx.CLIP_CHILDREN|wx.CLOSE_BOX|wx.CAPTION)
        self.setPalette(white_palette)

        self.parent = parent

        panel = QWidget(self)
#        italic = wx.Font(panel.GetFont().GetPointSize(), panel.GetFont().GetFamily(), wx.ITALIC, wx.NORMAL)
#        bold_italic = wx.Font(panel.GetFont().GetPointSize(), panel.GetFont().GetFamily(), wx.ITALIC, wx.BOLD)
#        panel.setStyleSheet("background-color:white")

        panelSizer = QVBoxLayout()

        avant_propos = QLabel(u"""<i>Afin d'améliorer le fonctionnement de WxGéométrie,
vous êtes invités à signaler tout problème rencontré.</i>""", panel)
        panelSizer.addWidget(avant_propos)
        panelSizer.addSpacing(5)

        rapport = QVBoxLayout()
        rapport_box = QGroupBox(u"Rapport d'incident", panel)
        rapport_box.setLayout(rapport)
        self.titre = titre = QLineEdit(panel)
        titre.setMinimumWidth(200)
        titre.setText(u"Résumé")
        titre.selectAll()
        rapport.addWidget(titre)

        sizer= QHBoxLayout()
        self.modules = modules = QComboBox(panel)
        modules.addItems([parent.onglet(md).titre for md in param.modules if hasattr(self.parent.onglet(md), "titre")])
        modules.setCurrentIndex(self.parent.currentIndex())
        sizer.addWidget(QLabel(u"Module concerné :", panel))
        sizer.addWidget(modules)
        rapport.addLayout(sizer)

        rapport.addWidget(QLabel(u"Description du problème :", panel))
        self.commentaire = commentaire = QTextEdit(panel)
        commentaire.setMinimumSize(200, 100)
        rapport.addWidget(commentaire)

        panelSizer.addWidget(rapport_box)

        sizer = QHBoxLayout()
        coordonnees_box = QGroupBox(u"Vos coordonnées (recommandées)", panel)
        coordonnees_box.setLayout(sizer)
        sizer.addWidget(QLabel(u"Nom :", panel))
        self.nom = nom = QLineEdit(panel)
        nom.setMinimumWidth(100)
        sizer.addWidget(nom)
        sizer.addWidget(QLabel(u" E-mail :"))
        self.mail = mail = QLineEdit(panel)
        mail.setMinimumWidth(100)
        sizer.addWidget(mail)

        panelSizer.addWidget(coordonnees_box)

        options = QVBoxLayout()
        options_box = QGroupBox(u"Options", panel)
        options_box.setLayout(options)
        self.histo = histo = QCheckBox("Inclure l'historique du module courant.")
        histo.setChecked(True)
        options.addWidget(histo)

        self.msg = msg = QCheckBox("Inclure l'historique des commandes.")
        msg.setChecked(True)
        options.addWidget(msg)

        panelSizer.addWidget(options_box)


        btnOK = QPushButton(u"Envoyer", panel)
        btnOK.setToolTip(u"Envoyer les informations.")
        btnCancel = QPushButton(u"Annuler", panel)
        btnCancel.setToolTip(u"Quitter sans rien envoyer.")

        sizer = QHBoxLayout()
        sizer.addWidget(btnOK)
        sizer.addStretch()
        sizer.addWidget(btnCancel)
        panelSizer.addLayout(sizer)

#        panel.SetAutoLayout(True)
        panel.setLayout(panelSizer)
#        panelSizer.Fit(panel)

        topSizer = QHBoxLayout()
        topSizer.addWidget(panel)

#        self.SetAutoLayout(True)
        self.setLayout(topSizer)

        self.sent.connect(self.termine)
        btnOK.clicked.connect(self.rapporter)
        btnCancel.clicked.connect(self.close)


    def rapporter(self):
        module = self.parent.onglet(self.modules.currentIndex())
        if self.histo.isChecked() and hasattr(module, "log"):
            histo = module.log.contenu()
        else:
            histo = ""
        if self.msg.isChecked():
            sys.stdout.flush()
            filename = path2(param.emplacements['log'] + u"/messages.log")
            try:
                file = open(filename, 'r')
                msg = file.read()
            finally:
                file.close()
        else:
            msg = ""
        self.hide()
        kw = {'titre': self.titre.text(), 'auteur': self.nom.text(),
              'email': self.mail.text(), 'description': self.commentaire.toPlainText(),
              'historique': histo, 'log': msg, 'config': informations_configuration(),
             }
        self.thread = GenericThread(self._rapporter, **kw)
        self.thread.start()
        # XXX: Qt complains here: "QObject::connect: Cannot queue arguments of type 'QTextBlock'"


    def _rapporter(self, **kw):
        # /!\ Ne **JAMAIS** utiliser `print()` depuis une autre thread que la principale !
        self.sent.emit(*rapporter(**kw))



    def termine(self, success, msg):
        if param.debug:
            print(' ** Remote site report **\n' + msg)
        if 'mail()' in msg:
            # Fonction mail() de PHP très probablement bloquée par Free.
            success = False
        if success:
            QMessageBox.information(self, u"Message envoyé", u"Le message a été envoyé avec succès. Merci !")
            self.close()
        else:
            QMessageBox.warning(self, u"Connexion impossible.", u"Impossible d'envoyer le message !")
            self.show()
