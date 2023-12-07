# !/usr/bin/env python
# -*- coding: utf-8 -*-

from shapely.geometry import MultiPolygon, Polygon
from shapely import unary_union


def merge_geometries(
    geometries: list[Polygon, MultiPolygon],
    exterior_only: bool = True,
    **kwargs
):
    """
    Merge a list of geometries into a single geometry, optionally returning only
    the exterior coordinates of the merged geometry

    Parameters
        - geometries: List of geometries (Polygons MultiPolygons) to merge
        - exterior_only: Whether to return only the exterior coordinates of the
        merged geometry
        - kwargs: Additional keyword arguments to pass to unary_union()

    Returns
        - merged_geometry: Merged geometry

    Notes
        - If the merged geometry is a MultiPolygon, the exterior coordinates of
        each geometry in the MultiPolygon are returned
    """

    merged_geometry = unary_union(geometries, **kwargs)

    if exterior_only:
        if merged_geometry.geom_type == 'Polygon':
            merged_geometry = Polygon(merged_geometry.exterior)
        elif merged_geometry.geom_type == 'MultiPolygon':
            merged_geometry = MultiPolygon(
                Polygon(geom.exterior) for geom in merged_geometry.geoms
            )
        else:
            raise ValueError(
                'Merged geometry is not a Polygon or MultiPolygon'
            )

    return merged_geometry
