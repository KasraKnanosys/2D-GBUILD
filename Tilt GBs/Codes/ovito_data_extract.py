# Cretaed by Nuruzzaman Sakib (nsakib@crimson.ua.edu)

import ovito
from ovito.data import BondsEnumerator
from ovito.modifiers import CreateBondsModifier, ExpressionSelectionModifier, DeleteSelectedModifier, ReplicateModifier
import sys

if len(sys.argv) != 2:
    print("Syntax: python ovito_data_extract.py GBX_Y.lmp")
    sys.exit()

def get_bond_properties(file_path):
    pipeline = ovito.io.import_file(file_path)
    pipeline.modifiers.append(CreateBondsModifier(mode=CreateBondsModifier.Mode.Uniform, cutoff=1.6))
    data = pipeline.compute()

    with open('bond_data.txt','w') as fdata:

        for a,b in data.particles.bonds.topology:
            fdata.write("{}\t{}\n".format(data.particles.identifiers[...][a],data.particles.identifiers[...][b]))

def get_atom_properties(file_path, i):
    pipeline = ovito.io.import_file(file_path)
    data = pipeline.compute()
    lx = data.cell_[:, 0][0]
    ly = data.cell_[:, 1][1]
    
    if (ly/2)>5:
        tolerance = 5
    else:
        tolerance = ly/2

    GB_pos = lx * i * 0.25
    expression = f'Position.X > ({GB_pos}+5) || Position.X < ({GB_pos}-5)'
    pipeline.modifiers.append(ExpressionSelectionModifier(expression=expression))
    pipeline.modifiers.append(DeleteSelectedModifier())
    pipeline.modifiers.append(ReplicateModifier(num_y=3))
    expression = f'Position.Y < -{tolerance} || Position.Y > ({ly}+{tolerance})'
    pipeline.modifiers.append(ExpressionSelectionModifier(expression=expression))
    pipeline.modifiers.append(DeleteSelectedModifier())
    pipeline.modifiers.append(CreateBondsModifier(mode=CreateBondsModifier.Mode.Uniform, cutoff=1.6))
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

    return ly,atom_id, pos_x, pos_y, neighbors

# Path to LAMMPS input file
lammps_input_file = sys.argv[1]
#print the bond info in a txt file
get_bond_properties(lammps_input_file)

for i in [1, 3]:
    ly,atom_id, pos_x, pos_y, neighbors = get_atom_properties(lammps_input_file, i)

    with open("atom_data_GB_" + str(i) + ".txt", "w") as file:
        file.write(f"{ly}\n")
        for i in range(len(atom_id)):
            if atom_id[i] in neighbors:
                file.write(f"{atom_id[i]}\t\t{pos_x[i]}\t\t{pos_y[i]}\t\t{' '.join(map(str, neighbors[atom_id[i]]))}\n")
            else:
                continue  # Skip this atom
