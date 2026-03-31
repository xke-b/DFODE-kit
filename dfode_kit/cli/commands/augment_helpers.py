from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_AUGMENT_PRESET = 'random-local-combustion-v1'


@dataclass(frozen=True)
class AugmentPreset:
    name: str
    summary: str
    resolved: dict[str, Any]
    notes: list[str]


AUGMENT_PRESETS: dict[str, AugmentPreset] = {
    DEFAULT_AUGMENT_PRESET: AugmentPreset(
        name=DEFAULT_AUGMENT_PRESET,
        summary='Current random local perturbation workflow with combustion-oriented defaults.',
        resolved={
            'heat_limit': False,
            'element_limit': True,
        },
        notes=[
            'This preset preserves the current default augmentation behavior on main.',
            'The CLI intentionally keeps the public surface minimal; detailed tuning should happen through config round-trip or future preset revisions.',
        ],
    )
}


def get_augment_preset(name: str) -> AugmentPreset:
    try:
        return AUGMENT_PRESETS[name]
    except KeyError as exc:
        raise ValueError(
            f"Unknown augment preset: {name}. Available presets: {', '.join(sorted(AUGMENT_PRESETS))}"
        ) from exc


def resolve_augment_plan(args) -> dict[str, Any]:
    if args.from_config:
        plan = load_plan_json(args.from_config)
        if plan.get('command_type') != 'augment':
            raise ValueError(f"Unsupported command_type in config: {plan.get('command_type')}")

        source = args.source or plan.get('source')
        mech = args.mech or plan.get('mechanism')
        save = args.save or plan.get('save')
        preset_name = args.preset or plan.get('preset', DEFAULT_AUGMENT_PRESET)
        target_size = args.target_size if args.target_size is not None else plan.get('target_size')
        seed = args.seed if args.seed is not None else plan.get('seed')
    else:
        _validate_required_args(args, ('source', 'mech', 'preset', 'target_size'))
        source = args.source
        mech = args.mech
        save = args.save
        preset_name = args.preset
        target_size = args.target_size
        seed = args.seed

    if args.apply and not save:
        raise ValueError('The --save path is required when using --apply.')

    preset = get_augment_preset(preset_name)
    source_path = Path(source).resolve()
    if not source_path.is_file():
        raise ValueError(f'Source file does not exist: {source_path}')

    mechanism_path = Path(mech).resolve()
    if not mechanism_path.is_file():
        raise ValueError(f'Mechanism file does not exist: {mechanism_path}')

    plan = {
        'schema_version': 1,
        'command_type': 'augment',
        'preset': preset.name,
        'preset_summary': preset.summary,
        'source': str(source_path),
        'mechanism': str(mechanism_path),
        'save': str(Path(save).resolve()) if save else None,
        'target_size': int(target_size),
        'seed': int(seed) if seed is not None else None,
        'config_path': str(Path(args.from_config).resolve()) if args.from_config else None,
        'notes': preset.notes,
        'resolved': dict(preset.resolved),
    }
    return plan


def apply_augment_plan(plan: dict[str, Any], quiet: bool = False) -> dict[str, Any]:
    import numpy as np

    from dfode_kit.data import get_TPY_from_h5, random_perturb

    source_path = Path(plan['source']).resolve()
    output_path = Path(plan['save']).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if quiet:
        with redirect_stdout(io.StringIO()):
            data = get_TPY_from_h5(source_path)
            augmented = random_perturb(
                data,
                plan['mechanism'],
                plan['target_size'],
                plan['resolved']['heat_limit'],
                plan['resolved']['element_limit'],
                seed=plan.get('seed'),
            )
    else:
        print('Handling augment command')
        print(f'Loading data from h5 file: {source_path}')
        data = get_TPY_from_h5(source_path)
        print('Data shape:', data.shape)
        augmented = random_perturb(
            data,
            plan['mechanism'],
            plan['target_size'],
            plan['resolved']['heat_limit'],
            plan['resolved']['element_limit'],
            seed=plan.get('seed'),
        )
        print('Saved augmented data shape:', augmented.shape)
        print(f'Saved augmented data to {output_path}')

    np.save(output_path, augmented)

    return {
        'event': 'augmentation_completed',
        'source': str(source_path),
        'output_path': str(output_path),
        'preset': plan['preset'],
        'requested_count': int(plan['target_size']),
        'returned_count': int(augmented.shape[0]),
        'feature_count': int(augmented.shape[1]) if augmented.ndim == 2 else None,
        'seed': plan.get('seed'),
    }


def dump_plan_json(plan: dict[str, Any], path: str | Path) -> Path:
    output_path = Path(path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return output_path


def load_plan_json(path: str | Path) -> dict[str, Any]:
    input_path = Path(path).resolve()
    return json.loads(input_path.read_text(encoding='utf-8'))


def _validate_required_args(args, names: tuple[str, ...]):
    missing = [f'--{name.replace("_", "-")}' for name in names if getattr(args, name) is None]
    if missing:
        raise ValueError(f'Missing required arguments: {", ".join(missing)}')
