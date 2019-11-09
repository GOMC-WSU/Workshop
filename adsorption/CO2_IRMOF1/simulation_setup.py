# coding: utf-8 #
import os
import sys
import xml.etree.ElementTree as et
import shutil
import glob
import fnmatch

#import from utility directory
base_directory = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(base_directory +"/BUILD/utility/"))
import top_generator as topGen
import utility_functions as uf 
import extend_unit_cell as euc
import config_builder  as cb


config_file = base_directory + '/ConfigSetup.xml'
top_file_adsorbent = "Top_adsorbent.inp"
top_file_adsorbate = "Top_adsorbate.inp"

# Read input file and initialize variables
print("================================================================================")
print("*** Reading XML file ***")
conf = cb.ConfigBuilder(config_file)
print("*** Finished Reading XML file ***")

if conf.HasElect():
    mof_dir = base_directory + '/BUILD/CoRE-MOFs/core-mof-v1.0-ddec/'
else:
    mof_dir = base_directory + '/BUILD/CoRE-MOFs/core-mof-v1.0/'

# Loop through all MOFs and create simulation files
allFiles = []
if(conf.sys.build_all):
    allFiles = os.listdir(mof_dir)
    print("*** Building all MOFs ***")
else:
    allFiles.append(conf.sys.mof_file)
    print("*** Building single MOF ***")

for cifFile in allFiles:
    if not fnmatch.fnmatch(cifFile, '*.cif'):
        print('WARNING: Ignoring file ' + cifFile)
        continue
    
    mof_file = cifFile
    mof_name = mof_file.split('_')[0]
    mof_path = mof_dir + mof_file

    print("*** PARAMETERS SUMMARY ***")
    conf.Print_summary(mof_name)

    # Create Build Directories
    print("*** Working on MOF: " + mof_name + " ***")
    uf.MakeDir("run_files")
    os.chdir("run_files")
    uf.MakeDir(mof_name)
    os.chdir(mof_name)
    uf.MakeDir("common")
    os.chdir("common")
    uf.MakeDir("MOF_base")
    uf.MakeDir("reservoir_base")
    os.chdir("MOF_base")

    # Copy MOF cif file into MOF_base directory and set up the cell basis info and extension using
    # maximum(rcut and rcutcoulomb)
    print("Reading cell basis information in " + mof_file)
    uf.Copy(mof_path, "./" + mof_file)
    mof_cellBasis = euc.MOF_Data(mof_file, mof_name, conf.GetRcut())
    conf.Print_cellData(mof_cellBasis)

    # Create MOF Base
    print("\n1.  Building MOF files")
    uf.Copy(base_directory + "/BUILD/pack/convert_XYZ_PDB.tcl", "./convert_XYZ_PDB.tcl")
    uf.Copy(base_directory + "/BUILD/model/" + top_file_adsorbent, "./" + top_file_adsorbent)
    #Prepare the Tcl script
    uf.replace_text('convert_XYZ_PDB.tcl', 'MOFNAME', mof_name)
    uf.replace_text('convert_XYZ_PDB.tcl', 'TOPFILENAME', top_file_adsorbent)

    print("\t1. Extending unit cell and generating Topology and XYZ file for MOF.")
    mof_cellBasis.WriteXYZ(top_file_adsorbent)
    if os.path.isfile(mof_name + ".xyz"):
        print("\t2. Unit cell extended and XYZ file generated successfully.")
    else:
        print("\t2. ERROR: error generating supercell XYZ file.") 
        sys.exit(-1)

    print("\t3. Converting XYZ file to PDB and PSF for MOF.")
    os.system("vmd -dispdev text < convert_XYZ_PDB.tcl" + '>> build_error.log 2>&1')
    if len(glob.glob(mof_name + "_BOX_0.pdb")) != 0:
        print("\t4. MOF PDB file generated successfully.")
    elif len(glob.glob(mof_name + "_BOX_0.psf")) != 0:
        print("\t4. MOF PSF file generated successfully.")
    else:
        print("\t4. ERROR: In generating MOF PSF file in convert_XYZ_PDB.tcl file.")
        sys.exit(-1)

    print("\t5. Cleaning MOF-base directory")
    uf.CleanDir(mof_name + "_BOX*")

    print("\n2.  Generating reservoir files.")
    # Create Reservoir Base
    os.chdir('../reservoir_base')
    uf.Copy(base_directory + '/BUILD/pack/pack_box_1.inp', './pack_box_1.inp')
    uf.Copy(base_directory + '/BUILD/pack/packmol', './packmol')
    uf.Copy(base_directory + '/BUILD/pack/build_psf_box_1.tcl', './build_psf_box_1.tcl')
    uf.Copy(base_directory + "/BUILD/model/" + top_file_adsorbate, "./" + top_file_adsorbate)
    uf.Copy(base_directory + '/BUILD/pdb/' + conf.sys.adsorbate_pdb, './' + conf.sys.adsorbate_pdb)
    # give executable permission
    os.chmod('packmol', 509)

    uf.replace_text('pack_box_1.inp', 'ADSBNAME', conf.sys.adsorbate_name)
    uf.replace_text('pack_box_1.inp', 'DDD0', conf.sys.reservoir_dim)
    uf.replace_text('pack_box_1.inp', 'RESVNUM', conf.sys.reservoir_number)
    uf.replace_text('build_psf_box_1.tcl', 'BASEDIR', base_directory)
    uf.replace_text('build_psf_box_1.tcl', 'ADSBSET', conf.sys.adsorbate_resname)
    uf.replace_text('build_psf_box_1.tcl', 'ADSBNAME', conf.sys.adsorbate_name)
    uf.replace_text('build_psf_box_1.tcl', 'TOPFILENAME', top_file_adsorbate)

    print("\t1. Packing reservoir box.")
    os.system("packmol < pack_box_1.inp" + '>> build_error.log 2>&1')
    if len(glob.glob("packed_*")) != 0:
        print("\t2. Reservoir packed succesfully.")
    else:
        print("\t2. ERROR: Packing reservoir was unsuccesful.")
        sys.exit(-1)

    print("\t3. Building PDB and PSF file for reservoir box.")
    os.system("vmd -dispdev text < build_psf_box_1.tcl" + '>> build_error.log 2>&1')
    if len(glob.glob("*.psf")) != 0:
        print("\t4. Reservoir PDB and PSF files generated succesfully.")
    else:
        print("\t4. ERROR: PSF generation for reservoir was unsuccesful.")
        sys.exit(-1)

    print("\t5. Cleaning reservoir directory.")
    uf.CleanDir("START_BOX_1*")

    print("\n*** ALL PDB and PSF input files succesfully built ***\n")
    print("3.  Setting control file.")

    # we are in the common directory
    os.chdir("../")
    uf.Copy(base_directory + "/BUILD/model/" + conf.sys.par_file, "./" + conf.sys.par_file)
    if conf.HasElect():
        shutil.copyfile(base_directory + "/BUILD/sim/elect.conf", "./in.conf")  
    else:
        shutil.copyfile(base_directory + "/BUILD/sim/noElect.conf", "./in.conf")

    conf.Write_SimData("in.conf")
    print("\n4.  Creating run directory for " + mof_name)
    # Generating runs for each fugacity
    os.chdir('../')
    print("\t1. Total number of runs: " + str(len(conf.runSim.runSimData)))
    for i in range(len(conf.runSim.runSimData)):
        to_print = conf.runSim.Summary_Str(i)
        print('\t\tBuilding ' + to_print)
        uf.MakeDir(to_print)
        os.chdir(to_print)

        dir = os.getcwd()
        uf.Copy('../common/in.conf', './in.conf')
        uf.Copy(base_directory +'/BUILD/sim/gcmc_cluster.cmd', './gcmc_cluster.cmd')
        uf.Copy(base_directory +'/BUILD/sim/GOMC_CPU_GCMC', './GOMC_CPU_GCMC')
        conf.Write_runData("in.conf", i, dir + to_print)
        shutil.move('./gcmc_cluster.cmd', './' + to_print + '.sh')
        # give executable permission
        os.chmod('GOMC_CPU_GCMC', 509)
        os.chdir('../')

    # delete in.conf and list of residue after finished copying
    os.remove("./common/in.conf")
    print("END: Run directories have been built")
    print("================================================================================")
    os.chdir(base_directory)
