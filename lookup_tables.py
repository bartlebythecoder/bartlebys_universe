# Used for the standard mongoose approach (Build #0)
mgt2e_standard_star_type_dy = {
    2: 'Special',
    3: 'M',
    4: 'M',
    5: 'M',
    6: 'M',
    7: 'K',
    8: 'K',
    9: 'G',
    10: 'G',
    11: 'F',
    12: 'Hot',
    13: 'Hot'
}

# Used for the realistic "optional" mongoose rules (Build #1)
mgt2e_optional_star_type_dy = {
    2: 'Special',
    3: 'M',
    4: 'M',
    5: 'M',
    6: 'M',
    7: 'M',
    8: 'M',
    9: 'K',
    10: 'G',
    11: 'F',
    12: 'Hot',
    13: 'Hot'
}

# Used for mongoose hot start types (Builds #0 and #1)
mgt2e_hot_star_type_dy = {
    2: 'A',
    3: 'A',
    4: 'A',
    5: 'A',
    6: 'A',
    7: 'A',
    8: 'A',
    9: 'A',
    10: 'B',
    11: 'B',
    12: 'O',
    13: 'O'
}

# Used for CT Book 6 rules (Build #2)
ct_star_type_dy = {
    2: 'A',
    3: 'M',
    4: 'M',
    5: 'M',
    6: 'M',
    7: 'M',
    8: 'K',
    9: 'G',
    10: 'F',
    11: 'F',
    12: 'F'
}

# Used for mongoose special star class (Builds #0 and #1)
mgt2e_special_star_class_dy = {
    2: 'VI',
    3: 'VI',
    4: 'VI',
    5: 'VI',
    6: 'IV',
    7: 'IV',
    8: 'IV',
    9: 'III',
    10: 'III',
    11: 'Giants',
    12: 'Giants'
}

# Used for mongoose giant star class (Builds #0 and #1)
mgt2e_giant_star_class_dy = {
    2: 'III',
    3: 'III',
    4: 'III',
    5: 'III',
    6: 'III',
    7: 'III',
    8: 'III',
    9: 'II',
    10: 'II',
    11: 'Ib',
    12: 'Ia'
}

# Used to build subsector number lists
subsector_letter_dy = {
    'A': [[1, 8], [1, 10]],
    'B': [[9, 16], [1, 10]],
    'C': [[17, 24], [1, 10]],
    'D': [[25, 32], [1, 10]],

    'E': [[1, 8], [11, 20]],
    'F': [[9, 16], [11, 20]],
    'G': [[17, 24], [11, 20]],
    'H': [[25, 32], [11, 20]],

    'I': [[1, 8], [21, 30]],
    'J': [[9, 16], [21, 30]],
    'K': [[17, 24], [21, 30]],
    'L': [[25, 32], [21, 30]],

    'M': [[1, 8], [31, 40]],
    'N': [[9, 16], [31, 40]],
    'O': [[17, 24], [31, 40]],
    'P': [[25, 32], [31, 40]]

}

# Used to lookup stellar temperature
star_class_col_num_dy = {
    'Ia':  0,
    'Ib':  1,
    'II':  2,
    'III': 3,
    'IV':  4,
    'V':   5,
    'VI':  6
}

# Used to lookup types of companion stars
companion_star_category_dy = {
    1: 'other',
    2: 'other',
    3: 'other',
    4: 'random',
    5: 'random',
    6: 'lesser',
    7: 'lesser',
    8: 'sibling',
    9: 'sibling',
    10: 'twin',
    11: 'twin',
    12: 'twin',
    13: 'twin'
}


# Used to lookup types of secondary stars
secondary_star_category_dy = {
    1: 'other',
    2: 'other',
    3: 'other',
    4: 'random',
    5: 'random',
    6: 'random',
    7: 'lesser',
    8: 'lesser',
    9: 'sibling',
    10: 'sibling',
    11: 'twin',
    12: 'twin',
    13: 'twin'
}


# Used to lookup types of secondary stars
orbit_number_to_au_dy = {
    0: 0,
    1: 0.4,
    2: 0.7,
    3: 1.0,
    4: 1.6,
    5: 2.8,
    6: 5.2,
    7: 10,
    8: 20,
    9: 40,
    10: 77,
    11: 154,
    12: 308,
    13: 615,
    14: 1230,
    15: 2500,
    16: 4900,
    17: 9800,
    18: 19500,
    19: 39500,
    20: 78700
}

base_eccentricity_dy = {
    1: -0.001,
    2: -0.001,
    3: -0.001,
    4: -0.001,
    5: -0.001,
    6: 0,
    7: 0,
    8: 0.03,
    9: 0.03,
    10: 0.05,
    11: 0.05,
    12: 0.3,
    13: 0.3,
    14: 0.3,
    15: 0.3
}

