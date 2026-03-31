from __future__ import annotations

from typing import Dict

import h5py
import numpy as np

SCALAR_FIELDS_GROUP = "scalar_fields"
MECHANISM_ATTR = "mechanism"


def require_h5_group(hdf5_file: h5py.File, group_name: str) -> h5py.Group:
    if group_name not in hdf5_file:
        raise ValueError(f"'{group_name}' group not found in HDF5 file")
    return hdf5_file[group_name]


def require_h5_attr(hdf5_file: h5py.File, attr_name: str):
    if attr_name not in hdf5_file.attrs:
        raise ValueError(f"Required HDF5 root attribute '{attr_name}' is missing")
    return hdf5_file.attrs[attr_name]


def ordered_group_dataset_names(group: h5py.Group) -> list[str]:
    names = list(group.keys())
    return sorted(names, key=_dataset_name_sort_key)


def read_scalar_field_datasets(hdf5_file_path: str) -> Dict[str, np.ndarray]:
    with h5py.File(hdf5_file_path, "r") as hdf5_file:
        scalar_group = require_h5_group(hdf5_file, SCALAR_FIELDS_GROUP)
        dataset_names = ordered_group_dataset_names(scalar_group)

        data = {name: scalar_group[name][:] for name in dataset_names}

    _validate_scalar_field_datasets(data, source=hdf5_file_path)
    return data


def stack_scalar_field_datasets(hdf5_file_path: str) -> np.ndarray:
    datasets = read_scalar_field_datasets(hdf5_file_path)
    return np.concatenate(list(datasets.values()), axis=0)


def _validate_scalar_field_datasets(datasets: Dict[str, np.ndarray], source: str) -> None:
    if not datasets:
        raise ValueError(f"No datasets found in '{SCALAR_FIELDS_GROUP}' for {source}")

    expected_columns = None
    for dataset_name, dataset in datasets.items():
        if dataset.ndim != 2:
            raise ValueError(
                f"Dataset '{dataset_name}' in '{SCALAR_FIELDS_GROUP}' must be 2D; got shape {dataset.shape}"
            )

        if expected_columns is None:
            expected_columns = dataset.shape[1]
        elif dataset.shape[1] != expected_columns:
            raise ValueError(
                "All datasets in 'scalar_fields' must share the same column count; "
                f"expected {expected_columns}, got {dataset.shape[1]} for dataset '{dataset_name}'"
            )


def _dataset_name_sort_key(name: str):
    try:
        return (0, float(name))
    except ValueError:
        return (1, name)
