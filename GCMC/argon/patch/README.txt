# To patch the histogram data, we need to copy them in this directory. 
# Use the following command to copy them in this directory and "pvt" direcotry:

cp ../run*/his*  .
cp ../run1/his1a.dat  pvt/.

# To accurately calculate the pressure, we need to calculate the constant C by
# extrapolating the predicted partition function to very low densities, where 
# the system exhibits ideal gas behavior. Change your directory to "pvt" and 
# run the following commands:

cd pvt/.

./patch.out

cp weights.dat input_fsp2.dat 

./pvt.out

# Plot the "pvt.dat" file and determine the intersection with y-axis. Then 
# change your directory to previous directory.

cd ../.

# Use the intersection value to modify the value of "lnZ0" in "phinput.idat" 
# file. To patch the data, run the following command and wait until it finishes

./patch.out

cp weights.dat input_fsp2.dat 

# Modify the fields in "phinput.idat" file, such as "Mu1", "MV(1)", and 
# "Nmid". Then run the following command wait until it finishes:
 
./phase.out

# Lastly, generate the coexistence data point by running the following command:
# This command will generate "trho.dat", "tp.dat", and "dhv.dat".

./pconv

# compare your results with "NIST.dat" file.





