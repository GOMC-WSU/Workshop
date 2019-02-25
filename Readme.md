# High Throughput Screening (MOFs):

1. Copy the compiled GOMC_CPU_GCMC executable file to "./BUILD/resources/sim/" directory.
2. Copy the compiled packmol executable file to "./BUILD/resources/pack/" directory.
3. Modified the job scrip according to your job scheduler.
4. If you are simulating adsorption of a molecule other than Noble gases, you need to
    1. Include the single molecule pdb file to "./BUILD/resources/pdb/" directory.
    2. Update the topology file in "./BUILD/resources/model" directory.
    3. Update the parameter file in "./BUILD/resources/model" directory.
5. Configure the simulation parameter by editing the "./BUILD/ConfigSetup.xml" file.
    1. To Perform High Throughput Screening, set the "HTS" True
    2. To Perform single MOF simulation, set the "HTS" False 
    3. If eletrostatic is turned off, it uses the cif file in "/BUILD/resources/CoRE-MOF-1.0-DFT-Minimized/minimized_structures"
    4. If eletrostatic is turned on, it uses the cif file in "/BUILD/resources/CoRE-MOF-1.0-DFT-Minimized/minimized_structures_with_DDEC_charges" 
6. Execute the "python ./simulation_setup.py" in your terminal to generate the simulation files for MOFs.
7. If you observed Error in the terminal, inspect the "build.log" file in common sub-directory.

