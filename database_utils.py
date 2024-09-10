import sqlite3


def create_system_details_table(db_name: str):
    # Creates the system details table in the database named db_name
    sql_create_system_table = '''
    CREATE TABLE system_details(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location TEXT,
        subsector TEXT,
        system_age REAL
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
         orbit_category TEXT,
         orbit_class TEXT,
         orbit_number REAL,
         orbit_eccentricity REAL,
         orbit_au REAL,
         orbit_min REAL,
         orbit_max REAL,
         star_type TEXT,
         star_subtype INTEGER,
         star_class TEXT,
         star_mass REAL,
         star_temperature REAL,
         star_diameter REAL,
         star_luminosity REAL,
         star_age REAL,
         gas_giants INTEGER,
         planetoid_belts INTEGER,
         terrestrial_planets INTEGER,
         minimal_orbit_number INTEGER,
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
    system_age)
    VALUES (?,?,?)
    '''
    values_to_insert = (
        system_details.location,
        system_details.subsector,
        system_details.system_age
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
    orbit_category,
    orbit_class,
    orbit_number,
    orbit_eccentricity,
    orbit_au,
    orbit_min,
    orbit_max,
    star_type,
    star_subtype,
    star_class,
    star_mass,
    star_temperature,
    star_diameter,
    star_luminosity,
    star_age)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    '''
    values_to_insert = (
        star_details.location,
        star_details.designation,
        star_details.orbit_category,
        star_details.orbit_class,
        star_details.orbit_number,
        star_details.orbit_eccentricity,
        star_details.orbit_au,
        star_details.orbit_min,
        star_details.orbit_max,
        star_details.star_type,
        star_details.star_subtype,
        star_details.star_class,
        star_details.star_mass,
        star_details.star_temperature,
        star_details.star_diameter,
        star_details.star_luminosity,
        star_details.star_age

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