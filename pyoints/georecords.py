# BEGIN OF LICENSE NOTE
# This file is part of Pyoints.
# Copyright (c) 2018, Sebastian Lamprecht, lamprecht@uni-trier.de
# 
# This software is copyright protected. A decision on a less restrictive licencing 
# model will be made before releasing this software.
# END OF LICENSE NOTE
"""Generic data structure to handle point data.
"""

import warnings
import numpy as np

from .coords import Coords

from . import (
    transformation,
    projection,
    assertion,
    nptools,
)


class GeoRecords(np.recarray, object):
    """Abstraction class to ease handling of point sets as well as structured
    matrices of point like objects. This gives the oportunity to handle
    unstructured point sets the same way like rasters or voxels. The class also
    provides a IndexKD object on demand to speed up neigbourhod analyzes.

    Parameters
    ----------
    proj : projection.Proj
        Projection object to provide the coordinate reference system.
    rec : np.recarray
        A numpy record array provides coordinates and attributes of `n` points.
        The field `coords` is required and represents coordinates of `k`
        dimensions.
    T : optional, array_like(Number, shape=(k+1, k+1))
        Linear transformation matrix to transform the coordinates. Set to a
        identity matrix if not given. This eases handling of structured point
        sets like rasters or voxels.

    Attributes
    ----------
    proj : projection.Proj
        Projection of the coordinates.
    t : np.matrix(Number, shape=(k+1, k+1))
        Linear transformation matrix to transform the coordinates.
    dim : positive int
        Number of coordinate dimensions of the `coords` field.
    count : positive int
        Number of objects within the data structure. E.g. number of points
        of a point cloud or number of cells of a raster.
    keys : np.ndarray(int, shape=self.shape)
        Keys or indices of the data structure.

    Examples
    --------

    >>> data = {
    ...    'coords': [(2, 3), (3, 2), (0, 1), (-1, 2.2), (9, 5)],
    ...    'values': [1, 3, 4, 0, 6]
    ... }
    >>> geo = GeoRecords(projection.Proj(), data)
    >>> print(geo.values)
    [1 3 4 0 6]
    >>> print(geo.coords)
    [[ 2.   3. ]
     [ 3.   2. ]
     [ 0.   1. ]
     [-1.   2.2]
     [ 9.   5. ]]

    Set new coordinates.

    >>> geo['coords'] = [(1, 2), (9, 2), (8, 2), (-7, 3), (7, 8)]
    >>> print(geo.coords)
    [[ 1.  2.]
     [ 9.  2.]
     [ 8.  2.]
     [-7.  3.]
     [ 7.  8.]]

    Use structured data (two dimensional matrix).

    >>> data = {
    ...    'coords': [
    ...                 [(2, 3.2), (-3, 2.2)],
    ...                 [(0, 1.1), (-1, 2.2)],
    ...                 [(-7, -1), (9.2, -5)]
    ...             ],
    ...    'values': [[1, 3], [4, 0], [-4, 2]]
    ... }
    >>> data = nptools.recarray(data,dim=2)
    >>> geo = GeoRecords(None, data)
    >>> print(geo.shape)
    (3, 2)
    >>> print(geo.coords)
    [[[ 2.   3.2]
      [-3.   2.2]]
    <BLANKLINE>
     [[ 0.   1.1]
      [-1.   2.2]]
    <BLANKLINE>
     [[-7.  -1. ]
      [ 9.2 -5. ]]]

    """

    def __init__(self, proj, rec, T=None):
        self.proj = proj    # validated by setter
        if T is None:
            T = transformation.t_matrix(self.extent().min_corner)
        self.t = T    # validated by setter

    def __new__(cls, proj, rec, T=None):
        if isinstance(rec, dict):
            rec = nptools.recarray(rec)
        elif not isinstance(rec, np.recarray):
            raise TypeError("'rec' needs to be of type 'np.recarray'")
        if 'coords' not in rec.dtype.names:
            raise ValueError("field 'coords' required")
        if not len(rec.dtype['coords'].shape) == 1:
            raise ValueError("malformed coordinate shape")
        if not rec.dtype['coords'].shape[0] >= 2:
            raise ValueError("at least two coordinate dimensions needed")
        return rec.view(cls)

    @property
    def dim(self):
        return self.dtype['coords'].shape[0]

    @property
    def coords(self):
        if not hasattr(self, '_coords'):
            # copy required for garbadge collection
            self._coords = self['coords'].view(Coords).copy()
        return self._coords

    def _clear_cache(self):
        if hasattr(self, '_coords'):
            del self._coords

    def __setattr__(self, attr, value):
        np.recarray.__setattr__(self, attr, value)
        if attr is 'coords':
            self._clear_cache()

    def __setitem__(self, key, value):
        np.recarray.__setitem__(self, key, value)
        if key is 'coords':
            self._clear_cache()

    def extent(self, *args):
        return self.coords.extent(*args)

    def indexKD(self, *args):
        return self.coords.indexKD(*args)

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self._t = getattr(obj, '_t', None)
        self._proj = getattr(obj, '_proj', None)

    # def __array_wrap__(self, out_arr, context=None):
    #     return np.ndarray.__array_wrap__(self, out_arr, context)

    @property
    def t(self):
        return self._t

    @t.setter
    def t(self, t):
        t = assertion.ensure_tmatrix(t)
        if not t.shape[0] == self.dim + 1:
            raise ValueError('dimensions do not fit')
        self._t = transformation.LocalSystem(t)
        self._clear_cache()

    @property
    def proj(self):
        return self._proj

    @proj.setter
    def proj(self, proj):
        if proj is None:
            proj = projection.Proj()
            warnings.warn("'proj' not set, so I assume '%s'" % proj.proj4)
        elif not isinstance(proj, projection.Proj):
            raise ValueError("'proj' needs to be of type 'projection.Proj'")
        self._proj = proj

    @property
    def count(self):
        return np.product(self.shape)

    def records(self):
        """Provides the flattened data records. Usefull if structured data
        (like matrices) are used.

        Returns
        -------
        array_like(shape=(self.count), dtype=self.dtype)
            Flattened

        Examples
        --------

        >>> data = {
        ...    'coords': [
        ...                 [(2, 3.2), (-3, 2.2)],
        ...                 [(0, 1.1), (-1, 2.2)],
        ...                 [(-7, -1), (9.2, -5)]
        ...             ],
        ... }
        >>> data = nptools.recarray(data, dim=2)
        >>> geo = GeoRecords(None, data)
        >>> print(geo.shape)
        (3, 2)
        >>> print(geo.records().coords)
        [[ 2.   3.2]
         [-3.   2.2]
         [ 0.   1.1]
         [-1.   2.2]
         [-7.  -1. ]
         [ 9.2 -5. ]]
        >>> geo.coords[0, 0] = (1, 1)


        """
        return self.reshape(self.count)

    @property
    def keys(self):
        """Keys or indices of the data structure.

        Returns
        -------
        np.ndarray(int, shape=(self.count))
            Array of indices. Each entry provides a index tuple e. g. to
            recieve data elements wth `__getitem__`.

        Examples
        --------

        Unstructured data.

        >>> data = {
        ...    'coords': [(2, 3, 1), (3, 2, 3), (0, 1, 0), (9, 5, 4)],
        ...    'values': [1, 3, 4, 0]
        ... }
        >>> geo = GeoRecords(None, data)
        >>> print(geo.keys)
        [[0]
         [1]
         [2]
         [3]]

        Structured data (two dimensional matrix).

        >>> data = np.ones(
        ...         (4,3), dtype=[('coords', float, 2)]).view(np.recarray)
        >>> geo = GeoRecords(None, data)
        >>> print(geo.keys)
        [[[0 0]
          [0 1]
          [0 2]]
        <BLANKLINE>
         [[1 0]
          [1 1]
          [1 2]]
        <BLANKLINE>
         [[2 0]
          [2 1]
          [2 2]]
        <BLANKLINE>
         [[3 0]
          [3 1]
          [3 2]]]

        """
        return nptools.indices(self.shape, flatten=False)

    def transform(self, T):
        """Transform coordinates.

        Parameters
        ----------
        T : array_like(Number, shape=(self.dim+1, self.dim+1))
            Transformation matrix to apply.

        See Also
        --------
        Coords.transform

        Examples
        --------

        >>> data = {
        ...    'coords': [(2, 3), (3, 2), (0, 1), (9, 5)],
        ...    'values': [1, 3, 4, 0]
        ... }
        >>> geo = GeoRecords(None, data)

        >>> T = transformation.matrix(t=[10, 20], s=[0.5, 1])
        >>> geo.transform(T)
        >>> print(geo.coords)
        [[11 23]
         [11 22]
         [10 21]
         [14 25]]

        """
        self.coords = self.coords.transform(T)
        self.t = T * self.t

    def project(self, proj):
        """Projects the coordinates to a different coordinate system.

        Parameters
        ----------
        proj : Proj
            Desired output projection system.

        See Also
        --------
        Proj

        Examples
        --------
        TODO

        """
        self.coords = projection.project(self.coords, self.proj, proj)
        self.proj = proj

    def add_fields(self, dtypes, data=None):
        """Adds data fields to the georecords.

        Parameters
        ----------
        dtypes : np.dtype
            Data types of the new fields.
        data : optional, list of arrays
            Data values of the new fields.

        Returns
        -------
        geo : self.__class__
            New GeoRecords with additional fields.

        See Also
        --------
        nptools.add_fields

        Examples
        --------

        Unstructured data.

        >>> data = {
        ...    'coords': [(2, 3, 1), (3, 2, 3), (0, 1, 0), (9, 5, 4)],
        ... }
        >>> geo = GeoRecords(None, data)
        >>> geo2 = geo.add_fields(
        ...     [('A', int), ('B', object)],
        ...     data=[[1, 2, 3, 4], ['a', 'b', 'c', 'd']]
        ... )
        >>> print(geo2.dtype.names)
        ('coords', 'A', 'B')
        >>> print(geo2.B)
        ['a' 'b' 'c' 'd']

        """

        records = nptools.add_fields(self, dtypes, data=data)
        return self.__class__(self.proj, records, T=self.t)

    def merge(self, rec):
        """Merges a record array with the georecords.

        Parameters
        ----------
        rec : array_like
            Record array with same fields than self.

        Returns
        -------
        geo : self.__class__
            New GeoRecords.

        See Also
        --------
        nptools.merge

        """
        data = nptools.merge((self, rec))
        return self.__class__(self.proj, data, T=self.t)

    def apply_function(self, func, dtypes=[object]):
        """Applies or maps a function to each element of the data array.

        Parameters
        ----------
        func : function
            This function is applied to record of the array.
        dtypes :  optional, np.dtype
            Desired data type of the output array.

        Returns
        -------
        geo : self.__class__
            New GeoRecords with shape `self.shape`.

        See Also
        --------
        nptools.apply_function

        """
        data = nptools.apply_function(self, func, dtypes=dtypes)
        return self.__class__(self.proj, data, T=self.t)