#!/bin/bash

# Exit immediately if any command exits with a non-zero status
set -e

####################ChangeThisPortionOnly####################################

dimension=400     #square box dimension (x=y), in angstrom unit 
no_of_grain=5     #total no of grain

#############################################################################

GB_name="GB${dimension}A_${no_of_grain}Gr"
#Create folder for the created structure
if [ ! -d ${GB_name} ]; then
    mkdir ${GB_name}
fi
cd ${GB_name}

#Setup for creating the coordinates of the GB structure
echo "Creating the required structure with user input"
python3 ../Codes/structure_gen_poly.py ${dimension} ${no_of_grain} "${GB_name}.cfg"

#Create .lmp files from cfg files and prepare GB_atom_data file
echo "Converting the .cfg file to .lmp file"
python3 ../Codes/cfg2lmp.py "${GB_name}.cfg"
#Run Lammps energy minimization
echo "Lammps energy minimization is running. May take time. Be patient."
mpiexec -np 8 lmp -in ../Codes/in.min -screen none
rm ./log.lammps

#Run ovito data extraction to extract only the GB atoms from the energy minimized structure
python3 ../Codes/ovito_data_extract_poly.py
#Run periodicpolyGrain to unwrap the GB atoms so that no bonds are formed with atoms in diffrent boundray region
python3 ../Codes/periodicpolyGrain.py
#Run identify_penta_hepta_poly to identify pentagon and heptagon
echo "Identifying the pentagon and heptagons in GB area and making pairs of them"
python3 ../Codes/identify_penta_hepta_poly.py atom_data_GB.txt Penta_Hepta.png
#Run to find the pairs of pentagon and heptagon
python3 ../Codes/pair_find.py ${dimension}

#check if there is two hexagons between penta-hepta pair
filename="coordinates_edges_two_hex++.txt"
# Check if the file exists and is readable
if [ -f "$filename" ] && [ -r "$filename" ]; then
    # Check if file content is blank (only whitespace or no content at all)
    if [[ ! $(<"$filename") =~ [^[:space:]] ]]; then
        # Commands to execute if file is blank
        echo "Running Type atom_id.py"
        python3 ../Codes/atom_id.py
        echo "Running Type Assign.py with min.lmp"
        python3 ../Codes/type_assign.py "${GB_name}.lmp"

    else
        echo "Running NNFind.py"
        python3 ../Codes/NNFind_1.py
        python3 ../Codes/NNFind_2.py
        python3 ../Codes/NNFind_3.py
        echo "Running Type atom_id.py"
        python3 ../Codes/atom_id.py
        echo "Running Type Assign.py with min.lmp"
        python3 ../Codes/type_assign.py "${GB_name}.lmp"
    fi
else
    echo "coordinates_edges_two_hex++.txt does not exist or is not readable."
fi
