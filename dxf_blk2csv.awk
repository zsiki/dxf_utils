#!/usr/bin/gawk -f
# 
# create csv file from block inserts in dxf file
# Zoltan Siki siki.zoltan@epito.bme.hu
# usage:
#        gawk -f dxf_blk2csv.awk dxf_file > csv_file
BEGIN {
    print "EAST;NORTH;LAYER;DIRECTION;SIZEX;SIZEY;NAME";    # print header
}
/^ENTITIES/,/^EOF/ {
	sub(/[ \t\r\n]+$/, "", $0);			# remove trailing white space
    if ($0 == "  0") {                  # next entity reached
        if (entity == "INSERT") {       #
            printf("%.2f;%.2f;%s;%.5f;%.2f;%.2f;%s\n", x, y, layer, angle, sizex, sizey, name);
        }
        entity = ""; name = ""; angle = 0; sizex = 1; sizey = 1; layer = "";
        last = "";                      # initialize variables
    }
    if (last == "  0") { entity = $0; } # actual entity type
    if (last == "  8") { layer = $0; }  # layer
    if (last == " 10") { x = $0; }      # east  
    if (last == " 20") { y = $0; }      # north
    if (last == " 41") { sizex = $0; }  # scale x
    if (last == " 42") { sizey = $0; }  # scale y
    if (last == " 50") { angle = $0; }  # direction
    if (last == "  2") { name = $0; }   # blockname
    last = $0;                          # last input line
}
