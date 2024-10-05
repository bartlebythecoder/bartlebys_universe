import bodies
import database_utils as du


def get_world_info(parms: bodies.Parameters, location: str):
    system_dy = du.get_system_info(parms, location)
    star_list = du.get_star_info(parms, location)
    return system_dy, star_list


def build_worlds(parms: bodies.Parameters, location: str):
    system_dy, star_list = get_world_info(parms, location)
    orbit_designation_list = []
    for each_star in star_list:
        each_star['star_designation'].append
    world_var = bodies.World(
        db_name=parms.db_name,
        location=location,
        orbit_slot='AA',
        star_designation='Xx',
        orbit_number=1.23,
        world_type='Yup'
    )

    print(world_var)
    du.insert_world_details(world_var)