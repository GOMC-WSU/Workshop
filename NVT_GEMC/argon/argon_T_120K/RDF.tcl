# set file name and loading pdb file
set filename  Argon_GEMC_T_120K_BOX_0.pdb
mol load pdb $filename

#get information from user
set rcut 14
set stepSize 0.1
set startFr 50

# atom selection
set sel1 "AR"
set sel2 "AR"
set selAll [atomselect top all]	

#file name
set writer [open "RDF_$sel1\_$sel2.dat" w]

#print header
puts $writer "#Radial Distribution Function"
puts $writer " "

#get number of frame 	
set nframes [molinfo top get numframes]
set lenFrame [expr ($nframes - $startFr)]

#getting information of box size in each frame
lappend BoxDim [exec grep CRYST1 "$filename" | awk "{print \$2}"]

#define an two dimension array for results
set data [expr int($rcut/$stepSize) + 1]
for {set i 0} { $i < $data } {incr i} {
    lappend RDF [list {*}"0 0"]
}

#RDF calculation
for {set j $startFr} {$j < $nframes} {incr j} {	
    
    set AllSel1 [atomselect top "name $sel1 and x != 0.0 and y != 0.0 and z !=0.0" frame $j]
    set AllSel2 [atomselect top "name $sel2 and x != 0.0 and y != 0.0 and z !=0.0" frame $j]


    set BoxL [lindex $BoxDim 0 $j]
    pbc set "$BoxL $BoxL $BoxL"
    set temRDF [measure gofr $AllSel1 $AllSel2 delta $stepSize rmax  $rcut usepbc 1]

    set ri [lindex $temRDF 0]
    set gr [lindex $temRDF 1]
   
    for {set i 0} { $i < $data} {incr i} {

    lset RDF $i 1 [expr [lindex $RDF $i 1] + [lindex $gr $i] ]
    lset RDF $i 0 [lindex $ri $i]
    }

    unset AllSel1
    unset AllSel2
    unset BoxL
    unset temRDF
    unset ri
    unset gr
}

#taking average of frames
    for {set i 0} { $i < $data } {incr i} {
	lset RDF $i 1 [expr [lindex $RDF $i 1]/$lenFrame]
    }
#print output to file
    for {set i 0} { $i < $data } {incr i} {
	puts $writer [lindex $RDF $i]
    }				

close $writer




