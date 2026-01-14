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

def modify_lammps_data(filename, atom_ids_to_change, new_atom_type):
    with open(filename, 'r') as file:
        lines = file.readlines()

    in_atoms_section = False
    modified_lines = []

    for line in lines:
        stripped_line = line.strip()
        
        if stripped_line.startswith("Atoms"):
            in_atoms_section = True
            modified_lines.append(line)
            continue
        elif stripped_line in ["Bonds", "Angles", "Dihedrals", "Impropers", "Velocities"]:
            in_atoms_section = False

        if in_atoms_section and len(stripped_line) > 0 and not stripped_line.startswith("#"):
            parts = line.split()
            try:
                atom_id = int(parts[0])
                if atom_id in atom_ids_to_change:
                    parts[1] = str(new_atom_type)
                    modified_line = ' '.join(parts) + '\n'
                    modified_lines.append(modified_line)
                else:
                    modified_lines.append(line)
            except ValueError:
                modified_lines.append(line)
        else:
            modified_lines.append(line)

    return ''.join(modified_lines)


lammps_input_file = "min.lmp"
atom_id_shared_edge = []

coordinates_list = []

with open('coordinates_shared_edge.txt', 'r') as file:
    for line in file.readlines():
        # Splitting the line by whitespaces and then creating tuples for every pair of numbers
        numbers = [float(num) for num in line.split()]
        coordinates_list.append((numbers[0], numbers[1]))


for i in range(len(coordinates_list)):
    pos_x = coordinates_list[i][0]
    pos_y = coordinates_list[i][1]
    atom_id_shared_edge.append(find_atom_id(lammps_input_file, pos_x, pos_y))

modified_content = modify_lammps_data('min.lmp', atom_id_shared_edge, 2)
with open('modified_data_file.lmp', 'w') as file:
    file.write(modified_content)

with open('same_atom_all.txt', 'w') as file:
    for i in range(0,len(atom_id_shared_edge),2):
        file.write(f"{atom_id_shared_edge[i]}\t\t{atom_id_shared_edge[i+1]}\n")
