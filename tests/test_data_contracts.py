import importlib
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import h5py
import numpy as np
import pytest


CONTRACTS_PATH = Path(__file__).resolve().parents[1] / "dfode_kit" / "data" / "contracts.py"
SPEC = spec_from_file_location("dfode_contracts_module", CONTRACTS_PATH)
contracts = module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(contracts)


def write_scalar_fields_h5(path: Path, datasets: dict[str, np.ndarray], mechanism: str = "mech.yaml"):
    with h5py.File(path, "w") as h5_file:
        h5_file.attrs[contracts.MECHANISM_ATTR] = mechanism
        group = h5_file.create_group(contracts.SCALAR_FIELDS_GROUP)
        for name, data in datasets.items():
            group.create_dataset(name, data=data)


def test_importing_data_contracts_does_not_require_cantera_or_torch():
    contracts_module = importlib.import_module("dfode_kit.data.contracts")
    assert contracts_module.SCALAR_FIELDS_GROUP == "scalar_fields"


def test_legacy_data_operations_contracts_path_re_exports_new_contracts_module():
    legacy_contracts = importlib.import_module("dfode_kit.data_operations.contracts")
    new_contracts = importlib.import_module("dfode_kit.data.contracts")

    assert legacy_contracts.SCALAR_FIELDS_GROUP == new_contracts.SCALAR_FIELDS_GROUP
    assert legacy_contracts.stack_scalar_field_datasets is new_contracts.stack_scalar_field_datasets


def test_stack_scalar_field_datasets_uses_deterministic_numeric_order(tmp_path):
    path = tmp_path / "states.h5"
    write_scalar_fields_h5(
        path,
        {
            "10": np.array([[10.0, 10.1]]),
            "2": np.array([[2.0, 2.1]]),
            "1": np.array([[1.0, 1.1]]),
        },
    )

    stacked = contracts.stack_scalar_field_datasets(path)

    assert np.allclose(
        stacked,
        np.array([[1.0, 1.1], [2.0, 2.1], [10.0, 10.1]]),
    )


def test_read_scalar_field_datasets_rejects_missing_group(tmp_path):
    path = tmp_path / "missing-group.h5"
    with h5py.File(path, "w") as h5_file:
        h5_file.attrs[contracts.MECHANISM_ATTR] = "mech.yaml"

    with pytest.raises(ValueError, match="scalar_fields"):
        contracts.read_scalar_field_datasets(path)


def test_read_scalar_field_datasets_rejects_inconsistent_column_counts(tmp_path):
    path = tmp_path / "bad-columns.h5"
    write_scalar_fields_h5(
        path,
        {
            "0": np.array([[1.0, 2.0, 3.0]]),
            "1": np.array([[4.0, 5.0]]),
        },
    )

    with pytest.raises(ValueError, match="column count"):
        contracts.read_scalar_field_datasets(path)


def test_require_h5_attr_rejects_missing_root_attr(tmp_path):
    path = tmp_path / "missing-attr.h5"
    with h5py.File(path, "w") as h5_file:
        h5_file.create_group(contracts.SCALAR_FIELDS_GROUP)

    with h5py.File(path, "r") as h5_file:
        with pytest.raises(ValueError, match=contracts.MECHANISM_ATTR):
            contracts.require_h5_attr(h5_file, contracts.MECHANISM_ATTR)
