#!/usr/bin/env python3
""" create a csv file from dxf BLOCK INSERT entites
    x, y, z, direction, layer and block_name are written to the output
"""

import sys
import ezdxf
import os.path

def print_ins(e, fo):
    """ print data of an INSERT entity

        :param e: entity to process
        :param fo: output file to write to
    """
    pos = e.dxf.insert
    print(f'{pos[0]:.3f};{pos[1]:.3f};{pos[2]:.3f};{e.dxf.rotation:.4f};{e.dxf.layer};{e.dxf.name}', file=fo)
    
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
print("x;y;z;DIRECTION;layer;NAME", file=fo)
msp = doc.modelspace()
# entity query for all INSERT entities in modelspace
for e in msp.query("INSERT"):
    print_ins(e, fo)
