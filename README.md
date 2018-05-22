# dxf_utils
Small utility scripts to handle dxf files

* 3dface2csv.awk - convert 3DFACE DXF entities to a csv file with WKT geometry useful to load into QGIS as Delemited text layer
* blk_list.awk - statistics about block inserts in a DXF file
* coo2dxf.awk - create dxf file from space separated coordinate list
* dxf2pg.awk - DXF entites to PostGIS database, supported entites: TEXT, MTEXT, LINE, POLYLINE
* dxf_attr2csv.awk - create csv file from block attributes in dxf file
* dxf_blk2csv.awk - create csv file from block inserts in dxf file
* dxf_txt2csv.awk - create csv file from texts in DXF file
* dxfinfo.awk - statistics about entities and layers in a DXF file
