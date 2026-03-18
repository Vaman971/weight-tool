Configuration
=============

All pipeline configuration is done through two mechanisms:

1. **CLI arguments** — passed to ``src.main`` at runtime.
2. **Component registry** — ``src/components/registry.py``, the single source of truth for which structures and files exist.

CLI arguments
-------------

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Argument
     - Default
     - Description
   * - ``--structure``
     - ``all``
     - Structure key from ``COMPONENT_REGISTRY``, or ``all`` to run every registered structure.
   * - ``--data-dir``
     - ``.``
     - Path to one structure's workbook directory, or a parent directory
       containing per-structure subdirectories.
   * - ``--output-dir``
     - ``./outputs``
     - Directory where reconciliation CSVs and geometry plots are written.  Created automatically if it does not exist.

Tolerance threshold
-------------------

The allowable error for any mass calculation or coordinate placement is
defined in ``src/validation.py``:

.. code-block:: python

   TOLERANCE_PCT = 5.0   # percent — per the spec

Change this constant to tighten or relax the Pass/Fail threshold across
all structures simultaneously.

Material densities
------------------

Densities are read directly from each Excel workbook's header row by the
data loaders.  They are **not** hardcoded in Python.  If the workbook
changes its density value, no code change is needed.

Typical values used across the fleet:

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - Material
     - Value
     - Unit
   * - Aluminium alloy (structural panels)
     - 2.83
     - g/cm³
   * - Carbon fibre floor panels (areal)
     - 3 500 – 4 900
     - g/m²

Logging
-------

The pipeline uses Python's standard ``logging`` module.  Log level is
set in ``src/main.py``:

.. code-block:: python

   logging.basicConfig(level=logging.INFO, ...)

To suppress INFO-level component summaries during scripted use, set the
level to ``WARNING``:

.. code-block:: python

   import logging
   logging.basicConfig(level=logging.WARNING)

   from src.main import build_structure
   wfs = build_structure("cargo_floor", data_dir)
