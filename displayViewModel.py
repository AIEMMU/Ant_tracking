from gui_utils import *
from get_library import *
from PyQt5 import QtWidgets
#from Tracker import get_tracker
#from callback_funcs import *
from settingsViewModel import *
from settingsView import *
from gui_threading import *
from progressbar import ProgressBar
import threading
import functools


class DisplayViewModel():
    def __init__(self, enableButtons, getPixmap):
        self.enableButtons, self.getPixmap = enableButtons, getPixmap
        self.threadpool = QThreadPool()

    def load_video(self):
        fn, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select Video", "", "Video Files (*.mp4)")
        if not fn: return
        data = get_db(fn)
        self.tracker = get_tracker(data)
        return self.update()

    def update(self):
        return self.getPixmap(self.tracker.predict_frame(0))

    def settings(self):
        model = SettingsViewModel(self.tracker,getPixmap, selectRegion, get_tfms, get_positions, set_values, getCorners, four_point_transform)
        settings = SettingsWindow(model)
        settings.exec_()
        try:
            if model.lPos is not None:
                self.tracker.left_right.setPos(model.lPos, model.rPos)
                return True
        except:
            print("No positions available for tracker")
        return False


    def displayVideo(self, v,l,r, completed):
        stats = GuiFrame_Stats(v, l, r, self.getPixmap, completed)
        stats.completed=False
        func = partial(self.execute_this_fn, stats)

        worker = Worker(func)  # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.callback)
        self.threadpool.start(worker)
        return True

    #multithreading
    def execute_this_fn(self, stats, progress_callback):
        progress_callback.emit(stats)
        # self.tracker.fit(cbs=[test(stats), DrawIDMulti()])
        print("Hey")
        self.tracker.fit(cbs=[yeild_frame_stats(stats),  DrawIDMulti()])
        stats.completed=True
        return "DONE"

    def print_output(self, s):
        print(f"HEY {s}")

    def callback(self, n ):
        print(f"Hey{n}")

    def thread_complete(self):
        print("THREAD COMPLETE!")

    # def processVideo(self, f2):
    #     f2(False)
    #     fn, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save output", "", "Video Files (*.mp4)")
    #     if fn=='':
    #         f2(True)
    #         return False
    #     pb = ProgressBar()
    #     progress = Progress(pb, QApplication.processEvents)
    #     progress.x = 0
    #     self.tracker.fit( cbs = [
    #         VidWriterCallback(VidWriter(fn, self.tracker.frame.shape[1], self.tracker.frame.shape[0])),
    #         yeild_progression(progress), DrawScores(), DrawIDMulti()])
    #     pb.close()
    #     f2(True)
    #     return True

    def export(self, vm):
        fn, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save output csv file", "", "Csv Files (*.csv)")
        if fn=='': return
        try:
            self.tracker.left_right.export(fn)
            QMessageBox.information(vm, "Message", "Results have been exported")
        except:
            QMessageBox.information(vm, "Message", "There were no results to export")


