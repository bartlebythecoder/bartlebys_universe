import tkinter as tk
from math import sqrt

import lookup_tables as lu
import math_functions as mf


#hex_centers = lu.hex_centers_list


def draw_hexagon(canvas, center_x, center_y, size, color="white"):
    """
    Draws a flat-topped hexagon on the canvas.
    """
    points = [
        (center_x - size, center_y),
        (center_x - size / 2, center_y - size * sqrt(3) / 2),
        (center_x + size / 2, center_y - size * sqrt(3) / 2),
        (center_x + size, center_y),
        (center_x + size / 2, center_y + size * sqrt(3) / 2),
        (center_x - size / 2, center_y + size * sqrt(3) / 2)
    ]
    canvas.create_polygon(points, fill=color, outline="black")

def draw_hex_grid(canvas, size, grid_width, grid_height):
    """
    Draws a flat-topped hex grid on the canvas.
    """
    hex_centers_list = []
    hex_label_dy = {}
    row_list = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
    column_list = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    row_index = 0
    for row in range(grid_height):

        if row_list[row_index] in ['01', '03', '05', '07']:
            col_index = 1
        else:
            col_index = 0
        for col in range(grid_width):

            offset_y = col * size * sqrt(3)
            if row % 2 == 1:  # Odd rows are offset
                offset_y += size * sqrt(3) / 2

            center_x = row * size * 1.5  # Vertical spacing for flat-topped hexes
            center_y = offset_y
            label = row_list[row_index] + column_list[col_index]
            print(center_y, center_y, label, row_index, col_index)
            hex_centers_list.append([[center_x, center_y], label])
            hex_label_dy[label] = [center_x, center_y]
            draw_hexagon(canvas, center_x, center_y, size)
            col_index += 1
        row_index += 1
    return hex_centers_list, hex_label_dy

def add_circle(event, hex_centers_list, hex_label_dy):
    """
    Adds a red circle to the canvas at the clicked coordinates.
    """
    center_x, center_y = event.x, event.y
    new_hex_label = mf.knn_classify(1, hex_centers_list, (center_x, center_y ))
    print(f'New Hex: {new_hex_label}')
    center_x, center_y = hex_label_dy[new_hex_label]
    radius = 10  # Adjust the radius as needed
    canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius, fill="red")


# Create the main window
root = tk.Tk()
root.title("Hex Grid")

# Canvas dimensions
canvas_width = 400
canvas_height = 543

# Create a canvas
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
canvas.pack()

# Grid parameters
row_count = 10
column_count = 11
cell_size = 30  # Radius of the inscribed circle

# Draw the grid
hex_centers, hex_label_dy = draw_hex_grid(canvas, cell_size, column_count, row_count)
# Bind mouse click event

canvas.bind("<Button-1>", lambda event: add_circle(event, hex_centers, hex_label_dy))

root.mainloop()
