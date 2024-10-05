import logging
import random

from bodies import Parameters
import database_utils as du
import generic_functions as gf
import build_functions as bf
import build_world_functions as bw

logging.basicConfig(
#    filename='stellar_build.log',
    level=logging.DEBUG,
    format ='%(asctime)s - %(levelname)s - %(message)s'
)

parms = Parameters(
    db_name='brock_3.db',
    build=0,
    frequency=2,
    random_seed=3)

random.seed(parms.random_seed)
du.create_sql_tables(parms)
subsector_dy, location_list = gf.get_location_details()

for each_location in location_list:

    logging.info(f'{each_location}')
    subsector = subsector_dy[each_location]

    if bf.system_present(parms, each_location):
        bf.build_system(parms, each_location, subsector)
        bw.build_worlds(parms, each_location)






