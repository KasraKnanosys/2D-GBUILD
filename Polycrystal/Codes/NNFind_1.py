# Created by Nuruzzaman Sakib (nsakib@crimson.ua.edu)

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
				
                if round(current_x,4) == round(x,4) and round(current_y,4) == round(y,4):
                    atom_id = current_atom_id
                    break
        
    if atom_id is None:
        print(x,y,"Atom not found.")
    
    return atom_id

lammps_input_file = "min.lmp"
atom_id_shared_edge = []

coordinates_list = []

with open('coordinates_edges_two_hex++.txt', 'r') as file:
    for line in file.readlines():
        # Splitting the line by whitespaces and then creating tuples for every pair of numbers
        numbers = [float(num) for num in line.split()]
        coordinates_list.append((numbers[0], numbers[1]))

for i in range(len(coordinates_list)):
    pos_x = coordinates_list[i][0]
    pos_y = coordinates_list[i][1]
    atom_id_shared_edge.append(find_atom_id(lammps_input_file, pos_x, pos_y))

with open('same_atom_two_hexa.txt', 'w') as file:
    for i in range(0,len(atom_id_shared_edge),2):
        file.write(f"{atom_id_shared_edge[i]}\t\t{atom_id_shared_edge[i+1]}\n")


