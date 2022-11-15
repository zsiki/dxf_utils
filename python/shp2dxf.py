#! /usr/bin/env python3
"""
    shp2dxf
    Convert several shp files to a single dxf file
    based on a rule file

    rule file may have from 2 to 5 fields separated by semicolon(;)
    1st field: unique part of the shape file as glob pattern to use as source for this rule
    2nd field: target layer name in destination DXF file
    3rd field: attribute name(s) to use in rule (optional), names separated by &
    4th field: attribute value(s) for rule (optional)
    5th field: block name to insert in case of point shape (optional)
    shp_id dxf_layer shp_attr_name shp_attr_value dxf_block_name

    Sample rules:


"""
import sys
import os.path
import glob
import fnmatch
import argparse
from math import isclose
import ezdxf
from osgeo import ogr

# column index fro rules
SHP_ID = 0
DXF_LAYER = 1
SHP_ATTR_NAMES = 2
SHP_ATTR_VALUES = 3
DXF_BLOCK_NAME = 4

# shape types
SHP_POINT = 1
SHP_LINE = 2
SHP_POLY = 3
SHP_POINTZ = 11
SHP_LINEZ = 13
SHP_POLYZ = 15
SHP_POINTM = 21
SHP_LINEM = 23
SHP_POLYM = 25
SHP_TYPES = (SHP_POINT, SHP_LINE, SHP_POLY, SHP_POINTZ, SHP_LINEZ, SHP_POLYZ,
             SHP_POINTM, SHP_LINEM, SHP_POLYM)

class Shp2Dxf():
    """ class to convert a group of SHP files to a single DXF file

        :param shp_dir: input folder of shape files to convert
        :param dxf_template: empty template drawing with layer and block definitions
        :param dxf_out: name of output DXF file
        :param rules: name of the text file with rules
        :param encoding: encoding for rules file
        :param verbose: verbose output to stdout
    """

    def __init__(self, shp_dir, dxf_template, dxf_out, rules, encoding, verbose):
        """ initialize """
        # get name of shape files
        self.shp_paths = glob.glob(os.path.join(shp_dir, '*.shp'))
        self.shp_names = [os.path.split(path)[1] for path in self.shp_paths]
        self.doc = ezdxf.readfile(dxf_template) # load template DXF
        if len(os.path.splitext(dxf_out)) == 0:
            dxf_out += '.dxf'
        self.dxf_out = dxf_out
        self.rules = self.load_rules(rules, encoding)     # load rules
        self.verbose = verbose

    @staticmethod
    def load_rules(rules, encoding):
        """ load the conversion rules from an ASCII file
            shp_id dxf_layer shp_attr_name shp_attr_value dxf_block_name
            shp_id is a glob pattern for the shp file name
        """
        res = []
        with open(rules, 'r', encoding=encoding) as rule_file:
            for line in rule_file.readlines():
                line = line.strip(' \t\n\r')
                if line.startswith('#'):
                    continue    # skip comment line
                if len(line) == 0:
                    continue    # skip empty line
                line_list = line.split(';')
                if len(line_list) < 2:
                    print(f"invalid line: {line}")
                    continue
                # check empty and replace with None
                line_list = [None if len(x.strip()) == 0 else x.strip() for x in line_list]
                if len(line_list) > 3 and line_list[2] is not None and \
                   line_list[3] is not None:
                    col_list = [x.strip().lower() for x in line_list[2].split('&')]
                    tmp_list = [x.strip() for x in line_list[3].split('&')]
                    if len(col_list) != len(tmp_list):
                        print(f'ERROR in rule skipped\n{line}')
                        continue
                    val_lists = []
                    for vals in tmp_list:
                        val_lists.append([x.strip() for x in vals.split(',')])
                    line_list[2] = col_list
                    line_list[3] = val_lists
                res.append(line_list)
        res.sort()  # sort by shp name
        return res

    @staticmethod
    def is_2d(pnts):
        """ check if points are in 2D
            :param pnts: list of point coordinates [(x1, y1, z1), (x2, y2, z2), ...]
            :returns: True/False 2D/3D
        """
        z_val = pnts[0][2]
        for pnt in pnts[1:]:
            if not isclose(z_val, pnt[2]):
                return False
        return True

    def shpid2paths(self, shp_id):
        """ extend shp id to path list

            :param shp_id: glob pattern to match to shape names
        """
        found_path = []
        for name, path in zip(self.shp_names, self.shp_paths):
            if fnmatch.fnmatch(name, shp_id):   # glob match?
                found_path.append(path)
        return found_path

    @staticmethod
    def filter(feature, attr_names, attr_values):
        """ check condition for attributes

            :param feature: feature from shp file
            :param attr_names: list of column names for condition
            :param attr_values: list of list with valid values
            :returns: True/False
        """
        for attr_name, attr_value in zip(attr_names, attr_values):
            if str(feature.GetField(attr_name)) not in attr_value:
                return False
        return True

    def convert(self):
        """ convert the shp files to dxf using rules """
        templ_layers = [layer.dxf.name for layer in self.doc.layers]
        templ_blocks = [block.name for block in self.doc.blocks]
        msp = self.doc.modelspace() # modelspace to write to
        for rule in self.rules:     # go through rules
            shp_id = rule[SHP_ID]           # shape id (unique part of the name)
            dxf_layer = rule[DXF_LAYER]     # target dxf layer
            if dxf_layer not in templ_layers:
                print(f"Missing layer in DXF template: {dxf_layer}")
                print("Rule skipped")
                continue
            shp_paths = self.shpid2paths(shp_id)
            if len(shp_paths) == 0:
                print(f"No match for shp name pattern: {shp_id}")
                print("Rule skipped")
                continue
            shp_attr_names = None
            if len(rule) > 2 and rule[SHP_ATTR_NAMES] is not None:
                shp_attr_names = rule[SHP_ATTR_NAMES]
            shp_attr_values = None
            if len(rule) > 3 and rule[SHP_ATTR_VALUES] is not None:
                shp_attr_values = rule[SHP_ATTR_VALUES]
            dxf_block_name = None
            if len(rule) > 4 and rule[DXF_BLOCK_NAME] is not None:
                dxf_block_name = rule[DXF_BLOCK_NAME]
                if dxf_block_name not in templ_blocks:
                    print(f"Missing block definition in DXF template: {dxf_block_name}")
                    print("Rule skipped")
                    continue
            for shp_path in shp_paths:   # iprocess input shp files
                if self.verbose:
                    print(f"{shp_path} to {dxf_layer}")
                shp_file = ogr.Open(shp_path)
                shp_layer = shp_file.GetLayer(0)
                geom_type = shp_layer.GetGeomType()
                if geom_type not in SHP_TYPES:
                    print(f"Invalid Shape type {geom_type} in {shp_path}")
                    print(f"Rule skippedi for {shp_path}")
                    shp_file = None     # close shp
                    continue    # skip unsupported shape type
                # collect field names
                field_names = [field.name.lower() for field in shp_layer.schema]
                if shp_attr_names:
                    for shp_attr_name in shp_attr_names:
                        if shp_attr_name not in field_names:
                            print(f"Invalid attribute name {shp_attr_name}")
                            print(f"Rule skippedi for {shp_path}")
                            shp_file = None     # close shp
                            continue    # attribute not in shape file skip
                n_feature = 0
                for feature in shp_layer:
                    if shp_attr_names is None or shp_attr_values is None or \
                       self.filter(feature, shp_attr_names, shp_attr_values):
                        n_feature += 1  # count of converted items
                        # copy geometry to target layer
                        geom = feature.GetGeometryRef()
                        if geom_type in (SHP_POINT, SHP_POINTZ, SHP_POINTM):
                            pnt = geom.GetPoint(0)
                            if dxf_block_name:
                                msp.add_blockref(dxf_block_name, pnt,
                                                 dxfattribs={'layer': dxf_layer})
                            else:
                                msp.add_point(pnt, dxfattribs={'layer': dxf_layer})
                        elif geom_type in (SHP_LINE, SHP_LINEZ, SHP_LINEM):
                            pnts = [geom.GetPoint(i) for i in range(geom.GetPointCount())]
                            if len(pnts) > 1:
                                if self.is_2d(pnts):
                                    pnts = [(p[0], p[1]) for p in pnts]
                                    msp.add_lwpolyline(pnts, dxfattribs={'layer': dxf_layer})
                                else:
                                    msp.add_polyline3d(pnts, dxfattribs={'layer': dxf_layer})
                        elif geom_type in (SHP_POLY, SHP_POLYZ, SHP_POLYM):
                            pnts = [geom.GetPoint(i) for i in range(geom.GetPointCount())]
                            if len(pnts) > 1:
                                if self.is_2d(pnts):
                                    pnts = [(p[0], p[1]) for p in pnts]
                                    msp.add_lwpolyline(pnts, close=True,
                                                       dxfattribs={'layer': dxf_layer})
                                else:
                                    msp.add_polyline3d(pnts, close=True,
                                                       dxfattribs={'layer': dxf_layer})
                if self.verbose:
                    print(f"{n_feature} features added to DXF")
                shp_file = None
        self.doc.saveas(self.dxf_out)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', metavar='shp_dir', type=str, nargs=1,
                        help='Folder of shape files to convert')
    parser.add_argument('-r', '--rules', type=str,
                        help='Conversion rules')
    parser.add_argument('-o', '--out_dxf', type=str,
                        help='Output DXF file')
    parser.add_argument('-t', '--template', type=str,
                        help='Template for DXF output')
    parser.add_argument('-e', '--encoding', type=str, default=sys.getdefaultencoding(),
                        help=f'Encoding for rules file, default {sys.getdefaultencoding()}')
    parser.add_argument('-v', '--verbose', action="store_true",
                        help='verbose output to stdout')
    args = parser.parse_args()
    S2D = Shp2Dxf(args.dir[0], args.template, args.out_dxf, args.rules,
                  args.encoding, args.verbose)
    S2D.convert()
