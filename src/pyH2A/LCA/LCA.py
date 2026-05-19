'''Life cycle assessment core workflow for pyH2A.

This module defines :class:`LCA`, which loads openLCA-exported matrices,
applies scenario-specific technosphere column updates, builds scaling vectors
via Sherman-Morrison updates, and computes LCIA indicator results.

To reduce repeated solve costs in Monte Carlo workloads, the implementation
uses both process-local and shared on-disk caches for base solve artifacts and
component basis vectors.
'''

import hashlib
import os
import tempfile
import time
from functools import lru_cache
from pathlib import Path

import numpy as np
import scipy.sparse
from pyH2A import Discounted_Cash_Flow
from pyH2A.LCA.LCA_lib import ExportFolder, Matrix, factorize
from pyH2A.Utilities.input_modification import process_table

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
    _base_solver_cache = {}  # {matrix_key: (_A_factor, _base_scaling_vector, _A_col0)}
    _component_basis_cache = {}  # {basis_cache_path: basis_matrix}
    _SHARED_CACHE_VERSION = 1
    _SHARED_CACHE_WAIT_S = 10.0
      
    def __init__(self, matrix_folder: str, dcf: Discounted_Cash_Flow):
        '''
            Initializes the LCA object and performs the LCA calculation.

            Parameters
            ----------
            matrix_folder : str
                Path to the openLCA matrix export folder.
            dcf : pyH2A.Discounted_Cash_Flow
                pyH2A Discounted_Cash_Flow object containing model inputs
                used to construct the scaling vector.
        '''

        (
            self.folder,
            self.tech_index_dict,
            self.A,
            self.B,
            self.C,
            self.f,
        ) = self._cached_export_data(matrix_folder)
        self._prepare_base_solver_data(matrix_folder)
        self._updated_col0 = None
        self.update_A_matrix_with_lca_components(dcf)
        self.build_scaling_vector()
        self.perform_LCA()
    
    @staticmethod      
    @lru_cache(maxsize=None)
    def _cached_export_data(matrix_folder: str):
        '''Load and cache openLCA folder metadata and matrices.

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

    @classmethod
    def _shared_cache_dir(cls):
        '''Return the shared on-disk cache directory.

        Returns
        -------
        pathlib.Path
            Directory path used to store shared cache artifacts. The directory
            is created if it does not already exist.
        '''

        cache_dir = Path(tempfile.gettempdir()) / 'pyH2A_lca_cache'
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    @classmethod
    def _build_matrix_cache_key(cls, matrix_folder: str, matrix) -> str:
        '''Build a stable cache key for matrix-dependent shared artifacts.

        Parameters
        ----------
        matrix_folder : str
            Path to the matrix export folder.
        matrix : ndarray or scipy.sparse matrix
            Matrix object used to include structural information in the key.

        Returns
        -------
        str
            SHA-1 digest string derived from cache version, export
            folder path, and matrix structure.
        '''

        if scipy.sparse.issparse(matrix):
            shape = matrix.shape
            nnz = matrix.nnz
        else:
            shape = np.asarray(matrix).shape
            nnz = int(np.count_nonzero(matrix))

        raw_key = (
            f"v{cls._SHARED_CACHE_VERSION}|{matrix_folder}|"
            f"shape={shape}|nnz={nnz}"
        )
        return hashlib.sha1(raw_key.encode('utf-8')).hexdigest()

    @classmethod
    def _base_cache_path(cls, matrix_key: str):
        '''Build the cache file path for base solver data.

        Parameters
        ----------
        matrix_key : str
            Cache key generated by :meth:`_build_matrix_cache_key`.

        Returns
        -------
        pathlib.Path
            Path to the ``.npz`` file storing base scaling_vector data.
        '''
        return cls._shared_cache_dir() / f"base_{matrix_key}.npz"

    @classmethod
    def _component_cache_path(cls, matrix_key: str, component_indices: np.ndarray):
        '''Build the cache file path for component basis vectors.

        Parameters
        ----------
        matrix_key : str
            Cache key generated by :meth:`_build_matrix_cache_key`.
        component_indices : numpy.ndarray
            Row indices of A-column components used to construct basis vectors.

        Returns
        -------
        pathlib.Path
            Path to the ``.npz`` file storing cached basis vectors for the
            specified component index set.
        '''
        idx_key = ','.join(str(int(i)) for i in component_indices)
        idx_hash = hashlib.sha1(idx_key.encode('ascii')).hexdigest()[:16]
        return cls._shared_cache_dir() / f"basis_{matrix_key}_{idx_hash}.npz"

    @staticmethod
    def _load_base_cache(cache_path):
        '''Load base solver cache arrays from disk.

        Parameters
        ----------
        cache_path : pathlib.Path
            Path to the base cache ``.npz`` file.

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray] or None
            Tuple ``(base_scaling_vector, A_col0)`` when cache loading succeeds;
            otherwise ``None``.
        '''

        if not cache_path.exists():
            return None

        try:
            with np.load(cache_path) as data:
                base_scaling_vector = np.asarray(data['base_scaling_vector']).reshape(-1)
                A_col0 = np.asarray(data['A_col0']).reshape(-1)
                return base_scaling_vector, A_col0
        except Exception:
            return None

    @staticmethod
    def _atomic_save_npz(cache_path, **arrays):
        '''Atomically save arrays to an ``.npz`` cache file.

        Parameters
        ----------
        cache_path : pathlib.Path
            Final destination path of the cache file.
        **arrays : dict
            Named arrays passed to :func:`numpy.savez`.

        Notes
        -----
        Data are first written to a process-specific temporary file and then
        moved into place with :func:`os.replace` to avoid partially-written
        cache files.
        '''

        tmp_path = Path(str(cache_path) + f".{os.getpid()}.tmp.npz")
        np.savez(tmp_path, **arrays)
        os.replace(tmp_path, cache_path)

    @staticmethod
    def _acquire_lock(lock_path):
        '''Acquire an exclusive file-based lock.

        Parameters
        ----------
        lock_path : pathlib.Path
            Lock file path.

        Returns
        -------
        int or None
            OS file descriptor when lock acquisition succeeds, otherwise
            ``None`` when lock is already held by another process.
        '''

        try:
            flags = os.O_CREAT | os.O_EXCL | os.O_RDWR
            fd = os.open(str(lock_path), flags)
            os.write(fd, str(os.getpid()).encode('ascii'))
            return fd
        except FileExistsError:
            return None

    @staticmethod
    def _release_lock(lock_path, lock_fd):
        '''Release a previously-acquired file lock.

        Parameters
        ----------
        lock_path : pathlib.Path
            Lock file path.
        lock_fd : int
            File descriptor returned by :meth:`_acquire_lock`.
        '''

        try:
            os.close(lock_fd)
        finally:
            try:
                os.remove(lock_path)
            except FileNotFoundError:
                pass

    def _ensure_factorized_solver(self):
        '''Ensure a process-local factorized solver is available.

        Returns
        -------
        object
            Factorized solver object returned by :func:`factorize`, supporting
            repeated ``solve`` calls.
        '''

        if self._A_factor is None:
            self._A_factor = factorize(self.A)
            LCA._base_solver_cache[self._matrix_cache_key] = (
                self._A_factor,
                self._base_scaling_vector,
                self._A_col0,
            )
        return self._A_factor

    def _load_and_cache_component_basis(self, cache_path, component_indices: np.ndarray, cache_key: str):
        '''Load component basis vectors from disk and cache them in process.

        Parameters
        ----------
        cache_path : pathlib.Path
            Path to the component basis cache ``.npz`` file.
        component_indices : numpy.ndarray
            Expected component row indices used for cache validation.
        cache_key : str
            In-process cache key used in ``_component_basis_cache``.

        Returns
        -------
        numpy.ndarray or None
            Loaded basis matrix when successful, otherwise ``None``.
        '''

        loaded = self._load_component_basis(cache_path, component_indices)
        if loaded is None:
            return None
        LCA._component_basis_cache[cache_key] = loaded
        return loaded

    def _compute_component_basis(self, component_indices: np.ndarray):
        '''Compute basis vectors ``A^{-1} e_i`` for specified row indices.

        Parameters
        ----------
        component_indices : numpy.ndarray
            Row indices of changed components in the first column of ``A``.

        Returns
        -------
        numpy.ndarray
            Basis matrix with one column per entry in ``component_indices``.
        '''

        solver = self._ensure_factorized_solver()
        n_rows = self.A.shape[0]
        n_cols = len(component_indices)

        eye_subset = np.zeros((n_rows, n_cols), dtype=float)
        eye_subset[component_indices, np.arange(n_cols)] = 1.0

        basis = np.asarray(solver.solve(eye_subset))
        if basis.ndim == 1:
            basis = basis.reshape(-1, 1)
        return basis

    def _build_and_cache_component_basis(self, cache_path, component_indices: np.ndarray, cache_key: str):
        '''Compute, persist, and cache component basis vectors.

        Parameters
        ----------
        cache_path : pathlib.Path
            Path where basis cache is written.
        component_indices : numpy.ndarray
            Row indices for basis construction.
        cache_key : str
            In-process cache key used in ``_component_basis_cache``.

        Returns
        -------
        numpy.ndarray
            Computed and cached basis matrix.
        '''

        basis = self._compute_component_basis(component_indices)
        self._atomic_save_npz(
            cache_path,
            component_indices=np.asarray(component_indices, dtype=int),
            basis=basis,
        )
        LCA._component_basis_cache[cache_key] = basis
        return basis

    def _wait_for_component_basis_cache(self, cache_path, component_indices: np.ndarray, cache_key: str):
        '''Wait for component basis cache produced by another process.

        Parameters
        ----------
        cache_path : pathlib.Path
            Path to basis cache file.
        component_indices : numpy.ndarray
            Expected row indices for cache validation.
        cache_key : str
            In-process cache key used in ``_component_basis_cache``.

        Returns
        -------
        numpy.ndarray or None
            Loaded basis matrix if available within wait window, else ``None``.
        '''

        deadline = time.time() + self._SHARED_CACHE_WAIT_S
        while time.time() < deadline:
            loaded = self._load_and_cache_component_basis(
                cache_path,
                component_indices,
                cache_key,
            )
            if loaded is not None:
                return loaded
            time.sleep(0.05)

        return None

    def _load_component_basis(self, cache_path, component_indices: np.ndarray):
        '''Load cached component basis vectors from disk.

        Parameters
        ----------
        cache_path : pathlib.Path
            Path to the component basis cache ``.npz`` file.
        component_indices : numpy.ndarray
            Expected component row indices for cache validation.

        Returns
        -------
        numpy.ndarray or None
            Basis matrix with columns ``A^{-1} e_i`` for each component index,
            or ``None`` when cache is missing/invalid.
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

    def _get_or_create_component_basis(self, component_indices: np.ndarray):
        '''Get or create shared basis vectors for component indices.

        Parameters
        ----------
        component_indices : numpy.ndarray
            Row indices of modified A-column components.

        Returns
        -------
        numpy.ndarray or None
            Basis matrix whose columns are ``A^{-1} e_i`` for each component
            index. Returns ``None`` if cache cannot be loaded/generated within
            the configured wait window.

        Notes
        -----
        The method uses an in-process cache first, then a shared on-disk cache.
        File locking ensures that only one process writes a given basis cache.
        '''

        cache_path = self._component_cache_path(self._matrix_cache_key, component_indices)
        cache_key = str(cache_path)

        in_process_cached = LCA._component_basis_cache.get(cache_key)
        if in_process_cached is not None:
            return in_process_cached

        loaded = self._load_and_cache_component_basis(
            cache_path,
            component_indices,
            cache_key,
        )
        if loaded is not None:
            return loaded

        lock_path = Path(str(cache_path) + '.lock')
        lock_fd = self._acquire_lock(lock_path)

        if lock_fd is None:
            return self._wait_for_component_basis_cache(
                cache_path,
                component_indices,
                cache_key,
            )

        try:
            # Another process may have completed while lock acquisition was racing.
            loaded = self._load_and_cache_component_basis(
                cache_path,
                component_indices,
                cache_key,
            )
            if loaded is not None:
                return loaded

            return self._build_and_cache_component_basis(
                cache_path,
                component_indices,
                cache_key,
            )
        finally:
            self._release_lock(lock_path, lock_fd)

    def _cache_base_solver_data(self):
        '''Store current base solver artifacts in process-local cache.'''

        LCA._base_solver_cache[self._matrix_cache_key] = (
            self._A_factor,
            self._base_scaling_vector,
            self._A_col0,
        )

    def _load_cached_base_solver_data(self, base_cache_path) -> bool:
        '''Load base solver artifacts from shared disk cache.

        Parameters
        ----------
        base_cache_path : pathlib.Path
            Path to base solver cache file.

        Returns
        -------
        bool
            ``True`` when cache data were loaded, otherwise ``False``.
        '''

        loaded = self._load_base_cache(base_cache_path)
        if loaded is None:
            return False

        self._base_scaling_vector, self._A_col0 = loaded
        self._cache_base_solver_data()
        return True

    def _compute_base_solver_data(self):
        '''Compute base scaling_vector and original first-column vector for ``A``.'''

        self._A_factor = factorize(self.A)
        f_vector = np.asarray(self.f).reshape(-1)
        self._base_scaling_vector = self._A_factor.solve(f_vector)
        if scipy.sparse.issparse(self.A):
            self._A_col0 = np.asarray(self.A[:, 0].toarray()).reshape(-1)
        else:
            self._A_col0 = np.asarray(self.A[:, 0]).reshape(-1)

    def _wait_for_base_solver_cache(self, base_cache_path) -> bool:
        '''Wait for base solver cache produced by another process.

        Parameters
        ----------
        base_cache_path : pathlib.Path
            Path to base solver cache file.

        Returns
        -------
        bool
            ``True`` when cache data became available, otherwise ``False``.
        '''

        deadline = time.time() + self._SHARED_CACHE_WAIT_S
        while time.time() < deadline:
            if self._load_cached_base_solver_data(base_cache_path):
                return True
            time.sleep(0.05)
        return False

    def _prepare_base_solver_data(self, matrix_folder: str):
        '''Prepare base solver data and process-local solver state.

        Parameters
        ----------
        matrix_folder : str
            Path to the openLCA matrix export folder.

        Notes
        -----
        This method initializes ``self._matrix_cache_key``, ``self._A_factor``,
        ``self._base_scaling_vector``, and ``self._A_col0``.

        It first attempts to reuse process-local and shared on-disk cache data.
        If cache data are unavailable, it computes base data once, writes cache
        artifacts atomically, and exposes them for subsequent reuse.
        '''

        self._matrix_cache_key = self._build_matrix_cache_key(matrix_folder, self.A)

        cached = LCA._base_solver_cache.get(self._matrix_cache_key)
        if cached is not None:
            self._A_factor, self._base_scaling_vector, self._A_col0 = cached
            return

        self._A_factor = None

        base_cache_path = self._base_cache_path(self._matrix_cache_key)
        if self._load_cached_base_solver_data(base_cache_path):
            return

        lock_path = Path(str(base_cache_path) + '.lock')
        lock_fd = self._acquire_lock(lock_path)

        if lock_fd is None:
            if self._wait_for_base_solver_cache(base_cache_path):
                return

            # Last-resort fallback if lock holder crashes: compute locally.
            self._compute_base_solver_data()
            self._cache_base_solver_data()
            return

        try:
            # Re-check in case another process completed before lock acquisition.
            if self._load_cached_base_solver_data(base_cache_path):
                return

            self._compute_base_solver_data()
            self._atomic_save_npz(
                base_cache_path,
                base_scaling_vector=self._base_scaling_vector,
                A_col0=self._A_col0,
            )
            self._cache_base_solver_data()
        finally:
            self._release_lock(lock_path, lock_fd)

    @staticmethod    
    def _get_lca_component_table_names(dcf):
        '''Return names of all input tables that start with ``LCA``.

        Parameters
        ----------
        dcf : pyH2A.Discounted_Cash_Flow
            DCF object containing parsed input tables in ``dcf.inp``.

        Returns
        -------
        list of str
            Table names whose lowercase form starts with ``lca``.
        '''
        return [
            table_name
            for table_name in dcf.inp
            if table_name.lower().startswith('lca')
        ]

    @staticmethod
    def _resolve_lca_values(dcf, lca_table_names):
        '''Resolve path-based ``Value`` fields for all LCA tables.

        Parameters
        ----------
        dcf : pyH2A.Discounted_Cash_Flow
            DCF object whose ``inp`` dictionary is modified in place.
        lca_table_names : list of str
            LCA table names to process.

        Notes
        -----
        Uses :func:`process_table` to resolve path expressions such as
        ``A > B > Value`` into numeric values.
        '''
        for lca_table_name in lca_table_names:
            process_table(dcf.inp, lca_table_name, 'Value')

    def _iter_lca_components(self, dcf, lca_table_names):
        '''Yield component entries from the configured LCA tables.

        Parameters
        ----------
        dcf : pyH2A.Discounted_Cash_Flow
            DCF object containing parsed input data.
        lca_table_names : list of str
            Table names to iterate.

        Yields
        ------
        tuple[str, dict]
            ``(component_name, component_data)`` pairs from each LCA table.
        '''
        for lca_table_name in lca_table_names:
            yield from dcf.inp[lca_table_name].items()

    @staticmethod
    def _extract_component_fields(component_name, component_data):
        '''Extract required ``UUID`` and ``Value`` fields from a component.

        Parameters
        ----------
        component_name : str
            Human-readable component name used in error messages.
        component_data : dict
            Component dictionary expected to contain ``UUID`` and ``Value``.

        Returns
        -------
        tuple
            Pair ``(uuid, value)`` extracted from ``component_data``.

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

    def _resolve_component_index(self, component_name, uuid):
        '''Resolve a component UUID to its technosphere row index.

        Parameters
        ----------
        component_name : str
            Human-readable component name used in error messages.
        uuid : str
            Process UUID expected in ``self.tech_index_dict``.

        Returns
        -------
        int
            Technosphere row index for the given UUID.

        Raises
        ------
        ValueError
            Raised when ``uuid`` is not available in the technosphere index.
        '''
        if uuid not in self.tech_index_dict:
            raise ValueError(
                f"LCA component '{component_name}' has UUID '{uuid}' "
                f"which was not found in the technosphere matrix index."
            )

        return self.tech_index_dict[uuid].index

    @staticmethod
    def _normalize_component_value(component_name, value):
        '''Normalize a component value to a scalar float.

        Parameters
        ----------
        component_name : str
            Human-readable component name used in error messages.
        value : float or array-like
            Component value to normalize.

        Returns
        -------
        float
            Scalar float value. Array-like inputs are summed first.

        Raises
        ------
        ValueError
            Raised when conversion to float fails.
        '''
        if isinstance(value, (np.ndarray, list, tuple)):
            value = np.sum(value)

        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"LCA component '{component_name}' resolved to non-numeric value: {value}"
            ) from exc

    @staticmethod
    def _signed_component_value(value, component_position):
        '''Apply sign convention for first-column component updates.

        Parameters
        ----------
        value : float
            Absolute component contribution.
        component_position : int
            Zero-based position of the component in the iteration order.

        Returns
        -------
        float
            Positive ``value`` for the first component and negative ``value``
            for all subsequent components.
        '''
        if component_position == 0:
            return value
        return -value

    def _component_update_entry(self, component_name, component_data, component_position):
        '''Create a normalized matrix update entry for one component.

        Parameters
        ----------
        component_name : str
            Human-readable component name.
        component_data : dict
            Component dictionary containing at least ``UUID`` and ``Value``.
        component_position : int
            Zero-based iteration position used for sign convention.

        Returns
        -------
        tuple[int, float]
            Pair ``(row_index, signed_value)`` for first-column updates.
        '''
        uuid, raw_value = self._extract_component_fields(component_name, component_data)
        tech_index = self._resolve_component_index(component_name, uuid)
        scalar_value = self._normalize_component_value(component_name, raw_value)
        signed_value = self._signed_component_value(scalar_value, component_position)
        return tech_index, signed_value

    def _apply_component_updates(self, dcf, lca_table_names):
        '''Apply all component updates to the first technosphere column.

        Parameters
        ----------
        dcf : pyH2A.Discounted_Cash_Flow
            DCF object containing the parsed input dictionary.
        lca_table_names : list of str
            LCA table names to read components from.

        Returns
        -------
        dict
            Mapping ``{row_index: signed_value}`` for all component updates.
        '''
        component_map = {}
        for component_position, component in enumerate(
            self._iter_lca_components(dcf, lca_table_names)
        ):
            component_name, component_data = component
            tech_index, signed_value = self._component_update_entry(
                component_name,
                component_data,
                component_position,
            )
            component_map[tech_index] = signed_value

        return component_map

    def _scaling_from_correction(self, correction):
        '''Compute scaling vector from a Sherman-Morrison correction term.

        Parameters
        ----------
        correction : array-like
            Correction vector ``z = A^{-1} u`` used in the rank-1 update.

        Returns
        -------
        numpy.ndarray
            Updated scaling vector.

        Raises
        ------
        ZeroDivisionError
            Raised when ``|1 + z[0]|`` is below ``self._SM_TOL``. In this
            implementation, no direct-solve fallback is used.

        Notes
        -----
        Uses ``x' = y - z * (y[0] / (1 + z[0]))`` where ``y`` is the base
        scaling_vector.
        '''
        correction = np.asarray(correction).reshape(-1)
        numerator = self._base_scaling_vector[0]
        denominator = 1.0 + correction[0]

        if abs(denominator) <= self._SM_TOL:
            raise ZeroDivisionError(
                "Sherman-Morrison denominator is too small; "
                "fallback direct solve is disabled."
            )

        return self._base_scaling_vector - correction * (numerator / denominator)

    def _scaling_from_cached_component_basis(self):
        '''Build scaling vector from cached component basis vectors.

        Returns
        -------
        numpy.ndarray or None
            Scaling vector if component indices are available and basis vectors
            can be loaded or generated; otherwise ``None``.

        Notes
        -----
        The basis matrix columns are ``A^{-1} e_i`` for changed rows. This
        avoids solving a full system for every Monte Carlo sample.
        '''
        component_indices = getattr(self, '_component_indices', None)
        if component_indices is None or len(component_indices) == 0:
            return None

        basis = self._get_or_create_component_basis(component_indices)
        if basis is None:
            return None

        base_values = self._A_col0[component_indices]
        delta_coeff = self._component_values - base_values
        correction = basis @ delta_coeff
        return self._scaling_from_correction(correction)
    
    def build_scaling_vector(self):
        '''
            Builds the scaling vector used for the LCA calculation.

            The scaling vector is computed via a Sherman-Morrison rank-1
            update, where the scenario change is represented by the updated
            first-column vector ``self._updated_col0``. This is possible
            because only the first column of ``A`` is changed in
            `update_A_matrix_with_lca_components()`.

            Returns
            -------
            None
                The computed scaling vector is stored on ``self.scaling_vector``.

            Notes
            -----
            Let A be the base matrix, A' be the modified matrix, and f be
            the demand vector. This method computes x' solving A' x' = f via
            Sherman-Morrison using:

            - base scaling_vector y = A^{-1} f
            - column update u = A'[:,0] - A[:,0]
            - correction z = A^{-1} u

            with x' = y - z * (y[0] / (1 + z[0])).

            In this implementation, if ``|1 + z[0]|`` is too small, an
            exception is raised and no direct-solve fallback is attempted.

        '''

        # Fast path: if modified rows are known, use cached basis vectors
        # A^-1 * e_i for those rows to avoid per-sample sparse solves.
        scaling_vector = self._scaling_from_cached_component_basis()
        if scaling_vector is not None:
            self.scaling_vector = scaling_vector
            return

        # First-column rank-1 update using an explicit delta column solve.
        solver = self._ensure_factorized_solver()

        # Only the first column of A changes per scenario.
        delta_col0 = self._updated_col0 - self._A_col0
        correction = solver.solve(delta_col0)

        self.scaling_vector = self._scaling_from_correction(correction)

    def update_A_matrix_with_lca_components(self, dcf):
        '''
            Builds an updated first-column vector for ``A`` from LCA
            component values.
            
            For each LCA component defined in dcf.inp with a UUID, this method
            finds the corresponding index in the technosphere matrix and sets
            that row in a copied first-column vector. If the value is an
            array/list like yearly H2 production, the sum is used.

            Parameters
            ----------
            dcf : pyH2A.Discounted_Cash_Flow
                pyH2A Discounted_Cash_Flow object containing LCA components table.

            Returns
            -------
            None
                ``self._updated_col0`` and component index/value arrays are
                updated in place.

            Notes
            -----
            The first discovered component is treated as the positive reference
            contribution and subsequent components are signed negatively.
        '''

        lca_table_names = self._get_lca_component_table_names(dcf)
        if not lca_table_names: 
            raise ValueError("No LCA component tables found in input. Define at least one table whose name starts with 'LCA'.")

        # Resolve any path-based references (e.g. "A > B > Value") into numbers.
        self._resolve_lca_values(dcf, lca_table_names)
        component_map = self._apply_component_updates(dcf, lca_table_names)

        self._component_indices = np.asarray(list(component_map.keys()), dtype=int)
        self._component_values = np.asarray(list(component_map.values()), dtype=float)

        updated_col0 = np.array(self._A_col0, copy=True)
        for row_index, signed_value in component_map.items():
            updated_col0[row_index] = signed_value
        self._updated_col0 = updated_col0

    def perform_LCA(self):
        '''
            Performs the Life Cycle Impact Assessment (LCIA) calculation.

            The method computes intermediate flows and final impact
            results using the intervention and characterization matrices.
            Results are stored in the class instance.

            Notes
            -----
            Final results are stored in the attribute `lca_results`
            as a dictionary mapping impact names to values and units.

            Returns
            -------
            None
                Results are stored on ``self.lca_results``.
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