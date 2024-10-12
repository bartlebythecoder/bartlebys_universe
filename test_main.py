import logging
import random

from bodies import Parameters
from bartlebys_universe import mgt_stellar_functions as mgt_stars
from bartlebys_universe import mgt_system_functions as mgt_systems
import database_utils as du

logging.basicConfig(
#    filename='stellar_build.log',
    level=logging.DEBUG,
    format ='%(asctime)s - %(levelname)s - %(message)s'
)

parms = Parameters(
    db_name='brock_6.db',
    build=0,
    frequency=2,
    random_seed=3)

random.seed(parms.random_seed)
du.create_dice_rolls_table(parms.db_name)
#mgt_stars.build_stellar_details(parms)
mgt_systems.build_system_details(parms)








