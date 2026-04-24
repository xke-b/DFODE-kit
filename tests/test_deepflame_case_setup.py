from pathlib import Path
from types import SimpleNamespace

from dfode_kit.cases.deepflame import update_one_d_sample_config


class DummyGas:
    def __init__(self, T, Y):
        self.T = T
        self.Y = Y


def test_update_one_d_sample_config_does_not_overwrite_sim_time_step_with_sim_time(tmp_path):
    case_path = tmp_path / 'case'
    system_path = case_path / 'system'
    system_path.mkdir(parents=True)
    (system_path / 'sampleConfigDict.orig').write_text(
        """simTimeStep             placeHolder;\n"
        "simTime                 placeHolder;\n"
        "simWriteInterval        placeHolder;\n"
        "unburntStates           placeHolder;\n"
        "equilibriumStates       placeHolder;\n"
        """,
        encoding='utf-8',
    )

    cfg = SimpleNamespace(
        mech_path=Path('/tmp/mech.yaml'),
        inert_specie='N2',
        domain_width=1.0,
        domain_length=2.0,
        ignition_region=0.5,
        sim_time_step=1e-6,
        sim_time=3.7e-3,
        sim_write_interval=1e-4,
        inlet_speed=0.7,
        p0=101325.0,
        initial_gas=DummyGas(300.0, [0.2, 0.8]),
        burnt_gas=DummyGas(2200.0, [0.1, 0.9]),
        species_names=['O2', 'N2'],
    )

    update_one_d_sample_config(cfg, case_path)
    text = (system_path / 'sampleConfigDict').read_text(encoding='utf-8')

    assert 'simTimeStep             1e-06;' in text
    assert 'simTime                 0.0037;' in text
