# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'calibrage.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogCalibrage(object):
    def setupUi(self, DialogCalibrage):
        DialogCalibrage.setObjectName("DialogCalibrage")
        DialogCalibrage.resize(510, 271)
        self.verticalLayout = QtWidgets.QVBoxLayout(DialogCalibrage)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_16 = QtWidgets.QLabel(DialogCalibrage)
        self.label_16.setObjectName("label_16")
        self.verticalLayout.addWidget(self.label_16)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame = QtWidgets.QFrame(DialogCalibrage)
        self.frame.setMinimumSize(QtCore.QSize(300, 30))
        self.frame.setMaximumSize(QtCore.QSize(300, 30))
        self.frame.setStyleSheet("background-color: rgb(255, 223, 148);\n"
"border-style: solid;\n"
"border-color: rgb(255, 170, 0);\n"
"border-width: 1px;")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setStyleSheet("color:rgb(255, 170, 0);\n"
"border-style:None;\n"
"")
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2, 0, QtCore.Qt.AlignHCenter)
        self.horizontalLayout.addWidget(self.frame)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_17 = QtWidgets.QLabel(DialogCalibrage)
        self.label_17.setObjectName("label_17")
        self.horizontalLayout_9.addWidget(self.label_17)
        self.longueur = QtWidgets.QLineEdit(DialogCalibrage)
        self.longueur.setObjectName("longueur")
        self.horizontalLayout_9.addWidget(self.longueur)
        self.label_18 = QtWidgets.QLabel(DialogCalibrage)
        self.label_18.setObjectName("label_18")
        self.horizontalLayout_9.addWidget(self.label_18)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_9)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
        self.line = QtWidgets.QFrame(DialogCalibrage)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.buttonBox = QtWidgets.QDialogButtonBox(DialogCalibrage)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DialogCalibrage)
        self.buttonBox.accepted.connect(DialogCalibrage.accept)
        self.buttonBox.rejected.connect(DialogCalibrage.close)
        QtCore.QMetaObject.connectSlotsByName(DialogCalibrage)

    def retranslateUi(self, DialogCalibrage):
        _translate = QtCore.QCoreApplication.translate
        DialogCalibrage.setWindowTitle(_translate("DialogCalibrage", "Calibrage de l\'écran"))
        self.label_16.setText(_translate("DialogCalibrage", "<html><head/><body><p>Pour calibrer votre écran mesurez avec une règle la barre orange suivante.</p><p>Reportez ensuite ci-dessous sa <span style=\" font-weight:600;\">longueur</span> en cm, pour que la résolution<br/>soit automatiquement calculée.</p></body></html>"))
        self.label_2.setText(_translate("DialogCalibrage", "Mesurez moi !"))
        self.label_17.setText(_translate("DialogCalibrage", "Longueur mesurée : "))
        self.label_18.setText(_translate("DialogCalibrage", "cm"))

