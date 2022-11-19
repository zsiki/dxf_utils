#!/usr/bin/env python3

"""
    Graphical user interface for blk2svg.py
    (c) Zoltan Siki siki (dot) zoltan (at) emk.bme.hu
"""

import sys
from os import path
from io import StringIO
import tkinter as tk
#from tkinter import ttk
#from tkinter import messagebox
from tkinter import filedialog
from txtwin import TxtWin
from cp2templ import Cp2Templ

class Cp2TemplGui(tk.Tk):
    """ class to add GUI to blk2svg.py """

    def __init__(self):
        """ initialize
        """
        tk.Tk.__init__(self)
        self.dxf_file = ""
        self.templ_file = ""
        self.out_file = ""
        self.layer_table = ""
        self.block_table = ""
        self.title("Copy entities to template DXF")

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

        self.out_label = tk.Label(self, text="Eredmény DXF fájl: ")
        self.out_entry = tk.Entry(self, width=60)
        self.out_select = tk.Button(self, text="...", command=self.select_out)
        self.out_label.grid(row=2, column=0, sticky="e")
        self.out_entry.grid(row=2, column=1, sticky="w")
        self.out_select.grid(row=2, column=2, sticky="w")

        self.layer_label = tk.Label(self, text="Réteg fordító tábla: ")
        self.layer_entry = tk.Entry(self, width=60)
        self.layer_select = tk.Button(self, text="...", command=self.select_layer_table)
        self.layer_label.grid(row=3, column=0, sticky="e")
        self.layer_entry.grid(row=3, column=1, sticky="w")
        self.layer_select.grid(row=3, column=2, sticky="w")

        self.block_label = tk.Label(self, text="Blokk fordító tábla: ")
        self.block_entry = tk.Entry(self, width=60)
        self.block_select = tk.Button(self, text="...", command=self.select_block_table)
        self.block_label.grid(row=4, column=0, sticky="e")
        self.block_entry.grid(row=4, column=1, sticky="w")
        self.block_select.grid(row=4, column=2, sticky="w")

        self.go_button = tk.Button(self, text="Indít", command=self.go)
        self.go_button.grid(row=5, column=2)

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
        out_file = filedialog.asksaveasfile(title="Output fájl kiválasztása", filetypes=[("DXF files", "*.dxf")])
        self.out_file = out_file.name
        self.out_entry.delete(0, tk.END)
        self.out_entry.insert(0, self.out_file)

    def select_layer_table(self):
        """ file name selection and add to entry """
        self.layer_table = filedialog.askopenfilename(title="Réteg tábla kiválasztása", filetypes=[("TXT files", "*.txt")])
        self.layer_entry.delete(0, tk.END)
        self.layer_entry.insert(0, self.layer_table)

    def select_block_table(self):
        """ file name selection and add to entry """
        self.block_table = filedialog.askopenfilename(title="Blokk tábla kiválasztása", filetypes=[("TXT files", "*.txt")])
        self.block_entry.delete(0, tk.END)
        self.block_entry.insert(0, self.block_table)

    def go(self):
        """ check entries and run conversion """
        dxf_name = self.dxf_entry.get()
        if not path.exists(dxf_name):
            tk.messagebox.showerror(title="Hiba", message="DXF input fájl nem létezik")
            return
        templ_name = self.templ_entry.get()
        if not path.exists(templ_name):
            tk.messagebox.showerror(title="Hiba", message="DXF sablon fájl nem létezik")
            return
        out_file = self.out_entry.get()
        if len(out_file.strip()) == 0:
            tk.messagebox.showerror(title="Hiba", message="Nem adott meg output DXF fájlt")
            return

        layer_table = self.layer_entry.get()
        if len(layer_table) > 0 and not path.exists(layer_table):
            tk.messagebox.showerror(title="Hiba", message="Réteg tábla fájl nem létezik")
            return

        block_table = self.block_entry.get()
        if len(block_table) > 0 and not path.exists(block_table):
            tk.messagebox.showerror(title="Hiba", message="Blokk tábla fájl nem létezik")
            return
        old_stdout = sys.stdout
        sys.stdout = string_io = StringIO()
        cp = Cp2Templ(dxf_name, templ_name, out_file, layer_table, block_table)
        cp.copy()
        txt_out = string_io.getvalue()
        if len(txt_out) > 0:
            TxtWin(txt_out, self)
        sys.stdout = old_stdout
        self.quit()

if __name__ == "__main__":
    conv = Cp2TemplGui()
    conv.mainloop()
