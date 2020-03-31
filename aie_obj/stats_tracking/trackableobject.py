class TrackableObject:
    def __init__(self, objID, centroids):
        #store obj ID, centroid list of centroids
        self.objID = objID
        self.centroids = [centroids]
        self.dir = ''
        self.entryFrame= 0