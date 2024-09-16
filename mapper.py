import tkinter as tk
from math import sqrt

import lookup_tables as lu
import math_functions as mf
import generic_functions as gf


hex_label_dy = lu.subsector_hex_centers_dy
hex_centers = gf.dict_to_indexed_list(hex_label_dy)
hexes_chosen = {}


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
    for row in range(grid_height):
        for col in range(grid_width):

            offset_y = col * size * sqrt(3)
            if row % 2 == 1:  # Odd rows are offset
                offset_y += size * sqrt(3) / 2

            center_x = row * size * 1.5  # Vertical spacing for flat-topped hexes
            center_y = offset_y
            draw_hexagon(canvas, center_x, center_y, size)


def create_tooltip(canvas, circle, text):
    """
    Creates and binds a tooltip to a given canvas object.
    """
    tooltip = tk.Label(canvas, text=text, bg="yellow", relief="solid", borderwidth=1)
    tooltip.pack_forget()  # Hide initially

    def enter(event):
        print(f'coords: {canvas.coords(circle)}')
        x, y = canvas.coords(circle)[0:2]  # Get the center of the circle
        tooltip.place(x=x + 10, y=y - 10)  # Position tooltip slightly offset from the center
        print(f'Tooltip placed {x}, {y}')

    def leave(event):
        tooltip.place_forget()  # Use place_forget to hide the tooltip

    # Bind events to the circle
    canvas.tag_bind(circle, "<Enter>", enter)
    canvas.tag_bind(circle, "<Leave>", leave)

    # Also bind the leave event to the tooltip itself
    tooltip.bind("<Leave>", leave)



def add_circle(event, hex_centers_list, hex_label_dy):
    """
    Adds a red circle to the canvas at the clicked coordinates and associates a tooltip.
    """
    center_x, center_y = event.x, event.y
    print(f'Hex Centers: {hex_centers_list}')
    new_hex_label = mf.knn_classify(1, hex_centers_list, (center_x, center_y ))
    print(f'Hex Selected: {new_hex_label}')
    center_x, center_y = hex_label_dy[new_hex_label]
    radius = 10  # Adjust the radius as needed
    print(f'{hex_label_dy[new_hex_label]}')
    if new_hex_label not in hexes_chosen:
        print('This is a new hex')

        circle = canvas.create_oval(center_x - radius, center_y - radius, center_x + radius,
                                    center_y + radius, fill="red")
        print(f'Circle:  {circle} ')

        circle_objects = canvas.find_withtag("circle_tag")

        hexes_chosen[new_hex_label] = circle

        # Pass the circle object directly
        print(f'placing tool tip here:  {hex_label_dy[new_hex_label]}')
        create_tooltip(canvas, circle, text=f"Hex: {new_hex_label}")


    else:
        print('Hex already created')
        canvas.delete(hexes_chosen[new_hex_label])
        del hexes_chosen[new_hex_label]




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
draw_hex_grid(canvas, cell_size, column_count, row_count)
canvas.bind("<Button-1>", lambda event: add_circle(event, hex_centers, hex_label_dy))

root.mainloop()
