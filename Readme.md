# High Throughput Screening (MOFs):

1. Copy the compiled GOMC_CPU_GCMC executable file to "./BUILD/resources/sim/" directory.
2. Copy the compiled packmol executable file to "./BUILD/resources/pack/" directory.
3. Modified the job scrip according to your job scheduler.
4. If you are simulating adsorption of a molecule other than Noble gases, you need to include the single molecule pdb file to "./BUILD/resources/pdb/" directory.
5. If you are simulating adsorption of a molecule other than Noble gases, you need to update the topology file in "./BUILD/resources/model" directory.
6. If you are simulating adsorption of a molecule other than Noble gases, you need to update the parameter file in "./BUILD/resources/model" directory.
7. If you are simulating adsorption of a polar molecule, currently partial charges are not read from cif files. You need to modify the topology file define partial charges on each atom. 
8. Configure the simulation parameter by editing the "./BUILD/ConfigSetup.xml" file.
9. Execute the "python ./simulation_setup.py" in your terminal to generate the simulation files for MOFs.

