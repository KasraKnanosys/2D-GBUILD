#!/bin/bash

# Exit immediately if any command exits with a non-zero status
set -e

####################ChangeThisPortionOnly####################################

r1=1      #rotation 
r2=3     #rotation
cell_width=$(echo "scale=2; 100/1.37" | bc)

#############################################################################

#Setup for creating the coordinates of the GB structure
GB_name="GB${r1}_${r2}"
python3 ./Codes/structure_gen.py ${r1} ${r2} ${cell_width} "${GB_name}.lmp"
# Replace the read_data line with the new input filename
sed -i "s/read_data .*/read_data ${GB_name}.lmp/" ./Codes/in.min
# Replace the write_data line with the new output filename
sed -i "s/write_data .*/write_data ${GB_name}.lmp/" ./Codes/in.min
lmp -in ./Codes/in.min -screen none
rm ./log.lammps

#Setup for creating the bi-atomic structure
file_name="same_atom.txt"

if [ ! -d ${GB_name} ]; then
    mkdir ${GB_name}
fi

cd ${GB_name}
mv ../"${GB_name}.lmp" .
# Check if the file exists
if [ -f "$file_name" ]; then
    # If the file exists, remove it
    rm "$file_name"
fi

# Create a new file with the same name
touch "$file_name"

echo "Executing ovito_data_extract.py with $GB_name"
python3 ../Codes/ovito_data_extract.py "${GB_name}.lmp"

echo "Executing identify_penta_hepta.py with atom_data_GB_1.txt and GB_Atoms_Left.png"
python3 ../Codes/identify_penta_hepta.py atom_data_GB_1.txt GB_Atoms_Left.png

echo "Executing shared_edge.py with $GB_name and Same_Atoms_Left.png"
python3 ../Codes/shared_edge.py "${GB_name}.lmp" Same_Atoms_Left.png

echo "Executing identify_penta_hepta.py with atom_data_GB_3.txt and GB_Atoms_Right.png"
python3 ../Codes/identify_penta_hepta.py atom_data_GB_3.txt GB_Atoms_Right.png

echo "Executing shared_edge.py with $GB_name and Same_Atoms_Right.png"
python3 ../Codes/shared_edge.py "${GB_name}.lmp" Same_Atoms_Right.png

echo "Executing type_assign.py with $GB_name"
python3 ../Codes/type_assign.py "${GB_name}.lmp"

#delete unnecessary files
for file in *.txt; do
    if [ -f "$file" ]; then
        rm "$file"
    fi
done

