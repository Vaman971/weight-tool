Documentation Workflow
======================

The documentation is built with Sphinx directly from the repository.
Once the virtual environment is active, the core Sphinx commands are the
same on Windows, Linux, and macOS. Only environment activation and the
shortcut wrappers differ by platform.

Environment activation
----------------------

.. list-table::
   :header-rows: 1
   :widths: 18 82

   * - Platform
     - Command
   * - Windows
     - ``.\.venv\Scripts\activate``
   * - Linux / macOS
     - ``source .venv/bin/activate``

If you prefer not to activate the virtual environment, use the explicit
interpreter path instead:

.. code-block:: bash

   # Windows
   .\.venv\Scripts\python -m pip install -e ".[docs]"

   # Linux / macOS
   ./.venv/bin/python -m pip install -e ".[docs]"

Canonical Sphinx commands
-------------------------

After activation, use these commands from the repository root on any OS:

.. code-block:: bash

   python -m sphinx -M clean docs/source docs/build
   python -m sphinx -M html docs/source docs/build
   python -m sphinx -M dirhtml docs/source docs/build
   python -m sphinx -M linkcheck docs/source docs/build
   python -m sphinx -M doctest docs/source docs/build

Live preview
------------

.. code-block:: bash

   python -m sphinx_autobuild docs/source docs/build/html

Repository shortcuts
--------------------

Shortcut wrappers are provided for platform-specific convenience:

.. code-block:: bash

   # Linux / macOS, from docs/
   make html
   make dirhtml
   make linkcheck
   make clean

   # Windows, from docs/
   .\make.bat html
   .\make.bat dirhtml
   .\make.bat linkcheck
   .\make.bat clean

The Windows batch wrapper prefers ``..\.venv\Scripts\python.exe`` when
that interpreter exists, so it works even without activating the venv.
The ``Makefile`` similarly prefers ``../.venv/bin/python`` on
Linux/macOS when it is available.

Restricted-network builds
-------------------------

If the build environment cannot reach the external intersphinx targets,
disable inventory lookups for the HTML build:

.. code-block:: powershell

   $env:SPHINX_OFFLINE = "1"
   python -m sphinx -M html docs/source docs/build
   Remove-Item Env:SPHINX_OFFLINE

``linkcheck`` still requires outbound network access because it validates
external URLs directly.

Output locations
----------------

Generated files are written to ``docs/build``:

* ``docs/build/html`` for the standard HTML site
* ``docs/build/dirhtml`` for directory-style HTML
* ``docs/build/linkcheck`` for link validation reports

Recommended review sequence
---------------------------

.. code-block:: bash

   python -m sphinx -M clean docs/source docs/build
   python -m sphinx -M html docs/source docs/build
   python -m sphinx -M linkcheck docs/source docs/build

If the HTML build is clean and ``linkcheck`` passes, the documentation is
ready for review or publishing.
