from PyQt5 import QtWidgets, uic, QtCore

class SettingsWindow(QtWidgets.QDialog):
    def __init__(self,model):
        self.model = model

        super(SettingsWindow, self).__init__() #call the inherited class __init__ method
        uic.loadUi("settings.ui", self) # load teh UI file

        self.videoPlayer = self.findChild(QtWidgets.QLabel, 'videoPlayer')
        self.videoPlayer.setAlignment(QtCore.Qt.AlignCenter)

        self.videoSlider = self.findChild(QtWidgets.QSlider, f'videoSlider')
        self.videoSlider.valueChanged.connect(self.sliderChanged)
        self.videoSlider.setMaximum(self.model.get_length())

        self.selectROI = self.findChild(QtWidgets.QPushButton, f'selectROI')
        self.selectROI.clicked.connect(self.roiSelection)

        self.selectROI = self.findChild(QtWidgets.QPushButton, f'selectCrop')
        self.selectROI.clicked.connect(self.cropSelection)

        self.selectROI = self.findChild(QtWidgets.QPushButton, f'resetButton')
        self.selectROI.clicked.connect(self.reset)

        self.sliders = self.model.set_values(self.findChild)
        [slider.valueChanged.connect(self.sliderChanged)for slider in self.sliders]

        self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, f'buttonBox')
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.cancel)
        pixmap = self.model.get_pixmap(0)
        pixmap = pixmap.scaled(self.videoPlayer.width(), self.videoPlayer.height(), QtCore.Qt.KeepAspectRatio)
        self.videoPlayer.setPixmap(pixmap)

    def reset(self):
        pixmap = self.model.reset()
        self.set_pixmap(pixmap)
        self.sliders = self.model.set_values(self.findChild)

    def cancel(self):
        self.model.reset()
        self.reset()

    def get_sliderSettings(self):
        return [s.value() for s in self.sliders]

    def cropSelection(self):
        pixmap = self.model.selectCrop()
        self.set_pixmap(pixmap)

    def roiSelection(self):
        pixmap = self.model.selectROI()
        self.set_pixmap(pixmap)

    def sliderChanged(self):
        settings = self.get_sliderSettings()
        print(settings)
        self.model.updateLayers(settings)
        pixmap = self.model.get_pixmap(self.videoSlider.value())
        self.set_pixmap(pixmap)

    def set_pixmap(self, pixmap):
        if pixmap is None: return
        pixmap = pixmap.scaled(self.videoPlayer.width(), self.videoPlayer.height(), QtCore.Qt.KeepAspectRatio)
        self.videoPlayer.setPixmap(pixmap)