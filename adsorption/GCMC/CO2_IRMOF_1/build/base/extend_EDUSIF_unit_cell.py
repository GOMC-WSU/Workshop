from pymatgen import Lattice, Structure, Molecule
import openbabel

#pymatgen
structure = Structure.from_file("EDUSIF_clean_min_charges.cif")
structure.make_supercell([2, 2, 2])
structure.to(filename="EDUSIF_2x2x2.cif")

#openbabel
obConversion = openbabel.OBConversion()
obConversion.SetInAndOutFormats("cif", "pdb")
mol = openbabel.OBMol()
obConversion.ReadFile(mol, "EDUSIF_2x2x2.cif")
obConversion.WriteFile(mol, 'EDUSIF_clean_min.pdb')
