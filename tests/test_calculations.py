import pytest

import calculations


def test_moles_from_mass():
    assert calculations.moles_from_mass(2.00, 138.12) == pytest.approx(0.01448, rel=1e-4)


def test_moles_from_volume():
    assert calculations.moles_from_volume(2.00, 1.08, 102.09) == pytest.approx(0.021158, rel=1e-4)
