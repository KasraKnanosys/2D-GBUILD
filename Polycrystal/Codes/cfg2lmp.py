# Created by Nuruzzaman Sakib (nsakib@crimson.ua.edu)

import sys

if len(sys.argv) != 2:
    print("Not enough command-line arguments provided for cfg2lmp.py code.")

# Read the .cfg file
with open(sys.argv[1], "r") as file:    #change file name
    lines = file.readlines()

# Extract metadata from the .cfg file
num_particles = int(lines[0].split('=')[1].strip())
xhi = float(lines[2].split('=')[1].split()[0])
yhi = float(lines[6].split('=')[1].split()[0])
zhi = float(lines[10].split('=')[1].split()[0])
entry_count = int(lines[11].split('=')[1].strip())

# Extract data lines with entry_count number of items
data_lines = [line for line in lines if len(line.split()) == entry_count]

# Extract pos_x, pos_y, and tags from the data lines
position_x = [float(line.split()[0])*xhi for line in data_lines]
position_y = [float(line.split()[1])*yhi for line in data_lines]
particle_type = [1 if float(line.split()[6]) == 0.0 else 2 for line in data_lines]

# Create the LAMMPS data file content with all atoms
lammps_data = [
    "#LAMMPS Data File generated from .cfg file using PYTHON. Created by Nuruzzaman Sakib",
    f"\n{num_particles} atoms",
    "2 atom types",
    f"\n{-xhi/2} {xhi/2} xlo xhi",
    f"{-yhi/2} {yhi/2} ylo yhi",
    f"0.0 {zhi} zlo zhi",
    "\nMasses\n",
    f"1 12.011",
    f"2 12.011\n\n",
    "Atoms  # atomic\n"
]
for atom_id, (x, y, tag) in enumerate(zip(position_x, position_y, particle_type), start=1):
    lammps_data.append(f"{atom_id} {tag} {x-(xhi/2)} {y-(yhi/2)} 5.0")

# Write to LAMMPS data file
output_file_path = "lammps_data.lmp"
with open(output_file_path, 'w') as file:
    file.write('\n'.join(lammps_data))

# Create the LAMMPS data file content with gb atoms
num_particles = particle_type.count(2)
#print(num_particles)
lammps_data = [
    "#LAMMPS Data File generated from .cfg file using PYTHON. Created by Nuruzzaman Sakib",
    f"\n{num_particles} atoms",
    "2 atom types",
    f"\n{-xhi/2} {xhi/2} xlo xhi",
    f"{-yhi/2} {yhi/2} ylo yhi",
    f"0.0 {zhi} zlo zhi",
    "\nMasses\n",
    f"1 12.011",
    f"2 12.011\n\n",
    "Atoms  # atomic\n"
]
for atom_id, (x, y, tag) in enumerate(zip(position_x, position_y, particle_type), start=1):
    if tag==2:
        lammps_data.append(f"{atom_id} {tag} {x-(xhi/2)} {y-(yhi/2)} 5.0")

output_file_path = "gb_data.lmp"
with open(output_file_path, 'w') as file:
    file.write('\n'.join(lammps_data))
