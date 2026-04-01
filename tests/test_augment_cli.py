import json
from pathlib import Path
from types import SimpleNamespace

import h5py
import numpy as np

from dfode_kit.cli.commands import augment, augment_helpers
import dfode_kit.data as data_module


class DummyArgs(SimpleNamespace):
    pass


def make_args(tmp_path, **overrides):
    source = tmp_path / 'sample.h5'
    with h5py.File(source, 'w') as h5:
        scalar = h5.create_group('scalar_fields')
        scalar.create_dataset('0.0', data=np.array([[1.0, 2.0], [3.0, 4.0]]))
        scalar.create_dataset('1.0', data=np.array([[5.0, 6.0], [7.0, 8.0]]))
        scalar.create_dataset('2.0', data=np.array([[9.0, 10.0], [11.0, 12.0]]))
    mech = tmp_path / 'mech.yaml'
    mech.write_text('stub', encoding='utf-8')
    data = {
        'command': 'augment',
        'source': str(source),
        'mech': str(mech),
        'save': str(tmp_path / 'aug.npy'),
        'preset': augment_helpers.DEFAULT_AUGMENT_PRESET,
        'target_size': 12,
        'seed': 123,
        'from_config': None,
        'write_config': None,
        'preview': True,
        'apply': False,
        'json': True,
        'time': None,
    }
    data.update(overrides)
    return DummyArgs(**data)


def test_resolve_augment_plan_uses_minimal_contract(tmp_path):
    args = make_args(tmp_path)

    plan = augment_helpers.resolve_augment_plan(args)

    assert plan['command_type'] == 'augment'
    assert plan['preset'] == augment_helpers.DEFAULT_AUGMENT_PRESET
    assert plan['target_size'] == 12
    assert plan['seed'] == 123
    assert plan['resolved'] == {'heat_limit': False, 'element_limit': True}
    assert plan['resolved_snapshot_names'] == ['0.0', '1.0', '2.0']


def test_resolve_augment_plan_from_config_allows_save_override(tmp_path):
    args = make_args(tmp_path, write_config=str(tmp_path / 'augment-plan.json'))
    plan = augment_helpers.resolve_augment_plan(args)
    config_path = augment_helpers.dump_plan_json(plan, args.write_config)

    override_path = tmp_path / 'override.npy'
    from_config_args = make_args(
        tmp_path,
        source=None,
        mech=None,
        save=str(override_path),
        preset=None,
        target_size=None,
        seed=None,
        from_config=str(config_path),
        preview=True,
        apply=False,
        time=None,
    )

    loaded = augment_helpers.resolve_augment_plan(from_config_args)

    assert loaded['save'] == str(override_path.resolve())
    assert loaded['target_size'] == 12
    assert loaded['seed'] == 123


def test_resolve_augment_plan_time_selectors_support_index_and_slice(tmp_path):
    args = make_args(tmp_path, time=['0', '1:'])

    plan = augment_helpers.resolve_augment_plan(args)

    assert plan['time_selectors'] == ['0', '1:']
    assert plan['resolved_snapshot_names'] == ['0.0', '1.0', '2.0']
    assert plan['resolved_snapshot_count'] == 3


def test_resolve_augment_plan_time_selector_can_stride(tmp_path):
    args = make_args(tmp_path, time=['::2'])

    plan = augment_helpers.resolve_augment_plan(args)

    assert plan['resolved_snapshot_names'] == ['0.0', '2.0']


def test_resolve_augment_plan_time_selector_out_of_range_fails(tmp_path):
    args = make_args(tmp_path, time=['10'])

    try:
        augment_helpers.resolve_augment_plan(args)
    except ValueError as exc:
        assert 'out of range' in str(exc)
    else:
        raise AssertionError('expected ValueError')


def test_apply_augment_plan_uses_selected_snapshots_only(tmp_path, monkeypatch):
    args = make_args(tmp_path, time=['1'])
    plan = augment_helpers.resolve_augment_plan(args)
    captured = {}

    def fake_random_perturb(data, mech_path, dataset, heat_limit, element_limit, seed=None):
        captured['data'] = data.copy()
        return data

    monkeypatch.setattr(data_module, 'random_perturb', fake_random_perturb)

    result = augment_helpers.apply_augment_plan(plan, quiet=True)

    assert result['resolved_snapshot_count'] == 1
    assert captured['data'].shape == (2, 2)
    assert captured['data'][0, 0] == 5.0
    assert Path(plan['save']).exists()



def test_handle_command_json_preview_and_apply(tmp_path, monkeypatch, capsys):
    args = make_args(tmp_path, preview=True, apply=True, json=True)

    monkeypatch.setattr(augment_helpers, 'apply_augment_plan', lambda plan, quiet=False: {
        'event': 'augmentation_completed',
        'output_path': plan['save'],
        'returned_count': 9,
        'source': plan['source'],
        'preset': plan['preset'],
        'requested_count': plan['target_size'],
        'seed': plan['seed'],
    })

    augment.handle_command(args)

    payload = json.loads(capsys.readouterr().out)
    assert payload['command_type'] == 'augment'
    assert payload['plan']['target_size'] == 12
    assert payload['plan']['resolved_snapshot_count'] == 3
    assert payload['apply']['returned_count'] == 9


def test_handle_command_requires_action(tmp_path):
    args = make_args(tmp_path, preview=False, apply=False, write_config=None)

    try:
        augment.handle_command(args)
    except ValueError as exc:
        assert 'Specify at least one action' in str(exc)
    else:
        raise AssertionError('expected ValueError')
