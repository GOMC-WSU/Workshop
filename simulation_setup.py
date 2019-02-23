# coding: utf-8 #
import os
import sys
import xml.etree.ElementTree as et
import shutil
import re
import math
import glob

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

# Read input file and initialize variables
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
temperature = e.find('temperature').text
electrostatic = e.find('electrostatic').text
tolerance = e.find('tolerance').text
runs = []
for run in e.find('runs').findall('run'):
    run_id = run.find('id').text
    run_fugacity = run.find('fugacity').text
    dic = {'id': run_id, 'fugacity': run_fugacity}
    runs.append(dic)

if electrostatic == 'True':
    mof_path = base_directory + '/BUILD/resources/CoRE-MOF-1.0-DFT-Minimized/minimized_structures_with_DDEC_charges/' + mof_file
elif electrostatic == 'False':
    mof_path = base_directory + '/BUILD/resources/CoRE-MOF-1.0-DFT-Minimized/minimized_structures/' + mof_file
else:
    print("ERROR: ELECTROSTATIC INPUT INVALID")
    print("EXITING...")
    sys.exit(-1)
if not os.path.isfile(mof_path):
    print("ERROR: MOF file not found.")
    print("MOF File: " + mof_file)
    sys.exit(-1)

# Create Build Directories
print("Setting up directories")
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

print(" ")
print(" - READING SETUP PARAMETERS - ")
print("==========================================")
print("")
print("MOF_NAME: " + mof_name)
print("ADSORBATE_NAME: " + adsorbate_name)
print("ELECTROSTATIC: " + electrostatic)
print("TOLERANCE: " + tolerance)
print("LRC: " + lrc)
print("TEMPERATURE: " + temperature)
print("MODEL: " + model)
print("RESERVOIR_DIM: " + reservoir_dim)
print("RESERVOIR_NUMBER: " + reservoir_number)
print("RCUT: " + rcut)
print("RUNSTEPS: " + runsteps)
print("SUPERCELL_EXPANSION_FACTOR: %.6f %.6f %.6f" % (supercelldim_x, supercelldim_y, supercelldim_z))
print(" ")
print("Cell Basis Vectors:")
print(box_0_vector1)
print(box_0_vector2)
print(box_0_vector3)

# Create MOF Base
print("Creating MOF base")
shutil.copyfile(base_directory + "/BUILD/resources/pack/extend_unit_cell.py", "./extend_unit_cell.py")
shutil.copyfile(base_directory + "/BUILD/resources/pack/convert_Pymatgen_PDB.tcl", "./convert_Pymatgen_PDB.tcl")
shutil.copyfile(base_directory + "/BUILD/resources/pack/build_psf_box_0.tcl", "./build_psf_box_0.tcl")
shutil.copyfile(base_directory + "/BUILD/resources/pack/setBeta.tcl", "./setBeta.tcl")
top_model_input = "Top_" + model + ".inp"
shutil.copyfile(base_directory + "/BUILD/resources/model/" + top_model_input, "./" + top_model_input)
replace_text("extend_unit_cell.py", 'FILEFILE', mof_file)
replace_text("build_psf_box_0.tcl", 'FILEFILE', mof_file)
replace_text("extend_unit_cell.py", 'MMMMMM', mof_name)
replace_text("extend_unit_cell.py", 'CCC', str(supercelldim_x))
replace_text("extend_unit_cell.py", 'YYY', str(supercelldim_y))
replace_text("extend_unit_cell.py", 'ZZZ', str(supercelldim_z))
replace_text('build_psf_box_0.tcl', 'NNNNNN', mof_name)
replace_text('build_psf_box_0.tcl', 'BASEDIR', base_directory)
replace_text('build_psf_box_0.tcl', 'FFIELD', model)
replace_text('setBeta.tcl', 'NNNNNN', mof_name)
replace_text('convert_Pymatgen_PDB.tcl', 'MMMMMM', mof_name)

print("Building PDB and PSF files for MOF:")
os.system('python extend_unit_cell.py')

if os.path.isfile(mof_name + "_clean_min.pdb"):
    print("unit cell extended, proceeding to next step")
else:
    print("ERROR: error generating supercell, check extend_unit_cell.py file and check if Pymatgen and Openbabel are installed correctly")
    sys.exit(-1)

os.system("vmd -dispdev text < convert_Pymatgen_PDB.tcl")
if len(glob.glob("*_modified.pdb")) != 0:
    print("pdb file modification complete, proceeding to next step")
else:
    print("ERROR: error in generating pdb file after running Pymatgen")
    sys.exit(-1)

os.system("vmd -dispdev text < build_psf_box_0.tcl")
os.system("vmd -dispdev text < setBeta.tcl")
if len(glob.glob("*.psf")) != 0:
    print("MOF psf and pdb files generated; proceeding to next step")
else:
    print("ERROR: Generating MOF psf file was unsuccessful, exiting...")
    sys.exit(-1)

print("================================================")
print("MOF pdb and psf input files succesfully built")
print("now proceeding to generate reservoir files")
print("================================================")

# Create Reservoir Base
os.chdir('../reservoir')
shutil.copyfile(base_directory + '/BUILD/resources/pdb/' + adsorbate_file, './' + adsorbate_file)
shutil.copyfile(base_directory + '/BUILD/resources/pack/pack_box_1.inp', './pack_box_1.inp')
shutil.copyfile(base_directory + '/BUILD/resources/pack/build_psf_box_1.tcl', './build_psf_box_1.tcl')

replace_text('pack_box_1.inp', 'AAAAAA', adsorbate_name)
replace_text('pack_box_1.inp', 'BASEDIR', base_directory)
replace_text('pack_box_1.inp', 'DDD0', reservoir_dim)
replace_text('pack_box_1.inp', 'NUM#', reservoir_number)
replace_text('build_psf_box_1.tcl', 'BASEDIR', base_directory)
replace_text('build_psf_box_1.tcl', 'RRRR', adsorbate_resname)
replace_text('build_psf_box_1.tcl', 'AAAAAA', adsorbate_name)
replace_text('build_psf_box_1.tcl', 'FFIELD', model)

print("Packing reservoir box...")
os.system("packmol < pack_box_1.inp")
if len(glob.glob("packed_*")) != 0:
    print("Reservoir packed succesfully, proceeding...")
else:
    print("ERROR: Packing reservoir unsuccesful, exiting...")
    sys.exit(-1)

os.system("vmd -dispdev text < build_psf_box_1.tcl")
if len(glob.glob("*.psf")) != 0:
    print("Reservoir psf and pdb files generated succesfully")
else:
    print("ERROR: psf generation for reservoir unsuccesful, exiting...")
    sys.exit(-1)

print("==================================")
print("configuring control file...")
print("==================================")
os.chdir("../")
shutil.copyfile(base_directory + "/BUILD/resources/sim/in.conf", "./in.conf")
replace_text("in.conf", "BASEDIR", base_directory)
replace_text("in.conf", "AAAAAA", adsorbate_name)
replace_text("in.conf", "NNNNNN", mof_name)
replace_text("in.conf", "RCRC", rcut)
replace_text("in.conf", "LRCO", lrc)
replace_text("in.conf", "TTT", temperature)
replace_text("in.conf", "TOLE", tolerance)
replace_text("in.conf", "FFIELD", model)
replace_text("in.conf", "EEEE", electrostatic)
replace_text("in.conf", "SSSSSSSS", runsteps)
replace_text("in.conf", "DDD0", reservoir_dim)
replace_text("in.conf", "DDD1", box_0_vector1)
replace_text("in.conf", "DDD2", box_0_vector2)
replace_text("in.conf", "DDD3", box_0_vector3)
replace_text("in.conf", "RRRR", adsorbate_resname)
replace_text("in.conf", "COORDSTEPS", coordfreq)
replace_text("in.conf", "CONSSTEPS", blockfreq)
replace_text("in.conf", "EQUILSTEPS", eq_steps)
print("Control file has been properly configured, now beginning runs setup")

# Generating runs for each fugacity
os.chdir('../')
print("Total number of runs: " + str(len(runs)))
for run in runs:
    print('Setting up run files for fugacity ' + run['fugacity'])
    current_dir = os.getcwd()
    directory = current_dir + '/run_' + run['fugacity']
    if not os.path.isdir(directory):
        os.mkdir(directory)
    os.chdir(directory)
    shutil.copyfile('../common/in.conf', './in.conf')
    shutil.copyfile(base_directory +'/BUILD/resources/sim/gcmc_cluster.cmd', './gcmc_cluster.cmd')
    shutil.copyfile(base_directory +'/BUILD/resources/sim/GOMC_CPU_GCMC', './GOMC_CPU_GCMC')
    replace_text("gcmc_cluster.cmd", "PPPPP", directory)
    replace_text("gcmc_cluster.cmd", "NNNNNN", mof_name)
    replace_text("gcmc_cluster.cmd", "AAAAAA", adsorbate_name)
    replace_text("gcmc_cluster.cmd", "FFF", run['fugacity'])
    replace_text("in.conf", "TTT", temperature)
    replace_text("in.conf", "FFF", run['fugacity'])
    os.chdir('../')

print("Run directories have been built")

