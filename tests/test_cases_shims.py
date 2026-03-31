from dfode_kit.cases import init as cases_init
from dfode_kit.df_interface import case_init as legacy_case_init


def test_df_interface_case_init_reexports_cases_symbols():
    assert legacy_case_init.resolve_oxidizer is cases_init.resolve_oxidizer
    assert legacy_case_init.DEFAULT_ONE_D_FLAME_PRESET == cases_init.DEFAULT_ONE_D_FLAME_PRESET
