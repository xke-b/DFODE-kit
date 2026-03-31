import importlib


def test_h5_kit_shim_reexports_io_helpers():
    legacy_h5_kit = importlib.import_module("dfode_kit.data_operations.h5_kit")
    canonical_io = importlib.import_module("dfode_kit.data.io_hdf5")

    assert legacy_h5_kit.touch_h5 is canonical_io.touch_h5
    assert legacy_h5_kit.get_TPY_from_h5 is canonical_io.get_TPY_from_h5


def test_data_operations_package_reexports_canonical_io_helpers():
    legacy_data_ops = importlib.import_module("dfode_kit.data_operations")
    canonical_io = importlib.import_module("dfode_kit.data.io_hdf5")

    assert legacy_data_ops.touch_h5 is canonical_io.touch_h5
    assert legacy_data_ops.get_TPY_from_h5 is canonical_io.get_TPY_from_h5
