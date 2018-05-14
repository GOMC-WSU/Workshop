# Copy the 'packmol' executable file into this directory.
#
# To pack 1000butane molecules in a 53 Angstrom cubic box and generate PDB and 
# PSF file. Copy and paste the following command in your terminal:


# This command packs 1000 butane molecules and saves it as "packed_butane.pdb"
./packmol < pack_box_0.inp

# This command generates new pdb and psf files using the VMD program
vmd < build_psf_box_0.tcl
