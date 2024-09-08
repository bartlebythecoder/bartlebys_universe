import logging
import string

import database_utils as du
import bodies
import star_functions as sf

logging.basicConfig(level=logging.DEBUG, format =' %(asctime)s - %(levelname)s - %(message)s')

subsector_list = list(string.ascii_uppercase[:16])  # A to P
parms = bodies.Parameters('brock_3.db', 0, 2, subsector_list ,3)

du.create_system_details_table(parms.db_name)
du.create_star_details_table(parms.db_name)
du.create_dice_rolls_table(parms.db_name)
logging.info(f'{parms.db_name} created')

for subsector in subsector_list:

    locations = sf.get_subsector_number_list(subsector)

    for each_location in locations:

        if sf.system_present(parms, each_location):

            primary_star = sf.populate_primary(parms, each_location)
            if sf.check_companion(primary_star):
                primary_star.designation = 'Aa'
                primary_companion = sf.populate_companion(primary_star)


            du.insert_star_details(primary_star)
            logging.info(f'{primary_star.location},{primary_star.star_class} {primary_star.star_type}{primary_star.star_subtype} '
                         f'Mass: {primary_star.star_mass}, Temp: {primary_star.star_temperature}, Di: {primary_star.star_diameter},'
                         f'Lum: {primary_star.star_luminosity:.3g}, Age: {primary_star.star_age} ')


            if primary_star.designation == 'Aa':
                du.insert_star_details(primary_companion)
                logging.info(
                    f'{primary_companion.location},{primary_companion.star_class} {primary_companion.star_type}{primary_companion.star_subtype} '
                    f'Mass: {primary_companion.star_mass}, Temp: {primary_companion.star_temperature}, Di: {primary_companion.star_diameter},'
                    f'Lum: {primary_companion.star_luminosity:.3g}, Age: {primary_companion.star_age} ')


            new_system = bodies.System(
                db_name=parms.db_name,
                build=parms.build,
                location=each_location,
                subsector=subsector,
                system_age=primary_star.star_age
            )

            du.insert_system_details(new_system)


