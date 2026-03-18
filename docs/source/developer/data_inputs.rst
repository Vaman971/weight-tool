Structured Inputs
=================

The loader layer is no longer tied to Excel workbooks only. Each
component loader can now consume the same normalized data from multiple
sources.

Supported formats
-----------------

.. list-table::
   :header-rows: 1
   :widths: 18 82

   * - Format
     - Shape
   * - Excel
     - The original workbook and sheet layout used by the repo data.
   * - CSV bundle
     - ``<COMPONENT>/metadata.json`` plus ``<COMPONENT>/primitives.csv``.
   * - JSON
     - One ``<COMPONENT>.json`` file with ``metadata`` and ``primitives``.
   * - SQLite
     - One ``<COMPONENT>.sqlite`` file with ``metadata`` and ``primitives`` tables.

Bundle conventions
------------------

For a CSV bundle, the CLI resolves component inputs by the registered
component stem. A cargo-floor sample exported from the repo looks like:

.. code-block:: text

   samples/structured_inputs/cargo_floor/
   |- CARGO_FLOOR_PANEL/
   |  |- metadata.json
   |  `- primitives.csv
   |- C_SECTION_STRUCT/
   |  |- metadata.json
   |  `- primitives.csv
   |- CARGO_BEAMS/
   |  |- metadata.json
   |  `- primitives.csv
   |- INPUTS/
   |  |- datums.csv
   |  `- frame_coords.csv
   `- VALIDATION/
      `- targets.csv

The same structure can instead be exported as JSON or SQLite files with
matching stems, for example ``C_SECTION_STRUCT.json`` or
``C_SECTION_STRUCT.sqlite``.

Exporter workflow
-----------------

The repository includes ``src.loaders.export`` so developers can create
structured samples from the current Excel parsing logic instead of
manually transcribing files.

.. code-block:: bash

   # CSV bundles
   python -m src.loaders.export --structure cargo_floor --source-dir ./data --output-dir ./samples/structured_inputs --format csv

   # JSON payloads
   python -m src.loaders.export --structure cargo_floor --source-dir ./data --output-dir ./samples/structured_inputs_json --format json

   # SQLite payloads
   python -m src.loaders.export --structure cargo_floor --source-dir ./data --output-dir ./samples/structured_inputs_sqlite --format sqlite

Running from structured samples
-------------------------------

Once exported, the main CLI can use the structured data without code
changes:

.. code-block:: bash

   python -m src.main --structure cargo_floor --data-dir ./samples/structured_inputs

Committed sample inputs are available for all three structured formats:

* ``samples/structured_inputs/cargo_floor`` for CSV bundles
* ``samples/structured_inputs_json/cargo_floor`` for JSON-only inputs
* ``samples/structured_inputs_sqlite/cargo_floor`` for SQLite inputs

Developer guidance
------------------

When adding a new structure, keep the normalized output contract the
same:

* primitives must still become a ``pd.DataFrame`` with the columns the
  component builder expects
* metadata must still expose the same keys, such as
  ``density_g_per_cm3``, ``areal_density_g_per_m2``, and ``symmetrical``
* validation and auxiliary inputs should follow the same stem-based
  resolution pattern used by the existing registry
