      PROGRAM PRECONVERT
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!                                                                 !
! PROGRAM PRECONVERT - PREPARES INPUT DATA FOR POP MODEL METEOR-  !
!                      OLOGICAL PREPROCESSOR                      !
!                                                                 !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!                                                                 !
! CALCULATION OF ETAPOINT ON A REGULAR LAMDA/PHI GRID AND WRITING !
! U,V,ETAPOINT,T,PS,Q,SD,MSL,TCC,10U, 10V, 2T,2D,LSP,CP,SSHF,SSR, !
! EWSS,NSSS TO AN OUTPUT FILE (GRIB 1 or 2 FORMAT).               ! 
!                                                                 !
! AUTHORS: L. HAIMBERGER, G. WOTAWA, 1994-04                      !
!                     adapted: A. BECK                            !
!                     2003-05-11                                  !
!          L. Haimberger 2006-12    V2.0                          !
!                    modified to handle arbitrary regular grids   !
!                    and T799 resolution data                     !
!          L. Haimberger 2010-03    V4.0                          !
!                    modified to grib edition 2 fields            !
!                    and T1279 resolution data                    !
!                                                                 !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!                                                                 !
! DESCRIPTION OF NEEDED INPUT:                                    !
!                                                                 !
! UNIT  FILE      PARAMETER(S)    DATA REPRESENTATION             !
!                                                                 !
! 11    fort.11   T,U,V           regular lamda phi grid          !
! 12    fort.12   D               regular lamda phi grid          !
! 13    fort.13   LNSP          fort.13  spherical harmonics             !
! 14    fort.14   SD,MSL,TCC,10U,                                 !
!                 10V,2T,2D       regular lamda phi grid          !
! 16    fort.16   LSP,CP,SSHF,                                    !
!                 SSR,EWSS,NSSS   regular lamda phi grid          !
! 17    fort.17   Q               regular lamda phi grid          !
!                                                                 !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!                                                                 !
! DESCRIPTION OF OUTPUT:                                          !
!                                                                 !
! UNIT  FILE      PARAMETER(S)    DATA REPRESENTATION             !
!                                                                 !
! 15    fort.15   U,V,ETA,T,PS,                                   !
!                 Q,SD,MSL,TCC,                                   !
!                 10U,10V,2T,2D,  regular lamda phi grid          !
!                 LSP,CP,SSHF,                                    !
!                 SSR,EWSS,NSSS                                   !
!                                                                 !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!

      USE PHTOGR
      USE GRTOPH
      USE FTRAFO
      USE RWGRIB2
      USE GRIB_API

      IMPLICIT NONE

      REAL, ALLOCATABLE, DIMENSION (:,:) :: LNPS
      REAL, ALLOCATABLE, DIMENSION (:,:) :: Z
      REAL, ALLOCATABLE, DIMENSION (:,:,:) :: T, UV , UV2
      REAL, ALLOCATABLE, DIMENSION (:,:,:) :: QA,OM,OMR
      REAL, ALLOCATABLE, DIMENSION (:,:,:) :: DIV, ETA,ETAR
      REAL, ALLOCATABLE, DIMENSION (:,:) :: DPSDL, DPSDM
      REAL, ALLOCATABLE, DIMENSION (:,:,:) :: PS,DPSDT
      REAL, ALLOCATABLE, DIMENSION (:,:,:) :: SURF,FLUX,OROLSM
      REAL, ALLOCATABLE, DIMENSION (:) :: WSAVE,H,SINL,COSL,WSAVE2
      REAL, ALLOCATABLE, DIMENSION (:) :: BREITE, GBREITE,AK, BK,pv

! Arrays for Gaussian grid calculations

      REAL  :: X1,X2,RMS,MW,SIG,LAM
      REAL,ALLOCATABLE :: CUA(:,:,:),CVA(:,:,:)

      REAL, ALLOCATABLE, DIMENSION (:,:) :: P,PP !,P2
      REAL, ALLOCATABLE, DIMENSION (:,:) :: XMN,HILFUV
      REAL, ALLOCATABLE, DIMENSION (:) :: LNPMN,LNPMN2,LNPMN3
      REAL, ALLOCATABLE, DIMENSION (:) :: WEIGHT
      REAL, ALLOCATABLE, DIMENSION (:,:) :: UGVG
      REAL, ALLOCATABLE, DIMENSION (:,:) :: DG, ETAG
      REAL, ALLOCATABLE, DIMENSION (:,:) :: GWSAVE
      REAL, ALLOCATABLE, DIMENSION (:) :: PSG,HILF

! end arrays for Gaussian grid calculations

      INTEGER, ALLOCATABLE, DIMENSION (:) :: MLAT,MPSURF,MPFLUX,MPORO,MPAR
      INTEGER, ALLOCATABLE :: GIFAX(:,:)

      REAL PI,COSB,DAK,DBK,P00
      REAL URLAR8,JMIN1,LLLAR8,MAXBMIN1,PIR8,DCOSB

      INTEGER I,J,K,L,IERR,M,LTEST,MK,NGI,NGJ
      INTEGER MFLUX,MSURF,MORO
      INTEGER LUNIT,LUNIT2

      INTEGER MAXL, MAXB, MLEVEL, LEVOUT,LEVMIN,LEVMAX
      INTEGER MOMEGA,MOMEGADIFF,MGAUSS,MSMOOTH, MNAUF,META,METADIFF
      INTEGER MDPDETA,METAPAR
      REAL RLO0, RLO1, RLA0, RLA1
      CHARACTER*300 MLEVELIST

      INTEGER MAUF, MANF,IFAX(10)

      INTEGER IGRIB(1),iret,ogrib

      CHARACTER*80 FILENAME

      NAMELIST /NAMGEN/ &
                 MAXL, MAXB, &
                 MLEVEL,MLEVELIST,MNAUF,METAPAR, &
                 RLO0, RLO1, RLA0, RLA1, &
                 MOMEGA,MOMEGADIFF,MGAUSS,MSMOOTH,META,METADIFF,&
                 MDPDETA

      LTEST=1

      call posnam (4,'NAMGEN')
      read (4,NAMGEN)

      MAUF=INT(360.*(REAL(MAXL)-1.)/(RLO1-RLO0)+0.0001)
!      PRINT*, MAUF

      MANF=INT(REAL(MAUF)/360.*(360.+RLO0)+1.0001)
      IF(MANF .gt. MAUF) MANF=MANF-MAUF


!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!                       ALLOCATE VARIABLES                        !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

      ALLOCATE (LNPS(0:(MNAUF+1)*(MNAUF+2)-1,1))

      ALLOCATE (H(0:(MNAUF+2)*(MNAUF+3)/2))

     
      ALLOCATE (OM(MAXL, MAXB, MLEVEL))

      ALLOCATE (ETA(MAXL,MAXB,MLEVEL))

      ALLOCATE (PS(MAXL, MAXB,1),DPSDT(MAXL, MAXB,1))

      
      ALLOCATE (WSAVE(4*MAUF+15),WSAVE2(4*MAUF+15))

      ALLOCATE (BREITE(MAXB),AK(MLEVEL+1),BK(MLEVEL+1),pv(2*mlevel+2))
      
      ALLOCATE (MPAR(2))

      ALLOCATE (COSL(MAXL),SINL(MAXL))
		
      ALLOCATE (CUA(2,4,MLEVEL),CVA(2,4,MLEVEL))
    	
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!     GAUSS STUFF !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


      IF(MGAUSS .EQ. 1) THEN
      LUNIT=0
      FILENAME='fort.18'

      call grib_open_file(LUNIT, TRIM(FILENAME),'r')
 
      call grib_new_from_file(LUNIT,igrib(1), iret)
 
! we can close the file
      call grib_close_file(LUNIT)
 
!      call grib_get(igrib(1),'gridType', j)

      NGJ=MNAUF+1

      ALLOCATE (GWSAVE(8*NGJ+15,NGJ/2))
      ALLOCATE(GIFAX(10,NGJ))
      ALLOCATE (GBREITE(NGJ),WEIGHT(NGJ))
      ALLOCATE (MLAT(NGJ))
      ALLOCATE (P(0:((MNAUF+3)*(MNAUF+4))/2,NGJ/2))
      ALLOCATE (PP(NGJ/2,0:((MNAUF+3)*(MNAUF+4))/2))
      ALLOCATE (Z(0:((MNAUF+3)*(MNAUF+4))/2,MAXB))

      call grib_get(igrib(1),'numberOfPointsAlongAMeridian', NGJ)
 
      !     get as a integer
      call grib_get(igrib(1),'pl', MLAT)

      NGI=SUM(MLAT)

      call grib_get(igrib(1),'numberOfVerticalCoordinateValues',mk)

      IF(mk/2-1 .ne. MLEVEL) THEN 
        WRITE(*,*) 'FATAL: Number of model levels',mk, &
          ' does not agree with', MLEVEL,' in namelist'
        STOP
      ENDIF
      call grib_get(igrib(1),'pv',pv)
        AK=pv(1:1+MLEVEL)
        BK=pv(2+MLEVEL:2*MLEVEL+2)

      ALLOCATE (LNPMN(0:(MNAUF+1)*(MNAUF+2)-1))
      ALLOCATE (LNPMN2(0:(MNAUF+1)*(MNAUF+2)-1))
      ALLOCATE (UGVG(NGI, 2*MLEVEL),HILFUV(2*MAXL,2))


      ALLOCATE (DPSDL(NGI,1),DPSDM(NGI,1))

      ALLOCATE (PSG(NGI),HILF(NGI))
      ALLOCATE (UV(MAXL, MAXB, 2*MLEVEL))
!      ALLOCATE (UV2(MAXL, MAXB, 2*MLEVEL))

      ALLOCATE (XMN(0:(MNAUF+1)*(MNAUF+2)-1, 2*MLEVEL))
      ALLOCATE (DG(NGI,MLEVEL),ETAG(NGI,MLEVEL))

! Initialisieren  Legendretransformation
!	auf das LaT/LON Gitter

      PI=ACOS(-1.D0)
!$OMP PARALLEL DO
      DO 20 J=1,MAXB

      BREITE(J)=SIN((RLA1-(J-1.D0)*(RLA1-RLA0)/(MAXB-1))* PI/180.D0)

      CALL PLGNFA(MNAUF,BREITE(J),Z(0,J))

20    CONTINUE
!$OMP END PARALLEL DO

! Avoid possible Pole problem
!      IF(RLA0 .EQ. -90.0) BREITE(MAXB)=sin(-89.99*PI/180.d0)
!      IF(RLA1 .EQ. 90.0)  BREITE(1)=sin(89.99*PI/180.d0)

! Initialisation of fields for  FFT and Legendre transformation
!	to  Gaussian grid and back to phase space
	X1=-1.D0
	X2=1.D0
	CALL GAULEG(X1,X2,GBREITE,WEIGHT,NGJ)

!$OMP PARALLEL DO PRIVATE(M)
	DO J=1,NGJ/2
               CALL PLGNFA(MNAUF,GBREITE(J),P(:,J))
		DO M=0,(MNAUF+3)*(MNAUF+4)/2
		  PP(J,M)=P(M,J)
	ENDDO
	ENDDO
!$OMP END PARALLEL DO


!       MPAR(1)=152
        FILENAME='fort.12'
        CALL READSPECTRAL(FILENAME,LNPMN,MNAUF,1,MLEVEL,(/152/),AK,BK)
!      goto 111
        CALL SET99(WSAVE,IFAX,mauf)
        CALL PHGCUT(LNPMN,PS,WSAVE,IFAX,Z, &
      MNAUF,MNAUF,MAUF,MANF,MAXL,MAXB,1)
      CALL STATIS(MAXL,MAXB,1,EXP(PS),RMS,MW,SIG)
      WRITE(*,'(A12,3F12.4)') 'STATISTICS: ',RMS,MW,SIG

        DO J=1,NGJ/2
          CALL SET99(GWSAVE(1,J),GIFAX(1,J),MLAT(J))
        ENDDO
	CALL PHGR213(LNPMN,HILF,GWSAVE,GIFAX,P,MLAT,MNAUF,NGI,NGJ,1)
        PSG=HILF
	CALL GRPH213(LNPMN2,PSG,GWSAVE,GIFAX,PP,WEIGHT,MLAT, &
      MNAUF,NGI,NGJ,1)
	CALL PHGR213(LNPMN2,HILF,GWSAVE,GIFAX,P,MLAT,MNAUF,NGI,NGJ,1)


        HILF=exp(PSG)-exp(HILF)

      CALL STATIS(NGI,1,1,HILF,RMS,MW,SIG)
      WRITE(*,'(A12,3F11.4)') 'STATISTICS: ',RMS,MW,SIG

        PSG=EXP(PSG)
        HILF=PSG
      CALL STATIS(NGI,1,1,HILF,RMS,MW,SIG)
      WRITE(*,'(A12,3F11.4)') 'STATISTICS: ',RMS,MW,SIG

  111         FILENAME='fort.10'
       CALL READSPECTRAL(FILENAME, &
      XMN,MNAUF,2*MLEVEL,MLEVEL,(/131,132/),AK,BK) 
!	Transformieren des Windes auf das Gaussgitter	
	CALL PHGR213(XMN,UGVG,GWSAVE,GIFAX,P,MLAT,MNAUF,NGI,NGJ,2*MLEVEL)
       DO K=1,MLEVEL
! North Pole
            CALL JSPPOLE(XMN(:,K),1,MNAUF,.TRUE.,CUA(:,:,K))
            CALL JSPPOLE(XMN(:,MLEVEL+K),1,MNAUF,.TRUE.,CVA(:,:,K))
! South Pole
            CALL JSPPOLE(XMN(:,K),-1,MNAUF,.TRUE.,CUA(:,3:4,K))
            CALL JSPPOLE(XMN(:,MLEVEL+K),-1,MNAUF,.TRUE.,CVA(:,3:4,K))
       ENDDO
    
        DO K=1,2*MLEVEL
          IF(MSMOOTH .ne. 0) CALL SPFILTER(XMN(:,K),MNAUF,MSMOOTH)
        ENDDO
        CALL PHGCUT(XMN,UV,WSAVE,IFAX,Z, &
      MNAUF,MNAUF,MAUF,MANF,MAXL,MAXB,2*MLEVEL)


 112        FILENAME='fort.13'
      CALL READSPECTRAL(FILENAME,XMN,MNAUF,MLEVEL,MLEVEL,(/155/),AK,BK)
!	Transformieren der horizontalen Divergenz auf das Gaussgitter			
	CALL PHGR213(XMN,DG,GWSAVE,GIFAX,P,MLAT,MNAUF,NGI,NGJ,MLEVEL)


!	Berechnung des Gradienten des Logarithmus des Bodendrucks 
!       auf dem Gaussgitter	
	CALL PHGRAD(LNPMN,DPSDL,DPSDM,GWSAVE,GIFAX,P,H,MLAT,MNAUF,NGI,NGJ,1)

!	Berechnung der Vertikalgeschwindigkeit auf dem Gaussgitter
      CALL CONTGL(HILF,DPSDL,DPSDM,DG,UGVG(:,1),UGVG(:,MLEVEL+1), &
      GBREITE,ETAG,MLAT,AK,BK,NGI,NGJ,MLEVEL)

 
 	CALL GRPH213(XMN,ETAG,GWSAVE,GIFAX,PP,WEIGHT,MLAT, &
      MNAUF,NGI,NGJ,MLEVEL)
        DO K=1,MLEVEL
          IF(MSMOOTH .ne. 0) CALL SPFILTER(XMN(:,K),MNAUF,MSMOOTH)
        ENDDO
        CALL PHGCUT(XMN,ETA,WSAVE,IFAX,Z,MNAUF,MNAUF,MAUF,MANF,MAXL,MAXB,MLEVEL)

	CALL GRPH213(XMN,HILF,GWSAVE,GIFAX,PP,WEIGHT,MLAT, MNAUF,NGI,NGJ,1)

        IF(MSMOOTH .ne. 0) CALL SPFILTER(XMN(:,1),MNAUF,MSMOOTH)
        CALL PHGCUT(XMN,DPSDT,WSAVE,IFAX,Z,MNAUF,MNAUF,MAUF,MANF,MAXL,MAXB,1)
!       GOTO 114

      CALL STATIS(MAXL,MAXB,1,DPSDT,RMS,MW,SIG)
      WRITE(*,'(A12,3F11.4)') 'STATISTICS DPSDT: ',RMS,MW,SIG

       IF(MOMEGADIFF .ne. 0) THEN
!	Berechnung von Omega auf dem Gaussgitter
	CALL OMEGA(PSG,DPSDL,DPSDM,DG,UGVG(:,1),UGVG(:,MLEVEL+1), &
      GBREITE,ETAG,MLAT,AK,BK,NGI ,NGJ,MLEVEL) 

	CALL GRPH213(XMN,ETAG,GWSAVE,GIFAX,PP,WEIGHT,MLAT,&
      MNAUF,NGI,NGJ,MLEVEL)
        DO K=1,MLEVEL
          IF(MSMOOTH .ne. 0) CALL SPFILTER(XMN(:,K),MNAUF,MSMOOTH)
        ENDDO
        CALL PHGCUT(XMN,OM,WSAVE,IFAX,Z,MNAUF,MNAUF,MAUF,MANF,MAXL,MAXB,MLEVEL)

       ENDIF !MOMEGA

	CALL GRPH213(XMN,PSG,GWSAVE,GIFAX,PP,WEIGHT,MLAT,MNAUF,NGI,NGJ,1)
        CALL PHGCUT(XMN,PS,WSAVE,IFAX,Z,MNAUF,MNAUF,MAUF,MANF,MAXL,MAXB,1)

      CALL STATIS(MAXL,MAXB,1,PS,RMS,MW,SIG)
      WRITE(*,'(A12,3F11.4)') 'STATISTICS: ',RMS,MW,SIG

 114  DEALLOCATE(HILF,PSG,DPSDL,DPSDM,ETAG,DG,LNPMN)

!      ALLOCATE (UV(MAXL, MAXB, 2*MLEVEL))
!	CALL GRPH213(XMN,UGVG,GWSAVE,GIFAX,PP,WEIGHT,MLAT,
!     *MNAUF,NGI,NGJ,2*MLEVEL)
!        DO K=1,2*MLEVEL
!          IF(MSMOOTH .ne. 0) CALL SPFILTER(XMN(:,K),MNAUF,MSMOOTH)
!        ENDDO
!        CALL PHGCUT(XMN,UV,WSAVE,IFAX,Z,
!     *MNAUF,MNAUF,MAUF,MANF,MAXL,MAXB,2*MLEVEL)
        DEALLOCATE(PP,P,UGVG,MLAT,GBREITE,WEIGHT,GWSAVE,XMN)

!        CALL ETAGAUSS(Z,WSAVE
!     *,BREITE,UV,ETA,OM,PS,
!     *MAUF,MAXB,MAXL,MANF,MNAUF,MLEVEL,MSMOOTH)

      ELSE

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!          READING OF PREPARED METEOROLOGICAL FIELDS              !
!                                                                 !
!          THE FOLLOWING FIELDS ARE EXPECTED:                     !
!                                                                 !
!          UNIT 11: T,U,V        (REGULAR GRID)                   !
!          UNIT 17: Q            (REGULAR GRID)                   !
!          UNIT 13: D            (REGULAR GRID)                   !
!          UNIT 12: LNSP         (SPHERICAL HARMONICS)            !
!          UNIT 14: SURFACE DATA (REGULAR GRID)                   !
!          UNIT 16: FLUX DATA    (REGULAR GRID)                   !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!
      ALLOCATE (MLAT(MAXB))
      MLAT=MAXL
      ALLOCATE (Z(0:((MNAUF+3)*(MNAUF+4))/2,1))
      ALLOCATE (DPSDL(MAXL,MAXB),DPSDM(MAXL,MAXB))
      ALLOCATE (UV(MAXL, MAXB, 2*MLEVEL),DIV(MAXL,MAXB,MLEVEL))

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!                  READING OF SURFACE PRESSURE                    !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

      FILENAME='fort.12'
        CALL READSPECTRAL(FILENAME,LNPS,MNAUF,1,MLEVEL,(/152/),AK,BK)

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!                      READING OF U,V                      !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!
! OPENING OF UNBLOCKED GRIB FILE
!
      FILENAME='fort.10'
      CALL READLATLON(FILENAME,UV,MAXL,MAXB,2*MLEVEL,(/131,132/))


      PI=ACOS(-1.D0)
      DO J=1,MAXB

        BREITE(J)=SIN((RLA1-(J-1.D0)*(RLA1-RLA0)/(MAXB-1))*PI/180.D0)

      ENDDO
! Avoid possible Pole problem
!      IF(RLA0 .EQ. -90.0) BREITE(MAXB)=sin(-89.99*PI/180.d0)
!      IF(RLA1 .EQ. 90.0)  BREITE(1)=sin(89.99*PI/180.d0)

      DO K=1,2*MLEVEL
        DO J=1,MAXB
          COSB=SQRT(1.0-(BREITE(J))*(BREITE(J)))
          IF(RLA0 .EQ. -90.0 .AND. J .EQ. MAXB .OR. &
             RLA1 .EQ. 90.0 .AND. J .EQ. 1) then
            UV(:,J,K)=UV(:,J,K)/1.D6
          else
            UV(:,J,K)=UV(:,J,K)*COSB
          endif
      ENDDO
      ENDDO

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!                     READING OF LNSP on grid                !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

! For debugging only
!      FILENAME='LNSPG_G.20060330.600'
!      INQUIRE(FILE=FILENAME,EXIST=EX)
!      CALL READLATLON(FILENAME,QA,
!     *MAXL,MAXB,1,1,(/152/))

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!                     READING OF DIVERGENCE                       !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

      IF(META .EQ. 0 .OR. METADIFF .EQ. 1) THEN
        FILENAME='fort.13'
        CALL READLATLON(FILENAME,DIV,MAXL,MAXB,MLEVEL,(/155/))
      ENDIF


!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!       CALCULATION OF ETAPOINT --> TOTAL TIME DERIVATIVE OF       !
!      ECMWF VERTICAL COORDINATE ETA MULTIPLIED BY DERIVATIVE     !
!      OF PRESSURE IN ETA DIRECTION                               !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

! Initialisieren  Legendretransformation
!	auf das LaT/LON Gitter
! Without Gaussian grid calculation Legendre Polynomials are calculated
! only for one latitude to save space

      DO J=1,MAXB

        CALL PLGNFA(MNAUF,BREITE(J),Z(0,1))

        CALL PHGCUT(LNPS,PS(:,J,1),WSAVE,IFAX,Z,MNAUF,MNAUF,MAUF,MANF,MAXL,1,1)


        IF(META .EQ. 0 .or. METADIFF .EQ. 1 ) THEN
          CALL PHGRACUT(LNPS,DPSDL(:,J),DPSDM(:,J),WSAVE,IFAX,Z,H,MAUF, &
      MNAUF,MAXL,1,MANF,1)
        ENDIF
      ENDDO
     
      PS=EXP(PS)

! For debugging only
      CALL STATIS(MAXL,MAXB,1,PS(:,:,1),RMS,MW,SIG)
      WRITE(*,'(A12,3F11.4)') 'STATISTICS: ',RMS,MW,SIG
      
      
       IF(MOMEGADIFF .ne. 0) THEN

         CALL OMEGA(PS,DPSDL,DPSDM,DIV,UV(:,:,1),UV(:,:,MLEVEL+1), &
      BREITE,OM,MLAT,AK,BK,MAXL*MAXB,MAXB,MLEVEL) 
       ENDIF
     
       IF(META .EQ. 0 .OR. METADIFF .ne. 0) THEN
         DPSDT=PS
         CALL CONTGL(DPSDT,DPSDL,DPSDM,DIV,UV(:,:,1),UV(:,:,MLEVEL+1), &
      BREITE,ETA,MLAT,AK,BK,MAXL*MAXB,MAXB,MLEVEL)
       ENDIF

      ENDIF ! MGAUSS

! CREATE FILE VERTICAL.EC NEEDED BY POP MODEL

      open(21,file='VERTICAL.EC')
      write(21,'(a)')
      write(21,'(a)') 'VERTICAL DISCRETIZATION OF POP MODEL'
      write(21,'(a)')
      write(21,'(i3,a)') MLEVEL,'   number of layers'
      write(21,'(a)')
      write(21,'(a)') '* A(NLEV+1)'
      write(21,'(a)')
      do 205 i=1,MLEVEL+1
205      write(21,'(f18.12)') AK(I)
      write(21,'(a)')
      write(21,'(a)') '* B(NLEV+1)'
      write(21,'(a)')
      do 210 i=1,MLEVEL+1
210      write(21,'(f18.12)') BK(I)
      close(21)

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!                     READING OF OMEGA                       !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

      IF(MOMEGA .NE. 0 ) THEN



         ALLOCATE (OMR(MAXL, MAXB, MLEVEL))
 
         FILENAME='fort.19'
         CALL READLATLON(FILENAME,OMR,MAXL,MAXB,MLEVEL,(/135/))

      IF(MOMEGADIFF .NE. 0 ) THEN

      DO K=1,MLEVEL
        CALL STATIS(MAXL,MAXB,1,ETA(:,:,K),RMS,MW,SIG)        
        WRITE(*,'(A12,I3,3F11.4)') '       ETA: ',K,RMS,MW,SIG
        CALL STATIS(MAXL,MAXB,1,OMR(:,:,K),RMS,MW,SIG)        
        WRITE(*,'(A12,I3,3F11.4)') '     OMEGA: ',K,RMS,MW,SIG
        CALL STATIS(MAXL,MAXB,1,OM(:,:,K)-OMR(:,:,K),RMS,MW,SIG)        
        WRITE(*,'(A12,I3,3F11.4)') 'OMEGA DIFF: ',K,RMS,MW,SIG
      ENDDO

      ENDIF
      ENDIF

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!                     READING OF ETA                       !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

      IF(META .NE. 0 ) THEN

         ALLOCATE (ETAR(MAXL, MAXB, MLEVEL))
 
         P00=101325.
         FILENAME='fort.21'
         CALL READLATLON(FILENAME,ETAR,MAXL,MAXB,MLEVEL,(/77/))

         if(MDPDETA .EQ. 1) THEN
          DO K=1,MLEVEL
           DAK=AK(K+1)-AK(K)
           DBK=BK(K+1)-BK(K)
           DO J=1,MAXB
             DO I=1,MAXL
               ETAR(I,J,K)=2*ETAR(I,J,K)*PS(I,J,1)*(DAK/PS(I,J,1)+DBK)/ &
                          (DAK/P00+DBK)
               IF(K .GT. 1) ETAR(I,J,K)=ETAR(I,J,K)-ETAR(I,J,K-1)
             ENDDO
           ENDDO
          ENDDO
         ENDIF

        IF(METADIFF .NE. 0 ) THEN

         DO K=1,MLEVEL
          CALL STATIS(MAXL,MAXB,1,ETA(:,:,K),RMS,MW,SIG)        
          WRITE(*,'(A12,I3,3F11.4)') '       ETA: ',K,RMS,MW,SIG
          CALL STATIS(MAXL,MAXB,1,ETAR(:,:,K),RMS,MW,SIG)        
          WRITE(*,'(A12,I3,3F11.4)') '     ETAR: ',K,RMS,MW,SIG
          CALL STATIS(MAXL,MAXB,1,ETA(:,:,K)-ETAR(:,:,K),RMS,MW,SIG)        
          WRITE(*,'(A12,I3,3F11.4)') 'ETA DIFF: ',K,RMS,MW,SIG
         ENDDO
         DO K=1,MLEVEL
          WRITE(*,'(I3,2F11.4)') K,ETA(1,MAXB/2,K),ETAR(1,MAXB/2,K)
         ENDDO
        ELSE
          ETA=ETAR
        ENDIF
      ENDIF

      ALLOCATE (T(MAXL, MAXB, MLEVEL))
      ALLOCATE (QA(MAXL, MAXB, MLEVEL))
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!                      READING OF T                      !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!
! OPENING OF UNBLOCKED GRIB FILE
!
      FILENAME='fort.11'
      CALL READLATLON(FILENAME,T,MAXL,MAXB,MLEVEL,(/130/))

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!                     READING OF SPECIFIC HUMIDITY                !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

      FILENAME='fort.17'
      CALL READLATLON(FILENAME,QA,MAXL,MAXB,MLEVEL,(/133/))

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!                     TEST READING OF UV from MARS (debug only)   !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

!      FILENAME='fort.22'
!      CALL READLATLON(FILENAME,UV2,MAXL,MAXB,2*MLEVEL,2,(/131,132/))



!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!                    WRITE MODEL LEVEL DATA TO fort.15            !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

!     Calculation of etadot in CONTGL needed scaled winds (ucosphi,vcosphi)
!     Now we are transforming back to the usual winds. 
      DO K=1,MLEVEL
        DO J=2,MAXB-1
          COSB=SQRT(1.0-(BREITE(J))*(BREITE(J)))
          UV(:,J,K)=UV(:,J,K)/COSB
          UV(:,J,MLEVEL+K)=UV(:,J,MLEVEL+K)/COSB
        ENDDO
! special treatment for poles, if necessary. 
        DO J=1,MAXB,MAXB-1
          COSB=SQRT(1.0-(BREITE(J))*(BREITE(J)))
          if(1.0-BREITE(J)*BREITE(J) .gt. 0 .OR. MGAUSS .NE. 1) then
            IF(RLA0 .EQ. -90.0 .AND. J .EQ. MAXB .OR. &
             RLA1 .EQ. 90.0 .AND. J .EQ. 1) then
             UV(:,J,K)=UV(:,J,K)*1.D6
             UV(:,J,MLEVEL+K)=UV(:,J,MLEVEL+K)*1.D6
            else
             UV(:,J,K)=UV(:,J,K)/COSB
             UV(:,J,MLEVEL+K)=UV(:,J,MLEVEL+K)/COSB
            endif
          else
              HILFUV(5:MAXL,:)=0.
              HILFUV(1:2,:)=0.
            IF(J.EQ.MAXB) THEN
! Suedpol
              HILFUV(3:4,1)=CUA(:,4,K)
              HILFUV(3:4,2)=CVA(:,4,K)
            ELSE
! Nordpol
              HILFUV(3:4,1)=CUA(:,2,K)
              HILFUV(3:4,2)=CVA(:,2,K)
            ENDIF
              CALL RFOURTR(HILFUV(:,1),WSAVE,IFAX,MAXL/2-1,MAXL,-1)
              DO I=0,MAXL-1
                IF(MANF+I.LE.MAXL) THEN
                  UV(I+1,J,K)=HILFUV(MANF+I,1)
                ELSE
                  UV(I+1,J,K)=HILFUV(MANF-MAXL+I,1)
                ENDIF
              ENDDO
              CALL RFOURTR(HILFUV(:,2),WSAVE,IFAX,MAXL/2-1,MAXL,-1)
              DO I=0,MAXL-1
                IF(MANF+I.LE.MAXL) THEN
                  UV(I+1,J,MLEVEL+K)=HILFUV(MANF+I,2)
                ELSE
                  UV(I+1,J,MLEVEL+K)=HILFUV(MANF-MAXL+I,2)
                ENDIF
              ENDDO
          endif
      ENDDO
      ENDDO

! open output file
      call grib_open_file(LUNIT,'fort.15','w')

! we use temperature on lat/lon on model levels as template for model level data
      LUNIT2=0
      call grib_open_file(LUNIT2,'fort.11','r')
      call grib_new_from_file(LUNIT2,igrib(1), iret)
      call grib_close_file(LUNIT2)


      CALL WRITELATLON(LUNIT,igrib(1),ogrib,UV(:,:,1),MAXL,MAXB,MLEVEL,MLEVELIST,1,(/131/))

      CALL WRITELATLON(LUNIT,igrib(1),ogrib,UV(:,:,MLEVEL+1),MAXL,MAXB,MLEVEL,MLEVELIST,1,(/132/))

      IF(MDPDETA .ne. 1 .AND. MGAUSS .EQ. 0 .and. META .eq. 1) THEN
        CALL WRITELATLON(LUNIT,igrib(1),ogrib,ETA,MAXL,MAXB,MLEVEL,MLEVELIST,1,(/77/))
      ELSE
        CALL WRITELATLON(LUNIT,igrib(1),ogrib,ETA,MAXL,MAXB,MLEVEL,MLEVELIST,1,(/METAPAR/))
      ENDIF

      CALL WRITELATLON(LUNIT,igrib(1),ogrib,T,MAXL,MAXB,MLEVEL,MLEVELIST,1,(/130/))

      CALL WRITELATLON(LUNIT,igrib(1),ogrib,PS,MAXL,MAXB,1,'1',1,(/134/))
 
      call grib_set(igrib(1),"levelType","ml")
      call grib_set(igrib(1),"typeOfLevel","hybrid")
      CALL WRITELATLON(LUNIT,igrib(1),ogrib,QA,MAXL,MAXB,MLEVEL,MLEVELIST,1,(/133/))

  
      IF(MOMEGA .EQ. 1) THEN
        call grib_open_file(LUNIT2,'fort.25','w')
        CALL WRITELATLON(LUNIT2,igrib(1),ogrib,OMR,MAXL,MAXB,MLEVEL,MLEVELIST,1,(/135/))

        IF(MOMEGADIFF .EQ. 1) THEN

          CALL WRITELATLON(LUNIT2,igrib(1),ogrib,DPSDT,MAXL,MAXB,1,'1',1,(/158/))

        OM=OM-OMR
        CALL WRITELATLON(LUNIT2,igrib(1),ogrib,OM,MAXL,MAXB,MLEVEL,MLEVELIST,1,(/001/))
      call grib_close_file(LUNIT2)
        ENDIF
      ENDIF

      IF(META .EQ. 1 .and. METADIFF .EQ. 1) THEN
        call grib_open_file(LUNIT2,'fort.26','w')
        CALL WRITELATLON(LUNIT2,igrib(1),ogrib,ETAR,MAXL,MAXB,MLEVEL,MLEVELIST,1,(/135/))

!        IF(MOMEGADIFF .EQ. 1) THEN

          CALL WRITELATLON(LUNIT2,igrib(1),ogrib,DPSDT,MAXL,MAXB,1,'1',1,(/158/))

        OM=ETA-ETAR
        CALL WRITELATLON(LUNIT2,igrib(1),ogrib,OM,MAXL,MAXB,MLEVEL,MLEVELIST,1,(/001/))
      call grib_close_file(LUNIT2)
!        ENDIF
      ENDIF


      call grib_close_file(LUNIT)



 2000 STOP 'SUCCESSFULLY FINISHED CONVERT_PRE: CONGRATULATIONS'
 3000 STOP 'ROUTINE CONVERT_PRE: ERROR'
 9999 stop 'ROUTINE CONVERT_PRE: ERROR'
      END

      

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      INTEGER FUNCTION IA (FIELD1,NI,NJ,NK,G)

      IMPLICIT NONE
      INTEGER NI,NJ,NK,I,J,K
      REAL FIELD1(NI,NJ,NK)
      REAL G
      REAL RMIN,RMAX,XMAX,A,A1,A2

      RMAX=FIELD1(1,1,1)
      RMIN=FIELD1(1,1,1)
      
      DO 100 K=1,NK
      DO 100 J=1,NJ
        DO 100 I=1,NI
          IF (FIELD1(I,J,K).GT.RMAX)RMAX=FIELD1(I,J,K)
          IF (FIELD1(I,J,K).LT.RMIN)RMIN=FIELD1(I,J,K)
100   CONTINUE

      IF (ABS(RMIN).GT.RMAX.OR.ABS(RMIN).EQ.RMAX) THEN
      XMAX=ABS(RMIN)
      ELSE
      XMAX=RMAX
      ENDIF
      
      IF (XMAX.EQ.0) THEN
      IA = 0
      RETURN
      ENDIF
      
      A1=LOG10 ((G/10.d0)/XMAX)
      A2=LOG10 ( G/XMAX )
      IF(A1 .gt. A2) THEN
        A=A2
      ELSE 
        A=A1
      ENDIF
      
      IF (A.GT.0) IA=INT(A)
      IF (A.LT.0) IA=INT(A-1.0)
      
      RETURN
      END
      
      SUBROUTINE STATIS (NI,NJ,NK,PHI,RMS,MW,SIG)
	IMPLICIT REAL (A-H,O-Z)

      REAL PHI(NI,NJ,NK),SIG,MW,RMS,P
 
      N=NI*NJ*NK
 
      RMS=0.
	MW=0.
 
      DO 10 I=1,NI
      DO 10 J=1,NJ
        DO 10 K=1,NK
	      P=PHI(I,J,K)
          RMS=RMS+P*P
 		MW=MW+P
10    CONTINUE

      RMS=SQRT(RMS/N)
	MW=MW/N
	
	IF(RMS*RMS-MW*MW.LT.0.) THEN	  
	  SIG=0.0
	ELSE
	  SIG=SQRT(RMS*RMS-MW*MW)
	ENDIF
 
      RETURN
      END
      
