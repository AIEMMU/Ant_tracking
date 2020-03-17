from aie_obj.stats_tracking.centroidtracker import CentroidTracker

class CentroidTrackerLR(CentroidTracker):
    def __init__(self, maxDisappeared=50,maxDistance=50, lpos=0, rpos=0,):
        super().__init__(maxDisappeared=maxDisappeared, maxDistance=maxDistance)
        self.lpos, self.rpos = lpos,rpos


    def reset(self):
        super().reset()

    def register(self, centroid):
        # when registering an object we use the next available object
        # ID to store the centroid
        if centroid[0] <=self.lpos or centroid[0]>= self.rpos: return

        self.objects[self.nextObjectID] = centroid
        self.disappeared[self.nextObjectID] = 0
        self.nextObjectID += 1

    def setPos(self, lpos, rpos):
        self.lpos, self.rpos = lpos, rpos
