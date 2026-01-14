#created by Nuruzzaman Saki (nsakib@crimson.ua.edu)

import sys
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

if len(sys.argv) != 3:
    print("Syntax: python penta_hepta.py GB_data.txt PNG_File_Name")
    sys.exit()

# Create an undirected graph
G = nx.Graph()

# Add nodes with x, y coordinates
nodes = {}
edges = []

try:
    with open(sys.argv[1], "r") as file:
        # Read the first line as the 'ly' variable
        ly = float(next(file).strip())

        # Process the remaining lines
        for line in file:
            node_data = line.split()
            node = int(node_data[0])
            x = float(node_data[1])
            y = float(node_data[2])
            nodes[node] = (x, y)
            neighbors = list(map(int, node_data[3:]))

            # Add edges
            for target_node in neighbors:
                if (node, target_node) not in edges and (target_node, node) not in edges:
                    edges.append((node, target_node))
except Exception as e:
    print(f"An error occurred: {e}")

#print(f"LY value: {ly}")

G.add_nodes_from(nodes.keys())
G.add_edges_from(edges)

# Perform backtracking to find polygons
polygons = []
visited = set()

def backtrack(node, path, start_node, depth):
    if depth > 4 and node == start_node:
        polygons.append(path)
        return
    elif (depth>7):
        return
            
    visited.add(node)
 
    #print("Visiting node:", node)
    #print("Depth:", depth)
    for neighbor in G.neighbors(node):
        if neighbor not in visited:
            neighbor_distance = np.linalg.norm(np.array(nodes[neighbor]) - np.array(nodes[start_node]))
            if neighbor_distance <= 3.2:
                if depth == 5 and start_node in G.neighbors(node):
                    #print("Current path:", path)
                    backtrack(start_node, path + [start_node], start_node, depth + 1)
                elif depth == 6 and start_node in G.neighbors(node):
                    #print("Current path:", path)
                    backtrack(start_node, path + [start_node], start_node, depth + 1)
                elif depth == 7 and start_node in G.neighbors(node):
                    #print("Current path:", path)
                    backtrack(start_node, path + [start_node], start_node, depth + 1)
                else:
                    #print("Current path:", path)
                    backtrack(neighbor, path + [neighbor], start_node, depth + 1)
    if node in visited:  # Add a check before removing the node from visited
        visited.remove(node)

for node in G.nodes():
    visited.clear()
    #print("Starting from node:", node)
    backtrack(node, [node], node, 1)

def remove_one_duplicate(nodes):
    duplicate_nodes = set()
    for node in nodes:
        if node in duplicate_nodes:
            nodes.remove(node)
            break
        else:
            duplicate_nodes.add(node)

#unique_polygons
def get_unique_polygons(polygons):
    unique_polygons = []
    normalized_polygon = []

    for polygon in polygons:
        if sorted(polygon[:-1]) not in normalized_polygon:
            unique_polygons.append(polygon)
            normalized_polygon.append(sorted(polygon[:-1]))

    return unique_polygons

filtered_polygon = get_unique_polygons(polygons)
filtered_polygons = []
for polygon in filtered_polygon:
    if len(polygon) != 7:
        filtered_polygons.append(polygon)

#print(filtered_polygons)
#print(len(filtered_polygons))

###########################remove polygons outside boundary################################
def count_nodes_above_line(polygon_nodes, nodes, line_y=0):
    """
    Counts the number of nodes in a polygon that are above a specified y-coordinate line.

    :param polygon_nodes: List of node identifiers forming the polygon.
    :param nodes: Dictionary mapping node identifiers to their (x, y) coordinates.
    :param line_y: The y-coordinate of the line. Default is 0.
    :return: The number of nodes above the specified line.
    """
    count_above_line = sum(1 for node in polygon_nodes if nodes[node][1] > line_y)
    return count_above_line

def count_nodes_below_line(polygon_nodes, nodes, line_y=ly):
    """
    Counts the number of nodes in a polygon that are below a specified y-coordinate line.

    :param polygon_nodes: List of node identifiers forming the polygon.
    :param nodes: Dictionary mapping node identifiers to their (x, y) coordinates.
    :param line_y: The y-coordinate of the line. Default is 0.
    :return: The number of nodes below the specified line.
    """
    count_below_line = sum(1 for node in polygon_nodes if nodes[node][1] < line_y)
    return count_below_line

polygon_removed = []
for polygon in filtered_polygons:
    no_above_line = count_nodes_above_line(polygon[:-1],nodes,line_y=0)
    if no_above_line>0:
        polygon_removed.append(polygon)

filtered_polygons = []
for polygon in polygon_removed:
    no_below_line = count_nodes_below_line(polygon[:-1],nodes,line_y=ly)
    if no_below_line>0:
        filtered_polygons.append(polygon)

###########################################################################################

# Visualize the polygons and nodes
coordinates = np.array([nodes[node] for node in G.nodes()])
#print(coordinates)

fig, ax = plt.subplots()
ax.set_aspect('equal')

pentagon_color = 'green'
heptagon_color = 'red'

pentagon_coord = []
heptagon_coord = []

print(len(filtered_polygons))

for polygon in filtered_polygons:

    poly_coords = [nodes[node] for node in polygon]
    patch = Polygon(poly_coords, closed=True, edgecolor='black')

    if len(polygon) == 6:
        patch.set_facecolor(pentagon_color)
        pentagon_coord.append(poly_coords)
    elif len(polygon) == 8:
        patch.set_facecolor(heptagon_color)
        heptagon_coord.append(poly_coords)

    ax.add_patch(patch)

       
# Plot nodes with node numbers
for node, (x, y) in nodes.items():
    plt.scatter(x, y, color='blue',s=5 )
    plt.text(x, y, str(node), color='black', ha='center', va='center',fontsize=4)

output_filename = sys.argv[2]
plt.savefig(output_filename)

#plt.show()
#print(pentagon_coord)
pentagon_coord = [sublist[:][:-1] for sublist in pentagon_coord]
heptagon_coord = [sublist[:][:-1] for sublist in heptagon_coord]
#print(pentagon_coord)

############################################Identify Unique Pentagon Heptagon Pair#############################################

# Calculate the centers of each heptagon
heptagon_centers = []
for heptagon_vertices in heptagon_coord:
    x_sum = 0.0
    y_sum = 0.0

    for vertex in heptagon_vertices:
        x, y = vertex
        x_sum += x
        y_sum += y

    num_vertices = len(heptagon_vertices)
    x_center = x_sum / num_vertices
    y_center = y_sum / num_vertices

    center = (x_center, y_center)
    heptagon_centers.append(center)

# Calculate the centers of each pentagon
pentagon_centers = []
for pentagon_vertices in pentagon_coord:
    x_sum = 0.0
    y_sum = 0.0

    for vertex in pentagon_vertices:
        x, y = vertex
        x_sum += x
        y_sum += y

    num_vertices = len(pentagon_vertices)
    x_center = x_sum / num_vertices
    y_center = y_sum / num_vertices

    center = (x_center, y_center)
    pentagon_centers.append(center)

# Make sure the poly centres are sorted based on y coordinate
sorted_pentagon_centers = sorted(pentagon_centers, key=lambda c: (c[1]))   # Sort pentagon centers
sorted_heptagon_centers = sorted(heptagon_centers, key=lambda c: (c[1]))   # Sort heptagon centers

# Function to check if a polygon has a pair within a specified distance
def find_extra_polygon(sorted_heptagon_centers, sorted_pentagon_centers):
    extra_polygon = None
    extra_polygon_type = None
    
    #print(len(sorted_pentagon_centers),'\n')
    #print(len(sorted_heptagon_centers),'\n')

    # Check if pentagons are extra
    if len(sorted_pentagon_centers) > len(sorted_heptagon_centers):       
        extra_polygon_type = '5'
        extra_polygon_centers = sorted_pentagon_centers
        other_polygon_centers = sorted_heptagon_centers
    elif len(sorted_pentagon_centers) < len(sorted_heptagon_centers):        
        extra_polygon_type = '7'
        extra_polygon_centers = sorted_heptagon_centers
        other_polygon_centers = sorted_pentagon_centers
    else:
        return extra_polygon, extra_polygon_type

    # Check if the first or last extra polygons don't have a pair within the specified distance
    combined_distances_f2l = 0

    #print(extra_polygon_type)    
    # Calculate the distance between the corresponding points in the two lists
    for i in range(len(other_polygon_centers)):
        e_center = extra_polygon_centers[i]
        o_center = other_polygon_centers[i]
        distance = abs(e_center[1] - o_center[1])
        #print('f2l',distance,'\n')
        if distance>3.8:
            combined_distances_f2l += 10
        else:
            combined_distances_f2l += distance
    #print(combined_distances_f2l)
    
    combined_distances_l2f = 0
    for i in range(len(other_polygon_centers)-1,-1,-1):
        e_center = extra_polygon_centers[i+1]
        o_center = other_polygon_centers[i]
        distance = abs(e_center[1] - o_center[1])
        #print('l2f',distance,'\n')
        if distance>3.8:
            combined_distances_l2f += 10
        else:
            combined_distances_l2f += distance
    
    #print(combined_distances_l2f)

    if combined_distances_f2l>combined_distances_l2f:
        extra_polygon = extra_polygon_centers[0]
        
    elif combined_distances_f2l<combined_distances_l2f:
        extra_polygon = extra_polygon_centers[-1]
    
    else:
        print("Need Your Attention!")
        
    return extra_polygon, extra_polygon_type

# Find the extra polygon and its type
extra_polygon, extra_polygon_type = find_extra_polygon(sorted_heptagon_centers, sorted_pentagon_centers)
if (extra_polygon == None) and (sorted_heptagon_centers[0][1] < 0 or sorted_pentagon_centers[0][1]<0):   #to avoid deleting polygon which is inside the unitcell

    if (sorted_heptagon_centers[0][1]<sorted_pentagon_centers[0][1]):
        sorted_heptagon_centers = sorted_heptagon_centers[1:]
    else:
        sorted_pentagon_centers = sorted_pentagon_centers[1:]

    extra_polygon, extra_polygon_type = find_extra_polygon(sorted_heptagon_centers, sorted_pentagon_centers)
 
# Separate the pentagon and heptagon coordinates (excluding the extra polygon)
pentagon_unique_coord = []
heptagon_unique_coord = []

for pentagon_center in sorted_pentagon_centers:
    if pentagon_center != extra_polygon:
        pentagon_unique_coord.append(pentagon_coord[pentagon_centers.index(pentagon_center)])

for heptagon_center in sorted_heptagon_centers:
    if heptagon_center != extra_polygon:
        heptagon_unique_coord.append(heptagon_coord[heptagon_centers.index(heptagon_center)])

#print(pentagon_coord)        
with open("penta_data_unique.txt", "w") as file:
    for i in range(len(pentagon_unique_coord)):
        file.write(f"{' '.join(f'{x} {y}' for x, y in pentagon_unique_coord[i])}\n")

#print(heptagon_coord)
with open("hepta_data_unique.txt", "w") as file:
    for i in range(len(heptagon_unique_coord)):
        file.write(f"{' '.join(f'{x} {y}' for x, y in heptagon_unique_coord[i])}\n")
        
print("Number of pentagons:", len(pentagon_unique_coord))
print("Number of heptagons:", len(heptagon_unique_coord))


