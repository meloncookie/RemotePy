# -*- coding: utf-8 -*-

import tkinter as Tk
from tkinter import messagebox
import json
import os

from numpy import isin

class ScrolledListbox(Tk.Listbox):
    """ Listbox widget with vertical scroll bar"""
    def __init__(self, master, **key):
        """Initialize extended widget "ScrolledListbox"

        inputs
        ----------
        master : Parent frame
        key : option dictionary
        """
        self.yscroll = Tk.Scrollbar(master, orient=Tk.VERTICAL)
        self.yscroll.pack(side=Tk.RIGHT, fill=Tk.Y, expand=1)
        key['yscrollcommand']=self.yscroll.set
        super().__init__(master, **key)
        self.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)
        self.yscroll.config(command=self.yview)

class DataFrame(Tk.Frame):
    """Class of control data
    
    When remote controler data is registered, data management and
    display control are performed.
    
    Data format(dictionary)
    ----------
    {'action key1': {'signal': [100, 20, ...], 'comment': 'xxx'},
     'action key2': {'signal': [360, 90, ...], 'comment': 'yyy'},
      ....
     '__system__':  {'signal': [], 'comment': 'meta comment'}
     }
    
    Remote control data consists of time sequence data and
    annotations with action (CH1, REC, etc...) as a key.
    
    The action key is displayed in a list. The current choice
    of the list is automatically identified.

    A special action key '__system__' means a comment for this entire data.
    This key always exists and cannot be erased.
    """
    # Widget size
    HEIGHT_KEYLIST = 10
    WIDTH_KEYLIST  = 18
    # Special key name
    SYSTEM_KEY = '__system__'
    # State
    STATE_CLOSED = 0
    STATE_OPENED = 1
    STATE_EDITED = 2

    def __init__(self, master, **key):
        """Initialize sub frame for data-control
        
        1. Register the remote control data read from the file.
        2. Data management, information update, and information
           display are performed.
        
        Parameters
        ----------
        master : Parent frame
        key : option dictionary
        
        GUI                     Widget
        ----------              ----------
         ________
        |  Open  |              self.open_button  (Button)
         ________
        |  Save  |              self.save_button  (Button)
         ________
        |  Close |              self.close_button (Button)

        key
         -----------
        |           |           self.key_list (ScrolledListbox)
        |           |
        |           |
        |           |
         -----------
        
        Select key
         ___________
        |           |           self.select_key (Entry)
         ___________                self.select_var (StringVar)
        |  Delete   |           self.delete_button (Button)

        Edit key
         ___________
        |           |           self.edit_key (Entry)
         ___________                self.edit_var (StringVar)
        |  Append   |           self.append_button (Button)
         ___________
        |  Rename   |           self.rename_button (Button)

        """
        super().__init__(master, **key)
        self.master = master
        # inner frame
        self.inner_frame0 = Tk.Frame(self)
        self.inner_frame1 = Tk.Frame(self)
        self.inner_frame2 = Tk.Frame(self)
        # variable
        self.select_var = Tk.StringVar(value='')
        self.edit_var = Tk.StringVar(value='')
        
        # widget in frame0
        self.open_button = Tk.Button(self.inner_frame0,
                                     text='Open',
                                     command=self._open)
        self.open_button['state'] = Tk.NORMAL
        self.save_button = Tk.Button(self.inner_frame0,
                                     text='Save',
                                     command=self._save)
        self.save_button['state'] = Tk.DISABLED
        self.close_button = Tk.Button(self.inner_frame0,
                                      text='Close',
                                      command=self._close)
        self.close_button['state'] = Tk.DISABLED
        self.open_button.pack(fill=Tk.X, padx=10, pady=5)
        self.save_button.pack(fill=Tk.X, padx=10, pady=5)
        self.close_button.pack(fill=Tk.X, padx=10, pady=5)

        # widget in frame1
        Tk.Label(self.inner_frame1, text='Key list').pack(anchor=Tk.W)
        self.key_list = ScrolledListbox(self.inner_frame1,
                                        selectmode=Tk.SINGLE,
                                        height=DataFrame.HEIGHT_KEYLIST,
                                        width=DataFrame.WIDTH_KEYLIST)
        self.key_list.pack(fill=Tk.X, padx=10, pady=5)
        
        # widget in frame2
        Tk.Label(self.inner_frame2, text='Select key').pack(anchor=Tk.W)
        self.select_key = Tk.Label(self.inner_frame2, 
                                   textvariable=self.select_var,
                                   relief='ridge')
        self.select_key.pack(fill=Tk.X, padx=10, pady=5)
        self.delete_button = Tk.Button(self.inner_frame2,
                                       text='Delete',
                                       command=self._delete)
        self.delete_button['state'] = Tk.DISABLED
        self.delete_button.pack(fill=Tk.X, padx=10, pady=5)

        Tk.Label(self.inner_frame2, text='Edit key').pack(anchor=Tk.W)
        self.edit_key = Tk.Entry(self.inner_frame2, 
                                 textvariable=self.edit_var)
        self.edit_key['state'] = Tk.DISABLED
        self.edit_key.pack(fill=Tk.X, padx=10, pady=5)
        self.append_button = Tk.Button(self.inner_frame2,
                                       text='Append',
                                       command=self._append)
        self.append_button['state'] = Tk.DISABLED
        self.append_button.pack(fill=Tk.X, padx=10, pady=5)
        self.rename_button = Tk.Button(self.inner_frame2,
                                       text='Rename',
                                       command=self._rename)
        self.rename_button['state'] = Tk.DISABLED
        self.rename_button.pack(fill=Tk.X, padx=10, pady=5)

        # Register callback when list is selected
        self.key_list.bind('<<ListboxSelect>>', self._key_list_select)
        # pack inner frame
        self.inner_frame0.pack(fill=Tk.X, padx=10, pady=5)
        self.inner_frame1.pack(fill=Tk.X, padx=10, pady=5)
        self.inner_frame2.pack(fill=Tk.X, padx=10, pady=5)
        # data
        self.save_data = {DataFrame.SYSTEM_KEY: {'signal':[], 'comment': ''}}
        self.save_keys = [DataFrame.SYSTEM_KEY]
        self.select_index = 0
        self.state = DataFrame.STATE_CLOSED

    def _key_list_select(self, event):
        """Callback when list is selected"""
        widget = event.widget
        tpl_select = widget.curselection()
        if(tpl_select):
            self.select_index = tpl_select[0]
            self._view_information()

    def _open(self):
        """Operation when the open button is pressed"""
        try:
            filename = self.master.get_filename()
            if os.path.isfile(filename):
                with open(filename) as fp:
                    self.save_data = json.load(fp)
                # Type check
                if not isinstance(self.save_data, dict):
                    raise Exception()
                for key in self.save_data:
                    if not isinstance(self.save_data[key], dict):
                        raise Exception()
            else:
                self.save_data = {DataFrame.SYSTEM_KEY: {'signal':[], 'comment': ''}}
            self.save_keys = list(self.save_data.keys())
            if DataFrame.SYSTEM_KEY not in self.save_keys:
                self.save_data[DataFrame.SYSTEM_KEY] = {'signal': [], 'comment': ''}
            else:
                self.save_keys.remove(DataFrame.SYSTEM_KEY)
            self.save_keys.sort()
            self.save_keys.insert(0, DataFrame.SYSTEM_KEY)
        except:
            messagebox.showerror('Error', "Can't open file or Data format is illegal.")
            return
        self.key_list.delete(0, Tk.END)
        self.key_list.insert(Tk.END, *self.save_keys)
        self.select_index = 0
        self.key_list.selection_set(self.select_index)
        self._view_information()

        self.open_button['state'] = Tk.DISABLED
        self.save_button['state'] = Tk.DISABLED
        self.close_button['state'] = Tk.NORMAL
        self.master.file_lock()
        self.state = DataFrame.STATE_OPENED
        self.delete_button['state'] = Tk.NORMAL
        self.edit_key['state'] = Tk.NORMAL
        self.append_button['state'] = Tk.NORMAL
        self.rename_button['state'] = Tk.NORMAL

    def _save(self):
        """Operation when the save button is pressed"""
        try:
            with open(self.master.get_filename(), mode='w') as fp:
                json.dump(self.save_data, fp)
        except:
            messagebox.showerror('Error', "Can't save safely.")
            return
        self.save_button['state'] = Tk.DISABLED
        self.state = DataFrame.STATE_OPENED

    def _close(self):
        """Operation when the close button is pressed"""
        if self.state == DataFrame.STATE_EDITED:
            ack = messagebox.askyesno('Data has been updated', 'Do you want to close without saving?')
            if ack is False:
                return
        self.open_button['state'] = Tk.NORMAL
        self.save_button['state'] = Tk.DISABLED
        self.close_button['state'] = Tk.DISABLED
        self.select_var.set('')
        self.key_list.delete(0, Tk.END)
        self.delete_button['state'] = Tk.DISABLED
        self.edit_key['state'] = Tk.NORMAL
        self.edit_var.set('')
        self.edit_key['state'] = Tk.DISABLED
        self.append_button['state'] = Tk.DISABLED
        self.rename_button['state'] = Tk.DISABLED
        self.save_data = {}
        self.select_index = 0
        self.state = DataFrame.STATE_CLOSED
        self.master.signal_disable()
        self.master.file_unlock()

    def _delete(self):
        """Operation when the delete button is pressed"""
        delete_key = self.save_keys[self.select_index]
        if delete_key == DataFrame.SYSTEM_KEY:
            return
        del self.save_data[delete_key]
        del self.save_keys[self.select_index]
        self.key_list.delete(self.select_index)
        if len(self.save_keys) <= self.select_index:
            self.select_index -= 1
        self.key_list.select_clear(0, Tk.END)
        self.key_list.select_set(self.select_index)
        self.state = DataFrame.STATE_EDITED
        self.save_button['state'] = Tk.NORMAL
        self._view_information()

    def _append(self):
        """Operation when the append button is pressed"""
        append_key = self.edit_var.get()
        if append_key == '' or append_key in self.save_keys:
            return
        self.save_data[append_key] = {'signal': [], 'comment': ''}
        self.save_keys.append(append_key)
        self.key_list.insert(Tk.END, append_key)
        self.select_index = len(self.save_keys) - 1
        self.key_list.select_clear(0, Tk.END)
        self.key_list.select_set(self.select_index)
        self.state = DataFrame.STATE_EDITED
        self.save_button['state'] = Tk.NORMAL
        self._view_information()

    def _rename(self):
        """Operation when the rename button is pressed"""
        now_key = self.save_keys[self.select_index]
        rename_key = self.edit_var.get()
        if rename_key == '' or rename_key in self.save_keys\
           or now_key == DataFrame.SYSTEM_KEY:
            return
        self.save_data[rename_key] = self.save_data[now_key]
        del self.save_data[now_key]
        self.save_keys[self.select_index] = rename_key
        self.key_list.delete(self.select_index)
        self.key_list.insert(self.select_index, rename_key)
        self.key_list.select_clear(0, Tk.END)
        self.key_list.select_set(self.select_index)
        self.state = DataFrame.STATE_EDITED
        self.save_button['state'] = Tk.NORMAL
        self._view_information()

    def _view_information(self):
        """Display signal / comment data by signalframe.py"""
        self.select_var.set(self.save_keys[self.select_index])
        selected = self.save_data.get(self.save_keys[self.select_index])
        selected_signal = selected.get('signal', [])
        selected_comment = selected.get('comment', '')
        self.master.signal_enable(selected_signal, selected_comment)

    def update(self, signal_list: list, comment_text: str):
        """Data update process from signalframe.py"""
        self.save_data[self.save_keys[self.select_index]] =\
            {'signal': signal_list.copy(), 'comment': comment_text}
        self.state = DataFrame.STATE_EDITED
        self.save_button['state'] = Tk.NORMAL
