Pre-commit Hooks
================

The project uses `pre-commit <https://pre-commit.com>`_ to enforce code
quality on every ``git commit``.  The configuration is in
``.pre-commit-config.yaml``.

Setup
-----

.. code-block:: bash

   pip install pre-commit
   pre-commit install     # installs hooks into .git/hooks/pre-commit

After installation, every ``git commit`` automatically runs all hooks.
A commit is blocked if any hook fails.

Running manually
----------------

Check all files right now (without committing):

.. code-block:: bash

   pre-commit run --all-files

Run a single hook:

.. code-block:: bash

   pre-commit run black --all-files
   pre-commit run flake8 --all-files

Hook reference
--------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Hook
     - Purpose
   * - **black**
     - Auto-formats Python code to a consistent style (line-length 100).  No manual formatting required.
   * - **isort**
     - Sorts and groups import statements alphabetically.
   * - **flake8** + extensions
     - Lints for PEP 8 violations, bugbear patterns, and redundant comprehensions.
   * - **mypy**
     - Static type checking.  All public functions must have type annotations.
   * - **bandit**
     - Security linting — flags common Python security issues (SQL injection patterns, hardcoded secrets, etc.).
   * - **pydocstyle**
     - Enforces NumPy docstring convention on all public functions and classes.
   * - **pyupgrade**
     - Automatically modernises syntax to Python 3.10+ style.
   * - **debug-statements**
     - Blocks commits that contain leftover ``print()``, ``pdb``, or ``breakpoint()`` calls.
   * - **trailing-whitespace**
     - Removes trailing spaces and ensures files end with a newline.
   * - **check-merge-conflict**
     - Blocks commits containing unresolved ``<<<<<<`` merge markers.
   * - **detect-private-key**
     - Blocks commits that appear to contain private keys or credentials.

Skipping a hook (emergency only)
---------------------------------

.. code-block:: bash

   # Skip all hooks for one commit
   git commit --no-verify -m "hotfix: ..."

   # Skip a specific hook
   SKIP=mypy git commit -m "wip: ..."

.. warning::
   Use ``--no-verify`` sparingly.  Code that bypasses hooks should be
   cleaned up before merging to main.
