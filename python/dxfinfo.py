#! /usr/bin/env python3
"""
    Generate report from a DXF file
"""
import sys
import numpy as np
import ezdxf

LAYER_FIELD = 16        # length of layer name in output
NUMBER_FIELD = 6        # length of entity counts in output

def print_row(lay, lay_row):
    """ print a row of table

        :param lay: layer name
        :param lay_row: numpy vector of entity counts
    """
    print(f'{lay[:LAYER_FIELD]:{LAYER_FIELD}s}', end=' ')
    for i in range(lay_row.shape[0]):
        print(f'{lay_row[i]:{NUMBER_FIELD}d}', end=' ')
    print()

if len(sys.argv) < 2:
    print('Usage: dxfinfo.py dxf_file')
    sys.exit()
try:
    doc = ezdxf.readfile(sys.argv[1])
except IOError:
    print(f"Not a DXF file or a generic I/O error.")
    sys.exit(1)
except ezdxf.DXFStructureError:
    print(f"Invalid or corrupted DXF file.")
    sys.exit(2)

msp = doc.modelspace()
entities = {}
for entity in msp:
    e_typ = entity.dxftype()
    if (entity.dxf.layer, e_typ) not in entities:
        entities[(entity.dxf.layer, e_typ)] = 0
    entities[(entity.dxf.layer, e_typ)] += 1
# collect different entity types
keys = sorted(entities.keys())
entities_found = sorted(list(set([key[1] for key in keys])))
num_ent_types = len(entities_found)
entity_dict = {e[1]:e[0] for e in enumerate(entities_found)}
# print header of table
print(f'{"Layer":{LAYER_FIELD}s}', end=' ')
layer_row = np.zeros(num_ent_types, dtype=np.int32)
total_row = np.zeros(num_ent_types, dtype=np.int32)
for e in entities_found:
    print(f'{e[:NUMBER_FIELD]:>{NUMBER_FIELD}s}', end=' ')
print()
last_layer = ""
for key in keys:
    layer = key[0]
    if layer != last_layer and np.sum(layer_row) > 0:
        print_row(last_layer, layer_row)
        total_row += layer_row
        layer_row.fill(0)           # intialize row
    layer_row[entity_dict[key[1]]] = entities[key]
    last_layer = layer
if np.sum(layer_row) > 0:
    print_row(last_layer, layer_row)
    total_row += layer_row
print_row("TOTAL", total_row)
