'''Life cycle assessment core workflow for pyH2A.

This module defines :class:`LCA`, which loads openLCA-exported matrices,
applies scenario-specific technosphere column updates, builds scaling vectors
via Sherman-Morrison updates, and computes LCIA indicator results.
Base artifacts are cached in both process-local RAM and shared on-disk
storage, while solver/factorization objects are kept in-memory only.
Component basis vectors are cached in process-local RAM and on disk.
In worker-based execution, factorization is used to generate the reusable
base scaling vector and basis vectors. After that, scaling vectors are
computed through the basis-correction route without repeated full-matrix
factorization, because A^{-1} e_i has already been computed during the
first Discounted_Cash_Flow call in run_pyH2A (which in turn calls the 
LCA class once) and created all the artifacts and stored on disk for all
workers before multiprocessing Monte Carlo begins.
'''

import hashlib
import os
from functools import lru_cache
from pathlib import Path
import numpy as np
import scipy.sparse
from pyH2A import Discounted_Cash_Flow
from pyH2A.Utilities.input_modification import process_table
from pyH2A.Utilities.lca_utils import *

class LCA:
    '''Perform LCA calculations from an openLCA matrix export.

    Parameters
    ----------
    matrix_folder : str
        Path to the openLCA matrix export folder containing the technosphere
        (A), intervention (B), characterization (C), and demand (f) matrices.
    dcf : pyH2A.Discounted_Cash_Flow
        Discounted cash flow object containing model inputs used to build LCA
        component updates and the final scaling vector.

    Attributes
    ----------
    folder : ExportFolder
        Loaded openLCA export folder.
    tech_index_dict : dict
        Mapping from process UUID to technosphere index metadata.
    A : ndarray or scipy.sparse matrix
        Technosphere matrix.
    B : ndarray or scipy.sparse matrix
        Intervention matrix.
    C : ndarray or scipy.sparse matrix
        Characterization matrix.
    f : ndarray
        Demand vector.
    _updated_col0 : ndarray
        Scenario-specific first technosphere column after applying LCA
        component updates.
    scaling_vector : ndarray
        Scenario-specific activity scaling vector.
    lca_results : dict
        LCIA results keyed by impact name, each with value and unit.
    '''

    _SM_TOL = 1e-12
    _base_solver_cache = {}  # {matrix_key: (_A_factor, _base_scaling_vector, _A_col0)} a class level dictionary cached in RAM for the base A matrix
    _component_basis_cache = {}  # {basis_cache_path: basis_matrix} cached in RAM for component basis vectors
      
    def __init__(self, matrix_folder: str, dcf: Discounted_Cash_Flow):
        '''
        Initialize the LCA object and perform the full LCA calculation workflow.

        This constructor loads all matrices, prepares solver and cache state, updates
        the first column of the technosphere matrix with scenario-specific values,
        builds the scaling vector, and computes LCIA results.

        Parameters
        ----------
        matrix_folder : str
            Path to the openLCA matrix export folder.
        dcf : pyH2A.Discounted_Cash_Flow
            Discounted_Cash_Flow object containing model inputs used to construct the scaling vector.
        '''
        (
            self.folder,
            self.tech_index_dict,
            self.A,
            self.B,
            self.C,
            self.f,
        ) = self.load_matrices_from_folder(matrix_folder)
        self.initialize_base_solver_and_artifacts(matrix_folder)
        self.update_technosphere_column_with_components(dcf)
        self.build_scaling_vector()
        self.perform_lca()
    
    @staticmethod      
    @lru_cache(maxsize=None)
    def load_matrices_from_folder(matrix_folder: str):
        '''Load and cache openLCA folder metadata and matrices.
           This method is decorated with lru_cache to enable reuse of loaded matrices across multiple LCA instances
           with the same matrix_folder argument. However, it is repeated for each process worker and do not get 
           shared across the workers in multi-processing environments. As it is not very expensive to load matrices
           from disk, it is considered acceptable.

        Parameters
        ----------
        matrix_folder : str
            Path to the openLCA matrix export folder.

        Returns
        -------
        folder : ExportFolder or None
            Loaded export folder when impact data are available.
            Returns ``None`` when impacts are missing.
        tech_index_dict : dict
            Dictionary mapping process UUIDs to technosphere index entries.
        A : ndarray or scipy.sparse matrix
            Technosphere matrix.
        B : ndarray or scipy.sparse matrix
            Intervention matrix.
        C : ndarray or scipy.sparse matrix
            Characterization matrix.
        f : ndarray
            Demand vector.

        Notes
        -----
        This method is ``lru_cache``-backed so repeated calls with the same
        ``matrix_folder`` reuse loaded objects.
        '''
        loaded_folder = ExportFolder(matrix_folder)
        if not loaded_folder.has_impacts():
            print('error: no impacts in your export')
            export_folder = None
        else:
            export_folder = loaded_folder

        tech_index_dict = loaded_folder.tech_index()
        A = loaded_folder.load(Matrix.A)
        B = loaded_folder.load(Matrix.B)
        C = loaded_folder.load(Matrix.C)
        f = loaded_folder.load(Matrix.f)
        return export_folder, tech_index_dict, A, B, C, f

    def initialize_base_solver_and_artifacts(self, matrix_folder: str):
        '''
        Prepare and cache the base solver and artifacts for the LCA calculation.

        This method initializes the matrix cache key, attempts to reuse process-local
        cached data, and if not available, loads artifacts from disk or computes them.
        Artifact cache entries include the base scaling vector and original first
        A-column, and are stored on both disk and in RAM. Solver/factorization
        objects are in-memory only and are never written to disk.

        Parameters
        ----------
        matrix_folder : str
            Path to the openLCA matrix export folder.

        Notes
        -----
        - Initializes self._matrix_cache_key, self._A_factor, self._base_scaling_vector, and self._A_col0.
        - Uses atomic file replacement for cache writes (no locking, single-writer assumed).
        '''
        if scipy.sparse.issparse(self.A):
            shape = self.A.shape
            nnz = self.A.nnz
        else:
            shape = np.asarray(self.A).shape
            nnz = int(np.count_nonzero(self.A))

        self._matrix_cache_key = build_matrix_cache_key(matrix_folder, shape, nnz)
        # Try to load solver and artifacts from RAM (process-local cache)
        cached = LCA._base_solver_cache.get(self._matrix_cache_key)
        if cached is not None:
            self._A_factor, self._base_scaling_vector, self._A_col0 = cached
            return
        # Not in RAM: try to load artifacts from disk cache (solver is not stored on disk).
        self._A_factor = None
        base_cache_path = get_disk_cache_dir(self.folder.folder) / f"base_{self._matrix_cache_key}.npz"
        if self.load_solver_from_disk_to_ram(base_cache_path):
            return
        # Not in disk: compute solver and artifacts 
        self._A_factor = factorize(self.A)  # Only stored in RAM
        f_vector = np.asarray(self.f).reshape(-1)
        self._base_scaling_vector = self._A_factor.solve(f_vector)
        if scipy.sparse.issparse(self.A):
            self._A_col0 = np.asarray(self.A[:, 0].toarray()).reshape(-1)
        else:
            self._A_col0 = np.asarray(self.A[:, 0]).reshape(-1)
        # Write only the artifacts to disk cache (not the solver)
        tmp_path = Path(str(base_cache_path) + f".{os.getpid()}.tmp.npz")
        np.savez(tmp_path, base_scaling_vector=self._base_scaling_vector, A_col0=self._A_col0)
        os.replace(tmp_path, base_cache_path)
        # Store in-process artifacts and solver state in RAM for fast reuse.
        self.store_solver_and_artifacts_in_ram()

    def load_solver_from_disk_to_ram(self, base_cache_path) -> bool:
        '''
        Load base artifacts from shared disk cache into process-local state.

        The disk cache contains only artifacts (base scaling vector and first
        A-column). Solver/factorization objects are reconstructed in memory
        when needed and are not read from disk.

        Parameters
        ----------
        base_cache_path : pathlib.Path
            Path to base solver cache file.

        Returns
        -------
        bool
            True if cache data were loaded, otherwise False.
        '''

        if not base_cache_path.exists():
            return False

        try:
            with np.load(base_cache_path) as data:
                self._base_scaling_vector = data['base_scaling_vector']
                self._A_col0 = data['A_col0']
            self.store_solver_and_artifacts_in_ram()
            return True
        except Exception:
            return False

    def store_solver_and_artifacts_in_ram(self):
        '''
        Store process-local solver state and base artifacts in RAM cache.

        The RAM cache stores the in-process factorization object together with
        base artifacts for reuse within the same process. Disk cache remains
        artifact-only.
        '''
        LCA._base_solver_cache[self._matrix_cache_key] = (
            self._A_factor,
            self._base_scaling_vector,
            self._A_col0,
        )
    
    def update_technosphere_column_with_components(self, dcf):
        '''
        Build an updated first-column vector for A from LCA component values.

        For each LCA component defined in dcf.inp with a UUID, this method finds
        the corresponding index in the technosphere matrix and sets that row in a
        copied first-column vector. If the value is an array/list (e.g., yearly H2
        production), the sum is used.

        Parameters
        ----------
        dcf : pyH2A.Discounted_Cash_Flow
            Discounted_Cash_Flow object containing LCA components table.

        Returns
        -------
        None
            Updates self._updated_col0 and component index/value arrays in place.

        Notes
        -----
        The first discovered component is treated as the positive reference contribution;
        subsequent components are signed negatively.
        '''

        lca_table_names = [table_name for table_name in dcf.inp if table_name.lower().startswith('lca')]
        if not lca_table_names: 
            raise ValueError("No LCA component tables found in input. Define at least one table whose name starts with 'LCA'.")

        # Resolve any path-based references (e.g. "A > B > Value") into numbers.
        [process_table(dcf.inp, lca_table_name, 'Value') for lca_table_name in lca_table_names]
        component_map = self.apply_component_updates(dcf, lca_table_names)

        if not component_map:
            raise ValueError("No LCA component indices found after processing input tables. Ensure at least one valid LCA component is defined.")

        self._component_indices = np.asarray(list(component_map.keys()), dtype=int)
        self._component_values = np.asarray(list(component_map.values()), dtype=float)

        updated_col0 = np.array(self._A_col0, copy=True)

        for row_index, signed_value in component_map.items():
            updated_col0[row_index] = signed_value
        self._updated_col0 = updated_col0  
    
    def apply_component_updates(self, dcf, lca_table_names):
        '''
        Apply all component updates to the first technosphere column.

        Parameters
        ----------
        dcf : pyH2A.Discounted_Cash_Flow
            DCF object containing the parsed input dictionary.
        lca_table_names : list of str
            LCA table names to read components from.

        Returns
        -------
        dict
            Mapping {row_index: signed_value} for all component updates.
        '''
        component_map = {}
        for component_position, component in enumerate(
            (item for lca_table_name in lca_table_names for item in dcf.inp[lca_table_name].items())
        ):
            component_name, component_data = component
            uuid, raw_value = self.extract_component_uuid_and_value(component_name, component_data)
            if uuid not in self.tech_index_dict:
                raise ValueError(
                    f"LCA component '{component_name}' has UUID '{uuid}' "
                    f"which was not found in the technosphere matrix index."
                )
            tech_index = self.tech_index_dict[uuid].index
            scalar_value = float(np.sum(raw_value) if isinstance(raw_value, (np.ndarray, list, tuple)) else raw_value)
            signed_value = scalar_value if component_position == 0 else -scalar_value
            component_map[tech_index] = signed_value

        return component_map
        
    def extract_component_uuid_and_value(self, component_name, component_data):
        '''
        Extract required UUID and Value fields from a component.

        Parameters
        ----------
        component_name : str
            Human-readable component name used in error messages.
        component_data : dict
            Component dictionary expected to contain 'UUID' and 'Value'.

        Returns
        -------
        tuple
            Pair (uuid, value) extracted from component_data.

        Raises
        ------
        ValueError
            Raised when required fields are missing.
        '''
        missing_fields = [
            key
            for key in ('UUID', 'Value')
            if key not in component_data
        ]
        if missing_fields:
            raise ValueError(
                f"LCA component '{component_name}' is missing required "
                f"field(s): {missing_fields}"
            )

        return component_data['UUID'], component_data['Value']
    
    def build_scaling_vector(self):
        '''
        Compute scaling vector from a Sherman-Morrison correction term.

        The scaling vector is computed for the LCA calculation using a Sherman-Morrison rank-1 update.
        The scenario change is represented by the updated first-column vector self._updated_col0.
        This is possible because only the first column of A is changed in
        update_technosphere_column_with_components().

        Returns
        -------
        None
            The computed scaling vector is stored on self.scaling_vector.

        Raises
        ------
        ZeroDivisionError
            Raised when |1 + z[0]| is below self._SM_TOL. In this implementation, no direct-solve fallback is used.

        Notes
        -----
        Uses x' = y - z * (y[0] / (1 + z[0])) where y is the base scaling vector and z is the correction vector (A^{-1} u) used in the rank-1 update.
        The basis matrix columns are A^{-1} e_i for changed rows. This avoids solving a full system for every Monte Carlo sample.
        With shared disk basis artifacts, worker processes pay the
        factorization cost once during artifact generation, then reuse the
        basis-correction route for subsequent scaling-vector evaluations.
        '''
        component_indices = self._component_indices

        basis = self.get_basis_vectors_from_ram_or_disk(self._matrix_cache_key, component_indices)
        if basis is None:
            return None

        base_values = self._A_col0[component_indices]
        delta_coeff = self._component_values - base_values
        correction = basis @ delta_coeff
        correction = np.asarray(correction).reshape(-1)
        numerator = self._base_scaling_vector[0]
        denominator = 1.0 + correction[0]

        if abs(denominator) <= self._SM_TOL:
            raise ZeroDivisionError(
                "Sherman-Morrison denominator is too small; "
                "fallback direct solve is disabled."
            )

        self.scaling_vector = self._base_scaling_vector - correction * (numerator / denominator)

    def get_basis_vectors_from_ram_or_disk(self, matrix_key: str, component_indices: np.ndarray):
        '''
        Retrieve or compute-and-cache basis vectors for the given component indices.

        Checks in-process cache, then disk cache, and computes if not found.

        Parameters
        ----------
        matrix_key : str
            Key for the matrix cache.
        component_indices : numpy.ndarray
            Row indices of modified A-column components.

        Returns
        -------
        numpy.ndarray or None
            Basis matrix whose columns are A^{-1} e_i for each component index, or None if cache cannot be loaded/generated.

        Notes
        -----
        Uses in-process cache first, then shared on-disk cache.
        '''
        idx_key = ','.join(str(int(i)) for i in component_indices)
        idx_hash = hashlib.sha1(idx_key.encode('ascii')).hexdigest()[:16]
        cache_path = get_disk_cache_dir(self.folder.folder) / f"basis_{matrix_key}_{idx_hash}.npz" 
        cache_key = str(cache_path)

        in_process_cached = LCA._component_basis_cache.get(cache_key)
        if in_process_cached is not None:
            return in_process_cached

        loaded = self.load_basis_vectors_from_disk(cache_path, component_indices)
        if loaded is None:
           return self.compute_and_store_basis_vectors(cache_path, component_indices, cache_key)
        
        LCA._component_basis_cache[cache_key] = loaded

        return loaded
    
    def load_basis_vectors_from_disk(self, cache_path, component_indices: np.ndarray):
        '''
        Load cached component basis vectors from disk and validate indices.

        Parameters
        ----------
        cache_path : pathlib.Path
            Path to the component basis cache .npz file.
        component_indices : numpy.ndarray
            Expected component row indices for cache validation.

        Returns
        -------
        numpy.ndarray or None
            Basis matrix with columns A^{-1} e_i for each component index, or None if cache is missing/invalid.
        '''

        if not cache_path.exists():
            return None

        try:
            with np.load(cache_path) as data:
                stored_indices = np.asarray(data['component_indices'], dtype=int)
                if not np.array_equal(stored_indices, component_indices):
                    return None

                basis = np.asarray(data['basis'])
                if basis.ndim == 1:
                    basis = basis.reshape(-1, 1)

                return basis
        except Exception:
            return None

    def compute_and_store_basis_vectors(self, cache_path, component_indices: np.ndarray, cache_key: str):
        '''
        Compute, persist, and cache component basis vectors for given indices.

        Parameters
        ----------
        cache_path : pathlib.Path
            Path where basis cache is written.
        component_indices : numpy.ndarray
            Row indices for basis construction.
        cache_key : str
            In-process cache key used in _component_basis_cache.

        Returns
        -------
        numpy.ndarray
            Computed and cached basis matrix.

        Notes
        -----
        - Computes basis vectors A^{-1} e_i for specified row indices.
        - Saves the basis matrix atomically by first writing to a temporary file and then moving it into place.
        - No locking is used; single-writer is assumed.
        '''
        if self._A_factor is None:
            self._A_factor = factorize(self.A)
            LCA._base_solver_cache[self._matrix_cache_key] = (
                self._A_factor,
                self._base_scaling_vector,
                self._A_col0,
            )
        
        solver = self._A_factor
        n_rows = self.A.shape[0]
        n_cols = len(component_indices)

        eye_subset = np.zeros((n_rows, n_cols), dtype=float)
        eye_subset[component_indices, np.arange(n_cols)] = 1.0

        basis = np.asarray(solver.solve(eye_subset))
        if basis.ndim == 1:
            basis = basis.reshape(-1, 1)
        
        tmp_path = Path(str(cache_path) + f".{os.getpid()}.tmp.npz")
        np.savez(tmp_path, component_indices=np.asarray(component_indices, dtype=int), basis=basis)
        os.replace(tmp_path, cache_path)
        LCA._component_basis_cache[cache_key] = basis
        return basis
    
    def perform_lca(self):
        '''
        Perform the Life Cycle Impact Assessment (LCIA) calculation.

        Computes intermediate flows and final impact results using the intervention
        and characterization matrices. Results are stored in the class instance.

        Returns
        -------
        None
            Results are stored on self.lca_results as a dictionary mapping impact names to values and units.

        Notes
        -----
        Final results are stored in the attribute lca_results as a dictionary mapping impact names to values and units.
        '''

        g = self.B @ self.scaling_vector
        h = self.C @ g

        # Store LCIA results on the instance for downstream use.
        self.lca_results = {}
        for i in self.folder.impact_index():
            self.lca_results[i.impact_name] = {
                'value': h[i.index],
                'unit': i.impact_unit
            }
