import logging
import copy

import bodies
import database_utils as du
import generic_functions as gf
import lookup_tables as lu


def log_star(star: bodies.Star):
    logging.info(
        f'{star.location}, {star.star_class} {star.star_type}{star.star_subtype} '
        f'Mass: {star.star_mass}, Temp: {star.star_temperature}, Di: {star.star_diameter},'
        f'Lum: {star.star_luminosity:.3g}, Age: {star.star_age} ')


def get_multiple_star_die_mod(star: bodies.Star):
    die_mod = 0
    if star.star_class in ['Ia', 'Ib', 'II', 'III', 'IV']:
        die_mod = 1
    elif star.star_class in ['V', 'VI']:
        if star.star_type in ['O', 'B', 'A', 'F' ]:
            die_mod = 1
        elif star.star_type == 'M':
            die_mod = -1

    return die_mod


def check_multiple_star(star: bodies.Star):
    # Returns True or False if an extra star is present attached to provided star
    # Used for checking secondary or companion stars

    die_mod = get_multiple_star_die_mod(star)
    total_dice = 2
    dice = gf.roll_dice(total_dice) + die_mod
    dice_info = bodies.DiceRoll(star.location, total_dice, 'multiple star present', -99, 'unk')
    dice_info.dice_result = dice
    if dice >= 10:
        dice_info.table_result = True
    else:
        dice_info.table_result = False
    du.insert_dice_rolls(star.db_name, dice_info)
    return dice_info.table_result


def find_secondary_category(star: bodies.Star):
    chart = lu.companion_star_category_dy
    die_mod = 0
    if star.star_class in ['III' or 'IV']:
        die_mod = -1

    dice = gf.roll_dice(2) + die_mod
    dice_info = bodies.DiceRoll
    dice_info.location = star.location
    dice_info.number = 2
    dice_info.reason = 'companion type'
    dice_info.dice_result = dice
    dice_info.table_result = lu.secondary_star_category_dy[dice]
    du.insert_dice_rolls(star.db_name, dice_info)
    return dice_info.table_result


def build_secondary_star(main: bodies.Star, parms: bodies.Parameters, secondary_type, designation):
    # Returns a companion star based on details of the star given (the main to the companion)
    secondary_category = find_secondary_category(main)
    logging.info(f'Secondary found.')
    secondary = bodies.Star(parms, main.location)

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

    return secondary


def find_companion_category(star: bodies.Star):
    chart = lu.companion_star_category_dy
    die_mod = 0
    if star.star_class in ['III' or 'IV']:
        die_mod = -1

    dice = gf.roll_dice(2) + die_mod
    dice_info = bodies.DiceRoll
    dice_info.location = star.location
    dice_info.number = 2
    dice_info.reason = 'companion type'
    dice_info.dice_result = dice
    dice_info.table_result = lu.companion_star_category_dy[dice]
    du.insert_dice_rolls(star.db_name, dice_info)
    return dice_info.table_result


def build_companion_star(main: bodies.Star, parms: bodies.Parameters):
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

    companion.get_companion_orbit_number(main)
    companion.stars_orbited = 1
    companion.get_orbit_eccentricity()
    companion.get_orbit_au()
    companion.get_orbit_min()
    companion.get_orbit_max()
    companion.get_companion_orbit_period(main)

    return companion


def process_secondary_star_loop(system: bodies.System, primary_star: bodies.Star, parms: bodies.Parameters):
    secondary_list = ['close', 'near', 'far']
    designation_list = ['B', 'C', 'D', 'X']
    designation_index = 0
    for each_secondary in secondary_list:
        if check_multiple_star(primary_star):
            if not (each_secondary == 'close' and primary_star.star_class in ['Ia', 'Ib', 'II', 'III']):
                secondary_companion = None
                system.stars_in_system += 1
                logging.info(f'{primary_star.location} {each_secondary} {designation_list[designation_index]} ')
                secondary = build_secondary_star(primary_star,
                                                 parms,
                                                 each_secondary,
                                                 designation_list[designation_index])
                if secondary.star_age > system.system_age:
                    system.system_age = secondary.star_age

                if check_multiple_star(secondary):
                    system.stars_in_system += 1
                    secondary_companion = build_companion_star(secondary, parms)
                    log_star(secondary_companion)
                    secondary.update_from_companion(secondary_companion)   # updates binary mass and designation

                    if secondary_companion.star_age > system.system_age:
                        system.system_age = secondary_companion.star_age

                du.update_star_tables(secondary, secondary_companion)
                designation_index += 1
            else:
                logging.info(f"Failed secondary {each_secondary} {primary_star.star_class}")

def build_primary_star(system, parms):

    companion_star = None
    primary_star = bodies.Star(parms, system.location)
    system.system_age = primary_star.star_age
    log_star(primary_star)
    if check_multiple_star(primary_star):
        system.stars_in_system += 1
        companion_star = build_companion_star(primary_star, parms)
        log_star(companion_star)
        primary_star.update_from_companion(companion_star)  # updates binary mass and designation

    du.update_star_tables(primary_star, companion_star)
    return primary_star


def build_stars(system: bodies.System, parms: bodies.Parameters):
    primary_star = build_primary_star(system, parms)
    process_secondary_star_loop(system, primary_star, parms)


def system_present(parms: bodies.Parameters, location: str):
    # returns a True or False if a system is present based on the frequency provided
    dice = gf.roll_dice(1)
    dice_info = bodies.DiceRoll
    dice_info.location = location
    dice_info.number = 1
    dice_info.reason = 'system present'
    dice_info.dice_result = dice
    if dice <= parms.frequency:
        dice_info.table_result = True
    else:
        dice_info.table_result = False

    du.insert_dice_rolls(parms.db_name, dice_info)

    return bodies.DiceRoll.table_result


def build_system(parms: bodies.Parameters, location, subsector):
    new_system = bodies.System(
        db_name=parms.db_name,
        build=parms.build,
        location=location,
        subsector=subsector,
        system_age=0,
        stars_in_system=1
    )
    build_stars(new_system, parms)
    du.insert_system_details(new_system)

