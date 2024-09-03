import random

import bodies
import database_utils as du
import lookup_tables as lu


def roll_dice(number: int):
    # Return a random number rolling the number of dice = number
    total = 0
    for each_roll in range(number):
        total += random.randint(1, 6)
    return total


def get_subsector_number_list(subsector: str):
    def get_string(num: int):
        str_num = str(num)
        if len(str_num) == 1: str_num = '0' + str_num
        return str_num

    def get_ranges(front_limits: list, back_limits: list):
        return (range(front_limits[0], front_limits[1] + 1), range(back_limits[0], back_limits[1] + 1))

    subsector_number_list = []

    front_limits = lu.subsector_letter_dictionary[subsector][0]
    back_limits = lu.subsector_letter_dictionary[subsector][1]
    front_digits, back_digits = get_ranges(front_limits, back_limits)

    for each_front in front_digits:
        for each_back in back_digits:
            front_str = get_string(each_front)
            back_str = get_string(each_back)
            subsector_number_list.append(front_str + back_str)

    return subsector_number_list


def system_present(frequency: int, db_name: str, location: str):
    # returns a True or False if a system is present based on the frequency provided
    dice = roll_dice(1)
    dice_info = bodies.DiceRoll
    dice_info.location = location
    dice_info.number = 1
    dice_info.reason = 'system present'
    dice_info.dice_result = dice
    if dice <= frequency:
        dice_info.table_result = True
    else:
        dice_info.table_result = False

    du.insert_dice_rolls(db_name, dice_info)

    return bodies.DiceRoll.table_result


def get_hot_star_type(star: object):
    # if the original get_star_type function returns a hot star, this function is used to return a star type
    dice = roll_dice(2)
    dice_info = bodies.DiceRoll(
        location=star.location,
        number=2,
        reason='hot star type',
        dice_result=dice,
        table_result=lu.mgt2e_hot_star_type_dy[dice])

    du.insert_dice_rolls(star.db_name, dice_info)
    return dice_info.table_result


def get_star_type(star: object):
    # returns the star type after being provided the current star details

    star_type_dy = lu.mgt2e_standard_star_type_dy

    dice = roll_dice(2)
    dice_info = bodies.DiceRoll(
        location=star.location,
        number=2,
        reason='star type',
        dice_result=dice,
        table_result=star_type_dy[dice])
    du.insert_dice_rolls(star.db_name, dice_info)

    if dice_info.table_result == 'Hot':
        dice_info.table_result = get_hot_star_type(star)

    return dice_info.table_result

def get_special_star_type(star: object):
    # if get_star_type returns a special star, use the class to return the final star type

    star_type_dy = lu.mgt2e_standard_star_type_dy
    dice = roll_dice(2) + 1

    # Special rule for IV luminosity stars
    if star.star_class == 'IV':
        if dice >= 3 and dice <= 6:
            dice += 5

    dice_info = bodies.DiceRoll(
        location=star.location,
        number=2,
        reason='special star type (with mods)',
        dice_result=dice,
        table_result=star_type_dy[dice])
    du.insert_dice_rolls(star.db_name, dice_info)

    star.star_type = star_type_dy[dice]

    if dice_info.table_result == 'Hot':
        dice_info.table_result = get_hot_star_type(star)

    # More special rules
    if star.star_class == 'IV' and star.star_type == 'O':
        star.star_type = 'B'

    if star.star_class == 'VI' and star.star_type == 'F':
        star.star_type = 'G'

    if star.star_class == 'VI' and star.star_type == 'A':
        star.star_type = ('B')

    return star.star_type


def get_giant_star_class(star: object):
    # if the original get_star_class returns a giant star, use this function to return the class
    dice = roll_dice(2)
    dice_info = bodies.DiceRoll(
        location=star.location,
        number=2,
        reason='star class',
        dice_result=dice,
        table_result=lu.mgt2e_giant_star_class_dy[dice])
    du.insert_dice_rolls(star.db_name, dice_info)

    return dice_info.table_result


def get_star_class(star: object):
    # returns the star class after being provided the current star details
    if star.star_type != 'Special':
        return 'V'

    else:
        dice = roll_dice(2)
        dice_info = bodies.DiceRoll(
            location=star.location,
            number=2,
            reason='star class',
            dice_result=dice,
            table_result=lu.mgt2e_special_star_class_dy[dice])
        du.insert_dice_rolls(star.db_name, dice_info)

        if dice_info.table_result == 'Giants':
            dice_info.table_result = get_giant_star_class(star)

        return dice_info.table_result



