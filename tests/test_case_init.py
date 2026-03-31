from pathlib import Path

from dfode_kit.df_interface.case_init import (
    AIR_OXIDIZER,
    DEFAULT_ONE_D_FLAME_PRESET,
    OneDFlameInitInputs,
    dump_plan_json,
    load_plan_json,
    one_d_flame_inputs_from_plan,
    one_d_flame_overrides_from_plan,
    one_d_flame_plan_dict,
    resolve_oxidizer,
)


def test_resolve_oxidizer_expands_air_alias():
    assert resolve_oxidizer('air') == AIR_OXIDIZER
    assert resolve_oxidizer('O2:1, N2:3.76') == 'O2:1, N2:3.76'


def test_plan_json_round_trip(tmp_path):
    inputs = OneDFlameInitInputs(
        mechanism='/tmp/mech.yaml',
        fuel='CH4:1',
        oxidizer='air',
        eq_ratio=1.0,
        T0=300.0,
        p0=101325.0,
    )
    plan = one_d_flame_plan_dict(
        inputs=inputs,
        resolved={'domain_length': 1.0, 'num_output_steps': 100},
        output_dir=str(tmp_path / 'case'),
    )

    path = dump_plan_json(plan, tmp_path / 'plan.json')
    loaded = load_plan_json(path)

    assert loaded['preset'] == DEFAULT_ONE_D_FLAME_PRESET
    assert loaded['inputs']['oxidizer'] == AIR_OXIDIZER
    assert loaded['resolved']['domain_length'] == 1.0

    reconstructed = one_d_flame_inputs_from_plan(loaded)
    overrides = one_d_flame_overrides_from_plan(loaded)

    assert reconstructed.fuel == 'CH4:1'
    assert reconstructed.oxidizer == AIR_OXIDIZER
    assert overrides == {'domain_length': 1.0, 'num_output_steps': 100}
