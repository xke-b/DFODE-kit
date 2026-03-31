import argparse


def add_command_parser(subparsers):
    sample_parser = subparsers.add_parser('sample', help='Perform sampling.')

    sample_parser.add_argument(
        '--mech',
        required=True,
        type=str,
        help='Path to the mechanism file.'
    )
    sample_parser.add_argument(
        '--case',
        required=True,
        type=str,
        help='Root directory containing data.'
    )
    sample_parser.add_argument(
        '--save',
        required=True,
        type=str,
        help='Path where the HDF5 file will be saved.'
    )
    sample_parser.add_argument(
        '--include_mesh',
        action='store_true',
        help='Include mesh data in the HDF5 file.'
    )


def handle_command(args):
    from dfode_kit.data.io_hdf5 import touch_h5
    from dfode_kit.cases.sampling import df_to_h5

    print('Handling sample command')
    df_to_h5(args.case, args.mech, args.save, include_mesh=args.include_mesh)
    print()
    touch_h5(args.save)
