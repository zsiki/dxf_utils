#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
    visual check tool for gcp_find.py
    (c) Zoltan Siki siki (dot) zoltan (at) emk.bme.hu
"""

from os import path
import tkinter as tk
#from tkinter import ttk
#from tkinter import messagebox
from tkinter import filedialog
from block2svg import Block2

class Blk2SvgGui(tk.Tk):
    """ class to add GUI to blk2svg.py """

    def __init__(self):
        """ initialize
        """
        tk.Tk.__init__(self)
        self.dxf_file = ""
        self.out_dir = "."
        self.title("Blokk -> SVG/PNG konverter")
        # add menu
        #self.menu = tk.Menu(master=self)
        #self.fileMenu = tk.Menu(self.menu, tearoff=0)
        #self.fileMenu.add_command(label="Open", command=self.select)
        #self.fileMenu.add_command(label="Exit", command=exit)
        #self.menu.add_cascade(label="File", menu=self.fileMenu)
        #self.config(menu=self.menu)

        self.dxf_label = tk.Label(self, text="DXF input fájl: ")
        self.dxf_entry = tk.Entry(self, width=60)
        self.dxf_select = tk.Button(self, text="...", command=self.select)
        self.dxf_label.grid(row=0, column=0, sticky="e")
        self.dxf_entry.grid(row=0, column=1, sticky="w")
        self.dxf_select.grid(row=0, column=2, sticky="w")
        self.blk_label = tk.Label(self, text="Blokk név minta: ")
        self.blk_entry = tk.Entry(self, width=30)
        self.blk_entry.insert(0, "*")
        self.blk_label.grid(row=1, column=0, sticky="e")
        self.blk_entry.grid(row=1, column=1, sticky="w")
        self.out_label = tk.Label(self, text="Cél könyvtár: ")
        self.out_entry = tk.Entry(self, width=60)
        self.out_entry.insert(0, ".")
        self.out_select = tk.Button(self, text="...", command=self.select_out)
        self.out_label.grid(row=2, column=0, sticky="e")
        self.out_entry.grid(row=2, column=1, sticky="w")
        self.out_select.grid(row=2, column=2, sticky="w")
        self.wid_label = tk.Label(self, text="Szélesség: ")
        self.wid_entry = tk.Entry(self, width=10)
        self.wid_entry.insert(0, "500")
        self.wid_label.grid(row=3, column=0, sticky="e")
        self.wid_entry.grid(row=3, column=1, sticky="w")
        self.hei_label = tk.Label(self, text="Magasság: ")
        self.hei_entry = tk.Entry(self, width=10)
        self.hei_entry.insert(0, "500")
        self.hei_label.grid(row=4, column=0, sticky="e")
        self.hei_entry.grid(row=4, column=1, sticky="w")
        self.sca_label = tk.Label(self, text="Méret szorzó: ")
        self.sca_entry = tk.Entry(self, width=10)
        self.sca_entry.insert(0, "80")
        self.sca_label.grid(row=5, column=0, sticky="e")
        self.sca_entry.grid(row=5, column=1, sticky="w")
        self.lwi_label = tk.Label(self, text="Vonalvastagság: ")
        self.lwi_entry = tk.Entry(self, width=10)
        self.lwi_entry.insert(0, "10")
        self.lwi_label.grid(row=6, column=0, sticky="e")
        self.lwi_entry.grid(row=6, column=1, sticky="w")
        self.col_label = tk.Label(self, text="Szín: ")
        self.col_entry = tk.Entry(self, width=15)
        self.col_entry.insert(0, "black")
        self.col_label.grid(row=7, column=0, sticky="e")
        self.col_entry.grid(row=7, column=1, sticky="w")
        self.otyp_list = ["svg", "png"]
        self.otyp_var = tk.StringVar()
        self.otyp_var.set("svg")
        self.otyp_label = tk.Label(self, text="Eredmény típus: ")
        self.otyp = tk.OptionMenu(self, self.otyp_var, *self.otyp_list)
        self.otyp_label.grid(row=8, column=0, sticky="e")
        self.otyp.grid(row=8, column=1, sticky="w")
        self.go_button = tk.Button(self, text="Indít", command=self.go)
        self.go_button.grid(row=9, column=2)

    def select(self):
        """ file name selection and add to entry """
        self.dxf_file = filedialog.askopenfilename(title="DXF fájl kiválasztása", filetypes=[("DXF files", "*.dxf")])
        self.dxf_entry.delete(0, tk.END)
        self.dxf_entry.insert(0, self.dxf_file)

    def select_out(self):
        """ output folder selection and add to entry """
        self.out_dir = filedialog.askdirectory(title="Cél könyvtár kiválasztása")
        self.out_entry.delete(0, tk.END)
        self.out_entry.insert(0, self.out_dir)

    def go(self):
        """ check entries and run conversion """
        dxf_name = self.dxf_entry.get()
        if not path.exists(dxf_name):
            tk.messagebox.showerror(title="Hiba", message="DXF fájl nem létezik")
            return
        block_name = self.blk_entry.get()
        if len(block_name) == 0:
            tk.messagebox.showerror(title="Hiba", message="Blokknév minta üres")
            return
        out_path = self.out_entry.get()
        if not path.exists(out_path):
            tk.messagebox.showerror(title="Hiba", message="Cél könyvtár nem létezik")
            return
        out_type = self.otyp_var.get()
        try:
            width = int(self.wid_entry.get())
        except:
            tk.messagebox.showerror(title="Hiba", message="Hibás szélesség")
            return
        try:
            height = int(self.hei_entry.get())
        except:
            tk.messagebox.showerror(title="Hiba", message="Hibás magasság")
            return
        try:
            scale = float(self.sca_entry.get())
        except:
            tk.messagebox.showerror(title="Hiba", message="Hibás méret szorzó")
            return
        try:
            lwidth = int(self.lwi_entry.get())
        except:
            tk.messagebox.showerror(title="Hiba", message="Hibás vonalvastagság")
            return
        color = self.col_entry.get()
        if len(color) == 0:
            tk.messagebox.showerror(title="Hiba", message="Szín üres")
            return
        b = Block2(dxf_name, block_name, out_path, out_type,
                   width, height, False, scale, lwidth, color)
        b.convert()
        exit()

if __name__ == "__main__":
    conv = Blk2SvgGui()
    conv.mainloop()
