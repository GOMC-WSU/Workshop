package require psfgen

topology ../topology_EDUSIF.inp

segment CO2 {
    pdb ./packed_CO2.pdb
    first none
    last none
}

coordpdb ./packed_CO2.pdb CO2

writepsf ./START_BOX_1.psf
writepdb ./START_BOX_1.pdb
