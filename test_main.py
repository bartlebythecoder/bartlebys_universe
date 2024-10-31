import logging
import random

from bodies import Parameters
from bartlebys_universe import mgt_stellar_functions as mgt_stars
from bartlebys_universe import mgt_system_functions as mgt_systems
from bartlebys_universe import mgt_orbit_functions as mgt_orbits
from bartlebys_universe import mgt_world_functions as mgt_worlds
import database_utils as du

logging.basicConfig(
#    filename='stellar_build.log',
    level=logging.DEBUG,
    format ='%(asctime)s - %(levelname)s - %(message)s'
)

parms = Parameters(
    db_name='brock_88.db',
    build=0,
    frequency=2,
    random_seed=3)

random.seed(parms.random_seed)
du.create_dice_rolls_table(parms.db_name)
#mgt_stars.build_stellar_details(parms)
#mgt_systems.build_system_details(parms)
mgt_orbits.build_orbit_details(parms)









