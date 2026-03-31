import importlib


def test_data_package_exports_augment_and_label_helpers():
    data_pkg = importlib.import_module("dfode_kit.data")
    augment_module = importlib.import_module("dfode_kit.data.augment")
    label_module = importlib.import_module("dfode_kit.data.label")

    assert data_pkg.random_perturb is augment_module.random_perturb
    assert data_pkg.label_npy is label_module.label_npy
