import numpy as np
import pandas as pd

class LeftRight():
    def __init__(self, recorder = None, pos_left=0, pos_right =0):
        self.trackableObjects, self.recorder, self.pos_left, self.pos_right = {}, recorder, pos_left, pos_right
        self.left = 0
        self.right = 0

    def reset(self):
        self.left = 0
        self.right = 0
        self.trackableObjects = {}
    def setPos(self, l,r):
        self.pos_left, self.pos_right = l,r
    def is_right(self, dir, cur_x, init_x):

        if dir > 0 and cur_x > self.pos_right and init_x < self.pos_right:
            self.right+=1
            return True
        return False

    def is_left(self, dir, cur_x, init_x):
        if dir < 0 and cur_x < self.pos_left and init_x > self.pos_left:
            self.left+=1
            return True
        return False

    def update(self, objId, centroid, i):
        to = self.trackableObjects.get(objId, None)
        if to is None:
            to = self.recorder(objId, centroid)
            to.entryFrame = i
        else:
            x = [c[0] for c in to.centroids]
            direction = centroid[0] - np.mean(x)
            to.centroids.append(centroid)
            if not to.counted:
                if self.is_right(direction, centroid[0], x[0]):
                    to.counted = True
                    to.dir = 'right'
                elif self.is_left(direction, centroid[0], x[0]) :
                    to.counted = True
                    to.dir = 'left'
            # elif to.counted:
            #     if self.is_right(direction, centroid[0], x[0]) and to.dir is not 'right':
            #         to.counted = True
            #         to.dir = 'right'
            #     elif self.is_left(direction, centroid[0], x[0])  and to.dir is not 'left' :
            #         to.counted = True
            #         to.dir = 'left'

        self.trackableObjects[objId] = to
        return self.left, self.right

    def export(self, fn):
        ids = []
        x = []
        y = []
        dir = []
        entryFrame = []
        for k, v in self.trackableObjects.items():
            if v.counted:
                ids.append(k)
                points = np.array(v.centroids).T
                dir.append(v.dir)
                entryFrame.append(v.entryFrame)
                x.append(points[0])
                y.append(points[1])

        df = pd.DataFrame({'id': ids, 'cx': x, 'cy': y, 'entryFrame': entryFrame, 'dir': dir})
        df.to_pickle(fn)

from aie_obj.obj_tracker.callbacks import *
class LeftRightCallback(Callback):
    _order = 1

    def __init__(self, left_right):
        self.left_right = left_right
        self.left, self.right = 0, 0

    def begin_fit(self):
        self.left, self.right=0,0
        self.left_right.reset()

    def setPos(self, l,r):
        self.left_right.setPos(l,r)

    def after_obj_tracker(self):
        for obj, centroid in self.run.stats.items():
            self.left, self.right = self.left_right.update(obj, centroid, self.run.n_iter)

    def export(self, fn):
        self.left_right.export(fn)
