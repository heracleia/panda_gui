#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tf.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

p = 0.0
q = 0.0
r = 0.0

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(525, 313)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(210, 250, 99, 27))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.settf)
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setGeometry(QtCore.QRect(150, 40, 221, 171))
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.horizontalSlider = QtWidgets.QSlider(self.splitter)
        self.horizontalSlider.setMinimum(-200)
        self.horizontalSlider.setMaximum(200)
        self.horizontalSlider.setSingleStep(1)
        self.horizontalSlider.setProperty("value", -200)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setTickInterval(0)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.horizontalSlider.valueChanged.connect(self.updatepvalue)
        self.horizontalSlider_2 = QtWidgets.QSlider(self.splitter)
        self.horizontalSlider_2.setMinimum(-200)
        self.horizontalSlider_2.setMaximum(200)
        self.horizontalSlider_2.setProperty("value", -200)
        self.horizontalSlider_2.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_2.setObjectName("horizontalSlider_2")
        self.horizontalSlider_2.valueChanged.connect(self.updateqvalue)
        self.horizontalSlider_3 = QtWidgets.QSlider(self.splitter)
        self.horizontalSlider_3.setMinimum(-200)
        self.horizontalSlider_3.setMaximum(200)
        self.horizontalSlider_3.setProperty("value", -200)
        self.horizontalSlider_3.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_3.setObjectName("horizontalSlider_3")
        self.horizontalSlider_3.valueChanged.connect(self.updatervalue)
        self.splitter_2 = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_2.setGeometry(QtCore.QRect(30, 40, 91, 171))
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setObjectName("splitter_2")
        self.label_2 = QtWidgets.QLabel(self.splitter_2)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.splitter_2)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.label = QtWidgets.QLabel(self.splitter_2)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.splitter_3 = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_3.setGeometry(QtCore.QRect(400, 42, 101, 171))
        self.splitter_3.setOrientation(QtCore.Qt.Vertical)
        self.splitter_3.setObjectName("splitter_3")
        self.pvalue = QtWidgets.QLabel(self.splitter_3)
        self.pvalue.setText("")
        self.pvalue.setAlignment(QtCore.Qt.AlignCenter)
        self.pvalue.setObjectName("pvalue")
        self.qvalue = QtWidgets.QLabel(self.splitter_3)
        self.qvalue.setText("")
        self.qvalue.setAlignment(QtCore.Qt.AlignCenter)
        self.qvalue.setObjectName("qvalue")
        self.rvalue = QtWidgets.QLabel(self.splitter_3)
        self.rvalue.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.rvalue.setText("")
        self.rvalue.setAlignment(QtCore.Qt.AlignCenter)
        self.rvalue.setObjectName("rvalue")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Set TF"))
        self.label_2.setText(_translate("MainWindow", "p - value"))
        self.label_3.setText(_translate("MainWindow", "q - value"))
        self.label.setText(_translate("MainWindow", "r - value"))

    def updatepvalue(self, value):
        self.pvalue.setText(str(value / 100.0))

    def updateqvalue(self, value):
        self.qvalue.setText(str(value / 100.0))

    def updatervalue(self, value):
        self.rvalue.setText(str(value / 100.0))

    def settf(self):
        p = self.horizontalSlider.value() / 100.0
        q = self.horizontalSlider_2.value() / 100.0
        r = self.horizontalSlider_3.value() / 100.0


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
