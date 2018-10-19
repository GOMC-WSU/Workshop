# Run the GOMC simulation in GCMC for 2 million steps.
# Assuming that GOMC base directory was cloned in your home directory:

~/Code/GOMC/bin/GOMC_CPU_GCMC +p4 carbondioxide_GCMC.conf > output_CO2.log &

# You can monitor the simulation by running the following command: 

tail -f output_CO2.log

# Wait until simulation finished, then exit command by typing "ctrl C"

##############################################################################
#
# To extract statistical properties, we can use 'awk' command.
# This command extract and save the number of CO2 molecules.

cat Blk_CO2_IRMOF_1_BOX_0.dat | awk '{print $1, $10 * $19}' > mol_CO2.dat

##############################################################################
#
# You can visualize the output of GOMC in VMD by following command
# To visualize the argon adsorption, run the following command:

vmd CO2_IRMOF_1_BOX_0.pdb &

