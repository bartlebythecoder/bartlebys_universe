import logging
import math
import random

import database_utils as du
import mgt_stellar_objects as mgt_star
import mgt_system_objects as mso
import mgt_system_functions as msf
import mgt_world_objects as mwo
import generic_functions as gf
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
                logging.info(f'{last_star} updated to {worlds_per_star_dy[last_star]} due to unallocated planets')
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


def assign_and_remove(my_list):
    """ Assigns a random value from the list and then removes it."""
    chosen_value = random.choice(my_list)
    my_list.remove(chosen_value)
    return chosen_value


def assign_worlds(worlds_per_star_dy, system):
    total_slots = sum(worlds_per_star_dy.values())
    logging.info(f'Total system orbits including empty orbits: {total_slots}')
    world_dy = {}
    key_list = list(range(1, total_slots + 1))
    for each_empty_orbit in range(0, system.empty_orbits):
        new_key = assign_and_remove(key_list)
        world_dy[new_key] = 'empty'

    for each_gas_giant in range(0, system.number_of_gas_giants):
        new_key = assign_and_remove(key_list)
        world_dy[new_key] = 'gas giant'

    for each_belt in range(0, system.number_of_planetoid_belts):
        new_key = assign_and_remove(key_list)
        world_dy[new_key] = 'belt'

    for each_planet in range(0,system.number_of_terrestrial_planets):
        new_key = assign_and_remove(key_list)
        world_dy[new_key] = 'planet'

    if key_list:
        logging.info(f'##############ERROR - key list still has properties {key_list}')

    return world_dy


def get_star_from_star_list(star_list, orbit_class):
    for each_star in star_list:
        if each_star.orbit_class == orbit_class:
            return each_star
    return None

def check_restricted_orbits(star: mgt_star.Star, orbit_number: float):
    new_orbit_number = orbit_number

    if (star.restricted_close_orbit_start and
            gf.is_between(orbit_number, star.restricted_close_orbit_start, star.restricted_close_orbit_end)):
        close_restriction = star.restricted_close_orbit_end - star.restricted_close_orbit_start
        new_orbit_number += close_restriction

    if (star.restricted_near_orbit_start and
            gf.is_between(orbit_number, star.restricted_near_orbit_start, star.restricted_near_orbit_end)):
        near_restriction = star.restricted_near_orbit_end - star.restricted_near_orbit_start
        new_orbit_number += near_restriction

    if (star.restricted_far_orbit_start and
            gf.is_between(orbit_number, star.restricted_far_orbit_start, star.restricted_far_orbit_end)):
        far_restriction = star.restricted_far_orbit_end - star.restricted_far_orbit_start
        new_orbit_number += far_restriction

    return new_orbit_number


def get_orbit_number(current_star: mgt_star.Star, previous_star: mgt_star.Star,
                     previous_orbits: int, system: mso.System):
    if (not previous_star) or (current_star.orbit_class != previous_star.orbit_class):
        orbit_number = current_star.minimum_allowable_orbit_number
        logging.info(f'New star orbit begins at {orbit_number}')
    else:
        orbit_number = previous_orbits + system.orbit_spread
        logging.info(f'Adding orbit at {orbit_number} {previous_star.orbit_class} {current_star.orbit_class}')
    orbit_number = check_restricted_orbits(current_star, orbit_number)
    return orbit_number





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

        system.get_orbit_spread(star_list, worlds_per_star_dy)
        logging.info(f'Orbit Spread: {system.orbit_spread}')

        world_dy = assign_worlds(worlds_per_star_dy, system)

        current_slot = 1
        previous_star = None
        previous_orbits = 0

        for each_star in star_list:

            if each_star.orbit_class in worlds_per_star_dy:

                number_of_worlds_per_star = worlds_per_star_dy[each_star.orbit_class] + current_slot

                for each_world in range(current_slot, number_of_worlds_per_star):
                    logging.info(f' Star: {each_star.orbit_class} Slot: {each_world} {world_dy[each_world]}')

                    current_star = get_star_from_star_list(star_list, each_star.orbit_class)

                    if current_star:
                        orbit_number = get_orbit_number(current_star, previous_star, previous_orbits, system)
                    else:
                        orbit_number = -1



                    world = mwo.World(
                        db_name=parms.db_name,
                        location=system.location,
                        orbit_slot=current_slot,
                        star_orbit_class=each_star.orbit_class,
                        orbit_number=orbit_number,
                        orbit_au = -1,
                        world_type=world_dy[each_world],
                        stars_orbited=-1,
                        stars_orbited_mass=-1,
                        orbit_eccentricity=0
                    )
                    world.get_stars_orbited(each_star, star_list)
                    world.get_au_from_orbit_number()

                    previous_star = current_star
                    previous_orbits = orbit_number

                    world.get_orbit_eccentricity()
                    du.insert_world_details(world)
                    current_slot += 1

        du.update_orbit_details_in_system(parms, system)


