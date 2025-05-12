import pytest
import os
from pathlib import Path
from pyH2A.run_pyH2A import pyH2A

def pytest_addoption(parser):
    parser.addoption(
        "--update-snapshots",
        action="store_true",
        default=False,
        help="After tests pass, regenerate snapshot files."
    )
    parser.addoption(
        "--update-templates", 
        action="store_true", 
        default=False, 
        help="Update mode input templates"
    )

@pytest.fixture
def run_pyh2a(request, tmp_path):
    params = {}

    def _inner(md_path: str, outdir: str, snapshot_dir: str = None):
        # 1) Run pyH2A without writing snapshots to check the correctness first.
        result = pyH2A(md_path, outdir, snapshot_directory=None)
        
        # Store parameters for teardown (if necessary)
        params['call'] = (md_path, outdir, snapshot_dir)
        
        # Check if we should regenerate snapshots
        if request.config.getoption("--update-snapshots") and snapshot_dir:
            # If no snapshots exist or if we're updating them, call pyH2A with snapshot_dir
            if not snapshot_dir or not any(Path(snapshot_dir).iterdir()):
                print(f"[INFO] No snapshots found for {snapshot_dir}, generating...")
                pyH2A(md_path, outdir, snapshot_directory=snapshot_dir)
        
        return result

    def _teardown():
        # On teardown, if snapshots need to be updated, we regenerate them
        if request.config.getoption("--update-snapshots"):
            md, out, snap = params.get('call', (None, None, None))
            if snap:
                print(f"[INFO] Re-generating snapshots for {snap}")
                pyH2A(md, out, snapshot_directory=snap)

    # Ensure we call _teardown at the end of each test session
    request.addfinalizer(_teardown)
    return _inner
