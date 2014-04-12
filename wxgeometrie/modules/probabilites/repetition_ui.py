# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'repetition_ui.ui'
#
# Created: Sat Apr 12 22:20:41 2014
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_DialogRepetition(object):
    def setupUi(self, DialogRepetition):
        DialogRepetition.setObjectName(_fromUtf8("DialogRepetition"))
        DialogRepetition.resize(400, 192)
        self.verticalLayout = QtGui.QVBoxLayout(DialogRepetition)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_evts = QtGui.QLabel(DialogRepetition)
        self.label_evts.setObjectName(_fromUtf8("label_evts"))
        self.horizontalLayout.addWidget(self.label_evts)
        self.evenements = QtGui.QLineEdit(DialogRepetition)
        self.evenements.setObjectName(_fromUtf8("evenements"))
        self.horizontalLayout.addWidget(self.evenements)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_probas = QtGui.QLabel(DialogRepetition)
        self.label_probas.setObjectName(_fromUtf8("label_probas"))
        self.horizontalLayout_2.addWidget(self.label_probas)
        self.probas = QtGui.QLineEdit(DialogRepetition)
        self.probas.setObjectName(_fromUtf8("probas"))
        self.horizontalLayout_2.addWidget(self.probas)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_niveaux = QtGui.QLabel(DialogRepetition)
        self.label_niveaux.setObjectName(_fromUtf8("label_niveaux"))
        self.horizontalLayout_4.addWidget(self.label_niveaux)
        self.niveaux = QtGui.QSpinBox(DialogRepetition)
        self.niveaux.setMinimum(1)
        self.niveaux.setMaximum(10)
        self.niveaux.setProperty("value", 3)
        self.niveaux.setObjectName(_fromUtf8("niveaux"))
        self.horizontalLayout_4.addWidget(self.niveaux)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.numeroter = QtGui.QCheckBox(DialogRepetition)
        self.numeroter.setChecked(True)
        self.numeroter.setObjectName(_fromUtf8("numeroter"))
        self.verticalLayout.addWidget(self.numeroter)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.buttonBox = QtGui.QDialogButtonBox(DialogRepetition)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DialogRepetition)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DialogRepetition.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DialogRepetition.reject)
        QtCore.QMetaObject.connectSlotsByName(DialogRepetition)

    def retranslateUi(self, DialogRepetition):
        DialogRepetition.setWindowTitle(_translate("DialogRepetition", "Répétition d\'expériences indépendantes", None))
        self.label_evts.setText(_translate("DialogRepetition", "Évènements:", None))
        self.evenements.setToolTip(_translate("DialogRepetition", "<html><head/><body><p>Rentrer les évènements séparés par un <span style=\" font-weight:600;\">point-virgule</span>.</p><p>Exemple: « A ; B ; C ».</p><p>Si un seul évènement est entré, l\'évènement contraire est rajouté.</p></body></html>", None))
        self.evenements.setWhatsThis(_translate("DialogRepetition", "<html><head/><body><p>Rentrer les évènements séparés par un <span style=\" font-weight:600;\">point-virgule</span>.</p><p>Exemple: « A ; B ; C ».</p><p>Si un seul évènement est entré, l\'évènement contraire est rajouté.</p></body></html>", None))
        self.label_probas.setText(_translate("DialogRepetition", "Probabilités: ", None))
        self.probas.setToolTip(_translate("DialogRepetition", "<html><head/><body><p>Rentrer les probabilités des évènements précédents, séparés par un <span style=\" font-weight:600;\">point-virgule</span>.</p><p>La dernière probabilité peut-être omise.</p></body></html>", None))
        self.probas.setWhatsThis(_translate("DialogRepetition", "<html><head/><body><p>Rentrer les probabilités des évènements précédents, séparés par un <span style=\" font-weight:600;\">point-virgule</span>.</p><p>La dernière probabilité peut-être omise.</p></body></html>", None))
        self.label_niveaux.setText(_translate("DialogRepetition", "Nombre de niveaux", None))
        self.numeroter.setToolTip(_translate("DialogRepetition", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Distinguer les expériences successives en rajoutant des indices aux évènements.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Par exemple, A<span style=\" vertical-align:sub;\">1</span>, puis A<span style=\" vertical-align:sub;\">2</span>, A<span style=\" vertical-align:sub;\">3</span>, etc.</p></body></html>", None))
        self.numeroter.setText(_translate("DialogRepetition", "Numéroter les évènements", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    DialogRepetition = QtGui.QDialog()
    ui = Ui_DialogRepetition()
    ui.setupUi(DialogRepetition)
    DialogRepetition.show()
    sys.exit(app.exec_())

