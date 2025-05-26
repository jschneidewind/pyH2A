import csv
import os
from typing import Iterator, List, Dict

import numpy
import numpy.linalg
import scipy.sparse
import logging

from pyH2A.Utilities.input_modification import file_import


class TechEntry:
    """A TechEntry contains the meta data of a row or column of the technosphere
    matrix A.

    Attributes
    ----------
    index : int
        The index of the entry in the matrix.
    process_id : str
        The ID of the process.
    process_name : str
        The name of the process.
    process_category : str
        The category of the process.
    process_location : str
        The location of the process.
    flow_id : str
        The ID of the flow.
    flow_name : str
        The name of the flow.
    flow_category : str
        The category of the flow.
    flow_unit : str
        The unit of the flow.
    flow_type : str
        The type of the flow.

    """

    def __init__(self):
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
    def _from_csv(row: List[str]) -> 'TechEntry':
        """Creates a TechEntry object from a list of CSV row strings.

        Parameters
        ----------
        row : list of str
            A list of strings representing a single row from a CSV file,
            expected to be in a specific order corresponding to `TechEntry` attributes.

        Returns
        -------
        TechEntry
            A new `TechEntry` instance populated with data from the CSV row.

        """
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
    def index_of(file_path: str) -> List['TechEntry']:
        """Reads a CSV file and returns a list of TechEntry objects.

        Parameters
        ----------
        file_path : str
            The path to the CSV file, which can be a regular filesystem path
            or a package resource path (e.g., "package.subdirectory~file_name").

        Returns
        -------
        list of TechEntry
            A list of `TechEntry` instances, each representing a row from the CSV.

        """
        index = []
        for row in _csv_rows_of(file_path):
            index.append(TechEntry._from_csv(row))
        return index
    
    @staticmethod
    def dict_of(file_path: str) -> Dict[str, 'TechEntry']:
        """Reads a CSV file and returns a dictionary of TechEntry objects,
        keyed by `process_id`.

        Parameters
        ----------
        file_path : str
            The path to the CSV file, which can be a regular filesystem path
            or a package resource path (e.g., "package.subdirectory~file_name").

        Returns
        -------
        dict
            A dictionary where keys are `process_id` strings and values are
            `TechEntry` instances.

        """
        dict_index = {}
        for row in _csv_rows_of(file_path):
            entry = TechEntry._from_csv(row)
            dict_index[entry.process_id] = entry
        return dict_index


class FlowEntry:
    """A FlowEntry contains the meta data of a row in the intervention matrix B.

    Attributes
    ----------
    index : int
        The index of the entry in the matrix.
    flow_id : str
        The ID of the flow.
    flow_name : str
        The name of the flow.
    flow_category : str
        The category of the flow.
    flow_unit : str
        The unit of the flow.
    flow_type : str
        The type of the flow.
    location_id : str
        The ID of the location.
    location_name : str
        The name of the location.
    location_code : str
        The code of the location.

    """

    def __init__(self):
        self.index = -1
        self.flow_id = ''
        self.flow_name = ''
        self.flow_category = ''
        self.flow_unit = ''
        self.flow_type = ''
        self.location_id = ''
        self.location_name = ''
        self.location_code = ''

    @staticmethod
    def _from_csv(row: List[str]) -> 'FlowEntry':
        """Creates a FlowEntry object from a list of CSV row strings.

        Parameters
        ----------
        row : list of str
            A list of strings representing a single row from a CSV file,
            expected to be in a specific order corresponding to `FlowEntry` attributes.

        Returns
        -------
        FlowEntry
            A new `FlowEntry` instance populated with data from the CSV row.

        """
        e = FlowEntry()
        e.index = int(row[0])
        e.flow_id = row[1]
        e.flow_name = row[2]
        e.flow_category = row[3]
        e.flow_unit = row[4]
        e.flow_type = row[5]
        e.location_id = row[6]
        e.location_name = row[7]
        e.location_code = row[8]
        return e

    @staticmethod
    def index_of(file_path: str) -> List['FlowEntry']:
        """Reads a CSV file and returns a list of FlowEntry objects.

        Parameters
        ----------
        file_path : str
            The path to the CSV file, which can be a regular filesystem path
            or a package resource path (e.g., "package.subdirectory~file_name").

        Returns
        -------
        list of FlowEntry
            A list of `FlowEntry` instances, each representing a row from the CSV.

        """
        index = []
        for row in _csv_rows_of(file_path):
            index.append(FlowEntry._from_csv(row))
        return index
    

class ImpactEntry:
    """An ImpactEntry contains the meta data of a row in the characterization
    matrix C.

    Attributes
    ----------
    index : int
        The index of the entry in the matrix.
    impact_id : str
        The ID of the impact.
    impact_name : str
        The name of the impact.
    impact_unit : str
        The unit of the impact.

    """

    def __init__(self):
        self.index = -1
        self.impact_id = ''
        self.impact_name = ''
        self.impact_unit = ''

    @staticmethod
    def _from_csv(row: List[str]) -> 'ImpactEntry':
        """Creates an ImpactEntry object from a list of CSV row strings.

        Parameters
        ----------
        row : list of str
            A list of strings representing a single row from a CSV file,
            expected to be in a specific order corresponding to `ImpactEntry` attributes.

        Returns
        -------
        ImpactEntry
            A new `ImpactEntry` instance populated with data from the CSV row.

        """
        e = ImpactEntry()
        e.index = int(row[0])
        e.impact_id = row[1]
        e.impact_name = row[2]
        e.impact_unit = row[3]
        return e

    @staticmethod
    def index_of(file_path: str) -> List['ImpactEntry']:
        """Reads a CSV file and returns a list of ImpactEntry objects.

        Parameters
        ----------
        file_path : str
            The path to the CSV file, which can be a regular filesystem path
            or a package resource path (e.g., "package.subdirectory~file_name").

        Returns
        -------
        list of ImpactEntry
            A list of `ImpactEntry` instances, each representing a row from the CSV.

        """
        index = []
        for row in _csv_rows_of(file_path):
            index.append(ImpactEntry._from_csv(row))
        return index


def matrix_of(file_handle, original_file_name: str):
    """Loads a matrix from a file-like object.

    Parameters
    ----------
    file_handle : file-like object
        The opened file-like object (BinaryIO), ready for reading.
    original_file_name : str
        The original name/path of the file. This is used to determine the file type
        (e.g., `.npz` for sparse matrices) based on its extension.

    Returns
    -------
    numpy.ndarray or scipy.sparse.csr_matrix
        The loaded matrix, either a dense NumPy array or a SciPy sparse matrix.

    Raises
    ------
    ValueError
        If the file format is not supported or cannot be inferred from `original_file_name`.
    IOError
        If there is an issue reading from the `file_handle`.

    See Also
    --------
    numpy.load : Function used to load `.npy` files.
    scipy.sparse.load_npz : Function used to load `.npz` files.

    Notes
    -----
    The `file_handle` is closed automatically after loading the matrix.

    """
    try:
        if original_file_name.endswith('.npz'):
            return scipy.sparse.load_npz(file_handle)
        return numpy.load(file_handle)
    finally:
        file_handle.close()


def _csv_rows_of(f: str) -> Iterator[List[str]]:
    """Reads rows from a CSV file, handling both regular file paths and package resources.

    Parameters
    ----------
    f : str
        The path to the CSV file, which can be a regular filesystem path
        or a package resource path (e.g., "package.subdirectory~file_name").

    Yields
    ------
    list of str
        A list of strings representing a single row from the CSV file.

    Notes
    -----
    The first row of the CSV (header) is skipped.
    If the file is not found or an error occurs during reading, a warning or error
    is logged, and an empty iterator is returned.

    """
    try:
        with file_import(f, 'r', return_path=False) as stream:
            reader = csv.reader(stream)
            next(reader)  # skip header
            for row in reader:
                yield row
    except FileNotFoundError:
        logging.warning(f"CSV file not found: {f}")
        return # Return an empty iterator if file not found
    except Exception as e:
        logging.error(f"Error reading CSV file {f}: {e}")
        return # Return an empty iterator on other errors


class ExportFolder:
    """Manages the loading of matrices and index files from a specified export folder
    or package resource.

    Parameters
    ----------
    folder : str
        The base folder or package path (e.g., "my_package.data_exports")
        where the matrices and index files are located.
    logger : logging.Logger
        A logger instance for recording information, warnings, and errors.

    """

    def __init__(
            self, 
            folder: str,
            logger: logging.Logger
            ) -> None:
        self.folder = folder
        self.logger = logger

    def tech_index(self) -> Dict[str, 'TechEntry']:
        """Loads the technosphere index (index_A.csv) and returns it as a dictionary.

        Returns
        -------
        dict
            A dictionary where keys are process IDs (`process_id`) and values are
            `TechEntry` objects. Returns an empty dictionary if the file is not found.

        """
        path = f"{self.folder}~index_A.csv"
        return TechEntry.dict_of(path)

    def flow_index(self) -> List['FlowEntry']:
        """Loads the flow index (index_B.csv) and returns it as a list.

        Returns
        -------
        list of FlowEntry
            A list of `FlowEntry` objects. Returns an empty list if the file is not found.

        """
        path = f"{self.folder}~index_B.csv"
        return FlowEntry.index_of(path)

    def impact_index(self) -> List['ImpactEntry']:
        """Loads the impact index (index_C.csv) and returns it as a list.

        Returns
        -------
        list of ImpactEntry
            A list of `ImpactEntry` objects. Returns an empty list if the file is not found.

        """
        path = f"{self.folder}~index_C.csv"
        return ImpactEntry.index_of(path)

    def has_impacts(self) -> bool:
        """Checks if the impact index file (index_C.csv) exists in the specified folder
        or package resource.

        Returns
        -------
        bool
            `True` if the `index_C.csv` file exists, `False` otherwise.

        """
        file_name = f"{self.folder}~index_C.csv"
        self.logger.info(f"Checking if impacts exist in {file_name}")
        try:
            imported_file = file_import(file_name, return_path=True)
            return imported_file is not None
        except Exception:
            self.logger.error(f"Error checking for impacts in {file_name}")
            return False

    def load(self, name: str):
        """Loads a matrix file (e.g., A.npy, B.npz) from the specified folder
        or package resource.

        The method first attempts to load the file directly using the given `name`.
        If that fails, it tries to find the file by combining `self.folder` with `name`
        and appending common extensions (`.npy`, `.npz`).

        Parameters
        ----------
        name : str
            The name of the matrix file (e.g., 'A', 'B', 'C', 'f').
            This can be a direct path or a package resource path.

        Returns
        -------
        numpy.ndarray or scipy.sparse.csr_matrix or None
            The loaded matrix if found, otherwise `None`.

        """
        try:
            self.logger.info(f"Loading {name} directly.")
            file_obj = file_import(name, mode='rb')
            self.logger.debug(f"File object for direct load: {file_obj}")
            if file_obj:
                return matrix_of(file_obj, name)
        except FileNotFoundError:
            self.logger.debug(f"File not found directly: {name}")
            pass
        except Exception as e:
            self.logger.error(f"Error loading {name} directly: {e}")
            pass
        
        base_path = f"{self.folder}~{name}"
        extensions = ['', '.npy', '.npz']
        for ext in extensions:
            full_path = base_path + ext
            try:
                self.logger.info(f"Attempting to load {full_path}")
                file_obj = file_import(full_path, mode='rb')
                self.logger.debug(f"File object for path with extension: {file_obj}")
                if file_obj:
                    return matrix_of(file_obj, full_path)
            except FileNotFoundError:
                self.logger.debug(f"File not found with extension: {full_path}")
                continue
            except Exception as e:
                self.logger.error(f"Error loading {full_path}: {e}")
                continue

        self.logger.warning(f"Could not load matrix: {name} in {self.folder}")
        return None


class Matrix:
    """Convenience class to define matrix names."""
    A = 'A'
    B = 'B'
    C = 'C'
    f = 'f'


def _as_dense(matrix):
    """Converts a matrix to a dense NumPy array if it's a sparse matrix.

    Parameters
    ----------
    matrix : numpy.ndarray or scipy.sparse.spmatrix
        The input matrix.

    Returns
    -------
    numpy.ndarray
        The dense representation of the input matrix.

    """
    if scipy.sparse.issparse(matrix):
        return matrix.todense()
    return matrix


def solve(matrix, f):
    """Solves a linear system `Ax = f` for `x`.

    Note that this function currently converts sparse matrices to a dense format
    before solving, which might be memory intensive for very large sparse matrices.

    Parameters
    ----------
    matrix : numpy.ndarray or scipy.sparse.spmatrix
        The coefficient matrix A.
    f : numpy.ndarray
        The right-hand side vector f.

    Returns
    -------
    numpy.ndarray
        The solution vector x.

    Raises
    ------
    numpy.linalg.LinAlgError
        If the matrix is singular or not square.

    See Also
    --------
    numpy.linalg.solve : Underlying function used for solving.

    """
    return numpy.linalg.solve(_as_dense(matrix), f)


def invert(matrix):
    """Computes the inverse of a square matrix.

    Note that this function currently converts sparse matrices to a dense format
    before inversion, which might be memory intensive for very large sparse matrices.

    Parameters
    ----------
    matrix : numpy.ndarray or scipy.sparse.spmatrix
        The square matrix to invert.

    Returns
    -------
    numpy.ndarray
        The inverse of the matrix.

    Raises
    ------
    numpy.linalg.LinAlgError
        If the matrix is singular or not square.

    See Also
    --------
    numpy.linalg.inv : Underlying function used for inversion.

    """
    return numpy.linalg.inv(_as_dense(matrix))