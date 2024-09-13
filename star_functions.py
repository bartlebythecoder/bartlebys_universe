import random
import csv
import logging
import copy

import bodies
import database_utils as du
import lookup_tables as lu
import generic_functions as gf


def log_star(star_detail: str, star: bodies.Star):
    logging.info(
        f'{star.location}, {star_detail}, {star.star_class} {star.star_type}{star.star_subtype} '
        f'Mass: {star.star_mass}, Temp: {star.star_temperature}, Di: {star.star_diameter},'
        f'Lum: {star.star_luminosity:.3g}, Age: {star.star_age} ')


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


def populate_primary(parms: bodies.Parameters, each_location: str):
    new_star = bodies.Star(
        db_name=parms.db_name,
        build=parms.build,
        location=each_location,
        designation='A',
        orbit_category='A',
        orbit_class='primary',
        orbit_number=0,
        stars_orbited=0,
        orbit_eccentricity=0,
        orbit_au=0,
        orbit_min=0,
        orbit_max=0,
        orbit_period=0,
        star_type="X",
        star_subtype=-1,
        star_class='XX',
        star_mass=-99,
        binary_mass=-99,
        star_temperature=-99,
        star_diameter=-99,
        star_luminosity=-99,
        star_age=-99,
        gas_giants=-99,
        planetoid_belts=-99,
        terrestrial_planets=-99,
        minimal_orbit_number=-99,
        habitable_zone_center=-99
    )

    new_star.get_star_type()
    new_star.get_star_class()

    if new_star.star_type == 'Special':
        new_star.get_special_star_type()

    new_star.get_star_subtype()
    new_star.get_star_mass()
    new_star.binary_mass = new_star.star_mass
    new_star.get_star_temperature()
    new_star.get_star_diameter()
    new_star.get_star_luminosity()
    new_star.get_star_age()

    return new_star


def build_blank_star(star: bodies.Star):
    # builds a blank star object using some details from the primary
    # will be used for companions or secondary stars
    return bodies.Star(
        db_name=star.db_name,
        build=star.build,
        location=star.location,
        designation='X',
        orbit_category='X',
        orbit_class='X',
        orbit_number=-99,
        stars_orbited=-99,
        orbit_eccentricity=-99,
        orbit_au=-99,
        orbit_min=-99,
        orbit_max=-99,
        orbit_period=-99,
        star_type='X',
        star_subtype=-99,
        star_class='X',
        star_mass=-99,
        binary_mass=-99,
        star_temperature=-99,
        star_diameter=-99,
        star_luminosity=-99,
        star_age=0,
        gas_giants=-99,
        planetoid_belts=-99,
        terrestrial_planets=-99,
        minimal_orbit_number=-99,
        habitable_zone_center=-99
    )


def check_multiple_star(star: bodies.Star):
    die_mod = 0
    if star.star_class in ['Ia', 'Ib', 'II', 'III', 'IV']:
        die_mod = 1
    elif star.star_class in ['V', 'VI']:
        if star.star_type in ['O', 'B', 'A', 'F' ]:
            die_mod = 1
        elif star.star_type == 'M':
            die_mod = -1

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


def create_twin(star: bodies.Star):
    # given a star it creates a cooler star using the Twin process
    # used for building secondary stars similar to the system primary or companions similar to their primary
    companion_star = copy.deepcopy(star)

    return companion_star


def get_previous_star_class(star_type: str):
    # returns a "lower" star class from the one provided
    # used for sibling companions
    type_list = ['O', 'B', 'A', 'F', 'G', 'K', 'M']
    try:
        index = type_list.index(star_type)
        if index < 6:  # Check if it's not the first element
            logging.info(f'Getting previous star class. Was {star_type} now {type_list[index + 1]}')
            return type_list[index + 1]
        else:
            logging.info(f'Getting previous star class. Keeping {type_list[6]}')
            return type_list[6]

    except ValueError:
        return 'X'  # Handle the case where the star class is not found in the list


def correct_cooler_star_type(star: bodies.Star):
    # corrects "illegal" star types and subtypes that occurred after lessor or sibling updates
    if star.star_class == 'IV' and star.star_type == 'M':
        star.star_type = 'K'
        star.star_subtype = 4
        logging.info(f'CORRECTION: IV M changed to IV K4')
    elif star.star_class == 'IV' and star.star_type == 'K' and star.star_subtype > 4:
        star.star_type = 'K'
        star.star_subtype = 4
        logging.info(f'CORRECTION: IV K > 4 changed to IV K4')
    elif star.star_class == 'VI' and (star.star_type == 'A' or star.star_type == 'F'):
        star.star_type = 'G'
        star.star_subtype = 0
        logging.info(f'CORRECTION: VI A or F > 4 changed to VI G0')
    return star


def create_sibling(star: bodies.Star):
    # given a star it creates a cooler star using the Sibling process
    # used for building secondary stars cooler than system primary or companions cooler than their primary
    total_dice = 1
    dice = gf.roll_dice(total_dice)
    dice_info = bodies.DiceRoll(star.location, total_dice, 'find siblings star type and subtype', -99, 'unk')
    dice_info.dice_result = dice
    dice_info.table_result = 'n/a'
    du.insert_dice_rolls(star.db_name, dice_info)

    if star.star_class not in ['D', 'BD']:
        cooler_star_subtype = star.star_subtype + dice
        if cooler_star_subtype <= 9:
            cooler_star_type = star.star_type

        else:
            cooler_star_subtype -= 10
            cooler_star_type = get_previous_star_class(star.star_type)
            if cooler_star_type == star.star_type and cooler_star_subtype < star.star_subtype:
                cooler_star_subtype = star.star_subtype
    else:
        cooler_star_subtype = ''
        cooler_star_type = ''

    cooler_star = build_blank_star(star)
    cooler_star.orbit_number = 0
    cooler_star.star_type = cooler_star_type
    cooler_star.star_subtype = cooler_star_subtype
    cooler_star.star_class = star.star_class
    cooler_star = correct_cooler_star_type(cooler_star)
    cooler_star.get_star_mass()
    cooler_star.get_star_temperature()
    cooler_star.get_star_diameter()
    cooler_star.get_star_luminosity()

    return cooler_star


def create_lesser(star: bodies.Star):
    # given a star it creates a cooler star using the Lesser process
    # used for building secondary stars cooler than system primary or companions cooler than their primary
    if star.star_type != 'M':
        cooler_star_type = get_previous_star_class(star.star_type)
    else:
        cooler_star_type = 'M'

    logging.info(f'Companion Type {cooler_star_type}')
    cooler_star = build_blank_star(star)
    cooler_star.orbit_number = 0
    cooler_star.star_class = star.star_class
    cooler_star.star_type = cooler_star_type
    cooler_star.get_star_subtype()
    cooler_star = correct_cooler_star_type(cooler_star)
    cooler_star.get_star_mass()
    cooler_star.get_star_temperature()
    cooler_star.get_star_diameter()
    cooler_star.get_star_luminosity()

    if cooler_star_type == star.star_type and cooler_star.star_subtype < star.star_subtype:
        cooler_star.star_subtype = star.star_subtype  # In the future convert to Brown Dwarf
        cooler_star.star_mass = star.star_mass
        cooler_star.star_temperature = star.star_temperature
        cooler_star.star_diameter = star.star_diameter
        cooler_star.star_luminosity = star.star_luminosity
        logging.info('Companion Twin for now.  Will be Brown Dwarf in the future')

    return cooler_star


def is_hotter(companion: bodies.Star, primary: bodies.Star):
    type_list = ['O', 'B', 'A', 'F', 'G', 'K', 'M']
    try:
        companion_index = type_list.index(companion.star_type)
        primary_index = type_list.index(primary.star_type)
        if companion_index > primary_index:
            return False
        elif companion_index == primary_index and companion.star_subtype > primary.star_subtype:
            return False
        else:
            return True

    except ValueError:
        logging.info('Random Companion Error')
        return False  # Handle the case where the star class is not found in the list


def create_random(star: bodies.Star):
    # given a star it creates a cooler star using the Random process
    # used for building secondary stars cooler than system primary or companions cooler than their primary
    temp_parms = bodies.Parameters(star.db_name, star.build, 0, 0)
    cooler_star = populate_primary(temp_parms, star.location)
    if is_hotter(cooler_star, star):
        logging.info('Random creation too hot, creating a lesser')
        cooler_star = create_lesser(star)

    return cooler_star


def build_white_dwarf(star):
    white_dwarf = build_blank_star(star)
    white_dwarf.star_class = 'D'
    white_dwarf.star_type = ''
    white_dwarf.star_subtype = ''
    white_dwarf.star_diameter = 1 / white_dwarf.star_mass * 0.01

    return white_dwarf


def build_brown_dwarf(star):
    brown_dwarf = build_blank_star(star)
    brown_dwarf.star_class = 'BD'
    brown_dwarf.star_type = ''
    brown_dwarf.star_subtype = ''
    return brown_dwarf


def create_other(star: bodies.Star):
    # given a star it creates a cooler star using the Other
    # used for building white dwarfs and brown dwarfs
    dice_roll = gf.roll_dice(2)
    dice_info = bodies.DiceRoll(
        location=star.location,
        number=2,
        reason='Other Column for non-primary',
        dice_result=dice_roll,
        table_result=dice_roll)
    du.insert_dice_rolls(star.db_name, dice_info)

    if dice_roll <= 7:
        other_star = build_white_dwarf(star)
    else:
        other_star = build_brown_dwarf(star)

    return other_star


def create_non_primary(primary: bodies.Star, category):
    # Used to create the main fields of non-primary star.
    # returns the non-primary details based on being provided the primary

    if category == 'Twin':
        non_primary = create_twin(primary)
    elif category == 'Sibling':
        non_primary = create_sibling(primary)
    elif category == 'Lesser':
        non_primary = create_lesser(primary)
    elif category == 'Random':
        non_primary = create_random(primary)
    elif category == 'Other':
        non_primary = create_other(primary)
    else:
        non_primary = None
        logging.info('Failed to create non-primary.  Unexpected Type')

    if non_primary.star_mass > primary.star_mass:
        logging.info(f'{primary.designation} **** Mass of non-primary {non_primary.star_mass} > Mass of Primary')
        logging.info('**** Reducing companion mass and diameter to match Primary')
        non_primary.star_mass = primary.star_mass
        non_primary.star_diameter = primary.star_diameter
    return non_primary


def update_orbit_information(star: bodies.Star):
    star.star_age = 0
    star.get_au()
    star.get_eccentricity()
    star.get_orbit_min()
    star.get_orbit_max()
    return star


def populate_companion(primary: bodies.Star):
    # Returns a companion star based on details of the star given (called primary in this instance)
    companion_category = find_companion_category(primary)
    logging.info(f'Companion found.  It is a {companion_category}')
    companion = create_non_primary(primary, companion_category)

    companion.binary_mass = companion.star_mass
    companion.orbit_category = primary.orbit_category
    companion.orbit_class = 'companion'
    companion.designation = primary.designation + 'b'
    companion.get_companion_orbit_number(primary)
    companion.stars_orbited = 1
    companion = update_orbit_information(companion)

    return companion


def populate_secondary(primary: bodies.Star, orbit_class: str, star_designation: str, stars_orbited: int):
    # Returns a secondary star based on details of the primary
    secondary_category = find_secondary_category(primary)
    logging.info(f'Secondary found.  It is a {secondary_category}')

    secondary = create_non_primary(primary, secondary_category)
    secondary.orbit_class = orbit_class
    if secondary.orbit_class == 'close':
        secondary.get_close_secondary_orbit_number()
    elif secondary.orbit_class == 'near':
        secondary.get_near_secondary_orbit_number()
    elif secondary.orbit_class == 'far':
        secondary.get_far_secondary_orbit_number()

    secondary.binary_mass = secondary.star_mass
    secondary = update_orbit_information(secondary)
    secondary.designation = star_designation
    secondary.orbit_category = star_designation
    secondary.stars_orbited = stars_orbited
    secondary.orbit_period = bodies.calculate_secondary_orbit_period(primary, secondary)

    return secondary


def update_companion_details(star: bodies.Star):
    # Updates related to adding a companion to the provided Star
    # Returns the updated star and the new companion
    companion = populate_companion(star)
    star.designation += 'a'
    star.binary_mass = star.star_mass + companion.star_mass
    companion.orbit_period = (bodies.calculate_companion_orbit_period(star, companion))
    return companion, star


def build_secondary_stars(primary_star: bodies.Star, stars_in_system: int, stars_orbited: int):
    secondary_list = ['close', 'near', 'far']
    designation_list = ['B', 'C', 'D', 'X']
    designation_index = 0
    for each_secondary in secondary_list:
        if check_multiple_star(primary_star):
            if each_secondary != 'close' and primary_star.star_class not in ['Ia', 'Ib', 'II', 'III']:
                secondary_companion = None
                stars_in_system += 1
                logging.info(f'{primary_star.location} {each_secondary} {designation_list[designation_index]} ')
                secondary = populate_secondary(primary_star,
                                               each_secondary,
                                               designation_list[designation_index],
                                               stars_orbited)

                if check_multiple_star(secondary):
                    stars_in_system += 1
                    secondary_companion, secondary = update_companion_details(secondary)

                du.update_star_tables(secondary, secondary_companion)
                designation_index += 1


def build_primary_star(location, parms):
    add_stars_in_system = 0
    add_stars_orbited = 0
    primary_companion = None
    primary_star = populate_primary(parms, location)
    if check_multiple_star(primary_star):
        add_stars_in_system += 1
        primary_companion, primary_star = update_companion_details(primary_star)
        add_stars_orbited += 1
    du.update_star_tables(primary_star, primary_companion)
    return primary_star, add_stars_in_system, add_stars_orbited


def build_system(each_location: str, stars_in_system: int, parms: bodies.Parameters):
    stars_orbited = 1
    stars_in_system = 1

    primary_star, add_stars_in_system, add_stars_orbited = build_primary_star(each_location, parms)

    stars_orbited += add_stars_orbited
    stars_in_system += add_stars_in_system

    build_secondary_stars(primary_star, stars_in_system, stars_orbited)

    return primary_star, stars_in_system
