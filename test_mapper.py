import math_functions as mf
import lookup_tables as lu

def dict_to_indexed_list(data_dict):
    """
    Converts a dictionary into a list of tuples, where each tuple contains a value from the dictionary and its corresponding index.

    Args:
        data_dict: The dictionary to be transformed.

    Returns:
        A list of tuples, each containing a value from the dictionary and its index.
    """
    return [(value, key) for key, value in data_dict.items()]


values = [(0,4), (20, 45), (20,45), (0,4), (0.4)]

test = mf.majority_vote(values)
print(test)

test_distance = mf.distance((4,4),(6,3))
print (test_distance)

labelled_points = [(0,4)]

hex_centers = [
    ([45.0, 25.98], '0102'),
    ([45.0, 77.94], '0103'),
    ([270.0, 51.96], '0203'),
    ([270.0, 103.92], '0204'),
    ([360.0, 519.62], '0401')
]
print(f'Hex Centers: {hex_centers}')
test_knn = mf.knn_classify(1, hex_centers, (45, 67))
print(test_knn)

filename = 'hex_label.json'
hex_label_dy = lu.subsector_hex_centers
hex_centers = dict_to_indexed_list(hex_label_dy)
print(hex_centers)
test_knn = mf.knn_classify(1, hex_centers, (45, 67))
print(test_knn)