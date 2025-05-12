import sqlite3
import time
import logging



def re_connect_to_db(c, conn, db_name):
    logging.info('Lost connection to DB')
    logging.info('Reconnecting...')
    time.sleep(2)
    conn.commit()
    c.close()
    conn.close()
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    return c, conn


def create_dice_rolls_table(db_name: str):
    # Creates the stellar_bodies table in the database named db_name
    sql_create_dice_rolls = '''
    CREATE TABLE dice_rolls(
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         location TEXT,
         number INTEGER,
         reason TEXT,
         dice_result INTEGER,
         table_result TEXT)
    '''

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    try:
        c.execute('DROP TABLE IF EXISTS dice_rolls')
        c.execute(sql_create_dice_rolls)
        conn.commit()
    finally:
        c.close()
        conn.close()


def insert_dice_rolls(db_name: str, dice_details: object):
    sql_insert_dice_details = '''
    INSERT INTO dice_rolls
    (location,
    number,
    reason,
    dice_result,
    table_result)
    VALUES (?,?,?,?,?)
    '''

    values_to_insert = (
        dice_details.location,
        dice_details.number,
        dice_details.reason,
        dice_details.dice_result,
        dice_details.table_result
    )

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    try:
        c.execute(sql_insert_dice_details, values_to_insert)

    except:
        c, conn = re_connect_to_db(c, conn, db_name)
        c.execute(sql_insert_dice_details, values_to_insert)

    finally:

        conn.commit()
        c.close()
        conn.close()


def create_star_details_table(db_name: str):
    # Creates the stellar_bodies table in the database named db_name
    sql_create_star_details = '''
    CREATE TABLE star_details(
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         location TEXT,
         designation INTEGER,
         star_type TEXT,
         star_subtype INTEGER,
         star_class TEXT,
         orbit_class TEXT,
         generation_type TEXT,
         orbit_number REAL,
         stars_orbited INT,
         orbit_eccentricity REAL,
         orbit_au REAL,
         orbit_min REAL,
         orbit_max REAL,
         orbit_period REAL,
         star_mass REAL,
         binary_mass REAL,
         star_temperature REAL,
         star_diameter REAL,
         star_luminosity REAL,
         binary_luminosity REAL,
         star_age REAL,
         minimum_allowable_orbit_number REAL,
         maximum_allowable_orbit_number REAL,
         restricted_close_orbit_start REAL,
         restricted_close_orbit_end REAL,
         restricted_near_orbit_start REAL,
         restricted_near_orbit_end REAL,
         restricted_far_orbit_start REAL,
         restricted_far_orbit_end REAL,
         orbit_number_range FLOAT,
         habitable_zone_center REAL,
         total_star_orbits INTEGER)
    '''

    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        c.execute('DROP TABLE IF EXISTS star_details')
        c.execute(sql_create_star_details)
        conn.commit()
    finally:
        c.close()
        conn.close()


def insert_star_details(star_details: object):
    sql_insert_star_details = '''
    INSERT INTO star_details
    (location,
    designation,
    star_type,
    star_subtype,
    star_class,
    orbit_class,
    generation_type,
    orbit_number,
    stars_orbited,
    orbit_eccentricity,
    orbit_au,
    orbit_min,
    orbit_max,
    orbit_period,
    star_mass,
    binary_mass,
    star_temperature,
    star_diameter,
    star_luminosity,
    binary_luminosity,
    star_age,
    minimum_allowable_orbit_number,
    maximum_allowable_orbit_number,
    restricted_close_orbit_start,
    restricted_close_orbit_end,
    restricted_near_orbit_start,
    restricted_near_orbit_end,
    restricted_far_orbit_start,
    restricted_far_orbit_end,
    orbit_number_range,
    habitable_zone_center,
    total_star_orbits)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    '''
    values_to_insert = (
        star_details.location,
        star_details.designation,
        star_details.star_type,
        star_details.star_subtype,
        star_details.star_class,
        star_details.orbit_class,
        star_details.generation_type,
        star_details.orbit_number,
        star_details.stars_orbited,
        star_details.orbit_eccentricity,
        star_details.orbit_au,
        star_details.orbit_min,
        star_details.orbit_max,
        star_details.orbit_period,
        star_details.star_mass,
        star_details.binary_mass,
        star_details.star_temperature,
        star_details.star_diameter,
        star_details.star_luminosity,
        star_details.binary_luminosity,
        star_details.star_age,
        star_details.minimum_allowable_orbit_number,
        star_details.maximum_allowable_orbit_number,
        star_details.restricted_close_orbit_start,
        star_details.restricted_close_orbit_end,
        star_details.restricted_near_orbit_start,
        star_details.restricted_near_orbit_end,
        star_details.restricted_far_orbit_start,
        star_details.restricted_far_orbit_end,
        star_details.orbit_number_range,
        star_details.habitable_zone_center,
        star_details.total_star_orbits
        )

    conn = sqlite3.connect(star_details.db_name)
    c = conn.cursor()

    try:
        c.execute(sql_insert_star_details, values_to_insert)
        conn.commit()
    except:
        c, conn = re_connect_to_db(c, conn, star_details.db_name)
        c.execute(sql_insert_star_details, values_to_insert)

    finally:
        conn.commit()
        c.close()
        conn.close()


def create_system_details_table(db_name: str):
    # Creates the system details table in the database named db_name
    sql_create_system_table = '''
    CREATE TABLE system_details(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location TEXT,
        subsector TEXT,
        system_age REAL,
        number_of_gas_giants INT,
        number_of_planetoid_belts INT,
        number_of_terrestrial_planets INT,

        total_system_orbits INT,
        baseline_number INT,
        baseline_orbit_number REAL,
        empty_orbits INT,
        orbit_spread FLOAT,
        anomalous_orbits INT)
    '''

    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        c.execute('DROP TABLE IF EXISTS system_details')
        c.execute(sql_create_system_table)
        conn.commit()
    finally:
        c.close()
        conn.close()


def insert_system_details(system_details: object):
    sql_insert_system_details = '''
    INSERT INTO system_details
    (location,
    subsector,
    system_age,
    number_of_gas_giants,
    number_of_planetoid_belts,
    number_of_terrestrial_planets,

    total_system_orbits,
    baseline_number,
    baseline_orbit_number,
    empty_orbits,
    orbit_spread,
    anomalous_orbits)
    VALUES (?,?,?,?,? ,?,?,?,?,?, ?,?)
    '''
    values_to_insert = (
        system_details.location,
        system_details.subsector,
        system_details.system_age,
        system_details.number_of_gas_giants,
        system_details.number_of_planetoid_belts,
        system_details.number_of_terrestrial_planets,
        system_details.total_system_orbits,
        system_details.baseline_number,
        system_details.baseline_orbit_number,
        system_details.empty_orbits,
        system_details.orbit_spread,
        system_details.anomalous_orbits)

    conn = sqlite3.connect(system_details.db_name)
    c = conn.cursor()
    try:
        c.execute(sql_insert_system_details, values_to_insert)
        conn.commit()

    except:
        c, conn = re_connect_to_db(c, conn, system_details.db_name)
        c.execute(sql_insert_system_details, values_to_insert)

    finally:

        conn.commit()
        c.close()
        conn.close()

def create_orbit_details_table(db_name: str):
    # Creates the world details table in the database named db_name
    sql_create_orbit_table = '''
    CREATE TABLE orbit_details(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location TEXT,
        orbit_slot INT,
        star_orbit_class TEXT,
        orbit_number REAL,
        orbit_au REAL,
        world_type TEXT,
        stars_orbited INT,
        stars_orbited_mass FLOAT,
        orbit_eccentricity REAL,
        orbit_period FLOAT
    )
    '''
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    try:
        c.execute('DROP TABLE IF EXISTS orbit_details')
        c.execute(sql_create_orbit_table)
        conn.commit()
    finally:
        c.close()
        conn.close()

def insert_orbit_details(orbit_details: object):
    sql_insert_orbit_details = '''
    INSERT INTO orbit_details
    (location,
    orbit_slot,
    star_orbit_class,
    orbit_number,
    orbit_au,
    world_type,
    stars_orbited,
    stars_orbited_mass,
    orbit_eccentricity,
    orbit_period)
    VALUES (?,?,?,?,?,?,?,?,?,?)
    '''

    values_to_insert = (
        orbit_details.location,
        orbit_details.orbit_slot,
        orbit_details.star_orbit_class,
        orbit_details.orbit_number,
        orbit_details.orbit_au,
        orbit_details.world_type,
        orbit_details.stars_orbited,
        orbit_details.stars_orbited_mass,
        orbit_details.orbit_eccentricity,
        orbit_details.orbit_period
    )

    conn = sqlite3.connect(orbit_details.db_name)
    c = conn.cursor()
    try:
        c.execute(sql_insert_orbit_details, values_to_insert)

    except:
        c, conn = re_connect_to_db(c, conn, orbit_details.db_name)
        c.execute(sql_insert_orbit_details, values_to_insert)

    finally:

        conn.commit()
        c.close()
        conn.close()



def get_star_info(parms, system_location):
    sql_select_star = '''
    SELECT 
        designation,
        orbit_class,
        minimum_allowable_orbit_number,
        maximum_allowable_orbit_number,
        restricted_close_orbit_start,
        restricted_close_orbit_end,
        restricted_near_orbit_start,
        restricted_near_orbit_end,
        restricted_far_orbit_start,
        restricted_far_orbit_end,
        orbit_number_range,
        habitable_zone_center,
        total_star_orbits
    FROM star_details WHERE location = ?
    '''
    conn = sqlite3.connect(parms.db_name)
    c = conn.cursor()

    try:
        c.execute(sql_select_star, (system_location,))
        rows = c.fetchall()  # Fetch all results
    finally:
        c.close()

    conn.close()

    star_info_list = []
    if rows:
        column_names = [description[0] for description in c.description]
        for row in rows:
            star_info = dict(zip(column_names, row))
            star_info_list.append(star_info)

    return star_info_list


def update_orbit_details_in_system(parms, system):
    #  Updates the baseline orbit number and orbit spread after the worlds have been created
    sql_update_details = '''
    UPDATE system_details
    SET baseline_orbit_number = ?,
        orbit_spread = ?
    WHERE location = ?
    '''

    values_to_update = (
        system.baseline_orbit_number,
        system.orbit_spread,
        system.location
    )
    logging.info(f'Updating system_details {values_to_update}')
    conn = sqlite3.connect(parms.db_name)
    c = conn.cursor()

    try:
        c.execute(sql_update_details, values_to_update)
        conn.commit()
    finally:
        c.close()

    conn.close()



def update_star_table(star):
    insert_star_details(star)


def get_locations(db_name):
    sql_select_location = """SELECT location FROM star_details GROUP BY location"""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        c.execute(sql_select_location)
        rows = c.fetchall()  # Fetch all results
    finally:
        c.close()

    conn.close()

    location_list = []
    if rows:
        for row in rows:
            location_list.append(row[0])
    return location_list


def get_subsector_locations(db_name, subsector):
    sql_select_location = """SELECT location FROM system_details WHERE subsector = ? GROUP BY location """
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        c.execute(sql_select_location, subsector)
        rows = c.fetchall()  # Fetch all results
    finally:
        c.close()

    conn.close()

    location_list = []
    if rows:
        for row in rows:
            location_list.append(row[0])
    return location_list

def get_star_list(db_name, location):
    sql_star_list = """SELECT  *
    FROM star_details WHERE location = ?"""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    try:
        c.execute(sql_star_list, (location,))
        rows = c.fetchall()  # Fetch all results
    finally:
        c.close()


    conn.close()

    star_list = []
    if rows:
        column_names = [description[0] for description in c.description]
        for row in rows:
            star_info = dict(zip(column_names, row))
            star_list.append(star_info)

    return star_list

def get_world_number_list(db_name):
    sql_world_number_list = """SELECT id FROM world"""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    try:
        c.execute(sql_world_number_list)
        rows = c.fetchall()  # Fetch all results
    finally:
        c.close()


    conn.close()

    world_list = []
    if rows:
        for row in rows:
            world_list.append(row[0])

    return world_list

def update_world_climate(db_name, world_climate):
    sql_update_details = '''
       INSERT INTO world_climate (world_id, axial_tilt)
       VALUES (?,?)
       '''

    values_to_update = (
        world_climate.world_id,
        world_climate.axial_tilt
    )

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    try:
        c.execute(sql_update_details, values_to_update)
        conn.commit()
        logging.info(f'Updating world_climate details {values_to_update}')
    except:
        c.close()
        conn.close()
        re_connect_to_db(c, conn, db_name)
        c.execute(sql_update_details, values_to_update)
        conn.commit()
        logging.info(f'Updating world_climate details {values_to_update}')

    finally:
        c.close()

    conn.close()

def update_world_biology(db_name, world_biology):
    sql_update_details = '''
       INSERT INTO world_biology (world_id, biomass_rating, biocomplexity_rating, biodiversity_rating,
       compatibility_rating, resource_rating, habitability_rating)
       VALUES (?,?,?,?,?,?,?)
       '''

    values_to_update = (

        world_biology.world_id,
        world_biology.biomass_rating,
        world_biology.biocomplexity_rating,
        world_biology.biodiversity_rating,
        world_biology.compatibility_rating,
        world_biology.resource_rating,
        world_biology.habitability_rating
    )

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    try:
        c.execute(sql_update_details, values_to_update)
        conn.commit()
        logging.info(f'Updating world_biology details {values_to_update}')
    except:
        c.close()
        conn.close()
        re_connect_to_db(c, conn, db_name)
        c.execute(sql_update_details, values_to_update)
        conn.commit()
        logging.info(f'Re-updating world_biology details {values_to_update}')

    finally:
        c.close()

    conn.close()


def update_world_population(db_name, world_biology):
    sql_update_details = '''
       INSERT INTO world_population (world_id, population_concentration, urban_pct,
       major_cities_total, major_cities_population_total)
       VALUES (?,?,?,?,?)
       '''

    values_to_update = (
        world_biology.world_id,
        world_biology.population_concentration,
        world_biology.urban_pct,
        world_biology.major_cities_total,
        world_biology.major_cities_population_total
    )

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    try:
        c.execute(sql_update_details, values_to_update)
        conn.commit()

    except:
        c.close()
        conn.close()
        re_connect_to_db(c, conn, db_name)
        c.execute(sql_update_details, values_to_update)
        conn.commit()
        logging.info(f'Re-updating world_biology details {values_to_update}')

    finally:
        c.close()

    conn.close()

def update_world_culture(db_name, world_culture):
    sql_update_details = '''
       INSERT INTO world_culture_mongoose (world_id, diversity, xenophilia, social_cohesion,
       progressiveness, expansionism, militancy)
       VALUES (?,?,?,?,?,?,?)
       '''

    values_to_update = (
        world_culture.world_id,
        world_culture.diversity,
        world_culture.xenophilia,
        world_culture.social_cohesion,
        world_culture.progressiveness,
        world_culture.expansionism,
        world_culture.militancy

    )

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    try:
        c.execute(sql_update_details, values_to_update)
        conn.commit()

    except:
        c.close()
        conn.close()
        re_connect_to_db(c, conn, db_name)
        c.execute(sql_update_details, values_to_update)
        conn.commit()
        logging.info(f'Re-updating world_biology details {values_to_update}')

    finally:
        c.close()

    conn.close()


def get_world_input(db_name, world_id):

    sql_statement = '''SELECT
    w.id, w.location_orbit, ts.size, ts.atmosphere, ts.hydrographics, ts.population, ts.government, ts.law, ts.tech_level, 
    ss.remarks, SUBSTR(ss.pbg, 1, 1) AS pop_mod, ob.temperature, ob.density, ob.gravity, ss.cx, ss.ix, w.main_world
    FROM world w
    LEFT JOIN traveller_stats ts
    ON ts.location_orb = w.location_orbit
    LEFT JOIN
    orbital_bodies ob
    ON ob.location_orbit = w.location_orbit
    LEFT JOIN
    system_stats ss
    ON ss.location = w.location
    WHERE w.id = ?
    '''


    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute(sql_statement, (world_id,))
    answers = c.fetchall()

    return answers[0]

def get_world_pcr(db_name, world_id):

    sql_statement = '''SELECT population_concentration
    FROM world_population w
    WHERE w.world_id = ?
    '''

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute(sql_statement, (world_id,))
    answers = c.fetchall()

    return answers[0]