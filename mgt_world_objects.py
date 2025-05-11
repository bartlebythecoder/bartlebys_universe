from dataclasses import dataclass
import logging
import math
import generic_functions as gf
import database_utils as du
import lookup_tables as lu
from bodies import Parameters, DiceRoll

@dataclass
class World:
    db_name: str
    name: str
    location: str
    location_orbit: str # Only used for worlds migrated from Legacy TUC
    orbit_slot: int  # Only used for worlds created from BU
    sector: int
    subsector: str
    main_world: int

@dataclass
class World_climate:
    db_name: str
    world_id: int
    axial_tilt: float
    axial_tile_remark: str

    def __init__(self, parms: Parameters, world_id: int):
        # Initialize attributes with provided values
        self.db_name = parms.db_name
        self.world_id = world_id
        self.axial_tilt = -99


    def generate_axial_tilt(self):

        axial_dice_roll = gf.roll_dice(2)
        dice_info = DiceRoll(
            location=str(self.world_id),
            number=2,
            reason='axial tilt 2d',
            dice_result=axial_dice_roll,
            table_result=str(axial_dice_roll))
        du.insert_dice_rolls(self.db_name, dice_info)

        axial_die_roll = gf.roll_dice(1)
        dice_info = DiceRoll(
            location=str(self.world_id),
            number=1,
            reason='axial tilt 1d',
            dice_result=axial_die_roll,
            table_result=str(axial_die_roll))
        du.insert_dice_rolls(self.db_name, dice_info)


        if axial_dice_roll in [2,3,4]:
            self.axial_tilt = (axial_die_roll - 1) / 50
        elif axial_dice_roll == 5:
            self.axial_tilt = axial_die_roll / 5
        elif axial_dice_roll == 6:
            self.axial_tilt = axial_die_roll
        elif axial_dice_roll == 7:
            self.axial_tilt = axial_die_roll + 6
        elif axial_dice_roll in [8,9]:
            self.axial_tilt = (axial_die_roll * 5) + 5
        else:
            extreme_axial_die_roll = gf.roll_dice(1)
            dice_info = DiceRoll(
                location=str(self.world_id),
                number=1,
                reason='extreme axial tilt 1d',
                dice_result=extreme_axial_die_roll,
                table_result=str(extreme_axial_die_roll))
            du.insert_dice_rolls(self.db_name, dice_info)

            if axial_die_roll in [1,2]:
                self.axial_tilt = (extreme_axial_die_roll * 10) + 10
            elif axial_die_roll == 3:
                self.axial_tilt = (extreme_axial_die_roll * 10) + 30
            elif axial_die_roll == 4:
                self.axial_tilt = (extreme_axial_die_roll ** 2) + 90
            elif axial_die_roll == 5:
                self.axial_tilt = 180 - (extreme_axial_die_roll ** 2)
            elif axial_die_roll == 6:
                self.axial_tilt = 120 + (extreme_axial_die_roll * 10)


@dataclass
class World_population:
    db_name: str
    world_id: int
    population_concentration: int
    urban_pct: float
    major_cities_total: int
    major_cities_population_total: int

    def __init__(self, parms: Parameters, world_id: int):
        # Initialize attributes with provided values
        self.db_name = parms.db_name
        self.world_id = world_id
        self.population_concentration = -99
        self.urban_pct = -99
        self.major_cities_total = -99
        self.major_cities_population_total = -99
        self.modifier_stats = du.get_pop_input(self.db_name, self.world_id)

    def generate_biomass(self):

        dice_roll = gf.roll_dice(2)
        dice_info = DiceRoll(
            location=str(self.world_id),
            number=2,
            reason='biomass base roll',
            dice_result=dice_roll,
            table_result=str(dice_roll))
        du.insert_dice_rolls(self.db_name, dice_info)

        biomass_input = self.modifier_stats
        print(f'{self.world_id} Biomass Input {biomass_input}')
        atmosphere = biomass_input[2]
        hydrographics = biomass_input[3]
        temperature = biomass_input[4]

        biomass_atmos_mod = 0
        biomass_hydro_mod = 0
        biomass_temp_mod = 0

        if atmosphere == 0: biomass_atmos_mod = -6
        elif atmosphere == 1: biomass_atmos_mod = -4
        elif atmosphere in [2,3,14]: biomass_atmos_mod = -3
        elif atmosphere in [4,5]: biomass_atmos_mod = -2
        elif atmosphere in [8,9,13]: biomass_atmos_mod = 2
        elif atmosphere == 10: biomass_atmos_mod = -3
        elif atmosphere == 11: biomass_atmos_mod = -5
        elif atmosphere == 12: biomass_atmos_mod = -7
        elif atmosphere >= 15: biomass_atmos_mod = -5

        if hydrographics == 0: biomass_hydro_mod = -4
        elif hydrographics in [1,2,3]: biomass_hydro_mod = -2
        elif hydrographics in [6,7,8]: biomass_hydro_mod = 1
        elif hydrographics >= 9: biomass_hydro_mod = 2

        if temperature > 353: biomass_temp_mod = -4
        elif temperature < 273: biomass_temp_mod = -2
        elif 279 < temperature < 303: biomass_temp_mod = 2

        biomass = dice_roll + biomass_atmos_mod + biomass_hydro_mod + biomass_temp_mod

        if biomass <0: biomass = 0

        #special case 2
        if atmosphere in [0,1,10,11,12,15,16,17,18,19,20] and biomass > 0:
            special_biomass = (biomass_atmos_mod * -1) - 1
            biomass += special_biomass

        self.biomass_rating = biomass


    def generate_biocomplexity(self):

        if self.biomass_rating > 0:
            dice_roll = gf.roll_dice(2) - 7
            dice_info = DiceRoll(
                location=str(self.world_id),
                number=2,
                reason='biocomplexity base roll',
                dice_result=dice_roll,
                table_result=str(dice_roll))
            du.insert_dice_rolls(self.db_name, dice_info)

            biocomplexity_input = self.modifier_stats
            atmosphere = biocomplexity_input [2]

            atmos_mod = 0
            if atmosphere not in [4,5,6,7,8,9]: atmos_mod = -2
            biocomplexity = dice_roll + self.biomass_rating + atmos_mod

        else:
            biocomplexity = 0



        self.biocomplexity_rating = biocomplexity

    def generate_biodiversity(self):

        if self.biomass_rating > 0:

            dice_roll = gf.roll_dice(2) - 7
            dice_info = DiceRoll(
                location=str(self.world_id),
                number=2,
                reason='biodiversity base roll',
                dice_result=dice_roll,
                table_result=str(dice_roll))
            du.insert_dice_rolls(self.db_name, dice_info)

            biodiversity = dice_roll + ((self.biomass_rating + self.biocomplexity_rating) / 2)
            biodiversity = round(biodiversity,1)
            if biodiversity < 1: biodiversity = 1

        else:
            biodiversity = 0

        biodiversity = round(biodiversity,0)
        self.biodiversity_rating = biodiversity

    def generate_compatibility(self):

        if self.biomass_rating > 0:

            dice_roll = gf.roll_dice(2)
            dice_info = DiceRoll(
                location=str(self.world_id),
                number=2,
                reason='compatibility base roll',
                dice_result=dice_roll,
                table_result=str(dice_roll))
            du.insert_dice_rolls(self.db_name, dice_info)
            compatibility_input = self.modifier_stats
            atmosphere = compatibility_input[2]

            atmos_mod = 0
            if atmosphere in [0,1,11,16,17]:
                atmos_mod = -8
            elif atmosphere in [2,4,7,9]:
                atmos_mod = -2
            elif atmosphere in [3,5,8]:
                atmos_mod = 1
            elif atmosphere == 6:
                atmos_mod = 2
            elif atmosphere in [10,15]:
                atmos_mod = -6
            elif atmosphere == 12:
                atmos_mod = -10
            elif atmosphere in [13,14]:
                atmos_mod = -1

            compatibility = dice_roll - (self.biocomplexity_rating/2) + atmos_mod
            compatibility = math.floor(compatibility)
            if compatibility < 0:
                compatibility = 0

        else:
            compatibility = 0

        self.compatibility_rating = compatibility

    def generate_resource(self):
        dice_roll = gf.roll_dice(2) - 7
        dice_info = DiceRoll(
            location=str(self.world_id),
            number=2,
            reason='world resource base roll',
            dice_result=dice_roll,
            table_result=str(dice_roll))
        du.insert_dice_rolls(self.db_name, dice_info)
        resource_input = self.modifier_stats
        atmosphere = resource_input[5]
        size = resource_input[6]
        earth_density = resource_input[7] / 5.5


        density_mod = 0
        if earth_density > 1.12: density_mod = 2
        elif earth_density < 0.5: density_mod = -2

        biomass_mod = 0
        if self.biomass_rating >= 3: biomass_mod = 2

        biodiversity_mod = 0
        if self.biodiversity_rating in [8,9,10]: biomass_mod = 1
        if self.biodiversity_rating >= 11: biodiversity_mod = 2

        compatibility_mod = 0
        if self.compatibility_rating in [0,1,2,3] and self.biomass_rating >= 1:
            compatibility_mod = -1
        elif self.compatibility_rating >=8:
            compatibility_mod = 2

        resource_rating = dice_roll + size + density_mod + biomass_mod + biodiversity_mod + compatibility_mod
        resource_rating = round(resource_rating,0)
        if resource_rating < 2: resource_rating = 2

        self.resource_rating = resource_rating

    def generate_habitability(self):
        habitability_input = self.modifier_stats
        atmosphere = habitability_input[2]
        hydrographics = habitability_input[3]
        temperature = habitability_input[4]
        size = habitability_input[5]
        gravity = habitability_input[7]

        size_mod = 0
        if size <= 4: size_mod = -1
        elif size >= 9: size_mod = 1

        atmosphere_mod = 0
        if atmosphere in [0,1,10]:
            atmosphere_mod = -8
        elif atmosphere in [2,14]:
            atmosphere_mod = -4
        elif atmosphere in [3,13]:
            atmosphere_mod = -3
        elif atmosphere in [4,9]:
            atmosphere_mod = -2
        elif atmosphere in [5,7,8]:
            atmosphere_mod = -1
        elif atmosphere in [11]:
            atmosphere_mod = -10
        elif atmosphere in [12,15,16,17,18,19]:
            atmosphere_mod = -12

        hydrographics_mod = 0
        if hydrographics == 0: hydrographics_mod = -4
        elif hydrographics in [1,2,3]: hydrographics_mod = -2
        elif hydrographics == 9: hydrographics_mod = -1
        elif hydrographics == 10: hydrographics_mod = -2

        temperature_mod = 0
        if temperature > 323: temperature_mod = -4
        elif 304 < temperature < 323: temperature_mod = -2
        elif temperature < 273: temperature_mod = -2

        gravity_mod = 0
        if gravity < 0.2: gravity_mod = -4
        elif 0.2 <= gravity < 0.4: gravity_mod = -2
        elif 0.4 <= gravity < 0.7: gravity_mod = -1
        elif 0.7 <= gravity < 1.1: gravity_mod = 1
        elif 1.1 <= gravity < 1.4: gravity_mod = -1
        elif 1.4 <= gravity < 2.0: gravity_mod = -3
        else: gravity_mod = -6

        habitability = 10 + size_mod + atmosphere_mod + hydrographics_mod + temperature_mod + gravity_mod
        habitability = round(habitability,0)
        if habitability < 0: habitability = 0
        self.habitability_rating = habitability