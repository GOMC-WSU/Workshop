# In this section, we will try to generate the PDB and PSF file for IRMOF-1.
###############################################################################
# Downloading the cif file
# To begin, we need to download the minimized structure of IRMOF-1 from 
CoRE-MOFs data base. You can download it from following link:

https://github.com/gregchung/gregchung.github.io/blob/master/CoRE-MOFs/CoRE-MOF-1.0-DFT-minimized.tar.gz

# After downloading, extract it by following command:

tar -xzvf CoRE-MOF-1.0-DFT-minimized.tar.gz

# Next we need to copy the IRMOF_1 *.cif to this directory. Assuming your 
# downloaded cif file is in the "Download" directory, use the following command:

cp ~/Downloads/CoRE-MOF-1.0-DFT-Minimized/minimized_structures/EDUSIF_clean_min.cif .

###############################################################################
# Next we should extend the unit cell by a factor of 2 for each unit cell and 
# export as a PDB file. For this section, please refer to the VESTA.pdf file.
#
###############################################################################
#
# To generate PDB and PSF, requires 3 steps.
# 1- exported PDB file from VESTA is not quite compatible with VMD. For instance
#    the PDB file has no residue name, residue ID. We use 
#    "convert_VESTA_PDB.tcl" to reformat the output PDF from VESTA. 

# This script will treat each atom as a separate molecule kind, renumber the 
# residue ID, and set residue name and save it in the 
# "EDUSIF_clean_min_modified.pdb" file.

vmd < convert_VESTA_PDB.tcl

# 2- To generate the PSF file, each molecule kind must be separated and stored
#    in separate file. Then VMD will be used to generate the PSF file. To 
#    facilitate the process, we use "build_EDUSIF_auto.tcl".

# This command will create new PDB and PSF file for IRMOF-1.

vmd < build_EDUSIF_auto.tcl

# 3- The last step to set the value of beta in pdb file "IRMOF_1_BOX_0.pdb" to
#    1 in order to fix the atoms in their positions. We use the "setBeta.tcl" 
#    to change the beta value.

vmd < setBeta.tcl

