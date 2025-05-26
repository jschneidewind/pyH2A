Development Guide for pyH2A
============================

1. Virtual Environment
----------------------

Set up an isolated Python environment to avoid conflicts and ensure reproducibility:

1. **Create the virtual environment**

   .. code-block:: bash

      python3 -m venv pyH2A_env

2. **Activate the virtual environment**

   - **Linux / macOS**

     .. code-block:: bash

        source pyH2A_env/bin/activate

   - **Windows (PowerShell)**

     .. code-block:: powershell

        pyH2A_env\Scripts\Activate.ps1

3. **Install the package and testing tools**

   .. code-block:: bash

      pip install -e .
      pip install pytest

   > **Tip:** You may also install development dependencies in one step:
   >
   > .. code-block:: bash
   >
   >    pip install -e ".[dev]"

2. Testing
----------

This section describes how to inspect the test directory structure, run the full suite, target individual tests, and update snapshots or templates.

2.1. Test File Structure
************************

Within the `tests/` directory you will find:

.. code-block:: text

   tests/
   ├── conftest.py                  # CLI flags & fixtures
   ├── expected_h2_costs.json       # Reference cost data
   ├── scenario1/
   │   ├── modeA/
   │   │   ├── scenario1-modeA.md
   │   │   ├── scenario1-modeA_template.md
   │   │   ├── Results/             # auto-generated outputs
   │   │   └── snapshots/
   │   │       └── PluginX/         # plugin-specific expected data
   │   └── modeB/
   └── scenario2/
       └── modeA/

2.2. Running the Full Test Suite
********************************

From the project root, simply execute:

.. code-block:: bash

   pytest

By default, pytest will:

- **Discover** all tests under `tests/`
- **Validate** Markdown templates (`test_template`)
- **Compare** hydrogen cost outputs (`test_scenario_mode_cost`)
- **Verify** plugin snapshot insertions (`test_scenario_and_plugin`)

2.3. Running Individual Tests
*****************************

You can pinpoint a single test case via pytest's “node ID” syntax:

- **By mode template** (e.g. `PVE-sensitivity`):

  .. code-block:: bash

     pytest tests/test_pyh2a_scenarios_and_plugins.py::test_template[PVE-sensitivity]

- **By scenario/mode cost** (e.g. `PVE-distance_time`):

  .. code-block:: bash

     pytest tests/test_pyh2a_scenarios_and_plugins.py::test_scenario_mode_cost[PVE-distance_time]

- **By plugin snapshot** (e.g. `ElectrolyzerPlugin`):

  .. code-block:: bash

     pytest tests/test_pyh2a_scenarios_and_plugins.py::test_scenario_and_plugin[PVE-base-ElectrolyzerPlugin]

2.4. Updating Snapshots & Templates
***********************************

Use the custom flags to regenerate expected files:

- **All scenarios & plugins**

  .. code-block:: bash

     pytest --update-snapshots
     pytest --update-templates

  or both at once:

  .. code-block:: bash

     pytest --update-snapshots --update-templates

- **Specific scenario/mode**

  .. code-block:: bash

     pytest tests/test_pyh2a_scenarios_and_plugins.py::test_scenario_mode_cost[PVE-monte_carlo] --update-snapshots
     pytest tests/test_pyh2a_scenarios_and_plugins.py::test_scenario_mode_cost[PEC-base]       --update-templates
     