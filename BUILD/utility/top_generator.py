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
        molCount: int
        atomname: string
        restype: string
        segment: string
        atomCharge: float 
    '''

    def __init__(self, atomName, atomcharge):
        self.molCount = 1
        self.atomName = atomName
        self.atomCharge = float(atomcharge)
        #All resname might have different charge but they have same type
        #We remove any number from restype
        self.restype = uf.GetString(atomName)
        #segment holds restype, only char without any number. 
        self.segment = self.restype

    def AddCharge(self):
        self.molCount += 1


    def GetAtom(self):
        out = "ATOM  %5s   %3s   %.6f  !\n" % (self.atomName, self.restype, self.atomCharge)
        return out

    def PrintSummary(self):
        print(self.GetAtom())
        print("PATCHING FIRS NONE LAST NONE \n\n")



class TopGenerate(object):
    ''' Generate topology file from cif file. Using charge defined 
    in cif files.
    Attributes:
        mof_file = string, molf file with no path included
        startTag = string, tag in cif file to start reading atom info
        endTag = string, tag in cif file to end reading atom info
        hasCharge = boolean, if cif has has charge information
        totalCharge = float, summation of total charge
        chargeAccuracy = int, number of decimal to read from charge
        moleculeMap = Molecule, list of all molecules

        tag_x_indx = index to read x fractional coordinate
        tag_y_indx = index to read y fractional coordinate
        tag_z_indx = index to read z fractional coordinate
        tag_charge_indx = index to read charge
        tag_symbol_indx = index to read atom symbol
    '''

    def __init__(self, mof): 
        self.mof_file = mof
        self.hasCharge = False
        self.totalCharge = 0.0
        self.startTag = ""
        self.endTag = "END"
        self.moleculeMap = []
        self.tag_x_indx = 0
        self.tag_y_indx = 0
        self.tag_z_indx = 0
        self.tag_charge_indx = 0
        self.tag_symbol_indx = 0
        self.chargeAccuracy = 7

    def DetectTag(self): 
        ''' Detect the tag in cif file.'''
        tag_loop = "loop_"
        tag_symbol = "_atom_site_type_symbol"
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
                    if(self.tag_z_indx != 0):
                        #avoid reading extra loop tag at the end
                        self.endTag = line
                        break
                    idx = 0
                elif line.startswith(tag_symbol):
                    self.tag_symbol_indx = idx
                    self.startTag = line
                    idx = idx + 1
                elif line.startswith(tag_x):
                    self.tag_x_indx = idx
                    self.startTag = line
                    idx = idx + 1
                elif line.startswith(tag_y):
                    self.tag_y_indx = idx
                    self.startTag = line
                    idx = idx + 1
                elif line.startswith(tag_z):
                    self.tag_z_indx = idx
                    self.startTag = line
                    idx = idx + 1
                elif line.startswith(tag_charge):
                    self.tag_charge_indx = idx
                    self.hasCharge = True
                    idx = idx + 1
                    self.startTag = line
                else:
                    idx = idx + 1
                    if line.startswith("_"):
                        self.startTag = line

        if (self.tag_x_indx == 0 or self.tag_y_indx == 0 or self.tag_z_indx == 0):
            print("ERROR: No tag detected to read the atom data in " + self.mof_file)
            print("Available tags: %s %s %s" %(tag_x, tag_y, tag_z))
            sys.exit(-1)


    def AddMol(self, atomName, charge):
        ''' If molecule already exist with same charge, we just add the charge
        otherwise, we append it to the list with new name'''
        newCharge = round(float(charge), self.chargeAccuracy)
        exist = False
        counter = 0
        segment = uf.GetString(atomName)
        for mol in self.moleculeMap:
            if(abs(mol.atomCharge - newCharge) < 10**(-self.chargeAccuracy)):
                if(mol.segment == segment):
                    exist = True
                    index = counter
                    break
            counter += 1
        
        if(exist):
            #If we could find atomName with same charge and segment name, no need to add molecule
            # we just add the charge to the existing molecule
            self.moleculeMap[index].AddCharge() 
        else:
            #We need to find the atomName with same segment. Start from 1
            counter = 1
            for mol in self.moleculeMap:
                if(mol.segment == segment):
                    counter += 1

            newName = atomName + str(counter)
            if(len(newName) > 4):
                print("ERROR: In PDB file atom name cannot be more than 4 Character: %s \n", newName)
                sys.exit(-1)
                
            self.moleculeMap.append(Molecule(newName, newCharge))
  
    def GetAtomName(self, atomName, charge):
        '''Find the molecule with same segment name and charge, 
        and return the atomName'''
        charge = round(charge, self.chargeAccuracy)
        segment = uf.GetString(atomName)
        for mol in self.moleculeMap:
            if(abs(mol.atomCharge - charge) < 10**(-self.chargeAccuracy)):
                if(mol.segment == segment):
                    return mol.atomName


    def ReadCharges(self):
        ''' Read and calcuate the average charges for molecules in cif file.
        Update the list of molecule in class'''
        reachedAtom = False
        netCharge = 0.0

        with open(self.mof_file, 'r') as file:
            for line in file:
                line = re.sub(' +', ' ', line).strip()
                if line.startswith(self.startTag):
                    reachedAtom = True
                    continue

                if(reachedAtom):
                    if(line.startswith(self.endTag)):
                        break
                    
                    atom = line.split(' ')[self.tag_symbol_indx]
                    if self.hasCharge:
                        charge = line.split(' ')[self.tag_charge_indx]
                    else:
                        charge = "0.0"

                    self.AddMol(atom, charge)
                    netCharge += round(float(charge), self.chargeAccuracy)

        self.totalCharge = netCharge
                       


def MakeTopology(topGen, top_file, extension):
    ''' Read the cif file, create a map of Molecule, and generate 
    the topology file'''

    # rfix string in topology file
    word_to_replace = "!RESIDUE-REPLACEMENT"  
    patch_text = "PATCHING FIRS NONE LAST NONE \n\n"  

    #topGen.DetectTag()
    #topGen.ReadCharges()
    netcharge = topGen.totalCharge * extension
    resname = topGen.mof_file[:4]

    # Insert the residue information in to the topology file
    out = "RESI  %5s         %.6f  !\n" % (resname, netcharge)
    uf.replace_text(top_file, word_to_replace, out + word_to_replace)

    for mol in topGen.moleculeMap:
        for i in range(mol.molCount * extension):
            uf.replace_text(top_file, word_to_replace, mol.GetAtom() + word_to_replace)

    uf.replace_text(top_file, word_to_replace, patch_text + word_to_replace)
    uf.replace_text(top_file, word_to_replace, "\n \nEND")
    print("           Net charge for %s: %.6f" % (topGen.mof_file, netcharge))