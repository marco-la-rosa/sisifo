import pytest

import calculations


def test_moles_from_mass():
    assert calculations.moles_from_mass(2.00, 138.12) == pytest.approx(0.01448, rel=1e-4)


def test_moles_from_volume():
    assert calculations.moles_from_volume(2.00, 1.08, 102.09) == pytest.approx(0.021158, rel=1e-4)


def test_moles_from_eq():
    assert calculations.moles_from_eq(0.01448, 1.5) == pytest.approx(0.02172, rel=1e-4)


def test_mass_from_moles():
    assert calculations.mass_from_moles(0.02172, 102.09) == pytest.approx(2.2174, rel=1e-4)


def test_volume_from_mass():
    assert calculations.volume_from_mass(2.2174, 1.08) == pytest.approx(2.0531, rel=1e-4)
