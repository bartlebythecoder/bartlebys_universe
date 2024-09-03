from dataclasses import dataclass


@dataclass
class Star:
    db_name: str
    build: int
    location: str
    subsector: str
    multiplicity: int  # Assuming 0 for single, 1 for primary, 2 for secondary, etc.
    orbit_class: str
    orbit_number: int
    star_type: str
    star_subtype: int
    star_mass: int
    star_temperature: int
    star_diameter: int
    star_luminosity: int
    system_age: int
    gas_giants: int
    planetoid_belts: int
    terrestrial_planets: int
    minimal_orbit_number: int
    habitable_zone_center: int


@dataclass
class DiceRoll:
    location: str
    number: int
    reason: str
    dice_result: int
    table_result: str

