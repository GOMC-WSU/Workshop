# Our goal is to add new adsorbate (CO2) to HTS. To do that, we need to
# 1. Add CO2 topology to BUILD/molel/Top_adsorbate.inp
# 2. Add CO2 force field parameters to “BUILD/molel/Parameters_Universal.par”
# for this example, we already added this file.

##############################################################################
# Create the simulation files for CO2 adsorption in IRMOF-1, using "simulation_setup.py"
# script for python 3

python ./simulation_setup.py

# Change your directory to the first adsorption simulation in 1 bar

cd run_files/EDUSIF/RUN1-FUGACITY-1.0-TEMPERATURE-298/

##############################################################################
# 1:
# Run the GOMC in GCMC simulation for 1 million steps.
# Assuming that GOMC binary is added to the path:

GOMC_CPU_GCMC +p1 in.conf > output_CO2.log &

# You can monitor the simulation by running the following command: 

tail -f output_CO2.log

# Wait until simulation finished, then exit command by typing "ctrl C"

##############################################################################
# 2:
# To extract statistical properties, we can use 'awk' command.
# This command extracts the average number of CO2 molecules in the system.

cat Blk_CO2_EDUSIF_*_BOX_0.dat | awk '{print $1, $10*$13}' > mol_CO2_avg.dat

# The instantaneous number of CO2 molecules can be extracted via:

cat output_CO2.log | awk '/STAT_0/ {print $2, $3*$5}' > mol_CO2_fluct.dat

# Plot these data using xmgrace and compare them with histogram data gnerated by
# GOMC (n2dis1a.dat)

xmgrace n2dis1a.dat &
xmgrace mol_CO2_avg.dat mol_CO2_fluct.dat &

##############################################################################
# 3:
# You can visualize the output of GOMC in VMD by following command
# To visualize the simulation, run the following command:

vmd CO2_EDUSIF_*_merged.psf CO2_EDUSIF_*_BOX_0.pdb &

# Open TkConsole window from Extensions/Tk Console
# Execute the following command in TkConsole to draw the simulation box and wrap 
# the adsorbent

pbc box
pbc wrap -sel "resname EDUS" -all

##############################################################################
# Change your directory to the second adsorption simulation in 10 bar

cd ../RUN2-FUGACITY-10.0-TEMPERATURE-298/

# Repeat the Steps 1, 2, and 3.
