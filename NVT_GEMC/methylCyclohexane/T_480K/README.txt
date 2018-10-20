# Run the GOMC simulation in NVT for 1 million steps.
# Assuming that GOMC base directory was cloned in your home direcotry:

~/Code/GOMC/bin/GOMC_CPU_GEMC mC6cycle_GEMC.conf > output_mC6cycle.log &

# You can monitor the simulation by running the following command: 

tail -f output_mC6cycle.log

# Wait until simulation finished, then exit command by typing "ctrl C"

##############################################################################
##############################################################################
#
# To extract statistical properties, we can use 'awk' command.
# This command extract and save the density value for liquid and vapor phase.

cat Blk_mC6cycle_GEMC_T_480K_BOX_0.dat | awk '{print $1 " " $13}' > density_liq.dat
cat Blk_mC6cycle_GEMC_T_480K_BOX_1.dat | awk '{print $1 " " $13}' > density_vap.dat

# This command extract and save the pressure value for vapor phase.

cat Blk_mC6cycle_GEMC_T_480K_BOX_1.dat | awk '{print $1 " " $11}' > pressure.dat

# This command extract and save the heat of vaporization value.

cat Blk_mC6cycle_GEMC_T_480K_BOX_1.dat | awk '{print $1 " " $15}' > heatOfVap.dat

##############################################################################
##############################################################################
#
# You can visualize the output of GOMC in VMD by following command
# To visualize the liquid phase, run the following command:

vmd mC6cycle_GEMC_T_480K_merged.psf mC6cycle_GEMC_T_480K_BOX_0.pdb &

# To visualize the change in the volume, select "Tk Console" under 
# "Extensions" tab. 
# 1- Type the following command in VMD TKConsole to draw a box.

  pbc box

# 2- Close the VMD TKConsole.
# 3- To visualize the simulation trajectories, on the right lower corner of 
#    VMD Main window, adjust the speed and click the play button.
# 4- Close the vmd application from VMD main window.


# To visualize the vapor phase, run the following command:

vmd mC6cycle_GEMC_T_480K_merged.psf mC6cycle_GEMC_T_480K_BOX_1.pdb &

# You can follow the same steps to visualize the simulation trajectories.

