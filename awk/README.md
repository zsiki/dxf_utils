# dxf_utils

## gawk scripts

* 3dface2csv.awk - convert 3DFACE DXF entities to a csv file with WKT geometry useful to load into QGIS as Delimited text layer
* blk_list.awk - statistics about block inserts in a DXF file
* coo2dxf.awk - create dxf file from space separated coordinate list
* dxf2pg.awk - DXF entites to PostGIS database, supported entites: TEXT, MTEXT, LINE, POLYLINE
* dxf_attr2csv.awk - create csv file from block attributes in dxf file
* dxf_blk2csv.awk - create csv file from block inserts in dxf file
* dxf_txt2csv.awk - create csv file from texts in DXF file
* dxfinfo.awk - statistics about entities and layers in a DXF file

## How to use these scripts?

You have to install gawk on your machine. There are binary releases for Linux and Windows.

Open a command line window and type the following command to list the statistics of the *sample.dxf*:

```
gawk -f dxfinfo.awk sample.dxf
```

The results are written to the standard output, if you would like to save them
into a file use redirection of standard output to file e.g.:

```
gawk -f dxfinfo.awk sample.dxf > sample_info.txt
```

or use pipe to send the output to another program.

## For Windows users

If you use Windows you have to install GNU AWK. You can find binary release here: http://gnuwin32.sourceforge.net/packages/gawk.htm. Download the zip file and unzip it (gawk.exe is enough).
