# Created by Nuruzzaman Sakib (nsakib@crimson.ua.edu)

from ovito.data import NearestNeighborFinder, DataCollection, Particles
from ovito.io import import_file, export_file
from ovito.modifiers import CoordinationAnalysisModifier, ExpressionSelectionModifier, DeleteSelectedModifier, CreateBondsModifier
# Load a dataset.
pipeline = import_file('min.lmp')

# List of atom IDs to find neighbors.
atom_ids = []

with open('same_atom_two_hexa.txt', 'r') as file:
    for line in file:
        # Split the line into atom IDs and add them to the list
        ids = list(map(int, line.split()))
        atom_ids.extend(ids)

print(atom_ids)

# Fetch the current data from the pipeline.
data = pipeline.compute()

atom_id_all = data.particles['Particle Identifier']
extracted_ids = []
# Create a nearest neighbor finder object with 20-unit cutoff radius.
finder = NearestNeighborFinder(12, data)

# Dictionary to store neighbors for each atom ID.
neighbors_dict = {}

# Iterate over specified atom IDs.
for atom_id in atom_ids:
    neighbors = [atom_id]
    
    # Get the index corresponding to the atom ID.
    index = list(atom_id_all).index(atom_id)

    # Find neighbors around the atom.
    for neighbor in finder.find(index):
        neighbors.append(atom_id_all[neighbor.index])  # or neighbor.id if you want to store IDs instead of indices.
    
    for neighbor_id in neighbors:
        if neighbor_id not in extracted_ids:
            extracted_ids.append(neighbor_id)

#print(extracted_ids)

def filter_lammps_data(input_file, output_file, desired_atom_ids):
    with open(input_file, 'r') as infile:
        lines = infile.readlines()
        
        # Determine where the Atoms section starts and ends
        atom_start = lines.index("Atoms # atomic\n") + 2
        atom_end = lines[atom_start:].index("\n") + atom_start
        
        # Extract the atom lines and filter them based on the desired IDs
        atom_lines = lines[atom_start:atom_end]
        filtered_atom_lines = [line for line in atom_lines if int(line.split()[0]) in desired_atom_ids]
        
        # Replace the original atom lines with the filtered lines in the content
        lines[atom_start:] = filtered_atom_lines

        # Update atom count in the header
        for i, line in enumerate(lines):
            if "atoms" in line:
                lines[i] = f"{len(filtered_atom_lines)} atoms\n"
                break
        
        # Write the modified content to the output file
        with open(output_file, 'w') as outfile:
            outfile.writelines(lines)

filter_lammps_data('min.lmp', 'output.data', extracted_ids)

def get_atom_properties(file_path):
    pipeline = import_file(file_path)
    data = pipeline.compute()
    lx = data.cell_[:, 0][0]
    ly = data.cell_[:, 1][1]

    pipeline.modifiers.append(CoordinationAnalysisModifier(cutoff = 1.85, number_of_bins = 200))
    pipeline.modifiers.append(ExpressionSelectionModifier(expression = 'Coordination < 2'))
    pipeline.modifiers.append(DeleteSelectedModifier())
    pipeline.modifiers.append(CreateBondsModifier(mode=CreateBondsModifier.Mode.Uniform, cutoff=1.85))
    data = pipeline.compute()

    # Get required data arrays
    atom_id = data.particles['Particle Identifier']
    #print(atom_id[:])
  
    position = data.particles['Position']
    pos_x = position[:,0]
    #print(pos_x[:])
    pos_y = position[:,1]

    neighbors = {}
    for a,b in data.particles.bonds.topology:
        if data.particles.identifiers[...][a] in neighbors:
            if data.particles.identifiers[...][b] not in neighbors[data.particles.identifiers[...][a]]:
                neighbors[data.particles.identifiers[...][a]].append(data.particles.identifiers[...][b])
        else:
            neighbors[data.particles.identifiers[...][a]] = [data.particles.identifiers[...][b]]

        # Add atom1 as a neighbor of atom2
        if data.particles.identifiers[...][b] in neighbors:
            if data.particles.identifiers[...][a] not in neighbors[data.particles.identifiers[...][b]]:
                neighbors[data.particles.identifiers[...][b]].append(data.particles.identifiers[...][a])
        else:
            neighbors[data.particles.identifiers[...][b]] = [data.particles.identifiers[...][a]]

    return atom_id, pos_x, pos_y, neighbors

# Path of LAMMPS input file
lammps_input_file = 'output.data'

atom_id, pos_x, pos_y, neighbors = get_atom_properties(lammps_input_file)

with open("atom_data_two_hexa++" + ".txt", "w") as file:
    for i in range(len(atom_id)):
        if atom_id[i] in neighbors:
            file.write(f"{atom_id[i]}\t\t{pos_x[i]}\t\t{pos_y[i]}\t\t{' '.join(map(str, neighbors[atom_id[i]]))}\n")

