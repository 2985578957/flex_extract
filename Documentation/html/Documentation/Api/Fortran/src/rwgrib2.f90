 MODULE RWGRIB2

!! Read or write a field variable on a lat/lon grid from/to GRIB file, or 
!! read a field in spectral representation from GRIB file

 CONTAINS

 SUBROUTINE READLATLON(FILENAME,FELD,MAXL,MAXB,MLEVEL,MPAR)

!! Read a field from GRIB file on lat-lon grid

 USE GRIB_API

 IMPLICIT NONE

   integer                            ::  ifile
   integer                            ::  iret
   integer                            ::  n,mk,parid,nm
   integer                            ::  i,k
   integer,dimension(:),allocatable   ::  igrib
   integer                            ::  numberOfPointsAlongAParallel
   integer                            ::  numberOfPointsAlongAMeridian
   real, dimension(:), allocatable    ::  values
   integer                            ::  numberOfValues
   real,dimension(maxl,maxb,mlevel)   ::  feld  
   integer:: maxl,maxb,mlevel,mstride,mpar(:),irest,div,level
   integer :: l(size(mpar))
   character*(*):: filename   
   
   feld=0.                          

   call grib_open_file(ifile, TRIM(FILENAME),'r')
 
   ! count the messages in the file
   call grib_count_in_file(ifile,n)
   allocate(igrib(n))
   igrib=-1
 
   ! Load the messages from the file.
   DO i=1,n
      call grib_new_from_file(ifile,igrib(i), iret)
   END DO
 
   ! we can close the file
   call grib_close_file(ifile)
 
      nm=size(mpar)
      div=mlevel/nm
      l=0
      
   ! Loop on all the messages in memory
  iloop:  DO i=1,n
!      write(*,*) 'processing message number ',i
      !     get as a integer
      call grib_get(igrib(i),'numberOfPointsAlongAParallel', &
           numberOfPointsAlongAParallel)
 
      !     get as a integer
      call grib_get(igrib(i),'numberOfPointsAlongAMeridian', &
           numberOfPointsAlongAMeridian)

      call grib_get(igrib(i),'numberOfVerticalCoordinateValues',mk)

      call grib_get_size(igrib(i),'values',numberOfValues)
!      write(*,*) 'numberOfValues=',numberOfValues
 
      allocate(values(numberOfValues), stat=iret)
      !     get data values
      call grib_get(igrib(i),'values',values)

      call grib_get(igrib(i),'paramId',parid)
      call grib_get(igrib(i),'level',level)

 kloop:  do k=1,nm
        if (parid .eq. mpar(k)) then
!         l(k)=l(k)+1
         feld(:,:,(k-1)*div+level)=reshape(values,(/maxl,maxb/))
!         print*,(k-1)*div+l(k),parid
         exit kloop
        end if
      end do kloop
      if (k .gt. nm .and. parid .ne. mpar(nm)) then
        write(*,*) k,nm,parid,mpar(nm)
        write(*,*) 'ERROR readlatlon: parameter ',parid,'is not',mpar
        stop
      end if

!      print*,i
   END DO iloop
! !   write(*,*) 'readlatlon: ',i-1,' records read'
 
   DO i=1,n
     call grib_release(igrib(i))
   END DO
 
   if (allocated(values)) deallocate(values)
   deallocate(igrib)

   END SUBROUTINE READLATLON

   SUBROUTINE WRITELATLON(iunit,igrib,ogrib,FELD,MAXL,MAXB,MLEVEL,&
   MLEVELIST,MSTRIDE,MPAR)

!! write a field on lat-lon grid to GRIB file

   USE GRIB_API

   IMPLICIT NONE

   INTEGER IFIELD,MLEVEL,MNAUF,I,J,K,L,MSTRIDE,IERR,JOUT
   INTEGER MPAR(MSTRIDE),MAXL,MAXB,LEVMIN,LEVMAX
   INTEGER IUNIT,igrib,ogrib
   REAL ZSEC4(MAXL*MAXB)
   REAL    FELD(MAXL,MAXB,MLEVEL)
   CHARACTER*(*) MLEVELIST
   INTEGER ILEVEL(MLEVEL),MLINDEX(MLEVEL+1),LLEN

 ! parse MLEVELIST

   LLEN=len(trim(MLEVELIST))
   if (index(MLEVELIST,'to') .ne. 0 .or. index(MLEVELIST,'TO') .ne. 0) THEN
     i=index(MLEVELIST,'/')
     read(MLEVELIST(1:i-1),*) LEVMIN
     i=index(MLEVELIST,'/',.true.)
     read(MLEVELIST(i+1:LLEN),*) LEVMAX
     l=0
     do i=LEVMIN,LEVMAX
       l=l+1
       ILEVEL(l)=i
     end do
   else
     l=1
     MLINDEX(1)=0
     do i=1,LLEN
       if (MLEVELIST(i:i) .eq. '/') THEN
         l=l+1
         MLINDEX(l)=i
       end if
     end do
     MLINDEX(l+1)=LLEN+1
     do i=1,l
       read(MLEVELIST(MLINDEX(i)+1:MLINDEX(i+1)-1),*) ILEVEL(i)
     end do
   end if 

   DO k=1,l
     call grib_set(igrib,"level",ILEVEL(k))
     DO j=1,MSTRIDE
       call grib_set(igrib,"paramId",MPAR(j))
!         if (MPAR(j) .eq. 87) then
!           call grib_set(igrib,"shortName","etadot")
!           call grib_set(igrib,"units","Pa,s**-1")
!         end if
!         if (MPAR(j) .eq. 77) then
!           call grib_set(igrib,"shortName","etadot")
!           call grib_set(igrib,"units","s**-1")
!         end if
       if (l .ne. mlevel) then
         zsec4(1:maxl*maxb)=RESHAPE(FELD(:,:,ILEVEL(k)),(/maxl*maxb/))
       else
         zsec4(1:maxl*maxb)=RESHAPE(FELD(:,:,k),(/maxl*maxb/))
       end if
       call grib_set(igrib,"values",zsec4)

       call grib_write(igrib,iunit)

     END DO
   END DO

   END SUBROUTINE WRITELATLON

   SUBROUTINE READSPECTRAL(FILENAME,CXMN,MNAUF,MLEVEL,MAXLEV,MPAR,A,B)

!!  Read a GRIB file in spherical harmonics

   USE GRIB_API

   IMPLICIT NONE

   integer                            ::  ifile
   integer                            ::  iret
   integer                            ::  n,mk,div,nm,k
   integer                            ::  i,j,parid
   integer,dimension(:),allocatable   ::  igrib
   real, dimension(:), allocatable    ::  values
   integer                            ::  numberOfValues,maxlev
   REAL :: A(MAXLEV+1),B(MAXLEV+1),pv(2*MAXLEV+2)
   REAL:: CXMN(0:(MNAUF+1)*(MNAUF+2)-1,MLEVEL)
  integer:: maxl,maxb,mlevel,mstride,mpar(:),mnauf,ioffset,ipar,ilev,l(size(mpar))
   character*(*):: filename                             
 
   call grib_open_file(ifile, TRIM(FILENAME),'r')
 
   ! count the messages in the file
   call grib_count_in_file(ifile,n)
   allocate(igrib(n))
   igrib=-1
 
   ! Load the messages from the file.
   DO i=1,n
      call grib_new_from_file(ifile,igrib(i), iret)
   END DO
 
   ! we can close the file
   call grib_close_file(ifile)
 
    l=0
   ! Loop on all the messages in memory
   iloop: DO i=1,n
   ! write(*,*) 'processing message number ',i
      !     get as a integer
      call grib_get(igrib(i),'pentagonalResolutionParameterJ', j)

      call grib_get_size(igrib(i),'values',numberOfValues)
   !   write(*,*) 'numberOfValues=',numberOfValues
 
      call grib_get(igrib(i),'numberOfVerticalCoordinateValues',mk)

      call grib_get(igrib(i),'level',ilev)

      

      call grib_get(igrib(i),'pv',pv)

      allocate(values(numberOfValues), stat=iret)
      !     get data values
      call grib_get(igrib(i),'values',values)

!      IOFFSET=mod(i-1,MSTRIDE)*(mk/2-1)
!           CXMN(:,IOFFSET+ilev)=values(1:(MNAUF+1)*(MNAUF+2))

      call grib_get(igrib(i),'paramId',parid)
      nm=size(mpar)
      div=mlevel/nm
      kloop:  do k=1,nm
        if (parid .eq. mpar(k)) then
         l(k)=l(k)+1
         cxmn(:,(k-1)*div+l(k))=values(1:(MNAUF+1)*(MNAUF+2))
!         print*,(k-1)*div+l(k),parid
         exit kloop
        end if
        
      end do kloop
      if (k .gt. nm .and. parid .ne. mpar(nm)) then
        write(*,*) k,nm,parid,mpar(nm)
        write(*,*) 'ERROR readspectral: parameter ',parid,'is not',mpar
        stop
      end if

!      print*,i

   END DO iloop

! !   write(*,*) 'readspectral: ',i-1,' records read'
 
   DO i=1,n
     call grib_release(igrib(i))
   END DO
 
   deallocate(values)
   deallocate(igrib)

   A=pv(1:1+MAXLEV)
   B=pv(2+MAXLEV:2*MAXLEV+2)

   END SUBROUTINE READSPECTRAL

END MODULE RWGRIB2
