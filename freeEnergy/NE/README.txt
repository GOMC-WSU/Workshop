# Calculating solvation free energy of Ne in cyclohexane 
# Performin NVT simulation for 4 intermediate states
 
##############################################################################
# 1:
# Change your directory to state_0

cd states/state_0/

# Run the NVT simulation for 1 million steps in intermediate state_0
# Assuming that GOMC binary is added to the path:

GOMC_CPU_NVT +p1 prod.conf > output_state_0.log &

# You can monitor the simulation by running the following command: 

tail -f output_state_0.log

# Wait until simulation finished, then exit by command "ctrl c"
 
##############################################################################
# 2:
# Change your directory to state_1

cd ../state_1/

# Run the NVT simulation for 1 million steps in intermediate state_1
# Assuming that GOMC binary is added to the path:

GOMC_CPU_NVT +p1 prod.conf > output_state_1.log &

# You can monitor the simulation by running the following command: 

tail -f output_state_1.log

# Wait until simulation finished, then exit by command "ctrl c"
 
##############################################################################
# 3:
# Change your directory to state_2

cd ../state_2/

# Run the NVT simulation for 1 million steps in intermediate state_2
# Assuming that GOMC binary is added to the path:

GOMC_CPU_NVT +p1 prod.conf > output_state_2.log &

# You can monitor the simulation by running the following command: 

tail -f output_state_2.log

# Wait until simulation finished, then exit by command "ctrl c"
 
##############################################################################
# 4:
# Change your directory to state_3

cd ../state_3/

# Run the NVT simulation for 1 million steps in intermediate state_3
# Assuming that GOMC binary is added to the path:

GOMC_CPU_NVT +p1 prod.conf > output_state_3.log &

# You can monitor the simulation by running the following command: 

tail -f output_state_3.log

# Wait until simulation finished, then exit by command "ctrl c"
 
##############################################################################
# 5:
# Processing the GOMC output to calculate the solvation free energy using TI
# BAR, and MBAR estimators implemented in alchemlyb and alchemical_analysis
# python tools

# Change your directory to result

cd ../../result

# Copy the free energy files into "data" direcotry

cp  ../states/state*/Free_Energy_BOX_0_PRODUCTION_*.dat ./data/.

# Calculate the solvation free energy with alchemlyb using python3

python3.7 ./free_energy_calc.py

# Calculate the solvation free energy with alchemical-analysis using python2

alchemical_analysis -a gomc -d data -p Free_Energy_BOX_0_PRODUCTION_ -q dat -g True -w True -f 10 -u 'kcal' -o plots -m '-ti_cubic-DEXP-IEXP'

# Visualize the results in "plots" directory
