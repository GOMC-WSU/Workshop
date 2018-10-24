program pconv

! this program converts data from phase.dat to data useful for plots

! 8/31/00 Added Gibbs free energy of transfer V3
! V4_1 - Modified for phlst_v8 file format
! V4_1 - heat of vaporization calculation added 2/17/03
! V8 - renamed to match phase version numbering.
!  6/24/05  Modified output file to split T vs. Rho data into
!  Separate liquid and vapor pieces for use in XMGRACE
implicit none

double precision, parameter :: avo_num = 6.022d23
double precision, parameter :: kb = 1.38d-23
double precision, parameter :: param_ang = 1.d-10
double precision, parameter :: param_kg = 1000.
double precision, parameter :: gas_const = 8.314e-3 ! KJ/mol K

integer iostat
integer icount
integer icomp,ncomp
double precision dum
double precision lnZliq,lnZgas,lnZ0
double precision ntliq,ntgas
double precision rho_liq, rho_gas
double precision temp,press,vol
double precision, dimension(:), allocatable :: mu
double precision, dimension(:), allocatable :: mw
double precision, dimension(:), allocatable :: nliq
double precision, dimension(:), allocatable :: ngas
double precision, dimension(:), allocatable :: xliq
double precision, dimension(:), allocatable :: xgas
double precision, dimension(:), allocatable :: dg
double precision dhv ! heat of vaporization kJ/mol
double precision pv_gas, pv_liq
double precision energy_gas, energy_liq
double precision u_gas, u_liq
logical lmono
logical llj
logical lreal
lmono = .false.
llj = .false.
lreal = .true.

if (lmono) write(*,*) 'MONOLAYER MODE'
if (llj) write(*,*) 'LENNARD-JONES MODE'
if (lreal) write(*,*) 'REAL FLUID MODE'
open(1, file = 'phase.dat', status = 'old')

read(1,*) ncomp,vol,lnZ0
allocate(mu(1:ncomp))
allocate(mw(1:ncomp))
allocate(nliq(1:ncomp))
allocate(ngas(1:ncomp))
allocate(xliq(1:ncomp))
allocate(xgas(1:ncomp))
allocate(dg(1:ncomp))
read(1,*) (mw(icomp),icomp=1,ncomp)
read(1,*)
read(1,*)

open(2, file = 'phgph.dat', status = 'unknown')
write(2,'(A,5x,A,10x,A,8x,A,8x,A,8x,A,9x,A)') 'Number', '     Temp', &
	'Chemical Potentials', 'Rho_liq', 'Rho_gas','Press', &
 	 'Mole Fractions'
open(3,file = 'trho.dat', status='unknown')
open(4,file = 'tp.dat', status = 'unknown')

open(5,file = 'prho.dat', status = 'unknown')
open(7,file = 'pxy.dat', status = 'unknown')
open(8,file = 'dg.dat', status = 'unknown')
open(9,file = 'dhv.dat', status = 'unknown')

open(10,file = 'trho_liq.dat', status='unknown')
open(11,file = 'trho_vap.dat', status='unknown')
open(12,file = 'pxy1.dat', status='unknown')
open(13,file = 'pxy2.dat', status='unknown')
iostat = 0
icount = 0
do while (iostat /= -1)
	ntliq = 0.0
	ntgas = 0.0
	rho_liq = 0.0
	rho_gas = 0.0
	xliq = 0.
	xgas = 0.0

	read(1,*,iostat=iostat) temp,(mu(icomp),icomp=1,ncomp), &
	energy_liq,energy_gas,(nliq(icomp),icomp=1,ncomp),&
        (ngas(icomp),icomp=1,ncomp),lnZliq,lnZgas
	
!	write(*,*) temp,mu,nliq,ngas
	if(iostat /= -1) then
		icount = icount + 1
		do icomp = 1, ncomp
			ntliq = ntliq + nliq(icomp)
			ntgas = ntgas + ngas(icomp)

			rho_liq = rho_liq + mw(icomp)*nliq(icomp)
			rho_gas = rho_gas + mw(icomp)*ngas(icomp)
			
!  Free energy of transfer calculation.  Volumes cancel out since this is 
!  grand canonical (liquid and vapor phases have the same volume)
!  Transfer from vapor to liquid
		
			dg(icomp) = -gas_const*temp* &
     				    log(nliq(icomp)/ngas(icomp))
		
		enddo
	
		if (lmono) then
			rho_liq = rho_liq/(vol)*100.
			rho_gas = rho_gas/(vol)*100. 

		else if(llj) then
			rho_liq = rho_liq/vol
			rho_gas = rho_gas/vol
		else if(lreal) then
			rho_liq = rho_liq/avo_num/(vol*param_ang**3)/param_kg
			rho_gas = rho_gas/avo_num/(vol*param_ang**3)/param_kg
		end if 

		do icomp = 1, ncomp
			xliq(icomp) = nliq(icomp)/ntliq
			xgas(icomp) = ngas(icomp)/ntgas
		enddo

! pressure is in bar

		if (lreal) then 
		   press = (lnZliq - lnZ0)*temp*kb/vol/param_ang**3/100000.
		else if (llj) then
		   press = (lnZliq - lnZ0)*temp/vol
		end if
		
! Heat of vaporization

                if (lreal) then
                   pv_liq = (press*1.0d5)*vol*param_ang**3/ntliq*avo_num
                   u_liq =energy_liq/ntliq*8.314

                   pv_gas = press*1.0d5*vol*param_ang**3/ntgas*avo_num
                   u_gas=energy_gas/ntgas*8.314
                   dhv = (u_gas+pv_gas - (u_liq+pv_liq))/1000.0d0 ! dhv kJ/mol
                endif
!		write(2,'(f12.4,2x,2f14.5,2x,f12.4,2x,<ncomp>f12.5,2x,<ncomp>f12.5)') &
		write(2,'(i5,2x,20(f12.5,2x))') icount, &
		temp,(mu(icomp),icomp=1,ncomp),rho_liq,rho_gas,press,&
			(xliq(icomp),icomp=1,ncomp), &
			(xgas(icomp),icomp=1,ncomp)

		write(3, '(20(f12.5,2x))') &
			temp,rho_liq,rho_gas

		write(4,'(20(f12.5,2x))') temp, press

		write(5,'(20(f12.5,2x))') press, rho_liq,rho_gas
		if (ncomp > 1) then
	   	   write(7,'(20(f12.5,2x))') press, xliq(1), xgas(1)
	           write(12,'(20(f12.5,2x))') xliq(1), press
                   write(13,'(20(f12.5,2x))') xgas(1), press
		endif
		write(8,'(20(f12.5,2x))') xliq(1),xgas(1), (dg(icomp),icomp=1,ncomp)
                write(9,*) temp, dhv
                
                write(10, '(20(f12.5,2x))') rho_liq, temp
                write(11, '(20(f12.5,2x))') rho_gas, temp
		endif 
	enddo
close(1)
close(2)
close(3)
close(4)
close(5)
close(7)
close(8)
close(9)
close(10)
close(11)
end
