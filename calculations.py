def moles_from_mass(mass_g: float, mw: float) -> float:
    """calculates moles (mol) from mass in grams and molecular weight in g/mol"""
    return mass_g / mw


def moles_from_volume(volume_ml: float, density_g_ml: float, mw: float) -> float:
    """calculates moles (mol) from volume in mL, density in g/mL and molecular weight in g/mol"""
    return moles_from_mass(volume_ml * density_g_ml, mw)
