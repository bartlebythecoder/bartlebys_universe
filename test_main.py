import logging
import random

import database_utils as du
import bodies
import star_functions as sf
import generic_functions as gf
import build_functions as bf

logging.basicConfig(
#    filename='stellar_build.log',
    level=logging.DEBUG,
    format ='%(asctime)s - %(levelname)s - %(message)s'
)

parms = bodies.Parameters('brock_3.db', 0, 2, 3)
random.seed(parms.random_seed)
logging.info(f'{parms.db_name} created')

du.create_sql_tables(parms)
subsector_dy, location_list = gf.get_location_details()

for each_location in location_list:
    logging.info(f'{each_location}')
    subsector = subsector_dy[each_location]
    stars_in_system = 0

    if sf.system_present(parms, each_location):
        primary_star, stars_in_system = bf.build_stars(each_location, stars_in_system, parms)
        new_system = bf.build_system(primary_star, stars_in_system, subsector, parms)




