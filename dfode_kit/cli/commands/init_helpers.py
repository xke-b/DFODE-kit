from __future__ import annotations

import io
import shutil
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

from dfode_kit.df_interface.case_init import (
    DEFAULT_ONE_D_FLAME_TEMPLATE,
    OneDFlameInitInputs,
    dump_plan_json,
    load_plan_json,
    one_d_flame_inputs_from_plan,
    one_d_flame_overrides_from_plan,
    one_d_flame_plan_dict,
    resolve_oxidizer,
)


OVERRIDE_FIELDS = {
    'domain_length': 'domain_length',
    'domain_width': 'domain_width',
    'ignition_region': 'ignition_region',
    'sim_time_step': 'sim_time_step',
    'sim_time': 'sim_time',
    'sim_write_interval': 'sim_write_interval',
    'num_output_steps': 'num_output_steps',
    'inlet_speed': 'inlet_speed',
}


def resolve_one_d_flame_plan(args) -> dict[str, Any]:
    if args.from_config:
        plan = load_plan_json(args.from_config)
        inputs = one_d_flame_inputs_from_plan(plan)
        overrides = one_d_flame_overrides_from_plan(plan)
        template = Path(inputs.template)
        out_dir = args.out or plan.get('output_dir')
    else:
        template = Path(args.template).resolve() if args.template else DEFAULT_ONE_D_FLAME_TEMPLATE.resolve()
        _validate_required_args(args, ('mech', 'fuel', 'oxidizer', 'phi'))
        inputs = OneDFlameInitInputs(
            mechanism=args.mech,
            fuel=args.fuel,
            oxidizer=resolve_oxidizer(args.oxidizer),
            eq_ratio=float(args.phi),
            T0=float(args.T0),
            p0=float(args.p0),
            preset=args.preset,
            template=str(template),
            inert_specie=args.inert_specie,
        )
        overrides = _extract_override_args(args)
        out_dir = args.out

    if args.out:
        out_dir = args.out

    if args.apply and not out_dir:
        raise ValueError('The --out path is required when using --apply.')

    template = Path(inputs.template).resolve()
    if not template.is_dir():
        raise ValueError(f'Template directory does not exist: {template}')

    cfg = _build_one_d_flame_config(inputs, overrides, quiet=getattr(args, 'json', False))

    resolved = {
        'flame_speed': cfg.flame_speed,
        'flame_thickness': cfg.flame_thickness,
        'domain_length': cfg.domain_length,
        'domain_width': cfg.domain_width,
        'ignition_region': cfg.ignition_region,
        'sim_time_step': cfg.sim_time_step,
        'num_output_steps': cfg.num_output_steps,
        'sim_write_interval': cfg.sim_write_interval,
        'sim_time': cfg.sim_time,
        'inlet_speed': cfg.inlet_speed,
        'inert_specie': cfg.inert_specie,
    }

    return one_d_flame_plan_dict(
        inputs=OneDFlameInitInputs(
            mechanism=inputs.mechanism,
            fuel=inputs.fuel,
            oxidizer=inputs.oxidizer,
            eq_ratio=inputs.eq_ratio,
            T0=inputs.T0,
            p0=inputs.p0,
            preset=inputs.preset,
            template=str(template),
            inert_specie=cfg.inert_specie,
        ),
        resolved=resolved,
        output_dir=out_dir,
        config_path=args.from_config,
    )


def apply_one_d_flame_plan(
    plan: dict[str, Any],
    force: bool = False,
    quiet: bool = False,
) -> dict[str, Any]:
    case_dir = Path(plan['output_dir']).resolve()
    template_dir = Path(plan['template']).resolve()

    if case_dir.exists():
        if not force:
            raise ValueError(f'Output directory already exists: {case_dir}. Use --force to replace it.')
        shutil.rmtree(case_dir)

    shutil.copytree(template_dir, case_dir)

    inputs = one_d_flame_inputs_from_plan(plan)
    overrides = one_d_flame_overrides_from_plan(plan)
    cfg = _build_one_d_flame_config(inputs, overrides, quiet=quiet)

    from dfode_kit.df_interface.oneDflame_setup import setup_one_d_flame_case

    if quiet:
        with redirect_stdout(io.StringIO()):
            setup_one_d_flame_case(cfg, case_dir)
    else:
        setup_one_d_flame_case(cfg, case_dir)

    metadata_path = dump_plan_json(plan, case_dir / 'dfode-init-plan.json')
    return {
        'event': 'case_initialized',
        'case_dir': str(case_dir),
        'metadata_path': str(metadata_path),
        'preset': plan['preset'],
    }


def _build_one_d_flame_config(
    inputs: OneDFlameInitInputs,
    overrides: dict[str, Any],
    quiet: bool = False,
):
    from dfode_kit.df_interface.flame_configurations import OneDFreelyPropagatingFlameConfig

    cfg = OneDFreelyPropagatingFlameConfig(
        mechanism=inputs.mechanism,
        T0=inputs.T0,
        p0=inputs.p0,
        fuel=inputs.fuel,
        oxidizer=inputs.oxidizer,
        eq_ratio=inputs.eq_ratio,
    )
    update_params = dict(overrides)
    update_params['inert_specie'] = inputs.inert_specie
    if quiet:
        with redirect_stdout(io.StringIO()):
            cfg.update_config(update_params)
    else:
        cfg.update_config(update_params)
    return cfg


def _extract_override_args(args) -> dict[str, Any]:
    overrides = {}
    for cli_name, field_name in OVERRIDE_FIELDS.items():
        value = getattr(args, cli_name)
        if value is not None:
            overrides[field_name] = value
    return overrides


def _validate_required_args(args, names: tuple[str, ...]):
    missing = [f'--{name.replace("_", "-")}' for name in names if getattr(args, name) is None]
    if missing:
        raise ValueError(f'Missing required arguments: {", ".join(missing)}')
