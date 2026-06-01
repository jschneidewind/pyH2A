'''Utilities for working with openLCA matrix exports in pyH2A.

This module was originally generated based on the openLCA source code, which
is licensed under the Mozilla Public License 2.0 (MPL 2.0; see
https://github.com/GreenDelta/olca-app).

It has been extensively modified to prioritize sparse-matrix calculations to
speed up LCA-based Monte Carlo analysis. Several helper classes and functions
have been added to facilitate loading matrices, caching results, and performing
repeated solves with the same coefficient matrix.
'''
from __future__ import annotations
import csv
from functools import lru_cache
import importlib
import os
from typing import List
import numpy
import scipy.linalg
import scipy.sparse
import scipy.sparse.linalg
import hashlib
from pathlib import Path

try:
    pypardiso = importlib.import_module('pypardiso')
except ImportError:
    pypardiso = None

try:
    scikit_umfpack = importlib.import_module('scikits.umfpack')
except ImportError:
    scikit_umfpack = None




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

    def tech_index(self) -> dict[str, TechEntry]:
        '''
        Load the technosphere index from ``index_A.csv``.

        Returns
        -------
        dict[str, TechEntry]
            Mapping from ``process_id`` (str) to :class:`TechEntry`.
            Returns an empty dict if ``index_A.csv`` does not exist.
        '''
        path = os.path.join(self.folder, 'index_A.csv')
        if not os.path.exists(path):
            return {}
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
    """
    Holds a pre-factorized matrix for repeated right-hand-side solves.

    This class stores a matrix factorization and provides a method to solve
    for one or more right-hand sides efficiently, reusing the factorization.

    Parameters
    ----------
    _solve_fn : callable
        Function that solves the linear system for a given right-hand side.

    Methods
    -------
    solve(rhs)
        Solve for one or many right-hand sides using the stored factorization.
    """

    def __init__(self, _solve_fn):
        self._solve_fn = _solve_fn

    def solve(self, rhs):
        """Solve for one or many right-hand sides.

        Parameters
        ----------
        rhs : array-like, shape (n,) or (n, k)
            A single RHS vector or a matrix of k RHS column vectors.

        Returns
        -------
        ndarray, shape (n,) or (n, k)
            Solution vector(s). Shape matches input.
        """
        rhs = numpy.asarray(rhs)
        if rhs.ndim == 1:
            return self._solve_fn(rhs)
        # 2-D: solve each column; underlying solvers (splu, pypardiso) accept 2-D directly
        return self._solve_fn(rhs)

def factorize(matrix):
    """
    Factorize a matrix and return a solver for repeated solves.

    This function performs the (potentially expensive) factorization and
    returns a reusable solver object with a ``.solve(rhs)`` method. Reusing
    this object avoids repeated factorization when solving the same coefficient
    matrix against multiple right-hand sides.

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
    """
    if scipy.sparse.issparse(matrix):
        # pypardiso: spsolve handles factorization internally and is the fastest option
        if pypardiso is not None:
            return _FactorizedSolver(lambda rhs: pypardiso.spsolve(matrix, rhs))

        # scikit-umfpack: if available, use for sparse LU
        if scikit_umfpack is not None:
            csc = matrix.tocsc() if not scipy.sparse.isspmatrix_csc(matrix) else matrix
            solver = scikit_umfpack.UmfpackLU(csc)
            return _FactorizedSolver(solver.solve)

        # splu: factorize once, reuse sparse LU factors for each rhs
        csc = matrix.tocsc() if not scipy.sparse.isspmatrix_csc(matrix) else matrix
        lu = scipy.sparse.linalg.splu(csc)
        return _FactorizedSolver(lu.solve)

    # Dense matrix: LU factorization with partial pivoting
    lu, piv = scipy.linalg.lu_factor(matrix)
    return _FactorizedSolver(lambda rhs: scipy.linalg.lu_solve((lu, piv), rhs))

@lru_cache(maxsize=None)
def matrix_folder_metadata_signature(matrix_folder: str) -> str:
    """
    Build a stable digest of matrix file paths, sizes, and mtimes.

    Parameters
    ----------
    matrix_folder : str
        Path to the matrix export folder.

    Returns
    -------
    str
        SHA-1 digest derived from each file's relative path, size, and
        nanosecond modification time. Returns 'missing-folder' if the folder does not exist,
        or 'empty-folder' if no files are found.
    """
    folder = Path(matrix_folder)
    if not folder.exists():
        return 'missing-folder'

    metadata_lines = []
    # Only include matrix and index files in the cache key
    INCLUDE_FILES = {
        'A', 'A.npy', 'A.npz',
        'B', 'B.npy', 'B.npz',
        'C', 'C.npy', 'C.npz',
        'f', 'f.npy', 'f.npz',
        'index_A.csv', 'index_C.csv',
    }
    for file_path in sorted(p for p in folder.rglob('*') if p.is_file()):
        rel_path = file_path.relative_to(folder).as_posix()
        # Only include files at the top level with allowed names
        if '/' in rel_path:
            continue
        if rel_path not in INCLUDE_FILES:
            continue
        try:
            stat = file_path.stat()
        except OSError:
            continue
        metadata_lines.append(
            f"{rel_path}|size={stat.st_size}|mtime_ns={stat.st_mtime_ns}"
        )

    if not metadata_lines:
        return 'empty-folder'

    metadata_blob = '\n'.join(metadata_lines)
    return hashlib.sha1(metadata_blob.encode('utf-8')).hexdigest()

@lru_cache(maxsize=None)
def build_matrix_cache_key(matrix_folder: str, matrix_shape: tuple, matrix_nnz: int, cache_version: int = 1) -> str:
    """
    Build a stable cache key for matrix-dependent shared artifacts.

    Parameters
    ----------
    matrix_folder : str
        Path to the matrix export folder.
    matrix_shape : tuple
        Shape of the matrix (rows, columns).
    matrix_nnz : int
        Number of non-zero elements in the matrix.
    cache_version : int, optional
        Version number for cache key (default is 1).

    Returns
    -------
    str
        SHA-1 digest string derived from cache version, export folder path, matrix structure, and matrix file metadata.
    """
    folder_signature = matrix_folder_metadata_signature(matrix_folder)
    raw_key = (
        f"v{cache_version}|{matrix_folder}|"
        f"shape={matrix_shape}|nnz={matrix_nnz}|filesig={folder_signature}"
    )
    return hashlib.sha1(raw_key.encode('utf-8')).hexdigest()

@lru_cache(maxsize=None)
def get_disk_cache_dir(output_directory: str) -> Path:
    """
    Return the shared on-disk cache directory (now set to the output directory).

    Parameters
    ----------
    output_directory : str
        Path to the output directory where the cache directory will be created.

    Returns
    -------
    pathlib.Path
        Directory path used to store shared cache artifacts. The directory is created if it does not already exist.
    """
    cache_dir = Path(output_directory) / 'Initial_Artifacts'
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir
