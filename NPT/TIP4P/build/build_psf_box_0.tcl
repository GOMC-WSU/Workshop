package require psfgen

topology ./top_TIP4P_water.inp

segment TIP4 {
    pdb ./packed_water.pdb
    first none
    last none
}

coordpdb ./packed_water.pdb TIP4

writepsf ./START_BOX_0.psf
writepdb ./START_BOX_0.pdb
