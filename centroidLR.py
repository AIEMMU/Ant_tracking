from aie_obj.stats_tracking.centroidtracker import *
from nms import *
from scipy.optimize import linear_sum_assignment


class CentroidTrackerLR(CentroidTracker):
    def __init__(self, maxDisappeared=50,maxDistance=50, lpos=0, rpos=0,):
        # print(maxDisappeared,maxDistance)
        super().__init__(maxDisappeared=maxDisappeared, maxDistance=maxDistance)
        self.lpos, self.rpos = lpos,rpos
        self.removed=[]
        self.id='ant'

    def reset(self):
        super().reset()

    def register(self, centroid):
        # when registering an object we use the next available object
        # ID to store the centroid
        # if centroid[0] >=self.lpos and centroid[0]<= self.rpos:
        id = f'{self.id}_{self.nextObjectID}'
        self.objects[id] = centroid
        self.disappeared[id] = 0
        self.nextObjectID += 1

    def setPos(self, lpos, rpos):
        self.lpos, self.rpos = lpos, rpos

    def deregister(self, objectID):
        # to deregister an object ID we delete the object ID from
        # both of our respective dictionaries
        del self.objects[objectID]
        del self.disappeared[objectID]
        self.removed.append(objectID)

    def update(self, rects):  #
        # check to see if the list of input bounding box rectangles
        # is empty
        self.removed = []
        if len(rects) == 0:
            # loop over any existing tracked objects and mark them
            # as disappeared
            for objectID in list(self.disappeared.keys()):
                self.disappeared[objectID] += 1

                # if we have reached a maximum number of consecutive
                # frames where a given object has been marked as
                # missing, deregister it
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)

            # return early as there are no centroids or tracking info
            # to update
            return self.objects, self.removed

        # initialize an array of input centroids for the current frame
        inputCentroids = np.zeros((len(rects), 2), dtype="int")
        ids = ['']*len(rects)
        # loop over the bounding box rectangles
        for (i,((startX, startY, endX, endY), id)) in enumerate(rects):
            # use the bounding box coordinates to derive the centroid
            cX = int((startX + endX) / 2.0)
            cY = int((startY + endY) / 2.0)
            inputCentroids[i] = (cX, cY)
            ids[i] = id

        # if we are currently not tracking any objects take the input
        # centroids and register each of them
        if len(self.objects) == 0:
            for i in range(0, len(inputCentroids)):
                self.id = ids[i]
                self.register(inputCentroids[i])

        # otherwise, are are currently tracking objects so we need to
        # try to match the input centroids to existing object
        # centroids
        else:
            # grab the set of object IDs and corresponding centroids
            objectIDs = list(self.objects.keys())
            objectCentroids = list(self.objects.values())

            # compute the distance between each pair of object
            # centroids and input centroids, respectively -- our
            # goal will be to match an input centroid to an existing
            # object centroid
            D = dist.cdist(np.array(objectCentroids), inputCentroids)
            row_ings, col_inds = linear_sum_assignment(D)
            # in order to perform this matching we must (1) find the
            # smallest value in each row and then (2) sort the row
            # indexes based on their minimum values so that the row
            # with the smallest value as at the *front* of the index
            # list
            # rows = D.min(axis=1).argsort()
            #
            # # next, we perform a similar process on the columns by
            # # finding the smallest value in each column and then
            # # sorting using the previously computed row index list
            # cols = D.argmin(axis=1)[rows]
            # print("hey there sailor", rows,row_ings)
            # print("Hey there sailor 2.0",cols,col_inds)
            #
            # # in order to determine if we need to update, register,
            # # or deregister an object we need to keep track of which
            # # of the rows and column indexes we have already examined
            usedRows = set()
            usedCols = set()

            # loop over the combination of the (row, column) index
            # tuples
            for (row, col) in zip(row_ings, col_inds):
                # if we have already examined either the row or
                # column value before, ignore it
                # val
                if row in usedRows or col in usedCols:
                    continue
                if D[row, col] > self.maxDistance: continue
                # otherwise, grab the object ID for the current row,
                # set its new centroid, and reset the disappeared
                # counter
                objectID = objectIDs[row]
                self.objects[objectID] = inputCentroids[col]
                self.disappeared[objectID] = 0

                # indicate that we have examined each of the row and
                # column indexes, respectively
                usedRows.add(row)
                usedCols.add(col)

            # compute both the row and column index we have NOT yet
            # examined
            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            unusedCols = set(range(0, D.shape[1])).difference(usedCols)

            # in the event that the number of object centroids is
            # equal or greater than the number of input centroids
            # we need to check and see if some of these objects have
            # potentially disappeared
            if D.shape[0] >= D.shape[1]:
                # loop over the unused row indexes
                for row in unusedRows:
                    # grab the object ID for the corresponding row
                    # index and increment the disappeared counter
                    objectID = objectIDs[row]
                    self.disappeared[objectID] += 1

                    # check to see if the number of consecutive
                    # frames the object has been marked "disappeared"
                    # for warrants deregistering the object
                    if self.disappeared[objectID] > self.maxDisappeared:
                        self.deregister(objectID)

            # otherwise, if the number of input centroids is greater
            # than the number of existing object centroids we need to
            # register each new input centroid as a trackable object
            else:
                for col in unusedCols:
                    self.register(inputCentroids[col])

        # return the set of trackable objects
        return self.objects, self.removed