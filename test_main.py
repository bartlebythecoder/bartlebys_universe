import logging
import string
import random

import database_utils as du
import bodies
import star_functions as sf
import generic_functions as gf

logging.basicConfig(
#    filename='stellar_build.log',
    level=logging.DEBUG,
    format ='%(asctime)s - %(levelname)s - %(message)s'
)


def log_star(star_detail: str, star: bodies.Star):
    logging.info(
        f'{star.location}, {star_detail}, {star.star_class} {star.star_type}{star.star_subtype} '
        f'Mass: {star.star_mass}, Temp: {star.star_temperature}, Di: {star.star_diameter},'
        f'Lum: {star.star_luminosity:.3g}, Age: {star.star_age} ')


subsector_list = list(string.ascii_uppercase[:16])  # A to P
parms = bodies.Parameters('brock_3.db', 0, 2, subsector_list, 3)
random.seed(parms.random_seed)

du.create_system_details_table(parms.db_name)
du.create_star_details_table(parms.db_name)
du.create_dice_rolls_table(parms.db_name)
logging.info(f'{parms.db_name} created')

location_list = []
subsector_dy = {}
for subsector in subsector_list:
    locations = gf.get_subsector_number_list(subsector)
    location_list += locations
    for each_location in locations:
        subsector_dy[each_location] = subsector

location_list.sort()

for each_location in location_list:
    logging.info(f'{each_location}')
    stars_in_system = 0
    stars_orbited = 0

    if sf.system_present(parms, each_location):
        stars_orbited = 1
        primary_star = sf.populate_primary(parms, each_location)
        primary_companion = None
        stars_in_system += 1
        if sf.check_multiple_star(primary_star):
            primary_companion = sf.populate_companion(primary_star)
            primary_star.binary_mass = primary_star.star_mass + primary_companion.star_mass
            primary_star.designation += 'a'
            primary_companion.stars_orbited = 1
            primary_companion.orbit_period = bodies.calculate_companion_orbit_period(primary_star, primary_companion)

            stars_orbited += 1
            stars_in_system += 1

        du.insert_star_details(primary_star)
        log_star('Primary', primary_star)

        if primary_companion is not None:
            du.insert_star_details(primary_companion)
            log_star('Primary Companion',primary_companion)

        if sf.check_multiple_star(primary_star) and primary_star.star_class not in ['Ia', 'Ib', 'II', 'III']:
            # close secondary
            secondary_close_companion = None
            stars_in_system += 1
            star_designation = 'B'
            next_designation = 'C'
            logging.info(f'Found Close Secondary {star_designation} {each_location}')
            secondary_close = sf.populate_secondary(primary_star, 'close')
            secondary_close.designation = star_designation
            secondary_close.orbit_category = star_designation
            secondary_close.stars_orbited = stars_orbited
            secondary_close.orbit_period = bodies.calculate_secondary_orbit_period(primary_star, secondary_close)

            if sf.check_multiple_star(secondary_close):
                secondary_close_companion = sf.populate_companion(secondary_close)
                secondary_close.binary_mass = secondary_close.star_mass + secondary_close_companion.star_mass
                secondary_close.designation += 'a'
                stars_in_system += 1
                secondary_close_companion.stars_orbited = 1
                secondary_close_companion.orbit_period = (
                    bodies.calculate_companion_orbit_period(secondary_close, secondary_close_companion))

            du.insert_star_details(secondary_close)
            log_star('Close Secondary', secondary_close)

            if secondary_close_companion is not None:
                du.insert_star_details(secondary_close_companion)
                log_star('Close Secondary Companion', secondary_close_companion)

        else:
            next_designation = 'B'

        if sf.check_multiple_star(primary_star):
            # near secondary
            secondary_near_companion = None
            stars_in_system += 1
            if next_designation == 'B':
                star_designation = 'B'
                next_designation = 'C'
            else:
                star_designation = 'C'
                next_designation = 'D'

            logging.info(f'Found Near Secondary {star_designation} {each_location} ')
            secondary_near = sf.populate_secondary(primary_star, 'near')
            secondary_near.designation = star_designation
            secondary_near.orbit_category = star_designation
            secondary_near.stars_orbited = stars_orbited
            secondary_near.orbit_period = bodies.calculate_secondary_orbit_period(primary_star, secondary_near)

            if sf.check_multiple_star(secondary_near):
                secondary_near_companion = sf.populate_companion(secondary_near)
                secondary_near_companion.stars_orbited = 1
                secondary_near.designation += 'a'
                secondary_near.binary_mass = secondary_near.star_mass + secondary_near_companion.star_mass
                stars_in_system += 1
                secondary_near_companion.orbit_period = (
                    bodies.calculate_companion_orbit_period(secondary_near, secondary_near_companion))

            du.insert_star_details(secondary_near)
            log_star('Near Secondary', secondary_near)

            if secondary_near_companion is not None:
                du.insert_star_details(secondary_near_companion)
                log_star('Near Secondary Companion', secondary_near_companion)

        if sf.check_multiple_star(primary_star):
            # far secondary
            secondary_far_companion = None
            stars_in_system += 1
            star_designation = next_designation
            logging.info(f'Found Far Secondary {star_designation}')
            secondary_far = sf.populate_secondary(primary_star, 'far')
            secondary_far.designation = star_designation
            secondary_far.orbit_category = star_designation
            secondary_far.stars_orbited = stars_orbited
            secondary_far.orbit_period = bodies.calculate_secondary_orbit_period(primary_star, secondary_far)

            if sf.check_multiple_star(secondary_far):
                secondary_far_companion = sf.populate_companion(secondary_far)
                secondary_far_companion.stars_orbited = 1
                secondary_far.designation += 'a'
                secondary_far.binary_mass = secondary_far.star_mass + secondary_far_companion.star_mass
                stars_in_system += 1
                secondary_far_companion.orbit_period = (
                    bodies.calculate_companion_orbit_period(secondary_far, secondary_far_companion))

            du.insert_star_details(secondary_far)
            log_star('Far Secondary', secondary_far)

            if secondary_far_companion is not None:
                du.insert_star_details(secondary_far_companion)
                log_star('Far Secondary Companion', secondary_far_companion)

        new_system = bodies.System(
            db_name=parms.db_name,
            build=parms.build,
            location=each_location,
            subsector=subsector_dy[each_location],
            system_age=primary_star.star_age,
            stars_in_system=stars_in_system
        )

        du.insert_system_details(new_system)


