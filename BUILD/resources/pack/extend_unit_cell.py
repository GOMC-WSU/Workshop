from pymatgen import Lattice, Structure, Molecule
import os

#pymatgen
structure = Structure.from_file("FILEFILE")
structure.make_supercell([XXX, YYY, ZZZ])
structure.to(filename="MOFNAME_XXXxYYYxZZZ.cif")

#use openbabel to convert cif to XYZ format.
os.system('babel  -icif "MOFNAME_XXXxYYYxZZZ.cif" -oxyz "MOFNAME_clean_min.xyz"')
