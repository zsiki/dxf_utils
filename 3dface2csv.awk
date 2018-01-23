#!/bin/gawk -f
# 
# Convert 3DFACE DXF entities to a csv file with WKT geometry
# useful to load into QGIS as Delemited text layer
# Zoltan Siki siki.zoltan@epito.bme.hu
# usage: 3dface2csv.awk your_file.dxf > delimited_layer.csv

BEGIN { entity = ""; i = 0;
		printf "id;layer;wkt\n";
}
/ENTITIES/,/EOF/ { if ($0 ~ "^ *0$") {
	if (entity == "3DFACE") {
		i++;
		printf "%d;\"%s\";", i, layer;
		printf "POLYGON ((%f %f %f, %f %f %f, %f %f %f, %f %f %f))\n", x1, y1, z1, x2, y2, z2, x3, y3, z3, x1, y1, z1;
		entity = "";
	}
}
	if (last ~ "^ *0$") { entity = $1; }
	if (last ~ "^ *8$") { layer = $1; }
	if (last ~ "^ *10$") { x1 = $1; }
	if (last ~ "^ *11$") { x2 = $1; }
	if (last ~ "^ *12$") { x3 = $1; }
	if (last ~ "^ *13$") { x4 = $1; }
	if (last ~ "^ *20$") { y1 = $1; }
	if (last ~ "^ *21$") { y2 = $1; }
	if (last ~ "^ *22$") { y3 = $1; }
	if (last ~ "^ *23$") { y4 = $1; }
	if (last ~ "^ *30$") { z1 = $1; }
	if (last ~ "^ *31$") { z2 = $1; }
	if (last ~ "^ *32$") { z3 = $1; }
	if (last ~ "^ *33$") { z4 = $1; }
	last = $0;
}
