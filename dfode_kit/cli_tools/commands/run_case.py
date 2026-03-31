from __future__ import annotations

import argparse
import json
from pathlib import Path


def add_command_parser(subparsers):
    run_case_parser = subparsers.add_parser(
        'run-case',
        help='Run a DeepFlame/OpenFOAM case using stored runtime configuration.',
    )
    run_case_parser.add_argument('--case', required=True, type=str, help='Path to the case directory.')
    run_case_parser.add_argument(
        '--runner',
        default='Allrun',
        type=str,
        help='Case runner script to execute inside the case directory. Defaults to Allrun.',
    )
    run_case_parser.add_argument(
        '--np',
        type=int,
        help='MPI rank count hint recorded in metadata. Defaults to config.default_np.',
    )
    run_case_parser.add_argument('--preview', action='store_true', help='Preview the resolved runtime command without executing it.')
    run_case_parser.add_argument('--apply', action='store_true', help='Execute the case runner.')
    run_case_parser.add_argument('--json', action='store_true', help='Print structured JSON output.')
    run_case_parser.add_argument(
        '--openfoam-bashrc',
        type=str,
        help='Override config.openfoam_bashrc for this invocation.',
    )
    run_case_parser.add_argument(
        '--conda-sh',
        type=str,
        help='Override config.conda_sh for this invocation.',
    )
    run_case_parser.add_argument(
        '--conda-env',
        type=str,
        help='Override config.conda_env_name for this invocation.',
    )
    run_case_parser.add_argument(
        '--deepflame-bashrc',
        type=str,
        help='Override config.deepflame_bashrc for this invocation.',
    )
    run_case_parser.add_argument(
        '--python-executable',
        type=str,
        help='Override config.python_executable for this invocation.',
    )
    run_case_parser.add_argument(
        '--mpirun-command',
        type=str,
        help='Override config.mpirun_command for this invocation.',
    )


def handle_command(args):
    from dfode_kit.runtime.run_case import execute_run_case, resolve_run_case_plan

    if not args.preview and not args.apply:
        raise ValueError('Specify at least one action: --preview or --apply.')

    plan = resolve_run_case_plan(args)
    json_result = {'case_type': 'deepflame-run-case'} if args.json else None

    if args.preview:
        if args.json:
            json_result['plan'] = plan
        else:
            _print_human_plan(plan)

    if args.apply:
        result = execute_run_case(plan, quiet=args.json)
        if args.json:
            json_result['apply'] = result
        else:
            print(f"Completed run-case in: {result['case_dir']}")
            print(f"exit_code: {result['exit_code']}")
            if result.get('stdout_log'):
                print(f"stdout_log: {result['stdout_log']}")
                print(f"stderr_log: {result['stderr_log']}")

    if args.json:
        print(json.dumps(json_result, indent=2, sort_keys=True))


def _print_human_plan(plan: dict):
    print('Resolved run-case plan')
    print(f"case_dir: {plan['case_dir']}")
    print(f"runner: {plan['runner']}")
    print('runtime_config:')
    for key, value in plan['runtime_config'].items():
        print(f'  {key}: {value}')
    print('shell_lines:')
    for line in plan['shell_lines']:
        print(f'  {line}')
