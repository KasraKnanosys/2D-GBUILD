# Created by Nuruzzaman Sakib (nsakib@crimson.ua.edu)

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
with open(sys.argv[1], "r") as file:
    for line in file:
        node_data = line.split()
        node = int(node_data[0])
        x = float(node_data[1])
        y = float(node_data[2])
        nodes[node] = (x, y)
        neighbors = list(map(int, node_data[3:]))

        # Add edges
        for target_node in neighbors:
            # Check if the edge or its reverse already exists
            if (node, target_node) not in edges and (target_node, node) not in edges:
                edge = (node, target_node)
                edges.append(edge)

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
                if (depth == 5 or depth == 6 or depth == 7) and start_node in G.neighbors(node):                   
                    #print("Current path:", path)
                    backtrack(start_node, path + [start_node], start_node, depth + 1)
                else:
                    #print("Current path:", path)
                    backtrack(neighbor, path + [neighbor], start_node, depth + 1)
        
        elif neighbor==start_node and (depth == 5 or depth == 7):
            backtrack(start_node, path + [start_node], start_node, depth + 1)            

    if node in visited:  # Add a check before removing the node from visited
        visited.remove(node)

for node in G.nodes():
    visited.clear()
    backtrack(node, [node], node, 1)

#unique_polygons
def get_unique_polygons(polygons):
    unique_polygons = []
    normalized_polygon = []

    for polygon in polygons:
        if sorted(polygon[:-1]) not in normalized_polygon:
            unique_polygons.append(polygon)
            normalized_polygon.append(sorted(polygon[:-1]))

    return unique_polygons

filtered_polygons = get_unique_polygons(polygons)
#print(filtered_polygons)
#print(len(filtered_polygons))

# Visualize the polygons and nodes
coordinates = np.array([nodes[node] for node in G.nodes()])
#print(coordinates)

fig, ax = plt.subplots()
ax.set_aspect('equal')

pentagon_color = 'green'
hexagon_color = 'blue'
heptagon_color = 'red'

pentagon_coord = []
heptagon_coord = []

for polygon in filtered_polygons:

    poly_coords = [nodes[node] for node in polygon]
    patch = Polygon(poly_coords, closed=True, edgecolor='black',linewidth=0.05)

    if len(polygon) == 6:
        patch.set_facecolor(pentagon_color)
        pentagon_coord.append(poly_coords)
    elif len(polygon) == 7:
        patch.set_facecolor(hexagon_color)
    elif len(polygon) == 8:
        patch.set_facecolor(heptagon_color)
        heptagon_coord.append(poly_coords)

    ax.add_patch(patch)

print("No of Pentagon:",len(pentagon_coord))
print("No of Heptagon:",len(heptagon_coord))       

# Plot nodes with node numbers
for _, (x, y) in nodes.items():
    plt.scatter(x, y, color='blue',s=.1, edgecolors='none' )

output_filename = sys.argv[2]
plt.savefig(output_filename, dpi = 600)

#plt.show()

# Save pentagon and heptagon coordinates to text files
with open("pentagon_coordinates.txt", "w") as pentagon_file:
    for coord in pentagon_coord:
        pentagon_file.write(' '.join(map(str, [item for sublist in coord for item in sublist])) + '\n')

with open("heptagon_coordinates.txt", "w") as heptagon_file:
    for coord in heptagon_coord:
        heptagon_file.write(' '.join(map(str, [item for sublist in coord for item in sublist])) + '\n')



