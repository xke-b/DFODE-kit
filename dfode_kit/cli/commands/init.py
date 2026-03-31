from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def add_command_parser(subparsers):
    init_parser = subparsers.add_parser(
        'init',
        help='Initialize canonical case templates from explicit presets.',
    )
    init_subparsers = init_parser.add_subparsers(dest='init_command')

    one_d_flame = init_subparsers.add_parser(
        'oneD-flame',
        help='Initialize a one-dimensional freely propagating premixed flame case.',
    )
    one_d_flame.add_argument('--mech', type=str, help='Path to the mechanism file.')
    one_d_flame.add_argument('--fuel', type=str, help='Fuel composition string, e.g. CH4:1.')
    one_d_flame.add_argument(
        '--oxidizer',
        type=str,
        help='Oxidizer composition string, or the alias "air".',
    )
    one_d_flame.add_argument('--phi', type=float, help='Equivalence ratio.')
    one_d_flame.add_argument('--T0', type=float, default=300.0, help='Initial temperature [K].')
    one_d_flame.add_argument('--p0', type=float, default=101325.0, help='Initial pressure [Pa].')
    one_d_flame.add_argument(
        '--preset',
        type=str,
        default='premixed-defaults-v1',
        help='Named initialization preset. Preserves current empirical DFODE-kit defaults.',
    )
    one_d_flame.add_argument(
        '--template',
        type=str,
        help='Path to the case template directory. Defaults to DFODE-kit canonical 1D flame template.',
    )
    one_d_flame.add_argument('--out', type=str, help='Output case directory for generated files.')
    one_d_flame.add_argument(
        '--from-config',
        type=str,
        help='Load an init plan/config JSON produced by --write-config.',
    )
    one_d_flame.add_argument(
        '--write-config',
        type=str,
        help='Write the fully resolved init plan/config to JSON.',
    )
    one_d_flame.add_argument(
        '--preview',
        action='store_true',
        help='Preview the resolved plan without copying the case template.',
    )
    one_d_flame.add_argument(
        '--apply',
        action='store_true',
        help='Generate the case directory from the resolved plan.',
    )
    one_d_flame.add_argument(
        '--json',
        action='store_true',
        help='Print resolved plan/output as JSON for agent-readable consumption.',
    )
    one_d_flame.add_argument(
        '--force',
        action='store_true',
        help='Overwrite the output directory if it already exists.',
    )
    one_d_flame.add_argument(
        '--inert-specie',
        type=str,
        default='N2',
        help='Inert species name to write into CanteraTorchProperties.',
    )

    one_d_flame.add_argument('--domain-length', type=float, help='Override resolved domain length [m].')
    one_d_flame.add_argument('--domain-width', type=float, help='Override resolved domain width [m].')
    one_d_flame.add_argument('--ignition-region', type=float, help='Override resolved ignition region [m].')
    one_d_flame.add_argument('--sim-time-step', type=float, help='Override resolved time step [s].')
    one_d_flame.add_argument('--sim-time', type=float, help='Override resolved end time [s].')
    one_d_flame.add_argument(
        '--sim-write-interval',
        type=float,
        help='Override resolved write interval [s].',
    )
    one_d_flame.add_argument('--num-output-steps', type=int, help='Override resolved number of output steps.')
    one_d_flame.add_argument('--inlet-speed', type=float, help='Override resolved inlet speed [m/s].')


PREVIEW_ONLY_KEYS = ('preview', 'apply', 'write_config', 'json', 'force', 'out', 'from_config', 'init_command', 'command')


def handle_command(args):
    if args.init_command != 'oneD-flame':
        raise ValueError('The init command currently supports only the oneD-flame subcommand.')
    _handle_one_d_flame(args)


def _handle_one_d_flame(args):
    from dfode_kit.cli.commands.init_helpers import resolve_one_d_flame_plan, apply_one_d_flame_plan

    if not args.preview and not args.apply and not args.write_config:
        raise ValueError('Specify at least one action: --preview, --apply, or --write-config.')

    plan = resolve_one_d_flame_plan(args)
    json_result = {'case_type': 'oneD-flame'} if args.json else None

    if args.write_config:
        from dfode_kit.cases.init import dump_plan_json

        config_path = dump_plan_json(plan, args.write_config)
        if args.json:
            json_result['config_written'] = {'path': str(config_path)}
        else:
            print(f'Wrote init config: {config_path}')

    if args.preview:
        if args.json:
            json_result['plan'] = plan
        else:
            _print_human_plan(plan)

    if args.apply:
        result = apply_one_d_flame_plan(plan, force=args.force, quiet=args.json)
        if args.json:
            json_result['apply'] = result
        else:
            print(f"Initialized case at: {result['case_dir']}")
            print(f"Metadata: {result['metadata_path']}")

    if args.json:
        print(json.dumps(json_result, indent=2, sort_keys=True))


def _print_human_plan(plan: dict):
    resolved = plan['resolved']
    print('Resolved oneD-flame init plan')
    print(f"preset: {plan['preset']}")
    print(f"template: {plan['template']}")
    print(f"output_dir: {plan['output_dir']}")
    print('inputs:')
    for key, value in plan['inputs'].items():
        print(f'  {key}: {value}')
    print('resolved:')
    for key in sorted(resolved):
        print(f'  {key}: {resolved[key]}')
    print('assumptions:')
    for key, value in plan['assumptions'].items():
        print(f'  {key}: {value}')
