from importlib import import_module


__all__ = [
    'AIR_OXIDIZER',
    'DEFAULT_ONE_D_FLAME_PRESET',
    'DEFAULT_ONE_D_FLAME_TEMPLATE',
    'ONE_D_FLAME_PRESETS',
    'OneDFlameInitInputs',
    'OneDFlamePreset',
    'OneDFreelyPropagatingFlameConfig',
    'df_to_h5',
    'dump_plan_json',
    'gather_species_arrays',
    'get_one_d_flame_preset',
    'load_plan_json',
    'one_d_flame_inputs_from_plan',
    'one_d_flame_overrides_from_plan',
    'one_d_flame_plan_dict',
    'resolve_oxidizer',
    'setup_one_d_flame_case',
]

_ATTRIBUTE_MODULES = {
    'AIR_OXIDIZER': ('dfode_kit.cases.init', 'AIR_OXIDIZER'),
    'DEFAULT_ONE_D_FLAME_PRESET': ('dfode_kit.cases.init', 'DEFAULT_ONE_D_FLAME_PRESET'),
    'DEFAULT_ONE_D_FLAME_TEMPLATE': ('dfode_kit.cases.init', 'DEFAULT_ONE_D_FLAME_TEMPLATE'),
    'ONE_D_FLAME_PRESETS': ('dfode_kit.cases.init', 'ONE_D_FLAME_PRESETS'),
    'OneDFlameInitInputs': ('dfode_kit.cases.init', 'OneDFlameInitInputs'),
    'OneDFlamePreset': ('dfode_kit.cases.init', 'OneDFlamePreset'),
    'OneDFreelyPropagatingFlameConfig': (
        'dfode_kit.cases.presets',
        'OneDFreelyPropagatingFlameConfig',
    ),
    'df_to_h5': ('dfode_kit.cases.sampling', 'df_to_h5'),
    'dump_plan_json': ('dfode_kit.cases.init', 'dump_plan_json'),
    'gather_species_arrays': ('dfode_kit.cases.sampling', 'gather_species_arrays'),
    'get_one_d_flame_preset': ('dfode_kit.cases.init', 'get_one_d_flame_preset'),
    'load_plan_json': ('dfode_kit.cases.init', 'load_plan_json'),
    'one_d_flame_inputs_from_plan': ('dfode_kit.cases.init', 'one_d_flame_inputs_from_plan'),
    'one_d_flame_overrides_from_plan': ('dfode_kit.cases.init', 'one_d_flame_overrides_from_plan'),
    'one_d_flame_plan_dict': ('dfode_kit.cases.init', 'one_d_flame_plan_dict'),
    'resolve_oxidizer': ('dfode_kit.cases.init', 'resolve_oxidizer'),
    'setup_one_d_flame_case': ('dfode_kit.cases.deepflame', 'setup_one_d_flame_case'),
}


def __getattr__(name):
    if name not in _ATTRIBUTE_MODULES:
        raise AttributeError(f"module 'dfode_kit.cases' has no attribute '{name}'")

    module_name, attribute_name = _ATTRIBUTE_MODULES[name]
    module = import_module(module_name)
    value = getattr(module, attribute_name)
    globals()[name] = value
    return value
