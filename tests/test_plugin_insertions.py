import json
import threading
import pytest
from pathlib import Path
import filecmp
import pyH2A.Plugins as Plugins
from pyH2A.run_pyH2A import pyH2A
from pyH2A.Utilities.plugin_input_output_processing import Generate_Template_Input_File
from tests.Utilities.test_utils import validate_dcf_insertions

EXPECTED_H2_COSTS_FILE = Path("tests/expected_h2_costs.json")
EXPECTED_H2_COSTS = {}
EXPECTED_COSTS_LOADED = False
if EXPECTED_H2_COSTS_FILE.exists():
    try:
        with open(EXPECTED_H2_COSTS_FILE, "r") as f:
            loaded = json.load(f)
        EXPECTED_H2_COSTS = {
            (scenario, mode): cost
            for scenario, modes in loaded.items()
            for mode, cost in modes.items()
        }
        EXPECTED_COSTS_LOADED = True
    except:
        pass

PLUGINS = {name: getattr(Plugins, name) for name in Plugins.__all__}
_run_cache = {}
_run_lock = threading.Lock()
_TESTS_ROOT = Path("tests")

def pytest_addoption(parser):
    parser.addoption("--update-snapshots", action="store_true", default=False, help="Regenerate snapshots")
    parser.addoption("--update-templates", action="store_true", default=False, help="Regenerate templates")

def collect_plugin_test_cases(root_dir: Path):
    cases = []
    for scenario_path in root_dir.iterdir():
        if not scenario_path.is_dir() or scenario_path.name.startswith((".", "__")):
            continue
        for mode_path in scenario_path.iterdir():
            if not mode_path.is_dir() or mode_path.name.startswith((".", "__")):
                continue
            scenario, mode = scenario_path.name, mode_path.name
            snapshots_dir = mode_path / "snapshots"
            if snapshots_dir.exists():
                for plugin_dir in snapshots_dir.iterdir():
                    if plugin_dir.is_dir() and not plugin_dir.name.startswith((".", "__")):
                        cases.append((scenario, mode, plugin_dir.name))
    return cases

_CASES = collect_plugin_test_cases(_TESTS_ROOT)
_PLUGIN_IDS = [f"{s}-{m}-{p}" for s, m, p in _CASES]
_SCENARIO_MODE_CASES = sorted({(s, m) for s, m, _ in _CASES})
_SCENARIO_MODE_IDS = [f"{s}-{m}" for s, m in _SCENARIO_MODE_CASES]

def _run_pyh2a(scenario, mode, snapshot_dir=None):
    mode_path = _TESTS_ROOT / scenario / mode
    md_file = mode_path / f"{scenario.lower()}-{mode}.md"
    results_dir = mode_path / "Results"
    if not md_file.exists():
        raise FileNotFoundError(f"Model file missing: {md_file}")
    results_dir.mkdir(parents=True, exist_ok=True)
    if snapshot_dir:
        Path(snapshot_dir).mkdir(parents=True, exist_ok=True)
    return pyH2A(str(md_file), str(results_dir), snapshot_directory=snapshot_dir)

@pytest.mark.parametrize("scenario,mode", _SCENARIO_MODE_CASES, ids=_SCENARIO_MODE_IDS)
def test_template(scenario, mode, request):
    update_templates = request.config.getoption("--update-templates")
    mode_path = _TESTS_ROOT / scenario / mode
    md_file = mode_path / f"{scenario.lower()}-{mode}.md"
    template_file = mode_path / f"{scenario.lower()}-{mode}_template.md"
    tmp_template = mode_path / f".tmp_{scenario.lower()}-{mode}_template.md"

    if update_templates:
        Generate_Template_Input_File(str(md_file), str(template_file))
    else:
        Generate_Template_Input_File(str(md_file), str(tmp_template))
        try:
            with open(template_file, "r") as f1, open(tmp_template, "r") as f2:
                if f1.read() != f2.read():
                    pytest.fail(f"Template mismatch for {scenario}/{mode}; run with --update-templates")
        finally:
            if tmp_template.exists():
                tmp_template.unlink()

@pytest.mark.parametrize("scenario,mode", _SCENARIO_MODE_CASES, ids=_SCENARIO_MODE_IDS)
def test_scenario_mode_cost(scenario, mode, request):
    update_snapshots = request.config.getoption("--update-snapshots")
    mode_path = _TESTS_ROOT / scenario / mode
    results = _run_pyh2a(scenario, mode)

    if not EXPECTED_COSTS_LOADED:
        pytest.skip("Expected H₂ cost data not loaded.")
    expected = EXPECTED_H2_COSTS.get((scenario, mode))
    if expected is None:
        pytest.fail(f"Expected H₂ cost missing for {scenario}/{mode}")
    calculated = results.base_case.h2_cost
    assert calculated == expected, f"H₂ cost mismatch for {scenario}/{mode}: expected {expected}, got {calculated}"

    if update_snapshots:
        snapshots_dir = mode_path / "snapshots"
        _run_pyh2a(scenario, mode, snapshot_dir=str(snapshots_dir))

@pytest.mark.parametrize("scenario,mode,plugin_name", _CASES, ids=_PLUGIN_IDS)
def test_scenario_and_plugin(scenario, mode, plugin_name, request):
    if request.config.getoption("--update-snapshots"):
        pytest.skip("--update-snapshots active")
    plugin_cls = PLUGINS.get(plugin_name)
    if plugin_cls is None:
        pytest.fail(f"Plugin '{plugin_name}' not found")
    snapshots_dir = _TESTS_ROOT / scenario / mode / "snapshots" / plugin_name
    if not snapshots_dir.exists():
        pytest.fail(f"Missing snapshots for {plugin_name} in {scenario}/{mode}")
    validate_dcf_insertions(plugin_cls, snapshots_dir, scenario)
