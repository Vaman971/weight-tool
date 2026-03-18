Architecture Overview
=====================

The system follows a strict three-layer hierarchy:

.. code-block:: text

   STRUCTURE -> COMPONENTS -> PRIMITIVES

   cargo_floor
     CARGO_FLOOR_PANELS
     C_SECTION_STRUTS
     CARGO_FLOOR_CROSS_BEAMS

   pax_floor
     PAX_FLOOR_PANELS
     I_SECTION_STRUTS
     PAX_FLOOR_RAILS
     PAX_FLOOR_CROSS_BEAMS

   pax_door
     PAX_DOOR_FRAMES
     PAX_DOOR_INTERCOSTALS
     PAX_DOOR_LINTEL
     PAX_DOOR_SILL

   keel_beam
     KEEL_BTM_PANEL
     KEEL_TOP_PANEL
     KEEL_SIDE_PANELS
     KEEL_RIBS
     KEEL_STRINGERS
     KEEL_LOCAL_ATTACHMENTS

Module map
----------

.. code-block:: text

   src/
   |- geometry.py               # Pure maths helpers
   |- weight_functions.py       # Primitive + WeightFunction
   |- validation.py             # Reconciliation + geometry plotting
   |- main.py                   # CLI orchestration
   |- data_loader.py            # Compatibility shim for the loader package
   |- loaders/
   |  |- common.py              # shared parsing helpers + format detection
   |  |- cargo_floor.py         # cargo floor loader definitions
   |  |- pax_floor.py           # pax floor loader definitions
   |  |- pax_door.py            # door loader definitions
   |  |- keel_beam.py           # keel beam loader definitions
   |  |- auxiliary.py           # INPUTS + VALIDATION loaders
   |  `- export.py              # structured sample exporter
   `- components/
      |- base.py                # BaseComponent ABC
      |- registry.py            # COMPONENT_REGISTRY
      |- generic/
      |  |- volumetric_beam.py  # GenericVolumetricBeam
      |  |- areal_surface.py    # GenericArealSurface
      |  `- stored_mass.py      # GenericStoredMassComponent
      |- cargo_floor/
      |- pax_floor/
      |- pax_door/
      `- keel_beam/

Generic implementations
-----------------------

Three shared generic classes now cover the repeated physics:

.. list-table::
   :header-rows: 1
   :widths: 28 22 50

   * - Class
     - Module
     - Used by
   * - ``GenericArealSurface``
     - ``components/generic/areal_surface.py``
     - cargo floor panels, PAX floor panels
   * - ``GenericVolumetricBeam``
     - ``components/generic/volumetric_beam.py``
     - cargo beams, cargo struts, PAX struts, PAX rails, PAX cross beams, PAX door components
   * - ``GenericStoredMassComponent``
     - ``components/generic/stored_mass.py``
     - all keel beam components

The volumetric generic now accepts configurable identifier fields, which
lets the same implementation support ids such as ``Frame + Element``,
``Frame + Strut + Element``, and ``Rail + Element`` without duplicating
the build loop.

Input architecture
------------------

The loader layer normalizes every supported source into the same pair:

.. code-block:: text

   (primitives: pd.DataFrame, metadata: dict[str, float | bool])

Supported source formats:

* Excel workbooks (legacy format, still fully supported)
* Structured CSV bundles
* Structured JSON payloads
* Structured SQLite files

That means the component builders remain format-agnostic. They only see
the normalized DataFrame and metadata produced by ``src/loaders``.

Inheritance hierarchy
---------------------

.. code-block:: text

   BaseComponent
   |- GenericArealSurface
   |  |- CargoFloorPanels
   |  `- PaxFloorPanels
   |- GenericVolumetricBeam
   |  |- CSectionStruct
   |  |- CargoFloorBeams
   |  |- ISectionStruct
   |  |- PaxFloorCrossBeams
   |  |- PaxFloorRails
   |  |- DoorFrames
   |  |- DoorIntercostals
   |  |- DoorLintel
   |  `- DoorSill
   `- GenericStoredMassComponent
      |- KeelBottomPanel
      |- KeelTopPanel
      |- KeelSidePanels
      |- KeelRibs
      |- KeelStringers
      `- KeelLocalAttachments
