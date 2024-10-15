import logging
import copy
import sqlite3

import generic_functions as gf
import database_utils as du
import lookup_tables as lu
import mgt_stellar_objects as mgt_star
import mgt_system_objects as mgt_system
from bodies import Parameters, DiceRoll

def populate_system_from_db(parms, location):
    db_name = parms.db_name
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT * 
            FROM system_details 
            WHERE location = ?
            """,
            (location,),
        )
        row = cursor.fetchone()
        if row:
            system = mgt_system.System.__new__(mgt_system.System)
            system.db_name = db_name  # Assuming you want to store the db_name
            system.build = parms.build
            system.location = row[1]  # Index 1 corresponds to the 'location' column
            system.subsector = row[2]
            system.system_age = row[3]
            system.number_of_gas_giants = row[4]
            system.number_of_planetoid_belts = row[5]
            system.number_of_terrestrial_planets = row[6]
            system.total_system_orbits = row[7]
            system.baseline_number = row[8]
            system.baseline_orbit_number = row[9]
            system.empty_orbits = row[10]
            system.orbit_spread = row[11]
            system.anomalous_orbits = row[12]
            system.get_total_worlds()
            return system

        else:
            return None
    finally:
        cursor.close()
        conn.close()


def build_system(system, star_list):
    system.get_subsector()
    system.get_system_age(star_list)
    system.get_number_of_gas_giants(star_list)
    system.get_number_of_planetoid_belts(star_list)
    system.get_number_of_terrestrial_planets(star_list)
    system.get_total_worlds()
    system.get_total_system_orbits(star_list)
    system.get_baseline_number(star_list)
    #system.get_baseline_orbit_number(star_list)
    system.get_empty_orbits()
    #system.get_orbit_spread(star_list)
    system.get_anomalous_orbits()


def build_system_details(parms):
    location_list = du.get_locations(parms.db_name)
    du.create_system_details_table(parms.db_name)
    for each_location in location_list:
        logging.info(f'Building system: {each_location}')
        dy_star_list = du.get_star_list(parms.db_name, each_location)  # SELECT results into dy
        star_list = mgt_star.get_star_list_from_dy_list(parms, dy_star_list)  # Converts dy list to object list
        new_system = mgt_system.System(parms, each_location)  # Creates instance
        build_system(new_system, star_list) # populates instance
        du.insert_system_details(new_system)  # writes instance to DB


