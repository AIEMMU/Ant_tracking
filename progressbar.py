from PyQt5 import QtCore, QtGui, QtWidgets
import sys


from progress_form import Ui_Dialog

class ProgressBar(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, desc = None, parent=None):
        super(ProgressBar, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setupUi(self)
        self.show()
        self.progressBar.setValue(0)
        if desc != None:
            self.setDescription(desc)

    def setValue(self, val): # Sets value
        self.progressBar.setProperty("value", val)

    def setDescription(self, desc): # Sets Pbar window title
        self.setWindowTitle(desc)

def main():
    app = QtWidgets.QApplication(sys.argv)
    # A new instance of QApplication
    form = ProgressBar('pbar')                        # We set the form to be our MainWindow (design)
    form.exec_()                                 # and execute the app

if __name__ == '__main__':                      # if we're running file directly and not importing it
    main()