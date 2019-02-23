#!/bin/bash

BASE_DIR=$( pwd )
CONFIG_FILE="${BASE_DIR}/BUILD/ConfigSetup.conf"

###############
#Set Variables#
###############

MOF_ID=$( awk '/^MOF_ID/{print $2}' ${CONFIG_FILE} )
MOF_NAME=$( awk '/^MOF_NAME/{print $2}' ${CONFIG_FILE} )
ADSORBATE_NAME=$( awk '/^ADSORBATE_NAME/{print $2}' ${CONFIG_FILE} )
ADSORBATE_RESNAME=$( awk '/^ADSORBATE_RESNAME/{print $2}' ${CONFIG_FILE} )
ELECTROSTATIC=$( awk '/^ELECTROSTATIC/{print $2}' ${CONFIG_FILE} )
TOLERANCE=$( awk '/^TOLERANCE/{print $2}' ${CONFIG_FILE} )
TEMPERATURE=$( awk '/^TEMPERATURE/{print $2}' ${CONFIG_FILE} )
RESERVOIR_DIM=$( awk '/^RESERVOIR_DIM/{print $2}' ${CONFIG_FILE} )
RESERVOIR_NUMBER=$( awk '/^RESERVOIR_NUMBER/{print $2}' ${CONFIG_FILE} )
MODEL=$( awk '/^MODEL/{print $2}' ${CONFIG_FILE} )
RCUT=$( awk '/^RCUT/{print $2}' ${CONFIG_FILE} )
LRC=$(awk '/^LRC/{print $2}' ${CONFIG_FILE} )
RUNSTEPS=$( awk '/^RUNSTEPS/{print $2}' ${CONFIG_FILE} )
SUPERCELL_X=$( awk '/^SUPERCELL_DIM/{print $2}' ${CONFIG_FILE} )
SUPERCELL_Y=$( awk '/^SUPERCELL_DIM/{print $3}' ${CONFIG_FILE} )
SUPERCELL_Z=$( awk '/^SUPERCELL_DIM/{print $4}' ${CONFIG_FILE} )
COORD_RESTART=$( echo "$RUNSTEPS*0.1" | bc -l )
CONSOLE_BLOCKAVG=$( echo "$RUNSTEPS*0.01" | bc -l )
EQSTEPS=$( echo "$RUNSTEPS*0.5" | bc -l )


if [ $ELECTROSTATIC = "True" ]; then
	MOF_FILE="${MOF_ID}_clean_min_charges.cif"
elif [ $ELECTROSTATIC = "False" ]; then 
	MOF_FILE="${MOF_ID}_clean_min.cif"
else
	echo "ELECTROSTATIC INPUT INVALID"
	echo "EXITING..."
	exit 1
fi

if [ $ELECTROSTATIC = "True" ]; then
	MOF_PWD="$BASE_DIR/BUILD/resources/CoRE-MOF-1.0-DFT-Minimized/minimized_structures_with_DDEC_charges/${MOF_FILE}"
elif [ $ELECTROSTATIC = "False" ]; then 
	MOF_PWD="$BASE_DIR/BUILD/resources/CoRE-MOF-1.0-DFT-Minimized/minimized_structures/${MOF_FILE}"
fi


ADSORBATE_FILE="${ADSORBATE_NAME}.pdb"

############################
#Create Build Directories
############################
echo "setting up directories"
mkdir Run_files
cd Run_files
mkdir Common
cd Common
mkdir MOF_base
mkdir reservoir_base
cd MOF_base
##############################
#copy MOF cif file into MOF_base directory
##############################
cp $MOF_PWD .

if [ -f $MOF_FILE ]; then
	echo "MOF_FILE succesfully copied into MOF_base directory"
else
	echo "ERROR: MOF_FILE NOT FOUND"
	exit 2
fi
################################
#Generate Cell Basis Vectors
################################
CELL_LENGTH_A=$( awk '/^_cell_length_a/{print $2}' ${MOF_FILE} )
CELL_LENGTH_B=$( awk '/^_cell_length_b/{print $2}' ${MOF_FILE} )
CELL_LENGTH_C=$( awk '/^_cell_length_c/{print $2}' ${MOF_FILE} )
CELL_ANGLE_ALPHA=$( awk '/^_cell_angle_alpha/{print $2}' ${MOF_FILE} )
CELL_ANGLE_BETA=$( awk '/^_cell_angle_beta/{print $2}' ${MOF_FILE} )
CELL_ANGLE_GAMMA=$( awk '/^_cell_angle_gamma/{print $2}' ${MOF_FILE} )
PI=$( echo "4*a(1)" | bc -l )
ALPHA=$( echo "$CELL_ANGLE_ALPHA*($PI/180)" | bc -l )
BETA=$( echo "$CELL_ANGLE_BETA*($PI/180)" | bc -l )
GAMMA=$( echo "$CELL_ANGLE_GAMMA*($PI/180)" | bc -l )
AX=$( echo "scale=5; $CELL_LENGTH_A*$SUPERCELL_X" | bc -l )
AY='0'
AZ='0'
BX=$( echo "scale=5; $CELL_LENGTH_B*c($GAMMA)*$SUPERCELL_Y" | bc -l )
BY=$( echo "scale=5; $CELL_LENGTH_B*s($GAMMA)*$SUPERCELL_Y" | bc -l )
BZ='0'
CX=$( echo "scale=5; $CELL_LENGTH_C*c($BETA)*$SUPERCELL_Z" | bc -l )
CY_BASE=$( echo "scale=5; (c($ALPHA)-c($BETA)*c($GAMMA))/s($GAMMA)" | bc -l )
CY=$( echo "scale=5; $CELL_LENGTH_C*((c($ALPHA)-c($BETA)*c($GAMMA))/s($GAMMA))*$SUPERCELL_Z" | bc -l )
CZ=$( echo "scale=5; $CELL_LENGTH_C*(sqrt(s($BETA)^2-${CY_BASE}^2))*$SUPERCELL_Z" | bc -l )

BOX_0_VECTOR1="$AX $AY $AZ"
BOX_0_VECTOR2="$BX $BY $BZ"
BOX_0_VECTOR3="$CX $CY $CZ"

echo " "
echo " - READING SETUP PARAMETERS - "
echo "=========================================="
echo ""
echo "MOF_NAME: " ${MOF_NAME}
echo "ADSORBATE_NAME: " ${ADSORBATE_NAME}
echo "ELECTROSTATIC: " ${ELECTROSTATIC}
echo "TOLERANCE: ${TOLERANCE}"
echo "LRC: ${LRC}"
echo "TEMPERATURE: ${TEMPERATURE}"
echo "MODEL: ${MODEL}"
echo "RESERVOIR_DIM: " ${RESERVOIR_DIM}
echo "RESERVOIR_NUMBER: " ${RESERVOIR_NUMBER}
echo "RCUT: " ${RCUT}
echo "RUNSTEPS: " ${RUNSTEPS}
echo "SUPERCELL_EXPANSION_FACTOR: ${SUPERCELL_X} ${SUPERCELL_Y} ${SUPERCELL_Z}"
echo " "
echo "Cell Basis Vectors:"
echo $BOX_0_VECTOR1
echo $BOX_0_VECTOR2
echo $BOX_0_VECTOR3




####################
#Create MOF Base
####################
echo "creating MOF base"

cp ../../../BUILD/resources/pack/extend_unit_cell.py .
cp ../../../BUILD/resources/pack/convert_Pymatgen_PDB.tcl .
cp ../../../BUILD/resources/pack/build_psf_box_0.tcl .
cp ../../../BUILD/resources/pack/setBeta.tcl .
cp ../../../BUILD/resources/model/Top_${MODEL}.inp .
sed -i "" -e  "s/FILEFILE/${MOF_FILE}/g" extend_unit_cell.py
sed -i "" -e  "s/MMMMMM/${MOF_ID}/g" extend_unit_cell.py
sed -i "" -e  "s/CCC/${SUPERCELL_X}/g" extend_unit_cell.py
sed -i "" -e  "s/YYY/${SUPERCELL_Y}/g" extend_unit_cell.py
sed -i "" -e  "s/ZZZ/${SUPERCELL_Z}/g" extend_unit_cell.py
sed -i "" -e  "s/MMMMMM/${MOF_ID}/g" *.tcl
sed -i "" -e  "s/NNNNNN/${MOF_NAME}/g" *.tcl
sed -i "" -e  "s/FFIELD/${MODEL}/g" build_psf_box_0.tcl

echo "building PDB and PSF files for MOF: Start"
python extend_unit_cell.py
if [ -f *_clean_min.pdb ]; then
	echo "unit cell extended, proceeding to next step"
else
	echo "ERROR: error generating supercell, check extend_unit_cell.py file and check if Pymatgen and Openbabel are installed correctly"
	exit 3
fi
echo +++++++++++++++++++++++++++++++++++++++
echo +++++++++++++++++++++++++++++++++++++++
echo "topology file needed, please paste topology file into MOF_base directory"

vmd -dispdev text < convert_Pymatgen_PDB.tcl
if [ -f *_modified.pdb ]; then
	echo "pdb file modification complete, proceeding to next step"
else
	echo "ERROR: error in generating pdb file after running Pymatgen"
	exit 4
fi
vmd -dispdev text < build_psf_box_0.tcl
vmd -dispdev text < setBeta.tcl
if [ -f *.psf ]; then
	echo "psf and pdb files generated; proceeding to next step"
else
	echo "ERROR: error in generating psf file, exiting..."
	exit 5
fi
echo ================================================
echo "MOF pdb and psf input files succesfully built"
echo "now proceeding to generate reservoir files"
echo ================================================

#########################
#Create Reservoir Base
#########################
cd ../reservoir_base
cp "../../../BUILD/resources/pdb/${ADSORBATE_FILE}" .
if [ -f $ADSORBATE_FILE ]; then
	echo "Adsorbate file succesfully copied into reservoir_base, psf and pdb build beginning"
else
	echo "Adsorbate file not found, exiting..."
	exit 6
fi
cp ../../../BUILD/resources/pack/packmol .
cp ../../../BUILD/resources/pack/pack_box_1.inp .
cp ../../../BUILD/resources/pack/build_psf_box_1.tcl .

sed -i "" -e  "s/AAAAAA/${ADSORBATE_NAME}/g" pack_box_1.inp
sed -i "" -e  "s/DDD0/${RESERVOIR_DIM}/g" pack_box_1.inp
sed -i "" -e  "s/NUM#/${RESERVOIR_NUMBER}/g" pack_box_1.inp
sed -i "" -e  "s/RRRR/${ADSORBATE_RESNAME}/g" build_psf_box_1.tcl
sed -i "" -e  "s/AAAAAA/${ADSORBATE_NAME}/g" build_psf_box_1.tcl
sed -i "" -e  "s/FFIELD/${MODEL}/g" build_psf_box_1.tcl

echo "topology file needed, please paste topology file into reservoir_base directory"

echo "packing reservoir box..."
packmol < pack_box_1.inp
if [ -f packed_* ]; then
	echo "Reservoir packed succesfully, proceeding..."
else
	echo "Packmol unsuccesful, exiting..."
	exit 7
fi
vmd < build_psf_box_1.tcl
if [ -f *.psf ]; then
	echo "Reservoir psf and pdb files generated succesfully"
	echo ===================================================
else 
	echo "psf generation unsuccesful, exiting..."
	exit 8
fi

###########################
#Set Up In.conf File (Control File) - original
###########################
echo ==================================
echo "configuring control file..."
echo ==================================
cd ../
cp ../../BUILD/resources/sim/in.conf .
sed -i "" -e  "s/AAAAAA/${ADSORBATE_NAME}/g" in.conf
sed -i "" -e  "s/NNNNNN/${MOF_NAME}/g" in.conf
sed -i "" -e  "s/RCRC/${RCUT}/g" in.conf
sed -i "" -e  "s/LRCO/${LRC}/g" in.conf
sed -i "" -e  "s/TTT/${TEMPERATURE}/g" in.conf
sed -i "" -e  "s/TOLE/${TOLERANCE}/g" in.conf
sed -i "" -e  "s/FFIELD/${MODEL}/g" in.conf
sed -i "" -e  "s/EEEE/${ELECTROSTATIC}/g" in.conf
sed -i "" -e  "s/SSSSSSSS/${RUNSTEPS}/g" in.conf
sed -i "" -e  "s/DDD0/${RESERVOIR_DIM}/g" in.conf
sed -i "" -e  "s/DDD1/${BOX_0_VECTOR1}/g" in.conf
sed -i "" -e  "s/DDD2/${BOX_0_VECTOR2}/g" in.conf
sed -i "" -e  "s/DDD3/${BOX_0_VECTOR3}/g" in.conf
sed -i "" -e  "s/RRRR/${ADSORBATE_RESNAME}/g" in.conf
sed -i "" -e  "s/COORDSTEPS/${COORD_RESTART}/g" in.conf
sed -i "" -e  "s/CONSSTEPS/${CONSOLE_BLOCKAVG}/g" in.conf
sed -i "" -e  "s/EQUILSTEPS/${EQSTEPS}/g" in.conf
echo "control file has been properly configured, now beginning runs setup"

#################################
#Read Data from Runs data file
#################################
cd ../
RUN_NUMBER=( $( awk '/^R /{print $2}' ${CONFIG_FILE} ) )
RUN_TOTAL=$( echo ${#RUN_NUMBER[@]} )
echo "total number of runs: $RUN_TOTAL"
RUN_FUGACITY=( $( awk '/^R /{print $3}' ${CONFIG_FILE} ) )
RUN_ID=1
until [ ${RUN_ID} -gt ${RUN_TOTAL} ]; do
	echo "setting up run files for run number $RUN_ID"
	FUGACITY=${RUN_FUGACITY[$RUN_ID - 1]}
	COMMAND_PATH=$( pwd )
	echo "The fugacity for run number $RUN_ID is $FUGACITY"
	echo "$PWD"
	mkdir "Run_${RUN_FUGACITY[$RUN_ID - 1]}"
	cd "Run_${RUN_FUGACITY[$RUN_ID - 1]}"
	cp ../Common/in.conf .
	cp ../../BUILD/resources/sim/gcmc_cluster.cmd .
	sed -i "" -e  "s@PPPPP@${COMMAND_PATH}@g" gcmc_cluster.cmd
	sed -i "" -e  "s/NNNNNN/$MOF_NAME/g" gcmc_cluster.cmd
	sed -i "" -e  "s/AAAAAA/$ADSORBATE_NAME/g" gcmc_cluster.cmd
	sed -i "" -e  "s/FFF/$FUGACITY/g" gcmc_cluster.cmd
	sed -i "" -e  "s/TTT/${TEMPERATURE}/g" in.conf
	sed -i "" -e  "s/FFF/${FUGACITY}/g" in.conf
	cp ../../BUILD/resources/sim/GOMC_CPU_GCMC .
	echo "run $RUN_ID has been set up, proceeding to next run"
	cd ../
	RUN_ID=$((RUN_ID+1))
done

echo "run directories have been built"

exit









