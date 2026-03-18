Quickstart
==========

Running the full pipeline
-------------------------

Once the virtual environment is active, the CLI command is the same on
Windows, Linux, and macOS. The loader layer now auto-detects supported
inputs by component stem, so the same structure can be run from:

* the original Excel workbooks
* structured CSV bundles
* structured JSON files
* structured SQLite files

.. code-block:: bash

   # Excel workbooks from the bundled sample data
   python -m src.main --structure cargo_floor --data-dir ./data

   # One structure from a flat workbook directory
   python -m src.main --structure cargo_floor --data-dir /path/to/cargo_floor

   # Structured CSV sample bundle exported from the repo data
   python -m src.main --structure cargo_floor --data-dir ./samples/structured_inputs

   # Run every registered structure
   python -m src.main --structure all --data-dir ./data

   # Custom output directory
   python -m src.main --structure pax_door --data-dir ./data --output-dir ./results

Outputs
~~~~~~~

For each structure the pipeline writes to ``--output-dir``:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - File
     - Description
   * - ``<structure>_reconciliation.csv``
     - Mass and coordinate reconciliation report.
   * - ``<structure>_geometry.png``
     - 3-D plot of component geometry and the combined centre of gravity.

Exporting structured inputs
---------------------------

The repository includes an exporter that converts the legacy Excel inputs
into structured CSV, JSON, or SQLite samples for developers.

.. code-block:: bash

   # CSV bundles
   python -m src.loaders.export --structure cargo_floor --source-dir ./data --output-dir ./samples/structured_inputs --format csv

   # JSON payloads
   python -m src.loaders.export --structure cargo_floor --source-dir ./data --output-dir ./samples/structured_inputs_json --format json

   # SQLite payloads
   python -m src.loaders.export --structure cargo_floor --source-dir ./data --output-dir ./samples/structured_inputs_sqlite --format sqlite

Using the API directly
----------------------

.. code-block:: python

   from pathlib import Path

   from src.main import build_structure
   from src.loaders import load_validation_targets
   from src.validation import reconcile

   data_dir = Path("./data/cargo_floor")
   weight_functions = build_structure("cargo_floor", data_dir)

   for wf in weight_functions:
       cog = wf.centre_of_gravity
       print(
           f"{wf.component_name}: {wf.total_mass_kg:.3f} kg | "
           f"CoG = ({cog[0]:.1f}, {cog[1]:.1f}, {cog[2]:.1f}) mm"
       )

   targets = load_validation_targets(data_dir / "VALIDATION.xlsx", "cargo_floor")
   report = reconcile(weight_functions, targets)
   print(report)

Using a single component programmatically
-----------------------------------------

.. code-block:: python

   import pandas as pd

   from src.components.pax_floor.rails import build_pax_floor_rails

   df = pd.DataFrame(
       [
           {
               "Rail": "INBD",
               "Element": "TOP_FLANGE",
               "Mass": 2886.0,
               "X1": 9499.6,
               "Y1": 804.5,
               "Z1": -504.7,
               "X2": 9499.6,
               "Y2": 725.5,
               "Z2": -504.7,
               "X3": 15367.0,
               "Y3": 725.5,
               "Z3": -504.7,
               "X4": 15367.0,
               "Y4": 804.5,
               "Z4": -504.7,
               "Thickness": 2.2,
           }
       ]
   )

   wf = build_pax_floor_rails(df, density_g_per_cm3=2.83, symmetrical=False)
   print(wf.total_mass_kg)
   print(wf.centre_of_gravity)

Querying the registry
---------------------

.. code-block:: python

   from src.components.registry import COMPONENT_REGISTRY

   print(list(COMPONENT_REGISTRY.keys()))

   for component in COMPONENT_REGISTRY["pax_floor"]:
       print(component["name"], "->", component["file"])
