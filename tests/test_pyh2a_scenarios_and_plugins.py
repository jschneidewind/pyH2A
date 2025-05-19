"""
Test suite for pyH2A scenarios, modes, and plugin validations.

Includes utilities for collecting test cases, running models,
comparing expected outputs, and managing snapshots/templates.
"""
import json
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type

import pytest
import pyH2A.Plugins as Plugins
from pyH2A.run_pyH2A import pyH2A
from pyH2A.Utilities.plugin_input_output_processing import Generate_Template_Input_File
from tests.test_utils import validate_dcf_insertions

# -----------------------------------------------------------------------------
# Global test data and configuration
# -----------------------------------------------------------------------------
EXPECTED_H2_COSTS_FILE: Path = Path("tests/expected_h2_costs.json")
EXPECTED_H2_COSTS: Dict[Tuple[str, str], Any] = {}
EXPECTED_COSTS_LOADED: bool = False

# Attempt to load expected H₂ cost values from JSON
try:
    if EXPECTED_H2_COSTS_FILE.exists():
        with EXPECTED_H2_COSTS_FILE.open("r") as f:
            loaded: Dict[str, Dict[str, Any]] = json.load(f)
        EXPECTED_H2_COSTS = {
            (scenario, mode): cost
            for scenario, modes in loaded.items()
            for mode, cost in modes.items()
        }
        EXPECTED_COSTS_LOADED = True
except json.JSONDecodeError:
    EXPECTED_COSTS_LOADED = False

# Cache for pyh2a runs and threading lock
_run_cache: Dict[Tuple[str, str], Any] = {}
_run_lock: threading.Lock = threading.Lock()

# Root directory containing tests
_TESTS_ROOT: Path = Path("tests")

# Map of plugin name to plugin class
PLUGINS: Dict[str, Type[Any]] = {name: getattr(Plugins, name) for name in Plugins.__all__}

# -----------------------------------------------------------------------------
# Pytest CLI options
# -----------------------------------------------------------------------------

def pytest_addoption(
        parser: pytest.Parser
        ) -> None:
    """
    Register custom command-line options for updating snapshots and templates.
    """
    parser.addoption(
        "--update-snapshots",
        action="store_true",
        default=False,
        help="Regenerate snapshot files"
    )
    parser.addoption(
        "--update-templates",
        action="store_true",
        default=False,
        help="Regenerate template input files"
    )

# -----------------------------------------------------------------------------
# Test case collection helpers
# -----------------------------------------------------------------------------

def collect_all_modes(
        root_dir: Path
        ) -> List[Tuple[str, str]]:
    """
    Gather all scenario/mode pairs from the given directory.
    """
    modes: List[Tuple[str, str]] = []
    for scenario_path in root_dir.iterdir():
        if not scenario_path.is_dir() or scenario_path.name.startswith((".", "__")):
            continue
        for mode_path in scenario_path.iterdir():
            if not mode_path.is_dir() or mode_path.name.startswith((".", "__")):
                continue
            modes.append((scenario_path.name, mode_path.name))
    return sorted(modes)


def collect_plugin_test_cases(
        root_dir: Path
        ) -> List[Tuple[str, str, str]]:
    """
    Identify plugin test cases by scanning snapshot directories.
    """
    cases: List[Tuple[str, str, str]] = []
    for scenario, mode in collect_all_modes(root_dir):
        snapshots_dir: Path = root_dir / scenario / mode / "snapshots"
        if snapshots_dir.exists():
            for plugin_dir in snapshots_dir.iterdir():
                if plugin_dir.is_dir() and not plugin_dir.name.startswith((".", "__")):
                    cases.append((scenario, mode, plugin_dir.name))
    return cases

# Prepare parameterization lists and IDs
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
    """
    Run pyH2A model for a given scenario/mode, optionally generating snapshots.

    Args:
        scenario: Name of the scenario directory.
        mode: Name of the mode directory.
        snapshot_dir: Directory path for writing snapshots.

    Returns:
        The results object from pyH2A.

    Raises:
        FileNotFoundError: If the markdown model file is missing.
    """
    mode_path: Path = _TESTS_ROOT / scenario / mode
    md_file: Path = mode_path / f"{scenario.lower()}-{mode}.md"
    results_dir: Path = mode_path / "Results"

    if not md_file.exists():
        raise FileNotFoundError(f"Model file missing: {md_file}")

    results_dir.mkdir(parents=True, exist_ok=True)
    if snapshot_dir:
        Path(snapshot_dir).mkdir(parents=True, exist_ok=True)

    return pyH2A(
        str(md_file),
        str(results_dir),
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
    """
    Validate or regenerate markdown templates for each scenario/mode.

    Skips test if --update-snapshots is active.
    """
    if request.config.getoption("--update-snapshots"):
        pytest.skip("--update-snapshots active")

    update_templates: bool = request.config.getoption("--update-templates")
    mode_path: Path = _TESTS_ROOT / scenario / mode
    md_file: Path = mode_path / f"{scenario.lower()}-{mode}.md"
    template_file: Path = mode_path / f"{scenario.lower()}-{mode}_template.md"
    tmp_file: Path = mode_path / f".tmp_{scenario.lower()}-{mode}_template.md"

    if update_templates:
        Generate_Template_Input_File(str(md_file), str(template_file))
    else:
        Generate_Template_Input_File(str(md_file), str(tmp_file))
        try:
            with template_file.open() as a, tmp_file.open() as b:
                if a.read() != b.read():
                    pytest.fail(
                        f"Template mismatch for {scenario}/{mode}; run with --update-templates"
                    )
        finally:
            if tmp_file.exists():
                tmp_file.unlink()


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
    """
    Check H₂ cost for each scenario/mode against expected values.

    Skips if --update-templates is active or no expected data loaded.
    """
    if request.config.getoption("--update-templates"):
        pytest.skip("--update-templates active")

    update_snapshots: bool = request.config.getoption("--update-snapshots")
    mode_path: Path = _TESTS_ROOT / scenario / mode

    if update_snapshots:
        snapshots_dir: Path = mode_path / "snapshots"
        _run_pyh2a(scenario, mode, snapshot_dir=str(snapshots_dir))
        results: Any = _run_pyh2a(scenario, mode)
    else:
        results: Any = _run_pyh2a(scenario, mode)

    if not EXPECTED_COSTS_LOADED:
        pytest.skip("Expected H₂ cost data not loaded.")

    expected: Any = EXPECTED_H2_COSTS.get((scenario, mode))
    if expected is None:
        pytest.fail(f"Expected H₂ cost missing for {scenario}/{mode}")

    actual: Any = results.base_case.h2_cost
    assert actual == expected, (
        f"H₂ cost mismatch for {scenario}/{mode}: expected {expected}, got {actual}"
    )


@pytest.mark.parametrize(
    "scenario,mode,plugin_name",
    _CASES,
    ids=_PLUGIN_IDS
)
def test_scenario_and_plugin(
        scenario: str,
        mode: str,
        plugin_name: str,
        request: pytest.FixtureRequest
        ) -> None:
    """
    Verify plugin-specific snapshot insertions.

    Skips if update flags are active.
    """
    if (
        request.config.getoption("--update-snapshots") or
        request.config.getoption("--update-templates")
    ):
        pytest.skip("--update-snapshots or --update-templates active")

    plugin_cls: Optional[Type[Any]] = PLUGINS.get(plugin_name)
    if plugin_cls is None:
        pytest.fail(f"Plugin '{plugin_name}' not found")

    snapshots_dir: Path = (_TESTS_ROOT / scenario / mode / "snapshots" / plugin_name)
    if not snapshots_dir.exists():
        pytest.fail(f"Missing snapshots for {plugin_name} in {scenario}/{mode}")

    validate_dcf_insertions(plugin_cls, snapshots_dir, scenario)
