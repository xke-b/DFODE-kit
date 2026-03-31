from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from dfode_kit import DFODE_ROOT


DEFAULT_ONE_D_FLAME_TEMPLATE = (
    DFODE_ROOT / "canonical_cases" / "oneD_freely_propagating_flame"
)
DEFAULT_ONE_D_FLAME_PRESET = "premixed-defaults-v1"
AIR_OXIDIZER = "O2:1, N2:3.76"


@dataclass(frozen=True)
class OneDFlamePreset:
    name: str
    summary: str
    assumptions: dict[str, str]
    notes: list[str]


ONE_D_FLAME_PRESETS: dict[str, OneDFlamePreset] = {
    DEFAULT_ONE_D_FLAME_PRESET: OneDFlamePreset(
        name=DEFAULT_ONE_D_FLAME_PRESET,
        summary=(
            "Current DFODE-kit empirical defaults for one-dimensional freely "
            "propagating premixed flames."
        ),
        assumptions={
            "domain_length": "flame_thickness / 10 * 500",
            "domain_width": "domain_length / 10",
            "ignition_region": "domain_length / 2",
            "sim_time_step": "1e-6",
            "num_output_steps": "100",
            "sim_write_interval": "(flame_thickness / flame_speed) * 10 / num_output_steps",
            "sim_time": "sim_write_interval * (num_output_steps + 1)",
            "inlet_speed": "flame_speed",
            "inert_specie": '"N2"',
        },
        notes=[
            "These values preserve the current hardcoded logic in OneDFreelyPropagatingFlameConfig.update_config().",
            "They are recommended starter defaults, not universal best practices.",
            "Override any resolved field explicitly when domain knowledge requires it.",
        ],
    )
}


@dataclass(frozen=True)
class OneDFlameInitInputs:
    mechanism: str
    fuel: str
    oxidizer: str
    eq_ratio: float
    T0: float
    p0: float
    preset: str = DEFAULT_ONE_D_FLAME_PRESET
    template: str = str(DEFAULT_ONE_D_FLAME_TEMPLATE)
    inert_specie: str = "N2"


def resolve_oxidizer(oxidizer: str) -> str:
    if oxidizer.strip().lower() == "air":
        return AIR_OXIDIZER
    return oxidizer


def get_one_d_flame_preset(name: str) -> OneDFlamePreset:
    try:
        return ONE_D_FLAME_PRESETS[name]
    except KeyError as exc:
        raise ValueError(
            f"Unknown oneD-flame preset: {name}. Available presets: {', '.join(sorted(ONE_D_FLAME_PRESETS))}"
        ) from exc


def one_d_flame_plan_dict(
    *,
    inputs: OneDFlameInitInputs,
    resolved: dict[str, Any],
    output_dir: str | None,
    config_path: str | None = None,
) -> dict[str, Any]:
    preset = get_one_d_flame_preset(inputs.preset)
    return {
        "schema_version": 1,
        "case_type": "oneD-flame",
        "preset": preset.name,
        "preset_summary": preset.summary,
        "template": str(Path(inputs.template).resolve()),
        "output_dir": str(Path(output_dir).resolve()) if output_dir else None,
        "config_path": str(Path(config_path).resolve()) if config_path else None,
        "inputs": {
            **asdict(inputs),
            "oxidizer": resolve_oxidizer(inputs.oxidizer),
            "template": str(Path(inputs.template).resolve()),
        },
        "assumptions": preset.assumptions,
        "notes": preset.notes,
        "resolved": resolved,
    }


def dump_plan_json(plan: dict[str, Any], path: str | Path) -> Path:
    output_path = Path(path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def load_plan_json(path: str | Path) -> dict[str, Any]:
    input_path = Path(path).resolve()
    return json.loads(input_path.read_text(encoding="utf-8"))


def one_d_flame_inputs_from_plan(plan: dict[str, Any]) -> OneDFlameInitInputs:
    if plan.get("case_type") != "oneD-flame":
        raise ValueError(f"Unsupported case_type in config: {plan.get('case_type')}")

    inputs = plan["inputs"]
    return OneDFlameInitInputs(
        mechanism=inputs["mechanism"],
        fuel=inputs["fuel"],
        oxidizer=inputs["oxidizer"],
        eq_ratio=float(inputs["eq_ratio"]),
        T0=float(inputs["T0"]),
        p0=float(inputs["p0"]),
        preset=inputs.get("preset", plan.get("preset", DEFAULT_ONE_D_FLAME_PRESET)),
        template=inputs.get("template", str(DEFAULT_ONE_D_FLAME_TEMPLATE)),
        inert_specie=inputs.get("inert_specie", "N2"),
    )


def one_d_flame_overrides_from_plan(plan: dict[str, Any]) -> dict[str, Any]:
    overrides = dict(plan.get("resolved", {}))
    overrides.pop("mechanism", None)
    overrides.pop("fuel", None)
    overrides.pop("oxidizer", None)
    overrides.pop("eq_ratio", None)
    overrides.pop("T0", None)
    overrides.pop("p0", None)
    overrides.pop("preset", None)
    overrides.pop("template", None)
    return overrides
