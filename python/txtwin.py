#!/usr/bin/env python3

"""
    Toplevel window to display text
    (c) Zoltan Siki siki (dot) zoltan (at) emk.bme.hu
"""

import tkinter as tk

class TxtWin(tk.Toplevel):
    """ simple windows to display text messages
        :param txt: text to display
    """

    def __init__(self, txt, master):
        """ initialize """
        super().__init__(master=master)
        self.title = "Output"
        self.geometry("800x600")
        self.h_scroll = tk.Scrollbar(self, orient='horizontal')
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_scroll = tk.Scrollbar(self)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_widget = tk.Text(self, width=80, height=25,
                             xscrollcommand=self.h_scroll.set,
                             yscrollcommand=self.v_scroll.set)
        self.txt_widget.insert(tk.END, txt)
        self.txt_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.h_scroll.config(command=self.txt_widget.xview)
        self.v_scroll.config(command=self.txt_widget.yview)
        self.grab_set()
        master.wait_window(self)
