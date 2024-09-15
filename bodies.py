from dataclasses import dataclass
import random
import logging
import math

import generic_functions as gf
import database_utils as du
import lookup_tables as lu

UNDEFINED_VALUE = -99
UNDEFINED_CATEGORY = 'XX'


@dataclass
class DiceRoll:
    location: str
    number: int
    reason: str
    dice_result: float
    table_result: str


@dataclass
class Parameters:
    db_name: str
    build: int
    frequency: int  # for checking if system is present
    random_seed: int


@dataclass
class System:
    db_name: str
    build: int
    location: str
    subsector: str
    system_age: float
    stars_in_system: int


@dataclass
class Star:
    db_name: str
    build: int
    location: str
    designation: str
    orbit_category: str
    orbit_class: str
    generation_type: str
    orbit_number: float
    stars_orbited: int
    orbit_eccentricity: float
    orbit_au: float
    orbit_min: float
    orbit_max: float
    orbit_period: float
    star_type: str
    star_subtype: int
    star_class: str
    star_mass: float
    binary_mass: float
    star_temperature: float
    star_diameter: float
    star_luminosity: float
    star_age: float
    gas_giants: int
    planetoid_belts: int
    terrestrial_planets: int
    minimal_orbit_number: int
    habitable_zone_center: int

    def __init__(self, parms: Parameters, each_location: str):
        # Initialize attributes with provided values
        self.db_name = parms.db_name
        self.build = parms.build
        self.location = each_location
        self.designation = 'A'
        self.orbit_category = 'A'
        self.orbit_class = 'primary'
        self.generation_type = 'primary'
        self.orbit_number = 0
        self.stars_orbited = 0
        self.orbit_eccentricity = 0
        self.orbit_au = 0
        self.orbit_min = 0
        self.orbit_max = 0
        self.orbit_period = 0

        # Initialize attributes with default undefined values
        self.star_type = UNDEFINED_CATEGORY
        self.star_subtype = UNDEFINED_VALUE
        self.star_class = UNDEFINED_CATEGORY
        self.star_mass = UNDEFINED_VALUE
        self.binary_mass = UNDEFINED_VALUE
        self.star_temperature = UNDEFINED_VALUE
        self.star_diameter = UNDEFINED_VALUE
        self.star_luminosity = UNDEFINED_VALUE
        self.star_age = UNDEFINED_VALUE

        # Not yet included
        self.gas_giants = UNDEFINED_VALUE
        self.planetoid_belts = UNDEFINED_VALUE
        self.terrestrial_planets = UNDEFINED_VALUE
        self.minimal_orbit_number = UNDEFINED_VALUE
        self.habitable_zone_center = UNDEFINED_VALUE

        # Call methods to populate attributes based on logic
        self.get_star_type()
        self.get_star_class()

        if self.star_type == 'Special':
            self.get_special_star_type()

        self.get_star_subtype()
        self.get_star_mass()
        self.binary_mass = self.star_mass
        self.get_star_temperature()
        self.get_star_diameter()
        self.get_star_luminosity()
        self.get_star_age()

    def update_from_companion(self, companion):
        # Update binary_mass and designation due to a companion being added
        self.designation += 'a'
        self.binary_mass = self.star_mass + companion.star_mass

    def get_hot_star_type(self):
        # if the original get_star_type function returns a hot star, this function is used to return a star type
        dice = gf.roll_dice(2)
        dice_info = DiceRoll(
            location=self.location,
            number=2,
            reason='hot star type',
            dice_result=dice,
            table_result=lu.mgt2e_hot_star_type_dy[dice])

        du.insert_dice_rolls(self.db_name, dice_info)
        self.star_type = dice_info.table_result

    def get_star_type(self):
        # returns the star type after being provided the current star details

        star_type_dy = lu.mgt2e_standard_star_type_dy

        dice = gf.roll_dice(2)
        dice_info = DiceRoll(
            location=self.location,
            number=2,
            reason='star type',
            dice_result=dice,
            table_result=star_type_dy[dice])
        du.insert_dice_rolls(self.db_name, dice_info)

        if dice_info.table_result == 'Hot':
            self.get_hot_star_type()
        else:
            self.star_type = dice_info.table_result

    def get_special_star_type(self):
        # if get_star_type returns a special star, use the class to return the final star type

        star_type_dy = lu.mgt2e_standard_star_type_dy
        dice = gf.roll_dice(2) + 1

        # Special rule for IV luminosity stars
        if self.star_class == 'IV':
            if 3 <= dice <= 6:
                dice += 5

        dice_info = DiceRoll(
            location=self.location,
            number=2,
            reason='special star type (with mods)',
            dice_result=dice,
            table_result=star_type_dy[dice])
        du.insert_dice_rolls(self.db_name, dice_info)

        self.star_type = star_type_dy[dice]

        if dice_info.table_result == 'Hot':
            logging.info('Special and Hot Found')
            self.get_hot_star_type()

        # More special rules
        if self.star_class == 'IV' and self.star_type == 'O':
            self.star_type = 'B'

        if self.star_class == 'VI' and self.star_type == 'F':
            self.star_type = 'G'

        if self.star_class == 'VI' and self.star_type == 'A':
            self.star_type = 'B'

    def get_previous_star_type(self, original_type):
        # returns a "lower" star class from the one provided
        # used for sibling companions
        type_list = ['O', 'B', 'A', 'F', 'G', 'K', 'M']
        try:
            index = type_list.index(original_type)
            if index < 6:  # Check if it's not the first element
                logging.info(f'Getting previous star type. Was {original_type} now {type_list[index + 1]}')
                self.star_type = type_list[index + 1]
            else:
                logging.info(f'Getting previous star class. Keeping {type_list[6]}')
                self.star_type = type_list[6]

        except Exception as e:
            logging.info(f'Previous Star Type Error {e}')
            self.star_type = 'X'

    def get_other_star_type(self):
        dice_roll = gf.roll_dice(2)
        dice_info = DiceRoll(
            location=self.location,
            number=2,
            reason='Other Star Type',
            dice_result=dice_roll,
            table_result=dice_roll)
        du.insert_dice_rolls(self.db_name, dice_info)

        if dice_roll <= 7:
            self.star_type = 'D'
            self.star_class = 'D'
        else:
            self.star_type = 'BD'
            self.star_class = 'BD'

    def get_non_primary_star_type(self, main, companion_category):

        if companion_category == 'twin':
            self.star_type = main.star_type

        elif companion_category == 'sibling':
            self.star_type = main.star_type
        elif companion_category == 'lesser':
            self.get_previous_star_type(main.star_type)
        elif companion_category == 'random':
            self.get_star_type()
            if is_hotter(self, main) or self.star_type == 'Special':
                self.get_previous_star_type(main.star_type)
        elif companion_category == 'other':
            self.get_other_star_type()

    def get_star_subtype(self):
        if self.star_class == 'IV' and self.star_type == 'K':
            dice_roll = random.randint(0, 4)
            self.star_subtype = dice_roll
            logging.info(f'restricted subtype IV class star {self.star_class} {self.star_type} {self.star_subtype}')
        else:
            dice_roll = random.randint(0, 9)
            self.star_subtype = dice_roll

        dice_info = DiceRoll(
            location=self.location,
            number=0,
            reason='d10 subtype roll',
            dice_result=dice_roll,
            table_result='n/a')
        du.insert_dice_rolls(self.db_name, dice_info)

    def get_sibling_type_subtype(self, main):
        if main.star_type not in ['M', 'D', 'BD']:
            total_dice = 1
            dice = gf.roll_dice(total_dice)
            dice_info = DiceRoll(main.location, total_dice, 'find siblings star type and subtype', dice, str(dice))
            du.insert_dice_rolls(main.db_name, dice_info)
            cooler_star_subtype = main.star_subtype + dice
            if cooler_star_subtype <= 9:
                self.star_subtype = cooler_star_subtype
            else:
                cooler_star_subtype -= 10
                self.star_subtype = cooler_star_subtype
                current_type = self.star_type
                self.get_previous_star_type(self.star_type)
        elif main.star_type in ['M', 'D', 'BD']:
            die = random.randint(main.star_subtype, 9)
            dice_info = DiceRoll(main.location, die, 'M class random subtype', die, str(die))
            du.insert_dice_rolls(main.db_name, dice_info)
            self.star_subtype = die
        else:
            logging.info('Subtype Error')
            self.star_subtype = -1

    def get_non_primary_star_subtype(self, main, companion_category):
        if companion_category == 'twin':
            self.star_subtype = main.star_subtype
        elif companion_category == 'sibling':
            self.get_sibling_type_subtype(main)
        elif companion_category == 'lesser':
            self.get_star_subtype()
        elif companion_category == 'random':
            self.get_star_subtype()

        elif companion_category == 'other':
            self.get_star_subtype()

        if main.star_subtype > self.star_subtype:
            self.star_subtype = main.star_subtype

    def get_giant_star_class(self):
        # if the original get_star_class returns a giant star, use this function to return the class
        dice = gf.roll_dice(2)
        dice_info = DiceRoll(
            location=self.location,
            number=2,
            reason='star class',
            dice_result=dice,
            table_result=lu.mgt2e_giant_star_class_dy[dice])
        du.insert_dice_rolls(self.db_name, dice_info)

        self.star_class = dice_info.table_result

    def get_star_class(self):
        # returns the star class after being provided the current star details
        if self.star_type != 'Special':
            self.star_class = 'V'

        else:
            dice = gf.roll_dice(2)
            dice_info = DiceRoll(
                location=self.location,
                number=2,
                reason='star class',
                dice_result=dice,
                table_result=lu.mgt2e_special_star_class_dy[dice])
            du.insert_dice_rolls(self.db_name, dice_info)

            if dice_info.table_result == 'Giants':
                self.get_giant_star_class()
            else:
                self.star_class = dice_info.table_result

    def fix_star_subtype_errors(self):
        if self.star_class == 'IV':
            if self.star_type == 'O':
                self.star_type = 'B'
                self.star_subtype = 0
            elif self.star_type in ['K','M']:
                self.star_type = 'K'
                self.star_subtype = 4
        elif self.star_class == 'VI':
            if self.star_type in ['A','F']:
                self.star_class = 'G'
                self.star_subtype = 0

    def get_brown_dwarf_mass(self):
        dice_roll_1 = gf.roll_dice(1)
        dice_roll_2 = gf.roll_dice(4)

        dice_info = DiceRoll(
            location=self.location,
            number=2,
            reason='Brown Dwarf Mass first roll',
            dice_result=dice_roll_1,
            table_result=str(dice_roll_1))
        du.insert_dice_rolls(self.db_name, dice_info)

        dice_info = DiceRoll(
            location=self.location,
            number=4,
            reason='Brown Dwarf Mass second roll',
            dice_result=dice_roll_2,
            table_result=str(dice_roll_2))
        du.insert_dice_rolls(self.db_name, dice_info)

        self.star_mass = (dice_roll_1 / 100) + ((dice_roll_2 - 1) / 1000)

    def get_white_dwarf_mass(self):
        dice_roll = gf.roll_dice(2)
        d10 = random.randint(1,10)

        dice_info = DiceRoll(
            location=self.location,
            number=2,
            reason='White Dwarf Mass first roll',
            dice_result=dice_roll,
            table_result=dice_roll)
        du.insert_dice_rolls(self.db_name, dice_info)

        dice_info = DiceRoll(
            location=self.location,
            number=1,
            reason='White Dwarf Mass second roll d10',
            dice_result=d10,
            table_result=str(d10))
        du.insert_dice_rolls(self.db_name, dice_info)

        self.star_mass = ((dice_roll - 1) / 10) + (d10/100)

    def get_main_star_mass(self):
        try:
            mass_table = gf.csv_to_dict_of_lists('stellar_mass_temperature.csv')
            lookup_key = self.star_type + str(self.star_subtype)
            star_class_col_num = lu.star_class_col_num_dy[self.star_class]
            self.star_mass = float(mass_table[lookup_key][star_class_col_num])

        except Exception as e:

            logging.info(f"A star mass error occurred: {e} {self.star_class} {self.star_type} {self.star_subtype}")
            self.star_mass = -1

    def get_star_mass(self):
        # Returns string value of the star mass
        if self.star_class == 'BD':
            self.get_brown_dwarf_mass()

        elif self.star_class == 'D':
            self.get_white_dwarf_mass()
        else:
            self.get_main_star_mass()

    def get_white_dwarf_temperature(self):
        if self.star_age <= 0.05:
            base_temp = 100000
        elif self.star_age <= 0.25:
            base_temp= 25000
        elif self.star_age <= 0.75:
            base_temp = 10000
        elif self.star_age <= 1.25:
            base_temp = 8000
        elif self.star_age <= 2.0:
            base_temp = 7000
        elif self.star_age <= 3.75:
            base_temp = 5500
        elif self.star_age <= 7.5:
            base_temp = 5000
        elif self.star_age <= 11.5:
            base_temp = 4000
        else:
            base_temp = 3800
        self.star_temperature = base_temp * self.star_mass / 0.6

    def get_brown_dwarf_temperature(self):
        if self.star_mass >= 0.070:
            self.star_temperature = 2400
        elif self.star_mass >= 0.055:
            self.star_temperature = 1850
        elif self.star_mass >= 0.045:
            self.star_temperature = 1300
        elif self.star_mass >= 0.035:
            self.star_temperature = 900
        elif self.star_mass >= 0.019:
            self.star_temperature = 550
        else: self.star_temperature = 300

    def get_star_temperature(self):
        # Returns the star temperature after receiving star details
        if self.star_class not in ['D', 'BD']:
            mass_table = gf.csv_to_dict_of_lists('stellar_mass_temperature.csv')
            lookup_key = self.star_type + str(self.star_subtype)
            self.star_temperature = float(mass_table[lookup_key][7])
        elif self.star_class == 'D':
            self.get_white_dwarf_temperature()
        elif self.star_class == 'BD':
            self.get_brown_dwarf_temperature()

    def get_white_dwarf_diameter(self):
        self.star_diameter = (1/self.star_mass) * 0.01

    def get_brown_dwarf_diameter(self):
        if self.star_mass >= 0.070:
            self.star_diameter = 0.100
        elif self.star_mass >= 0.055:
            self.star_diameter = 0.600
        elif self.star_mass >= 0.045:
            self.star_diameter = 0.050
        elif self.star_mass >= 0.035:
            self.star_diameter = 0.040
        elif self.star_mass >= 0.019:
            self.star_diameter = 0.025
        else:
            self.star_diameter = 0.013

    def get_star_diameter(self):
        # Returns the star diameter after receiving star details
        try:
            if self.star_class not in ['D', 'BD']:
                diameter_table = gf.csv_to_dict_of_lists('stellar_diameter.csv')
                star_class_col_num = lu.star_class_col_num_dy[self.star_class]
                lookup_key = self.star_type + str(self.star_subtype)
                self.star_diameter = float(diameter_table[lookup_key][star_class_col_num])
            elif self.star_class == 'D':
                self.get_white_dwarf_diameter()
            elif self.star_class == 'BD':
                self.get_brown_dwarf_diameter()
            else:
                logging.info(f"A star diameter if else error occurred")
                self.star_diameter = -1
        except Exception as e:
            logging.info(f"A star diameter try except error occurred: {e}")
            self.star_diameter = -1

    def get_star_luminosity(self):
        # Returns the star luminosity after receiving star details
        try:
            self.star_luminosity = round((self.star_diameter ** 2) * ((self.star_temperature / 5772) ** 4),8)

        except Exception as e:
            logging.info(f"A star luminosity error occurred: {e}")
            self.star_luminosity = -1

    def calculate_main_sequence_lifespan(self):
        return 10 / self.star_mass ** 2.5

    def get_small_star_age(self):
        d1 = gf.roll_dice(1)
        dice_info = DiceRoll(
            location=self.location,
            number=1,
            reason='small star age 1D',
            dice_result=d1,
            table_result='n/a')
        du.insert_dice_rolls(self.db_name, dice_info)

        d3 = gf.roll_dice(1)
        dice_info = DiceRoll(
            location=self.location,
            number=1,
            reason='small star age d3',
            dice_result=d3,
            table_result='n/a')
        du.insert_dice_rolls(self.db_name, dice_info)
        small_age = d1 * 2 + (d3 // 2) - 1
        if small_age < 0.01: small_age = 0.01

        self.star_age = round(small_age, 3)

    def get_large_star_age(self):
        percent = random.random()
        dice_info = DiceRoll(
            location=self.location,
            number=0,
            reason='d100 for large star age',
            dice_result=percent,
            table_result='n/a')
        du.insert_dice_rolls(self.db_name, dice_info)
        large_age = self.calculate_main_sequence_lifespan() * percent
        if self.star_mass <= 4.7 and large_age <= 0.01:
            large_age = 0.01

        self.star_age = round(large_age, 3)

    def get_class_iv_star_age(self):
        percent = random.random()
        dice_info = DiceRoll(
            location=self.location,
            number=0,
            reason='d100 for iv star age',
            dice_result=percent,
            table_result='n/a')
        du.insert_dice_rolls(self.db_name, dice_info)
        main_seq_lifespan = self.calculate_main_sequence_lifespan()
        subgiant_lifespan = main_seq_lifespan/(4 + self.star_mass)

        self.star_age = round(main_seq_lifespan + (subgiant_lifespan * percent),3)

    def get_class_iii_star_age(self):
        percent = random.random()
        dice_info = DiceRoll(
            location=self.location,
            number=0,
            reason='d100 for iii star age',
            dice_result=percent,
            table_result='n/a')
        du.insert_dice_rolls(self.db_name, dice_info)
        main_seq_lifespan = self.calculate_main_sequence_lifespan()
        subgiant_lifespan = main_seq_lifespan / (4 + self.star_mass)
        giant_lifespan = main_seq_lifespan/(10 * self.star_mass ** 3)
        self.star_age = round(main_seq_lifespan + subgiant_lifespan + (giant_lifespan * percent),3)

    def get_star_age(self):
        # returns the age of the system after receiving the star details

        try:
            if self.star_class in ['Ia', 'Ib', 'II', 'V', 'VI'] and self.star_mass <= 0.9:
                self.get_small_star_age()

            elif self.star_class in ['Ia', 'Ib', 'II', 'V', 'VI'] and self.star_mass > 0.9:
                self.get_large_star_age()

            elif self.star_class == 'IV':
                self.get_class_iv_star_age()

            elif self.star_class == 'III':
                self.get_class_iii_star_age()

            else:
                self.star_age = -1

        except Exception as e:
            logging.info(f"A star age error occurred: {e}")
            self.star_age = -99

    def get_white_dwarf_age(self):
        # Unclear instructions
        self.get_small_star_age() # skipping this for now
        mass = random.randint(1,3)
        dice_info = DiceRoll(
            location=self.location,
            number=0,
            reason='d3 for WD star age-mass',
            dice_result=mass,
            table_result=str(mass))
        du.insert_dice_rolls(self.db_name, dice_info)
        star_final_age = round((10/mass ** 2.5) * (1 + (1 / (4 + mass)) + (1 / (10 * mass ** 3))), 2)
        self.star_age += star_final_age

    def get_non_primary_star_age(self):
        if self.star_class not in ['BD', 'D']:
            self.star_age = 0
        elif self.star_class == 'BD':
            self.get_small_star_age()
        elif self.star_class == 'D':
            self.get_white_dwarf_age()

    def get_companion_orbit_number(self, primary: object):
        # returns the orbit number of a companion star after receiving the primary details

        if primary.star_class not in ['Ia', 'Ib', 'II', 'III']:
            logging.info(f'{primary.star_class} using default method for orbit #')

            die_roll_1 = gf.roll_dice(1)
            dice_info = DiceRoll(
                location=self.location,
                number=1,
                reason='first roll for orbit #',
                dice_result=die_roll_1,
                table_result=die_roll_1)
            du.insert_dice_rolls(self.db_name, dice_info)

            die_roll_2 = gf.roll_dice(2)
            dice_info = DiceRoll(
                location=self.location,
                number=2,
                reason='first roll for orbit #',
                dice_result=die_roll_1,
                table_result=die_roll_1)
            du.insert_dice_rolls(self.db_name, dice_info)

            self.orbit_number = die_roll_1 / 10 + (die_roll_2 - 7) / 100

        else:
            logging.info(f'{primary.star_class} using giant method for orbit #')
            die_roll = gf.roll_dice(1)
            dice_info = DiceRoll(
                location=self.location,
                number=1,
                reason='orbit number for giant',
                dice_result=die_roll,
                table_result=die_roll)
            du.insert_dice_rolls(self.db_name, dice_info)
            moa_table = gf.csv_to_dict_of_lists('moa.csv')
            lookup_key = self.star_type + str(self.star_subtype)
            star_class_col_num = lu.star_class_col_num_dy[self.star_class]
            self.orbit_number = float(moa_table[lookup_key][star_class_col_num]) * die_roll

    def get_close_secondary_orbit_number(self):
        die_roll = gf.roll_dice(1)

        if die_roll == 1:
            self.orbit_number = 0.5
        else:
            self.orbit_number = die_roll - 1

        dice_info = DiceRoll(
            location=self.location,
            number=1,
            reason='close secondary orbit number',
            dice_result=die_roll,
            table_result=str(self.orbit_number))
        du.insert_dice_rolls(self.db_name, dice_info)

    def get_near_secondary_orbit_number(self):
        die_roll = gf.roll_dice(1)

        self.orbit_number = die_roll + 5

        dice_info = DiceRoll(
            location=self.location,
            number=1,
            reason='near secondary orbit number',
            dice_result=die_roll,
            table_result=str(self.orbit_number))
        du.insert_dice_rolls(self.db_name, dice_info)

    def get_far_secondary_orbit_number(self):
        die_roll = gf.roll_dice(1)

        self.orbit_number = die_roll + 11

        dice_info = DiceRoll(
            location=self.location,
            number=1,
            reason='far secondary orbit number',
            dice_result=die_roll,
            table_result=str(self.orbit_number))
        du.insert_dice_rolls(self.db_name, dice_info)

    def get_secondary_orbit_number(self):
        if self.orbit_class == 'far': self.get_far_secondary_orbit_number()
        elif self.orbit_class == 'near':  self.get_near_secondary_orbit_number()
        elif self.orbit_class == 'close': self.get_close_secondary_orbit_number()
        else:
            logging.info('Secondary Orbit Number error')
            self.orbit_number = -1

    def get_orbit_au(self):
        if self.orbit_number < 1:
            self.orbit_au = lu.orbit_number_to_au_dy[1] * self.orbit_number
        else:
            self.orbit_au = lu.orbit_number_to_au_dy[self.orbit_number]

    def get_base_eccentricity(self):
        logging.info(f'Getting base eccentricity.  Total stars directly orbited {self.stars_orbited}')

        dice_roll = gf.roll_dice(2) + 2
        if self.stars_orbited > 1:
            dice_roll += 1

        dice_info = DiceRoll(
            location=self.location,
            number=2,
            reason='generating base eccentricity',
            dice_result=dice_roll,
            table_result=lu.base_eccentricity_dy[dice_roll])
        du.insert_dice_rolls(self.db_name, dice_info)

        return float(dice_info.table_result)

    def adjust_eccentricity(self):

        def calculate_eccentricity(dice, divisor):
            dice_roll = gf.roll_dice(dice)
            calculation = dice_roll / divisor

            dice_info = DiceRoll(
                location=self.location,
                number=dice,
                reason='calculating adjustment',
                dice_result=dice_roll,
                table_result=str(calculation))
            du.insert_dice_rolls(self.db_name, dice_info)

            return calculation

        row_roll = gf.roll_dice(2)

        if row_roll <= 5:
            adjustment = calculate_eccentricity(1,1000)

        elif 6 <= row_roll <= 7:
            adjustment = calculate_eccentricity(1, 200)

        elif 8 <= row_roll <= 9:
            adjustment = calculate_eccentricity(1, 100)

        elif row_roll == 10:
            adjustment = calculate_eccentricity(1, 20)

        elif row_roll >= 11:
            adjustment = calculate_eccentricity(2, 20)

        else:
            adjustment = -99
            logging.info('Error calculating eccentricity')

        return adjustment

    def get_orbit_eccentricity(self):
        self.orbit_eccentricity = self.get_base_eccentricity() + self.adjust_eccentricity()

    def get_orbit_min(self):
        self.orbit_min = self.orbit_au * (1 - self.orbit_eccentricity)

    def get_orbit_max(self):
        self.orbit_max = self.orbit_au * (1 + self.orbit_eccentricity)

    def get_companion_orbit_period(self, main):
        self.orbit_period =  round(math.sqrt(self.orbit_au **3/(main.star_mass + self.star_mass))*365.25,2)

    def get_secondary_orbit_period(self, main):
        self.orbit_period = round(math.sqrt(self.orbit_au **3/(main.binary_mass + self.star_mass))*365.25,2)


def is_hotter(companion: Star, primary: Star):
    type_list = ['O', 'B', 'A', 'F', 'G', 'K', 'M']
    logging.info(f'Checking if companion is hotter than main')
    try:
        companion_index = type_list.index(companion.star_type)
        primary_index = type_list.index(primary.star_type)
        logging.info(f' Type Indicies {companion_index} {primary_index}')
        logging.info(f' Subtypes {companion.star_subtype} {primary.star_subtype}')
        if companion_index > primary_index:
            logging.info('False. Companion Index > Primary Index')
            return False
        elif companion_index == primary_index and companion.star_subtype < primary.star_subtype:
            logging.info('False. Companion Index = Primary Index and Companion Subtype < Primary Subtype')
            return False
        else:
            logging.info('True')
            return True

    except ValueError:
        logging.info('Random Companion Error')
        return False