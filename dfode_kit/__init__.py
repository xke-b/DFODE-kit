import os
from importlib import import_module
from pathlib import Path


DFODE_ROOT = Path(__file__).resolve().parent.parent
os.environ["DFODE_ROOT"] = str(DFODE_ROOT)

__all__ = [
    "DFODE_ROOT",
    "read_openfoam_scalar",
    "BCT",
    "inverse_BCT",
    "BCT_torch",
    "inverse_BCT_torch",
    "gather_species_arrays",
    "df_to_h5",
    "touch_h5",
    "get_TPY_from_h5",
    "advance_reactor",
    "load_model",
    "predict_Y",
    "nn_integrate",
    "integrate_h5",
]

_ATTRIBUTE_MODULES = {
    "read_openfoam_scalar": ("dfode_kit.utils", "read_openfoam_scalar"),
    "BCT": ("dfode_kit.utils", "BCT"),
    "inverse_BCT": ("dfode_kit.utils", "inverse_BCT"),
    "BCT_torch": ("dfode_kit.utils", "BCT_torch"),
    "inverse_BCT_torch": ("dfode_kit.utils", "inverse_BCT_torch"),
    "gather_species_arrays": ("dfode_kit.cases.sampling", "gather_species_arrays"),
    "df_to_h5": ("dfode_kit.cases.sampling", "df_to_h5"),
    "touch_h5": ("dfode_kit.data.io_hdf5", "touch_h5"),
    "get_TPY_from_h5": ("dfode_kit.data.io_hdf5", "get_TPY_from_h5"),
    "advance_reactor": ("dfode_kit.data.integration", "advance_reactor"),
    "load_model": ("dfode_kit.data.integration", "load_model"),
    "predict_Y": ("dfode_kit.data.integration", "predict_Y"),
    "nn_integrate": ("dfode_kit.data.integration", "nn_integrate"),
    "integrate_h5": ("dfode_kit.data.integration", "integrate_h5"),
}


def __getattr__(name):
    if name not in _ATTRIBUTE_MODULES:
        raise AttributeError(f"module 'dfode_kit' has no attribute '{name}'")

    module_name, attribute_name = _ATTRIBUTE_MODULES[name]
    module = import_module(module_name)
    value = getattr(module, attribute_name)
    globals()[name] = value
    return value
