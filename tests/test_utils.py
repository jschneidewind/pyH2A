"""Utility functions for validating DiscountedCashFlow (DCF) insertions by plugins.

This module provides functions to compare complex data structures, including
those containing NumPy arrays, and to validate the effects of pyH2A plugins
on DiscountedCashFlow objects by comparing their state against pre-recorded
snapshots.
"""
from pathlib import Path
from typing import Any, List, Tuple, Type

import numpy as np
import csv
import pickle

from pyH2A.DiscountedCashFlow import DiscountedCashFlow # Assuming this is the correct import path.


def compare_values(val1: Any, val2: Any) -> bool:
    """Recursively compare two values for equality.

    Handles comparisons for basic types, NumPy arrays, dictionaries, and lists.
    For dictionaries, keys and corresponding values must match. For lists,
    elements at corresponding positions must match.

    Parameters
    ----------
    val1 : Any
        The first value to compare.
    val2 : Any
        The second value to compare.

    Returns
    -------
    bool
        True if the values are considered equal, False otherwise.
        Type mismatches immediately result in False.
    """
    if type(val1) is not type(val2):
        return False # Different types are not considered equal.

    if isinstance(val1, np.ndarray):
        # Use numpy's array_equal for element-wise comparison of arrays.
        return np.array_equal(val1, val2)

    if isinstance(val1, dict):
        if val1.keys() != val2.keys():
            return False # Different keys mean dictionaries are not equal.
        # Recursively compare values for each key.
        return all(compare_values(val1[k], val2[k]) for k in val1)

    if isinstance(val1, list):
        if len(val1) != len(val2):
            return False # Different lengths mean lists are not equal.
        # Recursively compare elements at each position.
        return all(compare_values(a, b) for a, b in zip(val1, val2))

    # For other types, use standard equality comparison.
    return val1 == val2


def validate_dcf_insertions(
        plugin_class: Type[Any],
        snapshot_dir: Path,
        scenario: str
        ) -> None:
    """Validate modifications made by a plugin to a DiscountedCashFlow object.

    This function loads a 'before' state of a DiscountedCashFlow object,
    applies the specified plugin to it, and then compares selected input
    entries against an 'after' state (also loaded from a snapshot).
    The specific entries to compare are read from a CSV file.

    Parameters
    ----------
    plugin_class : Type[Any]
        The class of the plugin to be instantiated and applied.
        It is assumed that the plugin's constructor or a method
        takes a DiscountedCashFlow instance and modifies it in place.
    snapshot_dir : Path
        The directory path containing the snapshot files. Expected files are:
        - `snapshot_before.pkl`: Pickled DiscountedCashFlow object before plugin application.
        - `snapshot_after.pkl`: Pickled DiscountedCashFlow object representing the expected state after plugin application.
        - `dict_entries.csv`: CSV file specifying which dictionary entries to compare.
          Each row should contain (key, subkey, field).
    scenario : str
        A descriptive name for the test scenario, used in assertion messages.

    Raises
    ------
    FileNotFoundError
        If any of the required snapshot files (`snapshot_before.pkl`,
        `snapshot_after.pkl`, `dict_entries.csv`) are not found in `snapshot_dir`.
    pickle.UnpicklingError
        If there is an error deserializing the .pkl files.
    csv.Error
        If there is an error reading the `dict_entries.csv` file.
    AssertionError
        If any of the compared values between the plugin-modified 'before' state
        and the 'after' state do not match according to `compare_values`.
    """
    before_path: Path = snapshot_dir / "snapshot_before.pkl"
    after_path: Path = snapshot_dir / "snapshot_after.pkl"
    entries_path: Path = snapshot_dir / "dict_entries.csv"

    # Load the DiscountedCashFlow object before plugin application.
    with before_path.open("rb") as f:
        dcf_before: DiscountedCashFlow = pickle.load(f)
    # Load the expected DiscountedCashFlow object after plugin application.
    with after_path.open("rb") as f:
        dcf_after: DiscountedCashFlow = pickle.load(f)

    # Load the list of dictionary entries to be compared.
    with entries_path.open("r", newline="") as f:
        reader = csv.reader(f)
        _header = next(reader, None) # Skip header row.
        # Each row in the CSV defines a path to a value within dcf.inp: (key, subkey, field)
        entries_to_compare: List[Tuple[str, str, str]] = [tuple(row) for row in reader]

    # Instantiate and apply the plugin to the 'before' DCF object.
    # This modifies dcf_before in place.
    plugin_instance = plugin_class(dcf_before) # Assuming plugin modifies dcf_before upon instantiation or via a method.
                                            # If plugin has an `apply` method, it would be: plugin_instance.apply(dcf_before)

    # Compare each specified entry in the modified dcf_before with dcf_after.
    for key, subkey, field in entries_to_compare:
        # Retrieve the value from the modified dcf_before.
        # Uses .get() to avoid KeyError if a path component is missing, returning None instead.
        value_from_plugin_modified_dcf: Any = dcf_before.inp.get(key, {}).get(subkey, {}).get(field)
        # Retrieve the corresponding expected value from dcf_after.
        expected_value_from_snapshot: Any = dcf_after.inp.get(key, {}).get(subkey, {}).get(field)

        if not compare_values(value_from_plugin_modified_dcf, expected_value_from_snapshot):
            error_message = (
                f"[{scenario}] Mismatch in DCF input at path: {key} -> {subkey} -> {field}. "
                f"Expected (from snapshot_after.pkl): {expected_value_from_snapshot!r}, "
                f"Got (after applying plugin to snapshot_before.pkl): {value_from_plugin_modified_dcf!r}"
            )
            raise AssertionError(error_message)