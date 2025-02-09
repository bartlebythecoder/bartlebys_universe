from dataclasses import dataclass
import logging
import math
import mgt_system_objects as mgt_system
import mgt_stellar_objects as mgt_star
import generic_functions as gf
import database_utils as du
import lookup_tables as lu
from bodies import Parameters, DiceRoll

@dataclass
class Orbit:
    db_name: str
    location: str
    orbit_slot: int
    star_orbit_class: str
    orbit_number: float
    orbit_au: float
    world_type: str
    stars_orbited: int
    stars_orbited_mass: float
    orbit_eccentricity: float
    orbit_period: float

    def get_stars_orbited(self, star: mgt_star.Star, star_list: list):
        total_stars = 0
        total_mass = 0
        adjusted_orbit_number = self.orbit_number

        for each_star in star_list:
            adjusted_orbit_number = self.orbit_number + star.orbit_number
            if star_eligible_for_orbit(self, each_star, adjusted_orbit_number):
                total_stars += 1
                total_mass += each_star.star_mass

        self.stars_orbited = total_stars
        self.stars_orbited_mass = total_mass


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

    def get_au_from_orbit_number(self):
        self.orbit_au = gf.extrapolate_table(self.orbit_number, lu.orbit_number_to_au_dy)

    def get_orbit_period(self):
        self.orbit_period = math.pow(self.orbit_au**3 / self.stars_orbited_mass, 1/3)

    def get_gas_giant_size_code(self, star: mgt_star.Star, system: mgt_system.System):
        dm = 0
        if star.star_class == 'VI':
            dm -= 1
        elif star.star_class == 'V' and star.star_type == 'M':
            dm -= 1
        elif star.star_type == 'BD':
            dm -= 1

        if system.orbit_spread < 0.1:
            dm -= 1

        first_die = gf.roll_dice(1) + dm

        if first_die <= 2: self.size_code = 'GS'
        elif 3 <= first_die <= 4: self.size_code = 'GM'
        elif first_die >= 5: self.size_code = 'GL'

        dice_info = DiceRoll(
            location=self.location,
            number=1,
            reason='gas giant diameter first roll. DM = ' + str(dm) ,
            dice_result=first_die,
            table_result=first_die)
        du.insert_dice_rolls(self.db_name, dice_info)


    def get_terrestrial_size_code(self):
        first_die = gf.roll_dice(1)
        second_roll_row = 0
        if first_die <= 2:
            second_roll_row = 1
        elif 3 <= first_die <= 4:
            second_roll_row = 2
        else:
            second_roll_row = 3

        dice_info = DiceRoll(
            location=self.location,
            number=1,
            reason='terrestrial diameter first roll.',
            dice_result=first_die,
            table_result='Row: ' + str(second_roll_row))
        du.insert_dice_rolls(self.db_name, dice_info)

        if second_roll_row == 1:
            num = 1
            second_die = gf.roll_dice(num)
        elif second_roll_row == 2:
            num = 2
            second_die = gf.roll_dice(num)
        else:
            num = 2
            second_die = gf.roll_dice(num) + 2

        self.size_code = gf.int_to_hex(second_die)

        dice_info = DiceRoll(
            location=self.location,
            number=num,
            reason='terrestrial diameter second roll.',
            dice_result=second_die,
            table_result=self.size_code)
        du.insert_dice_rolls(self.db_name, dice_info)

    def get_size_code(self, star: mgt_star.Star, system: mgt_system.System):
        if self.world_type == 'belt':
            self.size_code = '0'
        elif self.world_type == 'gas giant':
            self.get_gas_giant_size_code(star, system)
        elif self.world_type == 'planet':
            self.get_terrestrial_size_code()
        else:
            self.size_code = None


def star_eligible_for_orbit(current_world, evaluated_star: mgt_star.Star, adjusted_orbit_number: float):
    # Does the evaluated star count as a star_orbited for the planet around the current star
    # Everything that orbits a primary can orbit a secondary if it is out far enough
    # But planets orbiting secondaries only orbit their star and any companions
    if evaluated_star.orbit_number < adjusted_orbit_number and current_world.star_orbit_class in ['primary']:
        return True
    elif (evaluated_star.orbit_number < adjusted_orbit_number and
          evaluated_star.orbit_class == current_world.star_orbit_class):
        return True
    else:
        logging.info(f"No more total stars: {evaluated_star.orbit_number} {adjusted_orbit_number}")
        logging.info(f"{evaluated_star.orbit_class}  {current_world.star_orbit_class}")

        return False
