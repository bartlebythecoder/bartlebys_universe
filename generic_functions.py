import random
import csv
import string
import logging


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


def get_location_details():
    subsector_list = list(string.ascii_uppercase[:16])  # A to P
    location_list = []
    subsector_dy = {}
    for subsector in subsector_list:
        locations = get_subsector_number_list(subsector)
        location_list += locations
        for each_location in locations:
            subsector_dy[each_location] = subsector

    location_list.sort()
    return subsector_dy, location_list


def dict_to_indexed_list(data_dict):
    """
    Converts a dictionary into a list of tuples, where each tuple contains a value from the dictionary and its corresponding index.

    Args:
        data_dict: The dictionary to be transformed.

    Returns:
        A list of tuples, each containing a value from the dictionary and its index.
    """
    return [(value, key) for key, value in data_dict.items()]


def is_between(x: float, a: float, b: float):
    """ Checks if a number `x` is between two floats `a` and `b` (inclusive). """
    return a <= x <= b

def extrapolate_table(x: float, data: dict):
    def get_keys(x_var):
        old_key = 0
        for key in data:
            if key > x_var:
                return old_key, key
            else:
                old_key = key
        return -1, -1

    if x > 20:
        x = 20
        logging.info('WARNING - ORBIT NUMBER > 20')
    elif x < 0:
        x = 0
        logging.info('WARNING - ORBIT NUMBER < 0')

    if x in data:
        return data[x]

    else:  # Handle fractional inputs using interpolation

        lower, upper = get_keys(x)
        lower_y = data[lower]
        upper_y = data[upper]

        fractional_part = (x - lower) / (upper - lower)
        estimated_y = lower_y + fractional_part * (upper_y - lower_y)
        return estimated_y


def int_to_hex(dec):
    # Converts integers to their hex replacements
    hex_digits = "0123456789ABCDEFGHJ"
    if dec > 18:
        dec = 18
    return hex_digits[dec % 17]


def hex_to_int(hex_val):
    # Converts hex values to integers
    response = hex_val
    try:
        hex_list = ['A','B','C','D','E','F','G','H']
        hex_dict = {'H': 17,
                    'G': 16,
                    'F': 15,
                    'E': 14,
                    'D': 13,
                    'C': 12,
                    'B': 11,
                    'A': 10}
        if hex_val in hex_list: response = int(hex_dict[hex_val])
        else: response = int(response)
        return response
    except Exception as e:
        logging.debug(f'failed hex_to_int with {hex_val} {e}')


def create_sector_coordinate_dy(dy: dict):
    """
    Returns a dictionary of x,y hex center coordinates for an entire sector.
    Requires the coordinates for the 'A' subsector as a dy.
    """

    subsector_hex_centers_dy = dy.copy()  # Create a copy of the input dictionary

    for xx in range(1, 33):  # Iterate over all x-coordinates
        for yy in range(1, 41):  # Iterate over all y-coordinates
            # Calculate the original x and y coordinates within the 'A' subsector
            original_xx = (xx - 1) % 8 + 1
            original_yy = (yy - 1) % 10 + 1
            original_key = f"{original_xx:02d}{original_yy:02d}"
            new_key = f"{xx:02d}{yy:02d}"
            subsector_hex_centers_dy[new_key] = subsector_hex_centers_dy[original_key]

    return subsector_hex_centers_dy