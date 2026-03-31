from pathlib import Path
from types import SimpleNamespace

from dfode_kit.runtime import run_case as run_case_helpers


class DummyArgs(SimpleNamespace):
    pass


def make_args(tmp_path, **overrides):
    case_dir = tmp_path / 'case'
    case_dir.mkdir()
    (case_dir / 'Allrun').write_text('#!/bin/sh\nexit 0\n', encoding='utf-8')
    data = {
        'case': str(case_dir),
        'runner': 'Allrun',
        'np': None,
        'preview': True,
        'apply': False,
        'json': True,
        'openfoam_bashrc': '/opt/openfoam7/etc/bashrc',
        'conda_sh': '/home/xk/miniconda3/etc/profile.d/conda.sh',
        'conda_env': 'deepflame',
        'deepflame_bashrc': '/home/xk/deepflame/bashrc',
        'python_executable': None,
        'mpirun_command': None,
    }
    data.update(overrides)
    return DummyArgs(**data)


def test_resolve_run_case_plan_uses_overrides(monkeypatch, tmp_path):
    args = make_args(tmp_path)
    monkeypatch.setattr(
        run_case_helpers,
        'resolve_runtime_config',
        lambda overrides=None: {
            'openfoam_bashrc': overrides['openfoam_bashrc'],
            'conda_sh': overrides['conda_sh'],
            'conda_env_name': overrides['conda_env_name'],
            'deepflame_bashrc': overrides['deepflame_bashrc'],
            'python_executable': overrides['python_executable'],
            'default_np': 4,
            'mpirun_command': 'mpirun',
        },
    )

    plan = run_case_helpers.resolve_run_case_plan(args)

    assert plan['case_type'] == 'deepflame-run-case'
    assert plan['runner'] == 'Allrun'
    assert 'conda activate deepflame' in plan['shell_script']
    assert plan['runtime_config']['openfoam_bashrc'] == '/opt/openfoam7/etc/bashrc'


def test_execute_run_case_json_mode_writes_logs(monkeypatch, tmp_path):
    case_dir = tmp_path / 'case'
    case_dir.mkdir()
    plan = {
        'case_dir': str(case_dir),
        'runner': 'Allrun',
        'shell_script': 'echo hello',
    }

    calls = {}

    class Completed:
        returncode = 0

    def fake_run(command, stdout=None, stderr=None, text=None):
        calls['command'] = command
        if stdout is not None:
            stdout.write('ok\n')
        if stderr is not None:
            stderr.write('')
        return Completed()

    monkeypatch.setattr(run_case_helpers.subprocess, 'run', fake_run)

    result = run_case_helpers.execute_run_case(plan, quiet=True)

    assert result['exit_code'] == 0
    assert Path(result['stdout_log']).is_file()
    assert Path(result['stderr_log']).is_file()
    assert calls['command'] == ['bash', '-lc', 'echo hello']



def test_legacy_run_case_helpers_shim_matches_new_module():
    from dfode_kit.cli_tools.commands import run_case_helpers as legacy_run_case_helpers

    assert legacy_run_case_helpers.resolve_run_case_plan is run_case_helpers.resolve_run_case_plan
    assert legacy_run_case_helpers.execute_run_case is run_case_helpers.execute_run_case
