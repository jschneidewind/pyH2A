"""Test suite for pyH2A scenarios, modes, and plugin validations.

This module contains tests for pyH2A, focusing on:
    - Validation and regeneration of markdown input templates.
    - Verification of H₂ production costs against expected values.
    - Validation of plugin-specific data insertions using snapshots.

It includes utilities for collecting test cases based on directory structure,
running pyH2A models, comparing outputs, and managing test artifacts like
snapshots and templates based on pytest command-line options.
"""
import json
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type

import pytest
import pyH2A.Plugins as Plugins # pyH2A.Plugins is a module containing all plugin classes.
from pyH2A.run_pyH2A import pyH2A
from pyH2A.Utilities.plugin_input_output_processing import Generate_Template_Input_File
from tests.test_utils import validate_dcf_insertions

# -----------------------------------------------------------------------------
# Global test data and configuration
# -----------------------------------------------------------------------------

# Path to the JSON file containing expected H₂ costs for various scenarios and modes.
EXPECTED_H2_COSTS_FILE: Path = Path("tests/expected_h2_costs.json")
# Dictionary to store expected H₂ costs, keyed by (scenario_name, mode_name).
EXPECTED_H2_COSTS: Dict[Tuple[str, str], Any] = {}
# Flag indicating whether the expected H₂ costs were successfully loaded.
EXPECTED_COSTS_LOADED: bool = False

# Attempt to load expected H₂ cost values from the JSON file.
try:
    if EXPECTED_H2_COSTS_FILE.exists():
        with EXPECTED_H2_COSTS_FILE.open("r") as f:
            # loaded is a temporary dict with scenario as key and a nested dict of mode:cost as value.
            loaded_costs_from_file: Dict[str, Dict[str, Any]] = json.load(f)
        # Restructure the loaded data into the EXPECTED_H2_COSTS format.
        EXPECTED_H2_COSTS = {
            (scenario, mode): cost
            for scenario, modes_data in loaded_costs_from_file.items()
            for mode, cost in modes_data.items()
        }
        EXPECTED_COSTS_LOADED = True
except json.JSONDecodeError:
    # If JSON is malformed, set loaded flag to False.
    EXPECTED_COSTS_LOADED = False

# Cache for pyH2A run results to avoid redundant computations, keyed by (scenario_name, mode_name).
_run_cache: Dict[Tuple[str, str], Any] = {}
# Threading lock to ensure thread-safe access to the _run_cache.
_run_lock: threading.Lock = threading.Lock()

# Root directory containing all test files and scenario/mode subdirectories.
_TESTS_ROOT: Path = Path("tests")

# Dictionary mapping plugin names (strings) to their corresponding plugin classes.
# This is built by iterating through all members of the pyH2A.Plugins module.
PLUGINS: Dict[str, Type[Any]] = {name: getattr(Plugins, name) for name in Plugins.__all__}

# -----------------------------------------------------------------------------
# Pytest CLI options
# -----------------------------------------------------------------------------

def pytest_addoption(parser: pytest.Parser) -> None:
    """Register custom command-line options for pytest.

    Adds options to control the regeneration of snapshot files and
    template input files during test runs.

    Parameters
    ----------
    parser : pytest.Parser
        The pytest command-line argument parser.
    """
    parser.addoption(
        "--update-snapshots",
        action="store_true",
        default=False,
        help="Regenerate snapshot files."
    )
    parser.addoption(
        "--update-templates",
        action="store_true",
        default=False,
        help="Regenerate template input files."
    )

# -----------------------------------------------------------------------------
# Test case collection helpers
# -----------------------------------------------------------------------------

def collect_all_modes(root_dir: Path) -> List[Tuple[str, str]]:
    """Scan the directory structure to find all scenario/mode pairs.

    Assumes a structure where `root_dir` contains scenario directories,
    and each scenario directory contains mode directories. Directories
    starting with '.' or '__' are ignored.

    Parameters
    ----------
    root_dir : Path
        The root directory to scan for scenarios and modes.

    Returns
    -------
    List[Tuple[str, str]]
        A sorted list of (scenario_name, mode_name) tuples.
    """
    modes: List[Tuple[str, str]] = []
    for scenario_path in root_dir.iterdir():
        # Ignore hidden files/directories and special Python directories.
        if not scenario_path.is_dir() or scenario_path.name.startswith((".", "__")):
            continue
        for mode_path in scenario_path.iterdir():
            if not mode_path.is_dir() or mode_path.name.startswith((".", "__")):
                continue
            modes.append((scenario_path.name, mode_path.name))
    return sorted(modes)


def collect_plugin_test_cases(root_dir: Path) -> List[Tuple[str, str, str]]:
    """Identify plugin test cases by scanning for snapshot directories.

    A plugin test case exists if a 'snapshots' directory is found
    under `root_dir/scenario/mode/`, and this 'snapshots' directory
    contains subdirectories corresponding to plugin names.

    Parameters
    ----------
    root_dir : Path
        The root directory to scan.

    Returns
    -------
    List[Tuple[str, str, str]]
        A list of (scenario_name, mode_name, plugin_name) tuples.
    """
    cases: List[Tuple[str, str, str]] = []
    for scenario, mode in collect_all_modes(root_dir):
        snapshots_dir: Path = root_dir / scenario / mode / "snapshots"
        if snapshots_dir.exists() and snapshots_dir.is_dir():
            for plugin_dir in snapshots_dir.iterdir():
                # Check if it's a directory and not a hidden/special one.
                if plugin_dir.is_dir() and not plugin_dir.name.startswith((".", "__")):
                    cases.append((scenario, mode, plugin_dir.name))
    return cases

# Prepare lists of test cases and corresponding IDs for pytest parametrization.
# These are generated once when the module is loaded.
_SCENARIO_MODE_CASES: List[Tuple[str, str]] = collect_all_modes(_TESTS_ROOT)
_SCENARIO_MODE_IDS: List[str] = [f"{s}-{m}" for s, m in _SCENARIO_MODE_CASES]

_CASES: List[Tuple[str, str, str]] = collect_plugin_test_cases(_TESTS_ROOT)
_PLUGIN_IDS: List[str] = [f"{s}-{m}-{p}" for s, m, p in _CASES]

# -----------------------------------------------------------------------------
# Model execution helper
# -----------------------------------------------------------------------------

def _run_pyh2a(
        scenario: str,
        mode: str,
        snapshot_dir: Optional[str] = None
        ) -> Any:
    """Execute the pyH2A model for a given scenario and mode.

    Constructs paths to the model's markdown file and results directory.
    Optionally, a snapshot directory can be specified for outputting
    intermediate data snapshots. Ensures necessary directories exist.

    Parameters
    ----------
    scenario : str
        The name of the scenario (corresponds to a directory).
    mode : str
        The name of the mode (corresponds to a subdirectory within the scenario).
    snapshot_dir : Optional[str], default None
        Path to the directory where snapshots should be written.
        If None, snapshots are not generated by this call.

    Returns
    -------
    Any
        The results object returned by the `pyH2A` function.

    Raises
    ------
    FileNotFoundError
        If the markdown model file for the specified scenario/mode does not exist.
    """
    mode_path: Path = _TESTS_ROOT / scenario / mode
    # Standard naming convention for markdown files: {scenario_lowercase}-{mode}.md
    md_file: Path = mode_path / f"{scenario.lower()}-{mode}.md"
    results_dir: Path = mode_path / "Results"

    if not md_file.exists():
        raise FileNotFoundError(f"Model file missing: {md_file}. Expected at this location for test purposes.")

    # Ensure output directories exist.
    results_dir.mkdir(parents=True, exist_ok=True)
    if snapshot_dir:
        Path(snapshot_dir).mkdir(parents=True, exist_ok=True)

    return pyH2A(
        input_file=str(md_file),
        output_directory=str(results_dir),
        snapshot_directory=snapshot_dir
    )

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------

@pytest.mark.parametrize(
    "scenario,mode",
    _SCENARIO_MODE_CASES,
    ids=_SCENARIO_MODE_IDS
)
def test_template(
        scenario: str,
        mode: str,
        request: pytest.FixtureRequest
        ) -> None:
    """Validate or regenerate markdown input templates for each scenario/mode.

    If the `--update-templates` command-line option is active, this test
    regenerates the template file (`{scenario}-{mode}_template.md`) based
    on the main input file (`{scenario}-{mode}.md`).
    Otherwise, it generates a temporary template and compares it against the
    existing one, failing if they differ.

    This test is skipped if the `--update-snapshots` option is active,
    as snapshot updates often imply model changes that would affect templates.

    Parameters
    ----------
    scenario : str
        The name of the scenario being tested.
    mode : str
        The name of the mode within the scenario being tested.
    request : pytest.FixtureRequest
        Pytest request object, used to access command-line options.
    """
    if request.config.getoption("--update-snapshots"):
        pytest.skip("Skipping template test because --update-snapshots is active.")

    update_templates_option: bool = request.config.getoption("--update-templates")
    mode_path: Path = _TESTS_ROOT / scenario / mode
    md_file: Path = mode_path / f"{scenario.lower()}-{mode}.md"
    template_file: Path = mode_path / f"{scenario.lower()}-{mode}_template.md"
    # Temporary file for comparison to avoid overwriting the actual template during a non-update run.
    tmp_template_file: Path = mode_path / f".tmp_{scenario.lower()}-{mode}_template.md"

    if update_templates_option:
        Generate_Template_Input_File(str(md_file), str(template_file))
        # No assertion needed here, the action is the update itself.
    else:
        Generate_Template_Input_File(str(md_file), str(tmp_template_file))
        try:
            assert template_file.exists(), f"Template file missing: {template_file}. Run with --update-templates to generate."
            with template_file.open("r") as actual_f, tmp_template_file.open("r") as expected_f:
                if actual_f.read() != expected_f.read():
                    pytest.fail(
                        f"Template mismatch for {scenario}/{mode}. "
                        f"Run pytest with --update-templates to regenerate."
                    )
        finally:
            # Clean up the temporary file.
            if tmp_template_file.exists():
                tmp_template_file.unlink()


@pytest.mark.parametrize(
    "scenario,mode",
    _SCENARIO_MODE_CASES,
    ids=_SCENARIO_MODE_IDS
)
def test_scenario_mode_cost(
        scenario: str,
        mode: str,
        request: pytest.FixtureRequest
        ) -> None:
    """Verify the calculated H₂ cost against expected values for each scenario/mode.

    Runs the pyH2A model for the given scenario and mode.
    If `--update-snapshots` is active, it first runs pyH2A to regenerate
    snapshots, then runs it again to get the results for comparison.
    Otherwise, it runs pyH2A once.
    The calculated H₂ cost is then compared against a predefined expected
    value loaded from `expected_h2_costs.json`.

    Skips if `--update-templates` is active or if expected cost data
    could not be loaded.

    Parameters
    ----------
    scenario : str
        The name of the scenario being tested.
    mode : str
        The name of the mode within the scenario being tested.
    request : pytest.FixtureRequest
        Pytest request object, used to access command-line options.
    """
    if request.config.getoption("--update-templates"):
        pytest.skip("Skipping cost test because --update-templates is active.")

    update_snapshots_option: bool = request.config.getoption("--update-snapshots")
    mode_path: Path = _TESTS_ROOT / scenario / mode

    if update_snapshots_option:
        snapshots_dir: Path = mode_path / "snapshots"
        # Run once to update/generate snapshots.
        _run_pyh2a(scenario, mode, snapshot_dir=str(snapshots_dir))
        # Run again without snapshot writing to get clean results for assertion.
        results: Any = _run_pyh2a(scenario, mode)
    else:
        results: Any = _run_pyh2a(scenario, mode)

    if not EXPECTED_COSTS_LOADED:
        pytest.skip("Expected H₂ cost data not loaded. Cannot perform cost assertion.")

    expected_cost: Any = EXPECTED_H2_COSTS.get((scenario, mode))
    if expected_cost is None:
        pytest.fail(
            f"Expected H₂ cost missing for {scenario}/{mode} in "
            f"{EXPECTED_H2_COSTS_FILE}. Please add it."
        )

    actual_cost: Any = results.base_case.h2_cost
    assert actual_cost == expected_cost, (
        f"H₂ cost mismatch for {scenario}/{mode}: "
        f"Expected {expected_cost}, got {actual_cost}. "
        f"If this is intended, update {EXPECTED_H2_COSTS_FILE} and/or snapshots."
    )


@pytest.mark.parametrize(
    "scenario,mode,plugin_name",
    _CASES, # Uses plugin-specific test cases
    ids=_PLUGIN_IDS
)
def test_scenario_and_plugin(
        scenario: str,
        mode: str,
        plugin_name: str,
        request: pytest.FixtureRequest
        ) -> None:
    """Verify plugin-specific data insertions using snapshot files.

    For each plugin that has snapshot data for a given scenario/mode,
    this test uses `validate_dcf_insertions` (from `test_utils`)
    to compare the plugin's behavior against its stored snapshots.

    Skips if either `--update-snapshots` or `--update-templates`
    command-line options are active, as these imply changes that
    would invalidate current snapshots for comparison.

    Parameters
    ----------
    scenario : str
        The name of the scenario.
    mode : str
        The name of the mode within the scenario.
    plugin_name : str
        The name of the plugin whose snapshots are being validated.
    request : pytest.FixtureRequest
        Pytest request object, used to access command-line options.
    """
    if (
        request.config.getoption("--update-snapshots") or
        request.config.getoption("--update-templates")
    ):
        pytest.skip(
            "Skipping plugin snapshot validation because "
            "--update-snapshots or --update-templates is active."
        )

    plugin_class: Optional[Type[Any]] = PLUGINS.get(plugin_name)
    if plugin_class is None:
        pytest.fail(f"Plugin class for '{plugin_name}' not found in PLUGINS mapping.")

    snapshots_dir_for_plugin: Path = (
        _TESTS_ROOT / scenario / mode / "snapshots" / plugin_name
    )
    if not snapshots_dir_for_plugin.exists() or not snapshots_dir_for_plugin.is_dir():
        # This should ideally not happen if collect_plugin_test_cases works correctly.
        pytest.fail(
            f"Snapshot directory missing for plugin '{plugin_name}' "
            f"in scenario '{scenario}', mode '{mode}'. "
            f"Expected at: {snapshots_dir_for_plugin}"
        )

    # The actual validation logic is delegated to this utility function.
    validate_dcf_insertions(plugin_class, snapshots_dir_for_plugin, scenario)