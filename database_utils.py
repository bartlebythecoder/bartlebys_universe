import sqlite3


def create_star_details_table(db_name: str):
    # Creates the stellar_bodies table in the database named db_name
    sql_create_star_details = '''
    CREATE TABLE star_details(
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         location TEXT,
         subsector TEXT,
         multiplicity INTEGER,
         orbit_class TEXT,
         orbit_number INTEGER,
         star_type TEXT,
         star_subtype INTEGER,
         star_class TEXT,
         star_mass INTEGER,
         star_temperature INTEGER,
         star_diameter INTEGER,
         star_luminosity INTEGER,
         system_age INTEGER,
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


def insert_star_details(db_name: str, star_details: object):
    sql_insert_star_details = '''
    INSERT INTO star_details
    (location,
    subsector,
    multiplicity,
    orbit_class,
    orbit_number,
    star_type,
    star_subtype,
    star_class)
    VALUES (?,?,?,?,?,?,?,?)
    '''
    values_to_insert = (
        star_details.location,
        star_details.subsector,
        star_details.multiplicity,
        star_details.orbit_class,
        star_details.orbit_number,
        star_details.star_type,
        star_details.star_subtype,
        star_details.star_class

        )

    conn = sqlite3.connect(db_name)
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