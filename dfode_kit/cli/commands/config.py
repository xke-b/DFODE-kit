from __future__ import annotations

import argparse
import json


def add_command_parser(subparsers):
    config_parser = subparsers.add_parser(
        'config',
        help='Manage persistent DFODE-kit runtime configuration.',
    )
    config_subparsers = config_parser.add_subparsers(dest='config_command')

    path_parser = config_subparsers.add_parser('path', help='Print the runtime config file path.')
    path_parser.add_argument('--json', action='store_true', help='Print structured JSON output.')

    show_parser = config_subparsers.add_parser('show', help='Show the current runtime configuration.')
    show_parser.add_argument('--json', action='store_true', help='Print structured JSON output.')

    schema_parser = config_subparsers.add_parser('schema', help='Show supported config keys and defaults.')
    schema_parser.add_argument('--json', action='store_true', help='Print structured JSON output.')

    set_parser = config_subparsers.add_parser('set', help='Persist a config key/value pair.')
    set_parser.add_argument('key', type=str)
    set_parser.add_argument('value', type=str)
    set_parser.add_argument('--json', action='store_true', help='Print structured JSON output.')

    unset_parser = config_subparsers.add_parser('unset', help='Reset a config key to its default.')
    unset_parser.add_argument('key', type=str)
    unset_parser.add_argument('--json', action='store_true', help='Print structured JSON output.')


def handle_command(args):
    from dfode_kit.runtime.config import (
        describe_config_schema,
        get_config_path,
        load_runtime_config,
        set_config_value,
        unset_config_value,
    )

    if args.config_command == 'path':
        path = str(get_config_path())
        if args.json:
            print(json.dumps({'config_path': path}, indent=2, sort_keys=True))
        else:
            print(path)
        return

    if args.config_command == 'show':
        config = load_runtime_config()
        if args.json:
            print(json.dumps(config, indent=2, sort_keys=True))
        else:
            for key, value in config.items():
                print(f'{key}: {value}')
        return

    if args.config_command == 'schema':
        schema = describe_config_schema()
        if args.json:
            print(json.dumps(schema, indent=2, sort_keys=True))
        else:
            for key, meta in schema.items():
                print(f'{key}:')
                print(f'  description: {meta["description"]}')
                print(f'  default: {meta["default"]}')
        return

    if args.config_command == 'set':
        config, path = set_config_value(args.key, args.value)
        if args.json:
            print(json.dumps({'event': 'config_set', 'key': args.key, 'path': str(path), 'config': config}, indent=2, sort_keys=True))
        else:
            print(f'Set {args.key} in {path}')
        return

    if args.config_command == 'unset':
        config, path = unset_config_value(args.key)
        if args.json:
            print(json.dumps({'event': 'config_unset', 'key': args.key, 'path': str(path), 'config': config}, indent=2, sort_keys=True))
        else:
            print(f'Unset {args.key} in {path}')
        return

    raise ValueError('The config command requires a subcommand: path, show, schema, set, or unset.')
