# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'repetition_ui.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogRepetition(object):
    def setupUi(self, DialogRepetition):
        DialogRepetition.setObjectName("DialogRepetition")
        DialogRepetition.resize(400, 192)
        self.verticalLayout = QtWidgets.QVBoxLayout(DialogRepetition)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_evts = QtWidgets.QLabel(DialogRepetition)
        self.label_evts.setObjectName("label_evts")
        self.horizontalLayout.addWidget(self.label_evts)
        self.evenements = QtWidgets.QLineEdit(DialogRepetition)
        self.evenements.setObjectName("evenements")
        self.horizontalLayout.addWidget(self.evenements)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_probas = QtWidgets.QLabel(DialogRepetition)
        self.label_probas.setObjectName("label_probas")
        self.horizontalLayout_2.addWidget(self.label_probas)
        self.probas = QtWidgets.QLineEdit(DialogRepetition)
        self.probas.setObjectName("probas")
        self.horizontalLayout_2.addWidget(self.probas)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_niveaux = QtWidgets.QLabel(DialogRepetition)
        self.label_niveaux.setObjectName("label_niveaux")
        self.horizontalLayout_4.addWidget(self.label_niveaux)
        self.niveaux = QtWidgets.QSpinBox(DialogRepetition)
        self.niveaux.setMinimum(1)
        self.niveaux.setMaximum(10)
        self.niveaux.setProperty("value", 3)
        self.niveaux.setObjectName("niveaux")
        self.horizontalLayout_4.addWidget(self.niveaux)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.numeroter = QtWidgets.QCheckBox(DialogRepetition)
        self.numeroter.setChecked(True)
        self.numeroter.setObjectName("numeroter")
        self.verticalLayout.addWidget(self.numeroter)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.buttonBox = QtWidgets.QDialogButtonBox(DialogRepetition)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DialogRepetition)
        self.buttonBox.accepted.connect(DialogRepetition.accept)
        self.buttonBox.rejected.connect(DialogRepetition.reject)
        QtCore.QMetaObject.connectSlotsByName(DialogRepetition)

    def retranslateUi(self, DialogRepetition):
        _translate = QtCore.QCoreApplication.translate
        DialogRepetition.setWindowTitle(_translate("DialogRepetition", "Répétition d\'expériences indépendantes"))
        self.label_evts.setText(_translate("DialogRepetition", "Évènements:"))
        self.evenements.setToolTip(_translate("DialogRepetition", "<html><head/><body><p>Rentrer les évènements séparés par un <span style=\" font-weight:600;\">point-virgule</span>.</p><p>Exemple: « A ; B ; C ».</p><p>Si un seul évènement est entré, l\'évènement contraire est rajouté.</p></body></html>"))
        self.evenements.setWhatsThis(_translate("DialogRepetition", "<html><head/><body><p>Rentrer les évènements séparés par un <span style=\" font-weight:600;\">point-virgule</span>.</p><p>Exemple: « A ; B ; C ».</p><p>Si un seul évènement est entré, l\'évènement contraire est rajouté.</p></body></html>"))
        self.label_probas.setText(_translate("DialogRepetition", "Probabilités: "))
        self.probas.setToolTip(_translate("DialogRepetition", "<html><head/><body><p>Rentrer les probabilités des évènements précédents, séparés par un <span style=\" font-weight:600;\">point-virgule</span>.</p><p>La dernière probabilité peut-être omise.</p></body></html>"))
        self.probas.setWhatsThis(_translate("DialogRepetition", "<html><head/><body><p>Rentrer les probabilités des évènements précédents, séparés par un <span style=\" font-weight:600;\">point-virgule</span>.</p><p>La dernière probabilité peut-être omise.</p></body></html>"))
        self.label_niveaux.setText(_translate("DialogRepetition", "Nombre de niveaux"))
        self.numeroter.setToolTip(_translate("DialogRepetition", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Distinguer les expériences successives en rajoutant des indices aux évènements.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Par exemple, A<span style=\" vertical-align:sub;\">1</span>, puis A<span style=\" vertical-align:sub;\">2</span>, A<span style=\" vertical-align:sub;\">3</span>, etc.</p></body></html>"))
        self.numeroter.setText(_translate("DialogRepetition", "Numéroter les évènements"))

