import pytest
from pathlib import Path
import pyH2A.Plugins as Plugins
from pyH2A.run_pyH2A import pyH2A
from tests.Utilities.test_utils import validate_dcf_insertions

PLUGINS = {name: getattr(Plugins, name) for name in Plugins.__all__}

EXPECTED_H2_COSTS = {
    ("PVE", "base"): 4.194302976489678,
    ("PVE", "opt"): 30.407326088821613,
    ("PEC", "base"): 139.41887561917213,
    ("PEC", "opt"): 185.13183678616176,
    ("PEC", "no_conc"): 15.826371459378658,
    ("Photocatalytic", "base"): 185.44329282256822,
    ("Photocatalytic", "opt"): 1.0546304750173923,
}

def collect_plugin_test_cases():
    cases = []
    root = Path("tests")
    
    for scenario_path in root.iterdir():
        if not scenario_path.is_dir():
            continue
        
        if scenario_path.name == "__pycache__":
            continue

        print(f"Found scenario directory: {scenario_path}")
        
        for mode_path in scenario_path.iterdir():
            if not mode_path.is_dir():
                continue

            if mode_path.name == "__pycache__":
                continue

            print(f"Found mode directory: {mode_path}")
            
            snapshots_dir = mode_path / "snapshots/"
            
            if not snapshots_dir.exists():
                print(f"Creating missing snapshots directory: {snapshots_dir}")
                snapshots_dir.mkdir(parents=True, exist_ok=True)

            # Step 2: Run pyH2A to create the snapshot structure
            md_file = mode_path / f"{scenario_path.name.lower()}-{mode_path.name}.md"
            results_dir = mode_path / "Results"
            if md_file.exists():
                pyH2A(str(md_file), str(results_dir), snapshot_directory=str(snapshots_dir))
                print(f"Snapshot structure created for {scenario_path}/{mode_path}.")
                
            if snapshots_dir.exists():
                print(f"Found snapshots directory: {snapshots_dir}")
                for plugin_dir in snapshots_dir.iterdir():
                    if plugin_dir.is_dir():
                        print(f"Adding test case for plugin: {plugin_dir.name}")
                        cases.append((scenario_path.name, mode_path.name, plugin_dir.name))

    print(f"Collected test cases: {cases}")
    return cases

@pytest.mark.parametrize("scenario,mode,plugin_name", collect_plugin_test_cases())
def test_plugin_insertion(scenario, mode, plugin_name, request):
    update_snapshots = request.config.getoption("--update-snapshots")

    plugin_cls = PLUGINS.get(plugin_name)

    md_file = Path(f"tests/{scenario}/{mode}/{scenario.lower()}-{mode}.md")
    results_dir = Path(f"tests/{scenario}/{mode}/Results")
    snapshots_dir = Path(f"tests/{scenario}/{mode}/snapshots")
    plugin_snapshot_dir = snapshots_dir / plugin_name

    if not md_file.exists():
        pytest.skip(f"Missing model file {md_file}")

    expected_key = (scenario, mode)
    expected_h2_cost = EXPECTED_H2_COSTS.get(expected_key)
    if expected_h2_cost is None:
        pytest.skip(f"No expected h2_cost configured for {scenario}/{mode}")

    results_dir.mkdir(parents=True, exist_ok=True)
    results = pyH2A(str(md_file), str(results_dir))


    assert abs(results.base_case.h2_cost - expected_h2_cost) < 1e-6, (
        f"[{scenario}/{mode}] Expected {expected_h2_cost}, got {results.base_case.h2_cost}"
    )
    
    if (not plugin_snapshot_dir.exists()) and update_snapshots:
        print(f"[INFO] No snapshots for {scenario}/{mode}, regenerating...")
        pyH2A(str(md_file), str(results_dir), snapshot_directory=str(snapshots_dir))
        
    if not plugin_snapshot_dir.exists():
        pytest.skip(f"Snapshot for plugin {plugin_name} missing after regeneration attempt.")

    if plugin_cls is None:
        pytest.skip(f"Plugin {plugin_name} not found in pyH2A.Plugins.__all__.")
        
    validate_dcf_insertions(plugin_cls, plugin_snapshot_dir, scenario)
