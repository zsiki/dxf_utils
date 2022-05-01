#! /usr/bin/env python3
"""
    Generate report from a DXF file
"""
import sys
import glob
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

def dxf_info(file_name):
    """ collect and print layer/entity info of a DXF file

        :param dxf_name: name of input file
    """
    try:
        doc = ezdxf.readfile(file_name)
    except IOError:
        print(f"*** ERROR Not a DXF file or a generic I/O error: {file_name}")
        return
    except ezdxf.DXFStructureError:
        print(f"*** ERROR Invalid or corrupted DXF file: {file_name}")
        return
    print(80 * '-')
    print(file_name)
    print('EXTMIN: ', doc.header['$EXTMIN'])
    print('EXTMAX: ', doc.header['$EXTMAX'])
    msp = doc.modelspace()
    entities = {}
    for entity in msp:
        e_typ = entity.dxftype()
        if (entity.dxf.layer, e_typ) not in entities:
            entities[(entity.dxf.layer, e_typ)] = 0
        entities[(entity.dxf.layer, e_typ)] += 1
    # collect different entity types
    keys = sorted(entities.keys())
    entities_found = sorted(list({key[1] for key in keys}))
    num_ent_types = len(entities_found)
    entity_dict = {e[1]:e[0] for e in enumerate(entities_found)}
    # print header of table
    print(f'\n{"Layer":{LAYER_FIELD}s}', end=' ')
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
    print()
    print_row("TOTAL", total_row)

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print('Usage: dxfinfo.py dxf_file [dxf_file [...]]')
        sys.exit()
    for arg in sys.argv[1:]:
        glob_names = glob.glob(arg)     # extend */? for windows
        if len(glob_names) == 0:
            print(f'*** ERROR File not found: {arg}')
            continue
        for name in glob.glob(arg):     # glob extension for windows
            dxf_info(name)
