from pathlib import Path

import h5py
import numpy as np
import cantera as ct

from dfode_kit.utils import is_number, read_openfoam_scalar


def gather_species_arrays(species_names, directory_path) -> np.ndarray:
    """
    Concatenate scalar arrays from OpenFOAM files for each species in the specified directory.
    """
    all_arrays = []
    num_cell = None
    directory_path = Path(directory_path)

    if not Path(directory_path).is_dir():
        raise ValueError(f'The directory does not exist: {directory_path}')

    for species in species_names:
        file_path = directory_path / species

        if file_path.is_file():
            try:
                species_array = read_openfoam_scalar(file_path)

                if isinstance(species_array, np.ndarray):
                    if num_cell is None:
                        num_cell = species_array.shape[0]
                    elif species_array.shape[0] != num_cell:
                        raise ValueError(
                            f'Shape mismatch for {species}: expected {num_cell}, got {species_array.shape[0]}.'
                        )

                all_arrays.append(species_array)
            except ValueError as e:
                print(f'Error reading {file_path}: {e}')
        else:
            print(f'File not found: {file_path}')

    for i in range(len(all_arrays)):
        if not isinstance(all_arrays[i], np.ndarray):
            if isinstance(all_arrays[i], float):
                all_arrays[i] = np.full((num_cell, 1), all_arrays[i])
            else:
                print(f'Warning: {all_arrays[i]} is not a numpy array or float.')

    if all_arrays:
        return np.concatenate(all_arrays, axis=1)
    raise ValueError('No valid species arrays found to concatenate.')


def df_to_h5(root_dir, mechanism, hdf5_file_path, include_mesh=True):
    """
    Iterate through directories in root_dir, concatenate arrays, and save to an HDF5 file.
    """
    root_path = Path(root_dir).resolve()
    mechanism = Path(mechanism).resolve()
    hdf5_file_path = Path(hdf5_file_path)
    gas = ct.Solution(mechanism)
    species_names = ['T', 'p'] + gas.species_names
    print(f'Species names: {species_names}')

    with h5py.File(hdf5_file_path, 'w') as hdf5_file:
        hdf5_file.attrs['root_directory'] = str(root_path)
        hdf5_file.attrs['mechanism'] = str(mechanism)
        hdf5_file.attrs['species_names'] = species_names

        scalar_group = hdf5_file.create_group('scalar_fields')

        numeric_dirs = [
            dir_path for dir_path in root_path.iterdir()
            if dir_path.is_dir() and is_number(dir_path.name) and dir_path.name != '0'
        ]
        numeric_dirs.sort(key=lambda x: float(x.name))

        for dir_path in numeric_dirs:
            try:
                concatenated_array = gather_species_arrays(species_names, dir_path)
                scalar_group.create_dataset(str(dir_path.name), data=concatenated_array)
            except ValueError as e:
                print(f'Error processing directory {dir_path}: {e}')

        if include_mesh:
            mesh_group = hdf5_file.create_group('mesh')
            mesh_files = [
                root_path / 'temp/0/Cx',
                root_path / 'temp/0/Cy',
                root_path / 'temp/0/Cz',
                root_path / 'temp/0/V',
            ]

            for mesh_file in mesh_files:
                if mesh_file.is_file():
                    try:
                        mesh_data = read_openfoam_scalar(mesh_file)
                        mesh_group.create_dataset(str(mesh_file.name), data=mesh_data)
                    except ValueError as e:
                        print(f'Error reading mesh file {mesh_file}: {e}')
                else:
                    print(f'Mesh file not found: {mesh_file}')

    print(f'Saved concatenated arrays to {hdf5_file_path}')
