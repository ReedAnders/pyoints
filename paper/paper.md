---
title: 'Pyoints: A Python package for point cloud, voxel and raster processing.'
tags:
  - Python
  - geoinformatics
  - remote sensing
  - point cloud analysis
  - raster analysis
authors:
  - name: Sebastian Lamprecht
    orcid: 0000-0002-8963-2762
    affiliation: 1
affiliations:
 - name: Trier University
   index: 1
date: 25 September 2018
bibliography: paper.bib
---


# Summary

The evolution of automated systems like autonomous robots and unmanned aerial 
vehicles leads to manifold chances in science, agriculture and industry.
Remote sensing sensors, like laser scanners and multi-spectral cameras can be
combined with sensor networks to monitor a research object all-embracingly.

The analysis of such big data is based on techniques of geoinformatics and 
remote sensing. Next to physically driven approaches, today machine learning 
techniques are used to extract relevant thematical information the data sets.
The analysis requires a fusion of the data sets, which is hardened conceptually
and technically by different data dimensions, data structures and various 
spatial, spectral and temporal resolutions.

Today various software to deal with these different data sources is available.
Software like GDAL [@GDAL] and OpenCV [@opencv_library] is intended for image 
processing. Libraries, like PCL [@PCL], Open3D [@Open3D] and PDAL [@PDAL] focus
on 3D point cloud processing. Each of these software packages provide an API 
specially designed to solve the problems of their field efficiently. When 
developing algorithms for automated processing of various types of input data, 
the differing APIs and programming languages of these software packages become 
a drawback. To supportfast  algorithm development and a short familiarization, 
a unified API would be desirable.

*Pyoints* is a python package to conveniently process and analyze point
cloud data, voxels and raster images. It is intended to be used to support
the development of advanced algorithms for geo-data processing.

The fundamental idea of *Pyoints* is to overcome the conceptual distinction 
between point clouds, voxel spaces and rasters to simplify data analysis 
and data fusion of variously structured data. Based on the assumption that any 
geo-object can be represented by a point, a data structure has been designed 
which provides a unified API for points, voxels and rasters. Each data 
structure maintains its characteristic features, to allow for an intuitive use, 
but all data is also considered as a two or three dimensional point cloud, 
providing spatial indices which are required in many applications to speed up 
spatial neighborhood queries.

During development great emphasis was put on designing a powerful but simple 
API while also providing solutions for most common problems. *Pyoints* 
implements fundamental functions and some advanced algorithms for point cloud, 
voxel and raster data processing, like coordinate transformation, vector
algebra, point filters, or interpolation. *Pyoints* also provides a unified 
API for loading and saving commonly used geo-data formats.

*Pyoints* was designed to support research activities and algorithm
development in the field of geoinformatis and remote sensing. Early versions of 
the software have been used for [@Lamprecht_2017a] and some pre-studies at 
Trier University. *Pyoints* is also used in the PANTHEON [@PANTHEON] project to 
monitor hazelnut orchards.

The source code of *Pyoints* has been archived to GitHub [@Pyoints_GitHub] and
PyPI [@Pyoints_PyPI]. The documentation can be found on GitHub Pages 
[@Pyoints_docs].


# Acknowledgements

This work was supported by the PANTHEON project which is funded by the European
Community Horizon 2020 programme under grant agreement 774571.


# References