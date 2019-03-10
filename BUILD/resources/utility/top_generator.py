import os
import re
import math
import glob
import sys

import utility_functions as uf 

class Molecule(object):
    ''' Holds the residue name, type, number of residue
    average charge
    Attributes:
        resname: string
        restype: string
        molCount: int
        avgCharge: float 
    '''

    def __init__(self, residuename, atomcharge):
        self.resname = residuename.upper()
        self.molCount = 1
        self.avgCharge = float(atomcharge)
        self.restype = ""
        #All resname might have different charge but they have same type
        #We remove any number from restype
        for c in str(residuename).upper():
            try:
                int(c)
                self.restype = self.restype
            except ValueError:
                self.restype += c

    def AddCharge(self, atomcharge):
        totalCharge = float(self.molCount) * self.avgCharge
        self.molCount += 1
        totalCharge += float(atomcharge)
        self.avgCharge = totalCharge / float(self.molCount)

    def GetRes(self):
        out = "RESI  %5s         %.6f  !\n" % (self.resname, self.avgCharge)
        return out

    def GetAtom(self):
        out = "ATOM  %5s   %3s   %.6f  !\n" % (self.resname, self.restype, self.avgCharge)
        return out

    def PrintSummary(self):
        print(self.GetRes())
        print(self.GetAtom())
        print("PATCHING FIRS NONE LAST NONE \n\n")



class TopGenerate(object):
    ''' Generate topology file from cif file. Using charge defined 
    in cif files.
    Attributes:
        mof_file = string, molf file with no path included
        tag = string, tag in cif file
        hasCharge = boolean, if cif has has charge information
        moleculeMap = Molecule, list of all molecules

        tag_x_indx = index to read x fractional coordinate
        tag_y_indx = index to read y fractional coordinate
        tag_z_indx = index to read z fractional coordinate
        tag_charge_indx = index to read charge
    '''

    def __init__(self, mof): 
        self.mof_file = mof
        self.hasCharge = False
        self.lastTag = ""
        self.moleculeMap = []
        self.tag_x_indx = 0
        self.tag_y_indx = 0
        self.tag_z_indx = 0
        self.tag_charge_indx = 0

    def DetectTag(self): 
        ''' Detect the tag in cif file.'''
        tag_loop = "loop_"
        tag_x = "_atom_site_fract_x"
        tag_y = "_atom_site_fract_y"
        tag_z = "_atom_site_fract_z"
        tag_charge = "_atom_site_charge"
        idx = 0

        #find the correct atom tag
        with open(self.mof_file, 'r') as infile:
            for line in infile:
                line = re.sub(' +', ' ', line).strip()
                if line.startswith("#"):
                    continue

                if line.startswith(tag_loop):
                    idx = 0
                elif line.startswith(tag_x):
                    self.tag_x_indx = idx
                    self.lastTag = line
                    idx = idx + 1
                elif line.startswith(tag_y):
                    self.tag_y_indx = idx
                    self.lastTag = line
                    idx = idx + 1
                elif line.startswith(tag_z):
                    self.tag_z_indx = idx
                    self.lastTag = line
                    idx = idx + 1
                elif line.startswith(tag_charge):
                    self.tag_charge_indx = idx
                    self.hasCharge = True
                    idx = idx + 1
                    self.lastTag = line
                else:
                    idx = idx + 1
                    if line.startswith("_"):
                        self.lastTag = line



        if (self.tag_x_indx == 0 or self.tag_y_indx == 0 or self.tag_z_indx == 0):
            print("ERROR: No tag detected to read the atom data in " + self.mof_file)
            print("Available tags: %s %s %s" %(tag_x, tag_y, tag_z))
            sys.exit(-1)


    def MolExist(self, atom, charge):
        ''' If molecule already exist, we just add the charge
        otherwise, we append it to the list'''
        exist = False
        counter = 0
        for mol in self.moleculeMap:
            if(mol.resname == atom.upper()):
                exist = True
                index = counter

            counter += 1
        
        if not exist:
            self.moleculeMap.append(Molecule(atom, charge))
        else:
            self.moleculeMap[index].AddCharge(charge)


    def ReadCharges(self):
        ''' Read and calcuate the average charges for molecules in cif file.
        Update the list of molecule in class'''
        reachedAtom = False

        with open(self.mof_file, 'r') as file:
            for line in file:
                line = re.sub(' +', ' ', line).strip()
                if line.startswith(self.lastTag):
                    reachedAtom = True
                    continue
                
                if(reachedAtom):
                    atom = line.split(' ')[0]
                    if self.hasCharge:
                        charge = line.split(' ')[self.tag_charge_indx]
                    else:
                        charge = str(0.0)

                    self.MolExist(atom, charge)


def MakeTopology(mof_file, top_file):
    ''' Read the cif file, create a map of Molecule, and generate 
    the topology file'''

    # rfix string in topology file
    word_to_replace = "!RESIDUE-REPLACEMENT"  
    patch_text = "PATCHING FIRS NONE LAST NONE \n\n"  

    topGen = TopGenerate(mof_file)
    topGen.DetectTag()
    topGen.ReadCharges()

    # Insert the residue information in to the topology file
    # and calculate the Net charge 
    netcharge = 0.0
    for mol in topGen.moleculeMap:
        uf.replace_text(top_file, word_to_replace, mol.GetRes() + word_to_replace)
        uf.replace_text(top_file, word_to_replace, mol.GetAtom() + word_to_replace)
        uf.replace_text(top_file, word_to_replace, patch_text + word_to_replace)
        netcharge += mol.avgCharge * float(mol.molCount)

    uf.replace_text(top_file, word_to_replace, "\n \nEND")
    print("    Net charge for %s: %.6f" % (mof_file, netcharge))