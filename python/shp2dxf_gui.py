#!/usr/bin/env python3

"""
    Graphical user interface for blk2svg.py
    (c) Zoltan Siki siki (dot) zoltan (at) emk.bme.hu
"""

import sys
from os import path
from io import StringIO
import tkinter as tk
from tkinter import filedialog
from txtwin import TxtWin
from shp2dxf import Shp2Dxf

class Shp2DxfGui(tk.Tk):
    """ class to add GUI to blk2svg.py """

    def __init__(self):
        """ initialize
        """
        tk.Tk.__init__(self)
        self.inp_dir = ""
        self.templ_file = ""
        self.out_file = ""
        self.rules_table = ""
        self.title("E-közmű SHP adatszolgáltatás konvertálása DXF-be")

        self.inp_label = tk.Label(self, text="Input SHP mappa: ")
        self.inp_entry = tk.Entry(self, width=60)
        self.inp_select = tk.Button(self, text="...", command=self.select_inp)
        self.inp_label.grid(row=0, column=0, sticky="e")
        self.inp_entry.grid(row=0, column=1, sticky="w")
        self.inp_select.grid(row=0, column=2, sticky="w")

        self.templ_label = tk.Label(self, text="DXF sablon fájl: ")
        self.templ_entry = tk.Entry(self, width=60)
        self.templ_select = tk.Button(self, text="...", command=self.select_templ)
        self.templ_label.grid(row=1, column=0, sticky="e")
        self.templ_entry.grid(row=1, column=1, sticky="w")
        self.templ_select.grid(row=1, column=2, sticky="w")

        self.out_label = tk.Label(self, text="DXF output fájl: ")
        self.out_entry = tk.Entry(self, width=60)
        self.out_select = tk.Button(self, text="...", command=self.select_out)
        self.out_label.grid(row=2, column=0, sticky="e")
        self.out_entry.grid(row=2, column=1, sticky="w")
        self.out_select.grid(row=2, column=2, sticky="w")

        self.rules_label = tk.Label(self, text="Konverziós szabályok tábla: ")
        self.rules_entry = tk.Entry(self, width=60)
        self.rules_select = tk.Button(self, text="...", command=self.select_rules_table)
        self.rules_label.grid(row=3, column=0, sticky="e")
        self.rules_entry.grid(row=3, column=1, sticky="w")
        self.rules_select.grid(row=3, column=2, sticky="w")

        self.go_button = tk.Button(self, text="Indít", command=self.go)
        self.go_button.grid(row=4, column=2)

    def select_inp(self):
        """ output folder selection and add to entry """
        self.inp_dir = filedialog.askdirectory(title="SHP forrás könyvtár kiválasztása")
        self.inp_entry.delete(0, tk.END)
        self.inp_entry.insert(0, self.inp_dir)

    def select_templ(self):
        """ file name selection and add to entry """
        self.templ_file = filedialog.askopenfilename(title="DXF sablon fájl kiválasztása", filetypes=[("DXF files", "*.dxf")])
        self.templ_entry.delete(0, tk.END)
        self.templ_entry.insert(0, self.templ_file)

    def select_out(self):
        """ file name selection and add to entry """
        out_file = filedialog.asksaveasfile(title="Output fájl kiválasztása", filetypes=[("DXF files", "*.dxf")])
        self.out_file = out_file.name
        self.out_entry.delete(0, tk.END)
        self.out_entry.insert(0, self.out_file)

    def select_rules_table(self):
        """ file name selection and add to entry """
        self.rules_table = filedialog.askopenfilename(title="Szabály tábla kiválasztása", filetypes=[("TXT files", "*.txt")])
        self.rules_entry.delete(0, tk.END)
        self.rules_entry.insert(0, self.rules_table)

    def go(self):
        """ check entries and run conversion """
        inp_dir = self.inp_entry.get()
        if not path.exists(inp_dir):
            tk.messagebox.showerror(title="Hiba", message="SHP input mappa nem létezik")
            return
        templ_name = self.templ_entry.get()
        if not path.exists(templ_name):
            tk.messagebox.showerror(title="Hiba", message="DXF sablon fájl nem létezik")
            return

        out_name = self.out_entry.get()
        if len(out_name) < 1:
            tk.messagebox.showerror(title="Hiba", message="Nem adott meg output DXF fájlt")

        rules_table = self.rules_entry.get()
        if not path.exists(rules_table):
            tk.messagebox.showerror(title="Hiba", message="konverziós szabályok tábla fájl nem létezik")
            return
        old_stdout = sys.stdout
        sys.stdout = string_io = StringIO()
        s = Shp2Dxf(inp_dir, templ_name, out_name, rules_table)
        s.convert()
        txt_out = string_io.getvalue()
        if len(txt_out) > 0:
            TxtWin(txt_out, self)
        sys.stdout = old_stdout
        exit()

if __name__ == "__main__":
    conv = Shp2DxfGui()
    conv.mainloop()
