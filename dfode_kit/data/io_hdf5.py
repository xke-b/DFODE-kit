import h5py
import numpy as np

from dfode_kit.data.contracts import SCALAR_FIELDS_GROUP, read_scalar_field_datasets


def touch_h5(hdf5_file_path):
    """
    Load an HDF5 file and print its contents and metadata.

    Parameters
    ----------
    hdf5_file_path : str
        The path to the HDF5 file to be opened.

    Returns
    -------
    None
        This function does not return any value. It prints the metadata, groups,
        and datasets contained in the HDF5 file.

    Raises
    ------
    FileNotFoundError
        If the specified HDF5 file does not exist.
    OSError
        If the file cannot be opened as an HDF5 file.
    """
    print(f"Inspecting HDF5 file: {hdf5_file_path}\n")

    with h5py.File(hdf5_file_path, "r") as hdf5_file:
        print("Metadata in the HDF5 file:")
        for attr in hdf5_file.attrs:
            print(f"{attr}: {hdf5_file.attrs[attr]}")

        print("\nGroups and datasets in the HDF5 file:")
        for group_name, group in hdf5_file.items():
            print(f"Group: {group_name}")
            for dataset_name in group.keys():
                dataset = group[dataset_name]
                print(f"  Dataset: {dataset_name}, Shape: {dataset.shape}")


def get_TPY_from_h5(file_path):
    """Read and stack all datasets from the ``scalar_fields`` HDF5 group."""
    datasets = read_scalar_field_datasets(file_path)
    print(f"Number of datasets in {SCALAR_FIELDS_GROUP} group: {len(datasets)}")
    return np.concatenate(list(datasets.values()), axis=0)
