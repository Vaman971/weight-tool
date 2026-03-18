Data Flow
=========

End-to-end pipeline
-------------------

.. code-block:: text

   Excel workbooks / CSV bundles / JSON / SQLite
        |
        v
   src.loaders
        |- resolve input by registered component stem
        |- normalize into (DataFrame, metadata)
        `- expose load_<component>() callables
        |
        v
   COMPONENT_REGISTRY
        |- loader
        |- builder
        |- file
        `- meta_keys
        |
        v
   build_structure() in main.py
        |- df, meta = loader(component_input)
        |- kwargs = {key: meta[key] for key in meta_keys}
        `- wf = builder(df, **kwargs)
        |
        v
   BaseComponent.build()
        |- compute area / volume / mass, or
        `- read stored mass for keel-beam primitives
        |
        v
   WeightFunction
        |- total_mass_g
        |- total_mass_kg
        |- centre_of_gravity
        `- summary_dataframe
        |
        v
   validation.py
        |- reconcile(weight_functions, targets)
        `- plot_components(weight_functions)

Component input normalization
-----------------------------

The loader package keeps format-specific parsing out of the component
classes. Each loader returns the same shape regardless of where the data
came from.

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Input type
     - Normalization rule
   * - Excel workbook
     - Read a sheet, locate the header row, rename columns, extract metadata, coerce numerics.
   * - CSV bundle
     - Read ``metadata.json`` plus ``primitives.csv`` from the component directory.
   * - JSON file
     - Read a single payload with ``metadata`` and ``primitives`` keys.
   * - SQLite file
     - Read ``metadata`` and ``primitives`` tables.

Coordinate system
-----------------

All coordinates are in the aircraft axis system in millimetres.

.. list-table::
   :header-rows: 1
   :widths: 10 90

   * - Axis
     - Direction
   * - X
     - Longitudinal, positive forward.
   * - Y
     - Lateral, positive starboard.
   * - Z
     - Vertical, positive up.

Symmetry handling
-----------------

.. list-table::
   :header-rows: 1
   :widths: 28 15 57

   * - Component type
     - SYM flag
     - Effect
   * - ``GenericArealSurface``
     - metadata only
     - Stored on the ``WeightFunction`` but not applied to mass.
   * - ``GenericVolumetricBeam``
     - metadata only
     - Stored on the ``WeightFunction`` but not applied to mass.
   * - ``GenericStoredMassComponent``
     - active
     - Applies ``symmetry_factor = 2.0`` for half-model stored-mass data.

Mass calculation formulae
-------------------------

**Areal density surfaces**

.. math::

   m = A_{\text{mm}^2} \times 10^{-6} \times \rho_{\text{areal}}

**Volumetric quad components**

.. math::

   A = \text{quad\_area}(P_1, P_2, P_3, P_4)

.. math::

   V = A \times |t|

.. math::

   m = V \times 10^{-3} \times \rho

**Stored mass**

.. math::

   m_{\text{effective}} = m_{\text{stored}} \times f_{\text{sym}}
