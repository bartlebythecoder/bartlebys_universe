import logging
import math
import copy
import sqlite3

import generic_functions as gf
import database_utils as du
import lookup_tables as lu
import mgt_stellar_objects as mgt_star
import mgt_system_objects as mso
import mgt_system_functions as msf
from bodies import Parameters, DiceRoll


def get_worlds_per_star_dy_first_calculation(star_list: list, system: mso.System):

    def calc_raw_result(system_worlds, star_orbits, system_orbits):
        logging.info(f'Calculating worlds per star: {system_worlds}, {star_orbits}, {system_orbits}')
        try:
            return system_worlds * star_orbits / system_orbits
        except:
            return 0

    result_dy = {}
    for each_star in star_list:
        if each_star.orbit_class == 'primary':
            total_worlds_this_star = calc_raw_result(system.total_number_of_worlds, each_star.total_star_orbits,
                                                     system.total_system_orbits)
            total_worlds_this_star = math.ceil(total_worlds_this_star)
            result_dy[each_star.orbit_class] = total_worlds_this_star
            logging.info(f'{system.location} {each_star.orbit_class} world total = {result_dy[each_star.orbit_class]}')
        elif each_star.orbit_class in ['near', 'close', 'far']:
            total_worlds_this_star = calc_raw_result(system.total_number_of_worlds, each_star.total_star_orbits,
                                                     system.total_system_orbits)
            total_worlds_this_star = math.floor(total_worlds_this_star)
            result_dy[each_star.orbit_class] = total_worlds_this_star
            logging.info(f'{system.location} {each_star.orbit_class} world total = '
                         f'{result_dy[each_star.orbit_class]}')
        elif each_star.orbit_class == 'companion':
            logging.info('No worlds for companion')
        else:
            logging.info('*****************ERROR in worlds per star function')

    return result_dy


def update_dy_with_remaining_worlds(worlds_per_star_dy: dict, system: mso.System):
    worlds_allocated = sum(worlds_per_star_dy.values())
    worlds_missing = system.total_number_of_worlds - worlds_allocated
    if worlds_missing > 0:
        for last_star in ('far', 'near', 'close'):
            if last_star in worlds_per_star_dy:
                worlds_per_star_dy[last_star] += worlds_missing
                logging.info(f'{last_star} updated to {worlds_per_star_dy[last_star]}')
                return worlds_per_star_dy

        logging.info('***************ERROR in world per star allocation - worlds missing > 0')
        return {}
    elif worlds_missing == 0:
        return worlds_per_star_dy  # No changes needed if worlds_missing is not positive

    else:
        logging.info('***************ERROR in world per star allocation - worlds missing < 0')
        return {}


def get_worlds_per_star_dy(star_list: list, system: mso):
    worlds_per_star_dy = get_worlds_per_star_dy_first_calculation(star_list, system)
    worlds_per_star_dy = update_dy_with_remaining_worlds(worlds_per_star_dy, system)
    return worlds_per_star_dy


def update_worlds_per_star_with_empty_orbits(worlds_dy, empty_orbits):
    if empty_orbits < 1:
        return worlds_dy
    else:
        if 'close' in worlds_dy:
            worlds_dy['close'] += 1
            empty_orbits -= 1
            logging.info('Empty orbit added to close secondary')

        if 'near' in worlds_dy and empty_orbits > 0:
            worlds_dy['near'] += 1
            empty_orbits -= 1
            logging.info('Empty orbit added to near secondary')

        if 'far' in worlds_dy and empty_orbits > 0:
            worlds_dy['far'] += 1
            empty_orbits -= 1
            logging.info('Empty orbit added to far secondary')

        if 'primary' in worlds_dy and empty_orbits > 0:
            worlds_dy['primary'] += empty_orbits
            logging.info(f' {empty_orbits} empty orbit(s) added to primary')

    return worlds_dy

def assign_worlds(worlds_per_star_dy):
    return_list = []
    for key in worlds_per_star_dy:
        pass

def build_world_details(parms: Parameters):
    location_list = du.get_locations(parms.db_name)
    du.create_world_details_table(parms.db_name)
    for each_location in location_list:
        logging.info(f'Location: {each_location}')
        dy_list = du.get_star_list(parms.db_name, each_location)  # SELECT results into dy
        star_list = mgt_star.get_star_list_from_dy_list(parms, dy_list)  # Converts dy list to object list
        logging.info(f'Star Object: {star_list}')
        system = msf.populate_system_from_db(parms, each_location)  # SELECT directly into System object

        worlds_per_star_dy = get_worlds_per_star_dy(star_list, system)  # New dict with # worlds per star
        system.get_baseline_orbit_number(star_list)
        logging.info(f'Original baseline orbit:  {system.baseline_orbit_number}')
        system.update_baseline_orbit_number(star_list[0], worlds_per_star_dy['primary'])
        logging.info(f'Updated baseline orbit:  {system.baseline_orbit_number}')

        worlds_per_star_dy = update_worlds_per_star_with_empty_orbits(worlds_per_star_dy, system.empty_orbits)

        system.get_orbit_spread(star_list)
        logging.info(f'Orbit Spread: {system.orbit_spread}')

        world_list = assign_worlds(worlds_per_star_dy)

        du.update_orbit_details_in_system(parms, system)


