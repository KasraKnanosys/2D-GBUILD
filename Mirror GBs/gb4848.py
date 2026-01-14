#created by Nuruzzaman Sakib (nsakib@crimson.ua.edu)

from ase import Atoms, Atom
from ase.build import make_supercell
from ase.io import write
import sys

defect_4 = [int(sys.argv[1]),int(sys.argv[2])]    #must be integer number

# Define individual atoms
atom1 = Atom('Se', (3.789717692600,       3.281983590000,       498.3294560000))
atom2 = Atom('Se', (0.947422317400,       1.640983590000,       498.3294560000))
atom3 = Atom('Se', (3.789717692600,       3.281983590000,       501.6705440000))
atom4 = Atom('Se', (0.947422317400,       1.640983590000,       501.6705440000))
atom5 = Atom('W',  (4.737168433000,       1.640983590000,       500.0000000000))
atom6 = Atom('W',  (1.894873057800,       3.281983590000,       500.0000000000))      

# Create Atoms object
molecule = Atoms([atom1, atom2, atom3, atom4, atom5, atom6])

# Define the simulation cell (box) size
molecule.cell = [
    [5.684590750400, 0, 0],
    [0, 3.282000000000, 0],
    [0, 0, 1000.000000000]
]

# set the pbc (periodic boundary conditions)
molecule.set_pbc([True, True, True])  # Periodic in all three directions

# Accessing information
#print("Number of atoms:", len(molecule))
#print("Atom types:", [atom.symbol for atom in molecule])
#print("Box dimensions:", molecule.cell.lengths())
#print("Atomic positions:\n", molecule.positions)

move_right_cell = (molecule.positions[4][0]- molecule.positions[5][0]) - molecule.positions[1][0]*2
#print(move_right_cell)

# Define replication factors
nx, ny, nz = 10, defect_4[0]+defect_4[1]+1, 1  # Replicate nx and ny times in x direction and y directions, 1 time in z direction
print(nx, ny, nz)
# Define the replication matrix
replication_matrix = [
    [nx, 0, 0],
    [0, ny, 0],
    [0, 0, nz]
]

# Create the supercell
supercell_L = make_supercell(molecule, replication_matrix, wrap = True, tol = 1e-08)

# Save the Left structure
#write('Left.xyz', supercell_L)

# Now 'supercell' is your replicated structure
#print("Number of atoms in supercell:", len(supercell))
#print("Supercell atomic positions:\n", supercell.positions)

#Now mirror the structure, Mirroring across the yz-plane
supercell_R = supercell_L.copy()
for atom in supercell_R:
    atom.position[0] = supercell_R.cell.lengths()[0] - atom.position[0]
    atom.position[1] = atom.position[1] + 1.641   #when making automated, change 1.641 to the y distance of M and X for MX2
    
# After mirroring, wrap atoms to ensure they are within the cell
supercell_R.wrap()
for atom in supercell_R:
    atom.position[0] = atom.position[0] + move_right_cell + supercell_R.cell.lengths()[0]

#Write the left supercell
write('Left.xyz', supercell_L)
# Write the right supercell
write('Right.xyz', supercell_R)

#########################################Find the Atoms near the GB Line#####################################
def find_nearest_atoms_to_boundaries(supercell, ny):
    # Sort atoms by their x-coordinate
    atoms_sorted_left = sorted(supercell, key=lambda atom: atom.position[0])
    if(atoms_sorted_left[0].symbol=='Se'):
        atoms_left = sorted(atoms_sorted_left[0:ny*2],key=lambda atom: atom.position[1])
        atoms_left = atoms_left[::2]
    elif (atoms_sorted_left[0].symbol=='W'):
        atoms_left = sorted(atoms_sorted_left[0:ny],key=lambda atom: atom.position[1])
    
    #print(atoms_left)
    
    atoms_sorted_right = sorted(supercell, key=lambda atom: -atom.position[0])
    if(atoms_sorted_right[0].symbol=='Se'):
        atoms_right = sorted(atoms_sorted_right[0:ny*2],key=lambda atom: atom.position[1])
        atoms_right = atoms_right[::2]
    elif (atoms_sorted_right[0].symbol=='W'):
        atoms_right = sorted(atoms_sorted_right[0:ny],key=lambda atom: atom.position[1])
    
    #print(atoms_right)
    return atoms_left, atoms_right

L_atoms_left, L_atoms_right = find_nearest_atoms_to_boundaries(supercell_L, ny)
R_atoms_left, R_atoms_right = find_nearest_atoms_to_boundaries(supercell_R, ny)

#add atoms to left supercell left portion
for i in range(defect_4[1]):
    if (L_atoms_left[ny-2-i].symbol == 'Se'):
        new_atom1 = Atom('W', position=(L_atoms_left[ny-2-i].position[0]-1.894844635, L_atoms_left[ny-2-i].position[1], 500.0000000000))
        supercell_L.append(new_atom1)

#add atoms to left supercell right portion
for i in range(defect_4[1]):
    if (L_atoms_right[ny-2-i].symbol == 'W'):
        new_atom1 = Atom('Se', position=(L_atoms_right[ny-2-i].position[0]+1.894844635, L_atoms_right[ny-2-i].position[1], 498.3294560000))
        supercell_L.append(new_atom1)
        new_atom2 = Atom('Se', position=(L_atoms_right[ny-2-i].position[0]+1.894844635, L_atoms_right[ny-2-i].position[1], 501.6705440000))
        supercell_L.append(new_atom2)

#add atoms to right supercell left portion
if (R_atoms_left[ny-1].symbol == 'W'):
        new_atom1 = Atom('Se', position=(R_atoms_left[ny-1].position[0]-1.894844635, R_atoms_left[ny-1].position[1], 498.3294560000))
        supercell_R.append(new_atom1)
        new_atom2 = Atom('Se', position=(R_atoms_left[ny-1].position[0]-1.894844635, R_atoms_left[ny-1].position[1], 501.6705440000))
        supercell_R.append(new_atom2)

for i in range(defect_4[0]-1):
    if (R_atoms_left[0+i].symbol == 'W'):
        new_atom1 = Atom('Se', position=(R_atoms_left[0+i].position[0]-1.894844635, R_atoms_left[0+i].position[1], 498.3294560000))
        supercell_R.append(new_atom1)
        new_atom2 = Atom('Se', position=(R_atoms_left[0+i].position[0]-1.894844635, R_atoms_left[0+i].position[1], 501.6705440000))
        supercell_R.append(new_atom2)
        
#add atoms to right supercell right portion
if (R_atoms_right[ny-1].symbol == 'Se'):
        new_atom1 = Atom('W', position=(R_atoms_right[ny-1].position[0]+1.894844635, R_atoms_right[ny-1].position[1], 500.0000000000))
        supercell_R.append(new_atom1)

for i in range(defect_4[0]-1):
    if (R_atoms_right[0+i].symbol == 'Se'):
        new_atom1 = Atom('W', position=(R_atoms_right[0+i].position[0]+1.894844635, R_atoms_right[0+i].position[1], 500.0000000000))
        supercell_R.append(new_atom1)


#Write the left supercell
write('Left2.xyz', supercell_L)
# Write the right supercell
write('Right2.xyz', supercell_R)

############################################################################################################################
                                #New supercell by merging left and right with new cell boundary
############################################################################################################################

# Define new cell dimensions
x_size = supercell_L.cell.lengths()[0] + supercell_R.cell.lengths()[0] + move_right_cell*2
y_size = supercell_L.cell.lengths()[1]
z_size = supercell_L.cell.lengths()[2]

merged_cell_dimensions = [[x_size, 0, 0], [0, y_size, 0], [0, 0, z_size]]

# Create a new empty Atoms object with the defined cell
merged_cell = Atoms(cell=merged_cell_dimensions, pbc=True)

# Copy atoms from the left supercell
for atom in supercell_L:
    merged_cell.append(atom)

# Copy atoms from the right supercell
for atom in supercell_R:
    merged_cell.append(atom)

# Optionally, adjust the positions or wrap the atoms
merged_cell.wrap()

# Save the merged structure
#write('WSe2_MTB_'+ str(defect_4[0])+ '_'+ str(defect_4[1]) +'.xyz', merged_cell)

#write Lammps data
fName = 'WSe2_MTB_'+ str(defect_4[0])+ '_'+ str(defect_4[1]) +'.lmp'
atom_types = set(atom.symbol for atom in merged_cell)

with open(fName,'w+') as f:

    f.write('%s (written by Nuruzzaman Sakib with the help of ASE)\n'%(fName))
    f.write('%d\tatoms\n'%(len(merged_cell)))
    f.write('%d\tatom types\n'%(len(atom_types)))
    f.write('0.0\t%.9f\txlo xhi\n'%(merged_cell.cell[0,0]))
    f.write('0.0\t%.9f\tylo yhi\n'%(merged_cell.cell[1,1]))
    f.write('0.0\t%.9f\tzlo zhi\n\n'%(merged_cell.cell[2,2]))
    
    f.write('Masses\n\n')
    f.write('%d\t%.9f\t\t# Se\n'%(1,78.96000000))   #mass of Se
    f.write('%d\t%.9f\t\t# W\n'%(2,183.8400000))    #mass of W
    
    f.write('\n')
    f.write('Atoms # charge\n\n')

    for atom in merged_cell:
        atom_type = 1 if atom.symbol == 'Se' else 2 if atom.symbol == 'W' else 0
        f.write('%d\t%d\t%.1f\t%.9f\t%.9f\t%.9f\n'%(atom.index+1,atom_type,0.0,atom.position[0],atom.position[1],atom.position[2]))

