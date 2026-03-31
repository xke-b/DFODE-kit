from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


APP_NAME = "dfode-kit"
CONFIG_FILENAME = "config.json"

CONFIG_KEYS: dict[str, str] = {
    "openfoam_bashrc": "Path to the OpenFOAM bashrc that should be sourced first.",
    "conda_sh": "Path to conda.sh used to activate a Conda environment before sourcing DeepFlame.",
    "conda_env_name": "Conda environment name used for Cantera/DeepFlame-compatible Python packages.",
    "deepflame_bashrc": "Path to the DeepFlame bashrc sourced after OpenFOAM and Conda activation.",
    "python_executable": "Optional Python executable path for future workflow commands and diagnostics.",
    "default_np": "Default MPI rank count for case execution commands.",
    "mpirun_command": "MPI launcher command used by case execution workflows.",
}

DEFAULT_CONFIG: dict[str, Any] = {
    "openfoam_bashrc": None,
    "conda_sh": None,
    "conda_env_name": None,
    "deepflame_bashrc": None,
    "python_executable": None,
    "default_np": 4,
    "mpirun_command": "mpirun",
}


def get_config_dir() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg).expanduser().resolve() / APP_NAME
    return Path.home().resolve() / ".config" / APP_NAME


def get_config_path() -> Path:
    return get_config_dir() / CONFIG_FILENAME


def load_runtime_config() -> dict[str, Any]:
    path = get_config_path()
    config = dict(DEFAULT_CONFIG)
    if path.is_file():
        loaded = json.loads(path.read_text(encoding="utf-8"))
        config.update(loaded)
    return config


def save_runtime_config(config: dict[str, Any]) -> Path:
    path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def validate_config_key(key: str) -> str:
    if key not in CONFIG_KEYS:
        raise ValueError(
            f"Unknown config key: {key}. Available keys: {', '.join(sorted(CONFIG_KEYS))}"
        )
    return key


def coerce_config_value(key: str, value: str) -> Any:
    if key == "default_np":
        return int(value)
    return value


def set_config_value(key: str, value: str) -> tuple[dict[str, Any], Path]:
    validate_config_key(key)
    config = load_runtime_config()
    config[key] = coerce_config_value(key, value)
    return config, save_runtime_config(config)


def unset_config_value(key: str) -> tuple[dict[str, Any], Path]:
    validate_config_key(key)
    config = load_runtime_config()
    config[key] = DEFAULT_CONFIG[key]
    return config, save_runtime_config(config)


def describe_config_schema() -> dict[str, dict[str, Any]]:
    return {
        key: {
            "description": CONFIG_KEYS[key],
            "default": DEFAULT_CONFIG[key],
        }
        for key in sorted(CONFIG_KEYS)
    }


def resolve_runtime_config(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    config = load_runtime_config()
    for key, value in (overrides or {}).items():
        if value is not None:
            validate_config_key(key)
            config[key] = value
    return config
