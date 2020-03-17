import numpy as np
from image_processor import *
def order_points(pts):
    #intialise a list of coordinates that will be ordered such
    #that the first entry is the left corner then right, then bot etc.

    rect = np.zeros((4,2), dtype="float32")
    #top left will have the smallest sum
    #bottom left is larget sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    #compute the diff between points
    # top right will have the smallest differnce
    # whereas bottom left will have the largest
    s= np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(s)]
    rect[3] = pts[np.argmax(s)]

    return rect

def four_point_transform(image, pts):
    #obtain a consistent order of points and unpack them individually
    rect = order_points(pts)
    (tl,tr,br,bl) = rect

    #compute the width of the new image which will be
    #maximum distance between the bottom left and bottom right
    widthA = np.sqrt((br[0]-bl[0])**2 + ((br[1]-bl[1])**2))
    widthB = np.sqrt((tr[0]-tl[0])**2 + ((tr[1]-tl[1])**2))

    maxWidth = max(int(widthA),int(widthB))

    #compute the height of the new image which will be
    #maximum distance between the top left and bottom left
    heightA = np.sqrt((tr[0]-br[0])**2 + ((tr[1]-br[1])**2))
    heightB = np.sqrt((tl[0]-bl[0])**2 + ((tl[1]-bl[1])**2))

    maxHeight = max(int(heightA),int(heightB))

    #now that we have the dimensions of the new iamge
    #we construct the set of destination points to obtain a birds
    # eye view
    dst = np.array([[0,0], [maxWidth-1,0], [maxWidth-1,maxHeight-1], [0,maxHeight-1]], dtype="float32")

    #compute the perspective warp matrix
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped

class SelectCorner:
    def __init__(self):
        self.pos = []

    def select_corner_function(self, event, x,y,flags, params):

        if event ==cv2.EVENT_LBUTTONUP:
            self.addCorner(x,y)
        if event ==cv2.EVENT_RBUTTONUP:
            self.removeCorner()

    def addCorner(self,x,y):
        if len(self.pos)>=4:return
        self.pos.append((x,y))
    def removeCorner(self):
        if len(self.pos)>0:
            self.pos.pop(-1)
    def reset(self):
        self.pos = []


def getCorners(img, w=None,h=None, select = SelectCorner()):
    select.pos = []
    img = cv2.resize(img, (img.shape[1]//2,img.shape[0]//2))
    cv2.namedWindow("Select Windows")
    cv2.setMouseCallback("Select Windows", select.select_corner_function)

    while(True):
        frame = img.copy()
        if len(select.pos) > 0:
            for p in select.pos:
                draw_circle (frame, p)
        if len(select.pos) > 1:
            for i in range(1,len(select.pos)):
                draw_line(frame,select.pos[i-1], select.pos[i])
        if len(select.pos) == 4:
            draw_line(frame, select.pos[-1], select.pos[0])

        cv2.imshow("Select Windows", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('r'):
            select.reset()

        if len(select.pos)==4 and key==13:
            break
    cv2.destroyAllWindows()
    return np.array(select.pos) *2
#
# import argparse
# ap = argparse.ArgumentParser()
# ap.add_argument('-i',"--image", required=True,help="path to image")
# args = vars(ap.parse_args())
# if __name__ == "__main__":
#     img = cv2.imread(args['image'])
#     p = getCorners(img)
#     print(p)
#     paper = four_point_transform(img, p.reshape(4,2))
#     cv2.imshow("paper", paper)
#     cv2.waitKey(0)