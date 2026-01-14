import grainBdr as gb
import sys

if len(sys.argv) != 5:
    print("Not enough command-line arguments provided for Lammps Structure Generation.")

cr = gb.twoPeriodicGB(N1=[int(sys.argv[1]),int(sys.argv[2])],N2=[int(sys.argv[2]),int(sys.argv[1])],cell_width=float(sys.argv[3]),verbose=False)
gb.writeLammpsData(cr,sys.argv[4])

