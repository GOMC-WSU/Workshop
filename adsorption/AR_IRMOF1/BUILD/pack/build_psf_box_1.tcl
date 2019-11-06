puts "Generatinf PDB and PSF files for packed_ADSBNAME.pdb !\n"

package require psfgen

topology ./TOPFILENAME

segment ADSBSET {
    pdb packed_ADSBNAME.pdb
    first none
    last none
}

coordpdb ./packed_ADSBNAME.pdb ADSBSET

writepsf ./START_BOX_1.psf
writepdb ./START_BOX_1.pdb

puts "Finished Generatinf PDB and PSF files for packed_ADSBNAME.pdb !\n"
puts "################################################################################\n\n"
