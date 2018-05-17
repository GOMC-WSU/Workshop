MODULE hdata
	integer ncomp
	integer nfiles ! number of files being read
	integer tnum	! temperature counter
	character*20, dimension(:), allocatable :: filename
        integer, dimension(:,:), allocatable :: m_partf
        integer, dimension(:,:), allocatable :: m_part
	double precision betap		! trial parameters
	double precision, dimension(:), allocatable :: nliq
        double precision, dimension(:), allocatable :: ngas
        double precision, dimension(:), allocatable :: avgnum ! average number of each particle type
	double precision Z,Zgas,Zliq	! partition function, exponent of calculation
	double precision, dimension(:), allocatable :: nmid	! mid-point number of particles on coexistence
	double precision, dimension(:), allocatable :: slope	! slope of line separating two phases
	double precision, dimension(:), allocatable :: beta
	double precision, dimension(:,:), allocatable :: mu
	double precision, dimension(:), allocatable :: mup
	integer, dimension(:), allocatable :: nentry
	double precision, dimension(:), allocatable :: weight	
	double precision, dimension(:), allocatable :: oldweight
	double precision, dimension(:,:), allocatable :: dens ! n distribution
        double precision energy_gas,energy_liq
	!define data type - this is to required to reduce memory usage
	type column1
		integer, pointer ::flength(:) ! Number of entries in the file
	end type
	type column2
		double precision, pointer :: flength2(:) ! Number of entries in the file
	end type
	type(column1), dimension(:,:), allocatable :: n
	type(column2), dimension(:), allocatable :: e

END MODULE hdata

program phase

! version 1.1 - 11/24/97  This program iterates to find the weights for
! patching the individual histograms together.  The histogram data is read
! in the form of N1, N2, E for each configuration.  Reads the weights in
! from the convergence program 'nwfsp1.f90'.

! modifications
! 11/24/97 - added code to calculate the average energy of each phase

! 3/9/98 - added a scheme to calculate the midpoint of the energy 
! distribution.  This allows the histograms to be added together in
! any order.

! 5/28/98 - modified storage of histogram lists to minimize memory
!           usage.

! 12/16/98 - changed iteration method from bisection to Newton's: V4.
! 11/16/99 - extended program from binary to n-component mixtures: V5
!	     merged phlst and pvt programs : V6

! 1/5/2000 - Added fixed pressure phase coexistence calculation. V7
!	     The chemical potential of the last component is varied to 
!	     get the correct pressure.

! 10/18/02 - Added calculation of the intermolecular energy of each phase V8


USE hdata
implicit none
! LIST FORMAT VARIABLES
character(2) suffix	! run suffix
integer, parameter :: maxpart = 100000
integer, parameter :: mentry = 1000000	! maximum number of observations
real, parameter :: tolerance = 5e-3 ! tolerance for convergence of weights
integer iostat				! iostat becomes -1 on end-of-file
integer ipart,i	! local counters
integer icomp,jcomp,ncomp2
integer ifile,jfile,kfile,iter
integer, dimension(:,:), allocatable :: n_temp ! temp array for n_1...n_n
double precision e_temp(mentry)			! energy temp array
double precision, dimension(:,:), allocatable :: mu_temp
double precision eng_min,eng_max 	!min and max of energies stored in the lists
double precision prob,maxd,val,y,ylog,tmp1	
double precision xdim,ydim,zdim	! linear dimensions of box on which data were taken
double precision xdim1,ydim1,zdim1	! linear dimensions of box for current file


!PHASE COEXISTENCE VARIABLES
integer, parameter :: maxtemp = 100	! maximun number of temperatures 
integer, parameter :: maxiter = 500	! maximum iterations for phase equil.
integer ntemp	! number of temperatures to calc phase coexistence
integer minp,maxp
double precision avg
double precision dmu1p
double precision, dimension(:), allocatable :: dmup
double precision nbelow, nbelow1	 ! for Newton's method
double precision mu2min(maxtemp),mu2max(maxtemp)
double precision mu2_incr(maxtemp)	! for calculation of phase diagram
double precision, dimension(:), allocatable ::mw
double precision ref_point ! lnZ0
double precision t_new(maxtemp)
character*20 ftemp,ftemp2,ftemp3,fname,fname2,fname3	!internal read/write for file naming

! FLAGS FOR PVT OR PHASE COEXISTENCE CALCULATIONS
logical lphase	! lphase = .true. => phase coexistence calculation
logical lpvt	! lpvt = .true. => pvt calculation
logical lfixp   ! lfixp = .true. => constant pressure
!VARIABLES FOR FIXED PRESSURE DIAGRAMS
double precision, parameter :: pconverg = 1e-3
integer flip2			! number of sign changes
integer iter2			! number of pressure iterations
double precision, parameter ::	ctbar = 138.0
double precision oldsign2,newsign2,sign2	! sign difference between calc'd press and spec'd
double precision diff2			! difference in press-pset
double precision pset				! specified pressure
double precision press			! calculated pressure
double precision lnZ0				! constant for pressure
double precision vol				! volume of the system

! VARIABLES FOR PHASE COEXISTENCE PRINTOUTS
integer j,num
character*20 file


lphase = .true. ! true = calculate phase diagram
lpvt = .false. ! true = calculate pvt properties
lfixp = .false. ! true = constant pressure calculation

write(*,*) 'PHASE VERSION 8.0'
if(lphase .and. lpvt) then

	write(*,*) 'Can not do phase coexistence and PVT at the same time'
	write(*,*) 'Program terminating'
	stop
	
elseif (.not. lphase .and. .not. lpvt) then

	write(*,*) 'Must set lphase or lpvt = true'
	write(*,*) 'Program terminating'
	stop
	
end if

if (lphase) then

	write(*,*) 'PHASE COEXISTENCE MODE'
	if(lfixp) then
		write(*,*)
		write(*,*) 'FIXED PRESSURE MODE'
	end if
		
else if (lpvt) then

	write(*,*) 'PVT MODE'
	
end if 

allocate(nmid(maxtemp))
allocate(slope(maxtemp))
open(unit=2,file='input_fsp2.dat',status='old')
read(2,*) ncomp
read(2,*) nfiles
read(2,*) suffix

allocate(dmup(ncomp))
allocate(mw(ncomp))
allocate(avgnum(ncomp))
allocate(ngas(ncomp))
allocate(nliq(ncomp))
allocate(n(ncomp,nfiles))
allocate(n_temp(ncomp,mentry))
allocate(e(nfiles))
allocate(filename(nfiles))
allocate(beta(nfiles))
allocate(mu(ncomp,nfiles))
allocate(mup(ncomp))
allocate(mu_temp(maxtemp,ncomp))
allocate(nentry(nfiles))
allocate(weight(nfiles))
allocate(oldweight(nfiles))
allocate(m_part(2,ncomp))
allocate(m_partf(2,ncomp))

do ifile = 1,nfiles
  read(2,*) filename(ifile),nentry(ifile),oldweight(ifile),beta(ifile),&
            (mu(icomp,ifile),icomp=1,ncomp)
  beta(ifile) = 1./beta(ifile)
enddo

close(unit=2)

!write(*,*) ncomp,nfiles,suffix

eng_min = 1e5
eng_max = -1e5

do icomp = 1,ncomp
   m_part(1,icomp) = maxpart + 1
   m_part(2,icomp) = -1
enddo

write(*,'(A,5x,A,3x,A,3x,A,5x,A,2x,A,2x,A,2x,A,3x,A)')&
   'histogram','npoints','tstar',&
     'chemical potentials','min max n1 n2 etc'

write(*,'(A)') &
   '============================================================================'
do ifile= 1,nfiles

   do icomp = 1,ncomp      
       m_partf(1,icomp) = maxpart + 1
       m_partf(2,icomp) = -1
    enddo   
   		
    open (23,file='his'//trim(filename(ifile))//trim(suffix)//'.dat') 
    read (23,*) beta(ifile),ncomp2,(mu(icomp,ifile),icomp=1,ncomp2),&
                xdim1,ydim1,zdim1
		  
    if (ncomp.ne.ncomp2) then
       write(*,*) &
            'Number of components do not match in input_hs.dat and histogram'
       stop
    endif
!        write(*,*) beta,ncomp2,mu,xdim1,ydim1,zdim1 
    beta(ifile) = 1./beta(ifile)
    if (ifile==1) then
      xdim = xdim1
      ydim = ydim1
      zdim = zdim1
    else
      if (xdim1/=xdim.or.ydim1/=ydim.or.zdim1/=zdim) then
	write (*,*) 'System size or temperature in file ',trim(filename(ifile))//trim(suffix),' inconsistent with first file'
	stop
      endif
    endif
    iostat = 0 
    i = 0
    do while (iostat/=-1) 
      i = i + 1    
      if(i+1.gt.mentry) then
        write(*,'(A,2x,2f12.1)') 'maximum number of entries exceeded',&
			    nentry(ifile),mentry
	write(*,*) 'Increase mentry - > line 62'
        stop
      endif
        
      read (23,*,iostat=iostat) (n_temp(icomp,i),icomp=1,ncomp),e_temp(i)
      
      if(iostat.ne.-1) then
        eng_min = min(eng_min,e_temp(i))
        eng_max = max(eng_max,e_temp(i))

	do icomp=1,ncomp
            m_part(1,icomp) = min(n_temp(icomp,i),m_part(1,icomp))
            m_part(2,icomp) = max(n_temp(icomp,i),m_part(2,icomp))

            m_partf(1,icomp) = min(n_temp(icomp,i),m_partf(1,icomp))
            m_partf(2,icomp) = max(n_temp(icomp,i),m_partf(2,icomp))       
        enddo   

      endif
            
    enddo
    nentry(ifile) = i - 1
!    write(*,*) nentry(ifile)
    do icomp=1,ncomp     ! allocate n-particle arrays   
    	allocate(n(icomp,ifile)%flength(1:i-1))
	do j=1,i-1
	   n(icomp,ifile)%flength(j) = n_temp(icomp,j)
	enddo
    enddo
    
    allocate(e(ifile)%flength2(1:i-1))
    e(ifile)%flength2(1:i-1) = e_temp(1:nentry(ifile))
    if(ncomp.eq.1) then
       write(*,'(A,1x,i10,2x,f8.2,2x,f8.2,2x,i5,2x,i5)') &
         'his'//trim(filename(ifile))//trim(suffix)//'.dat', &
      nentry(ifile), 1./beta(ifile),(mu(icomp,ifile),icomp=1,ncomp),&
       ((m_partf(j,icomp),j=1,2), icomp=1,ncomp)
    elseif(ncomp.eq.2) then   
       write(*,'(A,1x,i10,2x,f8.2,2x,f8.2,2x,f8.2,2i6,1x,2i6)') &
         'his'//trim(filename(ifile))//trim(suffix)//'.dat', &
      nentry(ifile), 1./beta(ifile),(mu(icomp,ifile),icomp=1,ncomp), &
       ((m_partf(j,icomp),j=1,2), icomp=1,ncomp)
    else   
       write(*,'(A,1x,i10,2x,f8.2,2x,f8.2,2x,f8.2,2x,i10)') &
         'his'//trim(filename(ifile))//trim(suffix)//'.dat', &
      nentry(ifile), 1./beta(ifile),(mu(icomp,ifile),icomp=1,ncomp)
      write(*,'(T60,10i10)') ((m_partf(j,icomp),j=1,2), icomp=1,ncomp)
    endif         
enddo

dmup(1) = mu(1,1)/10000.  ! set increment for coexistence interation
vol = xdim*ydim*zdim  ! calculate system volume

if ( lfixp ) then
	if (ncomp < 2) then
		write(*,*) 'FIXED PRESSURE REQUIRES NCOMP > 1'
		write(*,*) 'PROGRAM TERMINATING'
		stop
	end if
	
	dmup(ncomp) = mu(ncomp,1)/1000.  
	
endif

minp = 100000
maxp = -100000
do icomp=1,ncomp
	minp = min(m_part(1,icomp),minp)
	maxp = max(m_part(2,icomp),maxp)
enddo

allocate(dens(ncomp,minp:maxp))

close(unit=23)
iter = 0 
maxd = 100
do while(maxd.gt.tolerance.and.iter.lt.1e4)
  iter = iter +1
  maxd = 0.0 
  do kfile = 1,nfiles
    weight(kfile) = 0.0
    do ifile = 1,nfiles      
      do i=1,nentry(ifile)
        y = 0.0
        ylog = -1e9  ! exp(ylog) = y = 0.0
        do jfile = 1,nfiles

	  prob = -(beta(jfile)-beta(kfile))*e(ifile)%flength2(i)
          do icomp=1,ncomp
             prob = prob + (beta(jfile)*mu(icomp,jfile)-beta(kfile)*mu(icomp,kfile))* &
                    n(icomp,ifile)%flength(i)
          enddo 
                
!         y = y+nentry(jfile)*exp(prob-log(oldweight(jfile)))
                   
! The following is a code rearrangement to avoid overflow problems
! This trick was compliments of Peter-Lawrence Montgomery 2/12/98
! Replace y with log(y)
! Define log_expsum(y,z) = log(exp(y)+exp(z)
! Evaluate log_expsum(y,z) = max(y,z) + log(1+exp(-abs(y-z)))

	  tmp1 = prob + log(nentry(jfile)/oldweight(jfile))	  
          ylog = max(ylog,tmp1) + log(1.+exp(-abs(ylog-tmp1)))
                          
        enddo
        weight(kfile) = weight(kfile)+exp(-ylog)      
      enddo
    enddo
    val = abs(weight(kfile)/oldweight(kfile)-1.)
    if (val.gt.maxd) maxd=val
  enddo 
!  write(*,'(8f15.4)') real(weight(1:nfiles))
  do i = 2,nfiles
    weight(i) = weight(i)/weight(1)
  enddo
  weight(1) = 1.0
  oldweight(1:nfiles)=weight(1:nfiles) 
  write(*,'(A,i5,5x,A,f12.6)') 'iteration = ',iter,'deviation = ',maxd    
enddo
open(unit=24, file='input_fsp2.dat',status='unknown')
write(24,*) ncomp
write(24,*) nfiles
write(24,*) suffix
do ifile=1,nfiles
   write(24,'(A5,i10.0,g15.6,10f14.4)') filename(ifile),nentry(ifile), &
   weight(ifile), 1./beta(ifile),(mu(icomp,ifile),icomp=1,ncomp)

!   write(24,*) filename(ifile),nentry(ifile),weight(ifile),&
!        1./beta(ifile),(mu(icomp,ifile),icomp=1,ncomp)  
enddo
write(24,*) 'total iterations = ',iter
close(24)

if (lphase) then

write(*,*) 'Starting coexistence calculation'
! start phase coexistence calculation
	
	open(unit=1,file='phinput.idat',status='old')
	if( lfixp ) then
		read(1,*)
		if(ncomp.gt.2) then
			read(1,*) mup(1),mup(ncomp-1),lnZ0,pset
		else
			read(1,*) mup(1),mup(ncomp),lnZ0,pset
		endif
		read(1,*)
	else
		read(1,*)
		read(1,*) mup(1), ref_point   ! initial guess
		read(1,*)
                read(1,*) (mw(icomp),icomp=1,ncomp)
		read(1,*)
	endif	
	open(unit=25, file='phase.dat', status = 'unknown')
	write(25, '(i2,5x,f8.2,3x,f10.6)') ncomp,xdim*ydim*zdim,ref_point
        write(25, '(f8.4,5x,f8.4)') (mw(icomp),icomp=1,ncomp)

	!write(25,'(A10,f8.1,A10,f8.4)') '# nmid = ', nmid(1),&
	!                                  'slope = ', slope(1)
	write (25,'(A,20A5/3h #,50A/3h #,50A)') '# Suffixes and Files = '&
	,suffix,(trim(filename(ifile)),ifile=1,nfiles)
	write (25,'(100A)') '#      T            mu1           mu2        Eng_liq         Eng_gas', &
        '       N_liq1          N_liq2        N_gas1         Ngas2  ln(Zliq) ln(Zgas)'
        close(25)
	
	iostat = 0
	i = 1
	do while(iostat.ne.-1)
   		read (1,*,iostat=iostat) t_new(i),mu2min(i),mu2max(i),&
                           mu2_incr(i),nmid(i),slope(i)
 
  		if(iostat.ne.-1) then
     			i = i + 1
  		endif
	enddo
close(1)

elseif (lpvt) then
	iostat = 0
	i=1
	open (28,file='pvt.dat',status='unknown')
	write (28,'(A,20A5/3h #,50A/3h /*,50A)') '# Suffixes and Files = '&
  	,suffix,(trim(filename(ifile)),ifile=1,nfiles)
	write (28,'(A)') '#    mu1          mu2           <N>           lnZ'  
	close(28)
	 
	open(unit=1,file='pvt.idat',status='old')
	do while(iostat.ne.-1)
		read(1,*,iostat=iostat) t_new(i),(mu_temp(i,icomp),icomp=1,ncomp)
!		write(*,*) t_new(i),mu_temp(i,:)
		if(iostat.ne.-1) then
     			i = i + 1
  		endif
	enddo
	
endif
ntemp = i-1
  
if(ntemp > maxtemp) then
	write(*,*) 'MAX NUMBER OF TEMPERATURES EXCEEDED'
	write(*,*) 'Increase maxtemp parameter -> line 78'
	write(*,*) 'Program terminating'
	stop
end if 

do tnum=1,ntemp
!  write(25,'(A10,f8.1,A10,f8.4)') '/* nmid = ', nmid(tnum),&
!                                  'slope = ', slope(tnum)
  betap = 1./t_new(tnum)  
  num = 0
  iter = 0
  if(lphase) then
  	if(mu2_incr(tnum).gt.0 .and. ncomp.gt.2) then
    		mup(ncomp) = mu2min(tnum)
  	else if(mu2_incr(tnum).lt.0 .and. ncomp.gt.2) then
    		mup(ncomp) = mu2max(tnum)
	else if(ncomp.eq.2) then
		mup(ncomp) = mu2min(tnum)
  	end if

  	do while ((ncomp.eq.1 .and. iter.eq.0) .or. & 
          (mup(ncomp).lt.mu2max(tnum)+.00001.and.mup(ncomp).gt.mu2min(tnum)-.00001))
  		if ( lfixp ) then
			if (ncomp < 2) then
				write(*,*) 'FIXED PRESSURE REQUIRES NCOMP > 1'
				write(*,*) 'PROGRAM TERMINATING'
				stop
			end if
		
			dmup(ncomp) = mu(ncomp,1)/1000.  
	
		endif
		
		iter2 = 0
  		flip2 = 0
  		oldsign2 = 1
		diff2 = 1e6
		num = num + 1
		do while(diff2.gt.pconverg.and.iter2.lt.maxiter) ! pressure loop, no indent
	
    		iter = 0      
		nbelow = 0.0
    		do while(abs(0.5-nbelow) > 1.e-6.and.iter.le.maxiter)      	
      
			if(iter > 0) then			
				mup(1) = mup(1) + dmup(1)
				call Zcalc(nbelow1)
				! set ln(x) - ln(1-x) to zero as this behaves better in convergence
			mup(1) = mup(1) - (log(nbelow1)-log(1.-nbelow1))*dmup(1)/ &
		 	(log(nbelow1)-log(nbelow) - log(1.-nbelow1) + log(1.-nbelow))		
			endif			
			call Zcalc(nbelow)			
			iter = iter + 1

    		enddo
		
		press = (log(Zliq) - lnZ0)*ctbar/betap/vol ! pressure is in bar	 
!		write(*,*) 'pressure = ', press
			
	 	if(.not. lfixp) then
	 
	 		diff2 = 1.e-6
		
    		else
	 
			sign2 = press-pset
			diff2 = abs(press-pset)     
			  
			if (flip2.gt.0) then
        			dmup(ncomp) = dmup(ncomp)/2.
        			flip2 = 0
      			endif

     			if(sign2.gt.0) then
       				mup(ncomp) = mup(ncomp) + dmup(ncomp)
        			newsign2 = -1
      			else
				mup(ncomp) = mup(ncomp) - dmup(ncomp)
        			newsign2 = 1
      			endif

      			if(newsign2.ne.oldsign2) then
        			oldsign2 = newsign2
        			flip2 = flip2 + 1
      			endif
				
		endif
!	 	write(*,*) sign2,press,pset,dmup(ncomp),mup(1),mup(ncomp)
 		iter2 = iter2 + 1
 	enddo ! end pressure loop
		
     do icomp=1,ncomp
       ngas(icomp) = ngas(icomp)/nbelow
       nliq(icomp) = nliq(icomp)/(1.-nbelow)
     enddo

     energy_gas = energy_gas/(nbelow)
     energy_liq = energy_liq/(1.-nbelow)
   
    open(25,file='phase.dat',status='old',position='append')
    write(25,'(10f14.4)') 1./betap,(mup(icomp),icomp=1,ncomp),&
         energy_liq,energy_gas, (nliq(icomp),icomp=1,ncomp), &
         (ngas(icomp),icomp=1,ncomp),log(Zliq),log(Zgas)
    close(25)
    
! use internal read/write to turn integers into characters    
    write(ftemp,*) tnum
    write(ftemp2,*) num
    read(ftemp,*) fname
    read(ftemp2,*) fname2
   	  
    do icomp = 1,ncomp
    	write(ftemp3,*) icomp
       	read(ftemp3,*) fname3
       	file = 'd'//trim(fname3)//'n'//trim(fname)//'t'//trim(fname2)//'a.dat'
       	open(unit=32, file = file, status ='unknown')
			write(32,'(A,f8.3,2x,10f10.2)') '#',&
            	1./betap,(mup(jcomp),jcomp=1,ncomp),xdim,ydim,zdim	    
       	do ipart= m_part(1,icomp),m_part(2,icomp)
        	   write(32,'(i6,g15.4e3)') ipart,dens(icomp,ipart)
       	enddo
       	close(unit=32)
    enddo

    mup(2) = mup(2) + mu2_incr(tnum)
  enddo ! end of chemical potential loop
  
  elseif(lpvt) then
    
    	num = 1
  	do icomp=1,ncomp
		mup(icomp) = mu_temp(tnum,icomp)
	enddo
	nmid = m_part(2,1)
	call Zcalc(nbelow)

	avg = 0.0
    	do icomp =1,ncomp
       		avg = avg + avgnum(icomp)
    	enddo
	open(28,file='pvt.dat',status='old',position='append')
	write(28,'(f15.6,5x,f15.6)') avg,log(Z)	
    	close(28)
	
	write(ftemp,*) tnum
    	write(ftemp2,*) num
    	read(ftemp,*) fname
    	read(ftemp2,*) fname2
   	  
   	do icomp = 1,ncomp
       		write(ftemp3,*) icomp
       		read(ftemp3,*) fname3
       		file = 'd'//trim(fname3)//'n'//trim(fname)//'t'//trim(fname2)//'a.dat'
       		open(unit=32, file = file, status ='unknown')
      		write(32,'(A,f8.3,2x,10f10.2)') '#',&
            	1./betap,(mup(jcomp),jcomp=1,ncomp),xdim,ydim,zdim
		
       		do ipart= m_part(1,icomp),m_part(2,icomp)
          		write(32,'(i6,g15.4e3)') ipart,dens(icomp,ipart)
       		enddo
       		close(unit=32)
    	enddo
    
    endif 
    
enddo ! end of temperature loop
write(*,*) 'Phase coexistence calculation complete'
write(*,*) 'PROGRAM TERMINATING' 
end

!=========================================================================   
Subroutine Zcalc(nbelow)
USE hdata

integer i,icomp	! local counters
double precision prob,y,ylog,tmp1
double precision nbelow	
double precision split
double precision nbelow2

nbelow2 = 0.0d0
Z = 0.0d0
Zgas = 0.0d0
Zliq = 0.0d0	          
dens = 0.0d0
avgnum = 0.0d0
nbelow = 0.
ngas = 0.0
nliq = 0.0
split = 0.0
energy_gas = 0.0d0
energy_liq = 0.0d0
! write(*,*) 'nmid = ',nmid,mup

do ifile = 1,nfiles
	do i=1,nentry(ifile)
		y = 0.0
		ylog = -1e9  ! exp(ylog) = y = 0.0
		do jfile=1,nfiles

                   prob = -(beta(jfile)-betap)*e(ifile)%flength2(i)
		   
                   do icomp=1,ncomp
                      prob = prob + &
                           (beta(jfile)*mu(icomp,jfile)-betap*mup(icomp))* &
                           n(icomp,ifile)%flength(i)
                   enddo

!           y = y+nentry(jfile)*exp(prob-log(weight(jfile)))
                   
! The following is a code rearrangement to avoid overflow problems
! This trick was compliments of Peter-Lawrence Montgomery 2/12/98
! Replace y with log(y)
! Define log_expsum(y,z) = log(exp(y)+exp(z))
! Evaluate log_expsum(y,z) = max(y,z) + log(1+exp(-abs(y-z)))

                   tmp1 = prob + log(nentry(jfile)/oldweight(jfile))	 
                   ylog = max(ylog,tmp1) + log(1.+exp(-abs(ylog-tmp1)))
					 
		enddo

		Z = Z + exp(-ylog)
		split = 0.0d0
		do icomp = 2,ncomp
			split = split + n(icomp,ifile)%flength(i)*slope(tnum)
		enddo
!                if(split.ne.0) write(*,*) split
                
		if(n(1,ifile)%flength(i).lt.nmid(tnum)+split) then
  			Zgas = Zgas + exp(-ylog)

                       nbelow = nbelow + exp(-ylog)
                        do icomp = 1,ncomp
                           ngas(icomp) = ngas(icomp) + &
			   n(icomp,ifile)%flength(i)*exp(-ylog)
                        enddo
                        energy_gas = energy_gas + &
                             e(ifile)%flength2(i)*exp(-ylog)
		else 
  			Zliq = Zliq + exp(-ylog)

                        do icomp = 1,ncomp
                           nliq(icomp) = nliq(icomp) +&
			   n(icomp,ifile)%flength(i)*exp(-ylog)
                        enddo
                        energy_liq = energy_liq + &
                             e(ifile)%flength2(i)*exp(-ylog)
                end if
	 
                do icomp=1,ncomp
                   avgnum(icomp) = avgnum(icomp) + n(icomp,ifile)%flength(i)*exp(-ylog)        
                   	dens(icomp,n(icomp,ifile)%flength(i)) = &
                   	dens(icomp,n(icomp,ifile)%flength(i))+ exp(-ylog)
                enddo
				
	enddo  
enddo

do icomp = 1,ncomp
   ngas(icomp) = ngas(icomp)/Z
   nliq(icomp) = nliq(icomp)/Z
   avgnum(icomp) = avgnum(icomp)/Z
enddo
energy_gas = energy_gas/Z
energy_liq = energy_liq/Z
dens=dens/Z
nbelow = nbelow/Z

return
end subroutine Zcalc
