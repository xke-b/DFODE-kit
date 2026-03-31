from importlib import import_module


__all__ = [
    'df_to_h5',
    'OneDFreelyPropagatingFlameConfig',
    'setup_one_d_flame_case',
]

_ATTRIBUTE_MODULES = {
    'df_to_h5': ('dfode_kit.cases.sampling', 'df_to_h5'),
    'OneDFreelyPropagatingFlameConfig': (
        'dfode_kit.cases.presets',
        'OneDFreelyPropagatingFlameConfig',
    ),
    'setup_one_d_flame_case': (
        'dfode_kit.cases.deepflame',
        'setup_one_d_flame_case',
    ),
}


def __getattr__(name):
    if name not in _ATTRIBUTE_MODULES:
        raise AttributeError(f"module 'dfode_kit.df_interface' has no attribute '{name}'")

    module_name, attribute_name = _ATTRIBUTE_MODULES[name]
    module = import_module(module_name)
    value = getattr(module, attribute_name)
    globals()[name] = value
    return value
