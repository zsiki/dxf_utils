#!/usr/bin/env python


"""
Some of the functions below are redistributed wit or without modification
from C64 Character Set to TrueType Converter (c64ttf.py) at https://github.com/atbrask/c64ttf
According to the copyright conditions we copied all the conditions here:

"C64 Character Set to TrueType Converter
Version 1.4
Copyright (c) 2013-2020, A.T.Brask (atbrask[at]gmail[dot]com)
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met: 
1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer. 
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution. 
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."


"""

import os
import fnmatch
import argparse
import ezdxf
import array
import time

from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import ttProgram
from fontTools.ttLib.tables._c_m_a_p import cmap_format_4, cmap_format_0
from fontTools.ttLib.tables._h_e_a_d import mac_epoch_diff
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from fontTools.ttLib.tables.O_S_2f_2 import Panose
from fontTools.ttLib.tables._n_a_m_e import NameRecord

import numpy

from shapely.geometry import Point, LineString, LinearRing, Polygon, linestring
from shapely.geometry.polygon import orient
from shapely.ops import polygonize

CMAP_UNI = [[0, "space", [0x20]],
            [1, "exclam", [0x21]],
            [2, "quotedbl", [0x22]],
            [3, "numbersign", [0x23]],
            [4, "dollar", [0x24]],
            [5, "percent", [0x25]],
            [6, "ampersand", [0x26]],
            [7, "quotesingle", [0x27]],
            [8, "parenleft", [0x28]],
            [9, "parenright", [0x29]],
            [10, "asterisk", [0x2a]],
            [11, "plus", [0x2b]],
            [12, "comma", [0x2c]],
            [13, "hyphen", [0x2d]],
            [14, "period", [0x2e]],
            [15, "slash", [0x2f]],
            [16, "zero", [0x30]],
            [17, "one", [0x31]],
            [18, "two", [0x32]],
            [19, "three", [0x33]],
            [20, "four", [0x34]],
            [21, "five", [0x35]],
            [22, "six", [0x36]],
            [23, "seven", [0x37]],
            [24, "eight", [0x38]],
            [25, "nine", [0x39]],
            [26, "colon", [0x3a]],
            [27, "semicolon", [0x3b]],
            [28, "less", [0x3c]],
            [29, "equal", [0x3d]],
            [30, "greater", [0x3e]],
            [31, "question", [0x3f]],
            [32, "at", [0x40]],
            [33, "A", [0x41]],
            [34, "B", [0x42]],
            [35, "C", [0x43]],
            [36, "D", [0x44]],
            [37, "E", [0x45]],
            [38, "F", [0x46]],
            [39, "G", [0x47]],
            [40, "H", [0x48]],
            [41, "I", [0x49]],
            [42, "J", [0x4a]],
            [43, "K", [0x4b]],
            [44, "L", [0x4c]],
            [45, "M", [0x4d]],
            [46, "N", [0x4e]],
            [47, "O", [0x4f]],
            [48, "P", [0x50]],
            [49, "Q", [0x51]],
            [50, "R", [0x52]],
            [51, "S", [0x53]],
            [52, "T", [0x54]],
            [53, "U", [0x55]],
            [54, "V", [0x56]],
            [55, "W", [0x57]],
            [56, "X", [0x58]],
            [57, "Y", [0x59]],
            [58, "Z", [0x5a]],
            [59, "bracketleft", [0x5b]],
            [60, "backslash", [0x5c]],
            [61, "bracketright", [0x5d]],
            [62, "asciicircum", [0x5e]],
            [63, "underscore", [0x5f]],
            [64, "grave", [0x60]],
            [65, "a", [0x61]],
            [66, "b", [0x62]],
            [67, "c", [0x63]],
            [68, "d", [0x64]],
            [69, "e", [0x65]],
            [70, "f", [0x66]],
            [71, "g", [0x67]],
            [72, "h", [0x68]],
            [73, "i", [0x69]],
            [74, "j", [0x6a]],
            [75, "k", [0x6b]],
            [76, "l", [0x6c]],
            [77, "m", [0x6d]],
            [78, "n", [0x6e]],
            [79, "o", [0x6f]],
            [80, "p", [0x70]],
            [81, "q", [0x71]],
            [82, "r", [0x72]],
            [83, "s", [0x73]],
            [84, "t", [0x74]],
            [85, "u", [0x75]],
            [86, "v", [0x76]],
            [87, "w", [0x77]],
            [88, "x", [0x78]],
            [89, "y", [0x79]],
            [90, "z", [0x7a]],
            [91, "braceleft", [0x7b]],
            [92, "bar", [0x7c]],
            [93, "braceright", [0x7d]],
            [94, "asciitilde", [0x7e]],
            [95, "glyph98", [0x7f]],
            [96, "glyph99", [0x80]],
            [97, "glyph100", [0x81]],
            [98, "glyph101", [0x82]],
            [99, "glyph102", [0x83]],
            [100, "glyph103", [0x84]],
            [101, "glyph104", [0x85]],
            [102, "glyph105", [0x86]],
            [103, "glyph106", [0x87]],
            [104, "glyph107", [0x88]],
            [105, "glyph108", [0x89]],
            [106, "glyph109", [0x8a]],
            [107, "glyph110", [0x8b]],
            [108, "glyph111", [0x8c]],
            [109, "glyph112", [0x8d]],
            [110, "glyph113", [0x8e]],
            [111, "glyph114", [0x8f]],
            [112, "glyph115", [0x90]],
            [113, "glyph116", [0x91]],
            [114, "glyph117", [0x92]],
            [115, "glyph118", [0x93]],
            [116, "glyph119", [0x94]],
            [117, "glyph120", [0x95]],
            [118, "glyph121", [0x96]],
            [119, "glyph122", [0x97]],
            [120, "glyph123", [0x98]],
            [121, "glyph124", [0x99]],
            [122, "glyph125", [0x9a]],
            [123, "glyph126", [0x9b]],
            [124, "glyph127", [0x9c]],
            [125, "glyph128", [0x9d]],
            [126, "glyph129", [0x9e]],
            [127, "glyph130", [0x9f]],
            [128, "glyph131", [0xa0]],
            [129, "exclamdown", [0xa1]],
            [130, "cent", [0xa2]],
            [131, "sterling", [0xa3]],
            [132, "currency", [0xa4]],
            [133, "yen", [0xa5]],
            [134, "brokenbar", [0xa6]],
            [135, "section", [0xa7]],
            [136, "dieresis", [0xa8]],
            [137, "copyright", [0xa9]],
            [138, "ordfeminine", [0xaa]],
            [139, "guillemotleft", [0xab]],
            [140, "logicalnot", [0xac]],
            [141, "glyph144", [0xad]],
            [142, "registered", [0xae]],
            [143, "overscore", [0xaf]],
            [144, "degree", [0xb0]],
            [145, "plusminus", [0xb1]],
            [146, "twosuperior", [0xb2]],
            [147, "threesuperior", [0xb3]],
            [148, "acute", [0xb4]],
            [149, "mu1", [0xb5]],
            [150, "paragraph", [0xb6]],
            [151, "middot", [0xb7]],
            [152, "cedilla", [0xb8]],
            [153, "onesuperior", [0xb9]],
            [154, "ordmasculine", [0xba]],
            [155, "guillemotright", [0xbb]],
            [156, "onequarter", [0xbc]],
            [157, "onehalf", [0xbd]],
            [158, "threequarters", [0xbe]],
            [159, "questiondown", [0xbf]],
            [160, "Agrave", [0xc0]],
            [161, "Aacute", [0xc1]],
            [162, "Acircumflex", [0xc2]],
            [163, "Atilde", [0xc3]],
            [164, "Adieresis", [0xc4]],
            [165, "Aring", [0xc5]],
            [166, "AE", [0xc6]],
            [167, "Ccedilla", [0xc7]],
            [168, "Egrave", [0xc8]],
            [169, "Eacute", [0xc9]],
            [170, "Ecircumflex", [0xca]],
            [171, "Edieresis", [0xcb]],
            [172, "Igrave", [0xcc]],
            [173, "Iacute", [0xcd]],
            [174, "Icircumflex", [0xce]],
            [175, "Idieresis", [0xcf]],
            [176, "Eth", [0xd0]],
            [177, "Ntilde", [0xd1]],
            [178, "Ograve", [0xd2]],
            [179, "Oacute", [0xd3]],
            [180, "Ocircumflex", [0xd4]],
            [181, "Otilde", [0xd5]],
            [182, "Odieresis", [0xd6]],
            [183, "multiply", [0xd7]],
            [184, "Oslash", [0xd8]],
            [185, "Ugrave", [0xd9]],
            [186, "Uacute", [0xda]],
            [187, "Ucircumflex", [0xdb]],
            [188, "ch734", [0x02de]],
            [189, "ch735", [0x02df]],
            [190, "ch736", [0x02e0]],
            [191, "ch737", [0x02e1]],
            [192, "ch738", [0x02e2]],
            [193, "ch739", [0x02e3]],
            [194, "ch740", [0x02e4]],
            [195, "ch741", [0x02e5]],
            [196, "ch742", [0x02e6]],
            [197, "ch743", [0x02e7]],
            [198, "ch744", [0x02e8]],
            [199, "ch745", [0x02e9]],
            [200, "ch746", [0x02ea]],
            [201, "ch747", [0x02eb]],
            [202, "ch748", [0x02ec]],
            [203, "ch749", [0x02ed]],
            [204, "ch750", [0x02ee]],
            [205, "ch751", [0x02ef]],
            [206, "ch752", [0x02f0]],
            [207, "ch753", [0x02f1]],
            [208, "ch754", [0x02f2]],
            [209, "ch755", [0x02f3]],
            [210, "ch756", [0x02f4]],
            [211, "ch757", [0x02f5]],
            [212, "ch758", [0x02f6]],
            [213, "ch759", [0x02f7]],
            [214, "ch760", [0x02f8]],
            [215, "ch761", [0x02f9]],
            [216, "ch762", [0x02fa]],
            [217, "ch763", [0x02fb]],
            [218, "ch764", [0x02fc]],
            [219, "ch765", [0x02fd]],
            [220, "ch766", [0x02fe]],
            [221, "ch767", [0x02ff]],
            [222, "ch768", [0x0300]] ]

CMAP_MACROMAN = [[0x0, ".null"],
                 [0x8, ".null"],
                 [0x9, "nonmarkingreturn"],
                 [0xd, "nonmarkingreturn"],
                 [0x1d, ".null"],
                 [0x20, "space"],
                 [0x21, "exclam"],
                 [0x23, "numbersign"],
                 [0x24, "dollar"],
                 [0x25, "percent"],
                 [0x26, "ampersand"],
                 [0x28, "parenleft"],
                 [0x29, "parenright"],
                 [0x2a, "asterisk"],
                 [0x2b, "plus"],
                 [0x2c, "comma"],
                 [0x2d, "hyphen"],
                 [0x2e, "period"],
                 [0x2f, "slash"],
                 [0x30, "zero"],
                 [0x31, "one"],
                 [0x32, "two"],
                 [0x33, "three"],
                 [0x34, "four"],
                 [0x35, "five"],
                 [0x36, "six"],
                 [0x37, "seven"],
                 [0x38, "eight"],
                 [0x39, "nine"],
                 [0x3a, "colon"],
                 [0x3b, "semicolon"],
                 [0x3c, "less"],
                 [0x3d, "equal"],
                 [0x3e, "greater"],
                 [0x3f, "question"],
                 [0x40, "at"],
                 [0x41, "A"],
                 [0x42, "B"],
                 [0x43, "C"],
                 [0x44, "D"],
                 [0x45, "E"],
                 [0x46, "F"],
                 [0x47, "G"],
                 [0x48, "H"],
                 [0x49, "I"],
                 [0x4a, "J"],
                 [0x4b, "K"],
                 [0x4c, "L"],
                 [0x4d, "M"],
                 [0x4e, "N"],
                 [0x4f, "O"],
                 [0x50, "P"],
                 [0x51, "Q"],
                 [0x52, "R"],
                 [0x53, "S"],
                 [0x54, "T"],
                 [0x55, "U"],
                 [0x56, "V"],
                 [0x57, "W"],
                 [0x58, "X"],
                 [0x59, "Y"],
                 [0x5a, "Z"],
                 [0x5b, "bracketleft"],
                 [0x5c, "backslash"],
                 [0x5d, "bracketright"],
                 [0x5e, "asciicircum"],
                 [0x5f, "underscore"],
                 [0x60, "grave"],
                 [0x61, "a"],
                 [0x62, "b"],
                 [0x63, "c"],
                 [0x64, "d"],
                 [0x65, "e"],
                 [0x66, "f"],
                 [0x67, "g"],
                 [0x68, "h"],
                 [0x69, "i"],
                 [0x6a, "j"],
                 [0x6b, "k"],
                 [0x6c, "l"],
                 [0x6d, "m"],
                 [0x6e, "n"],
                 [0x6f, "o"],
                 [0x70, "p"],
                 [0x71, "q"],
                 [0x72, "r"],
                 [0x73, "s"],
                 [0x74, "t"],
                 [0x75, "u"],
                 [0x76, "v"],
                 [0x77, "w"],
                 [0x78, "x"],
                 [0x79, "y"],
                 [0x7a, "z"],
                 [0x7b, "braceleft"],
                 [0x7c, "bar"],
                 [0x7d, "braceright"],
                 [0x7e, "asciitilde"],
                 [0x81, "Aring"],
                 [0x8c, "aring"],
                 [0xa3, "sterling"],
                 [0xae, "AE"],
                 [0xaf, "Oslash"],
                 [0xb9, "pi"],
                 [0xbe, "ae"],
                 [0xbf, "oslash"],
                 [0xca, "space"],
                 [0xd3, "quotedblright"],
                 [0xd5, "quoteright"]]


class TT():

    def __init__(self,dxf_name,out_file,fontname,unitsPerEm,line_width):
        self.dxf_name = dxf_name
        self.out_file = out_file
        self.fontname = fontname
        self.unitsPerEm = unitsPerEm
        self.line_width = line_width

        self.ttfont = TTFont()
        self.glyphs = self.makeEmptyGlyphs()

    def makeEmptyGlyphs(self):
        bitmap = dict()
        bitmap[".notdef"] = [ [[[-382,0],[-382,2048],[382,2048],[382,0]],[[-256,130],[256,130],[256,1918],[-256,1918]]], []] # ide majd egy kontúrvonalakből álló tömb kell! A kontúrvonal egy koordinátákból álló tömb.
#        bitmap[".notdef"] = [[],[]]
        bitmap[".null"] = [[],[]]
        bitmap["nonmarkingreturn"] = [[],[]]

        return bitmap

    def saveFont(self):
        unicodes = [code for glyph in self.glyphs for code in self.glyphs[glyph][1]]
        
        copyrightYear = time.strftime("%Y")
        creator = "Block2TTF"
        version = "1.0"

        # Populate basic tables (there are a few dependencies so order matters)
        self.makeTable_glyf()
        self.makeTable_maxp()
        self.makeTable_loca()
        self.makeTable_head()
        self.makeTable_hmtx()
        self.makeTable_hhea()
        self.makeTable_OS2( min(unicodes), max(unicodes))
        self.makeTable_cmap()
        self.makeTable_name("Regular", copyrightYear, creator, version)
        self.makeTable_post()

        if self.out_file is None:
            self.out_file = self.dxf_name + '.ttf'
        elif not os.path.exists(os.path.dirname(self.out_file)):
            print(f'out_file parameter has not a valid file or path name')
            self.out_file = self.dxf_name + '.ttf'
            
        self.ttfont.save( self.out_file )

        # We have to compile the TTFont manually when saving as TTX
        # (to auto-calculate stuff here and there)
        self.ttfont["glyf"].compile(self.ttfont)
        self.ttfont["maxp"].compile(self.ttfont)
        self.ttfont["loca"].compile(self.ttfont)
        self.ttfont["head"].compile(self.ttfont)
        self.ttfont["hmtx"].compile(self.ttfont)
        self.ttfont["hhea"].compile(self.ttfont)
        self.ttfont["OS/2"].compile(self.ttfont)
        self.ttfont["cmap"].compile(self.ttfont)
        self.ttfont["name"].compile(self.ttfont)
        self.ttfont["post"].compile(self.ttfont)
#        print("PLEASE NOTE: When exporting directly to XML, the checkSumAdjustment value in the head table will be 0.")
#        self.ttfont.saveXML( self.out_file +'.ttx' )

    # glyf - Glyph Data
    def makeTable_glyf(self):
        glyf = newTable("glyf")
        glyf.glyphs = {glyph: self.makeTTFGlyph(self.glyphs[glyph][0]) for glyph in self.glyphs}

        # We need to sort the glyphs in a specific way (so all basic glyphs are below index 256) to work around a MacRoman related quirk.
        glyf.glyphOrder = sorted([key for key in glyf.glyphs.keys() if not key.startswith('uni')])
        glyf.glyphOrder += sorted([key for key in glyf.glyphs.keys() if key.startswith('uni')])

        self.ttfont["glyf"] = glyf
        self.ttfont.glyphOrder = glyf.glyphOrder

    def makeTTFGlyph(self,polygons):
        result = Glyph()
        result.numberOfContours = len(polygons)
        result.coordinates = GlyphCoordinates([coordinate for polygon in polygons for coordinate in polygon])
        result.flags = array.array("B", [1] * len(result.coordinates))
        result.endPtsOfContours = [sum(len(polygon) for polygon in polygons[:idx + 1]) - 1 for idx in range(len(polygons))]
        result.program = ttProgram.Program()
        result.program.assembly = []
        return result

    # maxp - Maximum Profile
    def makeTable_maxp(self):
        maxp = newTable("maxp")

        maxp.tableVersion = 0x00010000
        maxp.numGlyphs  = 0           # Auto-calculated by maxp.compile()
        maxp.maxPoints = 0            # Auto-calculated by maxp.compile()
        maxp.maxContours = 0          # Auto-calculated by maxp.compile()
        maxp.maxCompositePoints = 0   # Auto-calculated by maxp.compile()
        maxp.maxCompositeContours = 0 # Auto-calculated by maxp.compile()
        maxp.maxZones = 2
        maxp.maxTwilightPoints = 0
        maxp.maxStorage = 0
        maxp.maxFunctionDefs = 0
        maxp.maxInstructionDefs = 0
        maxp.maxStackElements = 0
        maxp.maxSizeOfInstructions = 0
        maxp.maxComponentElements = 0
        maxp.maxComponentDepth = 0    # Auto-calculated by maxp.compile()

        self.ttfont["maxp"] = maxp

    # loca - Index to Location
    def makeTable_loca(self):
        # Nothing to do here... Locations are auto-calculated by glyf.compile()
        self.ttfont["loca"] = newTable("loca")

    # head - Font Header
    def makeTable_head(self):
        head = newTable("head")

        head.tableVersion = 1.0
        head.fontRevision = 1.0
        head.checkSumAdjustment = 0   # Auto-calculated when writing the TTF.
        head.magicNumber = 0x5F0F3CF5
        head.flags = 11               # bits 0, 1, and 3 = 1 + 2 + 8 = 11
        head.unitsPerEm = self.unitsPerEm
        head.created = int(time.time() - mac_epoch_diff)
        head.modified = int(time.time() - mac_epoch_diff)
        head.xMin = 0                 # Auto-calculated by maxp.compile()
        head.xMax = 0                 # Auto-calculated by maxp.compile()
        head.yMin = 0                 # Auto-calculated by maxp.compile()
        head.yMax = 0                 # Auto-calculated by maxp.compile()
        head.macStyle = 0
        head.lowestRecPPEM = 8
        head.fontDirectionHint = 0
        head.indexToLocFormat = 0
        head.glyphDataFormat = 0

        self.ttfont["head"] = head

    # hmtx - Horizontal Metrics
    def makeTable_hmtx(self):
        hmtx = newTable("hmtx")
        hmtx.metrics = dict()

        for glyphName in self.ttfont["glyf"].keys():
            if glyphName == ".null":
                hmtx[".null"] = (0, 0)
            else:
                glyph = self.ttfont["glyf"].glyphs[glyphName]
                lsb = 0
                if hasattr(glyph, "coordinates") and len(glyph.coordinates) > 0:
                    lsb = min([coord[0] for coord in glyph.coordinates])
                hmtx[glyphName] = (self.unitsPerEm, lsb)

        self.ttfont["hmtx"] = hmtx

    # hhea - Horizontal Header
    def makeTable_hhea(self):
        hhea = newTable("hhea")

        hhea.tableVersion = 1.0
        hhea.ascent = int(self.unitsPerEm/2)
        hhea.descent = int(-self.unitsPerEm/2)
        hhea.lineGap = 0
        hhea.advanceWidthMax = 0      # Auto-calculated by hhea.compile()
        hhea.minLeftSideBearing = 0   # Auto-calculated by hhea.compile()
        hhea.minRightSideBearing = 0  # Auto-calculated by hhea.compile()
        hhea.xMaxExtent = 0           # Auto-calculated by hhea.compile()
        hhea.caretSlopeRise = 1
        hhea.caretSlopeRun = 0
        hhea.caretOffset = 0
        hhea.reserved0 = 0
        hhea.reserved1 = 0
        hhea.reserved2 = 0
        hhea.reserved3 = 0
        hhea.metricDataFormat = 0
        hhea.numOfLongHorMetrics = 0  # Auto-calculated by hmtx.compile()

        self.ttfont["hhea"] = hhea

    # OS/2 - OS/2 and Windows Specific Metrics
    def makeTable_OS2(self, minUnicode, maxUnicode):
        size = self.unitsPerEm
        descent = int(self.unitsPerEm/2)

        os_2 = newTable("OS/2")

        os_2.version = 4
        os_2.xAvgCharWidth = size
        os_2.usWeightClass = 400      # Meaning "Normal (Regular)"
        os_2.usWidthClass = 5         # Meaing "Medium (normal)"
        os_2.fsType = 0               # Windows-only licensing bits...
        os_2.ySubscriptXSize = size
        os_2.ySubscriptYSize = size >> 1
        os_2.ySubscriptXOffset = 0
        os_2.ySubscriptYOffset = descent
        os_2.ySuperscriptXSize = size >> 1
        os_2.ySuperscriptYSize = size >> 1
        os_2.ySuperscriptXOffset = 0
        os_2.ySuperscriptYOffset = size >> 1
        os_2.yStrikeoutSize = self.line_width
        os_2.yStrikeoutPosition = (size >> 1) - descent
        os_2.sFamilyClass = 0x080a    # Class ID = 8 (Sans Serif), Subclass ID = 10 (Matrix)
        panose = Panose()
        panose.bFamilyType = 2        # Text and Display
        panose.bSerifStyle = 1        # No Fit
        panose.bWeight = 6            # Medium
        panose.bProportion = 9        # Monospaced
        panose.bContrast = 6          # Medium
        panose.bStrokeVariation = 2   # Gradual/Diagonal
        panose.bArmStyle = 2          # Straight Arms/Horizontal
        panose.bLetterForm = 8        # Normal/Square
        panose.bMidline = 1           # No Fit
        panose.bXHeight = 1           # No Fit
        os_2.panose = panose
        os_2.ulUnicodeRange1 = 0b10000000000000000000000010000011 # Basic Latin + Latin-1 supplement + Greek and Coptic + General punctuation
        os_2.ulUnicodeRange2 = 0b00010000000000001111100001100000 # Arrows + Mathematical operators + Box drawing + Block elements + Geometric shapes + Misc. symbols + Dingbats + Private use area
        os_2.ulUnicodeRange3 = 0b00000000000000000000000000000000 # n/a
        os_2.ulUnicodeRange4 = 0b00000000000000000000000000000000 # n/a
        os_2.achVendID = "C=64"       # :-)
        os_2.fsSelection = 64         # Regular
        os_2.fsFirstCharIndex = minUnicode
        os_2.fsLastCharIndex = maxUnicode
        os_2.sTypoAscender = size - descent
        os_2.sTypoDescender = 0 - descent
        os_2.sTypoLineGap = 0
        os_2.usWinAscent = size - descent
        os_2.usWinDescent = descent
        os_2.ulCodePageRange1 = 0b00000000000000000000000000000001 # Latin 1 (Code page 1252)
        os_2.ulCodePageRange2 = 0b11000000000000000000000000000000 # WE/Latin 1 (Code page 850) + US (Code page 437)
        os_2.sxHeight = int(self.unitsPerEm * 1.5)                    # Guess (we don't always have a lower-case "x" at 0x78 to measure (as the standard suggests))
        os_2.sCapHeight = size - descent
        os_2.usDefaultChar = 0
        os_2.usBreakChar = 32
        os_2.usMaxContex = 0

        self.ttfont["OS/2"] = os_2

    # cmap - Character to Glyph Mapping
    def makeTable_cmap(self):
        unicodeCMAP = {index: glyph for glyph in self.glyphs if glyph in self.ttfont["glyf"].glyphs for index in self.glyphs[glyph][1]}
        macRoman = dict(CMAP_MACROMAN)
#        macRomanCMAP = {index: macRoman[index] if index in macRoman and macRoman[index] in self.ttfont["glyf"].glyphs else '.notdef' for index in range(256)}

        # Unicode
        cmap4_0_3 = cmap_format_4(4)
        cmap4_0_3.platformID = 0
        cmap4_0_3.platEncID = 3
        cmap4_0_3.language = 0
        cmap4_0_3.cmap = unicodeCMAP

        # Mac Roman
#        cmap0_1_0 = cmap_format_0(0)
#        cmap0_1_0.platformID = 1
#        cmap0_1_0.platEncID = 0
#        cmap0_1_0.language = 0
#        cmap0_1_0.cmap = macRomanCMAP

        # Windows
        cmap4_3_1 = cmap_format_4(4)
        cmap4_3_1.platformID = 3
        cmap4_3_1.platEncID = 1
        cmap4_3_1.language = 0
        cmap4_3_1.cmap = unicodeCMAP

        cmap = newTable("cmap")
        cmap.tableVersion = 0
#        cmap.tables = [cmap4_0_3, cmap0_1_0, cmap4_3_1]
        cmap.tables = [cmap4_0_3, cmap4_3_1]
        self.ttfont["cmap"] = cmap

    # name - Naming Table
    def makeTable_name(self, subFamily, copyrightYear, creator, version):
        copyright = "Copyright {0} {1}".format(copyrightYear, creator)
        fullName = "{0} {1}".format(self.fontname, subFamily)
        uniqueID = "{0} {1}".format(creator, fullName)
        versionText = "Version {0}".format(version)
        psFontName = "".join([b for b in "{0}-{1}".format(self.fontname, creator) if 32 < ord(b) < 127 and b not in '[](){}<>/%'])[:63]
        nameEntries = [copyright, self.fontname, subFamily, uniqueID, fullName, versionText, psFontName]

        unicodeEnc = [0, 3, 0, "utf_16_be"]
        macintoshEnc = [1, 0, 0, "latin1"]
        microsoftEnc = [3, 1, 0x409, "utf_16_be"]
        encodings = [unicodeEnc, macintoshEnc, microsoftEnc]

        name = newTable("name")
        name.names = [self.makeNameRecord(idx, entry, *conf) for idx, entry in enumerate(nameEntries) for conf in encodings]

        self.ttfont["name"] = name

    def makeNameRecord(self, nameID, string, platformID, platEncID, langID, encoding):
        rec = NameRecord()
        rec.nameID = nameID
        rec.platformID = platformID
        rec.platEncID = platEncID
        rec.langID = langID
        rec.string = str(string).encode(encoding)
        return rec

    # post - Postscript Information
    def makeTable_post(self):
        post = newTable("post")

        post.glyphOrder = []
        post.extraNames = []
        post.mapping = dict()

        post.formatType = 2
        post.italicAngle = 0
        post.underlinePosition = int(-self.unitsPerEm/2)
        post.underlineThickness = self.line_width
        post.isFixedPitch = 1
        post.minMemType42 = 0
        post.maxMemType42 = 0
        post.minMemType1 = 0
        post.maxMemType1 = 0

        self.ttfont["post"] = post



class Block2TTF():
    """ class to convert DXF blocks to TrueType Font
        :param dxf_name: input DXF to process
        :param charcodes: character code file in order to assign blocks to specified characters
        :param block_name: glob pattern for block names to convert (* = all)
        :param out_file: output TTF file name (and directory)
        :param fontname: font name
        :param unitsPerEm: font-units per EM-square
        :param scale: scale for CAD coordinates
        :param line_width: line width in SVG
        :param verbose: verbose output
    """

    def __init__(self, dxf_name, charcodes, block_name, out_file, fontname, unitsPerEm, scale, line_width, verbose):
        """ initialize """
        self.dxf_name = dxf_name
        self.charcodes_file = charcodes
        self.block_name = block_name
        self.out_file = out_file
        self.scale = scale
        self.line_width = line_width
        self.verbose = verbose

        self.tt = TT(dxf_name,out_file, fontname, unitsPerEm, line_width)
        self.block_contours = []


    def convert(self):
        """ convert blocks """
        
        # processing input dxf file
        doc = ezdxf.readfile(self.dxf_name)
        for block in doc.blocks:
            if not block.name.startswith("*"): # skip special blocks
                if fnmatch.fnmatch(block.name, self.block_name):
                    if self.verbose:
                        print(block.name)
                    self.block2tt(block)

        if self.charcodes_file is None:                    
            # without "--charcodes" parameter characters assigned to blocks in the order of the blocks in DXF
            self.tt.glyphs.update( {char[1] : [self.block_contours[char[0]][1], char[2]] for char in CMAP_UNI if char[0] < len(self.block_contours)} )
        else:
            # with "--charcodes" parameter characters assigned to blocks by character codes given in character code file
            if self.verbose:
                print("Processing input charcode file {0}...".format(self.charcodes_file))

            with open(self.charcodes_file, "rt") as f:
                lines = f.readlines()
            if not len(lines):
                print("Empty character code file. ")
                return
            
            for i, line in enumerate(lines):
                block_char = line.strip().split("\t")
                
                # bad line if
                # 1. line does not consist of 2 elements
                # 2. 1st and 2nd elements are not strings
                # 3. 2nd string not only contains digits 
                if len(block_char) != 2 or not isinstance(block_char[0], str) or \
                    not isinstance(block_char[1], str) or not block_char[1].isdigit():
                    print(f"Bad line in character code file in line {i+1}.")
                    continue
                    
                block_charcode = int(block_char[1])
                
                # if charcode in file not exists in CMAP_UNI
                if not any( ( block_charcode in char[2] for char in CMAP_UNI) ):
                    print(f"Unsupported character code {block_char[1]} in line {i+1}.")
                    continue
                
                # if block name in file not exist in DXF
                if not any( (block_contour[0]==block_char[0] for block_contour in self.block_contours) ):
                    print(f"Can't find block name from character code file in DXF: {block_char[0]}.")
                    continue
                
                char_id = [char[0] for char in CMAP_UNI if block_charcode in char[2]][0]
                block_contours = [block_contour[1] for block_contour in self.block_contours if block_contour[0]==block_char[0]][0]
                
                self.tt.glyphs.update( {CMAP_UNI[char_id][1] : [block_contours, CMAP_UNI[char_id][2]]} )

            if self.verbose:
                print("Input charcode file {0} successfully processed.".format(self.charcodes_file))
    
        self.tt.saveFont()


    def block2tt(self, block):
        """ export block to TTX (TrueType XML format by fontTools)
            :param block: block definition
            :returns: TTF glyphs object
        """
        geoms_union = Polygon()
        contours = []
        x0, y0, _ = block.base_point    # basepoint of block
        for entity in block:
            typ = entity.dxftype()
            if typ == "LINE":
                x1 = (entity.dxf.start[0] - x0) * self.scale
                y1 = (entity.dxf.start[1] - y0) * self.scale
                x2 = (entity.dxf.end[0] - x0) * self.scale
                y2 = (entity.dxf.end[1] - y0) * self.scale

                linebuf = LineString([(x1, y1), (x2, y2)]).buffer( self.line_width/2, cap_style=2 )
                geoms_union = geoms_union.union(linebuf)

            elif typ == "CIRCLE":
                xc = (entity.dxf.center[0] - x0) * self.scale
                yc = (entity.dxf.center[1] - y0) * self.scale
                r = entity.dxf.radius * self.scale

                if block.name =="Segelykero":
                    a=1

                kulso = Point(xc,yc).buffer(r+self.line_width/2, resolution=6)
                belso = Point(xc,yc).buffer(r-self.line_width/2, resolution=6)
                circlebuf = Polygon( kulso.exterior, ([belso.exterior] if not belso.is_empty else [])  )
                geoms_union = geoms_union.union(circlebuf)

            elif typ == "ARC":
                xc = (entity.dxf.center[0] - x0) * self.scale
                yc = (entity.dxf.center[1] - y0) * self.scale
                r = entity.dxf.radius * self.scale

                # number of segments = approximate 6 segments / a quarter circle (15 degree)
                angle_diff = entity.dxf.end_angle - entity.dxf.start_angle
                numsegments = round( (angle_diff+360 if angle_diff<0 else angle_diff) /15 )

                # The coordinates of the arc
                theta = numpy.radians(numpy.linspace(entity.dxf.start_angle, (entity.dxf.end_angle if angle_diff>0 else entity.dxf.end_angle+360.0), numsegments))
                x = xc + r * numpy.cos(theta)
                y = yc + r * numpy.sin(theta)

                arc = LineString(numpy.column_stack([x, y]))
                arcbuf = arc.buffer( self.line_width/2, cap_style=2 )
                geoms_union = geoms_union.union(arcbuf)
                
            elif typ == "HATCH":

                # only external border is considered
                if entity.dxf.solid_fill == 1:

                    if isinstance(entity.paths.paths[0],
                                  ezdxf.entities.boundary_paths.PolylinePath):
                        p = []
                        for v in entity.paths.paths[0].vertices:
                            p.append( ((v[0] - x0) * self.scale, (v[1] - y0) * self.scale) )
                        if len(p)>2: 
                            hatch_polygons = [ Polygon(p) ]
                        else:
                            print(f'Unsupported HATCH boundary type (2 point polygon), block: {block.name}')
                            hatch_polygons = [ Polygon() ]
                        
                    elif isinstance(entity.paths.paths[0],
                                    ezdxf.entities.boundary_paths.EdgePath):

                        linestrings = []

                        for edge in entity.paths.paths[0].edges:
                            if isinstance(edge, ezdxf.entities.boundary_paths.LineEdge):
                                linestrings.append ((( round((edge.start_point[0] - x0) * self.scale),
                                    round((edge.start_point[1] - y0) * self.scale)),
                                    (round((edge.end_point[0] - x0) * self.scale),
                                     round((edge.end_point[1] - y0) * self.scale))))
                                
                            elif isinstance(edge, ezdxf.entities.boundary_paths.ArcEdge):
                                #edge.end_angle = min(edge.end_angle, 359.9)

                                # number of segments = approximate 6 segments / a quarter circle (15 degree)
                                angle_diff = edge.end_angle - edge.start_angle
                                numsegments = round( (angle_diff+360 if angle_diff<0 else angle_diff) /15 )

                                # The coordinates of the arc
                                theta = numpy.radians(numpy.linspace(edge.start_angle, (edge.end_angle if angle_diff>0 else edge.end_angle+360.0), numsegments))
                                x = ((edge.center[0] + edge.radius * numpy.cos(theta))-x0) * self.scale
                                y = ((edge.center[1] + edge.radius * numpy.sin(theta))-y0) * self.scale
                              
                                linestrings.append( tuple( (round(p[0]),round(p[1])) for p in numpy.column_stack([x, y])) )

                            elif isinstance(edge, ezdxf.entities.boundary_paths.EllipseEdge):
                                print(f'Unsupported HATCH edgepath type: EllipseEdge, block: {block.name}')
                            elif isinstance(edge, ezdxf.entities.boundary_paths.SplineEdge):
                                print(f'Unsupported HATCH edgepath type: SplineEdge, block: {block.name}')
                            else:
                                print(f'Unsupported HATCH edgepath type: ?, block: {block.name}')

                        if len(linestrings):
                            hatch_polygons = list(polygonize(linestrings))
                        else:
                            hatch_polygons = [Polygon()]
                                
                    else:
                        print(f'Unsupported HATCH boundary type, block: {block.name}')
                        continue
                    
                    for hatch_polygon in hatch_polygons:
                        geoms_union = geoms_union.union(hatch_polygon)
                    
                else:
                    print(f'HATCH with solid fill are only supported, block: {block.name}')

            elif typ == "LWPOLYLINE":
                p = []
                with entity.points() as points:
                    for pp in points:
                        p.append( ( (pp[0] - x0) * self.scale, (pp[1] - y0) * self.scale) )
                if entity.closed:
                    polyline = LinearRing(p)
                else:
                    polyline = LineString(p)
                    
                polylinebuf = polyline.buffer( self.line_width/2, cap_style=2 )
                geoms_union = geoms_union.union(polylinebuf)
                
            elif typ == "POLYLINE":
                if entity.get_mode() in ['AcDb2dPolyline', 'AcDb3dPolyline']:
                    p = []
                    for v in entity.vertices:
                        p.append( ( (v.dxf.location[0] - x0) * self.scale, (v.dxf.location[0] - y0) * self.scale) )
                    if entity.is_closed:
                        polyline = LinearRing(p)
                    else:
                        polyline = LineString(p)
                    
                    polylinebuf = polyline.buffer( self.line_width/2, cap_style=2 )
                    geoms_union = geoms_union.union(polylinebuf)

                else:
                    print(f'Unsupported POLYLINE mode: {entity.get_mode()}, block: {block.name}')
            else:
                print(f'Unsupported entity type: {typ}, block: {block.name}')


        if geoms_union.is_empty or not geoms_union.is_valid:
            return
        
        if geoms_union.geom_type == "Polygon":
            contours = contours + self.Polygon2Contours(geoms_union) 
        elif geoms_union.geom_type in ["MultiPolygon","GeometryCollection"]:
            for geom in list(geoms_union.geoms):
                if geom.geom_type == "Polygon":
                    contours = contours + self.Polygon2Contours(geom)
                    
        self.block_contours.append( [block.name, contours] )
        if self.verbose:
            print(f"{block.name} block successfully converted.")


    def Polygon2Contours(self, polygon):
        """ convert a Shapely Polygon object to TTF contour
            :param polygon: Shapely Polygon object
            :returns: array of contours
        """
        # Polygon exterior coords to ttf contour (orientation +1)
        a=len(polygon.interiors)
        polygon = orient( polygon, sign=-1.0 )
        contours = [ [ [round(coord[0]),round(coord[1])] for coord in list(polygon.exterior.coords)[:-1]] ]

        # Polygon interior coords to ttf contour (orientation -1)
        for interior_polygon in list(polygon.interiors):
            contours.append( [ [round(coord[0]),round(coord[1])] for coord in interior_polygon.coords[:-1] ] )
        return contours


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="block2ttf.py v0.1 - AutoCAD Blocks to TrueType Font Converter (c) 2022 MMK-GGT")
    parser.add_argument('name', metavar='file_name', type=str, nargs=1,
                        help='DXF file to process')
    parser.add_argument('-b', '--block', type=str, default='*',
                        help='glob pattern for block name, default=*')
    parser.add_argument("-c", "--charcodes", type=str,
                        help="text file containing the assignment of character codes to blocks")
    parser.add_argument('-o', '--out_file', type=str,
                        help='output TTF file')
    parser.add_argument("-n", "--fontname", type=str, default='MMK-GGT Font',
                        help="Font name (default is 'MMK-GGT Font')")
    parser.add_argument('-u', '--units_per_em', type=int, default=2048,
                        help='font-units per em-square in TTF, default=2048')
    parser.add_argument('-s', '--scale', type=float, default=256.0,
                        help='scale, default=256')
    parser.add_argument('-l', '--lwidth', type=int, default=32,
                        help='line width, default=32')
    parser.add_argument('-v', '--verbose', action="store_true",
                        help='verbose output to stdout')

    args = parser.parse_args()

    b = Block2TTF(args.name[0], args.charcodes, args.block, args.out_file, args.fontname,
                  args.units_per_em, args.scale, args.lwidth, args.verbose)
    b.convert()


