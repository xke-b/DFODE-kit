from dfode_kit.cases import init as cases_init


def test_cases_init_exports_expected_symbols():
    assert callable(cases_init.resolve_oxidizer)
    assert cases_init.DEFAULT_ONE_D_FLAME_PRESET == "premixed-defaults-v1"
