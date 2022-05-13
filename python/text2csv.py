#!/usr/bin/env python3
""" create a csv file from dxf TEXT entites
    position (x, y, z, alignment, rotation, layer and text are written to the output
"""

import sys
import ezdxf
import os.path

def print_text(e, fo):
    pos = e.get_pos()
    print(f'{pos[1][0]:.3f};{pos[1][1]:.3f};{pos[1][2]:.3f};{pos[0]};{e.dxf.rotation:.4f};{e.dxf.layer};{e.dxf.text}', file=fo)
    
if len(sys.argv) < 2:
    print(f'Usage: {sys.argv[0]} input_dxf [output_csv]')
    sys.exit(0)

fin = sys.argv[1]
if len(sys.argv) < 3:
    fout = os.path.splitext(fin)[0] + '.csv'
else:
    fout = sys.argv[2]
try:
    doc = ezdxf.readfile(fin)
except IOError:
    print(f'DXF input failed {fin}')
    sys.exit(1)
try:
    fo = open(fout, 'w')
except:
    print(f'File creation failed {fout}')
    sys.exit(2)

# header for output
print("x;y;z;align;rotation;layer;text", file=fo)
msp = doc.modelspace()
# entity query for all TEXT entities in modelspace
for e in msp.query("TEXT"):
    print_text(e, fo)
