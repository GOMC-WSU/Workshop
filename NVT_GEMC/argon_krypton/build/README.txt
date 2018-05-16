# Copy the 'packmol' executable file into this directory.
#
# To pack 300 argon molecules and 300 molecule krypton in a 32 Angstrom cubic 
# box for liquid phase.Pack 200 argon molecules and 200 krypton molecule in a 
# 63 Angstrom cubic box for vapor phase and generate PDB and PSF file. 
# Copy and paste the following command in your terminal:


# This command packs both molecule kind and saves it as 
# "packed_argon_krypton_liq.pdb"

./packmol < pack_box_0.inp

# This command generates new pdb and psf files for Box 0.

vmd < build_psf_box_0.tcl


# This command packs both molecules kind and saves it as 
# "packed_argon_krypton_vap.pdb"

./packmol < pack_box_1.inp

# This command generates new pdb and psf files for Box 1.

vmd < build_psf_box_1.tcl
