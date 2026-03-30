UV ?= uv
PYTHON ?= .venv/bin/python

.PHONY: bootstrap-harness bootstrap-docs docs-build docs-serve check test verify

bootstrap-harness:
	$(UV) venv .venv
	$(UV) pip install --python $(PYTHON) pytest numpy h5py

bootstrap-docs:
	$(UV) venv .venv
	$(UV) pip install --python $(PYTHON) -r requirements-docs.txt

docs-build:
	$(PYTHON) -m mkdocs build --clean

docs-serve:
	$(PYTHON) -m mkdocs serve

check:
	$(PYTHON) -m compileall dfode_kit tests

test:
	$(PYTHON) -m pytest -q

verify: check test
