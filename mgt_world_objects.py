from dataclasses import dataclass
import random
import logging
import math

import generic_functions as gf
import database_utils as du
import lookup_tables as lu
from bodies import Parameters, DiceRoll

@dataclass
class World:
    db_name: str
    location: str
    orbit_slot: int
    star_designation: str
    orbit_number: float
    world_type: str


