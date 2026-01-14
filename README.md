# 2D-BUILD
This file contains the codes and user manual for the Grain Boundary Generation of TMD materials. The code can create Mirror-Twin Grain Boundaries (MTB), Tilt-Grain Boundaries and Polycrystalline TMD structures.

# **Polycrystal code:**

## cfg2lmp.py:

- Read the box dimension and number of atoms from the provided cfg file

- Read the atom position and tags ( from graphene code)

- Create the LAMMPS data file using the LAMMPS input file format

- Write the LAMMPS data file with all the atoms (LAMMPS_data.lmp)

- Write another data file with the grain boundary and boundary atoms only (gb_data.lmp)

## in.min:

- Simple LAMMPS script to run energy minimization of the created graphene structure with LCBOP potential.

- Write the minimized structure in LAMMPS format (min.lmp).

## ovito_data_extract_poly.py:

- It can extract the atom id from the ‘gb_data.lmp’ file and then extract the position (x and y) values of the atoms for only GB atoms.

- Then it uses the OVITO Python module to obtain bond properties for GB atoms and all atoms, and stores the information in separate files (bond_data.txt and bond_data_all.txt). It mainly creates a list of neighbor atoms based on the bonded topology, with a cut-off distance taken as 1.85Å. So, it will have 3 neighbors for each atom, as ‘C’ is bonded with the neighboring three carbon atoms in graphene. Then it writes the GB atoms’ neighbor list in a text file named ‘atom_data_GB.txt’.

## periodicpolyGrain.py:

- It creates a dictionary with GB atom IDs as keys and position and neighbor lists as values.

- In the GB atoms, because the structure is periodic, the bonds formed between two neighboring atoms may lie on opposite sides of the box. This code module can identify bonded atoms and unwrap the GB atoms, ensuring that no bonded atom positions are on opposite sides of the box. To do that, we first calculated the chains of atoms on either side of the box that share a bond across the boundary of the created structure. Then move the entire chain, which is shorter compared to the other one.

- After that, the shifted/moved atom properties along with the unmoved ones are written in a new text file (data_shifted.lmp) for later use.

- It also edited the ‘atom_data_GB.txt’ file with the new positional coordinate of the moved atoms.

##  identify_penta_hepta_poly.py:

- First, a graph is created using the Python networkx module. Then, from the ‘atom_data_GB.txt’ file, the nodes and edges of the graph are created by using the GB atoms' positions (x, y) as the nodes' positions and bonds as edges.

- Then, using depth-first search (DFS), all nodes in the graph are visited. A decision point that asks if the depth is greater than 4 and if the current node is the start node. If true, this path is added to the polygons list as it forms a closed loop.

- Another decision point that checks if the depth exceeds 7. If yes, the function returns to avoid deeper recursion. This is because the heptagon has 7 nodes and is the highest-polygon present in the graph.

- The process loops through each neighbor of the current node. For each neighbor, the function checks whether it has been visited, calculates the distance to the start node, and decides whether to continue the recursion based on that distance.

- If the neighbor is within a permissible distance (e.g., <= 3.2 units), and it hasn't been visited, the function recurses with the neighbor as the new node. If the depth is 5, 6, or 7 and the start node is in its neighbor list, it recurses directly back to the start node to check for polygon completion.

- If the neighbor is the start node and the depth is either 5 or 7, the function recurses back to the start node to check if a valid polygon can be formed.

- After exploring a path or returning from a recursive call, the current node is removed from the visited set. This step is crucial to allow other paths to be explored with this node as part of a potential polygon.

- The function completes its execution for a single node's recursion, then returns control to the main loop, which triggers the backtrack function for each node in the graph.

- Each node in the graph is used as a start node, and the process repeats, finding all possible polygons that include each node.

## pair_find.py:

- This code takes the polygon list created from the ‘identify_penta_hepta_poly.py’ code as input.

- Then, using the Hungarian algorithm, it generates the pair list of pentagons and heptagons present in the graph. For this, it uses the distance between pentagon and heptagon centers as a cost function and iterates over all the pentagons and heptagons to minimize the cost function. We also accounted for the periodic nature of the structure when calculating distances between the pentagon and the heptagon.

- Finally, it gives the cost-minimized pair list of pentagons and heptagons.

- For the visualization, it colors the shared edge between the pentagon and heptagon pair as yellow, for a 5|7 pair, which has a hexagon in between them, it colors the edges shared by the 5|6 and 7|6 as cyan.

- It writes a text file 'coordinates_shared_edge.txt' with the shared edges coordinates (x,y).

## NNFind_1/2/3.py:

- If the pair_find.py found a 5|7 pair that has two or more hexagons in between them, then this code finds the atoms of the adjacent hexagons, a hexagon that has at least one edge shared with either the pentagon or the heptagon. It then uses the graph-searching algorithm from pair_find.py to find pentagons, hexagons, and heptagons. It then identifies the shared edge between the hexagon network and the pentagon and heptagon.

- It appends the shared edges coordinates to the 'coordinates_shared_edge.txt' file.

## atom_id.py:

- This part of the code then takes 'coordinates_shared_edge.txt' as input. From the coordinates of the shared edge nodes, it finds the atom IDs for those coordinates in the energy-minimized structure (min.lmp).

- Those atom IDs are written in a text file named ‘same_atom_all.txt’.

## type_assign.py:

- This code takes the ‘same_atom_all.txt’ as input.

- It then visits all the atoms and traverses its neighbors. When it traverses an atom, set its type either as type-1 or type-2; all the neighbors of type-1 are type-2, and vice versa. An exception is made only for the atoms that are listed in the ‘same_atom_all.txt’ file. For an atom pair listed in ‘same_atom_all.txt’, both of them will be set to the same type, and other neighbor atoms will be the opposite type.

- After setting type for all the atoms, it generates two LAMMPS data file, one is the hBN structure and another one is the corresponding $WSe_2$ GB structure in LAMMPS input data format. These two structures are the exact conversion of the graphene structure with the same type of defect and the same number of GBs. These outputs can be changed by the user to create other TMDs of the same space group and graphene-like materials.

## polygen.sh:

- This is a bash script that contains all the Python module code and their commands to automate the conversion process. By changing the dimension and number of grains, one can generate graphene, hBN, and $WSe_2$ structures with different sizes and numbers of grains.

  

# **BiCrystal Code:**

## in.min:

- Simple LAMMPS script to run energy minimization of the created graphene structure with LCBOP potential.

- Write the minimized structure in LAMMPS format (min.lmp).

## ovito_data_extract.py:

- This module prepares the data file for the conversion of tilted graphene structures to $WSe_2$ or hBN structures (mono-elemental to bi-elemental).

- First, it replicates the y direction using _pipeline.modifiers.append(ReplicateModifier(num_y=3))_ and then selects a 10Å strip of the GB portion of the structure. Due to periodicity, the tilted GB structures have two GB in the structure.

- After that, it creates a bond using 1.60Å as a cut-off distance for bond creation using the _CreateBondsModifier_ of OVITO.

- Finally, it writes the atom id, position, and neighbor list of the selected GB area to a text file named ‘_atom_data_GB.txt_’.

## identify_penta_hepta.py:

- This mainly works similarly to the ‘_identify_penta_hepta_poly.py_’ code, which identifies the pentagon, hexagon, and heptagon from the input data.

- It then finds the pair of pentagon and heptagon (5|7) from the graph. In order to do that, it first counts the number of pentagons and heptagons. If the number is the same, it identifies the 5|7 pair based on the distance between the pentagon and the heptagon center. If the number is unequal, then it finds the extra polygon type (either pentagon or heptagon), removes it, and forms the pair list.

- After that, it writes two text files, one containing pentagon coordinates and another containing the heptagon coordinates.

## shared_edge.py:

- This portion of the code reads the coordinates of the pentagon and heptagon text files generated by ‘_identify_penta_hepta.py_’.

- After that, it sorts the pentagon and heptagon based on the location of their center. Finally, it finds the shared edges between the pentagon and the heptagon for each pair.

- For a shared edge, there are two nodes. Using the coordinates of those nodes, later this code finds the atom IDs for each node from the ‘_min.lmp_’ file.

- Then it writes the atom IDs in a text file named ‘_same_atom.dat_’.

## type_assign.py:

- This code takes the ‘same_atom.dat’ as input.

- It then visits all the atoms and traverses its neighbors. When it traverses an atom, set its type to either type-1 or type-2; all the neighbors of type-1 are type-2, and vice versa. An exception is made only for the atoms that are listed in the ‘same_atom_all.txt’ file. For an atom pair listed in ‘same_atom_all.txt’, both of them will be set to the same type, and other neighbor atoms will be the opposite type.

- After setting type for all the atoms, it generates two LAMMPS data files, one is the hBN structure and another one is the corresponding $WSe_2$ GB structure in LAMMPS input data format. These two structures are exact conversions of the graphene structure, with the same type of defect and the same number of GBs. These outputs can be changed by the user to create other TMDs of the same space group and graphene-like materials.

## **Mirror GBs:**

- Defined the unit cell using ASE library (Python module)

- Defined the replication number for the x and y directions from the user input. By changing the replication number in the x and y directions, the user can actually fully control the dimensions of the structure in the planar direction.

- The Y-direction replication number is controlled by the number of tetragons and octagons needed. If the GB area contains nt number of tetragons, the number of octagons is always two for a unit cell, then the y replication number will be $y_{r} = n_{t} + 1$. Suppose there are 2 tetragons, then an octagon, then 3 tetragons, and then an octagon again. If this creates a periodic defect chain, the number of y replication will be = (2+3) + 1 = 6.

- After the required replication of the unit cell in both directions, the structure was mirrored with respect to the yz plane to create a mirror boundary. After the mirror operation, the atoms were wrapped to ensure all the atoms are inside the box dimension.

- The original structure is named as supercell_L, and the mirrored structure is named as supercell_R.

- Added atoms to supercell_L and supercell_R to create the specified defect at the boundary. First, the atoms near the GB boundary for both supercells were identified, then the alternate extra atoms were added, i.e., if the existing atom is ‘Se’, then we added ‘W’ and vice versa. The number of added atoms is determined from the number of tetragons in the defective structure’s unit cell.

- Stitch the original and mirrored structures together, adding atoms, and create the final structure.
