from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import Any

from dfode_kit.runtime_config import resolve_runtime_config


def resolve_run_case_plan(args) -> dict[str, Any]:
    case_dir = Path(args.case).resolve()
    if not case_dir.is_dir():
        raise ValueError(f'Case directory does not exist: {case_dir}')

    runner_path = case_dir / args.runner
    if not runner_path.is_file():
        raise ValueError(f'Case runner does not exist: {runner_path}')

    runtime_config = resolve_runtime_config(
        {
            'openfoam_bashrc': args.openfoam_bashrc,
            'conda_sh': args.conda_sh,
            'conda_env_name': args.conda_env,
            'deepflame_bashrc': args.deepflame_bashrc,
            'python_executable': args.python_executable,
            'mpirun_command': args.mpirun_command,
            'default_np': args.np,
        }
    )
    _validate_runtime_config(runtime_config)

    shell_lines = [
        f'source {shlex.quote(runtime_config["openfoam_bashrc"])}',
        f'source {shlex.quote(runtime_config["conda_sh"])}',
        f'conda activate {shlex.quote(runtime_config["conda_env_name"])}',
        f'source {shlex.quote(runtime_config["deepflame_bashrc"])}',
        'set -eo pipefail',
        'which dfLowMachFoam',
        f'cd {shlex.quote(str(case_dir))}',
        f'chmod +x {shlex.quote(args.runner)}',
        f'./{shlex.quote(args.runner)}',
    ]

    return {
        'schema_version': 1,
        'case_type': 'deepflame-run-case',
        'case_dir': str(case_dir),
        'runner': args.runner,
        'np': runtime_config['default_np'],
        'runtime_config': runtime_config,
        'shell_lines': shell_lines,
        'shell_script': '\n'.join(shell_lines),
    }


def execute_run_case(plan: dict[str, Any], quiet: bool = False) -> dict[str, Any]:
    case_dir = Path(plan['case_dir']).resolve()
    command = ['bash', '-lc', plan['shell_script']]

    if quiet:
        stdout_log = case_dir / 'log.dfode-run-case.stdout'
        stderr_log = case_dir / 'log.dfode-run-case.stderr'
        with stdout_log.open('w', encoding='utf-8') as stdout_handle, stderr_log.open('w', encoding='utf-8') as stderr_handle:
            completed = subprocess.run(command, stdout=stdout_handle, stderr=stderr_handle, text=True)
        result = {
            'event': 'run_case_completed',
            'case_dir': str(case_dir),
            'runner': plan['runner'],
            'exit_code': completed.returncode,
            'stdout_log': str(stdout_log),
            'stderr_log': str(stderr_log),
        }
    else:
        completed = subprocess.run(command)
        result = {
            'event': 'run_case_completed',
            'case_dir': str(case_dir),
            'runner': plan['runner'],
            'exit_code': completed.returncode,
        }

    if completed.returncode != 0:
        raise ValueError(f"Case runner failed with exit code {completed.returncode}: {case_dir / plan['runner']}")

    return result


def _validate_runtime_config(config: dict[str, Any]):
    required = ['openfoam_bashrc', 'conda_sh', 'conda_env_name', 'deepflame_bashrc']
    missing = [key for key in required if not config.get(key)]
    if missing:
        raise ValueError(
            'Missing runtime config values: '
            + ', '.join(missing)
            + '. Use `dfode-kit config set ...` or per-command overrides.'
        )
