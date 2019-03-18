import sys
from time import sleep

if sys.version_info[0] == 2:  # Just checking your Python version to import Tkinter properly.
    from Tkinter import *
else:
    from tkinter import *

PROJECTOR_RES_W = 1366
PROJECTOR_RES_H = 768

class Fullscreen_Window:
    def __init__(self):
        self.tk = Tk()
        screen_w = self.tk.winfo_screenwidth() - PROJECTOR_RES_W
        self.tk.geometry('%dx%d+%d+%d' % (PROJECTOR_RES_W, PROJECTOR_RES_H, screen_w, 0))
        self.frame = Canvas(self.tk)
        self.frame.configure(background='black', highlightthickness=0)
        self.frame.pack(fill='both', expand=True)
        self.state = True
        self.tk.attributes("-fullscreen", self.state)
        self.tk.bind("<F11>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)

    def __del__(self):
        self.close()

    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"

    def close(self):
        self.tk.destroy()

    def update(self):
        self.tk.update_idletasks()
        self.tk.update()

    def draw_line(self, p1, p2, **kwargs):
        self.frame.create_line(p1[0], p1[1], p2[0], p2[1], **kwargs)
        self.update()

    def draw_points(self, xs, ys, s=100, **kwargs):
        for x, y in zip(xs, ys):
            self.frame.create_oval(x-s, y-s, x+s, y+s, **kwargs)
        self.update()

    def draw_point(self, x, y, c='white', s=100, **kwargs):
        self.frame.create_oval(x-s, y-s, x+s, y+s, fill=c, outline=c, **kwargs)
        self.update()

    def clear(self):
        self.frame.delete('all')
        self.update()

    def get_dims(self):
        return self.frame.winfo_height(), self.frame.winfo_width()

if __name__ == '__main__':
    w = Fullscreen_Window()
    w.tk.update_idletasks()
    w.tk.update()
    sleep(1)

    height, width = w.frame.winfo_height(), w.frame.winfo_width()
    print(width, height)
    for ittr in range(1):
        for x in range(1, 16):
            w.frame.delete("all")
            w.frame.create_line(width * x / 16, 0, width * x / 16, height, fill='white', width=3)
            w.tk.update_idletasks()
            w.tk.update()
            sleep(.55)

        for y in range(1, 9):
            w.frame.delete("all")
            w.frame.create_line(0, height * y / 9, width, height * y / 9, fill='white', width=3)
            w.tk.update_idletasks()
            w.tk.update()
            sleep(.55)

    sleep(2)
