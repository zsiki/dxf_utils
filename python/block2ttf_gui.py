#!/usr/bin/env python3

"""
    Graphical user interface for blk2svg.py
    (c) Zoltan Siki siki (dot) zoltan (at) emk.bme.hu
"""

import os
import sys
import tkinter as tk
#from tkinter import ttk
#from tkinter import messagebox
from io import StringIO
from tkinter import filedialog
from txtwin import TxtWin
from block2ttf import Block2TTF

class Blk2TtfGui(tk.Tk):
    """ class to add GUI to block2ttf.py """

    def __init__(self):
        """ initialize
        """
        tk.Tk.__init__(self)
        self.dxf_file = ""
        self.out_dir = "."
        self.res_file = ""
        self.chcodes_file = ""
        self.title("Blokk -> TTF konverter")

        self.dxf_label = tk.Label(self, text="DXF input fájl: ")
        self.dxf_entry = tk.Entry(self, width=60)
        self.dxf_select = tk.Button(self, text="...", command=self.select_in)
        self.dxf_label.grid(row=0, column=0, sticky="e")
        self.dxf_entry.grid(row=0, column=1, sticky="w")
        self.dxf_select.grid(row=0, column=2, sticky="w")

        self.blk_label = tk.Label(self, text="Blokk név minta: ")
        self.blk_entry = tk.Entry(self, width=30)
        self.blk_entry.insert(0, "*")
        self.blk_label.grid(row=1, column=0, sticky="e")
        self.blk_entry.grid(row=1, column=1, sticky="w")

        self.out_label = tk.Label(self, text="TTF output fájl: ")
        self.out_entry = tk.Entry(self, width=60)
        self.out_select = tk.Button(self, text="...", command=self.select_out)
        self.out_label.grid(row=2, column=0, sticky="e")
        self.out_entry.grid(row=2, column=1, sticky="w")
        self.out_select.grid(row=2, column=2, sticky="w")

        self.chcodes_label = tk.Label(self, text="Karakterkód fájl: ")
        self.chcodes_entry = tk.Entry(self, width=60)
        self.chcodes_select = tk.Button(self, text="...", command=self.select_chcodes)
        self.chcodes_label.grid(row=3, column=0, sticky="e")
        self.chcodes_entry.grid(row=3, column=1, sticky="w")
        self.chcodes_select.grid(row=3, column=2, sticky="w")

        self.res_label = tk.Label(self, text="Üzenet fájl: ")
        self.res_entry = tk.Entry(self, width=60)
        self.res_select = tk.Button(self, text="...", command=self.select_res)
        self.res_label.grid(row=4, column=0, sticky="e")
        self.res_entry.grid(row=4, column=1, sticky="w")
        self.res_select.grid(row=4, column=2, sticky="w")

        self.font_label = tk.Label(self, text="Font név: ")
        self.font_entry = tk.Entry(self, width=30)
        self.font_entry.insert(0, "MMK-GGT jelkulcsok font")
        self.font_label.grid(row=5, column=0, sticky="e")
        self.font_entry.grid(row=5, column=1, sticky="w")

        self.unit_sper_em_label = tk.Label(self, text="M-négyzetenkénti egységek száma: ")
        self.unit_sper_em_entry = tk.Entry(self, width=10)
        self.unit_sper_em_entry.insert(0, "2048")
        self.unit_sper_em_label.grid(row=6, column=0, sticky="e")
        self.unit_sper_em_entry.grid(row=6, column=1, sticky="w")

        self.sca_label = tk.Label(self, text="Méret szorzó: ")
        self.sca_entry = tk.Entry(self, width=10)
        self.sca_entry.insert(0, "256")
        self.sca_label.grid(row=7, column=0, sticky="e")
        self.sca_entry.grid(row=7, column=1, sticky="w")

        self.lwi_label = tk.Label(self, text="Vonalvastagság: ")
        self.lwi_entry = tk.Entry(self, width=10)
        self.lwi_entry.insert(0, "32")
        self.lwi_label.grid(row=8, column=0, sticky="e")
        self.lwi_entry.grid(row=8, column=1, sticky="w")

        self.go_button = tk.Button(self, text="Indít", command=self.go)
        self.go_button.grid(row=9, column=2)

    def select_in(self):
        """ input file name selection and add to entry """
        self.dxf_file = filedialog.askopenfilename(title="DXF fájl kiválasztása",
                                                   filetypes=[("DXF files", "*.dxf")])
        self.dxf_entry.delete(0, tk.END)
        self.dxf_entry.insert(0, self.dxf_file)

    def select_out(self):
        """ output file name selection and add to entry """
        self.out_dir = filedialog.asksaveasfilename(title="Cél állomány (TTF) kiválasztása")
        # TODO add TTF extension
        self.out_entry.delete(0, tk.END)
        self.out_entry.insert(0, self.out_dir)

    def select_res(self):
        """ result file name selection and add to entry """
        self.res_file = filedialog.asksaveasfilename(title="Hibaüzenetek fájl kiválasztása",
                                                       filetypes=[("TXT files", "*.txt"),("All files", "*")])
        self.res_entry.delete(0, tk.END)
        self.res_entry.insert(0, self.res_file)

    def select_chcodes(self):
        """ character code file selection and add to entry """
        self.chcodes_file = filedialog.askopenfilename(title="Karakter kód fájl kiválasztása",
                                                       filetypes=[("TXT files", "*.txt"),("All files", "*")])
        self.chcodes_entry.delete(0, tk.END)
        self.chcodes_entry.insert(0, self.chcodes_file)

    def go(self):
        """ check entries and run conversion """
        dxf_name = self.dxf_entry.get()
        if not os.path.exists(dxf_name):
            tk.messagebox.showerror(title="Hiba", message="DXF fájl nem létezik")
            return
        block_name = self.blk_entry.get()
        if len(block_name) == 0:
            tk.messagebox.showerror(title="Hiba", message="Blokknév minta üres")
            return
        out_file = self.out_entry.get()
        if not os.access(out_file, os.W_OK):
            try:
                open(out_file, 'w').close()
                os.unlink(out_file)
            except:
                tk.messagebox.showerror(title="Hiba", message="Cél állományt nem lehet létrehozni")
                return
        chcode_file = self.chcodes_entry.get()
        if not os.path.exists(chcode_file):
            tk.messagebox.showerror(title="Hiba", message="Karakterkód fájl nem létezik")
            return
        try:
            fontname = str(self.font_entry.get())
        except:
            tk.messagebox.showerror(title="Hiba", message="Hibás font név")
            return
        try:
            unit_per_em = int(self.unit_sper_em_entry.get())
        except:
            tk.messagebox.showerror(title="Hiba", message="Hibás M-négyzetenkénti egységek száma")
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

        res_file = self.res_entry.get()
        if len(res_file) == 0:
            res_file = "stdout"
        old_stdout = sys.stdout
        sys.stdout = string_io = StringIO()
        b = Block2TTF(dxf_name, chcode_file, block_name, out_file, fontname,
                  unit_per_em, scale, lwidth, False)
        b.convert()
        txt_out = string_io.getvalue()
        if len(txt_out) > 0:
            TxtWin(txt_out, self)
        sys.stdout = old_stdout
        self.quit()

if __name__ == "__main__":
    conv = Blk2TtfGui()
    conv.mainloop()
