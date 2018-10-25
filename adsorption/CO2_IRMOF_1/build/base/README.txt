###############################################################################
# In this section, we will try to generate the PDB and PSF file for IRMOF-1.
# The IRMOF-1 cif file was downloaded from CoRE-MOF database
# https://github.com/gregchung/gregchung.github.io/tree/master/CoRE-MOFs
#
# Using VESTA, the unit cell was extended by 2X and exported as  
# "EDUSIF_clean_min_charges_modified.pdb" in pdb format.
###############################################################################
#
# To generate PDB and PSF, reuiqres 3 steps.
# 1- exported PDB file from VESTA is not quite compatible with VMD. For instance
#    the PDB file has no residue name, residue ID. We use 
#    "convert_VESTA_PDB.tcl" to reformat the output PDF from VESTA. 

# This script treats each atom as a seperate molecule kind, renumbers the 
# residue ID, and set residue name and save it in the 
# "EDUSIF_clean_min_charges_modified.pdb" file.
# running vmd with "-dispdev text" runs VMD in text mode.

vmd -dispdev text< convert_VESTA_PDB.tcl

# 2- To generate the PSF file, each molecule kind must be separated and stored
#    in seperate file. Then VMD will be used to generate the PSF file. To 
#    facilitate the process, we use "build_EDUSIF_auto.tcl".

# This command will create new PDB and PSF file for IRMOF-1.

vmd -dispdev text< build_EDUSIF_auto.tcl

# 3- The last step to set the value of beta in pdb file "IRMOF_1_BOX_0.pdb" to
#    1 in order to fix the atoms in their positions. We use the "setBeta.tcl" 
#    to change the beta value.

vmd -dispdev text < setBeta.tcl

