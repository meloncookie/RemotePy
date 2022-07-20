# -*- coding: utf-8 -*-

import tkinter as Tk
from tkinter import filedialog
import os

class FileFrame(Tk.Frame):
    """Class of file select"""
    # Length of character string in the file_entry field 
    WIDTH_FILENAME = 60
    
    def __init__(self, master, **key):
        """Initialize sub frame for file select

        **********
        GUI
        **********
               ---------------           --------
        File: |               |         | Select |
               ---------------           --------

        **********
        Widget
        **********
        self.file_entry  (file_entry)
            self.filename_var (StringVar)
        self.file_select (Button)
        """
        super().__init__(master, **key)
        # inner frame
        self.inner_frame0 = Tk.Frame(self)
        # variable
        self.filename_var = Tk.StringVar()
        # widget in frame0
        Tk.Label(self.inner_frame0, text='File').pack(side=Tk.LEFT)
        self.file_entry = Tk.Entry(self.inner_frame0, 
                                   textvariable=self.filename_var,
                                   width=FileFrame.WIDTH_FILENAME)
        self.file_entry.pack(side=Tk.LEFT, fill=Tk.X, padx=5)
        self.file_select = Tk.Button(self.inner_frame0, text='Select',
                                     command=self._file_select)
        self.file_select.pack(side=Tk.LEFT, padx=10)
        # pack inner frame
        self.inner_frame0.pack(fill=Tk.X, padx=10, pady=5)
        # others
        self.current_dir = os.path.curdir

    def _file_select(self):
        """Operation when the select button is pressed"""
        filename = filedialog.asksaveasfilename(initialdir = self.current_dir, confirmoverwrite=False)
        if filename and os.path.exists(filename):
            filename = os.path.abspath(filename)
            self.current_dir = os.path.dirname(filename)
        self.filename_var.set(filename)

    def disable(self):
        """Disable file_entry field & button"""
        self.file_entry['state'] = Tk.DISABLED
        self.file_select['state'] = Tk.DISABLED
    
    def enable(self):
        """Enable file_entry field & button"""
        self.file_entry['state'] = Tk.NORMAL
        self.file_select['state'] = Tk.NORMAL
    
    def get_filename(self):
        """Get a file name
        
        Acquire the file name entered in the file_entry field.
        
        Returns
        ----------
        string  file name. But it may be an invalid file name.
        ''      (No file_entry)
        """
        get_name = self.filename_var.get()
        return(get_name)
