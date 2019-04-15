      MODULE PHTOGR

      INTEGER, PARAMETER :: MAXAUF=36000

      CONTAINS

      SUBROUTINE PHGR213(CXMN,FELD,WSAVE,IFAX,Z,MLAT,MNAUF,
     *MAXL,MAXB,MLEVEL)

C     DIE ROUTINE F]HRT EINE TRANSFORMATION EINER
C     FELDVARIABLEN VOM PHASENRAUM IN  DEN PHYSIKALISCHEN
C     RAUM AUF DAS REDUZIERTE GAUSS'SCHE GITTER DURCH
C
C     CXMN   = SPEKTRALKOEFFIZIENTEN IN DER REIHENFOLGE
C              CX00,CX01,CX11,CX02,....CXMNAUFMNAUF
C     FELD   = FELD DER METEOROLOGISCHEN VARIABLEN
C	WSAVE  = Working Array fuer Fouriertransformation
C     Z 	 = LEGENDREFUNKTIONSWERTE
C
C     MNAUF    ANZAHL DER FOURIERKOEFFIZIENTEN
C     MAXL     ANZAHL DER FUER DAS GITTER BENUTZTEN LAENGEN
C     MAXB     ANZAHL DER FUER DAS GITTER BENOETIGTEN BREITEN
C     MLEVEL   ANZAHL DER LEVELS, DIE TRANSFORMIERT WERDEN
C
      IMPLICIT NONE

C			Anzahl der Gitterpunkte auf jedem Breitenkreis
      INTEGER MLAT(MAXB/2)
      INTEGER K,MAXL,MAXB,MLEVEL,MNAUF
      INTEGER IND(MAXB)
      
			
C    FELD DER LEGENDREPOLYNOME FUER EINE BREITE
      REAL Z(0:((MNAUF+3)*(MNAUF+4))/2,MAXB/2)

      REAL CXMN(0:(MNAUF+1)*(MNAUF+2)-1,MLEVEL)
      REAL FELD(MAXL,MLEVEL)
      REAL WSAVE(8*MAXB+15,MAXB/2)
      INTEGER :: IFAX(10,MAXB)
      
      IND(1)=0
     	DO 7 K=2,MAXB/2
       	IND(K)=IND(K-1)+MLAT(K-1)
7 		CONTINUE

!$OMP PARALLEL DO SCHEDULE(DYNAMIC)
     	DO 17 K=1,MAXB/2
        CALL PHSYM(K,IND,CXMN,FELD,Z,WSAVE,IFAX,MLAT,
     *MNAUF,MAXL,MAXB,MLEVEL)

17 		CONTINUE
!$OMP END PARALLEL DO

        RETURN
        END SUBROUTINE PHGR213
C
C
      SUBROUTINE PHSYM(K,IND,CXMN,FELD,Z,WSAVE,IFAX,MLAT,
     *MNAUF,MAXL,MAXB,MLEVEL)

      IMPLICIT NONE

      INTEGER MLAT(MAXB/2)
      INTEGER K,L,I,J,LLS,LLPS,LL,LLP,MAXL,MAXB,MLEVEL,MNAUF
      INTEGER IND(MAXB)
      INTEGER :: IFAX(10,MAXB)
      
			
C    FELD DER FOURIERKOEFFIZIENTEN
      REAL :: CXMS(0:MAXAUF-1),CXMA(0:MAXAUF-1)

C    FELD DER LEGENDREPOLYNOME FUER EINE BREITE
      REAL Z(0:((MNAUF+3)*(MNAUF+4))/2,MAXB/2)
      REAL ACR,ACI,SCR,SCI

      REAL CXMN(0:(MNAUF+1)*(MNAUF+2)-1,MLEVEL)
      REAL FELD(MAXL,MLEVEL)
      REAL WSAVE(8*MAXB+15,MAXB/2)

      	DO 6 L=1,MLEVEL
      	 LL=0
      	 LLP=0
         DO 1 I=0,MNAUF
          SCR=0.D0
          SCI=0.D0
          ACR=0.D0
          ACI=0.D0
          LLS=LL
          LLPS=LLP
          IF(2*I+1.LT.MLAT(K)) THEN
C	Innerste Schleife aufgespalten um if-Abfrage zu sparen
            DO 18 J=I,MNAUF,2
              SCR=SCR+Z(LLP,K)*CXMN(2*LL,L)
              SCI=SCI+Z(LLP,K)*CXMN(2*LL+1,L)
              LL=LL+2            
              LLP=LLP+2            
18          CONTINUE
            LL=LLS+1
            LLP=LLPS+1
            DO 19 J=I+1,MNAUF,2
              ACR=ACR+Z(LLP,K)*CXMN(2*LL,L)
              ACI=ACI+Z(LLP,K)*CXMN(2*LL+1,L)
              LL=LL+2            
              LLP=LLP+2            
19          CONTINUE
          ENDIF
          LL=LLS+(MNAUF-I+1)
          LLP=LLPS+(MNAUF-I+3)
          CXMS(2*I)=SCR+ACR
          CXMS(2*I+1)=SCI+ACI
          CXMA(2*I)=SCR-ACR
          CXMA(2*I+1)=SCI-ACI
    1    CONTINUE
C         CALL FOURTR(CXMS,FELD(IND(k)+1,L),WSAVE(:,K),MNAUF,
C     *MLAT(K),1)
C         CALL FOURTR(CXMA,FELD(MAXL-IND(k)-MLAT(K)+1,L),
C     *WSAVE(:,K),MNAUF,MLAT(K),1)
         CALL RFOURTR(CXMS,WSAVE(:,K),IFAX(:,K),MNAUF,
     *MLAT(K),1)
          FELD(IND(k)+1:IND(K)+MLAT(K),L)=CXMS(0:MLAT(K)-1)
         CALL RFOURTR(CXMA,
     *WSAVE(:,K),IFAX(:,K),MNAUF,MLAT(K),1)
         FELD(MAXL-IND(k)-MLAT(K)+1:MAXL-IND(k),L)=CXMA(0:MLAT(K)-1)
C         WRITE(*,*) IND+1,FELD(IND+1,L)
6 			CONTINUE

      END SUBROUTINE PHSYM

      SUBROUTINE PHGCUT(CXMN,FELD,WSAVE,IFAX,Z,
     *                  MNAUF,MMAX,MAUF,MANF,MAXL,MAXB,MLEVEL)

C     DIE ROUTINE FUEHRT EINE TRANSFORMATION EINER
C     FELDVARIABLEN VOM PHASENRAUM IN  DEN PHYSIKALISCHEN
C     RAUM AUF KUGELKOORDINATEN DURCH. Es kann ein Teilausschnitt
C			Der Erde angegeben werden. Diese Routine ist langsamer als
C			phgrph
C
C     CXMN   = SPEKTRALKOEFFIZIENTEN IN DER REIHENFOLGE
C              CX00,CX01,CX11,CX02,....CXMNAUFMNAUF
C     FELD   = FELD DER METEOROLOGISCHEN VARIABLEN
C     BREITE = SINUS DER GEOGRAFISCHEN BREITEN
C
C     MNAUF    ANZAHL DER FOURIERKOEFFIZIENTEN
C     MAUF     ANZAHL DER LAENGEN UND DER FOURIERKOEFFIZIENTEN
C     MANF     ANFANG DES LAENGENBEREICHS FUER DAS GITTER,
C              AUF DAS INTERPOLIERT WERDEN SOLL
C     MAXL     ANZAHL DER FUER DAS GITTER BENUTZTEN LAENGEN
C     MAXB     ANZAHL DER FUER DAS GITTER BENOETIGTEN BREITEN
C     MLEVEL   ANZAHL DER LEVELS, DIE TRANSFORMIERT WERDEN
C
        IMPLICIT REAL (A-H,O-Z)

C    FELD DER FOURIERKOEFFIZIENTEN

C    FELD DER LEGENDREPOLYNOME FUER EINE BREITE
        REAL Z(0:((MMAX+3)*(MMAX+4))/2,MAXB)

        DIMENSION CXMN(0:(MMAX+1)*(MMAX+2)-1,MLEVEL)
        REAL FELD(MAXL,MAXB,MLEVEL)
      DIMENSION WSAVE(4*MAUF+15)
      INTEGER:: IFAX(10)
      
      LOGICAL SYM

C
C      write(*,*)mauf,mnauf,manf,maxl

     
        IF(MAUF.LE.MNAUF) WRITE(*,*) 'TOO COARSE LONGITUDE RESOLUTION'
          IF((MANF.LT.1).OR.(MAXL.LT.1).OR.
     *       (MANF.GT.MAUF).OR.(MAXL.GT.MAUF)) THEN
            WRITE(*,*) 'WRONG LONGITUDE RANGE',MANF,MAXL
            STOP
          ENDIF

C Pruefe, ob Ausgabegitter symmetrisch zum Aequator ist
C Wenn ja soll Symmetrie der Legendrepolynome ausgenutzt werden
      IF(MAXB .GT. 4) THEN
          SYM=.TRUE.
	    DO 11 J=5,5
	      IF(ABS(ABS(Z(100,J))-ABS(Z(100,MAXB+1-J))).GT.1E-11)
     *    SYM=.FALSE.
C	      WRITE(*,*) ABS(Z(100,J)),ABS(Z(100,MAXB+1-J))
11	  CONTINUE
      WRITE(*,*) 'Symmetrisch: ',SYM
      ELSE
        SYM=.FALSE.
      ENDIF

	
		IF(SYM) THEN
!$OMP PARALLEL DO 
      	DO J=1,(MAXB+1)/2
          CALL PHSYMCUT(J,CXMN,FELD,Z,WSAVE,IFAX,
     *MAUF,MNAUF,MAXL,MAXB,MLEVEL,MANF)

        ENDDO
!$OMP END PARALLEL DO
		ELSE
!$OMP PARALLEL DO 
        DO J=1,MAXB
            CALL PHGPNS(CXMN,FELD,Z,WSAVE,IFAX,
     *J,MNAUF,MAUF,MANF,MAXL,MAXB,MLEVEL)
        ENDDO
!$OMP END PARALLEL DO

      ENDIF


        RETURN
        END SUBROUTINE PHGCUT

        SUBROUTINE PHSYMCUT(J,CXMN,FELD,Z,WSAVE,IFAX,
     *MAUF,MNAUF,MAXL,MAXB,MLEVEL,MANF)

        IMPLICIT REAL (A-H,O-Z)

C    FELD DER FOURIERKOEFFIZIENTEN

        REAL :: CXM(0:MAXAUF-1),CXMA(0:MAXAUF-1)


C    FELD DER LEGENDREPOLYNOME FUER EINE BREITE
        REAL Z(0:((MNAUF+3)*(MNAUF+4))/2,MAXB)
        REAL SCR,SCI,ACR,ACI

        DIMENSION CXMN(0:(MNAUF+1)*(MNAUF+2)-1,MLEVEL)
        REAL FELD(MAXL,MAXB,MLEVEL)
      DIMENSION WSAVE(4*MAUF+15)
        INTEGER :: IFAX(10)

        DO 16 L=1,MLEVEL
      	 LL=0
      	 LLP=0
         DO 17 I=0,MNAUF
          SCR=0.D0
          SCI=0.D0
          ACR=0.D0
          ACI=0.D0
          LLS=LL
          LLPS=LLP
C	Innerste Schleife aufgespalten um if-Abfrage zu sparen
          DO 18 K=I,MNAUF,2
            SCR=SCR+Z(LLP,J)*CXMN(2*LL,L)
            SCI=SCI+Z(LLP,J)*CXMN(2*LL+1,L)
            LL=LL+2            
            LLP=LLP+2            
18        CONTINUE
          LL=LLS+1
          LLP=LLPS+1
          DO 19 K=I+1,MNAUF,2
            ACR=ACR+Z(LLP,J)*CXMN(2*LL,L)
            ACI=ACI +Z(LLP,J)*CXMN(2*LL+1,L)
            LL=LL+2            
            LLP=LLP+2            
19        CONTINUE
          LL=LLS+MNAUF-I+1
          LLP=LLPS+MNAUF-I+3
          CXM(2*I)=SCR+ACR
          CXM(2*I+1)=SCI+ACI
          CXMA(2*I)=SCR-ACR
          CXMA(2*I+1)=SCI-ACI
17       CONTINUE
         
         CALL RFOURTR(CXM,WSAVE,IFAX,MNAUF,MAUF,1)
         DO 26 I=0,MAXL-1
           IF(MANF+I.LE.MAUF) THEN
             FELD(I+1,J,L)=CXM(MANF+I-1)
           ELSE
             FELD(I+1,J,L)=CXM(MANF-MAUF+I-1)
           ENDIF
26       CONTINUE
         CALL RFOURTR(CXMA,WSAVE,IFAX,MNAUF,MAUF,1)
         DO 36 I=0,MAXL-1
           IF(MANF+I.LE.MAUF) THEN
             FELD(I+1,MAXB+1-J,L)=CXMA(MANF+I-1)
           ELSE
             FELD(I+1,MAXB+1-J,L)=CXMA(MANF-MAUF+I-1)
           ENDIF
36       CONTINUE
16 			CONTINUE

      END SUBROUTINE PHSYMCUT

      SUBROUTINE PHGPNS(CXMN,FELD,Z,WSAVE,IFAX,
     *J,MNAUF,MAUF,MANF,MAXL,MAXB,MLEVEL)

        IMPLICIT NONE
        INTEGER,intent(in) :: MNAUF,MAUF,MANF,J,MAXL,MAXB,MLEVEL
        REAL :: CXM(0:MAXAUF-1)
        REAL,intent(in) :: Z(0:((MNAUF+3)*(MNAUF+4))/2,MAXB)

        REAL,intent(in) :: CXMN(0:(MNAUF+1)*(MNAUF+2)-1,MLEVEL)

        REAL,intent(in) :: WSAVE(4*MAUF+15)

        REAL :: FELD(MAXL,MAXB,MLEVEL)
        INTEGER :: IFAX(10)

        INTEGER I,L

          DO L=1,MLEVEL
            CALL LEGTR(CXMN(:,L),CXM,Z(:,J),MNAUF,MAUF)
            CALL RFOURTR(CXM,WSAVE,IFAX,MNAUF,MAUF,1)
           
            DO I=0,MAXL-1
                  IF(MANF+I.LE.MAUF) THEN
                    FELD(I+1,J,L)=CXM(MANF+I-1)
                  ELSE
                    FELD(I+1,J,L)=CXM(MANF-MAUF+I-1)
                  ENDIF
            ENDDO
          ENDDO
      END SUBROUTINE PHGPNS
C
        SUBROUTINE LEGTR(CXMN,CXM,Z,MNAUF,MAUF)
        IMPLICIT NONE
        INTEGER MNAUF,MAUF,LL,LLP,I,J
        REAL CXM(0:MAXAUF-1)
        REAL CXMN(0:(MNAUF+1)*(MNAUF+2)-1)
        REAL Z(0:((MNAUF+3)*(MNAUF+4))/2)
        REAL CI,CR
C
C     DIESE ROUTINE BERECHNET DIE FOURIERKOEFFIZIENTEN CXM
C
        LL=0
        LLP=0
        DO 1 I=0,MNAUF
            CR=0.D0
            CI=0.D0
            DO 2 J=I,MNAUF
              CR=CR+Z(LLP)*CXMN(2*LL)
              CI=CI+Z(LLP)*CXMN(2*LL+1)
              LL=LL+1
              LLP=LLP+1
    2     CONTINUE
          LLP=LLP+2
          CXM(2*I)=CR
          CXM(2*I+1)=CI
    1 CONTINUE
        RETURN
        END SUBROUTINE LEGTR
C
C     
C
      SUBROUTINE RFOURTR(CXM,TRIGS,IFAX,MNAUF,MAXL,ISIGN)
C     BERECHNET DIE FOURIERSUMME MIT EINEM FFT-ALGORITHMUS
      IMPLICIT REAL (A-H,O-Z)
      DIMENSION CXM(0:MAXAUF-1)
      REAL :: WSAVE(2*MAXL),TRIGS(2*MAXL)
      INTEGER IFAX(10)

      DO I=MNAUF+1,MAXL-1
          CXM(2*I)=0.0
          CXM(2*I+1)=0.0
      ENDDO
      CALL FFT99(CXM,WSAVE,TRIGS,IFAX,1,1,MAXL,1,1)
      DO I=0,MAXL-1
        CXM(I)=CXM(I+1)
      ENDDO

      RETURN
      END SUBROUTINE RFOURTR
C     
C     
      SUBROUTINE GAULEG(X1,X2,X,W,N)
C     BERECHNET DIE GAUSS+SCHEN BREITEN
        IMPLICIT REAL (A-H,O-Z)
        DIMENSION X(N),W(N)
      PARAMETER (EPS=3.D-14)
      M=(N+1)/2
      XM=0.5D0*(X2+X1)
      XL=0.5D0*(X2-X1)
      DO 12 I=1,M
        Z=DCOS(3.141592654D0*(I-.25D0)/(N+.5D0))
1       CONTINUE
          P1=1.D0
          P2=0.D0
          DO 11 J=1,N
            P3=P2
            P2=P1
            P1=((2.D0*J-1.D0)*Z*P2-(J-1.D0)*P3)/J
11        CONTINUE
          PP=N*(Z*P1-P2)/(Z*Z-1.D0)
          Z1=Z
          Z=Z1-P1/PP
        IF(ABS(Z-Z1).GT.EPS)GO TO 1
        X(I)=XM-XL*Z
        X(N+1-I)=XM+XL*Z
        W(I)=2.D0*XL/((1.D0-Z*Z)*PP*PP)
        W(N+1-I)=W(I)
12    CONTINUE
      RETURN
      END SUBROUTINE GAULEG
C
C
        SUBROUTINE PLGNFA(LL,X,Z)
C
C PLGNDN BERECHNET ALLE NORMIERTEN ASSOZIIERTEN
C LEGENDREFUNKTIONEN VON P00(X) BIS PLL(X)
C UND SCHREIBT SIE IN DAS FELD Z
C Die Polynome sind wie im ECMWF indiziert, d.h.
C P00,P10,P11,P20,P21,P22,...
C	Ansonsten ist die Routine analog zu PLGNDN
C X IST DER COSINUS DES ZENITWINKELS ODER
C       DER SINUS DER GEOGRAFISCHEN BREITE
C
        IMPLICIT REAL (A-H,O-Z)
        DIMENSION Z(0:((LL+3)*(LL+4))/2)
C
      L=LL+2
      I=1
      Z(0)=1.D0
      FACT=1.D0
      POT=1.D0
      SOMX2=DSQRT(1.D0-X*X)
        DO 14 J=0,L
          DJ=DBLE(J)
        IF(J.GT.0) THEN
          FACT=FACT*(2.D0*DJ-1.D0)/(2.D0*DJ)
            POT=POT*SOMX2
          Z(I)=DSQRT((2.D0*DJ+1.D0)*FACT)*POT
          I=I+1
        ENDIF
          IF(J.LT.L) THEN
            Z(I)=X*
     *DSQRT((4.D0*DJ*DJ+8.D0*DJ+3.D0)/(2.D0*DJ+1.D0))*Z(I-1)
            I=I+1
          ENDIF
          DK=DJ+2.D0
        DO 14 K=J+2,L
          DDK=(DK*DK-DJ*DJ)
          Z(I)=X*DSQRT((4.D0*DK*DK-1.D0)/DDK)*Z(I-1)-
     *    DSQRT(((2.D0*DK+1.D0)*(DK-DJ-1.D0)*(DK+DJ-1.D0))/
     *    ((2.D0*DK-3.D0)*DDK))*Z(I-2)
          DK=DK+1.D0
          I=I+1
14    CONTINUE
      RETURN
      END SUBROUTINE PLGNFA


      SUBROUTINE DPLGND(MNAUF,Z,DZ)
C
C DPLGND BERECHNET DIE ABLEITUNG DER NORMIERTEN ASSOZIIERTEN
C LEGENDREFUNKTIONEN VON P00(X) BIS PLL(X)
C UND SCHREIBT SIE IN DAS FELD DZ
C DIE REIHENFOLGE IST
C P00(X),P01(X),P11(X),P02(X),P12(X),P22(X),..PLL(X)
C
        IMPLICIT REAL (A-H,O-Z)
        DIMENSION Z(0:((MNAUF+3)*(MNAUF+4))/2)
        DIMENSION DZ(0:((MNAUF+2)*(MNAUF+3))/2)
C
				IF(Z(0).NE.1.D0) THEN
			WRITE(*,*) 'DPLGND: Z(0) must be 1.0'
					STOP
				ENDIF
				
				LLP=0
				LLH=0
        DO 1 I=0,MNAUF+1
            DO 2 J=I,MNAUF+1
              IF(I.EQ.J) THEN
              	WURZELA=
     *DSQRT(DBLE((J+1)*(J+1)-I*I)/DBLE(4*(J+1)*(J+1)-1))
                DZ(LLH)=DBLE(J)*WURZELA*Z(LLP+1)
              ELSE
              		WURZELB=
     *DSQRT(DBLE((J+1)*(J+1)-I*I)/DBLE(4*(J+1)*(J+1)-1))
                DZ(LLH)=
     *DBLE(J)*WURZELB*Z(LLP+1)-DBLE(J+1)*WURZELA*Z(LLP-1)
     						WURZELA=WURZELB
	        ENDIF
	        LLH=LLH+1              
          LLP=LLP+1
2	      CONTINUE
        LLP=LLP+1
1	CONTINUE
	RETURN
	END SUBROUTINE DPLGND
	

* Spectral Filter of Sardeshmukh and Hoskins (1984, MWR)
* MM=Spectral truncation of field
* MMAX= Spectral truncation of filter
*
      SUBROUTINE SPFILTER(FELDMN,MM,MMAX)

      IMPLICIT NONE

      INTEGER MM,MMAX,I,J,K,L
      REAL FELDMN(0:(MM+1)*(MM+2)-1)
      REAL KMAX,SMAX,FAK

      SMAX=0.1
      KMAX=-ALOG(SMAX)
      KMAX=KMAX/(float(MMAX)*float(MMAX+1))**2
c      WRITE(*,*)'alogsmax',alog(smax),'KMAX:',KMAX
        l=0
        do i=0,MM
          do j=i,MM
c          write(*,*) i,j,feld(k),feld(k)*exp(-KMAX*(j*(j+1))**2)
            if(j .le. MMAX) then
c               fak=exp(-KMAX*(j*(j+1))**2)
               fak=1.0
               feldmn(2*l)=feldmn(2*l)*fak
               feldmn(2*l+1)=feldmn(2*l+1)*fak
            else
               feldmn(2*l)=0.
               feldmn(2*l+1)=0.
            endif
            l=l+1
          enddo
        enddo
      END SUBROUTINE SPFILTER

      END MODULE PHTOGR
    


































