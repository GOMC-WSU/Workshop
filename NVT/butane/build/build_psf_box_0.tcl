package require psfgen

topology ./top_butane_ua.top

segment C4A {
    pdb ./packed_butane.pdb
    first none
    last none
}

coordpdb ./packed_butane.pdb C4A

writepsf ./START_BOX_0.psf
writepdb ./START_BOX_0.pdb
