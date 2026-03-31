from __future__ import annotations

import json

from dfode_kit.cli.commands.augment_helpers import DEFAULT_AUGMENT_PRESET


def add_command_parser(subparsers):
    augment_parser = subparsers.add_parser(
        'augment',
        help='Perform data augmentation from sampled state data.',
    )
    augment_parser.add_argument('--source', type=str, help='Path to the sampled HDF5 source file.')
    augment_parser.add_argument('--mech', type=str, help='Path to the YAML mechanism file.')
    augment_parser.add_argument('--save', type=str, help='Path to save the augmented NumPy array.')
    augment_parser.add_argument(
        '--preset',
        type=str,
        default=DEFAULT_AUGMENT_PRESET,
        help='Named augmentation preset.',
    )
    augment_parser.add_argument(
        '--target-size',
        dest='target_size',
        type=int,
        help='Requested number of augmented rows.',
    )
    augment_parser.add_argument('--seed', type=int, help='Random seed for reproducible augmentation.')
    augment_parser.add_argument('--from-config', type=str, help='Load an augment plan/config JSON.')
    augment_parser.add_argument('--write-config', type=str, help='Write the resolved augment plan/config to JSON.')
    augment_parser.add_argument('--preview', action='store_true', help='Preview the resolved plan without executing augmentation.')
    augment_parser.add_argument('--apply', action='store_true', help='Execute augmentation and write the output array.')
    augment_parser.add_argument('--json', action='store_true', help='Print structured JSON output.')


def handle_command(args):
    from dfode_kit.cli.commands.augment_helpers import apply_augment_plan, dump_plan_json, resolve_augment_plan

    if not args.preview and not args.apply and not args.write_config:
        raise ValueError('Specify at least one action: --preview, --apply, or --write-config.')

    plan = resolve_augment_plan(args)
    json_result = {'command_type': 'augment'} if args.json else None

    if args.write_config:
        config_path = dump_plan_json(plan, args.write_config)
        if args.json:
            json_result['config_written'] = {'path': str(config_path)}
        else:
            print(f'Wrote augment config: {config_path}')

    if args.preview:
        if args.json:
            json_result['plan'] = plan
        else:
            _print_human_plan(plan)

    if args.apply:
        result = apply_augment_plan(plan, quiet=args.json)
        if args.json:
            json_result['apply'] = result
        else:
            print(f"Completed augmentation from: {result['source']}")
            print(f"output_path: {result['output_path']}")
            print(f"returned_count: {result['returned_count']}")

    if args.json:
        print(json.dumps(json_result, indent=2, sort_keys=True))


def _print_human_plan(plan: dict):
    print('Resolved augment plan')
    print(f"preset: {plan['preset']}")
    print(f"source: {plan['source']}")
    print(f"mechanism: {plan['mechanism']}")
    print(f"save: {plan['save']}")
    print(f"target_size: {plan['target_size']}")
    print(f"seed: {plan['seed']}")
    print('resolved:')
    for key in sorted(plan['resolved']):
        print(f"  {key}: {plan['resolved'][key]}")
    print('notes:')
    for note in plan['notes']:
        print(f'  - {note}')
