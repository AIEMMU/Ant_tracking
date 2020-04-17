from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QImage, QPixmap
import cv2
from typing import *
import numpy as np
from functools import partial
from image_processor import *

class Progress:
    def __init__(self, pb, f):
        self._x = 0
        self.pb = pb
        self.f = f
    @property
    def x(self):
        "this method runs whenever you try to access self.x"
        return self._x
    @x.setter
    def x(self, value):
        "this method runs whenever you try to set x"
       # print(f"Setting x to value {value}")
        self._x = value
        self.pb.setValue(self._x)
        self.f()


class GuiFrame_Stats:
    def __init__(self, videoPlayer, totalLeft, totalRight, f, f2):
        self._frame, self._tL, self._tR, self._completed = None, None, None, False
        self.videoPlayer, self.totalLeft, self.totalRight, self.f, self.f2 = videoPlayer, totalLeft, totalRight,f, f2
    @property
    def completed(self):
        return self._frame

    @completed.setter
    def completed(self, value):
        self.f2(value)
    @property
    def frame(self):
        "this method runs whenever you try to access self.x"
        return self._frame

    @frame.setter
    def frame(self, value):
        "this method runs whenever you try to set x"
        #print(f"Setting x to value {value}")
        pixmap = self.f(value)
        if pixmap is None: return
        pixmap = pixmap.scaled(self.videoPlayer.width(), self.videoPlayer.height(), QtCore.Qt.KeepAspectRatio)
        self.videoPlayer.setPixmap(pixmap)

    @property
    def tL(self):
        "this method runs whenever you try to access self.x"
        return self._tL

    @tL.setter
    def tL(self, value):
        "this method runs whenever you try to set x"
        self.totalLeft.setText(f'{value}')

    @property
    def tR(self):
        "this method runs whenever you try to access self.x"
        return self._tL

    @tR.setter
    def tR(self, value):
        "this method runs whenever you try to set x"
        self.totalRight.setText(f'{value}')


def listify(o):
    if o is None: return []
    if isinstance(o, list): return o
    if isinstance(o, str): return [o]
    if isinstance(o, Iterable): return list(o)
    return [o]

def setify(o): return o if instance(o,set) else set(listify(0))

def getPixmap(frame):
    if frame is None: return
    h, w, c = frame.shape
    bytes_per_line = c * w
    image = QImage(np.array(frame), w, h, c*w, QImage.Format_RGB888).rgbSwapped()
    pixmap = QPixmap(image)
    return pixmap

def enableButtons(btns, enable):
    for btn in listify(btns):
        btn.setEnabled(enable)

def selectRegion(frame, num):

    h,w = frame.shape[:2]
    frame = cv2.resize(frame, (w//2, h//2))
    fromCenter = False
    showCrosshair = False
    rects = []

    while True:
        # draw bounding boxes over objects
        # selectROI's default behaviour is to draw box starting from the center
        # when fromCenter is set to false, you can draw box starting from top left corner
        bbox = cv2.selectROI('Select Places to track from', frame, fromCenter, showCrosshair)
        x,y,w,h = bbox
        if bbox is None: break

        cv2.rectangle(frame, (x,y), (x+w,y+h), (0, 255, 0), 2)
        bb = (int(x * 2), int(y * 2), int(w * 2), int(h * 2))
        rects.append(bb)
        if len(rects) == num: break

    cv2.destroyAllWindows()
    return rects

def get_tfms(settings):
    if settings[2] %2==0: settings[2]+=1
    f1 = cv2.pyrDown
    f2 = partial(adaptThreshold, blurSize=settings[0],thresh = settings[1], block_size =settings[2], offset = settings[3] )
    f3 = partial(get_centroids_pyrdown, min_value=settings[4], max_value = settings[5])

    f4 = partial(get_centroids_pyrdown, min_value=settings[6], max_value=settings[7])

    return [f1,brightness, f2,addBorder, getContours,f3], [f1,make_hsv, color_mask,addBorder,getContours,f4]

def get_pos(m):
    if m[0][0] < m[1][0]:

        lPos = [m[0][0] + m[0][2], m[0][1], m[0][3]]
        rPos = [m[1][0],  m[1][1], m[1][3]]
    else:

        rPos = [m[0][0] + m[0][2], m[0][1], m[0][3]]
        lPos = [m[1][0] ,  m[1][1], m[1][3]]
    return lPos, rPos

def get_positions(p, size):
     rh = int(size[0] * p)
     return rh, size[1]-rh

def set_values(f):
    names = [ 'blurSize', 'thresh', 'blockSize', 'offset', 'minArea', 'maxArea','minArea_2', 'maxArea_2']
    values = [ 5, 255, 51, 1, 10, 500,50, 500]
    max = [ 15, 255, 100, 100, 499, 1000, 499, 2000]

    sliders = [set_sliders(f ,n, v, mv) for n, v, mv in zip(names, values, max)]
    sliders[-3].setMinimum(500)
    sliders[-1].setMinimum(500)
    sliders[2].setMinimum(3)
    return sliders

def set_sliders( f, name, value, max_value):
    slider = f(QtWidgets.QSlider, name)
    slider.setMaximum(max_value)
    slider.setValue(value)
    slider.setMinimum(1)
    return slider