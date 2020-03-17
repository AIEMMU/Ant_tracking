# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!

import sys
from displayView import MainWindow
from PyQt5 import QtWidgets
from displayViewModel import *


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(DisplayViewModel(enableButtons, getPixmap))  # create an instace of our class
    window.show()
    app.exec_()  # start the application
if __name__ == "__main__":
    main()

