# Created by Nuruzzaman Sakib (nsakib@crimson.ua.edu)

import ovito
from ovito.modifiers import CreateBondsModifier, CoordinationAnalysisModifier, ExpressionSelectionModifier, DeleteSelectedModifier

def find_atom_id(lammps_file):
    atom_id = []
    pos_xy = []

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

                atom_id.append(int(data[0]))
                pos_xy.append((float(data[2]),float(data[3])))
    return atom_id, pos_xy

lammps_file = 'gb_data.lmp'
gb_id, _ = find_atom_id(lammps_file)

atom_id, pos = find_atom_id('min.lmp')

extracted_pos = [pos[i] for i in range(len(atom_id)) if atom_id[i] in gb_id]
n_atom = len(extracted_pos)

with open('min.lmp','r') as fdata:
    lines = fdata.readlines()
    dim_xlo = float(lines[5].split()[0])
    dim_xhi = float(lines[5].split()[1])
    dim_ylo = float(lines[6].split()[0])
    dim_yhi = float(lines[6].split()[1])
    dim_zlo = float(lines[7].split()[0])
    dim_zhi = float(lines[7].split()[1])

# Print the extracted pos elements
with open('data.lmp','w') as fdata:
    fdata.write('# LAMMPS data file written by python_NSAKIB\n')
    fdata.write('{} {}\n'.format(n_atom,'atoms'))
    fdata.write('1 atom types\n')
    fdata.write('{} {} {}\n'.format(dim_xlo,dim_xhi,'xlo xhi'))
    fdata.write('{} {} {}\n'.format(dim_ylo,dim_yhi,'ylo yhi'))
    fdata.write('{} {} {}\n'.format(dim_zlo,dim_zhi,'zlo zhi'))
    fdata.write('\n')
    fdata.write('Mass\n')
    fdata.write('\n')
    fdata.write('1  12.0 # C\n')
    fdata.write('\n')
    fdata.write('Atoms  # atomic\n')
    fdata.write('\n')
        
    for i in range(len(extracted_pos)):
        fdata.write('{}\t{}\t{}\t{}\t{}\n'.format(i+1,'1',extracted_pos[i][0],extracted_pos[i][1],'5'))
    
    fdata.close()

def get_bond_properties(file_path,file_name):
    pipeline = ovito.io.import_file(file_path)
    pipeline.modifiers.append(CreateBondsModifier(mode=CreateBondsModifier.Mode.Uniform, cutoff=1.85))
    data = pipeline.compute()

    with open(file_name,'w') as fdata:

        for a,b in data.particles.bonds.topology:
            fdata.write("{}\t{}\n".format(data.particles.identifiers[...][a],data.particles.identifiers[...][b]))


def get_atom_properties(file_path):
    pipeline = ovito.io.import_file(file_path)
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

# Provide the path to your LAMMPS input file
lammps_input_file = 'data.lmp'

atom_id, pos_x, pos_y, neighbors = get_atom_properties(lammps_input_file)

# Print bond properties
get_bond_properties(lammps_input_file,'bond_data.txt')  #GB_area_bond properties
get_bond_properties('min.lmp','bond_data_all.txt')   #all atom bond properties

with open("atom_data_GB" + ".txt", "w") as file:
    for i in range(len(atom_id)):
        if atom_id[i] in neighbors:
            file.write(f"{atom_id[i]}\t\t{pos_x[i]}\t\t{pos_y[i]}\t\t{' '.join(map(str, neighbors[atom_id[i]]))}\n")

# Print the extracted pos elements
n_atom = len(neighbors)
with open('data.lmp','w') as fdata:
    fdata.write('# LAMMPS data file written by python_NSAKIB\n')
    fdata.write('{} {}\n'.format(n_atom,'atoms'))
    fdata.write('1 atom types\n')
    fdata.write('{} {} {}\n'.format(dim_xlo,dim_xhi,'xlo xhi'))
    fdata.write('{} {} {}\n'.format(dim_ylo,dim_yhi,'ylo yhi'))
    fdata.write('{} {} {}\n'.format(dim_zlo,dim_zhi,'zlo zhi'))
    fdata.write('\n')
    fdata.write('Mass\n')
    fdata.write('\n')
    fdata.write('1  12.0 # C\n')
    fdata.write('\n')
    fdata.write('Atoms  # atomic\n')
    fdata.write('\n')
        
    for i in range(len(atom_id)):
        if atom_id[i] in neighbors:
            fdata.write('{}\t{}\t{}\t{}\t{}\n'.format(atom_id[i],'1',pos_x[i],pos_y[i],'5'))
    
    fdata.close()
