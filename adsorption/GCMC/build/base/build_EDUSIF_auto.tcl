#set your file name without ".pdb"
###################################
set filename EDUSIF_clean_min_modified
set topology "../topology_EDUSIF.inp"
set output   IRMOF_1_BOX_0
###################################
set infile "$filename.pdb"
mol load pdb "$filename.pdb"
set all [atomselect top all]
lappend totnameArr [$all get resname]

#find the unique resname
set totmolsize [llength [lindex $totnameArr 0]]
set currentN " "
for {set i 0} {$i < $totmolsize} {incr i} {
    set thisName [lindex $totnameArr 0 $i]
    if {"$currentN" ne "$thisName"} {
	lappend nameArr $thisName
	unset currentN
	set currentN $thisName
    }
}

# export each residue name to their file
set molsize [llength $nameArr]
for {set i 0} {$i < $molsize} {incr i} {
    set thisName [lindex $nameArr $i]
    exec grep -w "$thisName" "$infile" > "$thisName.pdb"
}

###################################################
# make segment
package require psfgen
resetpsf 
topology "$topology"

for {set i 0} {$i < $molsize} {incr i} {
    set thisName [lindex $nameArr $i]
    segment "$thisName" {
	pdb "$thisName.pdb"
	first none
	last none
    }
}

# read the exported residue file
for {set i 0} {$i < $molsize} {incr i} {
    set thisName [lindex $nameArr $i]
    #Read coordinates
    coordpdb "$thisName.pdb" "$thisName"
}

# print out pdb and psf file
writepsf "$output.psf"
writepdb "$output.pdb"

for {set i 0} {$i < $molsize} {incr i} {
    set thisName [lindex $nameArr $i]
    file delete "$thisName.pdb"
}
