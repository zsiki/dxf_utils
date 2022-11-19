#!/usr/bin/env python3

"""
    Grafical user interface for dxfinfo.py
    (c) Zoltan Siki siki (dot) zoltan (at) emk.bme.hu
"""

import sys
from os import path
from io import StringIO
import tkinter as tk
from tkinter import filedialog
from txtwin import TxtWin
from dxfinfo import DxfInfo

class DxfInfoGui(tk.Tk):
    """ class to add GUI to blk2svg.py """

    def __init__(self):
        """ initialize
        """
        tk.Tk.__init__(self)
        self.dxf_file = ""
        self.out_file = "stdout"
        self.templ_file = ""
        self.title("DXF Info")

        self.dxf_label = tk.Label(self, text="DXF input fájl: ")
        self.dxf_entry = tk.Entry(self, width=60)
        self.dxf_select = tk.Button(self, text="...", command=self.select)
        self.dxf_label.grid(row=0, column=0, sticky="e")
        self.dxf_entry.grid(row=0, column=1, sticky="w")
        self.dxf_select.grid(row=0, column=2, sticky="w")

        self.templ_label = tk.Label(self, text="DXF sablon fájl: ")
        self.templ_entry = tk.Entry(self, width=60)
        self.templ_select = tk.Button(self, text="...", command=self.select_templ)
        self.templ_label.grid(row=1, column=0, sticky="e")
        self.templ_entry.grid(row=1, column=1, sticky="w")
        self.templ_select.grid(row=1, column=2, sticky="w")

        self.out_label = tk.Label(self, text="Eredmény fájl: ")
        self.out_entry = tk.Entry(self, width=60)
        self.out_select = tk.Button(self, text="...", command=self.select_out)
        self.out_label.grid(row=2, column=0, sticky="e")
        self.out_entry.grid(row=2, column=1, sticky="w")
        self.out_select.grid(row=2, column=2, sticky="w")

        self.go_button = tk.Button(self, text="Indít", command=self.go)
        self.go_button.grid(row=3, column=2)

    def select(self):
        """ file name selection and add to entry """
        self.dxf_file = filedialog.askopenfilename(title="DXF fájl kiválasztása", filetypes=[("DXF files", "*.dxf")])
        self.dxf_entry.delete(0, tk.END)
        self.dxf_entry.insert(0, self.dxf_file)

    def select_templ(self):
        """ file name selection and add to entry """
        self.templ_file = filedialog.askopenfilename(title="DXF sablon fájl kiválasztása", filetypes=[("DXF files", "*.dxf")])
        self.templ_entry.delete(0, tk.END)
        self.templ_entry.insert(0, self.templ_file)

    def select_out(self):
        """ file name selection and add to entry """
        out_file = filedialog.asksaveasfile(title="Output fájl kiválasztása", filetypes=[("TXT files", "*.txt")])
        self.out_file = out_file.name
        self.out_entry.delete(0, tk.END)
        self.out_entry.insert(0, self.out_file)

    def go(self):
        """ check entries and run conversion """
        dxf_name = self.dxf_entry.get()
        if not path.exists(dxf_name):
            tk.messagebox.showerror(title="Hiba", message="DXF fájl nem létezik")
            return
        templ_name = self.templ_entry.get()
        if len(templ_name) > 0 and not path.exists(templ_name):
            tk.messagebox.showerror(title="Hiba", message="Sablon DXF fájl nem létezik")
            return
        out_file = self.out_entry.get()
        if len(out_file) == 0:
            out_file = "stdout"
        old_stdout = sys.stdout
        sys.stdout = string_io = StringIO()
        DI = DxfInfo(dxf_name, templ_name, out_file)
        DI.dxf_info()
        if len(templ_name) > 0:
            DI.layer_compare()
            DI.block_compare()
        txt_out = string_io.getvalue()
        if len(txt_out) > 0:
            TxtWin(txt_out, self)
        sys.stdout = old_stdout
        selt.quit()

if __name__ == "__main__":
    info = DxfInfoGui()
    info.mainloop()
