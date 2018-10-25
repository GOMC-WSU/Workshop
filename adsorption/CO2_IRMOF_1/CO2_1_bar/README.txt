# Run the GOMC simulation in GCMC for 2 million steps.
# Assuming that GOMC binary is added to the path:

GOMC_CPU_GCMC +p1 carbondioxide_GCMC.conf > output_CO2.log &

# You can monitor the simulation by running the following command: 

tail -f output_CO2.log

# Wait until simulation finished, then exit command by typing "ctrl C"

##############################################################################
#
# To extract statistical properties, we can use 'awk' command.
# This command extracts the average number of CO2 molecules in the system.

cat Blk_CO2_IRMOF_1_BOX_0.dat | awk '{print $1, $10 * $19}' > mol_CO2.dat

# The instantaneous number of CO2 molecules can be extracted via:
cat output_CO2.log | awk '/STAT_0/ {print $2, $3*$11}'>CO2_fluct.dat

##############################################################################
#
# You can visualize the output of GOMC in VMD by following command
# To visualize the simulation, run the following command:

vmd CO2_IRMOF_1_BOX_0.pdb &

