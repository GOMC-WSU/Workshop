import os
import re
import math
import glob
import sys


# replace it in topology file
word_to_replace = "!RESIDUE-REPLACEMENT"  
patch_text = "PATCHING FIRS NONE LAST NONE \n\n"    

mof_file= "MOF-FILENAME"
top_file = "TOP-FILENAME"
mof_name = mof_file.split('_')[0]


class molecule(object):
    ''' Holds the residue name, type, number of residue
    average charge
    Attributes:
        resname: string
        restype: string
        molCount: int
        avgCharge: float '''

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


def MolExist(allmol, atom, charge):
    ''' If molecule already exist, we just add the charge
    otherwise, we append it to the list'''
    exist = False
    for mol in allmol:
        if(mol.resname == atom.upper()):
            exist = True
    
    if not exist:
        allmol.append(molecule(atom, charge))
    else:
        for mol in allmol:
            if(mol.resname == atom.upper()):
                mol.AddCharge(charge)


def replace_text(filename, text_to_search, replacement_text):
    '''This function will replace <text_to_search> text with
    <replacement_text> string in <filename>'''
    with open(filename, 'r') as file:
        filedata = file.read()
    filedata = filedata.replace(text_to_search, replacement_text)
    with open(filename, 'w') as file:
        file.write(filedata)


#########################################
# Main function
allMolecule = []
reachedAtom = False
elect = False
keywordfound = True

#find the correct atom tag
with open(mof_file, 'r') as infile:
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
    print("ERROR: No tag detected to read the atom data in " + mof_file)
    print("Available tag: '_atom_site_charge' or '_atom_site_type_symbol'")
    sys.exit(-1)


with open(mof_file, 'r') as file:
    for line in file:
        line = re.sub(' +', ' ', line).strip()
        if line.startswith(keyword):
            reachedAtom = True
            continue
        
        if(reachedAtom):
            atom = line.split(' ')[0]
            if elect:
                charge = line.split(' ')[4]
            else:
                charge = str(0.0)
            MolExist(allMolecule, atom, charge)


# Insert the residue information in to the topology file
# and calculate the Net charge 
netcharge = 0.0
for mol in allMolecule:
    replace_text(top_file, word_to_replace, mol.GetRes() + word_to_replace)
    replace_text(top_file, word_to_replace, mol.GetAtom() + word_to_replace)
    replace_text(top_file, word_to_replace, patch_text + word_to_replace)
    netcharge += mol.avgCharge * float(mol.molCount)

replace_text(top_file, word_to_replace, "\n \nEND")
print("Net charge for %s: %.6f" % (mof_name, netcharge))