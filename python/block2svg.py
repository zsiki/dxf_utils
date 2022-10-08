#! /usr/bin/env python3

""" convert DXF block entities into SVG XML or PNG files """

import sys
import os
import fnmatch
import argparse
import ezdxf
import drawSvg as draw
from math import hypot, sin, cos, atan, atan2, pi

class Block2():
    """ class to convert DXF blocks to other symbol formats

        :param dxf_name: input DXF to process
        :param block_name: glob pattern for block names to convert (* = all)
        :param out_path: path to folder to write SVGs/PNGs
        :param out_type: svg or png
        :param width: width of SVG
        :param height: height of SVG
        :param verbose: verbose output
        :param scale: scale for CAD coordinates
        :param lwidth: line width in SVG
        :param color: line and fill color in SVG
    """

    def __init__(self, dxf_name, block_name, out_path, out_type,
                 width, height, verbose, scale, lwidth, color):
        """ initialize """
        self.dxf_name = dxf_name
        self.block_name = block_name
        self.out_path = out_path
        self.out_type = out_type
        self.width = width
        self.height = height
        self.verbose = verbose
        self.scale = scale
        self.line_width = lwidth
        self.color = color

    def convert(self):
        """ convert blocks """
        try:
            doc = ezdxf.readfile(self.dxf_name)
        except IOError:
            print(f"*** ERROR Not a DXF file or a generic I/O error: {self.dxf_name}")
            sys.exit()
        except ezdxf.DXFStructureError:
            print(f"*** ERROR Invalid or corrupted DXF file: {self.dxf_name}")
            sys.exit()
        for block in doc.blocks:
            if not block.name.startswith("*"): # skip special blocks
                if fnmatch.fnmatch(block.name, self.block_name):
                    if self.verbose:
                        print(block.name)
                    res = self.block2svg(block)
                    if self.out_type == 'png':
                        res.savePng(os.path.join(self.out_path,
                                    block.name + '.' + self.out_type))
                    elif self.out_type == 'svg':
                        res.saveSvg(os.path.join(self.out_path,
                                    block.name + '.' + self.out_type))

    @staticmethod
    def bulge_arc(start, end, bulge):
        """ calculate arc parameters between two points with bulge

            :param start: start point of arc (x, y)
            :param end: end point of arc (x, y)
            :param bulge: CAD arc parameter 
            :return: centerX, centerY, radius, start_angle, end_angle
        """
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        chord = hypot(dx, dy)
        sign = 1 if bulge > 0 else -1
        delta = 4 * atan(abs(bulge))
        #r = chord * (bulge * bulge + 1) / 4 / bulge
        r = abs(chord / 2 / sin(delta / 2))
        #a1 = atan2(dy, dx) + pi / 2 - 2 * atan(bulge)    # angle to center from start point
        a = atan2(dy, dx) + (pi - delta) * sign * 0.5
        cx = start[0] + r * cos(a)
        cy = start[1] + r * sin(a)
        start_a = atan2(start[1] - cy, start[0] - cx)
        end_a = atan2(end[1] - cy, end[0] - cx)
        return cx, cy, r, start_a, end_a

    def block2svg(self, block):
        """ export block to SVG

            :param block: block definition
            :returns: svg object
        """
        # initialize SVG
        d = draw.Drawing(self.width, self.height, origin='center')
        x0, y0, _ = block.base_point    # basepoint of block
        for entity in block:
            typ = entity.dxftype()
            if typ == "LINE":
                x1 = (entity.dxf.start[0] - x0) * self.scale
                y1 = (entity.dxf.start[1] - y0) * self.scale
                x2 = (entity.dxf.end[0] - x0) * self.scale
                y2 = (entity.dxf.end[1] - y0) * self.scale
                d.append(draw.Lines(x1, y1, x2, y2, close=False,
                                    stroke_width=self.line_width, stroke=self.color))
            elif typ == "CIRCLE":
                xc = (entity.dxf.center[0] - x0) * self.scale
                yc = (entity.dxf.center[1] - y0) * self.scale
                r = entity.dxf.radius * self.scale
                d.append(draw.Circle(xc, yc, r, fill='none',
                                     stroke_width=self.line_width, stroke=self.color))
            #elif typ == "ELLIPSE":
            #    xc = (entity.dxf.center[0] - x0) * self.scale
            #    yc = (entity.dxf.center[1] - y0) * self.scale
            #    rx = (entity.dxf.major_axis)
            #    ry = (entity.dxf.minor_axis)
            #    d.append(draw.Ellipse(xc, yc, rx, ry,
            #                          stroke_width=self.line_width, stroke=self.color))
            elif typ == "ARC":
                xc = (entity.dxf.center[0] - x0) * self.scale
                yc = (entity.dxf.center[1] - y0) * self.scale
                r = entity.dxf.radius * self.scale
                d.append(draw.Arc(xc, yc, r, entity.dxf.start_angle,
                                  entity.dxf.end_angle, cw=False, fill='none',
                                  stroke_width=self.line_width, stroke=self.color))
            elif typ == "TEXT":
                pos = entity.get_pos()
                x = (pos[1][0] - x0) * self.scale
                y = (pos[1][1] - y0) * self.scale
                h = entity.dxf.height * self.scale
                d.append(draw.Text(entity.dxf.text, h, x, y, fill=self.color))
            elif typ == "HATCH":
                # only external border is considered
                if entity.dxf.solid_fill == 1:
                    p = draw.Path(stroke_width=self.line_width, stroke=self.color,
                                  fill=self.color)
                    if isinstance(entity.paths.paths[0],
                                  ezdxf.entities.boundary_paths.PolylinePath):
                        v = entity.paths.paths[0].vertices[0]
                        first = ((v[0] - x0) * self.scale, (v[1] - y0) * self.scale)
                        last = first
                        p.M(*first)
                        bulge = v[2]
                        for v in entity.paths.paths[0].vertices[1:]:
                            act = ((v[0] - x0) * self.scale, (v[1] - y0) * self.scale)
                            if abs(bulge) > 0.1:  # arc
                                _, _, r, _, _ = self.bulge_arc(last, act, bulge)
                                sweep_flag = 0 if bulge > 0 else 1
                                p.A(r, r, 0, 0, sweep_flag, *act)
                            else:
                                p.L(*act)
                            bulge = v[2]
                            last = act
                        # close 
                        if abs(bulge) > 0.1:
                            _, _, r, _, _ = self.bulge_arc(last, first, bulge)
                            sweep_flag = 0 if bulge > 0 else 1
                            p.A(r, r, 0, 0, sweep_flag, *first)
                        p.Z()
                    elif isinstance(entity.paths.paths[0],
                                    ezdxf.entities.boundary_paths.EdgePath):
                        for edge in entity.paths.paths[0].edges:
                            if isinstance(edge, ezdxf.entities.boundary_paths.LineEdge):
                                if first is None:
                                    p.M((edge.start_point[0] - x0) * self.scale,
                                        (edge.start_point[1] - y0) * self.scale)
                                    first = False
                                p.L((edge.end_point[0] - x0) * self.scale,
                                    (edge.end_point[1] - y0) * self.scale)
                            elif isinstance(edge, ezdxf.entities.boundary_paths.ArcEdge):
                                edge.end_angle = min(edge.end_angle, 359.9)
                                p.arc((edge.center[0] - x0) * self.scale,
                                      (edge.center[1] - y0) * self.scale,
                                      edge.radius * self.scale,
                                      edge.start_angle, edge.end_angle)
                    else:
                        print('Unsupported HATCH boundary type')
                        continue
                    d.append(p)
                else:
                    print('HATCH with solid fill are only supported')
            elif typ == "LWPOLYLINE":
                p = draw.Path(stroke_width=self.line_width, stroke=self.color,
                              fill='none')
                with entity.points() as points:
                    pp = points[0]
                    first = ((pp[0] - x0) * self.scale, (pp[1] - y0) * self.scale)
                    p.M(*first)
                    act = first
                    bulge = pp[4]
                    for pp in points[1:]:
                        act = ((pp[0] - x0) * self.scale, (pp[1] - y0) * self.scale)
                        if abs(bulge) > 0.1:
                            _, _, r, _, _ = self.bulge_arc(last, act, bulge)
                            sweep_flag = 0 if bulge > 0 else 1
                            p.A(r, r, 0, 0, sweep_flag, *act)
                        else:
                            p.L(*act)
                        bulge = pp[4]
                        last = act
                if entity.closed:
                    if abs(bulge) > 0.1:
                        _, _, r, _, _ = self.bulge_arc(last, act, bulge)
                        sweep_flag = 0 if bulge > 0 else 1
                        p.A(r, r, 0, 0, sweep_flag, *act)
                        #else:
                            #p.L(*first)
                    p.Z()
                d.append(p)
                #p = []
                #with entity.points() as points:
                #    for pp in points:
                #        p.append((pp[0] - x0) * self.scale)
                #        p.append((pp[1] - y0) * self.scale)
                #closed = False
                #if entity.closed:
                #    closed = True
                #d.append(draw.Lines(*p, stroke=self.color, stroke_width=self.line_width,
                #                    fill="none", close=closed))
            elif typ == "POLYLINE":
                if entity.get_mode() in ('AcDb2dPolyline', 'AcDb3dPolyline'):
                    p = []
                    for v in entity.vertices:
                        p.append((v.dxf.location[0] - x0) * self.scale)
                        p.append((v.dxf.location[1] - y0) * self.scale)
                    closed = False
                    if entity.is_closed:
                        closed = True
                    d.append(draw.Lines(*p, stroke=self.color,
                             stroke_width=self.line_width, fill="none", close=closed))
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
                        help='path to save SVG/PNG files to')
    parser.add_argument('-t', '--type', type=str, default='svg',
                        help='Output type svg/png, default=svg')
    parser.add_argument('-w', '--width', type=float, default=500.0,
                        help='SVG or image width, default=500')
    parser.add_argument('-e', '--height', type=float, default=500.0,
                        help='SVG or image height, default=500')
    parser.add_argument('-s', '--scale', type=float, default=40.0,
                        help='scale, default=40')
    parser.add_argument('-l', '--lwidth', type=int, default=5,
                        help='line width, default=5')
    parser.add_argument('-c', '--color', type=str, default="black",
                        help='color, default=black')
    parser.add_argument('-v', '--verbose', action="store_true",
                        help='verbose output to stdout')

    args = parser.parse_args()
    if not os.path.isdir(args.out_path):
        raise argparse.ArgumentTypeError(f"Output path does not exists: {args.out_path}")
    if not os.access(args.out_path, os.W_OK):
        raise argparse.ArgumentTypeError(f"Output path is not writeable: {args.out_path}")
    if not args.type in ('png', 'svg'):
        raise argparse.ArgumentTypeError("Output type must be 'svg' or 'png'")

    b = Block2(args.name[0], args.block, args.out_path, args.type,
               args.width, args.height, args.verbose, args.scale,
               args.lwidth, args.color)
    b.convert()
