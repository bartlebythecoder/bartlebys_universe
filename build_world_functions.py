import time
import logging
import math

import bodies
import database_utils as du
import generic_functions as gf


def get_world_info(parms: bodies.Parameters, location: str):
    system_dy = du.get_system_info(parms, location)
    star_list = du.get_star_info(parms, location)
    return system_dy, star_list

def calculate_world_star_total(parms: bodies.Parameters, star_info_dy: dict):
    system_dy = star_info_dy['system_dy']
    star_list = star_info_dy['star_list']
    location = system_dy['location']
    for each_star in star_list:
        system_total_worlds = (system_dy['number_of_gas_giants'] + system_dy['number_of_planetoid_belts']
                               + system_dy['number_of_terrestrial_planets'])
        fraction = system_total_worlds * each_star['total_star_orbits'] / system_dy['total_system_orbits']
        if each_star['orbit_class'] == 'primary':
            fraction = math.ceil(fraction)
        else:
            fraction = math.floor(fraction)

        each_star['world_total'] = fraction


def orbit_number_restriction_adjustment(orbit_number, star):
    if star['restricted_close_orbit_start'] is not None:
        if star['restricted_close_orbit_start'] < orbit_number < star['restricted_close_orbit_end']:
            restriction_difference = star['restricted_close_orbit_end'] - star['restricted_close_orbit_start']
            orbit_number += restriction_difference

    if star['restricted_near_orbit_start'] is not None:
        if star['restricted_near_orbit_start'] < orbit_number < star['restricted_near_orbit_end']:
            restriction_difference = star['restricted_near_orbit_end'] - star['restricted_near_orbit_start']
            orbit_number += restriction_difference

    if star['restricted_far_orbit_start'] is not None:
        if star['restricted_far_orbit_start'] < orbit_number < star['restricted_far_orbit_end']:
            restriction_difference = star['restricted_far_orbit_end'] - star['restricted_far_orbit_start']
            orbit_number += restriction_difference


    return orbit_number


def build_orbits(parms: bodies.Parameters, star_info_dy: dict):
    system_dy = star_info_dy['system_dy']
    star_list = star_info_dy['star_list']
    location = system_dy['location']

    for each_star in star_list:
        orbit_number = each_star['minimum_allowable_orbit_number']
        for orbit_counter, each_orbit in enumerate(range(0, each_star['total_star_orbits'])):
            orbit_digit = orbit_counter + 1
            if orbit_digit < system_dy['baseline_number'] or each_star['orbit_class'] != 'primary':
                orbit_number += system_dy['orbit_spread']
            else:
                if orbit_number <= system_dy['baseline_orbit_number']:
                    orbit_number = system_dy['baseline_orbit_number'] + system_dy['orbit_spread']
                else:
                    orbit_number += system_dy['orbit_spread']

            if each_star['orbit_class'] == 'primary':
                orbit_number = orbit_number_restriction_adjustment(orbit_number, each_star)

            if orbit_number <= (each_star['maximum_allowable_orbit_number'] * 1.1):

                orbit_slot = each_star['designation'] + str(orbit_digit)
                world_var = bodies.World(
                    db_name=parms.db_name,
                    location=location,
                    orbit_slot=orbit_slot,
                    star_designation=each_star['designation'],
                    orbit_number=orbit_number,
                    world_type='Yup'
                )

                try:
                    du.insert_orbit_details(world_var)
                except:
                    logging.info('**************ERROR writing to World Details')
                    time.sleep(2)
                    logging.info('**************Trying Again')
                    du.insert_orbit_details(world_var)

            else:
                logging.info(f'{location}:  {each_star['orbit_class']} {orbit_number} too high')

def find_anomalous_orbit_count(parm, location):
    dice_roll = gf.roll_dice(2)
    dice_info = bodies.DiceRoll(
        location=location,
        number=2,
        reason='anomalous_orbit_count',
        dice_result=dice_roll,
        table_result=str(dice_roll))
    du.insert_dice_rolls(parm.db_name, dice_info)

    if dice_roll <= 9:
        return 0
    elif dice_roll <= 10:
        return 1
    elif dice_roll <= 11:
        return 2
    elif dice_roll == 12:
        return 3
    else:
        return -1


def get_anomalous_orbit_type(parm, location):
    dice_roll = gf.roll_dice(2)
    dice_info = bodies.DiceRoll(
        location=location,
        number=2,
        reason='anomalous_orbit_type',
        dice_result=dice_roll,
        table_result=str(dice_roll))
    du.insert_dice_rolls(parm.db_name, dice_info)

    if dice_roll <= 7:
        return 'random'
    elif dice_roll <= 8:
        return 'eccentric'
    elif dice_roll <= 9:
        return 'inclined'
    elif dice_roll <= 11:
        return 'retrograde'
    elif dice_roll == 12:
        return 'trojan'
    else:
        return -1

def build_anomalous_orbits(parm, star_info_dy):
    system_dy = star_info_dy['system_dy']
    star_list = star_info_dy['star_list']
    location = system_dy['location']
    number_of_anomalous_orbits = find_anomalous_orbit_count(parm, location)
    if number_of_anomalous_orbits > 0:
        for each_orbit in range(0, number_of_anomalous_orbits):
            anomalous_orbit_type = get_anomalous_orbit_type(parm, location)

def build_worlds(parms: bodies.Parameters, location: str):
    system_dy, star_list = get_world_info(parms, location)
    star_info_dy = {
        'system_dy': system_dy,
        'star_list': star_list
            }
    calculate_world_star_total(parms, star_info_dy)
    logging.info(f'Star Info: {star_info_dy['star_list']}')
    build_orbits(parms, star_info_dy)
    build_anomalous_orbits(parms, star_info_dy)

