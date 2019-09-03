package require psfgen

topology ./top_NobleGases.inp

segment AR {
    pdb ./packed_argon_liq.pdb
    first none
    last none
}

coordpdb ./packed_argon_liq.pdb AR

writepsf ./START_BOX_0.psf
writepdb ./START_BOX_0.pdb
