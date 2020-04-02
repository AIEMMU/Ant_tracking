import cv2

def get_video(path):
    vid = cv2.VideoCapture(path)
    return vid

class Dataset():
    def __init__(self, x): self.x = x
    def __len__(self): return int(self.x.get(cv2.CAP_PROP_FRAME_COUNT))
    def __getitem__(self,i):
        self.x.set(cv2.CAP_PROP_POS_FRAMES, i)
        return self.read()
    def read(self):
        _,frame = self.x.read()
        return frame

class DataLoader:
    def __init__(self, ds): self.ds = ds
    def __iter__(self):
        self.ds[0]
        for i in range(len(self.ds)): yield self.ds.read()

class DataLoader_skip:
    def __init__(self, ds, skip=4): self.ds, self.skip = ds,skip
    def __iter__(self):
        self.ds[0]
        for i in range(len(self.ds)):
            frame =  self.ds.read()
            if i % self.skip!=0:continue
            yield frame

class DataBunch():
    def __init__(self, video_dl):
        self.video_dl = video_dl

    @property
    def video_ds(self): return self.video_dl.ds

def get_db(fn, **kwargs):
    return DataBunch(DataLoader_skip(Dataset(get_video(fn)),5))
