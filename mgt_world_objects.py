from dataclasses import dataclass
import random
import logging
import math
import mgt_stellar_objects as mgt_star
import generic_functions as gf
import database_utils as du
import lookup_tables as lu
from bodies import Parameters, DiceRoll

@dataclass
class World:
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
