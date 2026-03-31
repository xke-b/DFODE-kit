from importlib import import_module


__all__ = [
    "touch_h5",
    "get_TPY_from_h5",
    "integrate_h5",
    "load_model",
    "nn_integrate",
    "predict_Y",
    "calculate_error",
    "random_perturb",
    "label_npy",
    "SCALAR_FIELDS_GROUP",
    "MECHANISM_ATTR",
    "read_scalar_field_datasets",
    "stack_scalar_field_datasets",
    "require_h5_attr",
    "require_h5_group",
]

_ATTRIBUTE_MODULES = {
    "touch_h5": ("dfode_kit.data.io_hdf5", "touch_h5"),
    "get_TPY_from_h5": ("dfode_kit.data.io_hdf5", "get_TPY_from_h5"),
    "integrate_h5": ("dfode_kit.data_operations.h5_kit", "integrate_h5"),
    "load_model": ("dfode_kit.data_operations.h5_kit", "load_model"),
    "nn_integrate": ("dfode_kit.data_operations.h5_kit", "nn_integrate"),
    "predict_Y": ("dfode_kit.data_operations.h5_kit", "predict_Y"),
    "calculate_error": ("dfode_kit.data_operations.h5_kit", "calculate_error"),
    "random_perturb": ("dfode_kit.data_operations.augment_data", "random_perturb"),
    "label_npy": ("dfode_kit.data_operations.label_data", "label_npy"),
    "SCALAR_FIELDS_GROUP": ("dfode_kit.data.contracts", "SCALAR_FIELDS_GROUP"),
    "MECHANISM_ATTR": ("dfode_kit.data.contracts", "MECHANISM_ATTR"),
    "read_scalar_field_datasets": ("dfode_kit.data.contracts", "read_scalar_field_datasets"),
    "stack_scalar_field_datasets": ("dfode_kit.data.contracts", "stack_scalar_field_datasets"),
    "require_h5_attr": ("dfode_kit.data.contracts", "require_h5_attr"),
    "require_h5_group": ("dfode_kit.data.contracts", "require_h5_group"),
}


def __getattr__(name):
    if name not in _ATTRIBUTE_MODULES:
        raise AttributeError(f"module 'dfode_kit.data_operations' has no attribute '{name}'")

    module_name, attribute_name = _ATTRIBUTE_MODULES[name]
    module = import_module(module_name)
    value = getattr(module, attribute_name)
    globals()[name] = value
    return value
