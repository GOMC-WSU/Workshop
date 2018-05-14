# Run the GOMC simulation in NVT for 2 million steps.
# Assuming that GOMC base directory was cloned in your Desktop:

~/Desktop/GOMC/bin/GOMC_CPU_NVT argon_NVT.conf > output_argon.log &

# You can monitor the simulation by running the following command: 

tail -f output_argon.log

# Wait until simulation finished, then exit command by typing "ctrl C"
# To generate the RDF, we use vmd to calculate the RDF. Load the GOMC output 
# PDB and PSF file into vmd.

vmd  Argon_NVT_T_120K_BOX_0.pdb &

# Under "Extensions" tab, select "Analysis", the click on 
# "Radial Pair Distribution Function g(r)". Follow the steps on opened window
# 1- To select the file, click on "(none)" and select 
#    "0 Argon_NVT_T_120K_BOX_0.pdb".
# 2- Select the residue name that you want to calculate RDF. Type "resname AR" 
#    in Selection 1 and Selection 2.
# 3- Check mark on "Save to File".
# 4- Click the "Compute g(r)" button to plot and save the g(r).
# 5- Click the "Save" button on the open window.
# 6- Close the vmd application from VMD main window.

# To extract the total energy and steps number use the following command:
# This command will extract the first and second column of Blk file and
# save it tp "energy.dat" file.

cat Blk_Argon_NVT_T_120K_BOX_0.dat | awk '{print $1 " " $2}' > energy.dat
