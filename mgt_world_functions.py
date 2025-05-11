import logging
import math
import random

import mgt_world_objects
import mgt_world_objects as mgt_worlds
import database_utils as du
import generic_functions as gf
from bodies import Parameters, DiceRoll


def build_tu_world_details(parms: Parameters):
    #   This function builds out BU tables for legacy TU worlds
    #   Assumes the world and world_uwp table is built and populated
    world_list = du.get_world_number_list(parms.db_name)
    for world_id in world_list:
        print(f'World ID present: {world_id}')


##################################################

def build_world_climate(parms, world_id):
    world_climate = mgt_world_objects.World_climate(parms, world_id)
    world_climate.generate_axial_tilt()
    du.update_world_climate(parms.db_name, world_climate)  # writes instance to DB

def build_world_biology(parms, world_id):
    world_biology = mgt_world_objects.World_biology(parms, world_id)
    world_biology.generate_biomass()
    world_biology.generate_biocomplexity()
    world_biology.generate_biodiversity()
    world_biology.generate_compatibility()
    world_biology.generate_resource()
    world_biology.generate_habitability()
    du.update_world_biology(parms.db_name, world_biology)  # writes instance to DB

def build_each_world(parms, world_id):
    logging.info(f'Building system: {world_id}')
    build_world_climate(parms, world_id)
    build_world_biology(parms, world_id)

def build_world_details(parms: Parameters):
    world_list = du.get_world_number_list(parms.db_name)
    for each_world in world_list:
        build_each_world(parms, each_world)

