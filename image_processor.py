import cv2

def make_bgr(x): return cv2.cvtColor(x, cv2.COLOR_LAB2BGR)
def make_lab(x): return cv2.cvtColor(x, cv2.COLOR_BGR2LAB)
def make_gray(x): return cv2.cvtColor(x, cv2.COLOR_BGR2GRAY)
def make_hsv(x): return cv2.cvtColor(x, cv2.COLOR_BGR2HSV)
def gaussian_blur(x, k=(5,5)): return cv2.GaussianBlur(x, k, 0)

def color_mask(x, lower=(36, 25, 25), upper=(86, 255, 255)):
    mask =cv2.inRange(x, lower, upper)
    return mask
#
def draw_text(frame, text, pos, color=(0,0,255), font_scale=0.6,line_thickness=2):
    return cv2.putText(frame, text, pos,cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, line_thickness)

def draw_rect(frame, startPos, endPos, color=(0,255,0), line_thickness=2):
    return cv2.rectangle(frame, startPos, endPos, color, line_thickness)

def draw_line(frame, startPos, endPos, color=(0,255,0), line_thickness=2):
    return cv2.line(frame, startPos, endPos, color, line_thickness)
def draw_circle(frame, pos, radius=4, color = (0, 0, 255), fillMode = -1):
    return cv2.circle(frame, pos, radius, color, fillMode)
def bb(c):
    x,y,w,h = cv2.cv2.boundingRect(c)
    return (x,y,x+w,y+h)

def getArea(c): return cv2.contourArea(c)

def get_centroids(contours, min_value=100, max_value=500,):
    centroids = []
    for c in contours:
        area = getArea(c)
        if area >= min_value and area <=max_value:
            centroids.append(bb(c))
    return centroids

def get_centroids_pyrdown(contours, min_value=100, max_value=500,id=None):
    centroids = []
    for c in contours:
        area = getArea(c)
        if area >= min_value and area <=max_value:
            if id is not None:
                centroids.append((bb(c*2), id))
            else:
                centroids.append(bb(c * 2))
    return centroids

def get_centroids_pyrdown_no_area(contours, min_value=50, id=None):
    centroids = []
    for c in contours:
        area = getArea(c)
        if area >= min_value:
            centroids.append(bb(c*2))
    if id is not None:
        ids = [id]* len(centroids)
        ids = [id]* len(centroids)
        return centroids, ids
    return centroids

def clahe(img, clipLimit=2., tileGridSize= (8,8)):
    tileGridSize = (tileGridSize,tileGridSize) if isinstance(tileGridSize, int) else tuple(tileGridSize)
    lab = make_lab(img)
    lab_planes = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=tileGridSize)
    lab_planes[0] = clahe.apply(lab_planes[0])
    lab = cv2.merge(lab_planes)
    return make_bgr(lab)

def adaptThreshold(img,blurSize=(5,5),thresh= 255, block_size=51, offset=20 ):
    blurSize = (blurSize, blurSize) if isinstance(blurSize, int) else tuple(blurSize)
    fgMask = cv2.blur(img.copy(), blurSize)
    fgMask = make_gray(fgMask)
    return cv2.adaptiveThreshold(fgMask, thresh, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, block_size,
                                   offset)

def getContours(img):
        _,contours, _=cv2.findContours(img.copy(), cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE )
        return contours




