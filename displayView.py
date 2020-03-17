from PyQt5 import QtWidgets, uic, QtCore
from gui_utils import *

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self,model):
        self.model = model
        super(MainWindow, self).__init__() #call the inherited class __init__ method
        uic.loadUi("gui.ui", self) # load teh UI file

        #video loader
        self.videoMenu = self.findChild(QtWidgets.QAction, 'loadVideo')
        self.videoMenu.triggered.connect(self.LoadVideo)

        #videoPlayer
        self.videoPlayer = self.findChild(QtWidgets.QLabel, 'videoPlayer')
        self.videoPlayer.setAlignment(QtCore.Qt.AlignCenter)

        # Buttons!
        self.processBtn = self.findChild(QtWidgets.QPushButton, 'processBtn')
        self.processBtn.clicked.connect(self.saveVideo)  # remeber to pass the definition of the method
        self.processBtn.setEnabled(False)
        #previewBtn
        self.previewBtn = self.findChild(QtWidgets.QPushButton, 'previewBtn')
        self.previewBtn.clicked.connect(self.settings)  # remeber to pass the definition of the method
        self.previewBtn.setEnabled(False)
        #exportBtn
        self.displayButton = self.findChild(QtWidgets.QPushButton, 'displayButton')
        self.displayButton.clicked.connect(self.updateVideoDisplay)  # remember to pass the definition of the method
        self.displayButton.setEnabled(False)

        self.exportBtn = self.findChild(QtWidgets.QPushButton, 'exportBtn')
        self.exportBtn.clicked.connect(self.export)
        self.exportBtn.setEnabled(False)

        self.totalLeft = self.findChild(QtWidgets.QLabel, 'totalLeft')
        self.totalRight= self.findChild(QtWidgets.QLabel, 'totalRight')
        self.f2 = partial(self.model.enableButtons, [self.previewBtn,self.exportBtn, self.displayButton,self.processBtn,  self.videoMenu])

    def LoadVideo(self):
        pixmap = self.model.load_video()
        if pixmap is None: return
        self.model.enableButtons([self.previewBtn, self.displayButton, self.exportBtn, self.processBtn], False)
        pixmap = pixmap.scaled(self.videoPlayer.width(), self.videoPlayer.height(), QtCore.Qt.KeepAspectRatio)
        self.videoPlayer.setPixmap(pixmap)
        self.model.enableButtons(self.previewBtn, True)

    def saveVideo(self):
        self.model.processVideo(self.f2)

    def settings(self):
        self.model.enableButtons([self.displayButton, self.processBtn], False)
        if self.model.settings():
            self.model.enableButtons([self.displayButton, self.processBtn], True)
            pixmap = self.model.update()
            pixmap = pixmap.scaled(self.videoPlayer.width(), self.videoPlayer.height(), QtCore.Qt.KeepAspectRatio)
            self.videoPlayer.setPixmap(pixmap)


    def updateVideoDisplay(self):
        self.model.displayVideo(self.videoPlayer, self.totalLeft, self.totalRight, self.f2)

    def export(self):
        self.model.export(self)

