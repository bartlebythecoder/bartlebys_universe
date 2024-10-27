import tkinter as tk
from math import sqrt

import bodies
import generic_functions as gf
import database_utils as du
import logging


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

    # Calculate the total width and height of the grid
    grid_width_pixels = (grid_width - 1) * size * 1.5 + size  # Account for the last hexagon's width
    grid_height_pixels = (grid_height - 1) * size * sqrt(3) + size * sqrt(3) / 2  # Account for the last row's height

    # Calculate the offsets to center the grid
    x_offset = (canvas_width - grid_width_pixels) / 2 + 50  # Increased horizontal offset
    y_offset = (canvas_height - grid_height_pixels) / 2 - 20  # Decreased vertical offset

    for row in range(grid_height):
        for col in range(grid_width):

            offset_y = col * size * sqrt(3)
            if row % 2 == 1:  # Odd rows are offset
                offset_y += size * sqrt(3) / 2

            center_x = row * size * 1.5  # Vertical spacing for flat-topped hexes
            center_y = offset_y

            # Apply the offsets to center the hexagons
            hex_center_x = center_x + x_offset
            hex_center_y = center_y + y_offset

            draw_hexagon(canvas, hex_center_x, hex_center_y, size)

            # Store the center coordinates in the dictionary
            hex_key = f"{row + 1:02d}{col + 1:02d}"
            subsector_hex_centers_dy[hex_key] = [hex_center_x, hex_center_y]


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


def update_map(subsector):
    canvas.delete("all")  # Clear the canvas
    draw_hex_grid(canvas, cell_size, column_count, row_count)  # Redraw the grid

    location_list = du.get_subsector_locations(parms.db_name, subsector)
    for each_location in location_list:
        if each_location in hex_label_dy:  # Use the updated hex_label_dy
            center_x, center_y = hex_label_dy[each_location]
            radius = 10  # Adjust the radius as needed
            circle = canvas.create_oval(center_x - radius, center_y - radius, center_x + radius,
                                        center_y + radius, fill="red")
            create_tooltip(canvas, circle, text=f"Hex: {each_location}")

    # Update the subsector label
    subsector_label.config(text=f"Subsector: {subsector}")


def on_key_press(event):
    global current_subsector_index
    if event.keysym == "Up":
        current_subsector_index = max(0, current_subsector_index - 1)
    elif event.keysym == "Down":
        current_subsector_index = min(len(subsectors) - 1, current_subsector_index + 1)
    elif event.keysym == "Escape":
        root.destroy()  # Exit the program
        return  # Stop further processing of the event

    update_map(subsectors[current_subsector_index])

subsector_hex_centers_dy = {}

hexes_chosen = {}

parms = bodies.Parameters(
    db_name='brock_88.db',
    build=0,
    frequency=2,
    random_seed=3)

# Create the main window
root = tk.Tk()
root.title("Hex Grid")

# Canvas dimensions
canvas_width = 500
canvas_height = 700

# Create a canvas
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
canvas.pack()

# Grid parameters
row_count = 8
column_count = 10
cell_size = 30  # Radius of the inscribed circle

# Draw the grid
draw_hex_grid(canvas, cell_size, column_count, row_count)

# Subsector list and current index
subsectors = [chr(i) for i in range(ord('A'), ord('P') + 1)]  # Create a list of subsectors from 'A' to 'P'
current_subsector_index = 0  # Start with subsector 'A'

subsector_label = tk.Label(root, text=f"Subsector: A")  # Start with 'A'
subsector_label.pack()


# Bind key press events
root.bind("<Up>", on_key_press)
root.bind("<Down>", on_key_press)
root.bind("<Escape>", on_key_press)  # Bind Escape key

# Calculate hex centers for all subsectors
hex_label_dy = gf.create_sector_coordinate_dy(subsector_hex_centers_dy)

update_map(subsectors[current_subsector_index])  # Initial map display

root.mainloop()