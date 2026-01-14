# Cretaed by Nuruzzaman Sakib (nsakib@crimson.ua.edu)

import sys
import math
import matplotlib.pyplot as plt

if len(sys.argv) != 3:
    print("Syntax: python shared_edge.py GBX_Y.lmp PNG_File_Name")
    sys.exit()

#lammps data file cell size
def read_ly_from_lammps_data(file_path):
    with open(file_path, 'r') as file:
        ly = None
        for line in file:
            if line.strip().endswith("ylo yhi"):
                ly = float(line.split()[1]) - float(line.split()[0])
            
            # If both lx and ly have been found, stop reading the file
            if ly is not None:
                break
        
    if ly is not None:
        return ly
    else:
        raise ValueError("ly value not found in the LAMMPS data file.")

# Open the file penta_data.txt for reading
with open('penta_data_unique.txt', 'r') as file:
    # Initialize an empty list to store the coordinate pairs
    pentagon_coord = []

    # Iterate over each line in the file
    for line in file:
        # Split the line by spaces to separate the coordinates
        coordinates = line.strip().split()

        # Extract the coordinates and convert them to float
        x1, y1, x2, y2, x3, y3, x4, y4, x5, y5 = map(float, coordinates)

        # Create a tuple pair of the coordinates and append it to the list
        pentagon_coord.append([(x1, y1), (x2, y2), (x3, y3), (x4, y4), (x5, y5), (x1, y1)])  # Repeat first node

# Open the file hepta_data.txt for reading
with open('hepta_data_unique.txt', 'r') as file:
    # Initialize an empty list to store the coordinate pairs
    heptagon_coord = []

    # Iterate over each line in the file
    for line in file:
        # Split the line by spaces to separate the coordinates
        coordinates = line.strip().split()

        # Extract the coordinates and convert them to float
        x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6, y6, x7, y7 = map(float, coordinates)

        # Create a tuple pair of the coordinates and append it to the list
        heptagon_coord.append([(x1, y1), (x2, y2), (x3, y3), (x4, y4), (x5, y5), (x6, y6), (x7, y7), (x1, y1)])  # Repeat first node

shared_edge_coordinates = []
ly = float(read_ly_from_lammps_data(sys.argv[1]))

for i in range(len(heptagon_coord)):
    # Iterate through each pair of consecutive vertices in the heptagon
    heptagon_vertices = heptagon_coord[i]
    pentagon_vertices = pentagon_coord[i]
    for k in range(len(heptagon_vertices) - 1):  # Updated range to exclude the repeated first node
        heptagon_edge_start = heptagon_vertices[k]
        heptagon_edge_end = heptagon_vertices[k + 1]

        # Iterate through each pair of consecutive vertices in the pentagon
        for m in range(len(pentagon_vertices) - 1):  # Updated range to exclude the repeated first node
            pentagon_edge_start = pentagon_vertices[m]
            pentagon_edge_end = pentagon_vertices[m + 1]

            # Check if the edge coordinates are the same
            if (heptagon_edge_start == pentagon_edge_start and heptagon_edge_end == pentagon_edge_end) or \
               (heptagon_edge_start == pentagon_edge_end and heptagon_edge_end == pentagon_edge_start):
                        
                # Check if the y-coordinates fall within the specified range
                if 0 <= heptagon_edge_start[1] <= ly and 0 <= heptagon_edge_end[1] <= ly:
                    shared_edge_coordinates.append(heptagon_edge_start)
                    shared_edge_coordinates.append(heptagon_edge_end)

# Extract x and y coordinates from shared edge coordinates
x_shared = [coord[0] for coord in shared_edge_coordinates]
y_shared = [coord[1] for coord in shared_edge_coordinates]

# Plot all coordinates
for pentagon_vertices in pentagon_coord:
    x_pentagon = [coord[0] for coord in pentagon_vertices]
    y_pentagon = [coord[1] for coord in pentagon_vertices]
    plt.plot(x_pentagon, y_pentagon, 'b')

for heptagon_vertices in heptagon_coord:
    x_heptagon = [coord[0] for coord in heptagon_vertices]
    y_heptagon = [coord[1] for coord in heptagon_vertices]
    plt.plot(x_heptagon, y_heptagon, 'g')

# Plot shared coordinates in red
plt.plot(x_shared, y_shared, 'ro')

# Set aspect ratio to equal
plt.axis('equal')

# Add labels and title
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Shared Edge Coordinates')

#########################################################################
def find_atom_id(lammps_file, x, y):
    atom_id = None

    with open(lammps_file, 'r') as file:
        atoms_section = False
        for line in file:
            if line.startswith('Atoms'):
                atoms_section = True
                continue
            
            if line.startswith('Velocities'):
                atoms_section = False
                break
                
            if atoms_section:
                data = line.split()
                if not data:
                    continue

                current_atom_id = int(data[0])    
                current_x = float(data[2])
                current_y = float(data[3])
				
                if round(current_x,12) == round(x,12) and round(current_y,12) == round(y,12):
                    atom_id = current_atom_id
                    break
        
    if atom_id is not None:
        print(f"Atom ID: {atom_id}")
    else:
        print("Atom not found.")
    return atom_id

lammps_input_file = sys.argv[1]
atom_id_shared_edge = []

for i in range(len(x_shared)):
    print(x_shared[i],y_shared[i])
    atom_id_shared_edge.append(find_atom_id(lammps_input_file, x_shared[i], y_shared[i]))
    
########################################################################

with open('same_atom.dat', 'a') as file:
    for i in range(0,len(atom_id_shared_edge),2):
        file.write(f"{atom_id_shared_edge[i]}\t\t{atom_id_shared_edge[i+1]}\n")

output_filename = sys.argv[2]
plt.savefig(output_filename)
# Show the plot
#plt.show()

