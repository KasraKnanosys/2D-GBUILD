
Author: Nuruzzaman Sakib and Md Rashidul Alam, University of Alabama, USA
This file describes how PolyGen.sh works, what the user must modify, and
all possible error messages.

---------------------------------------------------------------------- 
PURPOSE
----------------------------------------------------------------------
PolyGen.sh automates the generation of polycrystalline graphene-like
materials and converts them into TMD structures (such as WSe2). The script
creates a periodic Voronoi polycrystal, performs a LAMMPS minimization,
extracts grain boundary atoms, identifies pentagon–heptagon defects,
matches defect pairs, assigns atom types, and outputs a TMD LAMMPS file.

It orchestrates more than 18 Python files plus LAMMPS and OVITO.

----------------------------------------------------------------------
USER PARAMETERS (ONLY THESE TWO SHOULD BE MODIFIED)
----------------------------------------------------------------------
Inside PolyGen.sh:

    dimension=400
    no_of_grain=5

dimension:
    Box dimension in Angstrom. Sets a square simulation cell of size
    dimension × dimension.

no_of_grain:
    Total number of Voronoi grains to generate. More grains lead to
    smaller grains and more grain boundaries.

PolyGen.sh creates an output folder:
    GB<dimension>A_<no_of_grain>Gr
Example:
    GB400A_5Gr

**----------------------------------------------------------------------**
**WORKFLOW EXECUTED BY PolyGen.sh**
**----------------------------------------------------------------------**

Step 1: Generate initial polycrystal structure
    python3 ../Codes/structure_gen_poly.py dimension no_of_grain GBname.cfg

Step 2: Convert CFG file to LAMMPS format
    python3 ../Codes/cfg2lmp.py GBname.cfg

Step 3: Energy minimization using LAMMPS
    mpiexec -np 8 lmp -in ../Codes/in.min
    (log.lammps is removed afterwards)

Step 4: Extract only grain boundary atoms
    python3 ../Codes/ovito_data_extract_poly.py
    Produces atom_data_GB.txt

Step 5: Remove periodic bond artifacts and unwrap GB atoms
    python3 ../Codes/periodicpolyGrain.py

Step 6: Identify pentagon and heptagon rings in the GB area
    python3 ../Codes/identify_penta_hepta_poly.py atom_data_GB.txt Penta_Hepta.png

Step 7: Pair pentagons with heptagons
    python3 ../Codes/pair_find.py dimension
    Produces coordinates_edges_two_hex++.txt

Step 8: Branch case depending on double-hexagon spacing

    Case A: If coordinates_edges_two_hex++.txt is EMPTY:
        python3 ../Codes/atom_id.py
        python3 ../Codes/type_assign.py GBname.lmp

    Case B: If file is NOT empty:
        python3 ../Codes/NNFind_1.py
        python3 ../Codes/NNFind_2.py
        python3 ../Codes/NNFind_3.py
        python3 ../Codes/atom_id.py
        python3 ../Codes/type_assign.py GBname.lmp

Step 9: Final TMD conversion
    type_assign.py produces:
        WSe2_GB*.lmp  (final TMD structure)
        type.txt
        out_col.txt

**----------------------------------------------------------------------**
****4. MAJOR PYTHON MODULES (SUMMARY)****
**----------------------------------------------------------------------**

structure_gen_poly.py        -  Generates polycrystal & Voronoi structure
polyCrystal.py               -  Periodic Voronoi + CVT relaxation
_cPolyUtils.c                -  C-accelerated Voronoi routines
cfg2lmp.py                   -  Convert .cfg → .lmp
ovito_data_extract_poly.py   - Extract GB atoms only
periodicpolyGrain.py         - Unwrap GB atoms
identify_penta_hepta_poly.py - Detects 5|7 rings
pair_find.py                 - Penta–hepta pairing logic
NNFind_1/2/3.py              - Neighbor repair tools
atom_id.py                   - Unique atom labeling
type_assign.py               - Assigns TMD atom types and builds final structure

**----------------------------------------------------------------------**
**5. FINAL OUTPUT FILES**
**----------------------------------------------------------------------**

Generated inside GB<dimension>A_<no_of_grain>Gr/:

    GB*.cfg                 Original polycrystal
    GB*.lmp                 Graphene-like LAMMPS file
    min.lmp                 LAMMPS minimized structure
    atom_data_GB.txt        GB atom list
    Penta_Hepta.png         Ring map (5|7)
    type.txt                Type assignment
    out_col.txt             Coloring output
    WSe2_GB*.lmp            Final TMD polycrystal (use this for your TMD work)

**----------------------------------------------------------------------**
**6. HOW TO RUN**
**----------------------------------------------------------------------**

Make sure:
    - LAMMPS is installed and "lmp" is in PATH
    - Python3 installed
    - OVITO Python module installed (pip install ovito)
    - ASE installed (pip install ase)
    - _cPolyUtils compiled via:
        python3 setup.py build_ext --inplace

Run PolyGen:
    bash PolyGen.sh

Do not change the folder locations unless updating PolyGen.sh paths.

**----------------------------------------------------------------------**
**7. POSSIBLE ERROR MESSAGES AND THEIR MEANING**
**----------------------------------------------------------------------**

1. Missing command-line arguments
   Example:
       Not enough command-line arguments provided
   Cause:
       A script was called manually with missing arguments.

2. coordinates_edges_two_hex++.txt missing or unreadable
   Cause:
       Pairing step failed or script was run from the wrong directory.

3. "It seems that either the cell is too small or there are too many grains."
   Cause:
       dimension too small or no_of_grain too large.
       Generated Voronoi regions fail.

4. Voronoi error: "Open region associated with generator"
   Cause:
       Periodic replication failed or invalid seeds.

5. LAMMPS errors:
       lmp: command not found
       MPI errors during mpiexec
   Cause:
       LAMMPS not installed or not in PATH.

6. Python module errors:
       ModuleNotFoundError: No module named 'ovito'
       ModuleNotFoundError: No module named 'ase'
   Cause:
       Missing Python dependencies.

7. _cPolyUtils not compiled:
       ImportError: No module named _cPolyUtils
   Fix:
       python3 setup.py build_ext --inplace

8. Missing or empty atom_data_GB.txt
   Cause:
       ovito_data_extract_poly.py failed or no GB atoms detected.

9. IndexError, list assignment error
   Cause:
       Missing neighbor lists, missing bond data, or earlier steps failing.


**----------------------------------------------------------------------**
**8. CITATION**
**----------------------------------------------------------------------**
If you use PolyGen in your research, please cite:

PolyGen toolkit — Nuruzzaman Sakib, University of Alabama
Large-scale experimental and theoretical study of graphene grain boundary
structures — Ophus, Shekhawat, Rasool, Zettl (Phys. Rev. B 92, 205402)

======================================================================

End of README
