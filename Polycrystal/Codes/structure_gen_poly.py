import polyCrystal as pc
import ase.io
import numpy
import sys

if len(sys.argv) != 4:
    print("Not enough command-line arguments provided for Lammps Structure Generation.")

cr = pc.periodicCrystal(L=numpy.array([int(sys.argv[1]),int(sys.argv[1])]),N=int(sys.argv[2]))
ase.io.write(sys.argv[3],cr)
