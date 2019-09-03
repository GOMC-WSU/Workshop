psfgen<<ENDMOL

topology ./top_NobleGases.inp

exec grep "AR" packed_argon_krypton_vap.pdb > Ar.pdb
exec grep "KR" packed_argon_krypton_vap.pdb > Kr.pdb

segment AR {
    pdb ./Ar.pdb
    first none
    last none
}

segment KR {
    pdb ./Kr.pdb
    first none
    last none
}

coordpdb ./Ar.pdb AR
coordpdb ./Kr.pdb KR

writepsf ./START_BOX_1.psf
writepdb ./START_BOX_1.pdb

file delete Ar.pdb
file delete Kr.pdb
