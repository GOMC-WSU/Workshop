puts "\n\n Creating PDB file for MOFNAME !\n\n"
#set your file name without ".xyz"
###################################
set filename MOFNAME
###################################
set topology ./TOPFILENAME
set output   "$filename\_BOX_0"
set Molname  [string range "$filename" 0 3]

mol load xyz "$filename.xyz"

set all [atomselect top all]

$all set resname "$Molname"
$all set chain "A"
$all set resid 1

$all set occupancy 0.0
$all set beta 1.0

$all writepdb "$output.pdb"

puts "Finished creating PDB file for MOFNAME.xyz !\n"
puts "################################################################################"
puts "\n\n Creating PSF file for MOFNAME !\n\n"

package require psfgen
resetpsf 
topology "$topology"

segment "$Molname" {
	pdb "$output.pdb"
	first none
	last none
}
coordpdb "$output.pdb" "$Molname"
writepsf "$output.psf"


puts "\n\nFinished Generating PSF files for MOFNAME_BOX_0.pdb !\n\n"
puts "################################################################################"