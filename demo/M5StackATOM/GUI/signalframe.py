# -*- coding: utf-8 -*-

import tkinter as Tk
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
from communication import Communication

class SignalFrame(Tk.Frame):
    """Class of signal transmission, reception management
    
    Get the waveform of the infrared demodulation IC output.
    It is also possible to transmit the acquired waveform.

    Waveform
    ----------
       _______      ______          ____ <-Blank time ->
    __|       |____|      |________|    |___________________
    start                               Considered as signal end
      <- t0 ->< t1 >< t2 ><-- t3 --><t4> ...   [usec]

    Data
    ----------
    [t0, t1, t2, t3, t4]  (The number of elements will be odd.)

    Signal end
    ----------
    1. If the size is specified, it is limited by the number of
       elements in the above data.
    2. If the idle time exceeds the specified time after the
       start of reception, it is regarded as the end of reception.

    Feature
    ----------
    The output of the infrared demodulation IC cannot restore
    the correct transmission waveform due to processing delay.
    This waveform delay is corrected on the device processing
    side(ESP32) by micropython.
    """
    # Widget size
    WIDTH_SIGNAL   = 14
    HEIGHT_SIGNAL  = 20
    WIDTH_COMMENT  = 14
    HEIGHT_COMMENT = 8
    WIDTH_ENTRY    = 5
    # background color
    COLOR_GREEN = '#98FB98'
    COLOR_PINK  = '#FFB6C1'

    def __init__(self, master, **key):
        """Initialize this sub frame

        Parameters
        ----------
        master : Parent frame

        GUI
        ----------

        **************          **************
            frame0                  frame1
        **************          **************
        
        Signal
        ---------------        -- Stop condition -------
        | 0001: 4000  |        |              _______   |
        | 0002:  800  |        | Wait [sec]  |       |  |
        | ...         |        |              _______   |
        | ...         |        | Size        |       |  |
        ---------------        |              _______   |
                               | Blank[msec] |       |  |
        Comment                --------------------------
        ---------------
        | This is a   |
        | comment     |        **************
        |             |            frame2
        |             |        **************
        ---------------         ________
                               | Record |
                                ________
                               | Commit |
                                ________
                               | Cancel |
                                ________
                               |  Send  |

        ***************
            Widget
        ***************
        frame0
            self.signal  (ScrolledText)
            self.comment (ScrolledText)
        frame1
            self.wait          (Entry)
                self.wait_var  (IntVar)
            self.size          (Entry)
                self.size_var  (IntVar)
            self.blank         (Entry)
                self.blank_var (IntVar)
        frame2
            self.record_button (Button)
            self.commit_button (Button)
            self.cancel_button (Button)
            self.send_button   (Button)
        """
        super().__init__(master, **key)
        self.mastar = master
        # inner frame
        self.inner_frame0 = Tk.Frame(self)
        self.inner_frame1 = Tk.LabelFrame(self, text='Stop condition')
        self.inner_frame2 = Tk.Frame(self)
        # variable
        self.wait_var = Tk.IntVar(value=3)     # [sec]
        self.size_var = Tk.IntVar(value=1023)
        self.blank_var = Tk.IntVar(value=200)  # [msec]
        # widget in frame0
        Tk.Label(self.inner_frame0, text='Signal').pack(anchor=Tk.W)
        self.signal = ScrolledText(self.inner_frame0,
                                   bg=SignalFrame.COLOR_GREEN, 
                                   width=SignalFrame.WIDTH_SIGNAL,
                                   height=SignalFrame.HEIGHT_SIGNAL)
        self.signal['state'] = Tk.DISABLED
        self.signal.pack(fill=Tk.X, padx=10, pady=5)

        Tk.Label(self.inner_frame0, text='Comment').pack(anchor=Tk.W)
        self.comment = ScrolledText(self.inner_frame0,
                                    bg=SignalFrame.COLOR_GREEN,
                                    width=SignalFrame.WIDTH_COMMENT,
                                    height=SignalFrame.HEIGHT_COMMENT)
        self.comment.bind("<KeyPress>", self._on_modified)
        self.comment['state'] = Tk.DISABLED
        self.comment.pack(fill=Tk.X, padx=10, pady=5)
        
        # widget in frame1
        Tk.Label(self.inner_frame1, text='Wait [sec]').grid(column=0, row=0, sticky=Tk.W, padx=10, pady=5)
        Tk.Label(self.inner_frame1, text='Size').grid(column=0, row=1, sticky=Tk.W, padx=10, pady=5)
        Tk.Label(self.inner_frame1, text='Blank [msec]').grid(column=0, row=2, sticky=Tk.W, padx=10, pady=5)
        self.wait = Tk.Entry(self.inner_frame1, 
                             textvariable=self.wait_var,
                             width=SignalFrame.WIDTH_ENTRY)
        self.wait.grid(column=1, row=0, sticky=Tk.EW, padx=10, pady=5)
        self.size = Tk.Entry(self.inner_frame1, 
                               textvariable=self.size_var,
                               width=SignalFrame.WIDTH_ENTRY)
        self.size.grid(column=1, row=1, sticky=Tk.EW, padx=10, pady=5)
        self.blank = Tk.Entry(self.inner_frame1, 
                              textvariable=self.blank_var,
                              width=SignalFrame.WIDTH_ENTRY)
        self.blank.grid(column=1, row=2, sticky=Tk.EW, padx=10, pady=5)
        
        # widget in frame2
        self.record_button = Tk.Button(self.inner_frame2,
                                       text='Record',
                                       command=self._record)
        self.record_button['state'] = Tk.DISABLED
        self.record_button.pack(fill=Tk.X, padx=10, pady=5)

        self.commit_button = Tk.Button(self.inner_frame2,
                                       text='Commit',
                                       command=self._commit)
        self.commit_button['state'] = Tk.DISABLED
        self.commit_button.pack(fill=Tk.X, padx=10, pady=5)

        self.cancel_button = Tk.Button(self.inner_frame2,
                                       text='Cancel',
                                       command=self._cancel)
        self.cancel_button['state'] = Tk.DISABLED
        self.cancel_button.pack(fill=Tk.X, padx=10, pady=5)
    
        self.send_button = Tk.Button(self.inner_frame2,
                                     text='Send',
                                     command=self._send)
        self.send_button['state'] = Tk.DISABLED
        self.send_button.pack(fill=Tk.X, padx=10, pady=5)

        # pack inner frame
        self.inner_frame0.pack(fill=Tk.X, side=Tk.LEFT, padx=10, pady=10)
        self.inner_frame1.pack(fill=Tk.X, side=Tk.TOP, padx=10, pady=15)
        self.inner_frame2.pack(fill=Tk.X, side=Tk.TOP, padx=10, pady=15)

        self.signal_modified = False
        self.comment_modified = False
        self.signal_original = []
        self.signal_override = []
        self.comment_original = ''

        self._communication = Communication()

    def _on_modified(self, event):
        """Check if the comment section has been updated"""
        if self.comment['state'] == Tk.NORMAL and self.comment_modified is False:
            self.comment_modified = True
            self.comment['bg'] = SignalFrame.COLOR_PINK
            self.commit_button['state'] = Tk.NORMAL
            self.cancel_button['state'] = Tk.NORMAL

    def _record(self):
        """Operation when the record button is pressed"""
        self._edit_off()
        _wait = self.wait_var.get()
        _timeout = _wait + 2
        _size = self.size_var.get()
        _blank = self.blank_var.get()
        if not self._communication.is_connect():
            if not self._communication.connect():
                messagebox.showerror('Error', "Can't connect device.")
                self._edit_on()
                return
        if 60 < _wait or 1023 < _size or _wait*1000 < _blank:
            messagebox.showerror('Error', 'Stop condition is invalid.')
            self._edit_on()
            return
        command = 'r[{},{},{}]\r\n'.format(_wait*1000, _blank, _size)
        ack = self._communication.record(command, _timeout)
        if ack[0]:
            self.signal_modified = True
            self.signal_override = ack[1]
            self._override_signal(self.signal_override)
        else:
            messagebox.showerror('Error', "Can't connect device.")
        self._edit_on()

    def _commit(self):
        """Operation when the commit button is pressed"""
        if self.signal_modified:
            self.signal_original = self.signal_override
        if self.comment_modified:
            self.comment_original = self._get_comment()
        self.enable(self.signal_original, self.comment_original)
        self.master.data_update(self.signal_original, self.comment_original)

    def _cancel(self):
        """Operation when the cancel button is pressed"""
        self.enable(self.signal_original, self.comment_original)

    def _send(self):
        """Operation when the send button is pressed"""
        self._edit_off()
        _timeout = 5
        if not self._communication.is_connect():
            if not self._communication.connect():
                messagebox.showerror('Error', "Can't connect device.")
                self._edit_on()
                return
        if self.signal_modified:
            if self.signal_override:
                command = 'w{}\r\n'.format(self.signal_override)
            else:
                command = ''
        else:
            if self.signal_original:
                command = 'w{}\r\n'.format(self.signal_original)
            else:
                command = ''
        if command:
            if not self._communication.send(command, _timeout):
                messagebox.showerror('Error', "Can't connect device.")
        self._edit_on()

    def _edit_off(self):
        self.record_button['state'] = Tk.DISABLED
        self.commit_button['state'] = Tk.DISABLED
        self.cancel_button['state'] = Tk.DISABLED
        self.send_button['state'] = Tk.DISABLED
        self.comment['state'] = Tk.DISABLED
    
    def _edit_on(self):
        self.record_button['state'] = Tk.NORMAL
        if self.signal_modified or self.comment_modified:
            self.commit_button['state'] = Tk.NORMAL
            self.cancel_button['state'] = Tk.NORMAL
        else:
            self.commit_button['state'] = Tk.DISABLED
            self.cancel_button['state'] = Tk.DISABLED
        self.send_button['state'] = Tk.NORMAL
        self.comment['state'] = Tk.NORMAL

    def _preset_signal(self, signal_list: list=[]):
        self.signal['state'] = Tk.NORMAL
        self.signal['bg'] = SignalFrame.COLOR_GREEN
        self.signal.delete('1.0', 'end')
        self.signal_original = signal_list
        self.signal_modified = False
        signal_text = ''
        for i,content in enumerate(self.signal_original):
            signal_text += '{:0>4d}: {:>7,d}\n'.format(i+1, content)
        self.signal.insert('1.0', signal_text)
        self.signal['state'] = Tk.DISABLED

    def _override_signal(self, signal_list: list):
        self.signal['state'] = Tk.NORMAL
        self.signal['bg'] = SignalFrame.COLOR_PINK
        self.signal.delete('1.0', 'end')
        self.signal_override = signal_list.copy()
        self.signal_modified = True
        signal_text = ''
        for i,content in enumerate(self.signal_override):
            signal_text += '{:0>4d}: {:>7,d}\n'.format(i+1, content)
        self.signal.insert('1.0', signal_text)
        self.signal['state'] = Tk.DISABLED

    def _get_comment(self):
        return(self.comment.get('1.0', 'end-1c'))

    def disable(self):
        """Disable all widgets"""
        self.signal['state'] = Tk.NORMAL
        # 1-line, 0-column to end
        self.signal.delete('1.0', 'end')
        self.signal['bg'] = SignalFrame.COLOR_GREEN
        self.signal['state'] = Tk.DISABLED
        self.comment['state'] = Tk.NORMAL
        self.comment.delete('1.0', 'end')
        self.comment['bg'] = SignalFrame.COLOR_GREEN
        self.comment['state'] = Tk.DISABLED
        self.record_button['state'] = Tk.DISABLED
        self.commit_button['state'] = Tk.DISABLED
        self.cancel_button['state'] = Tk.DISABLED
        self.send_button['state'] = Tk.DISABLED

    def enable(self, signal_list: list, comment_text: str):
        """Enable all widgets & Initialize"""
        self.signal_modified = False
        self.comment_modified = False
        self._preset_signal(signal_list)
        self.comment_original = comment_text

        self.comment['state'] = Tk.NORMAL
        self.comment['bg'] = SignalFrame.COLOR_GREEN
        self.comment.delete('1.0', 'end')
        self.comment.insert('1.0', comment_text)

        self.record_button['state'] = Tk.NORMAL
        self.commit_button['state'] = Tk.DISABLED
        self.cancel_button['state'] = Tk.DISABLED
        self.send_button['state'] = Tk.NORMAL
