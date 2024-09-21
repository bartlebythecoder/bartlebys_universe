import sqlite3


def create_system_details_table(db_name: str):
    # Creates the system details table in the database named db_name
    sql_create_system_table = '''
    CREATE TABLE system_details(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location TEXT,
        subsector TEXT,
        system_age REAL,
        primary_star_class TEXT,
        number_of_stars_in_system INT,
        stars_in_system TEXT,
        number_of_gas_giants INT,
        number_of_planetoid_belts INT,
        number_of_terrestrial_planets INT,
        minimum_allowable_orbit_number REAL,
        restricted_orbits TEXT
    )
    '''

    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS system_details')
    c.execute(sql_create_system_table)
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
         habitable_zone_center INTEGER)
    '''

    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS star_details')
    c.execute(sql_create_star_details)
    conn.commit()
    c.close()
    conn.close()


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
    c.execute('DROP TABLE IF EXISTS dice_rolls')
    c.execute(sql_create_dice_rolls)
    conn.commit()
    c.close()
    conn.close()


def insert_system_details(system_details: object):
    sql_insert_system_details = '''
    INSERT INTO system_details
    (location,
    subsector,
    system_age,
    primary_star_class,
    number_of_stars_in_system,
    stars_in_system,
    number_of_gas_giants,
    number_of_planetoid_belts,
    number_of_terrestrial_planets,
    minimum_allowable_orbit_number,
    restricted_orbits)
    VALUES (?,?,?,?,?,?,?,?,?,?,?)
    '''
    values_to_insert = (
        system_details.location,
        system_details.subsector,
        system_details.system_age,
        system_details.primary_star_class,
        system_details.number_of_stars_in_system,
        str(system_details.stars_in_system),
        system_details.number_of_gas_giants,
        system_details.number_of_planetoid_belts,
        system_details.number_of_terrestrial_planets,
        system_details.minimum_allowable_orbit_number,
        str(system_details.restricted_orbits)
    )

    conn = sqlite3.connect(system_details.db_name)
    c = conn.cursor()
    c.execute(sql_insert_system_details, values_to_insert)
    conn.commit()
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
    star_age,
    minimum_allowable_orbit_number,
    maximum_allowable_orbit_number,
    restricted_close_orbit_start,
    restricted_close_orbit_end,
    restricted_near_orbit_start,
    restricted_near_orbit_end,
    restricted_far_orbit_start,
    restricted_far_orbit_end,
    orbit_number_range)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
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
        star_details.star_age,
        star_details.minimum_allowable_orbit_number,
        star_details.maximum_allowable_orbit_number,
        star_details.restricted_close_orbit_start,
        star_details.restricted_close_orbit_end,
        star_details.restricted_near_orbit_start,
        star_details.restricted_near_orbit_end,
        star_details.restricted_far_orbit_start,
        star_details.restricted_far_orbit_end,
        star_details.orbit_number_range
        )

    conn = sqlite3.connect(star_details.db_name)
    c = conn.cursor()
    c.execute(sql_insert_star_details, values_to_insert)
    conn.commit()
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
    c.execute(sql_insert_dice_details, values_to_insert)
    conn.commit()
    c.close()
    conn.close()


def create_sql_tables(parms):
    create_system_details_table(parms.db_name)
    create_star_details_table(parms.db_name)
    create_dice_rolls_table(parms.db_name)


def update_star_table(star):
    insert_star_details(star)

