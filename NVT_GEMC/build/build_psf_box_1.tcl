psfgen<<ENDMOL

topology ./top_NobleGases.inp

segment AR {
    pdb ./packed_argon_vap.pdb
    first none
    last none
}

coordpdb ./packed_argon_vap.pdb AR

writepsf ./START_BOX_1.psf
writepdb ./START_BOX_1.pdb
