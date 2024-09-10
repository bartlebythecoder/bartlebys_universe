import logging
import string
import random

import database_utils as du
import bodies
import star_functions as sf

logging.basicConfig(
#    filename='stellar_build.log',
    level=logging.DEBUG,
    format =' %(asctime)s - %(levelname)s - %(message)s'
)


def log_star(star: object):
    logging.info(
        f'{star.location},{star.star_class} {star.star_type}{star.star_subtype} '
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
for subsector in subsector_list:
    locations = sf.get_subsector_number_list(subsector)
    location_list += locations

location_list.sort()

for each_location in location_list:
    logging.info(f'Looking {each_location}')

    if sf.system_present(parms, each_location):
        primary_star = sf.populate_primary(parms, each_location)
        primary_companion = None
        if sf.check_multiple_star(primary_star):
            primary_companion = sf.populate_companion(primary_star)
            primary_star.designation += 'a'

        du.insert_star_details(primary_star)
        log_star(primary_star)

        if primary_companion is not None:
            du.insert_star_details(primary_companion)
            log_star(primary_companion)

        if sf.check_multiple_star(primary_star) and primary_star.star_class not in ['Ia','Ib','II','III']:
            # close secondary
            secondary_close_companion = None
            star_designation = 'B'
            next_designation = 'C'
            logging.info(f'Found Close Secondary {star_designation} {each_location}')
            secondary_close = sf.populate_secondary(primary_star, 'close')
            secondary_close.designation = star_designation
            secondary_close.orbit_category = star_designation

            if sf.check_multiple_star(secondary_close):
                secondary_close_companion = sf.populate_companion(secondary_close)
                secondary_close.designation += 'a'

            du.insert_star_details(secondary_close)
            log_star(secondary_close)

            if secondary_close_companion is not None:
                du.insert_star_details(secondary_close_companion)
                log_star(secondary_close_companion)

        else:
            next_designation = 'B'

        if sf.check_multiple_star(primary_star):
            # near secondary
            secondary_near_companion = None
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

            if sf.check_multiple_star(secondary_near):
                secondary_near_companion = sf.populate_companion(secondary_near)
                secondary_near.designation += 'a'

            du.insert_star_details(secondary_near)
            log_star(secondary_near)

            if secondary_near_companion is not None:
                du.insert_star_details(secondary_near_companion)
                log_star(secondary_near_companion)


        if sf.check_multiple_star(primary_star):
            # far secondary
            secondary_far_companion = None
            star_designation = next_designation
            logging.info(f'Found Far Secondary {star_designation}')
            secondary_far = sf.populate_secondary(primary_star, 'far')
            secondary_far.designation = star_designation
            secondary_far.orbit_category = star_designation


            if sf.check_multiple_star(secondary_far):
                secondary_far_companion = sf.populate_companion(secondary_far)
                secondary_far.designation += 'a'

            du.insert_star_details(secondary_far)
            log_star(secondary_far)

            if secondary_far_companion is not None:
                du.insert_star_details(secondary_far_companion)
                log_star(secondary_far_companion)


        new_system = bodies.System(
            db_name=parms.db_name,
            build=parms.build,
            location=each_location,
            subsector=subsector,
            system_age=primary_star.star_age
        )

        du.insert_system_details(new_system)


