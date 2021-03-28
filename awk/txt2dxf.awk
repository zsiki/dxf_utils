#!/usr/bin/gawk -f
#
# create minimal dxf file from space delimited coordinate list
# point positions and point_ids as text are sent to dxf
# input coordinate format:
#   point_id easting northing elevation code/layer
# elevations and codes are optional
# default separators are white spaces (space/TAB) use -F from command line to
# customize field separator
# (C) Zoltan Siki siki.zoltan@emk.bme.hu
# usage:
#        gawk -f txt2dxf.awk coodinate_list > dxf_file

BEGIN {
    # some constants in dxf units
    dx = 0.1;       # easting offset of point id text
    dy = -0.25;     # northin offset of point id text
    th = 0.5;       # text height of point id text
    # minimal DXF header
    print "  0";
    print "SECTION";
    print "  2";
    print "ENTITIES"
}

{ # for each input line
    if (NF < 4 || $4 == "") {
        elev = 0.0;         # default elevation
    } else {
        elev = $4;
    }
    if (NF < 5 || $5 == "") {
        layer = "POINTS";   # default layer
    } else {
        layer = $5;
    }
    # point id text
    printf "  0\nTEXT\n  8\n%s\n 10\n%f\n 20\n%f\n 30\n%f\n", layer, $2+dx, $3+dyi, elev;
    printf " 40\n%f\n 50\n0.0\n  1\n%s\n", th, $1;
    # point entity
    printf "  0\nPOINT\n  8\n%s\n 10\n%f\n 20\n%f\n 30\n%f\n", layer, $2, $3, elev;
}

END {
    # footer for DXF
    print "  0\nENDSEC\n  0\nEOF"
}
