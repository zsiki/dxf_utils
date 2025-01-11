#! /usr/bin/env python3
"""
    Create a DXF file from a DXF file keeping seelected entities and layers,
    a space separated lists can be given to select layers and entity types,
    use -- to close layer or entity list before input file,
    layer names and entity types are case insensitive

    python dxf_filter.py --layers 0 1 --entities LINE TEXT -- input.dxf
    python dxf_filter.py --layers 0 1 --entities LINE TEXT --target out.dxf input.dxf

    TODO LWPOLYLINE not in target
"""
import sys
import os.path
import argparse
import ezdxf
from ezdxf.addons import Importer

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('name', metavar='file_name', type=str, nargs=1,
                        help='DXF file to process')
    parser.add_argument('-l', '--layers', nargs='+', default=[],
                        help='Layers to copy target')
    parser.add_argument('-e', '--entities', nargs='+', default=[],
                        help='Entities to copy tartget')
    parser.add_argument('-t', '--target', default=None,
                        help='Target DXF file')
    args = parser.parse_args()

    if args.target is None:
        args.target = os.path.splitext(args.name[0])[0] + '_filtered.dxf'
    # convert names to upper case
    entities = [a.upper() for a in args.entities]
    layers = [a.upper() for a in args.layers]

    try:
        sdoc = ezdxf.readfile(args.name[0])
    except IOError:
        print(f"Not a DXF file or a generic I/O error: {args.name[0]}")
        sys.exit(1)
    except ezdxf.DXFStructureError:
        print(f"Invalid or corrupted DXF file: {args.names[0]}")
        sys.exit(2)

#    tdoc = ezdxf.new()
    tdoc = ezdxf.new('AC1009')
    importer = Importer(sdoc, tdoc)

    # import tables from source
    # get layers, linetypes, tyles tables from source
    importer.import_tables(('layers', 'linetypes', 'styles'))
    # get layer table from source
#    importer.import_table('layers', '*')
    # collect block names from source
    # ...
    # get block definitions from source
#    importer.import_blocks()
    smsp = sdoc.modelspace()
    tmsp = tdoc.modelspace()
    for entity in smsp:
        if (len(entities) == 0 or entity.dxftype() in entities) and \
           (len(layers) == 0 or entity.dxf.layer.upper() in layers):
            importer.import_entity(entity, tmsp)

    importer.finalize()
    tdoc.saveas(args.target)
