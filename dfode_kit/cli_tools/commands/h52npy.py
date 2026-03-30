import argparse

def add_command_parser(subparsers):
    h52npy_parser = subparsers.add_parser('h52npy', help='Convert HDF5 scalar fields to NumPy array.')
    h52npy_parser.add_argument('--source', 
                               required=True,
                               type=str, 
                               help='Path to the HDF5 file.')
    h52npy_parser.add_argument('--save_to', 
                               required=True,
                               type=str, 
                               help='Path for the output NumPy file.')

def handle_command(args):
    print("Handling h52npy command")
    # Load the HDF5 file and concatenate datasets
    concatenate_datasets_to_npy(args.source, args.save_to)

def concatenate_datasets_to_npy(hdf5_file_path, output_npy_file):
    """Concatenate all datasets under the ``scalar_fields`` group and save to NPY."""
    import numpy as np

    from dfode_kit.data_operations.contracts import stack_scalar_field_datasets

    concatenated_array = stack_scalar_field_datasets(hdf5_file_path)
    print(f"Shape of the final concatenated array: {concatenated_array.shape}")
    np.save(output_npy_file, concatenated_array)
    print(f"Saved concatenated array to {output_npy_file}")
