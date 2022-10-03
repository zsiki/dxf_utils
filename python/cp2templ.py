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
        :param layer_table: translator table for layer names
        :param block_table: translator table for block names
    """
    def __init__(self, dxf_file, template_file, out_file, layer_table,
                 block_table):
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
        self.layer_table = None
        if layer_table:
            self.layer_table = self.load_table(layer_table)
        self.block_table = None
        if block_table:
            self.block_table = self.load_table(block_table)

    @staticmethod
    def load_table(file_name):
        """ load two column translator table for layers or blocks
            fields are separated by semicolon (;)
            first column contains the name in original dxf file
            second column contains the name in the template file
        """
        try:
            f = open(file_name, "r")
        except:
            print(f"translator table not loaded and not used: {file_name}")
            return None
        table = {}
        for line in f:
            lst = line.strip('\n\r\t ').split(';')
            if len(lst) != 2:
                print("Translator table line skipped:\n{line}")
                continue
            table[lst[0]] = lst[1]
        f.close()
        return table

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
            if self.layer_table and e_layer in self.layer_table:
                e_layer = self.layer_table[e_layer] # translate layer name
            if e_typ not in ENTITIES:
                print(f'unsupported entitiy skipped: {e_typ}')
                continue    # skip unsupported entities
            if e_layer not in templ_layers:
                print(f'no layer in template drawing entity skipped {e_layer}')
                continue    # skip entity on missing layer
            if e_typ == 'INSERT':
                b_name = entity.dxf.name
                if self.block_table and b_name in self.block_table:
                    b_name = self.block_table[b_name]
                if b_name not in templ_blocks:
                    print(f'no block definition in template drawing skipped {b_name}')
                    continue    # skip missing blocks in template
            if entity.is_supported_dxf_attrib('layer'):
                entity.dxf.layer = e_layer
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
                        help='output DXF file name')
    parser.add_argument('-l', '--layer_table', type=str, default=None,
                        help='Layer name translator table')
    parser.add_argument('-b', '--block_table', type=str, default=None,
                        help='Block name translator table')
    args = parser.parse_args()
    CT = Cp2Templ(args.name[0], args.template, args.out_file,
                  args.layer_table, args.block_table)
    CT.copy()
