#! /usr/bin/env python3
"""
    shp2dxf
    Convert several shp files to a single dxf file
    based on a rule file

    rule file may have from 2 to 5 fields separated by semicolon(;)
    1st field: unique part of the shape file as glob pattern to use as source for this rule
    2nd field: target layer name in destination DXF file
    3rd field: attribute name to use in rule (optional)
    4th field: attribute value for rule (optional)
    5th field: block name to insert in case of point shape (optional)
    shp_id dxf_layer shp_attr_name shp_attr_value dxf_block_name

"""
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
SHP_ATTR_NAME = 2
SHP_ATTR_VALUE = 3
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
    """

    def __init__(self, shp_dir, dxf_template, dxf_out, rules):
        """ initialize """
        # get name of shape files
        self.shp_paths = glob.glob(os.path.join(shp_dir, '*.shp'))
        self.shp_names = [os.path.split(path)[1] for path in self.shp_paths]
        self.doc = ezdxf.readfile(dxf_template) # load template DXF
        if len(os.path.splitext(dxf_out)) == 0:
            dxf_out += '.dxf'
        self.dxf_out = dxf_out
        self.rules = self.load_rules(rules)     # load rules

    @staticmethod
    def load_rules(rules):
        """ load the conversion rules from an ASCII file
            shp_id dxf_layer shp_attr_name shp_attr_value dxf_block_name
            shp_id is a unique part of the shp file name
        """
        res = []
        with open(rules, 'r') as rule_file:
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
                if len(line_list) > 3 and line_list[3] is not None:
                    if line_list[3].find(',') > -1: # coma separated values
                        val_list = [x.strip() for x in line_list[3].split(',')]
                    else:
                        val_list = [line_list[3]]
                    line_list[3] = val_list
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

    def shpid2path(self, shp_id):
        """ extend shp id to path """
        for name, path in zip(self.shp_names, self.shp_paths):
            #if name.find(shp_id) > -1:
            if fnmatch.fnmatch(name, shp_id):
                return path
        return None

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
                continue
            shp_path = self.shpid2path(shp_id)
            shp_attr_name = None
            if len(rule) > 2 and rule[SHP_ATTR_NAME] is not None:
                shp_attr_name = rule[SHP_ATTR_NAME].lower()
            shp_attr_value = None
            if len(rule) > 3 and rule[SHP_ATTR_VALUE] is not None:
                shp_attr_value = rule[SHP_ATTR_VALUE]
            dxf_block_name = None
            if len(rule) > 4 and rule[DXF_BLOCK_NAME] is not None:
                dxf_block_name = rule[DXF_BLOCK_NAME]
                if dxf_block_name not in templ_blocks:
                    print(f"Missing block definition in DXF template: {dxf_block_name}")
                    continue
            if shp_path:   # is there an input shp?
                shp_file = ogr.Open(shp_path)
                shp_layer = shp_file.GetLayer(0)
                geom_type = shp_layer.GetGeomType()
                if geom_type not in SHP_TYPES:
                    print(f"Invalid Shape type {geom_type}")
                    shp_file = None     # close shp
                    continue    # skip unsupported shape type
                # collect field names (UPPER CASE)
                field_names = [field.name.lower() for field in shp_layer.schema]
                if shp_attr_name and shp_attr_name not in field_names:
                    print(f"Invalid attribute name {shp_attr_name}")
                    shp_file = None     # close shp
                    continue    # attribute not in shape file skip
                for feature in shp_layer:
                    if shp_attr_name is None or shp_attr_value is None or \
                       str(feature.GetField(shp_attr_name)) in shp_attr_value:
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
    args = parser.parse_args()
    S2D = Shp2Dxf(args.dir[0], args.template, args.out_dxf, args.rules)
    S2D.convert()
