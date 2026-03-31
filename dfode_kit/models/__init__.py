"""Model architectures and registry helpers."""

from importlib import import_module


__all__ = [
    "MLP",
    "build_mlp",
    "create_model",
    "get_model_factory",
    "register_model",
    "registered_models",
]

_ATTRIBUTE_MODULES = {
    "MLP": ("dfode_kit.models.mlp", "MLP"),
    "build_mlp": ("dfode_kit.models.mlp", "build_mlp"),
    "create_model": ("dfode_kit.models.registry", "create_model"),
    "get_model_factory": ("dfode_kit.models.registry", "get_model_factory"),
    "register_model": ("dfode_kit.models.registry", "register_model"),
    "registered_models": ("dfode_kit.models.registry", "registered_models"),
}


def __getattr__(name):
    if name not in _ATTRIBUTE_MODULES:
        raise AttributeError(f"module 'dfode_kit.models' has no attribute '{name}'")

    module_name, attribute_name = _ATTRIBUTE_MODULES[name]
    module = import_module(module_name)
    value = getattr(module, attribute_name)
    globals()[name] = value
    return value
