'''Utilities for working with openLCA matrix exports in pyH2A.

This module was originally generated based on the openLCA source code, which
is licensed under the Mozilla Public License 2.0 (MPL 2.0; see
https://github.com/GreenDelta/olca-app).

It has been extensively modified to prioritize sparse-matrix calculations and
speed up LCA-based Monte Carlo analysis.
'''
from __future__ import annotations

import csv
import importlib
import os
from typing import List
import numpy
import numpy.linalg
import scipy.linalg
import scipy.sparse
import scipy.sparse.linalg

try:
    scikit_umfpack = importlib.import_module('scikits.umfpack')
except ImportError:
    scikit_umfpack = None


_SPARSE_CSC_CACHE = {}


class TechEntry:
    '''
    Meta data for a single row or column of the technosphere matrix A.

    Instances are typically constructed via :meth:`_from_csv` rather than
    directly, and collected into a dictionary by :meth:`dict_of`.

    Attributes
    ----------
    index : int
        Row/column index in the technosphere matrix A. Default is ``-1``.
    process_id : str
        Unique identifier of the process.
    process_name : str
        Human-readable name of the process.
    process_category : str
        Category of the process.
    process_location : str
        Geographic location of the process.
    flow_id : str
        Unique identifier of the reference flow.
    flow_name : str
        Human-readable name of the reference flow.
    flow_category : str
        Category of the reference flow.
    flow_unit : str
        Unit of the reference flow.
    flow_type : str
        Type of the reference flow (e.g., product, waste).

    See Also
    --------
    ImpactEntry : Equivalent structure for characterization-matrix rows.
    '''

    def __init__(self):
        '''
        Initialize a TechEntry with empty/default attribute values.

        Attributes
        ----------
        index : int
            Row/column index in the technosphere matrix A. Default is ``-1``.
        process_id : str
            Unique identifier of the process.
        process_name : str
            Human-readable name of the process.
        process_category : str
            Category of the process.
        process_location : str
            Geographic location of the process.
        flow_id : str
            Unique identifier of the reference flow.
        flow_name : str
            Human-readable name of the reference flow.
        flow_category : str
            Category of the reference flow.
        flow_unit : str
            Unit of the reference flow.
        flow_type : str
            Type of the reference flow (e.g., product, waste).
        '''
        self.index = -1
        self.process_id = ''
        self.process_name = ''
        self.process_category = ''
        self.process_location = ''
        self.flow_id = ''
        self.flow_name = ''
        self.flow_category = ''
        self.flow_unit = ''
        self.flow_type = ''

    @staticmethod
    def _from_csv(row: List[str]) -> TechEntry:
        '''
        Construct a TechEntry from a CSV row.

        Parameters
        ----------
        row : List[str]
            A row from ``index_A.csv`` with columns: index, process_id,
            process_name, process_category, process_location, flow_id,
            flow_name, flow_category, flow_unit, flow_type.

        Returns
        -------
        TechEntry
            Populated TechEntry instance.
        '''
        e = TechEntry()
        e.index = int(row[0])
        e.process_id = row[1]
        e.process_name = row[2]
        e.process_category = row[3]
        e.process_location = row[4]
        e.flow_id = row[5]
        e.flow_name = row[6]
        e.flow_category = row[7]
        e.flow_unit = row[8]
        e.flow_type = row[9]
        return e

    @staticmethod
    def dict_of(file_path: str) -> dict:
        '''
        Build a dictionary of TechEntry objects keyed by process ID.

        Parameters
        ----------
        file_path : str
            Path to the ``index_A.csv`` file.

        Returns
        -------
        dict
            Mapping from ``process_id`` (str) to :class:`TechEntry`.
        '''
        dict_index = {}
        for row in _csv_rows_of(file_path):
            entry = TechEntry._from_csv(row)
            dict_index[entry.process_id] = entry
        return dict_index


class ImpactEntry:
    '''
    Meta data for a single row of the characterization matrix C.

    Instances are typically constructed via :meth:`_from_csv` rather than
    directly, and collected into an ordered list by :meth:`index_of`.

    Attributes
    ----------
    index : int
        Row index in the characterization matrix C. Default is ``-1``.
    impact_id : str
        Unique identifier of the impact category.
    impact_name : str
        Human-readable name of the impact category (e.g., ``'Global Warming'``).
    impact_unit : str
        Unit of the impact category (e.g., ``'kg CO2 eq'``).

    See Also
    --------
    TechEntry : Equivalent structure for technosphere-matrix rows/columns.
    '''

    def __init__(self):
        '''
        Initialize an ImpactEntry with empty/default attribute values.

        Attributes
        ----------
        index : int
            Row index in the characterization matrix C. Default is ``-1``.
        impact_id : str
            Unique identifier of the impact category.
        impact_name : str
            Human-readable name of the impact category.
        impact_unit : str
            Unit of the impact category (e.g., ``kg CO2 eq``).
        '''
        self.index = -1
        self.impact_id = ''
        self.impact_name = ''
        self.impact_unit = ''

    @staticmethod
    def _from_csv(row: List[str]) -> ImpactEntry:
        '''
        Construct an ImpactEntry from a CSV row.

        Parameters
        ----------
        row : List[str]
            A row from ``index_C.csv`` with columns:
            index, impact_id, impact_name, impact_unit.

        Returns
        -------
        ImpactEntry
            Populated ImpactEntry instance.
        '''
        e = ImpactEntry()
        e.index = int(row[0])
        e.impact_id = row[1]
        e.impact_name = row[2]
        e.impact_unit = row[3]
        return e

    @staticmethod
    def index_of(file_path: str) -> List[ImpactEntry]:
        '''
        Build an ordered list of ImpactEntry objects from a CSV file.

        Parameters
        ----------
        file_path : str
            Path to the ``index_C.csv`` file.

        Returns
        -------
        List[ImpactEntry]
            List of :class:`ImpactEntry` objects in row order.
        '''
        index = []
        for row in _csv_rows_of(file_path):
            index.append(ImpactEntry._from_csv(row))
        return index


def matrix_of(file_path: str):
    '''
    Load a matrix from a file.

    Parameters
    ----------
    file_path : str
        Path to the matrix file. ``.npz`` files are loaded as sparse
        matrices via :func:`scipy.sparse.load_npz`; all other extensions
        are loaded as dense arrays via :func:`numpy.load`.

    Returns
    -------
    scipy.sparse.spmatrix or numpy.ndarray
        The loaded matrix.
    '''
    if file_path.endswith('.npz'):
        return scipy.sparse.load_npz(file_path)
    else:
        return numpy.load(file_path)


def _csv_rows_of(f: str) -> List[List[str]]:
    '''
    Read all data rows from a CSV file, skipping the header.

    Parameters
    ----------
    f : str
        Path to the UTF-8 encoded CSV file.

    Returns
    -------
    List[List[str]]
        All rows after the header, where each row is a list of string fields.
    '''
    with open(f, 'r', encoding='utf-8') as stream:
        reader = csv.reader(stream)
        next(reader)  # skip header
        return list(reader)


class ExportFolder:
    '''
    Interface to an openLCA matrix-export directory.

    Provides methods to load the technosphere index, impact index, and
    individual matrix files (A, B, C, f) from a directory produced by the
    openLCA matrix-export feature.

    Parameters
    ----------
    folder : str
        Path to the openLCA matrix-export directory containing
        ``index_A.csv``, ``index_C.csv``, and the matrix files.

    Attributes
    ----------
    folder : str
        The directory path supplied at construction.

    See Also
    --------
    Matrix : String constants for standard matrix file names.
    '''

    def __init__(self, folder: str):
        '''
        Initialize an ExportFolder.

        Parameters
        ----------
        folder : str
            Path to the openLCA matrix-export directory containing
            ``index_A.csv``, ``index_C.csv``, and the matrix files.
        '''
        self.folder = folder

    def tech_index(self) -> List[TechEntry]:
        '''
        Load the technosphere index from ``index_A.csv``.

        Returns
        -------
        dict
            Mapping from ``process_id`` (str) to :class:`TechEntry`.
            Returns an empty dict if ``index_A.csv`` does not exist.
        '''
        path = os.path.join(self.folder, 'index_A.csv')
        if not os.path.exists(path):
            return []
        return TechEntry.dict_of(path)

    def impact_index(self) -> List[ImpactEntry]:
        '''
        Load the impact category index from ``index_C.csv``.

        Returns
        -------
        List[ImpactEntry]
            Ordered list of :class:`ImpactEntry` objects.
            Returns an empty list if ``index_C.csv`` does not exist.
        '''
        path = os.path.join(self.folder, 'index_C.csv')
        if not os.path.exists(path):
            return []
        return ImpactEntry.index_of(path)

    def has_impacts(self):
        '''
        Check whether the export folder contains an impact index.

        Returns
        -------
        bool
            ``True`` if ``index_C.csv`` exists in the folder,
            ``False`` otherwise.
        '''
        path = os.path.join(self.folder, 'index_C.csv')
        return os.path.exists(path)

    def load(self, name: str):
        '''
        Load a named matrix file from the export folder.

        Searches for the file in order: exact path, then with a ``.npy``
        extension, then with a ``.npz`` extension.

        Parameters
        ----------
        name : str
            Base name of the matrix file (e.g., ``'A'``, ``'B'``, ``'C'``).

        Returns
        -------
        scipy.sparse.spmatrix, numpy.ndarray, or None
            The loaded matrix, or ``None`` if no matching file is found.
        '''
        path = os.path.join(self.folder, name)
        if os.path.exists(path):
            return matrix_of(path)
        p = path + '.npy'
        if os.path.exists(p):
            return matrix_of(p)
        p = path + '.npz'
        if os.path.exists(p):
            return matrix_of(p)
        return None


class Matrix:
    '''
    String constants for the standard openLCA matrix file names.

    Attributes
    ----------
    A : str
        Technosphere matrix file name (``'A'``).
    B : str
        Intervention matrix file name (``'B'``).
    C : str
        Characterization matrix file name (``'C'``).
    f : str
        Final-demand vector file name (``'f'``).
    '''

    A = 'A'
    B = 'B'
    C = 'C'
    f = 'f'


class _FactorizedSolver:
    '''
    Wrapper around a pre-factorized matrix for repeated right-hand-side solves.

    Stores the factorization result (e.g., sparse LU factors) once and exposes
    a :meth:`solve` method that performs only the cheap back-substitution step
    on each call, avoiding redundant re-factorization.

    Parameters
    ----------
    _solve_fn : callable
        A function ``f(rhs) -> ndarray`` that applies the stored factors to a
        right-hand side. Typically ``lu.solve`` from
        :func:`scipy.sparse.linalg.splu`.

    See Also
    --------
    factorize : Factory function that creates a :class:`_FactorizedSolver`.
    '''

    def __init__(self, _solve_fn):
        '''
        Store the pre-factorized solve callable.

        Parameters
        ----------
        _solve_fn : callable
            A function ``f(rhs) -> ndarray`` produced by a prior factorization
            step (e.g., ``scipy.sparse.linalg.splu(A).solve``).
        '''
        self._solve_fn = _solve_fn

    def solve(self, rhs):
        '''Solve for one or many right-hand sides.

        Parameters
        ----------
        rhs : array-like, shape (n,) or (n, k)
            A single RHS vector or a matrix of k RHS column vectors.

        Returns
        -------
        ndarray, shape (n,) or (n, k)
            Solution vector(s). Shape matches input.
        '''
        rhs = numpy.asarray(rhs)
        if rhs.ndim == 1:
            return self._solve_fn(rhs)
        # 2-D RHS matrices are handled directly by the underlying solver.
        return self._solve_fn(rhs)


def factorize(matrix):
    '''
    Factorize a matrix once and return a solver for repeated solves.

    Unlike :func:`solve`, this function performs the (potentially expensive)
    matrix factorization once and stores the sparse factors so that subsequent
    right-hand-side solves only require triangular back-substitution — no
    re-factorization. This is significantly faster when the same matrix must
    be solved against multiple right-hand sides.

    Note: this stores the sparse LU factors (L and U), not the dense inverse.
    The inverse of a sparse matrix is generally dense and should never be
    formed explicitly.

    Parameters
    ----------
    matrix : ndarray or scipy.sparse matrix
        The coefficient matrix to factorize.

    Returns
    -------
    _FactorizedSolver
        Object with a `.solve(rhs)` method that reuses the stored factors.
    '''
    if scipy.sparse.issparse(matrix):
        # splu: factorize once, reuse sparse LU factors for each rhs
        csc = matrix.tocsc() if not scipy.sparse.isspmatrix_csc(matrix) else matrix
        lu = scipy.sparse.linalg.splu(csc)
        return _FactorizedSolver(lu.solve)

    # Dense matrix: LU factorization with partial pivoting
    lu, piv = scipy.linalg.lu_factor(matrix)
    return _FactorizedSolver(lambda rhs: scipy.linalg.lu_solve((lu, piv), rhs))
