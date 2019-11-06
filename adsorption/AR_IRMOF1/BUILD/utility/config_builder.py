import xml.etree.ElementTree as et
import utility_functions as uf 
import numpy as np
import extend_unit_cell as euc

class System(object):
    ''' Hole elements of the general adsorption system
    Atributes:
        build_all = boolean
        adsorbate_pdb = string
        adsorbate_resname = string
        reservoir_dim = string
        reservoir_number = string
        model = string
        par_file = string
        '''

    def __init__(self, file):
        tree = et.parse(file)
        root = tree.getroot()
        e = root.find('system')
        build_all = e.find('HTS').find('active').text
        self.mof_file = e.find('HTS').find('mofname').text
        self.build_all = (build_all.lower() == "true")
        self.adsorbate_pdb = e.find('adsorbate').find('name').text
        self.adsorbate_name = self.adsorbate_pdb.split('.')[0]
        self.adsorbate_resname = e.find('adsorbate').find('resname').text
        self.reservoir_dim = e.find('reservoir').find('dim').text
        self.reservoir_number = e.find('reservoir').find('number').text
        self.model = e.find('model').text
        self.par_file = "Parameters_" + self.model + ".par"

    def Write_Conf(self, file):
        uf.replace_text(file, "ADSBNAME", self.adsorbate_name)
        uf.replace_text(file, "FFIELD", self.model)
        uf.replace_text(file, "DDD0", self.reservoir_dim)
        uf.replace_text(file, "ADSBSET", self.adsorbate_resname)

    def Print_summary(self):
        print("%-20s: %-s" %("MODEL", self.model))
        print("%-20s: %-s" %("ADSORBATE_PDB", self.adsorbate_pdb))
        print("%-20s: %-s" %("ADSORBATE_RESNAME", self.adsorbate_resname))
        print("%-20s: %-s" %("RESERVOIR_DIM", self.reservoir_dim))
        print("%-20s: %-s" %("RESERVOIR_NUMBER", self.reservoir_number))
        print("%-20s: %-s" %("BUILD ALL MOFs", str(self.build_all)))


class Simulation(object):
    ''' Holding the list of parameter to be replaced in in.conf
    These value are only sets once for all runs.
    Atributes:
        simData = arraye of [name, keyword, value]
        name = string
        keyword = string, to be replaces
        value = string, to replace the keyword. '''

    def __init__(self, file):
        tree = et.parse(file)
        root = tree.getroot()
        e = root.find('simulation')
        self.simData = []

        for element in e.findall('element'):
            kw = element.find('keyword').text
            val = element.find('value').text
            name = element.get('name').upper()
            self.simData.append([name, kw, val])

    def FindVal(self, name):
        ''' Find the value corresponding to the name.
        Return the value'''
        elName = name.upper()
        for i in range(len(self.simData)):
            if(elName == self.simData[i][0]):
                return self.simData[i][2]
        
        print(name + ' did not found in Simulation parameter.')
        exit(1)

    def SetVal(self, name, val):
        ''' Set the value corresponding to the name.'''
        elName = name.upper()
        for i in range(len(self.simData)):
            if(elName == self.simData[i][0]):
                self.simData[i][2] = val
        
        print(name + ' did not found in Simulation parameter.')
        exit(1)

    def Find_Kw_Val(self, name):
        ''' Find the keyword to be replaced and value corresponding to the name.
        Return an array of size 2 [keyword, value]'''
        elName = name.upper()
        for i in range(len(self.simData)):
            if(elName == self.simData[i][0]):
                temp = [self.simData[i][1], self.simData[i][2]]
                return temp

    def Write_Conf(self, file):
        ''' Replace the keyword with value in config file'''
        for i in range(len(self.simData)):
            uf.replace_text(file, self.simData[i][1], self.simData[i][2])

    def Print_summary(self):
        for i in range(len(self.simData)):
            print("%-20s: %-s" % (self.simData[i][0], self.simData[i][2]))



class Run_Simulation(object):
    ''' Holding the list of parameter to be replaced in in.conf
    These value are specific for each runs.
    Atributes:
        runSimData = arraye of [[runid, [name, keyword, value]], ...]
        runid = string, run ID
        name = string
        keyword = string, to be replaces
        value = string, to replace the keyword. '''

    def __init__(self, file):
        tree = et.parse(file)
        root = tree.getroot()
        e = root.find('run_simulation')
        self.runSimData = []

        for run in e.findall('run'):
            runid = run.get('id').upper()
            simData = []
            for element in run.findall('element'):
                kw = element.find('keyword').text
                val = element.find('value').text
                name = element.get('name').upper()
                simData.append([name, kw, val])

            self.runSimData.append([runid, simData])

    def FindVal(self, idx, name):
        ''' Find the value corresponding to the idx and name.
        Return the value'''
        elName = name.upper()
        for j in range(len(self.runSimData[idx][1])):
            if(elName == self.runSimData[idx][1][j][0]):
                return self.runSimData[idx][1][j][2] 

        print(name + ' did not found in run_simulation parameter.')
        exit(1)      

    def SetVal(self, idx, name, val):
        ''' Set the value corresponding to the idx and name.'''
        elName = name.upper()
        for j in range(len(self.runSimData[idx][1])):
            if(elName == self.runSimData[idx][1][j][0]):
                self.runSimData[idx][1][j][2] = val

        print(name + ' did not found in run_simulation parameter.')
        exit(1)           

    def Find_Kw_Val(self, idx, name):
        ''' Find the keyword to be replaced and value corresponding to the idx and name.
        Return an array of size 2 [keyword, value]'''
        elName = name.upper()
        for j in range(len(self.runSimData[idx][1])):
            if(elName == self.runSimData[idx][1][j][0]):
                temp = [self.runSimData[idx][1][j][1], self.runSimData[idx][1][j][2]]
                return temp

    def Write_Conf(self, file, idx):
        ''' Replace the keyword with value in config file'''
        for j in range(len(self.runSimData[idx][1])):
            uf.replace_text(file, self.runSimData[idx][1][j][1], self.runSimData[idx][1][j][2])

    def Print_summary(self):
        for i in range(len(self.runSimData)):
            to_print = "Run" + self.runSimData[i][0]
            for j in range(len(self.runSimData[i][1])):
                name = self.runSimData[i][1][j][0]
                val = self.runSimData[i][1][j][2]
                to_print += ": %s(%5s)" % (name, val)

            print(to_print)

    def Summary_Str(self, id):
        to_print = "RUN" + self.runSimData[id][0]
        for j in range(len(self.runSimData[id][1])):
            name = self.runSimData[id][1][j][0]
            val = self.runSimData[id][1][j][2]
            to_print += "-%s-%s" % (name, val)

        return(to_print)



class ConfigBuilder(object):
    '''Holding Sytem, Simulation and Run_Simulation object.
    Handles, writing, and print summary
    'Atributes:
        sys = System class
        sim = Simulation class
        runSim = Run_Simulation class
        mof_name = string
        base_directory = string
        basis = 3x3 matrix'''

    def __init__(self, confSetup):
        self.sys = System(confSetup)
        self.sim = Simulation(confSetup)
        self.runSim = Run_Simulation(confSetup)
        self.mof_name = ""
        self.base_directory = ""
        self.box_0_vector1 = ""
        self.box_0_vector2 = ""
        self.box_0_vector3 = ""


    def Print_summary(self, mof_name):
        self.mof_name = mof_name
        self.sys.Print_summary()
        print("%-20s: %-s" %("MOF_NAME", mof_name))
        self.sim.Print_summary()
        self.runSim.Print_summary()

    def Print_cellData(self, cellbasis):
        box_vector = cellbasis.GetCellVector()
        self.box_0_vector1 = "{:8.4f} {:8.4f} {:8.4f} ".format(*box_vector[0])
        self.box_0_vector2 = "{:8.4f} {:8.4f} {:8.4f} ".format(*box_vector[1])
        self.box_0_vector3 = "{:8.4f} {:8.4f} {:8.4f} ".format(*box_vector[2])
        print("SUPERCELL_EXPANSION_FACTOR: {:d} x {:d} x {:d}".format(*cellbasis.extend))
        print("CELL BASIS VECTOR 0: " + self.box_0_vector1)
        print("CELL BASIS VECTOR 1: " + self.box_0_vector2)
        print("CELL BASIS VECTOR 2: " + self.box_0_vector3)

    def Write_SimData(self, file):
        uf.replace_text(file, "MOFNAME", self.mof_name)
        uf.replace_text(file, "DDD1", self.box_0_vector1)
        uf.replace_text(file, "DDD2", self.box_0_vector2)
        uf.replace_text(file, "DDD3", self.box_0_vector3)
        uf.replace_text(file, "BASEFUGACITY", self.mof_name[:4] + "   0.0")
        self.sys.Write_Conf(file)
        self.sim.Write_Conf(file)

    def Write_runData(self, file, runID, dir):
        self.runSim.Write_Conf(file, runID)
        uf.replace_text("gcmc_cluster.cmd", "RUN-DIR", dir)
        uf.replace_text("gcmc_cluster.cmd", "MOFNAME", self.mof_name)
        uf.replace_text("gcmc_cluster.cmd", "ADSBNAME", self.sys.adsorbate_name)
        uf.replace_text("gcmc_cluster.cmd", "FFF", self.runSim.FindVal(runID, 'fugacity'))

    def HasElect(self):
        return (self.sim.FindVal('electrostatic').lower() == 'true')

    def GetRcut(self):
        rcut = float(self.sim.FindVal('rcut'))
        rcutCol = 0.0
        if(self.HasElect()):
            rcutCol = float(self.sim.FindVal('rcutcoulomb'))

        return max(rcut, rcutCol)


