from .callbacks import *
import cv2
import numpy as np

def draw_text(frame, text, pos, color=(0,0,255), font_scale=0.6,line_thickness=2):
    return cv2.putText(frame, text, pos,cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, line_thickness)

def draw_rect(frame, startPos, endPos, color=(0,255,0), line_thickness=2):
    return cv2.rectangle(frame, startPos, endPos, color, line_thickness)

def draw_line(frame, startPos, endPos, color=(0,255,0), line_thickness=2):
    return cv2.line(frame, startPos, endPos, color, line_thickness)
def draw_circle(frame, pos, radius=4, color = (0, 0, 255), fillMode = -1):
    return cv2.circle(frame, pos, radius, color, fillMode)

class FitStartCallBack(Callback):

    def begin_fit(self):
        self.run.n_iter = 0
        if self.run.stats_tracker is not None:
            self.run.reset()

    def after_pred(self):
        self.run.n_iter += 1


class VidWriter():
    def __init__(self, fn, w, h): self.fn, self.w, self.h, self.video_writer = fn, w, h, None

    def create_video(self):
        self.video_writer = cv2.VideoWriter(self.fn, -1, 30, (self.w, self.h), True)

    def close_video(self):
        self.video_writer.release()

    def write_to_video(self, frame):
        self.video_writer.write(frame)


class VidWriterCallback(Callback):
    _order = 1

    def __init__(self, vw):
        self.vw = vw

    def begin_tracking(self):
        self.vw.create_video()

    def after_fit(self):
        self.vw.close_video()

    def after_tracking(self):
        self.vw.write_to_video(self.run.frame)

class DrawRect(Callback):
    _order=-1
    def after_pred(self):
        [draw_rect(self.run.frame, (c[:2]), (c[2:]), (0,255,0), 2) for c in self.run.pred]

class DrawRectMutli(Callback):
    _order=-1
    def after_pred(self):
        for pred in self.run.pred:
            [draw_rect(self.run.frame, (c[:2]), (c[2:]), (0, 255, 0), 2) for c in pred]



class DrawVerticalLines(Callback):
    _order=1
    def __init__(self,x,x2):
        self.x = x
        self.x2 = x2

    def setPos(self, x,x2):
        self.x = x
        self.x2 = x2
    def after_pred(self):
        draw_line(self.run.frame, (self.x,0), (self.x, self.run.frame.shape[0]))
        draw_line(self.run.frame, (self.x2, 0), (self.x2, self.run.frame.shape[0]))

class DrawBoundingBoxes(Callback):
    _order=1
    def __init__(self,x,x2):
        self.x = x
        self.x2 = x2

    def setPos(self, x,x2):
        self.x = x
        self.x2 = x2

    def after_pred(self):
        draw_rect(self.run.frame, (0, self.x[1]), (self.x[0], self.x[1]+self.x[2]))
        draw_rect(self.run.frame, (self.x2[0], self.x2[1]), (self.x2[0]+self.run.frame.shape[0], self.x2[1]+self.x2[2]))

class DrawID(Callback):
    _order=2
    def after_pred(self):
        for obj, centroid in self.run.stats.items():
            text = f'ID {obj}'
            draw_text(self.run.frame, text, (centroid[0]-10, centroid[1]-10))
            draw_circle(self.run.frame, (centroid[0], centroid[1]))

class DrawIDMulti(Callback):
    _order=2
    def after_pred(self):
        for stats in self.stats:
            for obj, centroid in stats[0].items():
                text = f'{obj}'
                draw_text(self.run.frame, text, (centroid[0]-10, centroid[1]-10))
                draw_circle(self.run.frame, (centroid[0], centroid[1]))

class BlackBorderCallback(Callback):
    _order = 3
    def __init__(self):
        self.p = 0.01
    def setPercent(self, p):
        self.p = p
    def after_pred(self):
        h = self.run.frame.shape[0]
        rh = int(h * self.p)
        self.run.frame[:, 0:rh] = 0
        self.run.frame[:, -rh:] = 0

class CropFrame(Callback):
    _order=1
    def setCrop(self, crop):
        if self.x > 0 and self.y > 0 and crop[0] >0 and crop[1] >0:

            self.x += crop[0]
            self.y += crop[1]
            self.w, self.h = crop[2:]
        else:
            self.x, self.y, self.w, self.h = crop

    def __init__(self, crop):
        self.x, self.y, self.w, self.h = crop

    def begin_pred(self):
        self.run.frame = self.run.frame[self.y:self.y+self.h,self.x:self.x+self.w]

class WarpFrame(Callback):
    _order=1
    def setPos(self, pos):
       self.pos = pos

    def __init__(self, pos, warp):
        self.pos = np.array([[pos[0],pos[1]],[pos[2],pos[1]],[pos[2],pos[3]],[pos[0],pos[3]]])
        self.warp = warp
    def reset(self, pos):
        self.pos = np.array([[pos[0], pos[1]], [pos[2], pos[1]], [pos[2], pos[3]], [pos[0], pos[3]]])
    def begin_pred(self):
        self.run.frame = self.warp(self.run.frame, self.pos.reshape(4,2))


class DrawScores(Callback):
    _order=4
    def after_pred(self):
        info = [
            ("Right", self.run.left_right.right),
            ("Left", self.run.left_right.left),
        ]
        for j, (k, v) in enumerate(info):
            text = f'{k}: {v}'
            draw_text(self.run.frame, text, (10,10 + ((j * 20) + 20)))

class yeild_frame_stats(Callback):
    _order=3
    def __init__(self,stats):
        self.stats = stats

    def after_pred(self):
        self.stats.frame = self.run.frame
        self.stats.tL = self.run.left_right.left
        self.stats.tR = self.run.left_right.right

class test(Callback):
    _order=3
    def __init__(self,stats):
        self.stats = stats

    def after_pred(self):
        self.stats.frame = self.run.frame

class yeild_progression(Callback):
    _order=1
    def __init__(self,progress):
        self.progress = progress
    def after_pred(self):
        self.progress.x = (self.run.n_iter / self.run.iters)*100