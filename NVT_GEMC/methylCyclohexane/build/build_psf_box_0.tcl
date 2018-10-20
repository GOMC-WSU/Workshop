psfgen<<ENDMOL

topology ./top_mC6cycle.inp

segment 1C6 {
    pdb ./packed_mC6cycle_liq.pdb
    first none
    last none
}

coordpdb ./packed_mC6cycle_liq.pdb 1C6

writepsf ./START_BOX_0.psf
writepdb ./START_BOX_0.pdb
