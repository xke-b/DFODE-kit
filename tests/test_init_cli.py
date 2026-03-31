from pathlib import Path
from types import ModuleType, SimpleNamespace
import sys

from dfode_kit.cli_tools.commands import init_helpers


class FakeCfg:
    flame_speed = 0.4
    flame_thickness = 0.001
    domain_length = 0.05
    domain_width = 0.005
    ignition_region = 0.025
    sim_time_step = 1e-6
    num_output_steps = 100
    sim_write_interval = 2e-4
    sim_time = 2.02e-2
    inlet_speed = 0.4
    inert_specie = 'N2'


class DummyArgs(SimpleNamespace):
    pass


def make_args(tmp_path, **overrides):
    data = {
        'command': 'init',
        'init_command': 'oneD-flame',
        'mech': str(tmp_path / 'mech.yaml'),
        'fuel': 'CH4:1',
        'oxidizer': 'air',
        'phi': 1.0,
        'T0': 300.0,
        'p0': 101325.0,
        'preset': 'premixed-defaults-v1',
        'template': str(tmp_path / 'template'),
        'out': str(tmp_path / 'case'),
        'from_config': None,
        'write_config': None,
        'preview': True,
        'apply': False,
        'json': True,
        'force': False,
        'inert_specie': 'N2',
        'domain_length': None,
        'domain_width': None,
        'ignition_region': None,
        'sim_time_step': None,
        'sim_time': None,
        'sim_write_interval': None,
        'num_output_steps': None,
        'inlet_speed': None,
    }
    data.update(overrides)
    return DummyArgs(**data)


def test_resolve_one_d_flame_plan_uses_template_and_overrides(tmp_path, monkeypatch):
    template = tmp_path / 'template'
    template.mkdir()
    args = make_args(tmp_path, domain_length=0.123)

    monkeypatch.setattr(init_helpers, '_build_one_d_flame_config', lambda inputs, overrides, quiet=False: FakeCfg())

    plan = init_helpers.resolve_one_d_flame_plan(args)

    assert plan['case_type'] == 'oneD-flame'
    assert plan['inputs']['oxidizer'] == 'O2:1, N2:3.76'
    assert plan['resolved']['domain_length'] == 0.05
    assert 'domain_length' in plan['assumptions']


def test_apply_one_d_flame_plan_copies_template_and_writes_metadata(tmp_path, monkeypatch):
    template = tmp_path / 'template'
    (template / 'system').mkdir(parents=True)
    (template / '0').mkdir()
    (template / 'system' / 'sampleConfigDict.orig').write_text('x', encoding='utf-8')
    (template / 'system' / 'setFieldsDict.orig').write_text('x', encoding='utf-8')
    (template / '0' / 'Ydefault.orig').write_text('x', encoding='utf-8')

    plan = {
        'case_type': 'oneD-flame',
        'preset': 'premixed-defaults-v1',
        'template': str(template),
        'output_dir': str(tmp_path / 'case'),
        'inputs': {
            'mechanism': str(tmp_path / 'mech.yaml'),
            'fuel': 'CH4:1',
            'oxidizer': 'O2:1, N2:3.76',
            'eq_ratio': 1.0,
            'T0': 300.0,
            'p0': 101325.0,
            'preset': 'premixed-defaults-v1',
            'template': str(template),
            'inert_specie': 'N2',
        },
        'resolved': {'domain_length': 0.05},
    }

    monkeypatch.setattr(init_helpers, '_build_one_d_flame_config', lambda inputs, overrides, quiet=False: FakeCfg())

    fake_module = ModuleType('dfode_kit.df_interface.oneDflame_setup')
    calls = {}

    def fake_setup(cfg, case_path):
        calls['case_path'] = str(case_path)

    fake_module.setup_one_d_flame_case = fake_setup
    monkeypatch.setitem(sys.modules, 'dfode_kit.df_interface.oneDflame_setup', fake_module)

    result = init_helpers.apply_one_d_flame_plan(plan, force=False)

    assert Path(result['case_dir']).is_dir()
    assert Path(result['metadata_path']).is_file()
    assert calls['case_path'] == result['case_dir']
