import tkinter as tk
from math import sqrt

import sys

import sqlite3
import bodies
import generic_functions as gf
import logging

def convert_to_hex_digit(value: str):
    number = int(value)
    if number > 9:
        return gf.int_to_hex(number)
    else:
        return str(value)

def get_subsector_info(db_name, subsector):
    sql_select_location = """
    SELECT t.location, t.system_name, t.starport, t.size, t.atmosphere, t.hydrographics, 
    t.population, t.government, t.law, t.tech_level, f.wtn
    FROM traveller_stats t
    LEFT JOIN system_stats s
    ON s.location = t.location
    LEFT JOIN far_trader f
    ON f.location = t.location
    WHERE main_world = 1 AND subsector = ?
    """
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        c.execute(sql_select_location, subsector)
        rows = c.fetchall()  # Fetch all results
    finally:
        c.close()

    conn.close()

    location_list = []
    name_list = []
    uwp_list = []
    size_list = []
    tech_list = []
    wtn_list = []
    atmosphere_list = []
    hydro_list = []

    if rows:
        for row in rows:
            location_list.append(row[0])
            name_list.append((row[1]))
            starport = row[2]
            size = convert_to_hex_digit(row[3])
            size_list.append(int(row[3]))

            atmosphere = convert_to_hex_digit(row[4])
            atmosphere_list.append(int(row[4]))

            hydrographics = convert_to_hex_digit(row[5])
            hydro_list.append(int(row[5]))

            population = convert_to_hex_digit(row[6])
            government = convert_to_hex_digit(row[7])
            law_level = convert_to_hex_digit(row[8])

            tech_level = convert_to_hex_digit(row[9])
            tech_list.append(int(row[9]))

            wtn = convert_to_hex_digit(row[10])
            wtn_list.append((int(row[10])*2))

            uwp = starport + size + atmosphere + hydrographics + population + government + law_level + '-' + tech_level

            uwp_list.append(uwp)


    return location_list, name_list, uwp_list, size_list, tech_list, wtn_list, atmosphere_list, hydro_list


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
    y_offset = (canvas_height - grid_height_pixels) / 2 - 50  # Decreased vertical offset

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
    global locations_list, names_list, name_objects, size_list, tech_list, wtn_list, current_mode
    canvas.delete("all")  # Clear the canvas
    draw_hex_grid(canvas, cell_size, column_count,
                  row_count)  # Redraw the grid

    (locations_list, names_list, uwp_list, size_list, tech_list, wtn_list,
     atmosphere_list, hydro_list) = get_subsector_info(parms.db_name, subsector)  # Update the lists

    name_objects = []  # Clear the list of name objects
    uwp_objects = []

    for i, each_location in enumerate(locations_list):
        if each_location in hex_label_dy:
            center_x, center_y = hex_label_dy[each_location]

            # Cycle through modes using a single variable
            if current_mode == "size":
                radius = size_list[i]
            elif current_mode == "tech":
                radius = tech_list[i]
            elif current_mode == "wtn":
                radius = wtn_list[i]
            else:  # Default mode (no specific mode selected)
                radius = 8

        if hydro_list[i] > 0:
                system_color = 'blue'
        else:
            system_color = 'black'
        color_label = "Blue = Hydro.  Black = No Hydro."

        if color_mode:
            color_label = "Atmosphere. W: None. Bl: stand. Cy: taint.  Y: ex.  R: corr insid"
            if hydro_list[i] > 0:
                if atmosphere_list[i] in [3, 5, 6, 8, 13, 14]:
                    system_color = 'blue'
                elif atmosphere_list[i] in [2, 4, 7, 9]:
                    system_color = 'cyan'
                elif atmosphere_list[i] in [10]:
                    system_color = 'yellow'
                elif atmosphere_list[i] in [11, 12]:
                    system_color = 'red'
                else: system_color = 'magenta'
            else:
                system_color = 'white'

        circle = canvas.create_oval(center_x - radius,
                                    center_y - radius,
                                    center_x + radius,
                                    center_y + radius,
                                    fill=system_color)
        create_tooltip(canvas, circle, text=f"Hex: {each_location}")

        # Add the name to the canvas and store its ID
        if show_names:
            name_id = canvas.create_text(center_x,
                                       center_y + 15,
                                       text=names_list[i],
                                       fill="blue",
                                       anchor="center")
            name_objects.append(name_id)  # Store the ID of the name object

        if show_uwp:
            uwp_id = canvas.create_text(center_x,
                                       center_y - 15,
                                       text=uwp_list[i],
                                       fill="blue",
                                       anchor="center")
            uwp_objects.append(uwp_id)  # Store the ID of the name object

    # Update the subsector label
    subsector_label.config(text=f"Subsector: {subsector}. (Use arrow keys to change)")
    mode_label.config(text=f"Current Mode: {current_mode}.  {color_label}")

def on_key_press(event):
    global current_subsector_row, current_subsector_col, show_names, \
        show_uwp, current_mode, color_mode
    if event.keysym == "Up":
        current_subsector_row = max(0, current_subsector_row - 1)
    elif event.keysym == "Down":
        current_subsector_row = min(3, current_subsector_row + 1)
    elif event.keysym == "Left":
        current_subsector_col = max(0, current_subsector_col - 1)
    elif event.keysym == "Right":
        current_subsector_col = min(3, current_subsector_col + 1)

    elif event.keysym == "space":
        show_names = not show_names  # Toggle the show_names flag
    elif event.keysym == "u":
        show_uwp = not show_uwp  # Toggle the show_uwp flag

    elif event.keysym == "s":
        # Cycle through modes
        if current_mode == "size":
            current_mode = "tech"
        elif current_mode == "tech":
            current_mode = "wtn"
        elif current_mode == "wtn":
            current_mode = "default"  # Add the default mode to the cycle
        else:  # current_mode == "default" or is not set
            current_mode = "size"  # Cycle back to size mode



    elif event.keysym == 'c':
        color_mode = not color_mode

    elif event.keysym == "Escape":
        sys.exit()  # Exit the entire


    # Calculate the subsector index based on row and column
    current_subsector_index = current_subsector_row * 4 + current_subsector_col
    update_map(subsectors[current_subsector_index])  # Update the map to show/hide names

    return

subsector_hex_centers_dy = {}

hexes_chosen = {}

parms = bodies.Parameters(
    db_name='solo-6v2.db',
    build=0,
    frequency=2,
    random_seed=3)

# Create the main window
root = tk.Tk()
root.title("Hex Grid")

# Create a title label
title_label = tk.Label(root, text="Sector Solo-6", font=("Helvetica", 16))  # Adjust font as needed
title_label.pack(side="top", pady=(20, 0))  # 20 pixels padding

# Subsector label (PACK THIS BEFORE THE CANVAS)
subsector_label = tk.Label(root, text=f"Subsector: A")
subsector_label.pack(side="top", pady=(10, 0))

# Canvas dimensions
canvas_width = 500
canvas_height = 600

# Create a canvas
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
canvas.pack()

# Grid parameters
row_count = 8
column_count = 10
cell_size = 30  # Radius of the inscribed circle

# Draw the grid
draw_hex_grid(canvas, cell_size, column_count, row_count)

# Subsector list in a 4x4 grid
subsectors = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
    'P'
]

# Current subsector row and column
current_subsector_row = 0
current_subsector_col = 0

# Bind key press events
root.bind("<Up>", on_key_press)
root.bind("<Down>", on_key_press)
root.bind("<Left>", on_key_press)  # Bind Left arrow key
root.bind("<Right>", on_key_press)  # Bind Right arrow key
root.bind("<space>", on_key_press)
root.bind("u", on_key_press)
root.bind("<Escape>", on_key_press)  # Bind Escape key

root.bind("s", on_key_press)
root.bind("c", on_key_press)

# Calculate hex centers for all subsectors
hex_label_dy = gf.create_sector_coordinate_dy(subsector_hex_centers_dy)
name_objects = []  # List to store the IDs of the name objects
show_names = False # Flag to track whether names should be shown
show_uwp = False # Flag to track whether uwp should be shown

current_mode =  "default"
color_mode = False

# Create a label to display the current mode
mode_label = tk.Label(root, text=f"Size Mode: {current_mode}")
mode_label.pack(side="bottom")  # Place the label at the bottom


# Create a label to display the hotkeys
hotkey_label = tk.Label(root, text="""<Space bar> Names.  "U" UWP.  "S" Size modes. "C" Color Modes""")
hotkey_label.pack(side="bottom")  # Place the label at the bottom of the window

# Calculate the subsector index based on row and column
current_subsector_index = current_subsector_row * 4 + current_subsector_col
update_map(subsectors[current_subsector_index])  # Update the map



# Start the main loop
root.mainloop()