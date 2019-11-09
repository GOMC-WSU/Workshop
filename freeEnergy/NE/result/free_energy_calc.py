from alchemlyb.parsing.gomc import  extract_dHdl,  extract_u_nk
from alchemlyb.estimators import MBAR, BAR, TI 
import alchemlyb.preprocessing.subsampling as ss
import pandas as pd
import numpy as np
import os

bd = os.path.dirname(os.path.realpath(__file__))

temprature = 298           #temperature (K)
k_b = 1.9872036E-3         #kcal/mol/K
k_b_T = temprature * k_b

def get_delta(est):
    """ Return the change in free energy and standard deviation for TI and MBAR estimators.
    
    """
    delta = est.delta_f_.iloc[0, -1] * k_b_T
    d_delta = est.d_delta_f_.iloc[0, -1] * k_b_T
    return delta, d_delta


def get_delta2(est):
    """ Return the change in free energy and standard deviation for BAR estimator.
    
    """
    ee = 0.0

    for i in range(len(est.d_delta_f_) - 1):
        ee += est.d_delta_f_.values[i][i+1]**2
    
    delta = est.delta_f_.iloc[0, -1] * k_b_T
    d_delta = k_b_T * ee**0.5
    return delta, d_delta

##################################################

numFile = 4
fname = "Free_Energy_BOX_0_PRODUCTION_"
ext = ".dat"
outfile="plots/result_alchemlyb.dat"
file_out=open(outfile,'w')

#read the free energy files 
data_loc = bd + "/data/"
files = []
for i in range(numFile):
    freeEn_file = fname + str(i) + ext
    file_path = data_loc + freeEn_file
    print("Reading File: %s " % (freeEn_file))
    files.append(file_path)
    

print("%s, %24s, %23s" % ("#TI (stdev) (kcal/mol)","MBAR (stdev) (kcal/mol)","BAR (stdev) (kcal/mol)"))
file_out.write("%s, %24s, %23s\n" % ("#TI (stdev) (kcal/mol)","MBAR (stdev) (kcal/mol)","BAR (stdev) (kcal/mol)"))
                
# Read the data for TI estimator and BAR or MBAR estimators.
list_data_TI = []
list_data_BAR = []
for f in files:
    dHdl = extract_dHdl(f, T=temprature)
    u_nkr = extract_u_nk(f, T=temprature)
    #Detect uncorrelated samples using VDW+Coulomb term in derivative 
    # of energy time series (calculated for TI)
    srs = dHdl['VDW'] + dHdl['Coulomb'] 
    list_data_TI.append(ss.statistical_inefficiency(dHdl, series=srs, conservative=False))
    list_data_BAR.append(ss.statistical_inefficiency(u_nkr, series=srs, conservative=False))


#for TI estimator
#print("Working on TI method ...")
dhdl = pd.concat([ld for ld in list_data_TI])
ti = TI().fit(dhdl)
sum_ti, sum_ds_ti = get_delta(ti)

#for MBAR estimator
#print("Working on MBAR method ...")
u_nk = pd.concat([ld for ld in list_data_BAR])
mbar = MBAR().fit(u_nk)
sum_mbar, sum_ds_mbar = get_delta(mbar)

#for BAR estimator
#print("Working on BAR method ...")
u_nk = pd.concat([ld for ld in list_data_BAR])
bar = BAR().fit(u_nk)
sum_bar, sum_ds_bar = get_delta2(bar)
    
#Print the data
print("%0.4f (%0.4f), %14.4f (%0.4f), %15.4f (%0.4f)" % (sum_ti, sum_ds_ti, sum_mbar, sum_ds_mbar, sum_bar, sum_ds_bar))
file_out.write("%0.4f (%0.4f), %14.4f (%0.4f), %15.4f (%0.4f)\n" % (sum_ti, sum_ds_ti, sum_mbar, sum_ds_mbar, sum_bar, sum_ds_bar))

        
file_out.close()
