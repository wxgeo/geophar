# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'repetition_ui.ui'
#
# Created: Mon Apr 16 22:36:53 2012
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_DialogRepetition(object):
    def setupUi(self, DialogRepetition):
        DialogRepetition.setObjectName("DialogRepetition")
        DialogRepetition.resize(400, 192)
        self.verticalLayout = QtGui.QVBoxLayout(DialogRepetition)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_evts = QtGui.QLabel(DialogRepetition)
        self.label_evts.setObjectName("label_evts")
        self.horizontalLayout.addWidget(self.label_evts)
        self.evenements = QtGui.QLineEdit(DialogRepetition)
        self.evenements.setObjectName("evenements")
        self.horizontalLayout.addWidget(self.evenements)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_probas = QtGui.QLabel(DialogRepetition)
        self.label_probas.setObjectName("label_probas")
        self.horizontalLayout_2.addWidget(self.label_probas)
        self.probas = QtGui.QLineEdit(DialogRepetition)
        self.probas.setObjectName("probas")
        self.horizontalLayout_2.addWidget(self.probas)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_niveaux = QtGui.QLabel(DialogRepetition)
        self.label_niveaux.setObjectName("label_niveaux")
        self.horizontalLayout_4.addWidget(self.label_niveaux)
        self.niveaux = QtGui.QSpinBox(DialogRepetition)
        self.niveaux.setMinimum(1)
        self.niveaux.setMaximum(10)
        self.niveaux.setProperty("value", 3)
        self.niveaux.setObjectName("niveaux")
        self.horizontalLayout_4.addWidget(self.niveaux)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.numeroter = QtGui.QCheckBox(DialogRepetition)
        self.numeroter.setChecked(True)
        self.numeroter.setObjectName("numeroter")
        self.verticalLayout.addWidget(self.numeroter)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.buttonBox = QtGui.QDialogButtonBox(DialogRepetition)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DialogRepetition)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), DialogRepetition.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), DialogRepetition.reject)
        QtCore.QMetaObject.connectSlotsByName(DialogRepetition)

    def retranslateUi(self, DialogRepetition):
        DialogRepetition.setWindowTitle(QtGui.QApplication.translate("DialogRepetition", "Répétition d\'expériences indépendantes", None, QtGui.QApplication.UnicodeUTF8))
        self.label_evts.setText(QtGui.QApplication.translate("DialogRepetition", "Évènements:", None, QtGui.QApplication.UnicodeUTF8))
        self.evenements.setToolTip(QtGui.QApplication.translate("DialogRepetition", "Rentrer les évènements séparés par une virgule.\n"
"Exemple: « A, B, C ».\n"
"Si un seul évènement est entré, l\'évènement contraire est rajouté.\n"
"", None, QtGui.QApplication.UnicodeUTF8))
        self.label_probas.setText(QtGui.QApplication.translate("DialogRepetition", "Probabilités: ", None, QtGui.QApplication.UnicodeUTF8))
        self.probas.setToolTip(QtGui.QApplication.translate("DialogRepetition", "Rentrer les probabilités des évènements précédents, séparés par une virgule.\n"
"La dernière probabilité peut-être omise.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_niveaux.setText(QtGui.QApplication.translate("DialogRepetition", "Nombre de niveaux", None, QtGui.QApplication.UnicodeUTF8))
        self.numeroter.setToolTip(QtGui.QApplication.translate("DialogRepetition", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Distinguer les expériences successives en rajoutant des indices aux évènements.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Par exemple, A<span style=\" vertical-align:sub;\">1</span>, puis A<span style=\" vertical-align:sub;\">2</span>, A<span style=\" vertical-align:sub;\">3</span>, etc.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.numeroter.setText(QtGui.QApplication.translate("DialogRepetition", "Numéroter les évènements", None, QtGui.QApplication.UnicodeUTF8))

