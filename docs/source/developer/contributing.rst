Contributing
============

Branching strategy
------------------

.. code-block:: text

   main          Production-ready code. Direct pushes blocked.
   develop       Integration branch. PRs merge here first.
   feature/<id>  New features or structures. Branch from develop.
   fix/<id>      Bug fixes. Branch from develop (or main for hotfixes).

Commit message format
---------------------

.. code-block:: text

   <type>(<scope>): <short summary>

   [optional body]

Types: ``feat``, ``fix``, ``refactor``, ``test``, ``docs``, ``chore``.

Examples:

.. code-block:: text

   feat(registry): add door_surround structure
   fix(stored_mass): handle missing X4 column for bar primitives
   test(keel_beam): add synthetic CoG midpoint test for local_attachments
   docs(api): add automodule rst for pax_door components

Code style rules
----------------

* **Line length:** 100 characters (enforced by black).
* **Naming:** ``snake_case`` for functions and variables, ``CamelCase`` for classes.
* **Docstrings:** NumPy style on all public functions, classes, and modules.
* **Type hints:** required on all public function signatures.
* **No dead code:** no commented-out logic, unused variables, or ``print()`` statements.
* **No hardcoded values:** material parameters should come from metadata, not Python constants.

Pull request checklist
----------------------

Before opening a PR, verify:

.. code-block:: text

   [ ] pre-commit run --all-files passes with zero errors
   [ ] pytest passes with zero failures
   [ ] New structures have a test file (test_<structure>.py)
   [ ] Synthetic DataFrames are used by default; real sample inputs are only used for integration tests
   [ ] New public functions have NumPy docstrings
   [ ] COMPONENT_REGISTRY updated if new structure added
   [ ] VALIDATION.xlsx reference created if no CATIA target exists
   [ ] No print() or debug statements in production code

Acceptance criteria
-------------------

All mass calculations must be within **5% relative error** compared to
the benchmark values in ``VALIDATION``.

The reconciliation report ``PassFail`` column must show ``PASS`` for:

* ``Mass (kg)``
* ``Z CoG (mm)``

X and Y CoG may fail when only a half-structure is provided, such as a
``SYM=True`` dataset without mirrored counterparts.
