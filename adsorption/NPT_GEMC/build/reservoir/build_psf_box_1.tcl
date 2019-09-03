package require psfgen

topology ../topology_EDUSIF.inp

segment AR {
    pdb ./packed_argon.pdb
    first none
    last none
}

coordpdb ./packed_argon.pdb AR

writepsf ./START_BOX_1.psf
writepdb ./START_BOX_1.pdb
