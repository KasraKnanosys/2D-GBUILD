PolyGen softawre created by Nuruzzaman Sakib, University of Alabama, USA
This is a python tool to create TMDC material (graphene like material) with Grain Boundaries

Installation:

1. First run "python3 setup.py build_ext --inplace" in a terminal with "Codes" directory as current directory to create the _cPolyUtils module created by Ashivni Shekhawat et al. Cite as - "Large-scale experimental and theoretical study of graphene grain boundary structures, Colin Ophus, Ashivni Shekhawat, Haider Rasool, and Alex Zettl, Phys. Rev. B 92, 205402"

Prerequisites:
1. Install NumPy (pip3 install numpy)
2. Install ASE  (pip3 install ase)
3. Install ovito using (pip3 install ovito)
4. Install LAMMPS (See LAMMPS website on how to install)

Instruction for use:

1. Change the bash file "PolyGen.sh" according to the Number of Grains and dimension of the structure. Just change the "dimension","no_of_grain".
2. run bash PloyGen.sh from its directory. Do not change the folder and TMDGen location. If you do, then change the bash script as well to accomodate the change.
3. After that, you need to run energy minimization of the created polycrystal of TMD GB structure before use in LAMMPS calculation.
