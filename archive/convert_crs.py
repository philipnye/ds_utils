# %%
# !/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Purpose
        Convert GEOJSON files from one CRS to CRS84
    Inputs
        - geojson: '*.geojson'
            - Import geojson
    Outputs
        - geojson: '*.geojson'
            - Export geojson
    Parameters
        XXX
    Notes
        - The CRS of the import geojson does not need to be specified - GeoPandas picks
        this up from the import file
'''

import os

import geopandas as gpd

# %%
os.chdir(
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/Demography and geography/' +
    'Shapefiles/Local authorities/' +
    'Unedited data'
)
# CONVERT CRS
gdf = gpd.read_file("Counties_and_Unitary_Authorities_May_2023_UK_BGC_-8232673021969424694.geojson")
gdf_converted = gdf.to_crs("urn:ogc:def:crs:OGC:1.3:CRS84")

# %%
os.chdir(
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/Demography and geography/' +
    'Shapefiles/Local authorities/' +
    'Edited data'
)

gdf_converted.to_file(
    "Counties_and_Unitary_Authorities_May_2023_UK_BGC_-8232673021969424694_CRS84.geojson",
    driver="GeoJSON"
)

# %%
