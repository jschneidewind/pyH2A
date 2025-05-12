import pytest
from pathlib import Path
from pyH2A.run_pyH2A import pyH2A
import json
import logging


logging.disable(logging.CRITICAL)

# load EXPECTED_H2_COSTS same as before
with open("tests/expected_h2_costs.json") as f:
    loaded = json.load(f)
EXPECTED_H2_COSTS = {
    (method, scenario): cost 
    for method, scenarios in loaded.items() 
    for scenario, cost in scenarios.items()
}

# helper to collect just scenarios and modes
def collect_mode_test_cases():
    root = Path("tests")
    for scenario_path in root.iterdir():
        if not scenario_path.is_dir() or scenario_path.name == "__pycache__":
            continue
        for mode_path in scenario_path.iterdir():
            if not mode_path.is_dir() or mode_path.name == "__pycache__":
                continue
            print(f"Found scenario: {scenario_path.name}, mode: {mode_path.name}")
            yield scenario_path.name, mode_path.name

@pytest.mark.parametrize("scenario,mode", collect_mode_test_cases())
def test_mode_run(scenario, mode, request):
    update_snapshots = request.config.getoption("--update-snapshots")

    md_file = Path(f"tests/{scenario}/{mode}/{scenario.lower()}-{mode}.md")
    results_dir = Path(f"tests/{scenario}/{mode}/Results")
    snapshots_dir = Path(f"tests/{scenario}/{mode}/snapshots")

    if not md_file.exists():
        pytest.skip(f"No model file: {md_file}")

    results_dir.mkdir(parents=True, exist_ok=True)
    results = pyH2A(str(md_file), str(results_dir))

    print("results.base_case.h2_cost", results.base_case.h2_cost)
    expected = EXPECTED_H2_COSTS.get((scenario, mode))
    if expected is None:
        pytest.skip(f"No expected H2 cost for {scenario}/{mode}")
    assert results.base_case.h2_cost == expected

    if update_snapshots:
        pyH2A(str(md_file), str(results_dir), snapshot_directory=str(snapshots_dir))
