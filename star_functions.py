import random
import csv
import logging
import copy

import bodies
import database_utils as du
import lookup_tables as lu


def roll_dice(number: int):
    # Return a random number rolling the number of dice = number
    # Perhaps needs a new home for general functions
    total = 0
    for each_roll in range(number):
        total += random.randint(1, 6)
    return total


def csv_to_dict_of_lists(filename: str):
    # Loads a CSV file into a dictionary of lists.
    # Returns a dictionary where keys are the first column values
    # Perhaps needs a new home in general functions

    with open(filename, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # Extract the header row
        return {row[0]: row[1:] for row in reader}


def get_subsector_number_list(subsector: str):
    def get_string(num: int):
        str_num = str(num)
        if len(str_num) == 1: str_num = '0' + str_num
        return str_num

    def get_ranges(front_limits: list, back_limits: list):
        return (range(front_limits[0], front_limits[1] + 1), range(back_limits[0], back_limits[1] + 1))

    subsector_number_list = []

    front_limits = lu.subsector_letter_dy[subsector][0]
    back_limits = lu.subsector_letter_dy[subsector][1]
    front_digits, back_digits = get_ranges(front_limits, back_limits)

    for each_front in front_digits:
        for each_back in back_digits:
            front_str = get_string(each_front)
            back_str = get_string(each_back)
            subsector_number_list.append(front_str + back_str)

    return subsector_number_list


def system_present(parms: object, location: str):
    # returns a True or False if a system is present based on the frequency provided
    dice = roll_dice(1)
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


def populate_primary(parms: object, each_location: str):
    new_star = bodies.Star(
        db_name=parms.db_name,
        build=parms.build,
        location=each_location,
        designation='A',
        orbit_class='primary',
        orbit_number=0,
        orbit_eccentricity=0,
        orbit_au=0,
        orbit_min=0,
        orbit_max=0,
        star_type="X",
        star_subtype=-1,
        star_class='XX',
        star_mass=1.0,
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
    new_star.get_star_temperature()
    new_star.get_star_diameter()
    new_star.get_star_luminosity()
    new_star.get_star_age()

    return new_star


def build_blank_star(star):
    # builds a blank star object using some details from the primary
    # will be used for companions or secondary stars
    return bodies.Star(
        db_name=star.db_name,
        build=star.build,
        location=star.location,
        designation='X',
        orbit_class='X',
        orbit_number=-99,
        orbit_eccentricity=-99,
        orbit_au=-99,
        orbit_min=-99,
        orbit_max=-99,
        star_type='X',
        star_subtype=-99,
        star_class='X',
        star_mass=-99,
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


def check_multiple_star(star: object):
    die_mod = 0
    if star.star_class in ['Ia', 'Ib', 'II', 'III', 'IV']:
        die_mod = 1
    elif star.star_class in ['V', 'VI']:
        if star.star_type in ['O', 'B', 'A', 'F' ]:
            die_mod = 1
        elif star.star_type == 'M':
            die_mod = -1

    total_dice = 2
    dice = roll_dice(total_dice) + die_mod
    dice_info = bodies.DiceRoll(star.location, total_dice, 'multiple star present', -99, 'unk')
    dice_info.dice_result = dice
    if dice >= 10:
        dice_info.table_result = True
    else:
        dice_info.table_result = False
    du.insert_dice_rolls(star.db_name, dice_info)
    return dice_info.table_result


def find_companion_category(star):
    chart = lu.companion_star_category_dy
    die_mod = 0
    if star.star_class in ['III' or 'IV']:
        die_mod = -1

    dice = roll_dice(2) + die_mod
    dice_info = bodies.DiceRoll
    dice_info.location = star.location
    dice_info.number = 2
    dice_info.reason = 'companion type'
    dice_info.dice_result = dice
    dice_info.table_result = lu.companion_star_category_dy[dice]
    du.insert_dice_rolls(star.db_name, dice_info)
    return dice_info.table_result


def find_secondary_category(star):
    chart = lu.companion_star_category_dy
    die_mod = 0
    if star.star_class in ['III' or 'IV']:
        die_mod = -1

    dice = roll_dice(2) + die_mod
    dice_info = bodies.DiceRoll
    dice_info.location = star.location
    dice_info.number = 2
    dice_info.reason = 'companion type'
    dice_info.dice_result = dice
    dice_info.table_result = lu.secondary_star_category_dy[dice]
    du.insert_dice_rolls(star.db_name, dice_info)
    return dice_info.table_result

def create_twin_companion(star):
    companion_star = copy.deepcopy(star)
    companion_star.designation='Ab'
    companion_star.orbit_class='primary companion'
    companion_star.star_age=0

    return companion_star


def get_previous_star_class(star_type):
    # returns a "lower" star class from the one provided
    # used for sibling companions
    type_list = ['O', 'B', 'A', 'F', 'G', 'K', 'M']
    try:
        index = type_list.index(star_type)
        if index < 6:  # Check if it's not the first element
            return type_list[index + 1]
        else:
            return type_list[6]

    except ValueError:
        return 'X'  # Handle the case where the star class is not found in the list


def fix_companion_type(companion_type, star):
    # returns a new companion type that corrects any type/class restrictions when given the current type and primary
    if star.star_class == 'IV' and (companion_type == 'K' or companion_type == 'M'):
        companion_type = star.star_type

    if star.star_class == 'VI' and (companion_type == 'A' or companion_type == 'F'):
        companion_type = 'G'

    return companion_type

def create_sibling_companion(star):
    total_dice = 1
    dice = roll_dice(total_dice)
    dice_info = bodies.DiceRoll(star.location, total_dice, 'find siblings star type and subtype', -99, 'unk')
    dice_info.dice_result = dice
    dice_info.table_result = 'n/a'
    du.insert_dice_rolls(star.db_name, dice_info)

    primary_subtype = star.star_subtype
    companion_subtype = primary_subtype + dice
    if companion_subtype <= 9:
        companion_type = star.star_type
    else:
        companion_subtype -= 10
        companion_type = get_previous_star_class(star.star_type)
        if companion_type == star.star_type and companion_subtype < primary_subtype:
            companion_subtype = primary_subtype

    if companion_type == 'K' and companion_subtype > 5:
        companion_subtype = star.star_subtype

    companion_type = fix_companion_type(companion_type, star)

    companion_star = build_blank_star(star)
    companion_star.designation = 'Ab'
    companion_star.orbit_class = 'primary companion'
    companion_star.orbit_number = 0
    companion_star.star_type = companion_type
    companion_star.star_subtype = companion_subtype
    companion_star.star_class = star.star_class
    companion_star.get_star_mass()
    companion_star.get_star_temperature()
    companion_star.get_star_diameter()
    companion_star.get_star_luminosity()
    companion_star.star_age=0

    return companion_star


def create_lesser_companion(star):

    if star.star_type != 'M':
        companion_type = get_previous_star_class(star.star_type)
    else:
        companion_type = 'M'

    companion_type = fix_companion_type(companion_type, star)

    logging.info(f'Companion Type {companion_type}')

    companion_star = build_blank_star(star)

    companion_star.designation = 'Ab'
    companion_star.orbit_class = 'primary companion'
    companion_star.orbit_number = 0
    companion_star.star_type = companion_type
    companion_star.get_star_subtype()
    companion_star.star_class = star.star_class
    companion_star.get_star_mass()
    companion_star.get_star_temperature()
    companion_star.get_star_diameter()
    companion_star.get_star_luminosity()
    companion_star.star_age=0

    if companion_type == star.star_type and companion_star.star_subtype < star.star_subtype:
        companion_star.star_subtype = star.star_subtype  # In the future convert to Brown Dwarf
        companion_star.star_mass = star.star_mass
        companion_star.star_temperature = star.star_temperature
        companion_star.star_diameter = star.star_diameter
        companion_star.star_luminosity = star.star_luminosity
        logging.info('Companion Twin for now.  Will be Brown Dwarf in the future')

    return companion_star


def is_hotter(companion, primary):
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


def create_random_companion(star):
    temp_parms = bodies.Parameters(star.db_name, star.build, 0, [], 0)
    companion_star = populate_primary(temp_parms, star.location)
    if is_hotter(companion_star, star):
        logging.info('Random creation too hot, creating a lesser')
        companion_star = create_lesser_companion(star)
    companion_star.orbit_class = 'primary companion'
    companion_star.designation = 'Ab'
    companion_star.star_age = 0
    return companion_star


def populate_companion(star):
    # Returns a companion star based on details of the star given
    companion_category = find_companion_category(star)
    logging.info(f'Primary companion found.  It is a {companion_category}')

    if companion_category == 'Twin':
        primary_companion = create_twin_companion(star)
    elif companion_category == 'Sibling':
        primary_companion = create_sibling_companion(star)
    elif companion_category == 'Lesser':
        primary_companion = create_lesser_companion(star)
    elif companion_category == 'Random':
        primary_companion = create_random_companion(star)
    else:
        primary_companion = create_sibling_companion(star)

    if primary_companion.star_mass > star.star_mass:
        logging.info('***************** Mass of companion > Mass of Primary')
        logging.info('***************** Reducing companion mass and diameter to match Primary')
        primary_companion.star_mass = star.star_mass
        primary_companion.star_diameter = star.star_diameter

    primary_companion.get_companion_orbit_number(star.designation)

    return primary_companion


def populate_secondary(star):
    # Returns a companion star based on details of the star given
    companion_category = find_companion_category(star)
    logging.info(f'Secondary found.  It is a {companion_category}')

    if companion_category == 'Twin':
        primary_companion = create_twin_companion(star)
    elif companion_category == 'Sibling':
        primary_companion = create_sibling_companion(star)
    elif companion_category == 'Lesser':
        primary_companion = create_lesser_companion(star)
    elif companion_category == 'Random':
        primary_companion = create_random_companion(star)
    else:
        primary_companion = create_sibling_companion(star)

    if primary_companion.star_mass > star.star_mass:
        logging.info('***************** Mass of companion > Mass of Primary')
        logging.info('***************** Reducing companion mass and diameter to match Primary')
        primary_companion.star_mass = star.star_mass
        primary_companion.star_diameter = star.star_diameter

    primary_companion.get_companion_orbit_number(star.designation)

    return primary_companion

