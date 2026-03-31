import json
from pathlib import Path
from types import SimpleNamespace

from dfode_kit.cli.commands import augment, augment_helpers


class DummyArgs(SimpleNamespace):
    pass


def make_args(tmp_path, **overrides):
    source = tmp_path / 'sample.h5'
    source.write_text('stub', encoding='utf-8')
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
    )

    loaded = augment_helpers.resolve_augment_plan(from_config_args)

    assert loaded['save'] == str(override_path.resolve())
    assert loaded['target_size'] == 12
    assert loaded['seed'] == 123


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
    assert payload['apply']['returned_count'] == 9


def test_handle_command_requires_action(tmp_path):
    args = make_args(tmp_path, preview=False, apply=False, write_config=None)

    try:
        augment.handle_command(args)
    except ValueError as exc:
        assert 'Specify at least one action' in str(exc)
    else:
        raise AssertionError('expected ValueError')
