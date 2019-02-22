#set your file name without ".pdb"
###################################
set filename EDUSIF_clean_min_modified
set topology ../../../BUILD/resources/model/Top_Universal.inp
set output   IRMOF-1_BOX_0
###################################
set infile "$filename.pdb"
mol load pdb "$filename.pdb"
set all [atomselect top all]
lappend totnameArr [$all get resname]

#find the unique resname
set totmolsize [llength [lindex $totnameArr 0]]
set currentN " "
for {set i 0} {$i < $totmolsize} {incr i} {
    if { "$i" eq "0" } {
	set thisName [lindex $totnameArr 0 $i]
	lappend nameArr $thisName
    } else {
	set thisName [lindex $totnameArr 0 $i]
	set ms [llength $nameArr]
	set exist 0
	#check to see if it is already exist in the list
	for {set j 0} {$j < $ms} {incr j} {
	    set currentN [lindex $nameArr $j]
	    if {"$currentN" eq "$thisName"} {
		set exist 1
	    }
	}
	if {"$exist" eq "0"} {
	    lappend nameArr $thisName
	}
    }
}

# reassign chain, resID and export each residue name to their file
set molsize [llength $nameArr]
set chainN A
for {set i 0} {$i < $molsize} {incr i} {
    set thisName [lindex $nameArr $i]
    set selection [atomselect top "resname $thisName"]
    $selection set chain "$chainN"
    #sort the resID
    lappend subSel [$selection get index]
    set atomsize [llength [lindex $subSel 0]]
    for {set j 0} {$j < $atomsize} {incr j} {
	set indx [lindex $subSel 0 $j]
	set temp [atomselect top "resname $thisName and index $indx"]
	$temp set resid [expr $j + 1]
    }
    unset subSel
    $selection writepdb "$thisName.pdb"
    #increament the chain for next residue
    set ascii [scan $chainN {%c}]
    incr ascii
    set chainN [format {%c} $ascii]
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
