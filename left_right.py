import numpy as np
import pandas as pd

class LeftRight():
    def __init__(self, recorder = None, pos_left=0, pos_right =0):
        self.trackableObjects, self.recorder, self.pos_left, self.pos_right = {}, recorder, pos_left, pos_right
        self.trackedObjects = {}
        self.obj_id=0
        self.left = 0
        self.right = 0
    def reset(self):
        self.left = 0
        self.right = 0
        self.trackableObjects = {}

    def setPos(self, l,r):
        self.pos_left, self.pos_right = l,r

    def is_right(self, dir, cur_pos):
        if dir > 0:
            if cur_pos[0] > self.pos_right +10:# and init_x < self.pos_right[0]:
                # if cur_pos[1] > self.pos_right[1] and cur_pos[1] < self.pos_right[1] + self.pos_right[2]:
                return True
        return False

    def is_left(self, dir, cur_pos):
        if dir < 0:
            if cur_pos[0] < self.pos_left -10 :#and init_x > self.pos_left[0]:
                # if cur_pos[1] > self.pos_left[1] and cur_pos[1] < self.pos_left[1] + self.pos_left[2]:
                return True
        return False

    def update(self, objId, centroid, i):
        to = self.trackableObjects.get(objId, None)

        if to is None:
            if centroid[0]< self.pos_left -10:
                return #objId
            elif centroid[0] > self.pos_right +10:
                return #objId
            to = self.recorder(objId, centroid)
            to.entryFrame = i
        else:
            x = [c[0] for c in to.centroids]
            direction = centroid[0] - np.mean(x)
            to.centroids.append(centroid)

            if self.is_right(direction, centroid):
                self.right += 1

                self.updateLeftRight(objId, dir='right')
                return objId
            elif self.is_left(direction, centroid):
                self.left += 1

                self.updateLeftRight(objId, dir='left')
                return objId
        self.trackableObjects[objId] = to

    def updateLeftRight(self, objID, dir=''):

        try:
            to = self.trackableObjects[objID]
            to.dir=dir
            id = objID.split('_')[0]+str(self.obj_id)
            self.trackedObjects[id] = to
            del self.trackableObjects[objID]
            self.obj_id+=1
        except:
            #print(f'')
            bb = 0
    def score(self):
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
            # if to.dir !='':
            distance = 0
            for j in range(1,len(v.centroids)):
                distance += np.linalg.norm(v.centroids[j-1] - v.centroids[j])
            # 60 fps, skipping 5 frames  tp get speed per second then need a pixel measurement
            if distance==0:continue
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
        for i, stats in enumerate(self.stats):
            objs =[]
            for obj in stats[1]:
                self.left_right.updateLeftRight(obj)

            for (obj, centroid) in stats[0].items():
                objID = self.left_right.update(obj, centroid, self.run.n_iter)
                if objID is not None:
                    objs.append(objID)
                self.left, self.right = self.left_right.score()

    def export(self, fn):
        self.left_right.export(fn)
