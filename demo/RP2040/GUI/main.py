# -*- coding: utf-8 -*-

import tkinter as Tk
from mainframe import MainFrame

root = Tk.Tk()
root.title("infrared recorder")
root.geometry("720x700")
root.minsize(640, 640)
root.maxsize(800, 780)
root.option_add('*font', ('fixed', 12))
sub_frame = MainFrame(root)
sub_frame.pack()
root.mainloop()
