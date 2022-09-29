#! /usr/bin/env python3
"""
    Copy all entites from one DXF drawing to another
    the layer and th inserted block names are preserved but
    the layer and block tables are not copied
"""
import sys
import argparse
import ezdxf
from ezdxf.addons import Importer

BYLAYER_COLOR = 256   # BYLAYER color
BYLAYER_LTYPE = "BYLAYER" # BYLAYER linetype
# supported entiies
ENTITIES = ['POINT', 'INSERT', 'TEXT', 'MTEXT', 'LINE', 'LWPOLYLINE',
            'MLINE', 'MPOLYGON', 'ARC', 'CIRCLE', 'DIMENSION',
            'ARCDIMENSION', 'ELLIPSE', 'HATCH', 'INSERT', 'LEADER',
            'POLYLINE', 'REGION', 'SHAPE', 'SOLID', 'SPLINE', 'TRACE']

class Cp2Templ():
    """
        :param dxf_file: entities are copied from this file
        :param template_file: entities are copied to this file
        :param out_file: the template is saved using this name
    """
    def __init__(self, dxf_file, template_file, out_file):
        """ intialize """
        self.dxf_file = dxf_file
        self.template_file = template_file
        self.out_file = out_file
        try:
            self.doc = ezdxf.readfile(dxf_file)
        except IOError:
            print(f"*** ERROR Not a DXF file or a generic I/O error: {dxf_file}")
            sys.exit()
        except ezdxf.DXFStructureError:
            print(f"*** ERROR Invalid or corrupted DXF file: {dxf_file}")
            sys.exit()
        try:
            self.templ = ezdxf.readfile(template_file)
        except IOError:
            print(f"*** ERROR Not a DXF file or a generic I/O error: {template_file}")
            sys.exit()
        except ezdxf.DXFStructureError:
            print(f"*** ERROR Invalid or corrupted DXF file: {template_file}")
            sys.exit()

    def copy(self):
        """ Copy entities is layer/block match
        """
        importer = Importer(self.doc, self.templ)
        # blocks in template
        templ_blocks = [block.name for block in self.templ.blocks]
        # layers in template
        templ_layers = [layer.dxf.name for layer in self.templ.layers]
        msp = self.doc.modelspace() # source drawing modespace
        templ_doc = self.templ.modelspace()
        for entity in msp:
            e_typ = entity.dxftype()
            e_layer = entity.dxf.layer
            if e_typ not in ENTITIES:
                print(f'unsupported entitiy skipped: {e_typ}')
                continue    # skip unsupported entities
            if e_layer not in templ_layers:
                print(f'no layer in template drawing entity skipped {e_layer}')
                continue    # skip entity on missing layer
            if e_typ == 'INSERT' and entity.dxf.name not in templ_blocks:
                print(f'no block definition in template drawing skipped {entity.dxf.name}')
                continue    # skip missing blocks in template
            if entity.is_supported_dxf_attrib('color'):
                entity.dxf.color = BYLAYER_COLOR
            if entity.is_supported_dxf_attrib('linetype'):
                entity.dxf.linetype = BYLAYER_LTYPE
            importer.import_entity(entity, templ_doc)
        importer.finalize()
        try:
            self.templ.saveas(self.out_file)
        except:
            print("Error writing DXF file, try to convert the source DXF files using ODAFileConverter before processing")

if __name__ == "__main__":
    # process command line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('name', metavar='file_name', type=str, nargs=1,
                        help='DXF file to copy from')
    parser.add_argument('-t', '--template', type=str, required=True,
                        help='Template DXF to copy to')
    parser.add_argument('-o', '--out_file', type=str, required=True,
                        help='output file name')
    args = parser.parse_args()
    CT = Cp2Templ(args.name[0], args.template, args.out_file)
    CT.copy()
