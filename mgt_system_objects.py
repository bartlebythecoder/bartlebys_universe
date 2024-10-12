from dataclasses import dataclass
import random
import logging

import generic_functions as gf
import database_utils as du
import lookup_tables as lu
from bodies import Parameters, DiceRoll


@dataclass
class System:
    db_name: str
    build: int
    location: str
    subsector: str
    system_age: float
    primary_star_class: str
    number_of_stars_in_system: int
    stars_in_system: list
    number_of_secondary_stars_in_system: int

    number_of_gas_giants: int
    number_of_planetoid_belts: int
    number_of_terrestrial_planets: int
    total_number_of_planets: int

    total_system_orbits: int
    baseline_number: int
    baseline_orbit_number: float
    empty_orbits: int
    orbit_spread: float
    anomalous_orbits: int

    def __init__(self, parms: Parameters, location: str):
        # Initialize attributes with provided values
        self.db_name = parms.db_name
        self.build = parms.build
        self.location = location
        self.subsector = 'X'
        self.system_age = 0
        self.primary_star_class = 'X'
        self.number_of_stars_in_system = -1
        self.stars_in_system = []
        self.number_of_secondary_stars_in_system = -1

        self.number_of_gas_giants = -1
        self.number_of_planetoid_belts = -1
        self.number_of_terrestrial_planets = -1
        self.total_number_of_planets = -1

        self.total_system_orbits = -1
        self.baseline_number = -1
        self.baseline_orbit_number = -1
        self.empty_orbits = -1
        self.orbit_spread = -1
        self.anomalous_orbits = -1

    def gas_giant_check(self):
        die_roll = gf.roll_dice(1)

        dice_info = DiceRoll(
            location=self.location,
            number=1,
            reason='checking for gg',
            dice_result=die_roll,
            table_result=str(die_roll))
        du.insert_dice_rolls(self.db_name, dice_info)
        if die_roll >= 2:
            return True
        else:
            return False

    def get_number_of_gas_giants(self, new_system):
        if self.gas_giant_check():
            dm = get_gas_giant_dm(new_system)

            dice_roll = gf.roll_dice(2)
            dice_roll += dm
            dice_info = DiceRoll(
                location=self.location,
                number=2,
                reason='gg quantity',
                dice_result=dice_roll,
                table_result=str(dice_roll))
            du.insert_dice_rolls(self.db_name, dice_info)

            if dice_roll <= 4:
                self.number_of_gas_giants = 1
            elif dice_roll <= 6:
                self.number_of_gas_giants = 2
            elif dice_roll <= 8:
                self.number_of_gas_giants = 3
            elif dice_roll <= 11:
                self.number_of_gas_giants = 4
            elif dice_roll == 12:
                self.number_of_gas_giants = 5
            elif dice_roll > 12:
                self.number_of_gas_giants = 6
        else:
            self.number_of_gas_giants = 0

    def gas_planetoid_belt_check(self):
        dice_roll = gf.roll_dice(2)

        dice_info = DiceRoll(
            location=self.location,
            number=2,
            reason='checking for belt',
            dice_result=dice_roll,
            table_result=str(dice_roll))
        du.insert_dice_rolls(self.db_name, dice_info)
        if dice_roll >= 8:
            return True
        else:
            return False

    def get_planetoid_belt_dm(self, new_system):
        dm = 0
        if new_system.number_of_gas_giants >= 1:
            dm += 1

        if new_system.primary_star_class == 'D':
            dm += 1

        count_post_stellars = new_system.stars_in_system.count('D')
        dm += count_post_stellars

        if new_system.number_of_stars_in_system >= 2:
            dm += 1

        return dm

    def get_number_of_planetoid_belts(self, new_system):
        if self.gas_planetoid_belt_check():
            dm = self.get_planetoid_belt_dm(new_system)

            dice_roll = gf.roll_dice(2)
            dice_roll += dm
            dice_info = DiceRoll(
                location=self.location,
                number=2,
                reason='belt quantity',
                dice_result=dice_roll,
                table_result=str(dice_roll))
            du.insert_dice_rolls(self.db_name, dice_info)

            if dice_roll <= 6:
                self.number_of_planetoid_belts = 1
            elif dice_roll <= 11:
                self.number_of_planetoid_belts = 2
            elif dice_roll >= 12:
                self.number_of_planetoid_belts = 3
        else:
            self.number_of_planetoid_belts = 0

    def get_number_of_terrestrial_planets(self, new_system):
        dm = -2
        count_post_stellars = new_system.stars_in_system.count('D')
        dm -= count_post_stellars

        first_roll = gf.roll_dice(2)
        first_roll += dm
        dice_info = DiceRoll(
            location=self.location,
            number=2,
            reason='planet quantity',
            dice_result=first_roll,
            table_result=str(first_roll))
        du.insert_dice_rolls(self.db_name, dice_info)

        if first_roll < 3:
            second_roll = random.randint(1, 3) + 2

            dice_info = DiceRoll(
                location=self.location,
                number=0,
                reason='d3 + 2 reroll',
                dice_result=second_roll,
                table_result=str(second_roll ))
            du.insert_dice_rolls(self.db_name, dice_info)

            self.number_of_terrestrial_planets = second_roll

        else:

            third_roll = random.randint(1, 3) - 1

            dice_info = DiceRoll(
                location=self.location,
                number=0,
                reason='d3 + 2 reroll',
                dice_result=third_roll ,
                table_result=str(third_roll ))
            du.insert_dice_rolls(self.db_name, dice_info)

            self.number_of_terrestrial_planets = first_roll + third_roll

    def get_total_system_orbits(self, star_list):
        total_system_orbits = 0
        for each_star in star_list:
            total_system_orbits += each_star['total_star_orbits']

        self.total_system_orbits = total_system_orbits

    def get_baseline_number(self, star: object):
        if gf.is_between(star.habitable_zone_center,
                        star.minimum_allowable_orbit_number,
                        star.maximum_allowable_orbit_number):
            self.baseline_number = star.hzco_is_available(self)
        else:
            self.baseline_number = 0

    def get_baseline_orbit_number(self, star):
        total_worlds = self.number_of_gas_giants + self.number_of_planetoid_belts + self.number_of_terrestrial_planets

        if 1 <= self.baseline_number < total_worlds:
            dice_roll = gf.roll_dice(2) - 7
            dice_info = DiceRoll(
                location=self.location,
                number=2,
                reason='2D-7 baseline orbit number 3a',
                dice_result=dice_roll,
                table_result=str(dice_roll))
            du.insert_dice_rolls(self.db_name, dice_info)
            if star.habitable_zone_center > 1:
                self.baseline_orbit_number = star.habitable_zone_center + (dice_roll / 10)
            else:
                self.baseline_orbit_number = star.habitable_zone_center + (dice_roll / 100)

        elif self.baseline_number < 1:
            dice_roll = gf.roll_dice(2) - 2
            dice_info = DiceRoll(
                location=self.location,
                number=2,
                reason='2D-2 baseline orbit number 3b',
                dice_result=dice_roll,
                table_result=str(dice_roll))
            du.insert_dice_rolls(self.db_name, dice_info)

            if star.minimum_allowable_orbit_number < 1:
                self.baseline_orbit_number = (star.habitable_zone_center - self.baseline_number +
                                              total_worlds + (dice_roll / 10))
            else:
                self.baseline_orbit_number = (star.minimum_allowable_orbit_number - (self.baseline_number / 10) +
                                              + (dice_roll / 100))

        elif self.baseline_number > total_worlds:
            dice_roll = gf.roll_dice(2) - 7
            dice_info = DiceRoll(
                location=self.location,
                number=2,
                reason='2D-7 baseline orbit number 3c',
                dice_result=dice_roll,
                table_result=str(dice_roll))
            du.insert_dice_rolls(self.db_name, dice_info)

            if star.habitable_zone_center - self.baseline_number + total_worlds >= 1:
                self.baseline_orbit_number = (star.habitable_zone_center - self.baseline_number +
                                              total_worlds + (dice_roll / 5))
            else:
                self.baseline_orbit_number = (star.habitable_zone_center -
                                              ((self.baseline_number + total_worlds + (dice_roll / 5)) / 10))
                if self.baseline_orbit_number < 0:
                    self.baseline_orbit_number = star.habitable_zone_center - 0.1
                    if self.baseline_orbit_number < star.minimum_allowable_orbit_number + (total_worlds * .01):
                        self.baseline_orbit_number = star.minimum_allowable_orbit_number + (total_worlds * .01)

    def get_empty_orbits(self):
        # This function does not change the star_orbit or total_system_orbit.
        # Needs to be handled at the planet creation phase
        # The start details have already been written

        dice_roll = gf.roll_dice(2)
        dice_info = DiceRoll(
            location=self.location,
            number=2,
            reason='empty orbits',
            dice_result=dice_roll,
            table_result=str(dice_roll))
        du.insert_dice_rolls(self.db_name, dice_info)

        if dice_roll <= 9:
            self.empty_orbits = 0
        elif dice_roll <= 10:
            self.empty_orbits = 1
        elif dice_roll <= 11:
            self.empty_orbits = 2
        else:
            self.empty_orbits = 3

    def get_orbit_spread(self, star: object):
        if self.baseline_number > 1:
            self.orbit_spread = ((self.baseline_orbit_number - star.minimum_allowable_orbit_number) /
                                 self.baseline_number)
        else:
            self.orbit_spread = (star.total_star_orbits /
                                 (star.total_star_orbits + self.empty_orbits + self.number_of_stars_in_system))

    def get_anomalous_orbits(self):
        dice_roll = gf.roll_dice(2)
        dice_info = DiceRoll(
            location=self.location,
            number=2,
            reason='anomalous_orbits',
            dice_result=dice_roll,
            table_result=str(dice_roll))
        du.insert_dice_rolls(self.db_name, dice_info)

        if dice_roll <= 9:
            self.anomalous_orbits = 0
        elif dice_roll <= 10:
            self.anomalous_orbits = 1
            self.number_of_terrestrial_planets += 1
        elif dice_roll <= 11:
            self.anomalous_orbits = 2
            self.number_of_terrestrial_planets += 2
        else:
            self.anomalous_orbits = 3
            self.number_of_terrestrial_planets += 3
        if self.number_of_terrestrial_planets > 13:
            self.number_of_planetoid_belts += self.number_of_terrestrial_planets - 13
            self.number_of_terrestrial_planets = 13


def get_gas_giant_dm(new_system):
    dm = 0
    if new_system.primary_star_class == 'V' and new_system.number_of_stars_in_system == 1:
        dm += 1

    if new_system.primary_star_class == 'BD':
        dm -= 2

    if new_system.primary_star_class == 'D':
        dm -= 2

    count_post_stellars = new_system.stars_in_system.count('D')
    dm -= count_post_stellars

    if new_system.number_of_stars_in_system >= 4:
        dm -= 1

    return dm