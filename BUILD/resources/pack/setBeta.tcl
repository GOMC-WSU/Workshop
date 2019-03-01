puts "Setting Beta to 1.0 for MOFNAME_BOX_0.pdb !\n"

#set your file name without ".pdb"
###################################
set input   MOFNAME_BOX_0
###################################
mol load pdb "$input.pdb"
set all [atomselect top all]
$all set occupancy 0.0
$all set beta 1.0
$all writepdb "$input.pdb"

puts "Finished setting Beta to 1.0 for MOFNAME_BOX_0.pdb !\n"
puts "################################################################################\n\n"
