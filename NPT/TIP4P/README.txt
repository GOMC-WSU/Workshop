###############################################################################
# To run the NPT simulation for TIP4P water, First we need to equilibrate the 
# system for 200,000 MC steps using NVT simulation. 
# Change your directory to "TIP4P_EQ" by following command:

cd TIP4P_EQ/.

# Run the GOMC simulation in NVT for 200,000 MC steps to equilibrate the system
# Assuming that GOMC base directory was cloned in your Desktop:

~/Desktop/GOMC/bin/GOMC_CPU_NVT +p4 water_TIP4P.conf > output_water.log &

# You can monitor the simulation by running the following command: 

tail -f output_water.log

# Wait until simulation finished, then exit command by typing "ctrl C"

###############################################################################
# Production simulation.
# Change your directory to "TIP4P_300_00K_PR/" directory to run the production
# simulation by following command:

cd ../TIP4P_300_00K_PR/.
 
# Run the GOMC simulation in NPT for 1 million steps from equilibrated system.
# Assuming that GOMC base directory was cloned in your Desktop:

~/Desktop/GOMC/bin/GOMC_CPU_NPT +p4 water_TIP4P.conf > output_water.log &

# Or if you have CUDA installed in your machine use the following command:

~/Desktop/GOMC/bin/GOMC_GPU_NPT water_TIP4P.conf > output_water.log &

# You can monitor the simulation by running the following command: 

tail -f output_water.log

# Wait until simulation finished, then exit command by typing "ctrl C"

###############################################################################
# To generate the RDF, we use vmd to calculate the RDF. Load the GOMC output 
# PDB and PSF file into vmd.

vmd TIP4P_Production_merged.psf  TIP4P_Production_BOX_0.pdb &

# Under "Extensions" tab, select "Analysis", the click on 
# "Radial Pair Distribution Function g(r)". Follow the steps on opened window
# 1- To select the file, click on "(none)" and select 
#    "0 TIP4P_Production_merged.psf".
# 2- Select the residue name that you want to calculate RDF. Type "type OH" 
#    in Selection 1 and Selection 2.
# 3- Check mark on "Save to File".
# 4- Click the "Compute g(r)" button to plot and save the g(r).
# 5- Click the "Save" button on the open window.
# 6- Close the vmd application from VMD main window.

# To extract the total energy and steps number use the following command:

cat Blk_TIP4P_Production_BOX_0.dat | awk '{print $1 " " $2}' > energy.dat

# To extract the density and steps number use the following command:

cat Blk_TIP4P_Production_BOX_0.dat | awk '{print $1 " " $11}' > density.dat

