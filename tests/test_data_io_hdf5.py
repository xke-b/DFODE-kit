import importlib
from pathlib import Path

import h5py
import numpy as np

from dfode_kit.data.contracts import MECHANISM_ATTR, SCALAR_FIELDS_GROUP


def write_scalar_fields_h5(path: Path, datasets: dict[str, np.ndarray], mechanism: str = "mech.yaml"):
    with h5py.File(path, "w") as h5_file:
        h5_file.attrs[MECHANISM_ATTR] = mechanism
        group = h5_file.create_group(SCALAR_FIELDS_GROUP)
        for name, data in datasets.items():
            group.create_dataset(name, data=data)


def test_importing_data_io_hdf5_does_not_require_cantera_or_torch():
    io_module = importlib.import_module("dfode_kit.data.io_hdf5")
    assert io_module.get_TPY_from_h5 is not None


def test_get_tpy_from_h5_uses_contract_ordering_and_stacks_datasets(tmp_path, capsys):
    path = tmp_path / "states.h5"
    write_scalar_fields_h5(
        path,
        {
            "10": np.array([[10.0, 10.1]]),
            "2": np.array([[2.0, 2.1]]),
            "1": np.array([[1.0, 1.1]]),
        },
    )

    io_module = importlib.import_module("dfode_kit.data.io_hdf5")
    stacked = io_module.get_TPY_from_h5(path)

    assert np.allclose(
        stacked,
        np.array([[1.0, 1.1], [2.0, 2.1], [10.0, 10.1]]),
    )
    assert f"Number of datasets in {SCALAR_FIELDS_GROUP} group: 3" in capsys.readouterr().out


def test_legacy_package_exports_point_to_extracted_io_helpers():
    legacy_data_operations = importlib.import_module("dfode_kit.data_operations")
    root_package = importlib.import_module("dfode_kit")
    io_module = importlib.import_module("dfode_kit.data.io_hdf5")

    assert legacy_data_operations.touch_h5 is io_module.touch_h5
    assert legacy_data_operations.get_TPY_from_h5 is io_module.get_TPY_from_h5
    assert root_package.touch_h5 is io_module.touch_h5
    assert root_package.get_TPY_from_h5 is io_module.get_TPY_from_h5
