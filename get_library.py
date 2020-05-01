from aie_obj.obj_tracker.datablock import get_db
from aie_obj.obj_tracker.Tracker import Tracker
from aie_obj.obj_tracker.obj_tracker import obj_tracker
from aie_obj.obj_tracker.callback_funcs import *
from centroidLR import CentroidTrackerLR
from aie_obj.stats_tracking.trackableobject import TrackableObject
from image_processor import *

from functools import partial
from selectCorners import four_point_transform
from left_right import *

def get_ant_tracker():
    # return obj_tracker([cv2.pyrDown,brightness,   adaptThreshold, getContours, partial(get_centroids_pyrdown, id='ant')])
    return obj_tracker([ cv2.pyrDown,brightness, adaptThreshold,addBorder, getContours, partial(get_centroids_pyrdown,min_value=10)])

def get_leaf_tracker():
    return obj_tracker([cv2.pyrDown, make_hsv, color_mask,addBorder, getContours, partial(get_centroids_pyrdown, min_value=50, max_value = 500)])

def get_tracker(data):
    h,w = data.video_ds[0].shape[:2]
    lr = partial(LeftRightCallback, LeftRight(TrackableObject, 0, 0))
    return Tracker([get_ant_tracker(),get_leaf_tracker()], data,stats_tracker=[CentroidTrackerLR(maxDisappeared=10, id='ant'), CentroidTrackerLR(maxDisappeared=10, id='leaf')],
                   cbs=[DrawRectMutli(), WarpFrame([0, 0, w, h], four_point_transform),BlackBorderCallback()], cb_funcs=lr)