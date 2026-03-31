import importlib


def test_data_integration_module_exports_expected_helpers():
    integration = importlib.import_module("dfode_kit.data.integration")
    canonical_io = importlib.import_module("dfode_kit.data.io_hdf5")

    assert callable(integration.advance_reactor)
    assert callable(integration.integrate_h5)
    assert callable(integration.calculate_error)
    assert callable(canonical_io.touch_h5)
    assert callable(canonical_io.get_TPY_from_h5)
