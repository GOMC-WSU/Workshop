###############################################################################
# To run the NPT simulation for SPCE water, First we need to equilibrate the 
# system for 200,000 MC steps using NVT simulation. 
# Change your directory to "Equilibration" by following command:

cd Equilibration/.

# Run the GOMC simulation in NVT for 200,000 MC steps to equilibrate the system
# Assuming that GOMC binary is added to the path:

GOMC_CPU_NVT +p1 eq.conf > output_water.log &

# You can monitor the simulation by running the following command: 

tail -f output_water.log

# Wait until simulation finished, then exit command by typing "ctrl C"

###############################################################################
# Production simulation.
# Change your directory to "Production" directory to run the production
# simulation by following command:

cd ../Production/.
 
# Run the GOMC simulation in NPT for 500,000 MC steps from equilibrated system.
# Assuming that GOMC binary is added to the path:

GOMC_CPU_NPT +p1 prod.conf > output_water.log &

# You can monitor the simulation by running the following command: 

tail -f output_water.log

# Wait until simulation finished, then exit command by typing "ctrl C"

###############################################################################
# vmd can be used to calculate the RDF. Load the GOMC output 
# PDB and PSF file into vmd.

vmd SPCE_Production_merged.psf  SPCE_Production_BOX_0.pdb &

# Under "Extensions" tab, select "Analysis", the click on 
# "Radial Pair Distribution Function g(r)". Follow the steps on opened window
# 1- To select the file, click on "(none)" and select 
#    "0 SPCE_Production_merged.psf".
# 2- Select the residue name that you want to calculate RDF. Type "type OT" 
#    in Selection 1 and Selection 2.
# 3- Check mark on "Save to File".
# 4- Click the "Compute g(r)" button to plot and save the g(r).
# 5- Click the "Save" button on the open window.
# 6- Close the vmd application from VMD main window.

# to extract the instantaneous fluctuations in the energy
cat output_water.log  | awk '/ENER_0/ {print $2, $3}' > energy_fluct.dat

# to extract the instantaneous fluctuations in the energy
cat output_water.log  | awk '/STAT_0/ {print $2, $5}' > density_fluct.dat

# To extract the average total energy and steps number use the following command:

cat Blk_SPCE_Production_BOX_0.dat | awk '{print $1, $2}' > energy.dat

# To extract the average density and steps number use the following command:

cat Blk_SPCE_Production_BOX_0.dat | awk '{print $1, $11}' > density.dat

