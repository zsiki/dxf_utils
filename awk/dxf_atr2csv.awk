#!/usr/bin/gawk -f
# 
# create csv file from block attributes in dxf file
# Zoltan Siki siki.zoltan@epito.bme.hu
# usage:
#        gawk -f dxf_atr2csv.awk dxf_file > csv_file

BEGIN {
    print "EAST;NORTH;LAYER;DIRECTION;SIZE;FLAG;TEXT;TAG";  # print header
    entity = ""; txt = ""; angle = 0; size = 1; layer = ""; flag = 0; tag = "";
}
/^ENTITIES/,/^EOF/ {
	sub(/[ \t\r\n]+$/, "", $0);			# remove trailing white space
    if ($0 == "  0") {                  # next entity reached
        if (entity == "ATTRIB") {   # output text data
            printf("%.2f;%.2f;%s;%.5f;%.2f;%d;%s;%s\n", x, y, layer, angle, size, flag, txt, tag);
        }
        entity = ""; txt = ""; angle = 0; size = 1; flag = 0; tag = "";
        last = "";                      # initialize variables
    }
    if (last == "  0") { entity = $0; } # actual entity type
    if (entity == "INSERT") {
        if (last == "  8") { layer = $0; }  # layer of insert
    }
    if (last == " 10") { x = $0; }      # east  
    if (last == " 20") { y = $0; }      # north
    if (last == " 40") { size = $0; }   # text size
    if (last == " 50") { angle = $0; }  # text direction
    if (last == "  1") { txt = $0; }    # text
    if (last == "  2") { tag = $0; }    # attribute tag
    if (last == " 70") { flag = $0; }   # visible flag
    last = $0;                          # last input line
}
