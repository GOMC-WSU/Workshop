from pymatgen import Lattice, Structure, Molecule
import openbabel

#pymatgen
structure = Structure.from_file("FILEFILE")
structure.make_supercell([XXX, YYY, ZZZ])
structure.to(filename="MOFNAME_XXXxYYYxZZZ.cif")

#openbabel
obConversion = openbabel.OBConversion()
obConversion.SetInAndOutFormats("cif", "pdb")
mol = openbabel.OBMol()
obConversion.ReadFile(mol, "MOFNAME_XXXxYYYxZZZ.cif")
obConversion.WriteFile(mol, 'MOFNAME_clean_min.pdb')
