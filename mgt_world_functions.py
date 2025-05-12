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
def generate_world_input_dictionary(parms, world_id):
    world_input_list = du.get_world_input(parms.db_name, world_id)
    input_dictionary = {
        'world_id':         world_input_list[0],
        'location_orbit':   world_input_list[1],
        'size':             world_input_list[2],
        'atmosphere':       world_input_list[3],
        'hydrographics':    world_input_list[4],
        'population':       world_input_list[5],
        'government':       world_input_list[6],
        'law':              world_input_list[7],
        'tech_level':       world_input_list[8],
        'remarks':          world_input_list[9],
        'pop_mod':          world_input_list[10],
        'temperature':      world_input_list[11],
        'density':          world_input_list[12],
        'gravity':          world_input_list[13],
        'cx':               world_input_list[14],
        'importance':       world_input_list[15],
        'main_world':       world_input_list[16]
    }
    return input_dictionary


def build_world_climate(parms, world_input_dictionary):
    world_climate = mgt_world_objects.World_Climate(parms, world_input_dictionary)
    world_climate.generate_axial_tilt()
    du.update_world_climate(parms.db_name, world_climate)  # writes instance to DB

def build_world_biology(parms, world_input_dictionary):
    world_biology = mgt_world_objects.World_Biology(parms, world_input_dictionary)
    world_biology.generate_biomass()
    world_biology.generate_biocomplexity()
    world_biology.generate_biodiversity()
    world_biology.generate_compatibility()
    world_biology.generate_resource()
    world_biology.generate_habitability()
    du.update_world_biology(parms.db_name, world_biology)  # writes instance to DB

def build_world_population(parms, world_input_dictionary):
    world_population = mgt_world_objects.World_Population(parms, world_input_dictionary)
    if world_input_dictionary['main_world'] == 1:
        world_population.generate_population_concentration()
        world_population.generate_urban_pct()
        world_population.generate_major_cities_stats()
        du.update_world_population(parms.db_name, world_population)  # writes instance to DB

def build_world_culture(parms, world_input_dictionary):
    world_culture = mgt_world_objects.World_Culture_Mongoose(parms, world_input_dictionary)
    if world_input_dictionary['main_world'] == 1:
        world_culture.generate_diversity()
        world_culture.generate_xenophilia()
        world_culture.generate_social_cohesion()
        world_culture.generate_progressiveness()
        world_culture.generate_expansionism()
        world_culture.generate_militancy()
        du.update_world_culture(parms.db_name, world_culture)  # writes instance to DB


def build_each_world(parms, world_id):
    logging.info(f'Building system: {world_id}')
    world_input_dictionary = generate_world_input_dictionary(parms, world_id)
    build_world_climate(parms, world_input_dictionary)
    build_world_biology(parms, world_input_dictionary)
    build_world_population(parms, world_input_dictionary)
    build_world_culture(parms, world_input_dictionary)

def build_world_details(parms: Parameters):
    world_list = du.get_world_number_list(parms.db_name)
    for each_world in world_list:
        build_each_world(parms, each_world)

