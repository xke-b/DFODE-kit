import argparse
import sys

from dfode_kit.cli_tools.command_loader import load_command, load_command_specs


DESCRIPTION = (
    'dfode-kit provides a command-line interface for performing various tasks '
    'related to deep learning and reacting flow simulations. This toolkit allows '
    'users to efficiently augment data, label datasets, sample from low-dimensional '
    'flame simulations, and train deep learning models. It is designed to support '
    'physics-informed methodologies for accurate and reliable simulations.'
)


def build_parser(command_specs, selected_command=None):
    parser = argparse.ArgumentParser(prog='dfode-kit', description=DESCRIPTION)
    parser.add_argument(
        '--list-commands',
        action='store_true',
        help='List available commands in deterministic order and exit.',
    )
    subparsers = parser.add_subparsers(dest='command')

    for command_name, command_spec in command_specs.items():
        if command_name == selected_command:
            command_module = load_command(command_name, command_specs)
            command_module.add_command_parser(subparsers)
        else:
            subparsers.add_parser(
                command_name,
                help=command_spec['help'],
                add_help=False,
            )

    return parser


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    command_specs = load_command_specs()

    lightweight_parser = build_parser(command_specs)
    known_args, _ = lightweight_parser.parse_known_args(argv)

    if known_args.list_commands:
        for command_name in command_specs:
            print(command_name)
        return 0

    if known_args.command is None:
        lightweight_parser.print_usage(sys.stderr)
        return 2

    try:
        command_module = load_command(known_args.command, command_specs)
    except KeyError:
        print(f"Unknown command: {known_args.command}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"Command '{known_args.command}' is unavailable: {exc}", file=sys.stderr)
        return 1

    parser = build_parser(command_specs, selected_command=known_args.command)
    args = parser.parse_args(argv)

    if not hasattr(command_module, 'handle_command'):
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 2

    try:
        command_module.handle_command(args)
    except Exception as exc:
        print(f"Command '{args.command}' failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
