psfgen<<ENDMOL

topology ./top_mC6cycle.inp

segment 1C6 {
    pdb ./packed_mC6cycle_vap.pdb
    first none
    last none
}

coordpdb ./packed_mC6cycle_vap.pdb 1C6

writepsf ./START_BOX_1.psf
writepdb ./START_BOX_1.pdb
