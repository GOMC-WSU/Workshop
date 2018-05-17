#!/bin/bash

g++ -O3 patch.cpp stoi.cpp -o patch.out

gfortran -O3 pconv.f90 -o pconv

gfortran -O3 phase.f90 -o phase.out

gfortran -O3  pvt.f90 -o pvt.out

cp pvt.out ../pvt/.
cp phase.out ../.
cp patch.out ../.
cp patch.out ../pvt/.
cp pconv ../.
