# To pack 400 mC6cycle molecules in a 55 Angstrom cubic box for liquid phase
# pack 100 mC6cycle molecules in a 73 Angstrom cubic box for vapor phase and 
# generate PDB and PSF file. 
# Copy and paste the following command in your terminal:

# This command packs 400 molecules and saves it as "packed_mC6cycle_liq.pdb"
packmol < pack_box_0.inp

# This command generates new pdb and psf files for Box 0.
vmd < build_psf_box_0.tcl


# This command packs 100 molecules and saves it as "packed_mC6cycle_vap.pdb"
packmol < pack_box_1.inp

# This command generates new pdb and psf files for Box 1.
vmd < build_psf_box_1.tcl
