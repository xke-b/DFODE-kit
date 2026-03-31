from importlib import import_module


__all__ = [
    "SCALAR_FIELDS_GROUP",
    "MECHANISM_ATTR",
    "read_scalar_field_datasets",
    "stack_scalar_field_datasets",
    "require_h5_attr",
    "require_h5_group",
    "touch_h5",
    "get_TPY_from_h5",
]

_ATTRIBUTE_MODULES = {
    "SCALAR_FIELDS_GROUP": ("dfode_kit.data.contracts", "SCALAR_FIELDS_GROUP"),
    "MECHANISM_ATTR": ("dfode_kit.data.contracts", "MECHANISM_ATTR"),
    "read_scalar_field_datasets": ("dfode_kit.data.contracts", "read_scalar_field_datasets"),
    "stack_scalar_field_datasets": ("dfode_kit.data.contracts", "stack_scalar_field_datasets"),
    "require_h5_attr": ("dfode_kit.data.contracts", "require_h5_attr"),
    "require_h5_group": ("dfode_kit.data.contracts", "require_h5_group"),
    "touch_h5": ("dfode_kit.data.io_hdf5", "touch_h5"),
    "get_TPY_from_h5": ("dfode_kit.data.io_hdf5", "get_TPY_from_h5"),
}


def __getattr__(name):
    if name not in _ATTRIBUTE_MODULES:
        raise AttributeError(f"module 'dfode_kit.data' has no attribute '{name}'")

    module_name, attribute_name = _ATTRIBUTE_MODULES[name]
    module = import_module(module_name)
    value = getattr(module, attribute_name)
    globals()[name] = value
    return value
