import argparse
import sys

from dfode_kit.cli_tools.command_loader import load_commands


def build_parser(commands):
    parser = argparse.ArgumentParser(
        prog='dfode-kit',
        description=(
            'dfode-kit provides a command-line interface for performing various tasks '
            'related to deep learning and reacting flow simulations. This toolkit allows '
            'users to efficiently augment data, label datasets, sample from low-dimensional '
            'flame simulations, and train deep learning models. It is designed to support '
            'physics-informed methodologies for accurate and reliable simulations.'
        ),
    )
    parser.add_argument(
        '--list-commands',
        action='store_true',
        help='List available commands in deterministic order and exit.',
    )
    subparsers = parser.add_subparsers(dest='command')

    for command_name, command_module in commands.items():
        command_module.add_command_parser(subparsers)

    return parser


def main(argv=None):
    commands = load_commands()
    parser = build_parser(commands)
    args = parser.parse_args(argv)

    if args.list_commands:
        for command_name in commands:
            print(command_name)
        return 0

    if args.command is None:
        parser.print_usage(sys.stderr)
        return 2

    command_module = commands.get(args.command)
    if command_module is None or not hasattr(command_module, 'handle_command'):
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
