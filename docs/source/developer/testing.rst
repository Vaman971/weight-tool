Testing Guide
=============

Philosophy
----------

Most tests use synthetic DataFrames so the component and geometry logic
stays fast, isolated, and easy to reason about. Loader and pipeline
integration tests then exercise the real workbook formats and the new
structured input plug-ins.

This split gives the project two useful properties:

* physics tests do not have to change every time an input format evolves
* loader changes can be validated against both the legacy Excel path and
  the normalized CSV, JSON, and SQLite paths

Running the tests
-----------------

.. code-block:: bash

   pytest
   pytest -v
   pytest -x
   pytest --cov=src --cov-report=term-missing

The suite is safe to launch from the repository root or from inside
``tests/`` because the integration tests resolve sample data from the
test file location instead of the current working directory.

Target a single file when you are iterating on one area:

.. code-block:: bash

   pytest tests/test_loader_plugins.py -v
   pytest tests/test_cross_beam.py -v
   pytest tests/test_areal_surface.py -v

Test file map
-------------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - File
     - What it covers
   * - ``test_geometry.py``
     - Core geometry and mass helpers.
   * - ``test_weight_functions.py``
     - ``WeightFunction`` aggregation, caching, and summaries.
   * - ``test_base_component.py``
     - ``BaseComponent`` guards and metadata helpers.
   * - ``test_registry.py``
     - ``COMPONENT_REGISTRY`` structure and callability.
   * - ``test_components.py``
     - Cargo floor components.
   * - ``test_pax_components.py``
     - PAX floor components.
   * - ``test_cross_beam.py``
     - ``GenericVolumetricBeam`` behavior and wrapper DRY checks.
   * - ``test_areal_surface.py``
     - ``GenericArealSurface`` behavior and panel wrapper DRY checks.
   * - ``test_pax_door.py``
     - PAX door components.
   * - ``test_keel_beam.py``
     - Stored-mass generic and keel-beam wrappers.
   * - ``test_data_loader.py``
     - Real workbook loader integration tests.
   * - ``test_loader_plugins.py``
     - Structured CSV, JSON, and SQLite loading plus exported bundle pipeline checks.
   * - ``test_main.py``
     - CLI orchestration helpers.
   * - ``test_validation.py``
     - Reconciliation thresholds and combined CoG logic.

Writing a new test
------------------

Prefer the smallest useful shape:

* one or two synthetic rows for component logic
* a temporary directory for structured loader tests
* a full exported bundle only when you need to verify the end-to-end CLI

That keeps failures local and makes it obvious whether a bug belongs to
geometry, a component wrapper, the loader layer, or the registry.
