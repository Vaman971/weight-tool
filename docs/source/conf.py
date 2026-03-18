"""Sphinx configuration for the Weight Function Calculator documentation."""

# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Path setup --------------------------------------------------------------
# Allow Sphinx to find the src package when running autodoc.
sys.path.insert(0, os.path.abspath("../.."))

# -- Project information -----------------------------------------------------
project = "Weight Function Calculator"
copyright = "2026, Aman"
author = "Aman"
release = "1.0.0"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",  # pull docstrings automatically
    "sphinx.ext.autosummary",  # generate API tables and summary pages
    "sphinx.ext.napoleon",  # parse NumPy / Google style docstrings
    "sphinx.ext.viewcode",  # add [source] links to every function
    "sphinx.ext.intersphinx",  # link to NumPy / pandas docs
    "sphinx.ext.todo",  # .. todo:: directives
    "sphinx_autodoc_typehints",  # render type hints in signatures
    "sphinx_design",  # cards, grids, and callouts for landing pages
    "sphinx_copybutton",  # copy button for code blocks
]

# Suppress known benign warnings.
suppress_warnings = [
    "autosectionlabel.*",  # duplicate label in different files
    "ref.python",  # unresolved Python refs in intersphinx
]

# Napoleon settings (NumPy docstring style used throughout this project)
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_attr_annotations = True

# autodoc defaults
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "member-order": "bysource",
    "special-members": "__init__",
}
autosummary_generate = True
autosummary_generate_overwrite = True
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"

# In restricted environments, set SPHINX_OFFLINE=1 to skip inventory lookups.
offline_docs = os.environ.get("SPHINX_OFFLINE") == "1"
if offline_docs:
    intersphinx_mapping = {}
else:
    intersphinx_mapping = {
        "python": ("https://docs.python.org/3", None),
        "numpy": ("https://numpy.org/doc/stable/", None),
        "pandas": ("https://pandas.pydata.org/docs/", None),
        "matplotlib": ("https://matplotlib.org/stable/", None),
    }

# Todo extension
todo_include_todos = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
html_theme = "pydata_sphinx_theme"

html_theme_options = {
    "github_url": "https://github.com/Vaman971/weight-tool",
    "use_edit_page_button": True,
    "navbar_start": ["navbar-logo"],
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["navbar-icon-links"],
    "header_links_before_dropdown": 6,
    "secondary_sidebar_items": ["page-toc", "edit-this-page", "sourcelink"],
    "show_nav_level": 2,
    "footer_start": ["copyright"],
    "footer_end": ["sphinx-version"],
    "show_toc_level": 3,
}

html_context = {
    "github_user": "airbus-amber",
    "github_repo": "weight-function-calculator",
    "github_version": "main",
    "doc_path": "docs/source",
}

html_sidebars = {
    "**": ["search-field", "sidebar-nav-bs"],
    "index": [],
}

html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_title = "Weight Function Calculator"
html_short_title = "WFC"
html_show_sourcelink = True

# -- Options for LaTeX / PDF output ------------------------------------------
latex_elements = {
    "papersize": "a4paper",
    "pointsize": "11pt",
}
