from dataclasses import dataclass
import math
import random
import generic_functions as gf
import database_utils as du
import lookup_tables as lu
import logging
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
class World_Climate:
    db_name: str
    world_id: int
    axial_tilt: float
    axial_tile_remark: str

    def __init__(self, parms: Parameters, world_input_dictionary: dict):
        # Initialize attributes with provided values
        self.db_name = parms.db_name
        self.world_id = world_input_dictionary['world_id']
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
class World_Biology:
    db_name: str
    world_id: int
    biomass_rating: int
    biocomplexity_rating: int
    biodiversity_rating: int
    compatibility_rating: int
    resource_rating: int
    habitability_rating: int
    input_dictionary: dict


    def __init__(self, parms: Parameters, world_input_dictionary: dict):
        # Initialize attributes with provided values
        self.db_name = parms.db_name
        self.world_id = world_input_dictionary['world_id']
        self.biomass_rating = -99
        self.biocomplexity_rating = -99
        self.biodiversity_rating = -99
        self.compatibility_rating = -99
        self.resource_rating = -99
        self.habitability_rating = -99
        self.input_dictionary = world_input_dictionary

    def generate_biomass(self):

        dice_roll = gf.roll_dice(2)
        dice_info = DiceRoll(
            location=str(self.world_id),
            number=2,
            reason='biomass base roll',
            dice_result=dice_roll,
            table_result=str(dice_roll))
        du.insert_dice_rolls(self.db_name, dice_info)

        atmosphere =    self.input_dictionary['atmosphere']
        hydrographics = self.input_dictionary['hydrographics']
        temperature =   self.input_dictionary['temperature']

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

            atmosphere =    self.input_dictionary['atmosphere']

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

            atmosphere = self.input_dictionary['atmosphere']

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

        atmosphere = self.input_dictionary['atmosphere']
        size = self.input_dictionary['size']
        earth_density = self.input_dictionary['gravity'] / 5.5


        density_mod = 0
        if earth_density > 1.12: density_mod = 2
        elif earth_density < 0.5: density_mod = -2

        biomass_mod = 0
        if self.biomass_rating >= 3: biomass_mod = 2

        biodiversity_mod = 0
        if self.biodiversity_rating in [8,9,10]: biodiversity_mod = 1
        if self.biodiversity_rating >= 11: biodiversity_mod = 2

        compatibility_mod = 0
        if self.compatibility_rating in [0,1,2,3] and self.biomass_rating >= 1:
            compatibility_mod = -1
        elif self.compatibility_rating >=8:
            compatibility_mod = 2

        resource_rating = dice_roll + size + density_mod + biomass_mod + biodiversity_mod + compatibility_mod
        resource_rating = round(resource_rating)
        if resource_rating < 2: resource_rating = 2

        self.resource_rating = resource_rating

    def generate_habitability(self):

        atmosphere = self.input_dictionary['atmosphere']
        hydrographics = self.input_dictionary['hydrographics']
        temperature = self.input_dictionary['temperature']
        size = self.input_dictionary['size']
        gravity = self.input_dictionary['gravity']

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


@dataclass
class World_Population:
    db_name: str
    world_id: int
    population_concentration: int
    urban_pct: float
    major_cities_total: int
    major_cities_population_total: int
    input_dictionary: dict


    def __init__(self, parms: Parameters, world_input_dictionary: dict):
        # Initialize attributes with provided values
        self.db_name = parms.db_name
        self.world_id = world_input_dictionary['world_id']
        self.population_concentration = -99
        self.urban_pct = -99
        self.major_cities_total = -99
        self.major_cities_population_total = -99
        self.input_dictionary = world_input_dictionary


    def generate_population_concentration(self):

        size = self.input_dictionary['size']
        atmosphere = self.input_dictionary['atmosphere']
        population = self.input_dictionary['population']
        government = self.input_dictionary['government']
        tech_level = self.input_dictionary['tech_level']
        remarks = self.input_dictionary['remarks']

        dice_roll = gf.roll_dice(1)
        dice_info = DiceRoll(
            location=str(self.world_id),
            number=1,
            reason='pcr base roll',
            dice_result=dice_roll,
            table_result=str(dice_roll))
        du.insert_dice_rolls(self.db_name, dice_info)

        if population == 0:
            pcr = 0

        elif dice_roll > population:
            pcr = 9

        else:

            size_mod = 0
            if size == 1: size_mod = 2
            elif size in [2,3]: size_mod = 1

            # in text as minimal tech
            atmos_mod = 0
            if atmosphere in [0,1,10,11,12]:
                atmos_mod = +3
            elif atmosphere in [2,3,4,7,9,13,14]:
                atmos_mod = +1

            gov_mod = 0
            if government == 7: gov_mod = -2

            tech_level_mod = 0
            if tech_level in [0,1]:
                tech_level_mod = -2
            elif tech_level in [2,3]:
                tech_level_mod = -1
            elif tech_level in [4,5,6,7,8,9]:
                tech_level_mod = 1

            remark_mod = 0
            if 'Ag' in remarks:
                remark_mod -= 2
            if 'In' in remarks:
                remark_mod += 1
            if 'Na' in remarks:
                remark_mod -= 1
            if 'Ri' in remarks:
                remark_mod += 1

            pcr = dice_roll + size_mod + atmos_mod + gov_mod + tech_level_mod + remark_mod

        if pcr < 0: pcr = 0
        elif pcr > 9: pcr = 9

        self.population_concentration = pcr

    def generate_urban_pct(self):

        size = self.input_dictionary['size']
        atmosphere = self.input_dictionary['atmosphere']
        population = self.input_dictionary['population']
        government = self.input_dictionary['government']
        law = self.input_dictionary['law']
        tech_level = self.input_dictionary['tech_level']
        remarks = self.input_dictionary['remarks']

        dice_roll = gf.roll_dice(2)
        dice_info = DiceRoll(
            location=str(self.world_id),
            number=2,
            reason='urban_pct base roll',
            dice_result=dice_roll,
            table_result=str(dice_roll))
        du.insert_dice_rolls(self.db_name, dice_info)

        minimum_pct = 0
        maximum_pct = 100

        min_max_roll = gf.roll_dice(1)
        dice_info = DiceRoll(
            location=str(self.world_id),
            number=1,
            reason='min max roll',
            dice_result=min_max_roll,
            table_result=str(min_max_roll))
        du.insert_dice_rolls(self.db_name, dice_info)

        pcr_mod = 0
        if self.population_concentration in [0,1,2]:
            pcr_mod = -3 + self.population_concentration
        elif self.population_concentration >= 7:
            pcr_mod = -6 + self.population_concentration

        atmos_mod = 0
        if atmosphere in [4,7,9]:
            atmos_mod = -1

        size_mod = 0
        if size == 0:
            size_mod = 2

        population_mod = 0
        if population == 8:
            population_mod = 1
        elif population == 9:
            population_mod = 2
            minimum_pct = 18 + min_max_roll
        elif population == 10:
            population_mod = 4
            minimum_pct = 50 + min_max_roll

        government_mod = 0
        if government == 0:
            government_mod = -2

        law_level_mod = 0
        if law >= 9:
            law_level_mod = 1

        tech_level_mod = 0
        if tech_level in [0,1,2]:
            tech_level_mod = -2
            maximum_pct = 20 + min_max_roll
        elif tech_level == 3:
            tech_level_mod = -1
            maximum_pct = 30 + min_max_roll
        elif tech_level == 4:
            tech_level_mod = 1
            maximum_pct = 60 + min_max_roll
        elif tech_level in [5,6,7,8,9]:
            tech_level_mod = 2
            maximum_pct = 90 + min_max_roll
        elif tech_level == 10:
            tech_level_mod = 1

        remarks_mod = 0
        if 'Ag' in remarks:
            remarks_mod = -2
            maximum_pct = 90 + min_max_roll
        elif 'Na' in remarks:
            remarks_mod = 2

        urban_pct_roll = (dice_roll + pcr_mod + atmos_mod + size_mod + population_mod + government_mod + law_level_mod
        + tech_level_mod + remarks_mod)

        if urban_pct_roll < 0: urban_pct_roll = 0
        elif urban_pct_roll > 13: urban_pct_roll = 13

        urban_pct_dict = {
            0: [0,0],
            1: [1,6],
            2: [7,12],
            3: [13-18],
            4: [19-24],
            5: [25,36],
            6: [37,48],
            7: [49,60],
            8: [61,72],
            9: [73,84],
            10: [85,90],
            11: [91,96],
            12: [97,99],
            13: [100,100]
        }

        start_pct_end_pct = urban_pct_dict[urban_pct_roll]
        urban_pct = random.randint(start_pct_end_pct[0], start_pct_end_pct[0] )

        if urban_pct < minimum_pct: urban_pct = minimum_pct
        elif urban_pct > maximum_pct: urban_pct = maximum_pct

        urban_pct = urban_pct / 100

        self.urban_pct = urban_pct


    def generate_major_cities_stats(self):
        population = self.input_dictionary['population']
        pop_mod = int(self.input_dictionary['pop_mod'])
        total_population: int = round((10 ** population) * pop_mod)
        urban_population: int = round(self.urban_pct * total_population)

        major_cities_total: int = 0
        major_city_population: int = 0

        if self.population_concentration == 0:
            major_cities_total = 0
            major_city_population = 0
        elif self.population_concentration >= 9 and population <= 5:
            major_cities_total = 1
            major_city_population = urban_population
        elif self.population_concentration < 9 and population <= 5:
            major_cities_total = 9 - self.population_concentration
            if population < major_cities_total: major_cities_total = population
            major_city_population = urban_population
        elif self.population_concentration >= 9 and population >= 6:
            dice_roll = gf.roll_dice(2)
            dice_info = DiceRoll(
                location=str(self.world_id),
                number=2,
                reason='major city pop roll',
                dice_result=dice_roll,
                table_result=str(dice_roll))
            du.insert_dice_rolls(self.db_name, dice_info)

            major_cities_total = population - dice_roll
            if major_cities_total <= 1: major_cities_total = 1
            major_city_population = urban_population

        else:
            dice_roll = gf.roll_dice(2)
            dice_info = DiceRoll(
                location=str(self.world_id),
                number=2,
                reason='major city roll',
                dice_result=dice_roll,
                table_result=str(dice_roll))
            du.insert_dice_rolls(self.db_name, dice_info)

            major_cities_total = round(((dice_roll - self.population_concentration) +
                                  ((self.urban_pct * 20) / self.population_concentration)))


            die_roll = gf.roll_dice(2)
            dice_info = DiceRoll(
                location=str(self.world_id),
                number=1,
                reason='major city pop roll',
                dice_result=die_roll,
                table_result=str(die_roll))
            du.insert_dice_rolls(self.db_name, dice_info)

            major_city_population = round((self.population_concentration/(die_roll + 7)) * urban_population)

        self.major_cities_total = major_cities_total
        if self.major_cities_total < 0: self.major_cities_total = 0
        self.major_cities_population_total = major_city_population



@dataclass
class World_Culture_Mongoose:
    db_name: str
    world_id: int
    diversity: int
    xenophilia: int
    uniqueness: int
    symbology: int
    social_cohension: int
    progressiveness: int
    expansionism: int
    militancy: int
    input_dictionary: dict


    def __init__(self, parms: Parameters, world_input_dictionary: dict):
        # Initialize attributes with provided values
        self.db_name = parms.db_name
        self.world_id = world_input_dictionary['world_id']
        self.diversity = -99
        self.xenophilia = -99
        self.symbology = -99
        self.social_cohesion = -99
        self.progressiveness = -99
        self.expansionism = -99
        self.militancy = -99
        self.input_dictionary = world_input_dictionary


    def generate_diversity(self):
        population = self.input_dictionary['population']
        heterogeneity: int = gf.hex_to_int(self.input_dictionary['cx'][1:2])
        diversity: int = 0

        if heterogeneity > population + 5:
            heterogeneity = population + 5
        elif heterogeneity < population - 5:
            heterogeneity = population - 5

        if heterogeneity < 1:
            if population > 0:
                heterogeneity = 1
            else:
                heterogeneity = 0

        self.diversity = heterogeneity

    def generate_xenophilia(self):
        acceptance: int = gf.hex_to_int(self.input_dictionary['cx'][2:3])
        population: int = self.input_dictionary['population']
        importance: int = 0
        raw_importance: str = self.input_dictionary['importance']
        raw_importance = raw_importance.replace("{","")
        raw_importance = raw_importance.replace("}", "")
        importance = int(raw_importance)

        xenophilia: int = acceptance

        if acceptance > importance + population:
            acceptance = importance + population
        elif acceptance < importance - population:
            acceptance = importance + population

        if acceptance < 1:
            if population > 0:
                acceptance = 1
            else:
                acceptance = 0

        self.xenophilia = acceptance

    def generate_social_cohesion(self):
        dice_roll = gf.roll_dice(2)
        dice_info = DiceRoll(
            location=str(self.world_id),
            number=2,
            reason='cohesion roll',
            dice_result=dice_roll,
            table_result=str(dice_roll))
        du.insert_dice_rolls(self.db_name, dice_info)

        government =    self.input_dictionary['government']
        law =           self.input_dictionary['law']
        diversity =     self.diversity
        population =    self.input_dictionary['population']
        pcr = du.get_world_pcr(self.db_name, self.input_dictionary['world_id'])[0]

        gov_mod: int = 0
        if government in [3,12]: gov_mod = 2
        elif government in [5,6,9]: gov_mod = 1

        law_mod = 0
        if law in [0,1,2]:
            law_mod = -2
        elif law >= 10:
            law_mod = 2

        pcr_mod = 0
        if pcr in [0,1,2,3]:
            pcr_mod = -2
        elif pcr >= 7:
            pcr_mod = 2

        diversity_mod = 0
        if diversity in [1,2]:
            diversity_mod = 4
        elif diversity in [3,4,5]:
            diversity_mod = 2
        elif diversity in [9,10,11]:
            diversity_mod = -2
        elif diversity >= 12:
            diversity_mod = -4

        self.social_cohesion = dice_roll + gov_mod + law_mod + pcr_mod + diversity_mod

        if self.social_cohesion < 1:
            if population > 0:
                self.social_cohesion = 1
            else:
                self.social_cohesion = 0


    def generate_progressiveness(self):
        dice_roll = gf.roll_dice(2)
        dice_info = DiceRoll(
            location=str(self.world_id),
            number=2,
            reason='progressiveness roll',
            dice_result=dice_roll,
            table_result=str(dice_roll))
        du.insert_dice_rolls(self.db_name, dice_info)

        population: int = self.input_dictionary['population']
        government: int = self.input_dictionary['government']
        law:        int = self.input_dictionary['law']
        diversity:  int = self.diversity
        xenophilia: int = self.xenophilia
        cohesion:   int = self.social_cohesion

        pop_mod: int = 0
        if population in [6,7,8]: pop_mod = -1
        elif population >= 9: pop_mod = -2

        gov_mod: int = 0
        if government == 5: gov_mod = 1
        elif government == 11: gov_mod = -2
        elif government in [13,14]: gov_mod = -6

        law_mod: int = 0
        if law in [9,10,11]: law_mod = -1
        elif law >= 12: law_mod = -4

        diversity_mod: int = 0
        if diversity in [1,2,3]: diversity_mod = -2
        elif diversity >= 12: diversity_mod = 1

        xenophilia_mod: int = 0
        if xenophilia in [1,2,3,4,5]:
            xenophilia_mod = -1
        elif xenophilia >= 9:
            xenophilia_mod = 2

        cohesion_mod: int = 0
        if cohesion in [1,2,3,4,5]:
            cohesion_mod = 2
        elif cohesion >= 9:
            cohesion_mod = -2

        self.progressiveness = dice_roll + pop_mod + gov_mod + law_mod + diversity_mod + xenophilia_mod + cohesion_mod
        if self.progressiveness < 1:
            if population > 0:
                self.progressiveness = 1
            else:
                self.progressiveness = 0

    def generate_expansionism(self):

        dice_roll = gf.roll_dice(2)
        dice_info = DiceRoll(
            location=str(self.world_id),
            number=2,
            reason='expansionism roll',
            dice_result=dice_roll,
            table_result=str(dice_roll))
        du.insert_dice_rolls(self.db_name, dice_info)

        government: int = self.input_dictionary['government']
        diversity:  int = self.diversity
        xenophilia: int = self.xenophilia
        population:     int = self.input_dictionary['population']

        gov_mod: int = 0
        if government == 10 or government >= 12:
            gov_mod = 2

        diversity_mod: int = 0
        if diversity in [1,2,3]:
            diversity_mod = 3
        elif diversity >= 12:
            diversity_mod = -3

        xenophilia_mod: int = 0
        if xenophilia <= 5:
            xenophilia_mod = 1
        elif xenophilia >= 9:
            xenophilia_mod = -2

        self.expansionism = dice_roll + gov_mod + diversity_mod + xenophilia_mod
        if self.expansionism < 1:
            if population > 0:
                self.expansionism = 1
            else:
                self.expansionism = 0

    def generate_militancy(self):

        dice_roll = gf.roll_dice(2)
        dice_info = DiceRoll(
            location=str(self.world_id),
            number=2,
            reason='militancy roll',
            dice_result=dice_roll,
            table_result=str(dice_roll))
        du.insert_dice_rolls(self.db_name, dice_info)

        government:     int = self.input_dictionary['government']
        law:            int = self.input_dictionary['law']
        xenophilia:     int = self.xenophilia
        expansionism:   int = self.expansionism
        population:     int = self.input_dictionary['population']

        gov_mod: int = 0
        if government >= 10: gov_mod = 3

        law_mod: int = 0
        if 9 <= law <= 11:
            law_mod = 1
        elif law >= 12:
            law_mod = 2

        xenophilia_mod: int = 0
        if xenophilia <= 5:
            xenophilia_mod = 1
        elif xenophilia >= 9:
            xenophilia_mod = -2

        expansionism_mod: int = 0
        if expansionism <= 5:
            expansionism_mod = -1
        elif 9 <= expansionism <= 11:
            expansionism_mod = 1
        elif expansionism >= 12:
            expansionism_mod = 2

        self.militancy = dice_roll + gov_mod + law_mod + xenophilia_mod + expansionism_mod
        if self.militancy < 1:
            if population > 0:
                self.militancy = 1
            else:
                self.militancy = 0
