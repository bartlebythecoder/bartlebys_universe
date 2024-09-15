import math_functions as mf


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

test_knn = mf.knn_classify(1, hex_centers, (45, 67))
print(test_knn)