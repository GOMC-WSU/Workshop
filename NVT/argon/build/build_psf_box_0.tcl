psfgen<<ENDMOL

topology ./top_NobleGases.inp

segment AR {
    pdb ./packed_argon.pdb
    first none
    last none
}

coordpdb ./packed_argon.pdb AR

writepsf ./START_BOX_0.psf
writepdb ./START_BOX_0.pdb
