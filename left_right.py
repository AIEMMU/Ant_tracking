import numpy as np
import pandas as pd

class LeftRight():
    def __init__(self, recorder = None, pos_left=[], pos_right =[]):
        self.trackableObjects, self.recorder, self.pos_left, self.pos_right = {}, recorder, pos_left, pos_right
        self.trackedObjects = {}
        self.left = 0
        self.right = 0

    def reset(self):
        self.left = 0
        self.right = 0
        self.trackableObjects = {}

    def setPos(self, l,r):
        self.pos_left, self.pos_right = l,r

    def is_right(self, dir, cur_pos, init_x, init_y):

        if dir > 0:
            if cur_pos[0] > self.pos_right[0] and init_x < self.pos_right[0]:
                if cur_pos[1] > self.pos_right[1] and cur_pos[1] < self.pos_right[1] + self.pos_right[2]:
                    return True
        return False

    def is_left(self, dir, cur_pos, init_x, init_y):
        if dir < 0:
            if cur_pos[0] < self.pos_left[0] and init_x > self.pos_left[0]:
                if cur_pos[1] > self.pos_left[1] and cur_pos[1] < self.pos_left[1] + self.pos_left[2]:
                    return True
        return False

    def update(self, objId, centroid, i):
        to = self.trackableObjects.get(objId, None)

        if to is None:
            to = self.recorder(objId, centroid)
            to.entryFrame = i
        else:
            x = [c[0] for c in to.centroids]
            y = [c[1] for c in to.centroids][-1]
            direction = centroid[0] - np.mean(x)
            to.centroids.append(centroid)

            if self.is_right(direction, centroid, x[0], y):
                to.dir = 'right'
                to.in_space+=1
            elif self.is_left(direction, centroid, x[0], y):
                to.dir = 'left'
                to.in_space += 1
        self.trackableObjects[objId] = to

    def updateLeftRight(self, objID):
        to = self.trackableObjects[objID]
        if to.dir != '':
            if to.dir=='right':
                self.right+=1
            elif to.dir=='left':
                self.left +=1

        self.trackedObjects[objID] = to
        del self.trackableObjects[objID]
        return self.left, self.right

    def export(self, fn):
        ids = []
        x = []
        y = []
        dir = []
        distances = []
        speeds = []
        entryFrame = []
        for k, v in self.trackedObjects.items():
            distance = 0
            for j in range(1,len(v.centroids)):
                distance += np.linalg.norm(v.centroids[j-1] - v.centroids[j])
            # 60 fps, skipping 10 frames  tp get speed per second then need a pixel measurement
            speed = distance/((len(v.centroids)*5) / 60.)
            distances.append(distance)
            speeds.append(speed)
            ids.append(k)
            points = np.array(v.centroids).T
            dir.append(v.dir)
            entryFrame.append(v.entryFrame)
            x.append(points[0])
            y.append(points[1])

        df = pd.DataFrame({'id': ids, 'cx': x, 'cy': y, 'entryFrame': entryFrame, 'dir': dir, 'distance': distances, 'speed': speeds})
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
        for (obj, centroid) in self.run.stats[0].items():
            self.left_right.update(obj, centroid, self.run.n_iter)

        for obj in self.run.stats[1]:
            self.left, self.right = self.left_right.updateLeftRight(obj)

    def export(self, fn):
        self.left_right.export(fn)
