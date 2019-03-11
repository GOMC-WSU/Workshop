# coding: utf-8 #
import os
import sys
import xml.etree.ElementTree as et
import shutil
import re
import math
import glob
import fnmatch

#import from utility directory
base_directory = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(base_directory +"/BUILD/resources/utility/"))
import top_generator as topGen
import utility_functions as uf 
import extend_unit_cell as euc


config_file = base_directory + '/ConfigSetup.xml'
top_file_adsorbent = "Top_adsorbent.inp"
top_file_adsorbate = "Top_adsorbate.inp"

# Read input file and initialize variables
print("================================================================================")
print("*** Reading XML file ***")
e = et.parse(config_file).getroot()
build_all = e.find('HTS').text
mof_file = e.find('mofname').text
adsorbate_name = e.find('adsorbate').find('name').text
adsorbate_pdb = adsorbate_name + '.pdb'
adsorbate_resname = e.find('adsorbate').find('resname').text
reservoir_dim = e.find('reservoir').find('dim').text
reservoir_number = e.find('reservoir').find('number').text
model = e.find('model').text
runsteps = e.find('steps').find('runsteps').text
coordfreq = e.find('steps').find('coordfreq').text
blockfreq = e.find('steps').find('blockfreq').text
eq_steps = e.find('steps').find('eqsteps').text
rcut = e.find('rcut').text
rcutLow = e.find('rcutLow').text
lrc = e.find('lrc').text
electrostatic = e.find('electrostatic').text
rcutcoulomb = e.find('rcutCoulomb').text
tolerance = e.find('tolerance').text
cachedFourier = e.find('cachedFourier').text



runs = []
for run in e.find('runs').findall('run'):
    run_id = run.find('id').text
    run_fugacity = run.find('fugacity').text
    run_temperature = run.find('temperature').text
    dic = {'id': run_id, 'fugacity': run_fugacity, 'temperature': run_temperature}
    runs.append(dic)

if electrostatic.lower() == 'true':
    mof_dir = base_directory + '/BUILD/resources/CoRE-MOF-1.0-DFT-Minimized/minimized_structures_with_DDEC_charges/'
else:
    mof_dir = base_directory + '/BUILD/resources/CoRE-MOF-1.0-DFT-Minimized/minimized_structures/'
    rcutcoulomb = rcut


# Loop through all MOFs and create simulation files
allFiles = []
if(build_all.lower() == 'true'):
    allFiles = os.listdir(mof_dir)
    print("*** Building all MOFs ***")
elif(build_all.lower() == 'false'):
    allFiles.append(mof_file)
    print("*** Building single MOF ***")
else:
    print("ERROR: High throughput screening INPUT INVALID")
    print("EXITING...")
    sys.exit(-1)

for cifFile in allFiles:
    if not fnmatch.fnmatch(cifFile, '*.cif'):
        print('WARNING: Ignoring file ' + cifFile)
        continue
    
    mof_file = cifFile
    mof_name = mof_file.split('_')[0]
    mof_path = mof_dir + mof_file

    # Create Build Directories
    print("*** Working on MOF: " + mof_name + " ***")
    if not os.path.isdir('run_files'):
        os.mkdir("run_files")
    os.chdir("run_files")
    if not os.path.isdir(mof_name):
        os.mkdir(mof_name)
    os.chdir(mof_name)
    if not os.path.isdir('common'):
        os.mkdir("common")
    os.chdir("common")
    if not os.path.isdir('MOF_base'):
        os.mkdir("MOF_base")
    if not os.path.isdir('reservoir_base'):
        os.mkdir("reservoir_base")
    os.chdir('MOF_base')

    # Copy MOF cif file into MOF_base directory and set up the cell basis info and extension using
    # maximum(rcut and rcutcoulomb)
    print("Reading cell basis information in " + mof_file)
    shutil.copyfile(mof_path, "./" + mof_file)
    mof_cellBasis = euc.MOF_Data(mof_file, mof_name, max(rcut, rcutcoulomb))
    box_vector = mof_cellBasis.GetCellVector()
    box_0_vector1 = "{:8.4f} {:8.4f} {:8.4f} ".format(*box_vector[0])
    box_0_vector2 = "{:8.4f} {:8.4f} {:8.4f} ".format(*box_vector[1])
    box_0_vector3 = "{:8.4f} {:8.4f} {:8.4f} ".format(*box_vector[2])

    print("*** PARAMETERS SUMMARY ***")
    print("MOF_NAME: " + mof_name)
    print("ADSORBATE_NAME: " + adsorbate_name)
    print("MODEL: " + model)
    print("RUNSTEPS: " + runsteps)
    print("BLOCKFREQ: " + blockfreq)
    print("LRC: " + lrc)
    print("RCUT: " + rcut)
    print("RCUTLOW: " + rcutLow)
    print("RCUTCOULOMB: " + rcutcoulomb)
    print("ELECTROSTATIC: " + electrostatic)
    print("TOLERANCE: " + tolerance)
    print("RESERVOIR_DIM: " + reservoir_dim)
    print("RESERVOIR_NUMBER: " + reservoir_number)
    print("SUPERCELL_EXPANSION_FACTOR: {:d} x {:d} x {:d}".format(*mof_cellBasis.extend))
    print("CELL BASIS VECTOR 0: " + box_0_vector1)
    print("CELL BASIS VECTOR 1: " + box_0_vector2)
    print("CELL BASIS VECTOR 2: " + box_0_vector3)
    print("================================================================================")

    # Create MOF Base
    print("1.  Building MOF files")
    shutil.copyfile(base_directory + "/BUILD/resources/pack/convert_Pymatgen_PDB.tcl", "./convert_Pymatgen_PDB.tcl")
    shutil.copyfile(base_directory + "/BUILD/resources/pack/build_psf_box_0.tcl", "./build_psf_box_0.tcl")
    shutil.copyfile(base_directory + "/BUILD/resources/pack/setBeta.tcl", "./setBeta.tcl")
    shutil.copyfile(base_directory + "/BUILD/resources/model/" + top_file_adsorbent, "./" + top_file_adsorbent)

    uf.replace_text("build_psf_box_0.tcl", 'FILEFILE', mof_name)
    uf.replace_text('build_psf_box_0.tcl', 'MOFNAME', mof_name)
    uf.replace_text('build_psf_box_0.tcl', 'TOPFILENAME', top_file_adsorbent)
    uf.replace_text('setBeta.tcl', 'MOFNAME', mof_name)
    uf.replace_text('convert_Pymatgen_PDB.tcl', 'MOFNAME', mof_name)

    print("1.1 Generating Topology file for MOF.")
    topGen.MakeTopology(mof_file, top_file_adsorbent)

    print("1.2 Extending unit cell and generating XYZ file for MOF.")
    mof_cellBasis.WriteXYZ()

    if os.path.isfile(mof_name + "_clean_min.xyz"):
        print("1.3 Unit cell extended and XYZ file generated successfully.")
    else:
        print("1.3 ERROR: error generating supercell XYZ file.") 
        print("    Check if Pymatgen and Openbabel are installed correctly.")
        sys.exit(-1)

    print("1.4 Converting XYZ file to formatted PDB for MOF.")
    os.system("vmd -dispdev text < convert_Pymatgen_PDB.tcl" + '>> build_error.log 2>&1')
    if len(glob.glob("*_modified.pdb")) != 0:
        print("1.5 PDB file formatting completed successfully")
    else:
        print("1.5 ERROR: In generating formatted PDB file in convert_Pymatgen_PDB.tcl script.")
        sys.exit(-1)

    print("1.6 Generating PSF file for MOF.")
    os.system("vmd -dispdev text < build_psf_box_0.tcl" + '>> build_error.log 2>&1')
    os.system("vmd -dispdev text < setBeta.tcl" + '>> build_error.log 2>&1')
    if len(glob.glob(mof_name + "_BOX_0.psf")) != 0:
        print("1.7 MOF PSF and PDB files generated successfully.")
    else:
        print("1.7 ERROR: In generating MOF PSF file in build_psf_box_0.tcl file.")
        sys.exit(-1)

    print("1.8 Cleaning MOF-base directory")
    uf.CleanDir(mof_name + "_BOX*")

    print(" ")
    print("2.  Generating reservoir files.")

    # Create Reservoir Base
    os.chdir('../reservoir_base')
    shutil.copyfile(base_directory + '/BUILD/resources/pack/pack_box_1.inp', './pack_box_1.inp')
    shutil.copyfile(base_directory + '/BUILD/resources/pack/packmol', './packmol')
    shutil.copyfile(base_directory + '/BUILD/resources/pack/build_psf_box_1.tcl', './build_psf_box_1.tcl')
    shutil.copyfile(base_directory + "/BUILD/resources/model/" + top_file_adsorbate, "./" + top_file_adsorbate)
    shutil.copyfile(base_directory + '/BUILD/resources/pdb/' + adsorbate_pdb, './' + adsorbate_pdb)
    # give executable permission
    os.chmod('packmol', 509)

    uf.replace_text('pack_box_1.inp', 'ADSBNAME', adsorbate_name)
    uf.replace_text('pack_box_1.inp', 'DDD0', reservoir_dim)
    uf.replace_text('pack_box_1.inp', 'RESVNUM', reservoir_number)
    uf.replace_text('build_psf_box_1.tcl', 'BASEDIR', base_directory)
    uf.replace_text('build_psf_box_1.tcl', 'ADSBSET', adsorbate_resname)
    uf.replace_text('build_psf_box_1.tcl', 'ADSBNAME', adsorbate_name)
    uf.replace_text('build_psf_box_1.tcl', 'TOPFILENAME', top_file_adsorbate)

    print("2.1 Packing reservoir box.")
    os.system("./packmol < pack_box_1.inp" + '>> build_error.log 2>&1')
    if len(glob.glob("packed_*")) != 0:
        print("2.1 Reservoir packed succesfully.")
    else:
        print("2.1 ERROR: Packing reservoir was unsuccesful.")
        sys.exit(-1)

    print("2.2 Building PDB and PSF file for reservoir box.")
    os.system("vmd -dispdev text < build_psf_box_1.tcl" + '>> build_error.log 2>&1')
    if len(glob.glob("*.psf")) != 0:
        print("2.2 Reservoir PDB and PSF files generated succesfully.")
    else:
        print("2.2 ERROR: PSF generation for reservoir was unsuccesful.")
        sys.exit(-1)

    print("2.3 Cleaning reservoir directory.")
    uf.CleanDir("START_BOX_1*")

    print("*** ALL PDB and PSF input files succesfully built ***")
    print(" ")
    print("3.  Setting control file.")

    # we are in common directory
    os.chdir("../")
    par_file = "Parameters_" + model + ".par"
    shutil.copyfile(base_directory + "/BUILD/resources/model/" + par_file, "./" + par_file)
    if electrostatic.lower() == 'true':
        shutil.copyfile(base_directory + "/BUILD/resources/sim/elect.conf", "./in.conf")  
    else:
        shutil.copyfile(base_directory + "/BUILD/resources/sim/noElect.conf", "./in.conf")

    uf.replace_text("in.conf", "BASEDIR", base_directory)
    uf.replace_text("in.conf", "ADSBNAME", adsorbate_name)
    uf.replace_text("in.conf", "MOFNAME", mof_name)
    uf.replace_text("in.conf", "RCUTSET", rcut)
    uf.replace_text("in.conf", "RCUTLOWSET", rcutLow)
    uf.replace_text("in.conf", "LRCSET", lrc)
    uf.replace_text("in.conf", "TOLESET", tolerance)
    uf.replace_text("in.conf", "FFIELD", model)
    uf.replace_text("in.conf", "ELECTSET", electrostatic)
    uf.replace_text("in.conf", "RCUTCOULOMBSET", rcutcoulomb)
    uf.replace_text("in.conf", "CACHSET", cachedFourier)
    uf.replace_text("in.conf", "RUNSTEPSET", runsteps)
    uf.replace_text("in.conf", "DDD0", reservoir_dim)
    uf.replace_text("in.conf", "DDD1", box_0_vector1)
    uf.replace_text("in.conf", "DDD2", box_0_vector2)
    uf.replace_text("in.conf", "DDD3", box_0_vector3)
    uf.replace_text("in.conf", "ADSBSET", adsorbate_resname)
    uf.replace_text("in.conf", "COORDSTEPS", coordfreq)
    uf.replace_text("in.conf", "CONSSTEPS", blockfreq)
    uf.replace_text("in.conf", "EQSTEPSET", eq_steps)
    uf.replace_textWithFile("in.conf", "BASEFUGACITY", "fugacity.txt")

    print(" ")
    print("4.  Creating run directory for " + mof_name)

    # Generating runs for each fugacity
    os.chdir('../')
    print("4.1 Total number of runs: " + str(len(runs)))
    for run in runs:
        print('4.2 Building run files: T:' + run['temperature'] + ', fugacity: ' + run['fugacity'])
        current_dir = os.getcwd()
        directory = current_dir + '/run_' + run['fugacity']
        if not os.path.isdir(directory):
            os.mkdir(directory)
        os.chdir(directory)
        shutil.copyfile('../common/in.conf', './in.conf')
        shutil.copyfile(base_directory +'/BUILD/resources/sim/gcmc_cluster.cmd', './gcmc_cluster.cmd')
        shutil.copyfile(base_directory +'/BUILD/resources/sim/GOMC_CPU_GCMC', './GOMC_CPU_GCMC')
        uf.replace_text("gcmc_cluster.cmd", "RUN-DIR", directory)
        uf.replace_text("gcmc_cluster.cmd", "MOFNAME", mof_name)
        uf.replace_text("gcmc_cluster.cmd", "ADSBNAME", adsorbate_name)
        uf.replace_text("gcmc_cluster.cmd", "FFF", run['fugacity'])
        uf.replace_text("in.conf", "TEMPSET", run['temperature'])
        uf.replace_text("in.conf", "FFF", run['fugacity'])
        #change the jub script name
        jobName = mof_name + '_fugacity_' + run['fugacity'] + '_T_' + run['temperature'] + '.cmd'
        shutil.move('./gcmc_cluster.cmd', './' + jobName)
        # give executable permission
        os.chmod('GOMC_CPU_GCMC', 509)
        os.chdir('../')

    # delete in.conf and list of residue after finished copying
    os.remove("./common/in.conf")
    os.remove("./common/fugacity.txt")
    print("END: Run directories have been built")
    print("================================================================================")
    os.chdir(base_directory)
