TMDGen.sh – Grain Boundary to TMD Conversion Driver
===================================================

TMDGen.sh is a bash wrapper that automates the full workflow:
1) Generate a graphene grain boundary (GB) structure.
2) Relax it with LAMMPS.
3) Extract GB topology with OVITO.
4) Identify 5|7 rings and shared edges.
5) Assign atom types and convert the GB to a biatomic TMD (e.g., WSe2). 


Directory Layout and Requirements
------------------------------------

Expected layout:

- TMDGen.sh
- Codes/
    - grainBdr.py, structure_gen.py, _cGBUtils.*  - creates Graphene GB structure   
    - ovito_data_extract.py                       - extracts GB atoms
    - identify_penta_hepta.py                     - identifies pentagons and heptagons rings and atoms
    - shared_edge.py                              - determines shared-atom pairs between pentagons and heptagons
    - type_assign.py                              - TMD atom types (M/X) and converts the graphene-like (psedu TMD) structure into a true TMD structure.
    - in.min  (LAMMPS input template)
    - setup.py (for compiling _cGBUtils)

Software prerequisites:

- bash (Linux/macOS)
- Python 3
- NumPy, SciPy, ASE, NetworkX, Matplotlib, OVITO Python module
- LAMMPS, with `lmp` available in your PATH
- The C extension `_cGBUtils` compiled via:
  python3 setup.py build_ext --inplace  (run inside Codes/) 


Parameters in TMDGen.sh
--------------------------

Edit only this block near the top of TMDGen.sh:

    r1=1      # rotation index 1 (GB construction parameter)
    r2=3      # rotation index 2 (GB construction parameter)
    cell_width=$(echo "scale=2; 100/1.37" | bc)

Meaning:

- r1, r2  
  Integers defining the GB character (N1 = [r1, r2], N2 = [r2, r1]).  They control the tilt angle and repeat distance of the graphene GB.   

- cell_width  
  Effective GB width (in Å) for the underlying graphene lattice.  
  The default `100/1.37` rescales a target TMD width (~100 Å) by the graphene–TMD bond-length ratio (~1.37), consistent with the conversion in `type_assign.py`.   


How to Run
-------------

**Installation:** 
1. First run "python3 setup.py build_ext --inplace" in a terminal with "Codes" directory as current directory to create the _cGBUtils module created by Ashivni Shekhawat et al. Cite as - "Large-scale experimental and theoretical study of graphene grain boundary structures, Colin Ophus, Ashivni Shekhawat, Haider Rasool, and Alex Zettl, Phys. Rev. B 92, 205402"
2. Install NumPy (pip3 install numpy)
3. Install ASE  (pip3 install ase)
4. Install ovito using (pip3 install ovito)
5. Install NetworkX (pip install networkx)
6. Install LAMMPS (See LAMMPS website on how to install)

From the directory **above** `Codes/`, run:

    bash TMDGen.sh

Do not move TMDGen.sh or Codes/ relative to each other unless you also update the paths inside TMDGen.sh.   


What TMDGen.sh Does (Step-by-Step)
-------------------------------------

1) **Graphene GB generation**

   - Builds a graphene GB using:
     
     python3 ./Codes/structure_gen.py ${r1} ${r2} ${cell_width} "${GB_name}.lmp"

     where `GB_name="GB${r1}_${r2}"`.  
     This calls `twoPeriodicGB` and `writeLammpsData` to create a periodic graphene GB in LAMMPS data format.   

2) **LAMMPS relaxation of the graphene GB**

   - Edits `./Codes/in.min` in place to set:
     - `read_data ${GB_name}.lmp`
     - `write_data ${GB_name}.lmp`
   - Runs LAMMPS:
     
     lmp -in ./Codes/in.min -screen none

   - Deletes the LAMMPS log (`log.lammps`).

   Result: a relaxed graphene GB data file `${GB_name}.lmp` in the parent directory.

3) **Set up per-GB working directory**

   - Creates a directory `${GB_name}` if it does not exist.
   - Moves `${GB_name}.lmp` into `${GB_name}`.
   - Creates an empty `same_atom.txt` in `${GB_name}` (used later as a temporary file).

4) **Topology extraction with OVITO**

   Inside `${GB_name}`:

   - Extract bond and atom/neighbor data around both GBs:

     python3 ../Codes/ovito_data_extract.py "${GB_name}.lmp"

   This script:
   - Writes `bond_data.txt` (list of bonded atom IDs).
   - Writes `atom_data_GB_1.txt` and `atom_data_GB_3.txt` (per-GB atomic positions and neighbors). :contentReference[oaicite:11]{index=11}  

5) **5|7 ring detection and shared-edge identification**

   - Left GB (GB_1):
     - Identify pentagons/heptagons and save a labeled PNG:
       
       python3 ../Codes/identify_penta_hepta.py atom_data_GB_1.txt GB_Atoms_Left.png :contentReference[oaicite:12]{index=12}  

     - Find shared edges between pentagons and heptagons and map them back to atom IDs:

       python3 ../Codes/shared_edge.py "${GB_name}.lmp" Same_Atoms_Left.png :contentReference[oaicite:13]{index=13}  

       This writes:
       - `penta_data_unique.txt`, `hepta_data_unique.txt`
       - `same_atom.dat` (pairs of atom IDs corresponding to shared edges).

   - Right GB (GB_3): repeats the same sequence with `atom_data_GB_3.txt`, producing `GB_Atoms_Right.png` and `Same_Atoms_Right.png`, and appending to `same_atom.dat`.

6) **Type assignment and TMD conversion**

   - Assigns atom types across the GB (graph coloring on the graphene lattice), then converts the structure to a biatomic TMD:

     python3 ../Codes/type_assign.py "${GB_name}.lmp" :contentReference[oaicite:14]{index=14}  

   - `type_assign.py`:
     - Reads the relaxed graphene GB (`${GB_name}.lmp`).
     - Uses `bond_data.txt` and `same_atom.dat` to build neighbor lists and enforce correct 2-coloring across shared edges.
     - Writes:
       - `data.lmp` (colored graphene data)
       - `WSe2_${GB_name}.lmp` (biatomic TMD structure with realistic z-coordinates and scaled x–y dimensions).

7) **Cleanup**

   - Deletes all `.txt` files in `${GB_name}` (keeps `.lmp` and `.png` files).


Outputs
----------

Inside `${GB_name}/` you will typically have:

- `${GB_name}.lmp`           → relaxed graphene GB (LAMMPS data)
- `WSe2_${GB_name}.lmp`      → converted TMD GB (LAMMPS data, biatomic)
- `GB_Atoms_Left.png`        → left GB ring map
- `GB_Atoms_Right.png`       → right GB ring map
- `Same_Atoms_Left.png`      → shared-edge visualization (left GB)
- `Same_Atoms_Right.png`     → shared-edge visualization (right GB)


Possible Error Messages and Causes
-------------------------------------

TMDGen.sh uses `set -e`, so **any non-zero exit code** from a command will abort the whole script. Below are the most common issues and their messages.

(1) Missing or wrong arguments (internal Python check)
------------------------------------------------------

From `structure_gen.py`:

    Not enough command-line arguments provided for Lammps Structure Generation. :contentReference[oaicite:15]{index=15}  

Cause: TMDGen.sh normally passes 4 arguments; this message appears only if you manually call `structure_gen.py` with too few arguments.

Fix: Always call it as:

    python3 ./Codes/structure_gen.py r1 r2 cell_width output_name.lmp


(2) Python, OVITO, or LAMMPS not installed / not in PATH
---------------------------------------------------------

Examples:

- `python3: command not found`
- `ModuleNotFoundError: No module named 'ovito'`
- `ModuleNotFoundError: No module named 'networkx'`
- `ModuleNotFoundError: No module named 'ase'`
- `lmp: command not found`

Fix:  
- Install the missing Python packages via `pip3 install ...`.  
- Install LAMMPS and ensure `lmp` is on your PATH.  
- Confirm you can run each of these manually before running TMDGen.sh.

(3) Missing input files (paths or names incorrect)
--------------------------------------------------

Typical messages:

- `python3: can't open file './Codes/structure_gen.py': [Errno 2] No such file or directory`
- `sed: can't read ./Codes/in.min: No such file or directory`
- `python3: can't open file '../Codes/ovito_data_extract.py': [Errno 2] No such file or directory`
- `FileNotFoundError: [Errno 2] No such file or directory: 'bond_data.txt'` (from `type_assign.py`)   

Fix:
- Make sure you run `bash TMDGen.sh` from the directory that actually contains `TMDGen.sh` and the `Codes/` folder.  
- Do not rename or move files inside Codes/ unless you also update the script paths.

(4) Error from shared_edge.py: missing or malformed cell size
-------------------------------------------------------------

`shared_edge.py` reads `ylo yhi` from the LAMMPS data header. If it cannot find this line, it raises:

    ValueError: ly value not found in the LAMMPS data file. :contentReference[oaicite:17]{index=17}  

Fix:
- Ensure `${GB_name}.lmp` is a valid LAMMPS data file and contains a line ending with `ylo yhi`.
- Do not manually edit the header in ways that remove or rename the `ylo yhi` line.


Notes
--------

- TMDGen.sh only **builds and converts** the GB structure; it does not perform final TMD relaxation. You must run your own LAMMPS minimization using `WSe2_${GB_name}.lmp` and an appropriate TMD potential before using the structure for production simulations.   
- You can adapt `type_assign.py` to other TMDs by modifying the z-positions and masses for the two atom types.


