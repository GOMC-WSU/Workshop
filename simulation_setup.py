# coding: utf-8 #
import os
import sys
import xml.etree.ElementTree as et
import shutil
import re
import math
import glob
import fnmatch

base_directory = os.path.dirname(os.path.realpath(__file__))
config_file = base_directory + '/BUILD/ConfigSetup.xml'

def replace_text(filename, text_to_search, replacement_text):
    '''This function will replace <text_to_search> text with
    <replacement_text> string in <filename>'''
    with open(filename, 'r') as file:
        filedata = file.read()
    filedata = filedata.replace(text_to_search, replacement_text)
    with open(filename, 'w') as file:
        file.write(filedata)

def FindParameter(filename, keyword):
    with open(filename, 'r') as file:
        for line in file:
            if line.startswith(keyword):
                line = re.sub(' +', ' ', line).strip()
                return line.split(' ')[1]

# clean all files except the file pattern
def CleanDir(filepattern):
    for file in os.listdir('.'):
        if not fnmatch.fnmatch(file, filepattern):
            os.remove(file)

# Read input file and initialize variables
print("================================================================================")
print("*** Reading XML file ***")
e = et.parse(config_file).getroot()
mof_file = e.find('mof').find('file').text
mof_name = mof_file.split('_')[0]
supercelldim_x = float(e.find('supercelldim').find('x').text)
supercelldim_y = float(e.find('supercelldim').find('y').text)
supercelldim_z = float(e.find('supercelldim').find('z').text)
adsorbate_name = e.find('adsorbate').find('name').text
adsorbate_file = adsorbate_name + '.pdb'
adsorbate_resname = e.find('adsorbate').find('resname').text
reservoir_dim = e.find('reservoir').find('dim').text
reservoir_number = e.find('reservoir').find('number').text
model = e.find('model').text
runsteps = e.find('steps').find('runsteps').text
coordfreq = e.find('steps').find('coordfreq').text
blockfreq = e.find('steps').find('blockfreq').text
eq_steps = e.find('steps').find('eqsteps').text
rcut = e.find('rcut').text
lrc = e.find('lrc').text
electrostatic = e.find('electrostatic').text
tolerance = e.find('tolerance').text
runs = []
for run in e.find('runs').findall('run'):
    run_id = run.find('id').text
    run_fugacity = run.find('fugacity').text
    run_temperature = run.find('temperature').text
    dic = {'id': run_id, 'fugacity': run_fugacity, 'temperature': run_temperature}
    runs.append(dic)

if electrostatic == 'True':
    mof_path = base_directory + '/BUILD/resources/CoRE-MOF-1.0-DFT-Minimized/minimized_structures_with_DDEC_charges/' + mof_file
    top_model_input = "Top_" + model + "charges.inp"
elif electrostatic == 'False':
    mof_path = base_directory + '/BUILD/resources/CoRE-MOF-1.0-DFT-Minimized/minimized_structures/' + mof_file
    top_model_input = "Top_" + model + ".inp"
else:
    print("ERROR: ELECTROSTATIC INPUT INVALID")
    print("EXITING...")
    sys.exit(-1)
if not os.path.isfile(mof_path):
    print("ERROR: MOF file not found.")
    print("MOF File: " + mof_file)
    sys.exit(-1)

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
if not os.path.isdir('reservoir'):
    os.mkdir("reservoir")
os.chdir('MOF_base')

# Copy MOF cif file into MOF_base directory
shutil.copyfile(mof_path, "./" + mof_file)

# Generate Cell Basis Vectors
cell_length_a = float(FindParameter(mof_file, '_cell_length_a'))
cell_length_b = float(FindParameter(mof_file, '_cell_length_b'))
cell_length_c = float(FindParameter(mof_file, '_cell_length_c'))
cell_angle_alpha = float(FindParameter(mof_file, '_cell_angle_alpha')) / 180
cell_angle_beta = float(FindParameter(mof_file, '_cell_angle_beta')) / 180
cell_angle_gamma = float(FindParameter(mof_file, '_cell_angle_gamma')) / 180
alpha = cell_angle_alpha * math.pi
beta = cell_angle_beta * math.pi
gamma = cell_angle_gamma * math.pi

ax = cell_length_a * supercelldim_x
ay = 0
az = 0
bx = cell_length_b * math.cos(gamma) * supercelldim_y
by = cell_length_b * math.sin(gamma) * supercelldim_y
bz = 0
cx = cell_length_c * math.cos(beta) * supercelldim_z
cy_base = (math.cos(alpha)-math.cos(beta)*math.cos(gamma))/math.sin(gamma)
cy = cell_length_c * ((math.cos(alpha)-math.cos(beta)*math.cos(gamma))/math.sin(gamma))*supercelldim_z
cz = cell_length_c * (math.sqrt(math.sin(beta)**2-cy_base**2))*supercelldim_z

box_0_vector1 = "%.6f %.6f %.6f" % (ax, ay, az)
box_0_vector2 = "%.6f %.6f %.6f" % (bx, by, bz)
box_0_vector3 = "%.6f %.6f %.6f" % (cx, cy, cz)

print("*** PARAMETERS SUMMARY ***")
print("MOF_NAME: " + mof_name)
print("ADSORBATE_NAME: " + adsorbate_name)
print("MODEL: " + model)
print("RUNSTEPS: " + runsteps)
print("BLOCKFREQ: " + blockfreq)
print("LRC: " + lrc)
print("RCUT: " + rcut)
print("ELECTROSTATIC: " + electrostatic)
print("TOLERANCE: " + tolerance)
print("RESERVOIR_DIM: " + reservoir_dim)
print("RESERVOIR_NUMBER: " + reservoir_number)
print("SUPERCELL_EXPANSION_FACTOR: %d x %d x %d" % (supercelldim_x, supercelldim_y, supercelldim_z))
print("CELL BASIS VECTOR 0: " + box_0_vector1)
print("CELL BASIS VECTOR 1: " + box_0_vector2)
print("CELL BASIS VECTOR 2: " + box_0_vector3)
print("================================================================================")

# Create MOF Base
print("1.  Creating MOF base")
shutil.copyfile(base_directory + "/BUILD/resources/pack/extend_unit_cell.py", "./extend_unit_cell.py")
shutil.copyfile(base_directory + "/BUILD/resources/pack/convert_Pymatgen_PDB.tcl", "./convert_Pymatgen_PDB.tcl")
shutil.copyfile(base_directory + "/BUILD/resources/pack/build_psf_box_0.tcl", "./build_psf_box_0.tcl")
shutil.copyfile(base_directory + "/BUILD/resources/pack/setBeta.tcl", "./setBeta.tcl")
shutil.copyfile(base_directory + "/BUILD/resources/model/" + top_model_input, "./" + top_model_input)
replace_text("extend_unit_cell.py", 'FILEFILE', mof_file)
replace_text("extend_unit_cell.py", 'MOFNAME', mof_name)
replace_text("extend_unit_cell.py", 'XXX', str(supercelldim_x))
replace_text("extend_unit_cell.py", 'YYY', str(supercelldim_y))
replace_text("extend_unit_cell.py", 'ZZZ', str(supercelldim_z))
replace_text("build_psf_box_0.tcl", 'FILEFILE', mof_name)
replace_text('build_psf_box_0.tcl', 'MOFNAME', mof_name)
replace_text('build_psf_box_0.tcl', 'BASEDIR', base_directory)
replace_text('build_psf_box_0.tcl', 'TOPFILENAME', top_model_input)
replace_text('setBeta.tcl', 'MOFNAME', mof_name)
replace_text('convert_Pymatgen_PDB.tcl', 'MOFNAME', mof_name)

print("1.1 Building PDB and PSF files for MOF:")
os.system('python extend_unit_cell.py' + '> build.log 2>&1')

if os.path.isfile(mof_name + "_clean_min.pdb"):
    print("1.2 Unit cell extended, proceeding to next step")
else:
    print("1.2 ERROR: error generating supercell, check extend_unit_cell.py file.") 
    print("    Check if Pymatgen and Openbabel are installed correctly.")
    sys.exit(-1)

os.system("vmd -dispdev text < convert_Pymatgen_PDB.tcl" + '> build.log 2>&1')
if len(glob.glob("*_modified.pdb")) != 0:
    print("1.3 PDB file modification complete, proceeding to next step")
else:
    print("1.3 ERROR: error in generating pdb file after running Pymatgen")
    sys.exit(-1)

os.system("vmd -dispdev text < build_psf_box_0.tcl" + '> build.log 2>&1')
os.system("vmd -dispdev text < setBeta.tcl" + '> build.log 2>&1')
if len(glob.glob(mof_name + "_BOX_0.psf")) != 0:
    print("1.4 MOF PSF and PDB files generated; proceeding to next step")
else:
    print("1.4 ERROR: Generating MOF psf file was unsuccessful, exiting...")
    sys.exit(-1)

print("1.5 Cleaning MOF-base directory")
CleanDir(mof_name + "_BOX*")

print(" ")
print("2.  Generating reservoir files.")

# Create Reservoir Base
os.chdir('../reservoir')
shutil.copyfile(base_directory + '/BUILD/resources/pdb/' + adsorbate_file, './' + adsorbate_file)
shutil.copyfile(base_directory + '/BUILD/resources/pack/pack_box_1.inp', './pack_box_1.inp')
shutil.copyfile(base_directory + '/BUILD/resources/pack/build_psf_box_1.tcl', './build_psf_box_1.tcl')

replace_text('pack_box_1.inp', 'ADSBNAME', adsorbate_name)
replace_text('pack_box_1.inp', 'BASEDIR', base_directory)
replace_text('pack_box_1.inp', 'DDD0', reservoir_dim)
replace_text('pack_box_1.inp', 'RESVNUM', reservoir_number)
replace_text('build_psf_box_1.tcl', 'BASEDIR', base_directory)
replace_text('build_psf_box_1.tcl', 'ADSBSET', adsorbate_resname)
replace_text('build_psf_box_1.tcl', 'ADSBNAME', adsorbate_name)
replace_text('build_psf_box_1.tcl', 'TOPFILENAME', top_model_input)

print("2.1 Packing reservoir box.")
os.system("packmol < pack_box_1.inp" + '> build.log 2>&1')
if len(glob.glob("packed_*")) != 0:
    print("2.1 Reservoir packed succesfully, proceeding...")
else:
    print("2.1 ERROR: Packing reservoir unsuccesful, exiting...")
    sys.exit(-1)

print("2.2 Building pdb and psf file for reservoir box.")
os.system("vmd -dispdev text < build_psf_box_1.tcl" + '> build.log 2>&1')
if len(glob.glob("*.psf")) != 0:
    print("2.2 Reservoir psf and pdb files generated succesfully")
else:
    print("2.2 ERROR: psf generation for reservoir unsuccesful, exiting...")
    sys.exit(-1)

print("2.3 Cleaning reservoir directory")
CleanDir("START_BOX_1*")

print("*** MOF PDB and PSF input files succesfully built ***")
print(" ")
print("3.  Setting control file.")

os.chdir("../")
par_file = "Parameters_" + model + ".par"
shutil.copyfile(base_directory + "/BUILD/resources/model/" + par_file, "./" + par_file)
shutil.copyfile(base_directory + "/BUILD/resources/sim/in.conf", "./in.conf")
replace_text("in.conf", "BASEDIR", base_directory)
replace_text("in.conf", "ADSBNAME", adsorbate_name)
replace_text("in.conf", "MOFNAME", mof_name)
replace_text("in.conf", "RCUTSET", rcut)
replace_text("in.conf", "LRCSET", lrc)
replace_text("in.conf", "TOLESET", tolerance)
replace_text("in.conf", "FFIELD", model)
replace_text("in.conf", "ELECTSET", electrostatic)
replace_text("in.conf", "RUNSTEPSET", runsteps)
replace_text("in.conf", "DDD0", reservoir_dim)
replace_text("in.conf", "DDD1", box_0_vector1)
replace_text("in.conf", "DDD2", box_0_vector2)
replace_text("in.conf", "DDD3", box_0_vector3)
replace_text("in.conf", "ADSBSET", adsorbate_resname)
replace_text("in.conf", "COORDSTEPS", coordfreq)
replace_text("in.conf", "CONSSTEPS", blockfreq)
replace_text("in.conf", "EQSTEPSET", eq_steps)

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
    replace_text("gcmc_cluster.cmd", "RUN-DIR", directory)
    replace_text("gcmc_cluster.cmd", "MOFNAME", mof_name)
    replace_text("gcmc_cluster.cmd", "ADSBNAME", adsorbate_name)
    replace_text("gcmc_cluster.cmd", "FFF", run['fugacity'])
    replace_text("in.conf", "TEMPSET", run['temperature'])
    replace_text("in.conf", "FFF", run['fugacity'])
    os.chdir('../')

# delete in.conf after finished copying
os.remove("./common/in.conf")
print("END: Run directories have been built")
print("================================================================================")

