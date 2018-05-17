# Run the GOMC simulation in NVT for 2 million steps.
# Assuming that GOMC base directory was cloned in your Desktop:

~/Desktop/GOMC/bin/GOMC_CPU_NVT dpc_NVT.conf > output_DPC.log &

# You can monitor the simulation by running the following command: 

tail -f output_DPC.log

# Wait until simulation finished, then exit command by typing "ctrl C"
# To generate the RDF, we use vmd to calculate the RDF. Load the GOMC output 
# PDB and PSF file into vmd.

vmd DPC_310_K_merged.psf DPC_310_K_BOX_0.pdb &

# Under "Extensions" tab, select "Analysis", the click on 
# "Radial Pair Distribution Function g(r)". Follow the steps on opened window
# 1- To select the file, click on "(none)" and select 
#    "0 DPC_310_K_merged.psf".
# 2- Select the residue name that you want to calculate RDF. Type "name C3A" 
#    in Selection 1 and Selection 2.
# 3- Set the starting frame by changing the value of "First:" to 100.
# 4- Set maximum RDF distance calculation by changing the value of the 
#    "max. r:" to 30.
# 5- Check mark on "Save to File".
# 6- Click the "Compute g(r)" button to plot and save the g(r).
# 7- Click the "Save" button on the open window.
# 8- Close the vmd application from VMD main window.

##############################################################################
##############################################################################
#
# You can visualize the self assembly of DPC by following command

vmd DPC_310_K_merged.psf DPC_310_K_BOX_0.pdb &

# To visualize the change in the volume, select "Tk Console" under 
# "Extensions" tab. 
# 1- Type the following command in VMD TKConsole to draw a box.

  pbc box

# 2- Close the VMD TKConsole.
# 3- To visualize the simulation trajectories, on the right lower corner of 
#    VMD Main window, adjust the speed and click the play button.
# 4- Close the vmd application from VMD main window.

