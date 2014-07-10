# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'wxgeometrie/GUI/calibrage.ui'
#
# Created: Thu Jul 10 17:03:16 2014
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_DialogCalibrage(object):
    def setupUi(self, DialogCalibrage):
        DialogCalibrage.setObjectName(_fromUtf8("DialogCalibrage"))
        DialogCalibrage.resize(510, 271)
        self.verticalLayout = QtGui.QVBoxLayout(DialogCalibrage)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_16 = QtGui.QLabel(DialogCalibrage)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.verticalLayout.addWidget(self.label_16)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.frame = QtGui.QFrame(DialogCalibrage)
        self.frame.setMinimumSize(QtCore.QSize(300, 30))
        self.frame.setMaximumSize(QtCore.QSize(300, 30))
        self.frame.setStyleSheet(_fromUtf8("background-color: rgb(255, 223, 148);\n"
"border-style: solid;\n"
"border-color: rgb(255, 170, 0);\n"
"border-width: 1px;"))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setStyleSheet(_fromUtf8("color:rgb(255, 170, 0);\n"
"border-style:None;\n"
""))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.horizontalLayout.addWidget(self.frame)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout_9 = QtGui.QHBoxLayout()
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        self.label_17 = QtGui.QLabel(DialogCalibrage)
        self.label_17.setObjectName(_fromUtf8("label_17"))
        self.horizontalLayout_9.addWidget(self.label_17)
        self.longueur = QtGui.QLineEdit(DialogCalibrage)
        self.longueur.setObjectName(_fromUtf8("longueur"))
        self.horizontalLayout_9.addWidget(self.longueur)
        self.label_18 = QtGui.QLabel(DialogCalibrage)
        self.label_18.setObjectName(_fromUtf8("label_18"))
        self.horizontalLayout_9.addWidget(self.label_18)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_9)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
        self.line = QtGui.QFrame(DialogCalibrage)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.buttonBox = QtGui.QDialogButtonBox(DialogCalibrage)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DialogCalibrage)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DialogCalibrage.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DialogCalibrage.close)
        QtCore.QMetaObject.connectSlotsByName(DialogCalibrage)

    def retranslateUi(self, DialogCalibrage):
        DialogCalibrage.setWindowTitle(_translate("DialogCalibrage", "Calibrage de l\'écran", None))
        self.label_16.setText(_translate("DialogCalibrage", "<html><head/><body><p>Pour calibrer votre écran mesurez avec une règle la barre orange suivante.</p><p>Reportez ensuite ci-dessous sa <span style=\" font-weight:600;\">longueur</span> en cm, pour que la résolution<br/>soit automatiquement calculée.</p></body></html>", None))
        self.label_2.setText(_translate("DialogCalibrage", "Mesurez moi !", None))
        self.label_17.setText(_translate("DialogCalibrage", "Longueur mesurée : ", None))
        self.label_18.setText(_translate("DialogCalibrage", "cm", None))

