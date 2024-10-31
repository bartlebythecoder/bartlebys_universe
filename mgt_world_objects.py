from dataclasses import dataclass
import logging
import math
import mgt_system_objects as mgt_system
import mgt_stellar_objects as mgt_star
import generic_functions as gf
import database_utils as du
import lookup_tables as lu
from bodies import Parameters, DiceRoll

@dataclass
class World:
    db_name: str
    location: str
    orbit_slot: int
    size: int
    size_code: str
    number_of_moons: int
