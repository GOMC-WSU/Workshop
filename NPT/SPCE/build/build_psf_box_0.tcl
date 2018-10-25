package require psfgen

topology ./top_SPCE_water.inp

segment SPCE {
    pdb ./packed_water.pdb
    first none
    last none
}

coordpdb ./packed_water.pdb SPCE

writepsf ./START_BOX_0.psf
writepdb ./START_BOX_0.pdb
