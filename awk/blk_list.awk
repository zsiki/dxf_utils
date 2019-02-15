#!/usr/bin/gawk -f
# 
# statistics about block inserts in a DXF file
# Zoltan Siki siki.zoltan@epito.bme.hu
# usage: blk_list.awk your_file.dxf
#		or
#		 blk_list.awk your_dxf_file.dxf > stats.txt
#		or
#		 blk_list.awk your_dxf_file.dxf | sort > stats.txt

/ENTITIES/,/EOF/ {
	sub(/[ \t\r\n]+$/, "", $0);				# remove trailing white space
	if (last == "  0") {					# next entity reached
		if (insert) { blk[name]++ }			# increment block count
		insert = ($0 == "INSERT" ? 1 : 0)
		name = "???";
	}
	if (last == "  2") { name = toupper($1) }
	last = $0
}
END { for (i in blk) { print i, blk[i] }
}
