import logging
import string
import random

import database_utils as du
import bodies
import star_functions as sf

logging.basicConfig(level=logging.DEBUG, format =' %(asctime)s - %(levelname)s - %(message)s')

# Parameters
db_name = 'brock_3.db'
build = 0
frequency = 2
subsector_list = list(string.ascii_uppercase[:16])  # A to P
random.seed(3)

du.create_star_details_table(db_name)
du.create_dice_rolls_table(db_name)
logging.info(f'{db_name} created')

for subsector in subsector_list:

    locations = sf.get_subsector_number_list(subsector)

    for each_location in locations:

        if sf.system_present(frequency, db_name, each_location):
            new_star = bodies.Star
            new_star.db_name = db_name
            new_star.build = build
            new_star.location = each_location
            new_star.subsector = subsector
            new_star.multiplicity = 0
            new_star.orbit_class = 'primary'
            new_star.orbit_number = 0
            new_star.star_type = sf.get_star_type(new_star)
            new_star.star_class = sf.get_star_class(new_star)

            if new_star.star_type == 'Special':
                new_star.star_type = sf.get_special_star_type(new_star)

            new_star.star_subtype = random.randint(0, 9)

            logging.info(f'{new_star.location} created')
            du.insert_star_details(db_name, new_star)
