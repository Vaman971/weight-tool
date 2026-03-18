Installation
============

Requirements
------------

* Python >= 3.10
* Git

Dependencies are declared in ``pyproject.toml`` and installed automatically.
After the virtual environment is active, the runtime and CLI commands are
the same on Windows, Linux, and macOS. The main OS-specific differences
are activation commands and the optional documentation wrappers.

Core runtime
~~~~~~~~~~~~

.. code-block:: text

   numpy>=1.26
   pandas>=2.2
   openpyxl>=3.1
   matplotlib>=3.8

Developer extras (``[dev]``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   pytest, pytest-cov, black, flake8, isort, mypy, bandit,
   pre-commit, pydocstyle, pyupgrade

Documentation extras (``[docs]``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   sphinx, pydata-sphinx-theme, sphinx-autodoc-typehints,
   sphinx-design, sphinx-copybutton, sphinx-autobuild

Steps
-----

1. **Clone the repository**

   .. code-block:: bash

      git clone https://github.com/airbus-amber/weight-function-calculator.git
      cd weight-function-calculator

2. **Create and activate a virtual environment**

   .. code-block:: bash

      python -m venv .venv

      # Linux / macOS
      source .venv/bin/activate

      # Windows
      .venv\Scripts\activate

3. **Install the package**

   For production use only:

   .. code-block:: bash

      pip install .

   For development (editable install with all dev tools):

   .. code-block:: bash

      pip install -e ".[dev]"

   For documentation work:

   .. code-block:: bash

      pip install -e ".[docs]"

   For full contributor setup:

   .. code-block:: bash

      pip install -e ".[dev,docs]"

4. **Install pre-commit hooks** *(recommended for contributors)*

   .. code-block:: bash

      pre-commit install

   Hooks run automatically on every ``git commit``:
   ``black``, ``isort``, ``flake8``, ``mypy``, ``bandit``,
   ``pydocstyle``, ``pyupgrade``, trailing-whitespace checks,
   and debug-statement detection.

5. **Verify the installation**

   .. code-block:: bash

      pytest

   All tests use synthetic DataFrames -- no Excel files are required
   to run the test suite.

Building the documentation
--------------------------

The canonical Sphinx commands are the same on every OS once the virtual
environment is active:

.. code-block:: bash

   python -m sphinx -M html docs/source docs/build

Shortcut wrappers differ by platform:

.. code-block:: bash

   # Linux / macOS
   cd docs
   make html

   # Windows
   cd docs
   .\make.bat html

The rendered HTML will be at ``docs/build/html/index.html``.
