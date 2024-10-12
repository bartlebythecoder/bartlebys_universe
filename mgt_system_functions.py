import logging
import copy

import generic_functions as gf
import database_utils as du
import lookup_tables as lu
import mgt_stellar_objects as mgt_star
import mgt_system_objects as mgt_system
from bodies import Parameters, DiceRoll

def build_system_details(parms):
    location_list = du.get_locations(parms.db_name)
    du.create_system_details_table(parms.db_name)
    for each_location in location_list:
        dy_list = du.get_star_list(parms.db_name, each_location)
        star_list = mgt_star.get_star_list_from_dy_list(parms, dy_list)
        new_system = mgt_system.System(parms, each_location)
        du.insert_system_details(new_system)


