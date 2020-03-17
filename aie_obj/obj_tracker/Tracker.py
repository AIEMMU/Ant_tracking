from .callback_funcs import *
from typing import *

def listify(o):
    if o is None: return []
    if isinstance(o, list): return o
    if isinstance(o, str): return [o]
    if isinstance(o, Iterable): return list(o)
    return [o]

def setify(o): return o if instance(o,set) else set(listify(0))

class Tracker():

    def __init__(self, obj_tracker, data, stats_tracker=None, cbs=None, cb_funcs=None):

        self.data = data
        self.obj_tracker = obj_tracker
        self.stats_tracker = stats_tracker
        self.cbs = []
        self.add_cb(FitStartCallBack())
        self.add_cbs(cbs)
        self.add_cbfs(cb_funcs)
        self.n_iter = 0

    def add_cbfs(self, cb_funcs):
        self.add_cbs(cbf() for cbf in listify(cb_funcs))

    def add_cbs(self, cbs):
        for cb in listify(cbs): self.add_cb(cb)

    def add_cb(self, cb):
        cb.set_runner(self)
        setattr(self, cb.name, cb)
        self.cbs.append(cb)

    def remove_cbs(self, cbs):
        for cb in listify(cbs): self.cbs.remove(cb)

    def predict_frame(self, i):
        self.predict(self.data.video_ds[i])
        return self.frame

    def get_pred(self):
        preds=[]
        return [element for lis in [pred(self.frame.copy()) for pred in listify(self.obj_tracker)] for element in lis]
        # for pred in listify(self.obj_tracker):
        #     preds = preds+pred(self.frame.copy())
        # return preds

    def predict(self, frame):
        try:
            if frame is not None:
                self.frame = frame;
                self('begin_pred')

                self.pred = self.get_pred()
                self('after_pred')
                if self.stats_tracker is not None:
                    self.stats = self.stats_tracker.update(self.pred)
                self('after_obj_tracker')
        except CancelPredictionException:
            self('after_cancel_pred')
        finally:
            self('after_tracking')

    def all_frames(self, dl):
        self.iters = len(dl.ds)
        try:
            for frame in dl: self.predict(frame)
        except CancelFitException:
            self('after_cancel_fit')

    def fit(self, cbs=None):
        self.add_cbs(cbs)

        try:
            for cb in self.cbs: cb.set_runner(self)
            self('begin_fit')
            if not self('begin_tracking'): self.all_frames(self.data.video_dl)

        except CancelLoopException:
            self('after_cancel_Loop')
        finally:
            self('after_fit')
            self.remove_cbs(cbs)

    def __call__(self, cb_name):
        res = False
        for cb in sorted(self.cbs, key=lambda x: x._order): res = cb(cb_name) or res
        return res


