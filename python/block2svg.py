#! /usr/bin/env python3

""" convert DXF block entities into SVG XML files """

# svgwrite pypi
# drawSvg pypi
# ogr2ogr cannot write SVG :(
# filled shape -> SVG <path>/<polygon>
# line/polyline -> SVG <line>/<polyline>

import os
import fnmatch
import argparse
import ezdxf
import drawSvg as draw

LINE_WIDTH = 10     # line width in SVG
COLOR = "black"

def block2svg(block, scale=100, width=500, height=500):
    """ export block to SVG

        :param block: block definition
        :param scale: scale for CAD coordinates
        :param width: width of SVG
        :param height: height of SVG
        :returns: svg object
    """
    d = draw.Drawing(width, height, origin='center')    # initialize SVG
    x0, y0, _ = block.base_point    # basepoint of block
    for entity in block:
        typ = entity.dxftype()
        if typ == "LINE":
            x1 = (entity.dxf.start[0] - x0) * scale
            y1 = (entity.dxf.start[1] - y0) * scale
            x2 = (entity.dxf.end[0] - x0) * scale
            y2 = (entity.dxf.end[1] - y0) * scale
            d.append(draw.Lines(x1, y1, x2, y2, close=False,
                                stroke_width=LINE_WIDTH, stroke=COLOR))
        elif typ == "CIRCLE":
            xc = (entity.dxf.center[0] - x0) * scale
            yc = (entity.dxf.center[1] - y0) * scale
            r = entity.dxf.radius * scale
            d.append(draw.Circle(xc, yc, r, fill='none',
                                 stroke_width=LINE_WIDTH, stroke=COLOR))
        elif typ == "ARC":
            xc = (entity.dxf.center[0] - x0) * scale
            yc = (entity.dxf.center[1] - y0) * scale
            r = entity.dxf.radius * scale
            d.append(draw.Arc(xc, yc, r, entity.dxf.start_angle,
                              entity.dxf.end_angle, cw=False, fill='none',
                              stroke_width=LINE_WIDTH, stroke=COLOR))
        elif typ == "TEXT":
            pos = entity.get_pos()
            x = (pos[1][0] - x0) * scale
            y = (pos[1][1] - y0) * scale
            h = entity.dxf.height * scale
            d.append(draw.Text(entity.dxf.text, h, x, y, fill=COLOR))
        elif typ == "HATCH":
            # only external border is considered
            if entity.dxf.solid_fill == 1:
                p = draw.Path(stroke_width=LINE_WIDTH, stroke=COLOR, 
                              fill=COLOR)
                first = True
                if isinstance(entity.paths.paths[0], ezdxf.entities.boundary_paths.PolylinePath):
                    for v in entity.paths.paths[0].vertices:
                        if first:
                            p.M((v[0] - x0) * scale, (v[1] - y0) * scale)
                            first = False
                        else:
                            p.L((v[0] - x0) * scale, (v[1] - y0) * scale)
                elif isinstance(entity.paths.paths[0], ezdxf.entities.boundary_paths.EdgePath):
                    for edge in entity.paths.paths[0].edges:
                        if isinstance(edge, ezdxf.entities.boundary_paths.LineEdge):
                            if first:
                                p.M((edge.start_point[0] - x0) * scale, (edge.start_point[1] - y0) * scale)
                                first = False
                            p.L((edge.end_point[0] - x0) * scale, (edge.end_point[1] - y0) * scale)
                        elif isinstance(edge, ezdxf.entities.boundary_paths.ArcEdge):
                            if edge.end_angle > 359.9: edge.end_angle = 359.9
                            p.arc((edge.center[0] - x0) * scale, (edge.center[1] - y0) * scale,
                                  edge.radius * scale, edge.start_angle, edge.end_angle)
                                  #includeM=first)
                            first = False
                else:
                    print('Unsupported HATCH boundary type')
                    continue
                d.append(p)
            else:
                print('HATCH with solid fill are only supported')
        elif typ == "LWPOLYLINE":
            p = []
            with entity.points() as points:
                for pp in points:
                    p.append((pp[0] - x0) * scale)
                    p.append((pp[1] - y0) * scale)
            if entity.closed:
                p.append(p[0])
                p.append(p[1])
            d.append(draw.Lines(*p, stroke=COLOR, stroke_width=LINE_WIDTH,
                                fill="none"))
        elif typ == "POLYLINE":
            if entity.get_mode() in ['AcDb2dPolyline', 'AcDb3dPolyline']:
                p = []
                for v in entity.vertices:
                    p.append((v.dxf.location[0] - x0) * scale)
                    p.append((v.dxf.location[1] - y0) * scale)
                if entity.is_closed:
                    p.append(p[0])
                    p.append(p[1])
                d.append(draw.Lines(*p, stroke=COLOR, stroke_width=LINE_WIDTH,
                                    fill="none"))
            else:
                print(f'Unsupported POLYLINE mode: {entity.get_mode()}, block: {block.name}')
        else:
            print(f'Unsupported entity type: {typ}, block: {block.name}')
    return d

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('name', metavar='file_name', type=str, nargs=1,
                        help='DXF file to process')
    parser.add_argument('-b', '--block', type=str, default='*',
                        help='glob pattern for block name, default=*')
    parser.add_argument('-o', '--out_path', type=str, default='.',
                        help='path to save SVG files to')
    parser.add_argument('-t', '--type', type=str, default='svg',
                        help='Output type svg/png, default=svg')
    parser.add_argument('-w', '--width', type=float, default=500.0,
                        help='SVG or image width, default=500')
    parser.add_argument('-e', '--height', type=float, default=500.0,
                        help='SVG or image height, default=500')
    parser.add_argument('-s', '--scale', type=float, default=80.0,
                        help='scale, default=80')
    args = parser.parse_args()
    if not os.path.isdir(args.out_path):
        raise argparse.ArgumentTypeError(f"Output path does not exists: {args.out_path}")
    if not os.access(args.out_path, os.W_OK):
        raise argparse.ArgumentTypeError(f"Output path is not writeable: {args.out_path}")
    if not args.type in ('png', 'svg'):
        raise argparse.ArgumentTypeError("Output type must be 'svg' or 'png'")

    doc = ezdxf.readfile(args.name[0])
    for block in doc.blocks:
        if not block.name.startswith("*"): # skip special blocks
            if fnmatch.fnmatch(block.name, args.block):
                print(block.name)
                res = block2svg(block, args.scale, args.width, args.height)
                if args.type == 'png':
                    res.savePng(os.path.join(args.out_path, block.name + '.' +
                                args.type))
                else:
                    res.saveSvg(os.path.join(args.out_path, block.name + '.' +
                                args.type))
