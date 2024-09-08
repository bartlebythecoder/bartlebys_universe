from dataclasses import dataclass
import random
import logging

import star_functions as sf
import database_utils as du
import lookup_tables as lu

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
    subsector_list: list
    random_seed: int


@dataclass
class System:
    db_name: str
    build: int
    location: str
    subsector: str
    system_age: float


@dataclass
class Star:
    db_name: str
    build: int
    location: str
    designation: str
    orbit_class: str
    orbit_number: int
    star_type: str
    star_subtype: int
    star_class: str
    star_mass: float
    star_temperature: float
    star_diameter: float
    star_luminosity: float
    star_age: float
    gas_giants: int
    planetoid_belts: int
    terrestrial_planets: int
    minimal_orbit_number: int
    habitable_zone_center: int

    def get_hot_star_type(self):
        # if the original get_star_type function returns a hot star, this function is used to return a star type
        dice = sf.roll_dice(2)
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

        dice = sf.roll_dice(2)
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
        dice = sf.roll_dice(2) + 1

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

    def get_star_subtype(self):
        if self.star_class == 'IV':
            dice_roll = random.randint(0, 4)
            self.star_subtype = dice_roll
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

    def get_giant_star_class(self):
        # if the original get_star_class returns a giant star, use this function to return the class
        dice = sf.roll_dice(2)
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
            dice = sf.roll_dice(2)
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

    def get_star_mass(self):
        # Returns string value of the star mass
        try:
            mass_table = sf.csv_to_dict_of_lists('stellar_mass_temperature.csv')
            lookup_key = self.star_type + str(self.star_subtype)
            star_class_col_num = lu.star_class_col_num_dy[self.star_class]
            self.star_mass = float(mass_table[lookup_key][star_class_col_num])

        except Exception as e:
            logging.info(f"A star mass error occurred: {e}")
            self.star_mass = -1

    def get_star_temperature(self):
        # Returns the star temperature after receiving star details

        mass_table = sf.csv_to_dict_of_lists('stellar_mass_temperature.csv')
        lookup_key = self.star_type + str(self.star_subtype)
        self.star_temperature = float(mass_table[lookup_key][7])

    def get_star_diameter(self):
        # Returns the star diameter after receiving star details
        try:
            diameter_table = sf.csv_to_dict_of_lists('stellar_diameter.csv')
            star_class_col_num = lu.star_class_col_num_dy[self.star_class]
            lookup_key = self.star_type + str(self.star_subtype)
            self.star_diameter = float(diameter_table[lookup_key][star_class_col_num])

        except Exception as e:
            logging.info(f"A star diameter error occurred: {e}")
            self.star_diameter = -1

    def get_star_luminosity(self):
        # Returns the star luminosity after receiving star details
        try:
            self.star_luminosity = round((self.star_diameter ** 2) * ((self.star_temperature / 5772) ** 4),3)

        except Exception as e:
            logging.info(f"A star luminosity error occurred: {e}")
            self.star_luminosity = -1

    def calculate_main_sequence_lifespan(self):
        return 10 / self.star_mass ** 2.5

    def get_small_star_age(self):
        d1 = sf.roll_dice(1)
        dice_info = DiceRoll(
            location=self.location,
            number=1,
            reason='small star age 1D',
            dice_result=d1,
            table_result='n/a')
        du.insert_dice_rolls(self.db_name, dice_info)

        d3 = sf.roll_dice(1)
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




