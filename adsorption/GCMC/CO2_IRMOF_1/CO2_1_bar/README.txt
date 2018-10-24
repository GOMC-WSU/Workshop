# Run the GOMC simulation in GCMC for 2 million steps.
# Assuming that GOMC base directory was cloned in your Desktop:

~/Desktop/GOMC/bin/GOMC_CPU_GCMC +p4 carbondioxide_GCMC.conf > output_CO2.log &

# if you have CUDA installed, you can use GPU code by running following command:

~/Desktop/GOMC/bin/GOMC_GPU_GCMC carbondioxide_GCMC.conf > output_CO2.log &

# You can monitor the simulation by running the following command: 

tail -f output_CO2.log

# Wait until simulation finished, then exit command by typing "ctrl C"

##############################################################################
##############################################################################
#
# To extract statistical properties, we can use 'awk' command.
# This command extract and save the argon mol fraction and total number of molecules.

cat Blk_CO2_IRMOF_1_BOX_0.dat | awk '{print $1 " " $10 " " $19}' > mol_CO2.dat

##############################################################################
##############################################################################
#
# You can visualize the output of GOMC in VMD by following command
# To visualize the argon adsorption, run the following command:

vmd CO2_IRMOF_1_BOX_0.pdb &

# To visualize the change in the volume, select "Tk Console" under 
# "Extensions" tab. 
# 1- Type the following command in VMD TKConsole to draw a box.

  pbc box

# 2- Close the VMD TKConsole.
# 3- To visualize the simulation trajectories, on the right lower corner of 
#    VMD Main window, adjust the speed and click the play button.
# 4- Close the vmd application from VMD main window.
