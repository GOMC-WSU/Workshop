#set your file name without ".xyz"
###################################
set filename MOFNAME_clean_min
###################################
set outfile "$filename\_modified"
mol load xyz "$filename.xyz"

set all [atomselect top all]
lappend indexArr [$all get index]
lappend nameArr [$all get name]

set currentN [lindex $nameArr 0 0]
set chainN A 

$all set occupancy 0.0
$all set beta 1.0

set atomsize [llength [lindex $indexArr 0]]
set j 0
for {set i 0} {$i < $atomsize} {incr i} {
    set temp [atomselect top "index $i"]
    set thisName [lindex $nameArr 0 $i]

    #check to see if atom type changed
    if {"$currentN" ne "$thisName"} {
	unset currentN
	set currentN $thisName
	#increamnet the chain letter
	set ascii [scan $chainN {%c}]
	incr ascii
	#set chainN [format {%c} $ascii]
	set j 0
    }
    incr j
    $temp set resname [lindex $nameArr 0 $i]
    $temp set name [lindex $nameArr 0 $i]
    $temp set chain "$chainN"
    $temp set resid $j

    unset temp
}

$all set occupancy 0.0
$all set beta 1.0

$all writepdb "$outfile.pdb"
