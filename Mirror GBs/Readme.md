README – gb4848.py

This script generates a WSe2 grain boundary (GB) that contains a 4|8-type defect sequence. 
It constructs two grains, mirrors one of them, inserts additional atoms to form the defect 
chain, and outputs a LAMMPS-ready data file.

USAGE
------
python gb4848.py <arg1> <arg2>

DESCRIPTION OF ARGUMENTS
-------------------------
arg1 = number of tetragonal (4-ring) units placed BEFORE the octagon in the 4|8 chain
arg2 = number of tetragonal (4-ring) units placed AFTER the octagon

The resulting GB contains this sequence:
    arg1 × (tetragon)  →  1 × (octagon)  →  arg2 × (tetragon) →  1 × (octagon) 

Example:
    python gb4848.py 2 3
This produces: 4 – 4 – 8 – 4 – 4 – 4 – 8 – 4 – 4 – 8 – 4 – 4 – 4 – 8 ...

WHAT THE SCRIPT DOES
---------------------
1. Builds a single 2H-WSe2 layer (Se–W–Se stacking) using ASE.
2. Creates a supercell:
       - 10 repetitions along x (perpendicular to the GB)
       - (arg1 + arg2 + 1) repetitions along y (along the GB)
3. Mirrors the supercell in x to form the second grain.
4. Identifies atoms at the grain boundaries and sorts them along y.
5. Inserts additional W and Se atoms to construct the 4|8 defect chain.
6. Merges the two grains into a single simulation cell.
7. Writes the final structure into a LAMMPS data file.

FILES GENERATED
---------------
Left.xyz       – left grain before defect insertion
Right.xyz      – right grain before defect insertion
Left2.xyz      – left grain after inserting 4|8 units
Right2.xyz     – right grain after inserting 4|8 units
WSe2_MTB_<arg1>_<arg2>.lmp   – final LAMMPS data file

REQUIREMENTS
------------
- Python 3
- ASE (Atomic Simulation Environment)
    Install with: pip install ase

POSSIBLE ERROR MESSAGES
------------------------

1. Missing command-line arguments
---------------------------------
If the script is run without two arguments:

    python gb4848.py

You will see:

    IndexError: list index out of range

This happens because the script expects two integers.  
Fix by running with two numbers:

    python gb4848.py 2 3


2. Non-integer arguments
------------------------
If arguments cannot be converted to integers:

    python gb4848.py a b

You will see:

    ValueError: invalid literal for int() with base 10: 'a'

Fix: provide only integers (e.g., 0, 1, 2, 3…).


3. ASE not installed
---------------------
If ASE is missing, the import at the top of the script will fail with:

    ModuleNotFoundError: No module named 'ase'

Fix: install ASE:

    pip install ase


IMPORTANT NOTE
---------------
The script DOES NOT perform energy minimization.
Users must run relaxation/minimization in LAMMPS using a suitable TMD potential 
to obtain physically realistic TMD GB structures.

