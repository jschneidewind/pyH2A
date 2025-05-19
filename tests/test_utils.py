"""
Utility functions for validating DiscountedCashFlow (DCF) insertions by plugins.
"""
from pathlib import Path
from typing import Any, List, Tuple, Type

import numpy as np
import csv
import pickle

from pyH2A.DiscountedCashFlow import DiscountedCashFlow


def compare_values(
        val1: Any, 
        val2: Any
        ) -> bool:
    """
    Recursively compare two values, handling numpy arrays, dictionaries, and lists.

    Args:
        val1: First value to compare.
        val2: Second value to compare.

    Returns:
        True if the values are equivalent, False otherwise.
    """
    if type(val1) is not type(val2):
        return False

    if isinstance(val1, np.ndarray):
        return np.array_equal(val1, val2)

    if isinstance(val1, dict):
        if val1.keys() != val2.keys():
            return False
        return all(compare_values(val1[k], val2[k]) for k in val1)

    if isinstance(val1, list):
        if len(val1) != len(val2):
            return False
        return all(compare_values(a, b) for a, b in zip(val1, val2))

    return val1 == val2


def validate_dcf_insertions(
        plugin_class: Type[Any],
        snapshot_dir: Path,
        scenario: str
        ) -> None:
    """
    Validate plugin modifications to a DiscountedCashFlow object.

    Loads pre- and post-plugin DiscountedCashFlow snapshots, applies the plugin,
    and compares specified input entries to verify consistency.

    :param plugin_class: Plugin class to be applied (expects a DCF instance).
    :type plugin_class: Type[Any]
    :param snapshot_dir: Path to directory containing `snapshot_before.pkl`, `snapshot_after.pkl`, and `dict_entries.csv`.
    :type snapshot_dir: Path
    :param scenario: Descriptive name of the scenario under test.
    :type scenario: str
    :raises AssertionError: If any compared value differs after plugin insertion.
    """
    before_path: Path = snapshot_dir / "snapshot_before.pkl"
    after_path:  Path = snapshot_dir / "snapshot_after.pkl"
    entries_path: Path = snapshot_dir / "dict_entries.csv"

    with before_path.open("rb") as f:
        dcf_before: DiscountedCashFlow = pickle.load(f)
    with after_path.open("rb") as f:
        dcf_after: DiscountedCashFlow = pickle.load(f)

    with entries_path.open("r", newline="") as f:
        reader = csv.reader(f)
        _header = next(reader, None)
        entries: List[Tuple[str, str, str]] = [tuple(row) for row in reader]

    # Apply plugin to the before snapshot
    plugin_class(dcf_before)

    # Compare each specified entry
    for key, subkey, field in entries:
        before_val: Any = dcf_before.inp.get(key, {}).get(subkey, {}).get(field)
        after_val:  Any = dcf_after.inp.get(key, {}).get(subkey, {}).get(field)

        if not compare_values(before_val, after_val):
            msg = (
                f"[{scenario}] Mismatch in {key} -> {subkey} -> {field}: "
                f"expected {after_val!r}, got {before_val!r}"
            )
            raise AssertionError(msg)
