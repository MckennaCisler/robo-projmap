import sys
from time import sleep
import numpy as np
import cv2

if sys.version_info[0] == 2:  # Just checking your Python version to import Tkinter properly.
    from Tkinter import *
else:
    from tkinter import *

from PIL import Image
from PIL import ImageTk



class DrawingWindow:
    def __init__(self):
        self.last_kinect_frame = np.zeros([1080, 1920, 3], dtype=np.float32)
        self.drawing = np.zeros([1080, 1920], dtype=np.float32)
        self.tk = Tk()
        self.tk.geometry('%dx%d+%d+%d' % (1920 / 2, 1080 / 2, 0, 0))
        self.frame = Canvas(self.tk)
        self.frame.configure(background='black', highlightthickness=0)
        self.frame.pack(fill='both', expand=True)
        self.frame.bind('<B1-Motion>', self.left_drag)

        self.circles = []

    # def __del__(self):
    #     self.close()

    def close(self):
        self.tk.destroy()

    def left_drag(self, event):
        print(event)
        cv2.circle(self.drawing, (event.x * 2, event.y * 2), 15, 1.0, -1)
        self.circles.append((event.x * 2, event.y * 2))

    def update(self):
        self.frame.delete('all')

        print('deleted')
        draw_expanded = np.expand_dims(self.drawing, -1)
        self.combined = draw_expanded * 255 + (1 - draw_expanded) * self.last_kinect_frame
        print('combined')
        self.small_frame = cv2.resize(self.combined, (960, 540)).astype(np.uint8)
        print(self.small_frame.shape, self.small_frame.dtype)
        self.im = Image.fromarray(self.small_frame)
        self.pim = ImageTk.PhotoImage(self.im)
        print(self.pim)
        self.frame.create_image(0,0,image=self.pim,anchor=NW)

        print('finished draw')

        #self.drawing *= 0.98

        self.tk.update_idletasks()
        self.tk.update()

if __name__ == '__main__':
    w = DrawingWindow()
    w.update()

    for i in range(1000):
        w.update()

    w.close()
