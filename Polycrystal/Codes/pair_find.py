# Created by Nuruzzaman Sakib (nsakib@crimson.ua.edu)

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from scipy.optimize import linear_sum_assignment
import numpy as np
import sys
import math

if len(sys.argv) != 2:
    print("Syntax: python pair_find.py dimension")
    sys.exit()

# Reading the pentagon and heptagon coordinates from the text files
with open("pentagon_coordinates.txt", "r") as file:
    pentagon_coordinates = []
    for line in file.readlines():
        values = list(map(float, line.strip().split()))
        coordinates = [(values[i], values[i+1]) for i in range(0, len(values), 2)]
        pentagon_coordinates.append(coordinates)

with open("heptagon_coordinates.txt", "r") as file:
    heptagon_coordinates = []
    for line in file.readlines():
        values = list(map(float, line.strip().split()))
        coordinates = [(values[i], values[i+1]) for i in range(0, len(values), 2)]
        heptagon_coordinates.append(coordinates)


# Helper functions
def calculate_center(polygon):
    x_coords = [x for x, y in polygon[:-1]]
    y_coords = [y for x, y in polygon[:-1]]
    return sum(x_coords) / len(x_coords), sum(y_coords) / len(y_coords)

def get_periodic_images(point, box_size_x, box_size_y):
    x, y = point
    images = [(x, y)]
    for i in range(-1, 2):
        for j in range(-1, 2):
            images.append((x + i * box_size_x, y + j * box_size_y))
    return images

def distance(point1, point2):
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

def min_distance_to_periodic_images(pentagon_center, heptagon_center, box_size_x, box_size_y):
    heptagon_images = get_periodic_images(heptagon_center, box_size_x, box_size_y)
    return min(distance(pentagon_center, image) for image in heptagon_images)

box_size_x = float(sys.argv[1])
box_size_y = float(sys.argv[1])

# Pairing pentagons with heptagons
pentagon_centers = [calculate_center(pentagon) for pentagon in pentagon_coordinates]
heptagon_centers = [calculate_center(heptagon) for heptagon in heptagon_coordinates]

cost_matrix = [[min_distance_to_periodic_images(pentagon_center, heptagon_center, box_size_x, box_size_y) 
                for heptagon_center in heptagon_centers] 
               for pentagon_center in pentagon_centers]

pentagon_indices, heptagon_indices = linear_sum_assignment(cost_matrix)
paired_pentagon_heptagon = list(zip(pentagon_indices, heptagon_indices))

# Identifying pairs with shared edges
def share_edge(polygon1, polygon2):
    for i in range(len(polygon1)):
        edge1 = {polygon1[i], polygon1[(i + 1) % len(polygon1)]}
        for j in range(len(polygon2)):
            edge2 = {polygon2[j], polygon2[(j + 1) % len(polygon2)]}
            if edge1 == edge2:
                return edge1
    return None

shared_edges = []
no_shared_edge_pairs = []

for pentagon_idx, heptagon_idx in paired_pentagon_heptagon:
    edge = share_edge(pentagon_coordinates[pentagon_idx], heptagon_coordinates[heptagon_idx])
    if edge:
        shared_edges.append((pentagon_idx, heptagon_idx, edge))
    else:
        no_shared_edge_pairs.append((pentagon_idx, heptagon_idx))


# Helper Functions
def is_point_between_points(point, point1, point2, tolerance=1e-10):
    x, y = point
    min_x_axis, max_x_axis = sorted([point1[0], point2[0]])
    min_y_axis, max_y_axis = sorted([point1[1], point2[1]])

    return min_x_axis <= x <= max_x_axis or min_y_axis <= y <= max_y_axis

def segment_intersection(segment1, segment2):
    """Check if two line segments intersect and return the intersection point if they do."""
    xdiff = (segment1[0][0] - segment1[1][0], segment2[0][0] - segment2[1][0])
    ydiff = (segment1[0][1] - segment1[1][1], segment2[0][1] - segment2[1][1])
    
    def determinant(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = determinant(xdiff, ydiff)
    if div == 0:
        return None  # Lines don't intersect

    d = (determinant(*segment1), determinant(*segment2))
    x = determinant(d, xdiff) / div
    y = determinant(d, ydiff) / div
    if (min(segment1[0][0], segment1[1][0]) <= x <= max(segment1[0][0], segment1[1][0]) and
        min(segment1[0][1], segment1[1][1]) <= y <= max(segment1[0][1], segment1[1][1]) and
        min(segment2[0][0], segment2[1][0]) <= x <= max(segment2[0][0], segment2[1][0]) and
        min(segment2[0][1], segment2[1][1]) <= y <= max(segment2[0][1], segment2[1][1])):
        return x, y
    return None

def classify_direction(edge, line_segment):
    #print(edge, line_segment)  
    edge_start, edge_end = edge
    line_start, line_end = line_segment
    
    # Calculate slope of the center segment
    if line_end[0] - line_start[0] == 0:  # Vertical line
        orientation = "vertical"
    else:
        slope = (line_end[1] - line_start[1]) / (line_end[0] - line_start[0])
        angle = math.degrees(math.atan(slope))
        if -60 <= angle <= 60:
            orientation = "horizontal"
        else:
            orientation = "vertical"
    
    #ensure the line direction is same for every pair   
    if orientation == "horizontal":
        if line_start[0]<line_end[0]:
            tmp = line_start
            line_start = line_end
            line_end = tmp
    elif orientation == "vertical":
        if line_start[1]<line_end[1]:
            tmp = line_start
            line_start = line_end
            line_end = tmp

    intersection = segment_intersection(edge, line_segment)
    
    if intersection:
        length_first = ((intersection[0] - edge_start[0])**2 + (intersection[1] - edge_start[1])**2)**0.5
        length_second = ((edge_end[0] - intersection[0])**2 + (edge_end[1] - intersection[1])**2)**0.5
        
        # Determine which side has the longer segment
        if length_first > length_second:
            longer_segment_point = edge_start
        else:
            longer_segment_point = edge_end
        
        # Cross product to determine direction of the longer segment
        
        if orientation == "horizontal":
            if (longer_segment_point[1]-intersection[1]) > 0:
                return "Up"
            else:
                return "Down"
        else:
            if (longer_segment_point[0]-intersection[0]) > 0:
                return "Right"
            else:
                return "Left"
    else:
        # Use the midpoint of the edge to determine its position relative to the center segment
        midpoint = ((edge_start[0] + edge_end[0]) / 2, (edge_start[1] + edge_end[1]) / 2)
        
        cross_product_sign = (line_end[0] - line_start[0]) * (midpoint[1] - line_start[1]) - (line_end[1] - line_start[1]) * (midpoint[0] - line_start[0])
        
        if orientation == "horizontal":
            if cross_product_sign > 0:
                return "Down"
            else:
                return "Up"
        else:
            if cross_product_sign > 0:
                return "Right"
            else:
                return "Left"

def distance_from_point_to_line(point, line):
    x0, y0 = point
    x1, y1 = line[0]
    x2, y2 = line[1]
    numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    denominator = ((y2 - y1)**2 + (x2 - x1)**2)**0.5
    return numerator / denominator

def find_edges_for_polygon(pentagon, heptagon, center_segment, threshold_distance=0.45):
    # Find vertices that are close to the center segment
    pentagon_vertices_near_segment = [vertex for vertex in pentagon if distance_from_point_to_line(vertex, center_segment) < threshold_distance and is_point_between_points(vertex, center_segment[0], center_segment[1])]
    heptagon_vertices_near_segment = [vertex for vertex in heptagon if distance_from_point_to_line(vertex, center_segment) < threshold_distance and is_point_between_points(vertex, center_segment[0], center_segment[1])]
    
    hepta_edges = []
    # If vertices are found near the segment
    if pentagon_vertices_near_segment and heptagon_vertices_near_segment:

        for vertex in pentagon_vertices_near_segment:
            for i in range(len(pentagon)):
                if pentagon[i] == vertex:
                    penta_edges = (pentagon[i], pentagon[(i + 1) % len(pentagon)])
        
        dir_penta = classify_direction(penta_edges, center_segment)
        #print(dir_penta)

        for vertex in heptagon_vertices_near_segment:
            for i in range(len(heptagon)):
                if heptagon[i] == vertex:
                    hepta_edges.append((heptagon[i], heptagon[(i + 1) % len(heptagon)]))
                    hepta_edges.append((heptagon[(i - 1) % len(heptagon)], heptagon[i]))
                    #print(hepta_edges)          
        
        dir_hepta = [classify_direction(edge, center_segment) for edge in hepta_edges]
        #print(dir_hepta)
        for i, direction in enumerate(dir_hepta):
            if direction == dir_penta:
                return penta_edges, hepta_edges[i]
        
    else:
        # If no vertex is near the segment, find the edge that intersects the segment
        for i in range(len(pentagon)):
            edge = (pentagon[i], pentagon[(i + 1) % len(pentagon)])
            if segment_intersection(edge, center_segment):
                penta_edges = edge
        for i in range(len(heptagon)):
            edge = (heptagon[i], heptagon[(i + 1) % len(heptagon)])
            if segment_intersection(edge, center_segment):
                hepta_edges = edge
            
        return penta_edges, hepta_edges
            
    return []

def relocate_polygon(polygon, reference_point, box_size=float(sys.argv[1])):
    """Relocate the polygon closer to a reference point based on periodic boundary conditions."""
    half_box = box_size / 2
    dx, dy = 0, 0
    
    # Calculate the shifts for x and y directions
    if abs(polygon[0][0] - reference_point[0]) > half_box:
        dx = box_size if polygon[0][0] < reference_point[0] else -box_size
    if abs(polygon[0][1] - reference_point[1]) > half_box:
        dy = box_size if polygon[0][1] < reference_point[1] else -box_size
        
    # Apply the shifts to all vertices of the polygon
    relocated_polygon = [(vertex[0] + dx, vertex[1] + dy) for vertex in polygon]
    
    return relocated_polygon

# Adjust the process for finding edge pairs with the refined relocation
edge_pairs_between_centers = []

for pentagon_idx, heptagon_idx in no_shared_edge_pairs:
    center_pentagon = calculate_center(pentagon_coordinates[pentagon_idx])
    center_heptagon = calculate_center(heptagon_coordinates[heptagon_idx])
    
    # Check the distance between the centers
    distance = np.linalg.norm(np.array(center_pentagon) - np.array(center_heptagon))
    
    # If the distance is greater than 20 units, relocate the heptagon
    if distance > 150:
        relocated_heptagon = relocate_polygon(heptagon_coordinates[heptagon_idx], center_pentagon)
        center_segment = (center_pentagon, calculate_center(relocated_heptagon))
        pentagon_edges, heptagon_edges = find_edges_for_polygon(pentagon_coordinates[pentagon_idx][:-1], relocated_heptagon[:-1], center_segment)
    else:
        center_segment = (center_pentagon, center_heptagon)
        pentagon_edges, heptagon_edges = find_edges_for_polygon(pentagon_coordinates[pentagon_idx][:-1], heptagon_coordinates[heptagon_idx][:-1], center_segment)
        
    # Append the results
    edge_pairs_between_centers.append((pentagon_idx, heptagon_idx, pentagon_edges, heptagon_edges))

# Visualizing the results with all center-connecting lines
fig, ax = plt.subplots(figsize=(10, 10))
colors = ['red', 'green']

# Plot pairs with shared edges and highlight the shared edge
for pentagon_idx, heptagon_idx, edge in shared_edges:
    pentagon = Polygon(pentagon_coordinates[pentagon_idx], closed=True, edgecolor='black', linewidth=0.05, facecolor=colors[0])
    heptagon = Polygon(heptagon_coordinates[heptagon_idx], closed=True, edgecolor='black', linewidth=0.05, facecolor=colors[1])
    ax.add_patch(pentagon)
    ax.add_patch(heptagon)
    edge_x = [coord[0] for coord in edge]
    edge_y = [coord[1] for coord in edge]
    plt.plot(edge_x, edge_y, color='yellow', linewidth=0.8)

# Looping through all pairs to visualize them
for pentagon_idx, heptagon_idx, pentagon_edges, heptagon_edges in edge_pairs_between_centers:
    # Plotting pentagon
    pentagon_patch = Polygon(pentagon_coordinates[pentagon_idx], closed=True, edgecolor='black', linewidth=0.05, facecolor='orange')
    ax.add_patch(pentagon_patch)

    # Plotting heptagon (relocated if necessary)
    center_pentagon = calculate_center(pentagon_coordinates[pentagon_idx])
    center_heptagon = calculate_center(heptagon_coordinates[heptagon_idx])
    distance = np.linalg.norm(np.array(center_pentagon) - np.array(center_heptagon))
    if distance > 150:
        relocated_heptagon = relocate_polygon(heptagon_coordinates[heptagon_idx], center_pentagon)
        heptagon_patch = Polygon(relocated_heptagon, closed=True, edgecolor='black', linewidth=0.05, facecolor='blue')
    else:
        heptagon_patch = Polygon(heptagon_coordinates[heptagon_idx], closed=True, edgecolor='black', linewidth=0.05, facecolor='orange')
    ax.add_patch(heptagon_patch)

    # Highlighting edges
    edge_x = [coord[0] for coord in pentagon_edges]
    edge_y = [coord[1] for coord in pentagon_edges]
    plt.plot(edge_x, edge_y, color='cyan', linewidth=0.8)


    edge_x = [coord[0] for coord in heptagon_edges]
    edge_y = [coord[1] for coord in heptagon_edges]
    plt.plot(edge_x, edge_y, color='cyan', linewidth=0.8)

    # Plotting center segment for each pair
    if distance > 150:
        center_segment = (center_pentagon, calculate_center(relocated_heptagon))
    else:
        center_segment = (center_pentagon, center_heptagon)
    center_segment_x = [center_segment[0][0], center_segment[1][0]]
    center_segment_y = [center_segment[0][1], center_segment[1][1]]
    plt.plot(center_segment_x, center_segment_y, color='red', linestyle='--', linewidth=0.5)

plt.gca().set_aspect('equal', adjustable='box')
plt.savefig("Penta_Hepta_Pair.png",dpi=600)

# Write the coordinates of pairs with shared edges
def write_polygon_coord(polygon):
    for coord in polygon:
        file.write("{}\t{}\n".format(coord[0],coord[1]))

def wrap_coordinates(point, limit=float(sys.argv[1])/2):

    x, y = point
    
    # Adjusting for the range [-limit, limit]
    wrapped_x = (x + limit) % (2 * limit) - limit
    wrapped_y = (y + limit) % (2 * limit) - limit
    
    return (round(wrapped_x,12), round(wrapped_y,12))


result = []
shared_edge = []

#for_penta_hepta_list with two or more hexagon between them
penta_hepta_no_shared_edge = []
edges_penta_hepta_no_shared_edge = []
#shared_edge
for pentagon_idx, heptagon_idx, edge in shared_edges:
    
    result += [wrap_coordinates(item) for item in pentagon_coordinates[pentagon_idx]]
    result += [wrap_coordinates(item) for item in heptagon_coordinates[heptagon_idx]]

    shared_edge += [wrap_coordinates(item) for item in edge]

# Looping through all pairs to visualize them for non-shared edge
for pentagon_idx, heptagon_idx, pentagon_edges, heptagon_edges in edge_pairs_between_centers:
    
    center_pentagon = calculate_center(pentagon_coordinates[pentagon_idx])
    center_heptagon = calculate_center(heptagon_coordinates[heptagon_idx])
    distance = np.linalg.norm(np.array(center_pentagon) - np.array(center_heptagon))
    
    if distance > 150:
        heptagon_coordinates[heptagon_idx] = relocate_polygon(heptagon_coordinates[heptagon_idx], center_pentagon)
        center_heptagon = calculate_center(heptagon_coordinates[heptagon_idx])
        distance = np.linalg.norm(np.array(center_pentagon) - np.array(center_heptagon))
    
    result += [wrap_coordinates(item) for item in pentagon_coordinates[pentagon_idx]]
    result += [wrap_coordinates(item) for item in heptagon_coordinates[heptagon_idx]]

    shared_edge += [wrap_coordinates(item) for item in pentagon_edges]
    shared_edge += [wrap_coordinates(item) for item in heptagon_edges]

    #for_extracting_penta_hepta_list with two or more hexagon between them
    if distance >5.5 and distance <20:
        penta_hepta_no_shared_edge += [wrap_coordinates(item) for item in pentagon_coordinates[pentagon_idx]]
        penta_hepta_no_shared_edge += [wrap_coordinates(item) for item in heptagon_coordinates[heptagon_idx]]

        edges_penta_hepta_no_shared_edge += [wrap_coordinates(item) for item in pentagon_edges]
        edges_penta_hepta_no_shared_edge += [wrap_coordinates(item) for item in heptagon_edges]

with open('coordinates_shared_edge.txt', 'w') as file:
    write_polygon_coord(shared_edge)

with open('coordinates_edges_two_hex++.txt', 'w') as file:
    write_polygon_coord(edges_penta_hepta_no_shared_edge)
