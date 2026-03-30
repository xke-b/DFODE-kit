UV ?= uv
PYTHON ?= .venv/bin/python

.PHONY: bootstrap-harness check test verify

bootstrap-harness:
	$(UV) venv .venv
	$(UV) pip install --python $(PYTHON) pytest numpy h5py

check:
	$(PYTHON) -m compileall dfode_kit tests

test:
	$(PYTHON) -m pytest -q

verify: check test
