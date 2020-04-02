from gui_utils import *
from PyQt5 import QtWidgets
from selectCorners import *

class SettingsViewModel():
    def __init__(self,tracker, getPixmap, selectRegion, get_tfms, get_pos, set_values, getCorners, four_transform):
         self.getPixmap, self.selectRegion = getPixmap, selectRegion
         self.get_tfms, self.get_pos, self.set_values =get_tfms, get_pos, set_values
         self.get_corners = getCorners
         self.tracker = tracker
         self.four_transform = four_transform
         self.orig_h, self.orig_w = tracker.data.video_ds[0].shape[:2]
         self.tracker.warp_frame.reset(np.array([0, 0, self.orig_w, self.orig_h]))
         self.tracker.draw_bounding_boxes.setPos([0,0,0],[self.orig_w,0,0])

    def get_length(self):
        return len(self.tracker.data.video_dl.ds)

    def get_pixmap(self, i):
        self.i = i
        return self.getPixmap(self.tracker.predict_frame(i))

    def updateFrame(self,):
        self.tracker.stats_tracker.reset()
        return self.getPixmap(self.tracker.predict_frame(self.i))

    def updateLayers(self, settings):
        ant,leaf = self.get_tfms(settings)
        self.tracker.obj_tracker[0].layers= ant
        self.tracker.obj_tracker[1].layers = leaf

    def selectCrop(self,):
        self.reset()
        p = self.get_corners(self.tracker.frame.copy())
        self.tracker.warp_frame.setPos(p)
        self.updateFrame()

        return self.updateFrame()

    def adjustROI(self, m):
        self.lPos = (self.lPos - m[0])
        self.rPos = self.rPos - m[0]
        self.tracker.draw_bounding_boxes.setPos([0, 0, 0], [self.orig_w, 0, 0])

    def selectROI(self, ):
        m = self.selectRegion(self.tracker.frame.copy(), 2)
        self.lPos, self.rPos  = self.get_pos(m)
        self.tracker.draw_bounding_boxes.setPos(self.lPos, self.rPos)
        self.tracker.left_right.setPos(self.lPos, self.rPos)
        self.tracker.stats_tracker.setPos(self.lPos, self.rPos)
        return self.updateFrame()

    def reset(self):
        self.lPos = None
        self.rPos = None
        self.tracker.stats_tracker.reset()
        self.tracker.draw_bounding_boxes.setPos([0, 0, 0], [self.orig_w, 0, 0])
        self.tracker.warp_frame.reset([0, 0, self.orig_w, self.orig_h])

        return self.updateFrame()

