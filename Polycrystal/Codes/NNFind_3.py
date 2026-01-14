# Created by Nuruzzaman Sakib (nsakib@crimson.ua.edu)

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

# Create an undirected graph
G = nx.Graph()

# Add nodes with x, y coordinates
nodes = {}
edges = []
with open("atom_data_two_hexa++.txt", "r") as file:
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

# Visualize the polygons and nodes
coordinates = np.array([nodes[node] for node in G.nodes()])
#print(coordinates)

fig, ax = plt.subplots()
ax.set_aspect('equal')

pentagon_color = 'green'
hexagon_color = 'blue'
heptagon_color = 'red'

hexagon_coord = []

for polygon in filtered_polygons:

    poly_coords = [nodes[node] for node in polygon]
    patch = Polygon(poly_coords, closed=True, edgecolor='black',linewidth=0.05)

    if len(polygon) == 6:
        patch.set_facecolor(pentagon_color)
    elif len(polygon) == 7:
        patch.set_facecolor(hexagon_color)
        hexagon_coord.append(poly_coords)
    elif len(polygon) == 8:
        patch.set_facecolor(heptagon_color)
        
    ax.add_patch(patch)

for _, (x, y) in nodes.items():
    plt.scatter(x, y, color='blue',s=.1, edgecolors='none' )

#plt.show()

#read the edges
edges = []

with open('coordinates_edges_two_hex++.txt', 'r') as file:
    lines = file.readlines()
    for i in range(0, len(lines)-1, 2):  # Step by 2 to get pairs of lines
        x1, y1 = map(float, lines[i].split())
        x2, y2 = map(float, lines[i+1].split())
        edge = ((x1, y1), (x2, y2))
        edges.append(edge)

def rounded(edge, PRECISION=6):
    """Return edge with coordinates rounded to the specified precision."""
    return tuple(sorted(((round(p[0], PRECISION), round(p[1], PRECISION)) for p in edge)))

def hexagon_edges(hexagon):
    """Generate edges from a hexagon's coordinates."""
    return [rounded((hexagon[i], hexagon[i+1])) for i in range(len(hexagon)-1)]

def hexagons_with_shared_edges(hexagons, edges):
    """Return hexagons that share at least one edge with the given edges."""
    edges = [rounded(edge) for edge in edges]
    shared_edge_hexagons = []
    
    for hexagon in hexagons:
        for edge in hexagon_edges(hexagon):
            if edge in edges:
                shared_edge_hexagons.append(hexagon)
                break  # No need to check further for this hexagon
    return shared_edge_hexagons

hexagons_with_edges_penta_hepta = hexagons_with_shared_edges(hexagon_coord, edges)

# Identifying hexagons with shared edges
def share_edge(polygon1, polygon2):
    for i in range(len(polygon1)):
        edge1 = {polygon1[i], polygon1[(i + 1) % len(polygon1)]}
        for j in range(len(polygon2)):
            edge2 = {polygon2[j], polygon2[(j + 1) % len(polygon2)]}
            if edge1 == edge2:
                return edge1
    return None

shared_edges = []

for i in range(len(hexagons_with_edges_penta_hepta)-1):
    for j in range(i+1,len(hexagons_with_edges_penta_hepta)):

        edge = share_edge(hexagons_with_edges_penta_hepta[i],hexagons_with_edges_penta_hepta[j])
        if edge:
            shared_edges.append(list(edge))
            break

def write_polygon_coord(polygon):
    for edge in polygon:
        for coord in edge:
            file.write("{}\t{}\n".format(coord[0],coord[1]))

with open('coordinates_shared_edge.txt', 'a') as file:
    write_polygon_coord(shared_edges)

