import os
import sys
import math
import re
import numpy as np
import top_generator as topGen
import utility_functions as uf 

''' This python code will extend and generate XYZ file for 
*.cif file with symmetry tag 
_symmetry_equiv_pos_as_xyz
"x, y, z"
 '''

class Cell(object):
    ''' Hold the cell information and operation functions
    Attributes:
        alpha: float
        beta: float
        gamma: float
        cell_lenght_a: float
        cell_lenght_b: float
        cell_lenght_c: float
        cell_basis: 3x3 matrix holding cell basis vectors
        cell_basis_inv: 3x3 matrix holding inverse of cell basis vectors
        '''
    
    def __init__(self, angle, length):
        self.alpha = angle[0]
        self.beta = angle[1]
        self.gamma = angle[2]
        self.cell_length_a = length[0]
        self.cell_length_b = length[1]
        self.cell_length_c = length[2]
        self.cell_basis = np.zeros((3,3), dtype=float)
        self.cell_basis_inv = np.zeros((3,3), dtype=float)
        self.SetUnitCell()


    def SetUnitCell(self):
        ''' Calculate the unit cell matrix'''
        ax = 1.0
        ay = 0.0
        az = 0.0
        bx = math.cos(self.gamma)
        by = math.sin(self.gamma)
        bz = 0.0
        cx = math.cos(self.beta)
        cy = (math.cos(self.alpha) - math.cos(self.beta) * math.cos(self.gamma)) / math.sin(self.gamma)
        cz = (math.sqrt(math.sin(self.beta)**2 - cy**2))
        #set the value
        self.cell_basis[0] = np.array([ax, ay, az])
        self.cell_basis[1] = np.array([bx, by, bz])
        self.cell_basis[2] = np.array([cx, cy, cz])
        self.cell_basis_inv = np.linalg.inv(self.cell_basis)


    def Extend(self, coord, extend_x, extend_y, extend_z):
        ''' Extend the unit cell in extend_x, extend_y, extend_z'''
        len_array = np.array([self.cell_length_a, self.cell_length_b, self.cell_length_c])
        coordExtended = coord + np.array([float(extend_x), float(extend_y), float(extend_z)])
        #scale the unit cell
        cell_b = self.cell_basis * len_array
        #get scaled slant coordinate
        slantScaled = np.matmul(coordExtended, cell_b)
        return slantScaled



class MOF_Data(object):

    def __init__(self, mof_file, mof_name, maxCutoff):
        #Reading input file and extension data
        self.cif_file = mof_file
        self.mof_name = mof_name
        self.output_file = mof_name + ".xyz"
        self.extend = np.array([1, 1, 1])
        self.rcut2 = float(maxCutoff) * 2.0 + 0.1
        self.cell_length = np.zeros(3, dtype=float)
        self.cell_angle = np.zeros(3, dtype=float)
        self.SetCellData()
        self.cellBasis = Cell(self.cell_angle, self.cell_length)
        self.CalcMinCellExtend()

    def SetCellData(self):
        ''' Setting cell length and angle'''
        cell_length_a = float(uf.FindParameter(self.cif_file, '_cell_length_a'))
        cell_length_b = float(uf.FindParameter(self.cif_file, '_cell_length_b'))
        cell_length_c = float(uf.FindParameter(self.cif_file, '_cell_length_c'))
        cell_angle_alpha = float(uf.FindParameter(self.cif_file, '_cell_angle_alpha')) 
        cell_angle_beta = float(uf.FindParameter(self.cif_file, '_cell_angle_beta'))
        cell_angle_gamma = float(uf.FindParameter(self.cif_file, '_cell_angle_gamma'))
        self.cell_length = np.array([cell_length_a, cell_length_b, cell_length_c])
        self.cell_angle = np.array([cell_angle_alpha, cell_angle_beta, cell_angle_gamma])
        self.cell_angle = self.cell_angle * math.pi / 180.0


    def CalcMinCellExtend(self):
        ''' Find the minimum required extension in each direction.
         extension is required for simulation box to be at least twice
         bigger that rcut'''
        self.extend[0] = int(np.ceil(self.rcut2 / self.cell_length[0]))
        self.extend[1] = int(np.ceil(self.rcut2 / self.cell_length[1]))
        self.extend[2] = int(np.ceil(self.rcut2 / self.cell_length[2]))
        
    def GetCellVector(self):
        ''' Extend the unit cell in extend_x, extend_y, extend_z
        and calculate the cell basis vector'''
        length = self.cell_length * self.extend
        cellV = self.cellBasis.cell_basis * length
        #slantScaled = np.matmul(self.extend, cell_b)
        return cellV

    def WriteXYZ(self, top_file):
        ''' Writing XYZ data calculated extension. and create Topology file'''
        # detect the tag in cif file
        cif_data = topGen.TopGenerate(self.cif_file)
        cif_data.DetectTag()
        cif_data.ReadCharges()
        #create the topology with extension
        topGen.MakeTopology(cif_data, top_file, self.extend[0] * self.extend[1] * self.extend[2])

        #Reading cif file
        reachedAtom = False
        molCount = 0

        with open(self.output_file, 'w') as outfile:
            outfile.write("TOTALATOM\n")
            outfile.write(self.mof_name + "\n")
            with open(self.cif_file, 'r') as infile:
                for line in infile:
                    line = re.sub(' +', ' ', line).strip()
                    if line.startswith(cif_data.startTag):
                        reachedAtom = True
                        continue
                    
                    if(reachedAtom):
                        if(line.startswith(cif_data.endTag)):
                            break

                        atom_name = line.split(' ')[cif_data.tag_symbol_indx]
                        x = float(line.split(' ')[cif_data.tag_x_indx])
                        y = float(line.split(' ')[cif_data.tag_y_indx])
                        z = float(line.split(' ')[cif_data.tag_z_indx])

                        if(cif_data.hasCharge):
                            charge = float(line.split(' ')[cif_data.tag_charge_indx])
                        else:
                            charge = 0.0

                        atom_name = cif_data.GetAtomName(atom_name, charge)
                        frac_coord = np.array([x, y, z])
                        for i in range(self.extend[0]):
                            for j in range(self.extend[1]):
                                for k in range(self.extend[2]):
                                    coord = self.cellBasis.Extend(frac_coord, i, j, k)
                                    to_print = "%4s %15.6f %15.6f %15.6f\n" % (atom_name, coord[0], coord[1], coord[2])
                                    outfile.write(to_print)
                                    molCount += 1


        uf.replace_text(self.output_file, "TOTALATOM", str(molCount))