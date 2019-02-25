import os
import sys
import math
import re
import numpy as np

''' This python code will extend and generate XYZ file for 
*.cif file with symmetry tag 
_symmetry_equiv_pos_as_xyz
"x, y, z"
 '''

class Cell(object):
    ''' Hold the cell information and operation finctions
    Attributes:
        alpha: float
        beta: float
        gamma: float
        cell_lenght_a: float
        cell_lenght_b: float
        cell_lenght_c: float
        cell_basis: 3x3 matrix holding cell basis vectors
        '''
    
    def __init__(self, alpha, beta, gamma, cell_a, cell_b, cell_c):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.cell_length_a = float(cell_a)
        self.cell_length_b = float(cell_b)
        self.cell_length_c = float(cell_c)
        self.cell_basis = np.zeros((3,3), dtype=float)
        self.SetUnitCell()


    def SetUnitCell(self):
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


    def Extend(self, coord, extend_x, extend_y, extend_z):
        len_array = np.array([self.cell_length_a, self.cell_length_b, self.cell_length_c])
        coordExtended = coord + np.array([float(extend_x), float(extend_y), float(extend_z)])
        #scale the unit cell
        cell_b = self.cell_basis * len_array
        #get scaled slant coordinate
        slantScaled = np.matmul(coordExtended, cell_b)
        return slantScaled


def replace_text(filename, text_to_search, replacement_text):
    '''This function will replace <text_to_search> text with
    <replacement_text> string in <filename>'''
    with open(filename, 'r') as file:
        filedata = file.read()
    filedata = filedata.replace(text_to_search, replacement_text)
    with open(filename, 'w') as file:
        file.write(filedata)

def FindParameter(filename, keyword):
    '''This function will find the keyword in the <filename> and
    return the second value'''
    with open(filename, 'r') as file:
        for line in file:
            if line.startswith(keyword):
                line = re.sub(' +', ' ', line).strip()
                return line.split(' ')[1]

#Reading input file and extension data
cif_file = "FILEFILE"
mof_name = "MOFNAME"
output_file = "MOFNAME_clean_min.xyz"
extend_x = int(XXX)
extend_y = int(YYY)
extend_z = int(ZZZ)


# Read Cell Basis information
print("Reading cell information from " + cif_file)
cell_length_a = float(FindParameter(cif_file, '_cell_length_a'))
cell_length_b = float(FindParameter(cif_file, '_cell_length_b'))
cell_length_c = float(FindParameter(cif_file, '_cell_length_c'))
cell_angle_alpha = float(FindParameter(cif_file, '_cell_angle_alpha')) 
cell_angle_beta = float(FindParameter(cif_file, '_cell_angle_beta'))
cell_angle_gamma = float(FindParameter(cif_file, '_cell_angle_gamma'))
print("Cell Info: alpha: %5.5f beta: %5.5f game: %5.5f" % (cell_angle_alpha, cell_angle_beta, cell_angle_gamma))
print("Cell Info: a: %5.5f b: %5.5f c: %5.5f" % (cell_length_a, cell_length_b, cell_length_c))

alpha = cell_angle_alpha * math.pi / 180.0
beta = cell_angle_beta * math.pi / 180.0
gamma = cell_angle_gamma * math.pi / 180.0
# make the cell opbject
cell_mof= Cell(alpha, beta, gamma, cell_length_a, cell_length_b, cell_length_c)

#Reading cif file
reachedAtom = False
elect = False
keywordfound = False
counter = 0

#find the correct atom tag
with open(cif_file, 'r') as infile:
    for line in infile:
        line = re.sub(' +', ' ', line).strip()
        if line.startswith("_atom_site_charge"):
            keyword = "_atom_site_charge"
            elect = True
            keywordfound = True
            break
        elif line.startswith("_atom_site_type_symbol"):
            keyword = "_atom_site_type_symbol"
            elect = False
            keywordfound = True
            break

if not keywordfound:
    print("ERROR: No tag detected to read the atom data in " + cif_file)
    print("Available tag: '_atom_site_charge' or '_atom_site_type_symbol'")
    sys.exit(-1)

with open(output_file, 'w') as outfile:
    outfile.write("TOTALATOM\n")
    outfile.write(mof_name + "\n")
    with open(cif_file, 'r') as infile:
        for line in infile:
            line = re.sub(' +', ' ', line).strip()
            if line.startswith(keyword):
                reachedAtom = True
                continue
            
            if(reachedAtom):
                atom_name = line.split(' ')[0]
                if elect:
                    #has different cif format
                    x = float(line.split(' ')[1])
                    y = float(line.split(' ')[2])
                    z = float(line.split(' ')[3])
                else:
                    x = float(line.split(' ')[2])
                    y = float(line.split(' ')[3])
                    z = float(line.split(' ')[4])

                frac_coord = np.array([x, y, z])
                for i in range(extend_x):
                    for j in range(extend_y):
                        for k in range(extend_z):
                            coord = cell_mof.Extend(frac_coord, i, j, k)
                            to_print = "%3s %15.6f %15.6f %15.6f\n" % (atom_name, coord[0], coord[1], coord[2])
                            outfile.write(to_print)
                            counter += 1


replace_text(output_file, "TOTALATOM", str(counter))
                        