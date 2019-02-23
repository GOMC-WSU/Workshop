package require psfgen

topology BASEDIR/BUILD/resources/model/TOPFILENAME

segment ADSBSET {
    pdb packed_ADSBNAME.pdb
    first none
    last none
}

coordpdb ./packed_ADSBNAME.pdb ADSBSET

writepsf ./START_BOX_1.psf
writepdb ./START_BOX_1.pdb
