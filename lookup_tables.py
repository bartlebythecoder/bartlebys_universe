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
    11: '1b',
    12: '1a'
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

#Used to lookup stellar temperature
star_class_col_num_dy = {
    'Ia':  0,
    'Ib':  1,
    'II':  2,
    'III': 3,
    'IV':  4,
    'V':   5,
    'VI':  6
}

#Used to lookup types of companion stars
companion_star_category_dy = {
    1: 'Other',
    2: 'Other',
    3: 'Other',
    4: 'Random',
    5: 'Random',
    6: 'Lesser',
    7: 'Lesser',
    8: 'Sibling',
    9: 'Sibling',
    10: 'Twin',
    11: 'Twin',
    12: 'Twin',
    13: 'Twin'
}
