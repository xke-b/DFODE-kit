from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import types

import numpy as np
import pytest


sys.modules.setdefault("torch", types.ModuleType("torch"))

UTILS_PATH = Path(__file__).resolve().parents[1] / "dfode_kit" / "utils.py"
SPEC = spec_from_file_location("dfode_utils_module", UTILS_PATH)
utils = module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(utils)


def test_bct_roundtrip_preserves_positive_values():
    arr = np.array([[1e-6, 0.1, 0.9], [0.2, 0.3, 0.5]], dtype=float)
    transformed = utils.BCT(arr)
    restored = utils.inverse_BCT(transformed)
    assert np.allclose(restored, arr)


def test_bct_rejects_negative_values():
    arr = np.array([[0.1, -0.2, 0.3]], dtype=float)
    with pytest.raises(ValueError):
        utils.BCT(arr)


def test_read_openfoam_scalar_uniform(tmp_path):
    content = """FoamFile
{
    version 2.0;
}
internalField   uniform 300;
"""
    path = tmp_path / "T"
    path.write_text(content)

    result = utils.read_openfoam_scalar(path)
    assert result == 300.0


def test_read_openfoam_scalar_nonuniform(tmp_path):
    content = """FoamFile
{
    version 2.0;
}
internalField   nonuniform List<scalar>
3
(
1.0
2.0
3.0
)
;
"""
    path = tmp_path / "YH2"
    path.write_text(content)

    result = utils.read_openfoam_scalar(path)
    assert result.shape == (3, 1)
    assert np.allclose(result[:, 0], [1.0, 2.0, 3.0])
