#! /usr/bin/env python3
"""
    Generate report from a DXF file
"""
import sys
import argparse
import numpy as np
import ezdxf

LAYER_FIELD = 32        # length of layer name in output
NUMBER_FIELD = 6        # length of entity counts in output

dxf2cad_version = {'AC1002': 'AutoCAD R2',
                   'AC1004': 'AutoCAD R9',
                   'AC1006': 'AutoCAD R10',
                   'AC1009': 'AutoCAD R11/R12',
                   'AC1012': 'AutoCAD R13',
                   'AC1014': 'AutoCAD R14',
                   'AC1015': 'AutoCAD R2000/R2002',
                   'AC1018': 'AutoCAD R2004/R2005/R2006',
                   'AC1021': 'AutoCAD R2007/R2008/R2009',
                   'AC1024': 'AutoCAD R2010/R2011/R2012',
                   'AC1027': 'AutoCAD R2013/R2014/R2015/R2016/R2017',
                   'AC1032': 'AutoCAD R2018/R2019/R2020/R2021/R2022/R2023'}

def cad_version(dxf_version):
    """ return AuoCAD version from DXF version
        :param dxf_version: DXF version from dxf file
    """
    if dxf_version in dxf2cad_version:
        return dxf2cad_version[dxf_version]
    return ''

class DxfInfo():
    """ class to collect DXF information

        :param dxf_file: the dxf file to process
        :param template_file: dxf file to compare layers and blocks
        :param output_file: output txt file
    """
    def __init__(self, dxf_file, template_file, output_file):
        """ initialize object """
        self.dxf_file = dxf_file
        self.template_file = template_file
        # load dxf
        try:
            self.doc = ezdxf.readfile(dxf_file)
        except IOError:
            print(f"*** ERROR Not a DXF file or a generic I/O error: {dxf_file}")
            sys.exit()
        except ezdxf.DXFStructureError:
            print(f"*** ERROR Invalid or corrupted DXF file: {dxf_file}")
            sys.exit()
        # load template dxf if any
        self.templ = None
        if template_file:
            try:
                self.templ = ezdxf.readfile(template_file)
            except IOError:
                print(f"*** ERROR Not a DXF file or a generic I/O error: {template_file}")
                sys.exit()
            except ezdxf.DXFStructureError:
                print(f"*** ERROR Invalid or corrupted DXF file: {template_file}")
                sys.exit()
        if output_file == 'stdout':
            self.out = sys.stdout
        else:
            try:
                self.out = open(output_file, 'w')
            except:
                print(f"*** ERROR creating output file: {output_file}")
                sys.exit()
        self.entities = None
        self.layers = None
        self.blocks = None

    def print_row(self, lay, lay_row):
        """ print a row of table

            :param lay: layer name
            :param lay_row: numpy vector of entity counts
        """
        print(f'{lay[:LAYER_FIELD]:{LAYER_FIELD}s}', end=' ', file=self.out)
        for i in range(lay_row.shape[0]):
            print(f'{lay_row[i]:{NUMBER_FIELD}d}', end=' ', file=self.out)
        print(file=self.out)

    def layer_compare(self):
        """ compare layers in doc and template """
        doc_layers = [layer.dxf.name for layer in self.doc.layers]
        templ_layers = [layer.dxf.name for layer in self.templ.layers]
        missing = [name for name in templ_layers if name not in doc_layers]
        extra = [name for name in doc_layers if name not in templ_layers]
        print(80 * '-', file=self.out)
        print(f"Template: {self.template_file}", file=self.out)
        if len(missing) > 0:
            print("Missing layers:", file=self.out)
            for layer in missing:
                print(layer, file=self.out)
        if len(extra) > 0:
            print("Extra layers:", file=self.out)
            for layer in extra:
                print(layer, file=self.out)

    def block_compare(self):
        """ compare blocks in doc and template """
        doc_blocks = [block.name for block in self.doc.blocks]
        templ_blocks = [block.name for block in self.templ.blocks]
        missing = [name for name in templ_blocks if name not in doc_blocks]
        extra = [name for name in doc_blocks if name not in templ_blocks]
        print(80 * '-', file=self.out)
        print(f"Template: {self.template_file}", file=self.out)
        if len(missing) > 0:
            print("Missing blocks:", file=self.out)
            for block in missing:
                print(block, file=self.out)
        if len(extra) > 0:
            print("Extra blocks:", file=self.out)
            for block in extra:
                print(block, file=self.out)

    def layer_entity(self):
        """ collect entities by layer into a dictionary, the dictionary
            has tuple indices composed of layer and entity type
        """
        msp = self.doc.modelspace()
        entities = {}
        for entity in msp:
            e_typ = entity.dxftype()
            try:
                layer = entity.dxf.layer
            except:     # TODO no layer for mpolygon from ezdxf
                print(f'missing layer for entity {e_typ} skipped')
                continue
            if (entity.dxf.layer, e_typ) not in entities:
                entities[(layer, e_typ)] = 0
            entities[(entity.dxf.layer, e_typ)] += 1
        # collect different entity types
        self.entities = entities

    def dxf_info(self):
        """ collect and print layer/entity info of a DXF file
        """
        print(80 * '-', file=self.out)
        print(f"{self.dxf_file} version: {self.doc.dxfversion} {cad_version(self.doc.dxfversion)}", file=self.out)
        e_min = self.doc.header['$EXTMIN']
        e_max = self.doc.header['$EXTMAX']
        print(f"EXTMIN: {e_min[0]:.3f} {e_min[1]:.3f} {e_min[2]:.3f}", file=self.out)
        print(f"EXTMAX: {e_max[0]:.3f} {e_max[1]:.3f} {e_max[2]:.3f}", file=self.out)
        if self.entities is None:
            self.layer_entity()
        keys = sorted(self.entities.keys())
        entities_found = sorted(list({key[1] for key in keys}))
        num_ent_types = len(entities_found)
        entity_dict = {e[1]:e[0] for e in enumerate(entities_found)}
        # print header of table
        print(f'\n{"Layer":{LAYER_FIELD}s}', end=' ', file=self.out)
        layer_row = np.zeros(num_ent_types, dtype=np.int32)
        total_row = np.zeros(num_ent_types, dtype=np.int32)
        for e in entities_found:
            print(f'{e[:NUMBER_FIELD]:>{NUMBER_FIELD}s}', end=' ', file=self.out)
        print(file=self.out)
        last_layer = ""
        for key in keys:
            layer = key[0]
            if layer != last_layer and np.sum(layer_row) > 0:
                self.print_row(last_layer, layer_row)
                total_row += layer_row
                layer_row.fill(0)           # intialize row
            layer_row[entity_dict[key[1]]] = self.entities[key]
            last_layer = layer
        if np.sum(layer_row) > 0:
            self.print_row(last_layer, layer_row)
            total_row += layer_row
        print(file=self.out)
        self.print_row("TOTAL", total_row)

if __name__ == '__main__':
    # process command line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('name', metavar='file_name', type=str, nargs=1,
                        help='DXF file to process')
    parser.add_argument('-t', '--template', type=str, default=None,
                        help='Template DXF to compare layers, blocks (optional)')
    parser.add_argument('-o', '--out_file', type=str, default='stdout',
                        help='output file name, default: stdout')
    args = parser.parse_args()
    DI = DxfInfo(args.name[0], args.template, args.out_file)
    DI.dxf_info()
    if args.template:
        DI.layer_compare()
        DI.block_compare()
