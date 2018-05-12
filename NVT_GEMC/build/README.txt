# Copy the 'packmol' executable file into this directory.
#
# To pack 800 argon molecules in a 36 Angstrom cubic box for liquid phase
# pack 200 argon molecules in a 57 Angstrom cubic box for vapor phase and 
# generate PDB and PSF file. 
# Copy and paste the following command in your terminal:


# This command packs 800 argon molecules and saves it as "packed_argon_liq.pdb"
./packmol < pack_box_0.inp

# This command generates new pdb and psf files for Box 0.
vmd < build_psf_box_0.tcl


# This command packs 200 argon molecules and saves it as "packed_argon_vap.pdb"
./packmol < pack_box_1.inp

# This command generates new pdb and psf files for Box 1.
vmd < build_psf_box_1.tcl
