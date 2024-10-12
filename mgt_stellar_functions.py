import logging
import copy

import generic_functions as gf
import database_utils as du
import lookup_tables as lu
import mgt_stellar_objects as mgt_star
from bodies import Parameters, DiceRoll


def log_star(star: mgt_star.Star):
    logging.info(
        f'{star.location}, {star.star_class} {star.star_type}{star.star_subtype} '
        f'Mass: {star.star_mass}, Temp: {star.star_temperature}, Di: {star.star_diameter},'
        f'Lum: {star.star_luminosity:.3g}, Age: {star.star_age} ')


def system_present(parms: Parameters, location: str):
    # returns a True or False if a system is present based on the frequency provided
    dice = gf.roll_dice(1)
    dice_info = DiceRoll
    dice_info.location = location
    dice_info.number = 1
    dice_info.reason = 'system present'
    dice_info.dice_result = dice
    if dice <= parms.frequency:
        dice_info.table_result = True
    else:
        dice_info.table_result = False

    du.insert_dice_rolls(parms.db_name, dice_info)

    return DiceRoll.table_result


def get_multiple_star_die_mod(star: mgt_star.Star):
    die_mod = 0
    if star.star_class in ['Ia', 'Ib', 'II', 'III', 'IV']:
        die_mod = 1
    elif star.star_class in ['V', 'VI']:
        if star.star_type in ['O', 'B', 'A', 'F']:
            die_mod = 1
        elif star.star_type == 'M':
            die_mod = -1

    return die_mod


def check_multiple_star(star: mgt_star.Star):
    # Returns True or False if an extra star is present attached to provided star
    # Used for checking secondary or companion stars

    die_mod = get_multiple_star_die_mod(star)
    total_dice = 2
    dice = gf.roll_dice(total_dice) + die_mod
    dice_info = DiceRoll(star.location, total_dice, 'multiple star present', -99, 'unk')
    dice_info.dice_result = dice
    if dice >= 10:
        dice_info.table_result = True
    else:
        dice_info.table_result = False
    du.insert_dice_rolls(star.db_name, dice_info)
    return dice_info.table_result


def find_companion_category(star: mgt_star.Star):
    chart = lu.companion_star_category_dy
    die_mod = 0
    if star.star_class in ['III' or 'IV']:
        die_mod = -1

    dice = gf.roll_dice(2) + die_mod
    dice_info = DiceRoll
    dice_info.location = star.location
    dice_info.number = 2
    dice_info.reason = 'companion type'
    dice_info.dice_result = dice
    dice_info.table_result = lu.companion_star_category_dy[dice]
    du.insert_dice_rolls(star.db_name, dice_info)
    return dice_info.table_result


def find_secondary_category(star: mgt_star.Star):
    chart = lu.companion_star_category_dy
    die_mod = 0
    if star.star_class in ['III' or 'IV']:
        die_mod = -1

    dice = gf.roll_dice(2) + die_mod
    dice_info = DiceRoll
    dice_info.location = star.location
    dice_info.number = 2
    dice_info.reason = 'companion type'
    dice_info.dice_result = dice
    dice_info.table_result = lu.secondary_star_category_dy[dice]
    du.insert_dice_rolls(star.db_name, dice_info)
    return dice_info.table_result


def build_companion_star(main: mgt_star.Star, parms: Parameters):
    # Returns a companion star based on details of the star given (the main to the companion)
    companion_category = find_companion_category(main)

    logging.info(f'Companion found.  It is a {companion_category}')
    companion = copy.deepcopy(main)

    companion.designation += 'b'

    companion.star_class = main.star_class
    companion.get_non_primary_star_type(main, companion_category)
    companion.get_non_primary_star_subtype(main, companion_category)
    companion.fix_star_subtype_errors()
    companion.orbit_class = 'companion'
    companion.generation_type = companion_category

    companion.get_star_mass()
    companion.binary_mass = companion.star_mass

    companion.get_non_primary_star_age()

    companion.get_star_diameter()
    companion.get_star_temperature()
    companion.get_star_luminosity()
    companion.binary_luminosity = companion.star_luminosity

    companion.get_companion_orbit_number(main)
    companion.stars_orbited = 1
    companion.get_orbit_eccentricity()
    companion.get_orbit_au()
    companion.get_orbit_min()
    companion.get_orbit_max()
    companion.get_companion_orbit_period(main)
    companion.minimum_allowable_orbit_number = None
    companion.maximum_allowable_orbit_number = None

    companion.habitable_zone_center = 0
    companion.total_star_orbits = 0

    return companion


def build_secondary_star(main: mgt_star.Star, parms: Parameters, secondary_type, designation):
    # Returns a companion star based on details of the star given (the main to the companion)
    secondary_category = find_secondary_category(main)
    logging.info(f'Secondary found.')
    secondary = mgt_star.Star(parms, main.location)

    secondary.designation = designation
    secondary.star_class = main.star_class
    secondary.get_non_primary_star_type(main, secondary_category)
    secondary.get_non_primary_star_subtype(main, secondary_category)
    secondary.fix_star_subtype_errors()
    secondary.orbit_class = secondary_type
    secondary.generation_type = secondary_category

    secondary.get_star_mass()
    secondary.binary_mass = secondary.star_mass

    secondary.get_non_primary_star_age()

    secondary.get_star_diameter()
    secondary.get_star_temperature()
    secondary.get_star_luminosity()
    secondary.binary_luminosity = secondary.star_luminosity
    secondary.get_hzco()

    secondary.get_secondary_orbit_number()
    if main.designation == 'Aa':
        secondary.stars_orbited = 2
    else:
        secondary.stars_orbited = 1

    secondary.get_orbit_eccentricity()
    secondary.get_orbit_au()
    secondary.get_orbit_min()
    secondary.get_orbit_max()
    secondary.get_secondary_orbit_period(main)
    secondary.get_minimum_allowable_orbit_number()
    secondary.get_secondary_maximum_allowable_orbit_number()

    return secondary


def process_secondary_star_loop(primary_star: mgt_star.Star,
                                parms: Parameters):
    secondary_stars = []
    secondary_list = ['close', 'near', 'far']
    designation_list = ['B', 'C', 'D', 'X']
    designation_index = 0
    close_star = None
    near_star = None
    far_star = None
    for each_secondary in secondary_list:
        if check_multiple_star(primary_star):
            if not (each_secondary == 'close' and primary_star.star_class in ['Ia', 'Ib', 'II', 'III']):
                secondary_companion = None
                logging.info(f'{primary_star.location} {each_secondary} {designation_list[designation_index]} ')
                secondary = build_secondary_star(primary_star,
                                                 parms,
                                                 each_secondary,
                                                 designation_list[designation_index])

                secondary_stars.append(secondary)

                # remember stars for orbit constraint calculations
                if each_secondary == 'close':
                    close_star = secondary
                    primary_star.get_restricted_close_orbits(secondary)
                if each_secondary == 'near':
                    near_star = secondary
                    primary_star.get_restricted_near_orbits(secondary)
                if each_secondary == 'far':
                    far_star = secondary
                    primary_star.get_restricted_far_orbits(secondary)

                if check_multiple_star(secondary):
                    secondary_companion = build_companion_star(secondary, parms)
                    secondary_stars.append(secondary_companion)

                    log_star(secondary_companion)
                    secondary.update_from_companion(secondary_companion)  # updates binary mass and designation
                    secondary.get_minimum_allowable_orbit_number_with_companion(primary_star, secondary_companion)

                designation_index += 1

            else:
                logging.info(f"Failed secondary {each_secondary} {primary_star.star_class}")

    if secondary_stars:
        secondary_stars = mgt_star.add_secondary_orbit_constraints(secondary_stars)

    return secondary_stars


def build_primary_star(parms, location):
    companion_star = None
    primary_star = mgt_star.Star(parms, location)
    log_star(primary_star)
    if check_multiple_star(primary_star):
        companion_star = build_companion_star(primary_star, parms)
        log_star(companion_star)
        primary_star.update_from_companion(companion_star)  # updates binary mass and designation
        primary_star.get_minimum_allowable_orbit_number_with_companion(primary_star, companion_star)
    else:
        companion_star = None
    return primary_star, companion_star


def build_stars(parms: Parameters, location: str):
    primary_star, primary_companion = build_primary_star(parms, location)
    secondary_stars = process_secondary_star_loop(primary_star, parms)
    primary_star.get_primary_orbit_number_range()
    primary_star.get_total_star_orbits()
    du.update_star_table(primary_star)
    if primary_companion is not None:
        du.update_star_table(primary_companion)
    for each_star in secondary_stars:
        du.update_star_table(each_star)


def build_stellar_details(parms):
    subsector_dy, location_list = gf.get_location_details()
    du.create_star_details_table(parms.db_name)
    for each_location in location_list:

        logging.info(f'{each_location}')

        if system_present(parms, each_location):
            build_stars(parms, each_location)
