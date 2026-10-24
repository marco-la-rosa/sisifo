def moles_from_mass(mass_g: float, mw: float) -> float:
    """calculates moles (mol) from mass in grams and molecular weight in g/mol"""
    return mass_g / mw


def moles_from_volume(volume_ml: float, density_g_ml: float, mw: float) -> float:
    """calculates moles (mol) from volume in mL, density in g/mL and molecular weight in g/mol"""
    return moles_from_mass(volume_ml * density_g_ml, mw)


def moles_from_eq(moles_limiting_reagent: float, eq: float) -> float:
    """calculates moles (mol) of reagent from the eq of the reagent and the moles of the limiting reagent"""
    return moles_limiting_reagent * eq


def mass_from_moles(moles: float, mw: float) -> float:
    """calculates mass in g from moles (mol) and molecular weight in g/mol"""
    return moles * mw


def volume_from_mass(mass_g: float, density_g_ml: float) -> float:
    """calculates mL from the mass in g and the density in g/mL"""
    return mass_g / density_g_ml


def yield_percent(
    mass_product_g: float,
    mw: float,
    moles_limiting_reagent: float,
    limiting_coefficient: float = 1,
    product_coefficient: float = 1,
) -> float:
    """
    calculates yield percentage from the mass of the product in g, the molecular weight of the product in g/mol,
    the moles (mol) of the limiting reagent and the limiting coefficient and product coefficient,
    taken from the balanced equation (e.g. 2 A -> B: limiting 2, product 1),
    both equal to 1 if not specified
    """
    theoretical_moles = moles_limiting_reagent * product_coefficient / limiting_coefficient
    return moles_from_mass(mass_product_g, mw) / theoretical_moles * 100
