#!/usr/bin/env python3
""" create a csv file from dxf TEXT entites
    x, y, z, alignment, rotation, layer and text are written to the output
"""

import sys
import ezdxf
import os.path

def print_text(e, fo):
    """ print data of an TEXT entity

        :param e: entity to process
        :param fo: output file to write to
    """
    pos = e.get_pos()
    print(f'{pos[1][0]:.3f};{pos[1][1]:.3f};{pos[1][2]:.3f};{pos[0]};{e.dxf.rotation:.4f};{e.dxf.layer};{e.dxf.text}', file=fo)
    
def print_mtext(e, fo):
    """ print data of an MTEXT entity, multiline texts are separated by '|'

        :param e: entity to process
        :param fo: output file to write to
    """
    # TODO aligment is always 0
    pos = e.dxf.insert
    print(f'{pos[0]:.3f};{pos[1]:.3f};{pos[2]:.3f};0;{e.dxf.rotation:.4f};{e.dxf.layer};{"|".join(e.plain_text(split=True))}', file=fo)
    
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
# entity query for all MTEXT entities in modelspace
for e in msp.query("MTEXT"):
    print_mtext(e, fo)
