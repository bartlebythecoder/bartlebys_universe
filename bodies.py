from dataclasses import dataclass
import random
import logging
import math

import generic_functions as gf
import database_utils as du
import lookup_tables as lu

UNDEFINED_VALUE = -99
UNDEFINED_CATEGORY = 'XX'


@dataclass
class DiceRoll:
    location: str
    number: int
    reason: str
    dice_result: float
    table_result: str


@dataclass
class Parameters:
    db_name: str
    build: int
    frequency: int  # for checking if system is present
    random_seed: int


@dataclass
class World:
    db_name: str
    location: str
    orbit_slot: str
    star_designation: str
    orbit_number: float
    world_type: str

