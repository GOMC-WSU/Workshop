# High Throughput Screening (MOFs):

1. Install the packages that are explained in `GOMC_Software_Requirement` document.
2. Copy the compiled `GOMC_CPU_GCMC` executable file to `./BUILD/resources/sim/` directory.
3. Copy the compiled `packmol` executable file to `./BUILD/resources/pack/` directory.
4. Modified the job scrip according to your job scheduler `./BUILD/resources/sim/gcmc_cluster.cmd`.
5. If you are simulating adsorption of a molecule other than Noble gases, you need to:
    1. Include the single-molecule-pdb file to `./BUILD/resources/pdb/` directory.
    2. Update the topology files for the adsorbate molecule in `./BUILD/resources/model` directory.
    3. Update the parameter file for the adsorbate molecule in `./BUILD/resources/model` directory.
6. Configure the simulation parameter by editing the `./BUILD/ConfigSetup.xml` file.
    1. To Perform High Throughput Screening, set the `<HTS>True<\HTS>`
    2. To Perform single MOF simulation, set the `<HTS>False<\HTS>`
    3. If eletrostatic is turned off, it uses the cif files in `/BUILD/resources/CoRE-MOF-1.0-DFT-Minimized/minimized_structures`
    4. If eletrostatic is turned on, it uses the cif files in `/BUILD/resources/CoRE-MOF-1.0-DFT-Minimized/minimized_structures_with_DDEC_charges` 
7. Execute the following command in your terminal to generate the simulation files for MOFs. 
   ```bash
   $ python ./simulation_setup.py
   ```
8. If you observed Error in the terminal, inspect the `build_error.log` file in common sub-directory.


# IMPORTANT:
1. Inspect the parameter files in `./BUILD/resources/model` for accuracy of the bonded and non-bonded parameters.
2. Interaction between atomtype can be modified using  `NBFIX` for CHARMM style, or `NBFIX_MIE` for Mie        style parameter file. For more information, refere to [GOMC Documentation](http://gomc.eng.wayne.edu/manual/input_file.html#nbfix "GOMC non-bonded").
3. For assigning charges, this script uses the charge, provided in `*.cif` file. If you are intrested to use       different charge, you need to modify the charge value in `*.cif` file.
