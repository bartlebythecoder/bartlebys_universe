import random
import csv
import logging

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


def check_companion(star: object):
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
    dice_info = bodies.DiceRoll(star.location, total_dice, 'companion present', -99, 'unk')
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
        die_mod = 1

    dice = roll_dice(2) + die_mod
    dice_info = bodies.DiceRoll
    dice_info.location = star.location
    dice_info.number = 2
    dice_info.reason = 'companion type'
    dice_info.dice_result = dice
    dice_info.table_result = lu.companion_star_category_dy[dice]
    du.insert_dice_rolls(star.db_name, dice_info)
    return dice_info.table_result

def create_twin_companion(star):
    companion_star = bodies.Star(
        db_name=star.db_name,
        build=star.build,
        location=star.location,
        designation='Ab',
        orbit_class='primary companion',
        orbit_number=0,
        star_type=star.star_type,
        star_subtype=star.star_subtype,
        star_class=star.star_class,
        star_mass=star.star_mass,
        star_temperature=star.star_temperature,
        star_diameter=star.star_diameter,
        star_luminosity=star.star_luminosity,
        star_age=star.star_age,
        gas_giants=-99,
        planetoid_belts=-99,
        terrestrial_planets=-99,
        minimal_orbit_number=-99,
        habitable_zone_center=-99
    )

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

    companion_star = bodies.Star(
        db_name=star.db_name,
        build=star.build,
        location=star.location,
        designation='Ab',
        orbit_class='primary companion',
        orbit_number=0,
        star_type=companion_type,
        star_subtype=companion_subtype,
        star_class=star.star_class,
        star_mass=star.star_mass,
        star_temperature=star.star_temperature,
        star_diameter=star.star_diameter,
        star_luminosity=star.star_luminosity,
        star_age=star.star_age,
        gas_giants=-99,
        planetoid_belts=-99,
        terrestrial_planets=-99,
        minimal_orbit_number=-99,
        habitable_zone_center=-99
    )
    companion_star.get_star_mass()
    companion_star.get_star_temperature()
    companion_star.get_star_diameter()
    companion_star.get_star_luminosity()
    companion_star.get_star_age()

    return companion_star

def populate_companion(star):
    # Returns a companion star based on details of the star given
    companion_category = find_companion_category(star)
    logging.info(f'Primary companion found.  It is a {companion_category}')

    if companion_category == 'Twin':
        primary_companion = create_twin_companion(star)
    elif companion_category == 'Sibling':
        primary_companion = create_sibling_companion(star)
    else:
        primary_companion = create_sibling_companion(star)

    return primary_companion