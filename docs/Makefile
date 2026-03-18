# Cross-platform Sphinx Makefile
SPHINXOPTS    ?=
SOURCEDIR     = source
BUILDDIR      = build

ifeq ($(OS),Windows_NT)
VENV_PYTHON   := ../.venv/Scripts/python.exe
else
VENV_PYTHON   := ../.venv/bin/python
endif

ifeq ($(wildcard $(VENV_PYTHON)),)
PYTHON_BIN    ?= python
else
PYTHON_BIN    ?= $(VENV_PYTHON)
endif

SPHINXBUILD   ?= $(PYTHON_BIN) -m sphinx
AUTOBUILD     ?= $(PYTHON_BIN) -m sphinx_autobuild

.PHONY: help clean html dirhtml linkcheck doctest livehtml

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	@$(SPHINXBUILD) -M clean "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

html:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

dirhtml:
	@$(SPHINXBUILD) -M dirhtml "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

linkcheck:
	@$(SPHINXBUILD) -M linkcheck "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

doctest:
	@$(SPHINXBUILD) -M doctest "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

livehtml:
	@$(AUTOBUILD) "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)
