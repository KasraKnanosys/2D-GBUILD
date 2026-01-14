# Created by Nuruzzaman Sakib (nsakib@crimson.ua.edu)

import math

with open('min.lmp','r') as fdata:
    lines = fdata.readlines()
    dim_xlo = float(lines[5].split()[0])
    dim_xhi = float(lines[5].split()[1])
    dim_ylo = float(lines[6].split()[0])
    dim_yhi = float(lines[6].split()[1])
    dim_z = float(lines[7].split()[1])

# Now, node_dict is a dictionary where:
# the key is the node number
# the value is another dictionary with keys "position_x", "position_y", and "neighbors"
node_dict = {}
with open("atom_data_GB.txt", "r") as file:
    for line in file:
        # Split the line into columns
        columns = line.strip().split()

        # Convert first three columns to appropriate data types
        node_no = int(columns[0])
        position_x = float(columns[1])
        position_y = float(columns[2])

        # Create a list for neighbors
        neighbors = [int(neighbor) for neighbor in columns[3:]]

        # Create a sub-dictionary for the node
        node_info = {"position_x": position_x, "position_y": position_y, "neighbors": neighbors}

        # Add the node information to the main dictionary
        node_dict[node_no] = node_info

#print(node_dict[2516]["neighbors"][0])

# Now, 'all_distances' is a dictionary where:
# the key is a node number
# the value is another dictionary where:
# the key is a neighbor's node number
# the value is the distance from the node to that neighbor

# Initialize an empty dictionary to hold all the distances

def atom_that_cross_boundary():
    all_distances = {}

    # Go through each node in the dictionary
    for node_number, node_info in node_dict.items():
        # Get the coordinates for this node
        node_x = node_info["position_x"]
        node_y = node_info["position_y"]

        # Then, get the neighbors
        neighbors = node_info["neighbors"]

        # Initialize an empty dictionary to hold the distances for this node
        distances = {}

        # Go through the neighbors one by one
        for neighbor in neighbors:
            # Get the coordinates for the neighbor
            neighbor_info = node_dict[neighbor]
            neighbor_x = neighbor_info["position_x"]
            neighbor_y = neighbor_info["position_y"]

            # Calculate the distance
            distance = math.sqrt((neighbor_x - node_x)**2 + (neighbor_y - node_y)**2)

            # Store the distance in the dictionary
            distances[neighbor] = distance

        # Store the distances for this node in the main dictionary
        all_distances[node_number] = distances

    #print(all_distances)

    # Define the cutoff
    cutoff = 1.85
    atom_list_cross_boundary = []
    # Go through each node and its distances
    for node_number, distances in all_distances.items():
        # Go through each neighbor and its distance
        for neighbor, distance in distances.items():
            # If the distance is greater than the cutoff
            if distance > cutoff:
                # Print the node number and its neighbor
                #print(f"Node {node_number} and neighbor {neighbor} have a distance of {distance}, which is greater than the cutoff.")
                if node_number not in atom_list_cross_boundary:
                    atom_list_cross_boundary.append(node_number)
                if neighbor not in atom_list_cross_boundary:
                    atom_list_cross_boundary.append(neighbor)
    #print(atom_list_cross_boundary)    
    return atom_list_cross_boundary

# find the chain of atoms that are connected together

def euclidean_distance(node):
    """Compute the Euclidean distance from the start node."""
    x1, y1 = node_dict[start_node]['position_x'], node_dict[start_node]['position_y']
    x2, y2 = node_dict[node]['position_x'], node_dict[node]['position_y']
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def find_path_and_sort(node, visited=None, distances=None):
    if visited is None:
        visited = set()  # keep track of visited nodes
        distances = {}  # keep track of distances from the start node
        distances[node] = 0  # distance from the start node to itself is 0

    visited.add(node)  # mark the current node as visited
    neighbors = set(node_dict[node]['neighbors'])

    for neighbor in neighbors - visited:
        distances[neighbor] = euclidean_distance(neighbor)
        find_path_and_sort(neighbor, visited, distances)

    return visited, distances

def calculate_avg_and_limits(nodes_group):
    
    max_x = max_y = float('-inf')  # Initialize to negative infinity
    min_x = min_y = float('inf')  # Initialize to positive infinity

    for node in nodes_group:
        pos_x, pos_y = node_dict[node]['position_x'], node_dict[node]['position_y']

        max_x = max(max_x, pos_x)
        min_x = min(min_x, pos_x)
        max_y = max(max_y, pos_y)
        min_y = min(min_y, pos_y)
    
    
    x_diff, sign_x = (abs(dim_xlo - min_x), min_x) if abs(dim_xlo - min_x) < abs(dim_xhi - max_x) else (abs(dim_xhi - max_x), max_x)
    y_diff, sign_y = (abs(dim_ylo - min_y), min_y) if abs(dim_ylo - min_y) < abs(dim_yhi - max_y) else (abs(dim_yhi - max_y), max_y)
    
    #print (x_diff,y_diff)

    if x_diff<y_diff:
        if sign_x<0:
            return "x", -1
        else:
            return "x", 1
        
    else:
        if sign_y<0:
            return "y", -1
        else:
            return "y", 1
    
    
    #print("You need to check x or y axis nearest finder")
    return "e", 0

# example usage:
atom_list_cross_boundary = atom_that_cross_boundary()
while len(atom_list_cross_boundary)>=1:
    start_node = atom_list_cross_boundary[0]  # start node
    #print(start_node)
    path, distances = find_path_and_sort(start_node)
    
    # sort nodes by distance
    sorted_nodes = sorted(path, key=distances.get)
    #print(sorted_nodes)

    #Get the distances in sorted order
    sorted_distances = [distances[node] for node in sorted_nodes]

    # Calculate slopes between successive points
    slopes = [(y2 - y1) for y1, y2 in zip(sorted_distances[:-1], sorted_distances[1:])]

    # Threshold for detecting an abrupt change
    threshold = 10  # Change this value based on your specific criteria

    # Print slopes
    #for i, slope in enumerate(slopes):
    #    print(f"{sorted_nodes[i]} {sorted_nodes[i+1]}: {slope}")

    # Detect abrupt changes in slopes
    slope_change = False
    for i, slope in enumerate(slopes[:-1]):
        if abs(slopes[i+1] - slope) > threshold:
            if slope_change == False:
                slope_change = True
                j=i
                continue

            if slope_change == True:
                node_set_1 = sorted_nodes[0:i+1]
                node_set_2 = sorted_nodes[i+1:]
                slope_change = False
                break
   
    if slope_change == True:
        node_set_1 = sorted_nodes[0:i+2]
        node_set_2 = sorted_nodes[i+2:]

    #print(node_set_1)
    #print(node_set_2)
      
    
    if len(node_set_1)<len(node_set_2):
        axis, sign = calculate_avg_and_limits(node_set_1)
        
        for node_no in node_set_1:
            #print(node_no)
            if axis =='x':
                node_dict[node_no]["position_x"] = node_dict[node_no]["position_x"] + (sign)*(dim_xlo - dim_xhi)
            elif axis =='y':
                node_dict[node_no]["position_y"] = node_dict[node_no]["position_y"] + (sign)*(dim_ylo - dim_yhi)
        
    else:
        axis, sign = calculate_avg_and_limits(node_set_2)
        #print(node_no)
        for node_no in node_set_2:
            #print(node_no)
            if axis =='x':
                node_dict[node_no]["position_x"] = node_dict[node_no]["position_x"] + (sign)*(dim_xlo - dim_xhi)
            elif axis =='y':
                node_dict[node_no]["position_y"] = node_dict[node_no]["position_y"] + (sign)*(dim_ylo - dim_yhi)
        
    atom_list_cross_boundary = atom_that_cross_boundary()

    node_set_1=[]
    node_set_2=[]


# Print the extracted pos elements
n_atom = len(node_dict)

with open('data_shifted.lmp','w') as fdata:
    fdata.write('# LAMMPS data file written by python_NSAKIB\n')
    fdata.write('{} {}\n'.format(n_atom,'atoms'))
    fdata.write('1 atom types\n')
    fdata.write('{} {} {}\n'.format(dim_xlo,dim_xhi,'xlo xhi'))
    fdata.write('{} {} {}\n'.format(dim_ylo,dim_yhi,'ylo yhi'))
    fdata.write('{} {} {}\n'.format('0.0',dim_z,'zlo zhi'))
    fdata.write('\n')
    fdata.write('Mass\n')
    fdata.write('\n')
    fdata.write('1  12.0 # C\n')
    fdata.write('\n')
    fdata.write('Atoms  # atomic\n')
    fdata.write('\n')
        
    for node_number, node_info in node_dict.items():
        fdata.write('{}\t{}\t{}\t{}\t{}\n'.format(node_number,'1',node_info["position_x"],node_info["position_y"],'5'))
    
    fdata.close()

#edit the atom_GB_data file
with open("atom_data_GB.txt", "w") as file:
    # Iterate over the items in the dictionary
    for node_no, node_info in node_dict.items():
        # Extract the information for each node
        position_x = node_info["position_x"]
        position_y = node_info["position_y"]
        neighbors = node_info["neighbors"]

        # Create a line to write to the file
        # Convert the neighbors to a space-separated string
        neighbors_str = " ".join(str(neighbor) for neighbor in neighbors)
        line = f"{node_no} {position_x} {position_y} {neighbors_str}\n"

        # Write the line to the file
        file.write(line)

