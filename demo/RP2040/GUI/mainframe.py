# -*- coding: utf-8 -*-

import tkinter as Tk
from fileframe import FileFrame
from dataframe import DataFrame
from signalframe import SignalFrame

class MainFrame(Tk.Frame):
    """Integrated class for all frames"""
    def __init__(self, master, **key):
        super().__init__(master, **key)
        self.file_frame = FileFrame(self)
        self.data_frame = DataFrame(self)
        self.signal_frame = SignalFrame(self)
        self.file_frame.pack(fill=Tk.X, padx=10, pady=5)
        self.data_frame.pack(side=Tk.LEFT, padx=10, pady=5)
        self.signal_frame.pack(side=Tk.LEFT, padx=10, pady=5)
    
    # Processing across frames
    def get_filename(self):
        return(self.file_frame.get_filename())
    
    def file_lock(self):
        self.file_frame.disable()
    
    def file_unlock(self):
        self.file_frame.enable()

    def signal_disable(self):
        self.signal_frame.disable()
    
    def signal_enable(self, signal_list: list, comment_text: str):
        self.signal_frame.enable(signal_list, comment_text)
    
    def data_update(self, signal_list: list, comment_text: str):
        self.data_frame.update(signal_list, comment_text)
