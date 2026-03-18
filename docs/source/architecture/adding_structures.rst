Adding a New Structure
======================

The registry-driven architecture still means a new structure can be
added without touching ``main.py``, ``validation.py``, or the shared
math utilities. The difference now is that you should work with the
generic component layer and the categorized loader package rather than
adding more one-off build loops and loader code.

Step 1 - Choose the right generic base
--------------------------------------

Ask how mass is produced for each primitive:

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - Primitive family
     - Recommended base
   * - 4-point element with volumetric density
     - ``GenericVolumetricBeam``
   * - 4-point element with areal density
     - ``GenericArealSurface``
   * - Stored mass with 1 to 6 geometry points
     - ``GenericStoredMassComponent``

Step 2 - Create the component wrappers
--------------------------------------

Create a new component package and keep the structure-specific files as
thin wrappers around the generic implementation whenever possible.

.. code-block:: python

   # src/components/my_structure/panels.py
   from __future__ import annotations

   import pandas as pd

   from ...weight_functions import WeightFunction
   from ..base import ComponentMetadata
   from ..generic.areal_surface import GenericArealSurface

   class MyPanels(GenericArealSurface):
       """Build my-structure panels with the shared areal logic."""

       def __init__(self, name: str, df: pd.DataFrame, metadata: ComponentMetadata) -> None:
           """Initialize the wrapper with panel and element ids."""
           super().__init__(name, df, metadata, identifier_fields=("Panel", "Element"))

   def build_my_panels(df: pd.DataFrame, **kwargs: float | bool) -> WeightFunction:
       """Build the my-structure panel weight function."""
       return MyPanels("MY_STRUCTURE_PANELS", df, kwargs).build()

Step 3 - Add a loader definition
--------------------------------

Add the loader to the relevant module under ``src/loaders/``. In most
cases this is only an ``ExcelComponentSpec`` plus a thin public function
that documents the supported input formats.

.. code-block:: python

   # src/loaders/my_structure.py
   from pathlib import Path

   import pandas as pd

   from .common import (
       _FRAME_COL_MAP,
       ComponentMetadata,
       ExcelComponentSpec,
       load_component_dataset,
   )

   _MY_PANEL_SPEC = ExcelComponentSpec(
       sheet_name="MY_PANEL",
       header_marker="FRAME",
       col_map=_FRAME_COL_MAP,
   )

   def load_my_panel(file_path: Path) -> tuple[pd.DataFrame, ComponentMetadata]:
       """Load my-structure panel data from a supported input source."""
       return load_component_dataset(file_path, _MY_PANEL_SPEC)

That single function will then work for the legacy workbook, structured
CSV bundle, JSON payload, or SQLite file.

Step 4 - Register the structure
-------------------------------

Add the loader and builder to ``src/components/registry.py``:

.. code-block:: python

   from ..loaders.my_structure import load_my_panel
   from .my_structure.panels import build_my_panels

   COMPONENT_REGISTRY["my_structure"] = [
       {
           "name": "MY_STRUCTURE_PANELS",
           "loader": load_my_panel,
           "builder": build_my_panels,
           "file": "MY_PANEL.xlsx",
           "meta_keys": ["density_g_per_cm3", "symmetrical"],
       }
   ]

The registered ``file`` value is still the canonical Excel filename, but
the CLI now resolves by stem as well, so ``MY_PANEL/``,
``MY_PANEL.json``, and ``MY_PANEL.sqlite`` are all valid alternatives.

Step 4.5 - Add or update API docs
---------------------------------

If the structure is intended to be maintained by other developers, add
API reference pages under ``docs/source/api/`` so the wrapper modules
and loaders appear in the generated Sphinx site.

Step 5 - Add tests
------------------

Cover both the wrapper behavior and the loader contract:

* synthetic component tests for mass, CoG, and edge cases
* registry tests
* structured loader tests where useful
* exporter or CLI integration if the structure ships with sample data

Step 6 - Verify the CLI
-----------------------

.. code-block:: bash

   python -m src.main --structure my_structure --data-dir /path/to/inputs

Checklist
---------

.. code-block:: text

   [ ] src/components/my_structure/ created
   [ ] generic wrapper builder(s) added
   [ ] load_my_xxx() added to src/loaders/<structure>.py
   [ ] registry entry added
   [ ] API reference pages added or updated
   [ ] tests added or updated
   [ ] sample/export plan documented
