#!/bin/gawk -f
# 
# DXF entites to PostGIS database
# Supported entites: TEXT, MTEXT, LINE, POLYLINE
# PostGIS tables have to be created
#
# Zoltan Siki siki.zoltan@epito.bme.hu
# usage: dxf2pg.awk your_file.dxf > sql_script.sql
#       or
#        gawk -f dxf2pg.awk your_file.dxf | psql

function init() {
	# clear variables for next entity
	entity = ""; subentity = "";
	x = ""; y = ""; z = "";
	x1 = ""; y1 = "";
	angle = "";
	layer = "";
	i = -1;	# index of next vertex
}

BEGIN { PI = atan2(0, -1);
	last = ""; init();
}
/ENTITIES/,/EOF/ {
	sub(/[ \t\r\n]+$/, "", $0);					# remove trailing white space
	if ($0 == "  0" && subentity != "VERTEX") {
		# save previous entity
		if (entity == "MTEXT" || entity == "TEXT") {
			if (angle == "") {
				if (x1 == "" || y1 == "") {
					angle = 0;
				} else {
					angle = atan2(y1, x1) * 180.0 / PI
				}
			}
			printf ("INSERT INTO txt_%s (angle, height, txt, the_geom) VALUES (%.6f,%.2f,'%s',ST_GeomFromText('POINT(%.2f %.2f)',23700));\n", layer, angle, height, txt, x, y);
		}
		else if (entity == "LINE") {
			printf ("INSERT INTO line_%s (the_geom) VALUES (ST_GeomFromText('LINESTRING(%.2f %.2f, %.2f %.2f)',23700));\n", layer, x, y, x1, y1);
		}
		else if (entity == "POLYLINE") {
			printf ("INSERT INTO line_%s (the_geom) VALUES (ST_GeomFromText('LINESTRING(", layer);
			for (k = 0; k < i; k++) {
				if (k == 0) {
					printf ("%.2f %.2f", xpoly[k], ypoly[k]);
				}
				else {
					printf (",%.2f %.2f", xpoly[k], ypoly[k]);
				}
			}
			printf (")',23700));\n");
		}
		if (entity != "POLYLINE") {
			init();
		}
	}
	if (last == "  0") {
		if ($1 == "VERTEX") {
			subentity = $1;
		} else {
			entity = $1;
		}
	}
	else if (last == "  1") { txt = $0; }		# text string
	else if (last == "  3") { print "too long text string"; }
	else if (last == "  5") { handle = $1; }	# CAD unique ID
	else if (last == "  8") {
		if (subentity == "") {layer = $1; }		# layer name
	}
	else if (last == " 10") {
		if (subentity == "") { x = $1; }		# X coord
		else { i++; xpoly[i] = $1;
		}
	}
	else if (last == " 11") { x1 = $1; }		# X coord
	else if (last == " 20") {
		if (subentity == "") { y = $1; }		# y coord
		else { ypoly[i] = $1; }
	}
	else if (last == " 21") { y1 = $1; }		# y coord
	else if (last == " 30") {
		if (subentity == "") {z = $1; }			# elevation
		else { zpoly[i] = $1; }
	}
	else if (last == " 40") { height = $1; }	# text height
	else if (last == " 50") {
		angle = $1; 		# text angle
	}
	else if (last == " 70") {
		if ($1 != 7 && (entity == "TEXT" || entity == "MTEXT")) {	# not bottom left aligned text
				print "no left alingned text";
		}
	}
	else if (last == " 72") {
		if ($1 == 3 && (entity == "TEXT" || entity == "MTEXT")) {	# no left to right text
			print "no left to right text";
		}
	}
	# remember last code
	last = $0;
}
