# In this section, we will try to generate the PDB and PSF file for IRMOF-1.
###############################################################################
# Downloading the cif file
# To begin, we need to download the minimized structure of IRMOF-1 from 
CoRE-MOFs data base. You can download it from following website:

https://github.com/gregchung/gregchung.github.io/blob/master/CoRE-MOFs/CoRE-MOF-1.0-DFT-minimized.tar.gz

# After downloading, exctract it by following command

tar -xzvf CoRE-MOF-1.0-DFT-minimized.tar.gz

# Next we need to copy the IRMOF_1 *.cif to this directory. Assuming your 
# downloaded file is in Download directory, use the following command:

cp  ~/Downloads/CoRE-MOF-1.0-DFT-Minimized/minimized_structures_with_DDEC_charges/EDUSIF_clean_min_charges.cif .

###############################################################################
# Extend the unit cell by a factor of 2 for each unit cell and export as a PDB 
# file. For this section, please refere to the VESTA.pdf file.
#
###############################################################################
#
# To generate PDB and PSF, reuiqres 3 steps.
# 1- exported PDB file from VESTA is not quite compatible with VMD. For instance
#    the PDB file has no residue name, residue ID. We use 
#    "convert_VESTA_PDB.tcl" to reformat the output PDF from VESTA. 

# This script will treat each atom as a seperate molecule kind, renumber the 
# residue ID, and set residue name and save it in the 
# "EDUSIF_clean_min_charges_modified.pdb" file.

vmd < convert_VESTA_PDB.tcl

# 2- To generate the PSF file, each molecule kind must be separated and stored
#    in seperate file. Then VMD will be used to generate the PSF file. To 
#    facilitate the process, we use "build_EDUSIF_auto.tcl".

# This command will create new PDB and PSF file for IRMOF-1.

vmd < build_EDUSIF_auto.tcl

# 3- The last step to set the value of beta in pdb file "IRMOF_1_BOX_0.pdb" to
#    1 in order to fix the atoms in their positions. We use the "setBeta.tcl" 
#    to change the beta value.

vmd < setBeta.tcl

