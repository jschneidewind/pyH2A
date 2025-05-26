import pytest
import os
from pathlib import Path
from pyH2A.run_pyH2A import pyH2A

def pytest_addoption(parser):
    """Add custom command-line options to pytest.

    Parameters
    ----------
    parser : pytest.Parser
        The pytest command-line argument parser.
    """
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
        help="Update mode input templates."
    )

@pytest.fixture
def run_pyh2a(request, tmp_path):
    """Pytest fixture to run pyH2A and manage test snapshots.

    This fixture provides a callable to execute pyH2A. It first runs
    pyH2A without writing snapshots to verify correctness. If the
    `--update-snapshots` command-line option is specified, it will
    then (re)generate snapshot files.

    Parameters
    ----------
    request : pytest.FixtureRequest
        The request object for the fixture.
    tmp_path : pathlib.Path
        A temporary directory path unique to each test function,
        provided by pytest.

    Yields
    ------
    function
        An inner function `_inner` that executes pyH2A.
    """
    params = {}

    def _inner(md_path: str, outdir: str, snapshot_dir: str = None):
        """Executes pyH2A and handles snapshot generation.

        Parameters
        ----------
        md_path : str
            Path to the pyH2A markdown input file.
        outdir : str
            Path to the output directory for pyH2A results.
        snapshot_dir : str, optional
            Path to the directory where snapshots are stored or
            should be generated. Defaults to None, in which case
            snapshot generation is skipped unless `--update-snapshots`
            is active.

        Returns
        -------
        object
            The result returned by the `pyH2A` function.
        """
        # Run pyH2A initially without writing snapshots to check correctness.
        result = pyH2A(md_path, outdir, snapshot_directory=None)

        # Store parameters for potential use in teardown.
        params['call'] = (md_path, outdir, snapshot_dir)

        # Check if snapshots should be (re)generated.
        if request.config.getoption("--update-snapshots") and snapshot_dir:
            # If no snapshots exist or if explicitly updating, call pyH2A with snapshot_dir.
            # This handles the case where snapshots might be missing and need initial creation.
            if not Path(snapshot_dir).exists() or not any(Path(snapshot_dir).iterdir()):
                print(f"[INFO] No snapshots found or directory empty for {snapshot_dir}, generating...")
                pyH2A(md_path, outdir, snapshot_directory=snapshot_dir)
            # If snapshots exist and we are updating, they will be handled by the teardown logic.

        return result

    def _teardown():
        """Finalizer to re-generate snapshots if requested.

        This function is called after each test that uses the `run_pyh2a`
        fixture finishes. If the `--update-snapshots` option is active,
        it re-runs pyH2A to ensure snapshots are up-to-date.
        """
        if request.config.getoption("--update-snapshots"):
            md, out, snap = params.get('call', (None, None, None))
            if md and out and snap: # Ensure all necessary parameters were captured
                print(f"[INFO] Re-generating snapshots for {snap} during teardown.")
                pyH2A(md, out, snapshot_directory=snap)

    request.addfinalizer(_teardown)
    return _inner