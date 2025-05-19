from pathlib import Path
from pyH2A.run_pyH2A import pyH2A
from pyH2A.DiscountedCashFlow import DiscountedCashFlow
from pyH2A.Plugins import *
import numpy as np
import csv
import pickle

def compare_values(val1, val2):
    """Recursively compare two values, handling numpy arrays, dicts, and lists."""
    # Compare types first
    if type(val1) != type(val2):
        return False

    # For numpy arrays
    if isinstance(val1, np.ndarray):
        return np.array_equal(val1, val2)
    
    # For dictionaries, compare keys and then recursively compare each value
    if isinstance(val1, dict):
        if val1.keys() != val2.keys():
            return False
        for key in val1:
            if not compare_values(val1[key], val2[key]):
                return False
        return True

    # For lists, compare each element
    if isinstance(val1, list):
        if len(val1) != len(val2):
            return False
        for item1, item2 in zip(val1, val2):
            if not compare_values(item1, item2):
                return False
        return True

    return val1 == val2

def validate_dcf_insertions(
    plugin_class: type,
    snapshot_dir: Path,
    scenario: str
) -> None:
    """Reusable function to test plugin insertions into DCF."""

    # Construct full snapshot file paths
    before_path = snapshot_dir / "snapshot_before.pkl"
    after_path = snapshot_dir / "snapshot_after.pkl"
    entries_path = snapshot_dir / "dict_entries.csv"

    # Load before and after DCF objects
    with open(before_path, "rb") as f:
        dcf_before: DiscountedCashFlow = pickle.load(f)
    with open(after_path, "rb") as f:
        dcf_after: DiscountedCashFlow = pickle.load(f)

    # Load the dict_entries
    with open(entries_path, "r", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        dict_entries: list[tuple[str, str, str]] = [tuple(row) for row in reader]

    # Apply plugin to dcf_before
    plugin_class(dcf_before)

    # Compare values
    for key, subkey, field in dict_entries:
        value_before = dcf_before.inp.get(key, {}).get(subkey, {}).get(field, None)
        value_after = dcf_after.inp.get(key, {}).get(subkey, {}).get(field, None)

        if not compare_values(value_before, value_after):
            raise AssertionError(
                f"[{scenario}] expected {value_after} but got {value_before} for "
                f"{key} -> {subkey} -> {field}"
            )