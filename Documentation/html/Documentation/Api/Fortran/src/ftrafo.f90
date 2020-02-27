MODULE FTRAFO

!! Implementation of the spectral transformation using reduced the Gaussian grid

CONTAINS

! Implementierung der spektralen Transformationsmethode unter Verwendung
! des reduzierten Gauss'schen Gitters


  SUBROUTINE VDTOUV(XMN,XLAM,XPHI,GWSAVE,IFAX,P,MLAT,MNAUF,NI,NJ,NK)

!! Berechnung der scale winds aus Vorticity und Divergenz
!! uebergibt man in XMN die Divergenz, so wird der divergente Anteil des
!! Windes (XPHI=Ud,XPHI=Vd) zurueckgegeben, uebergibt man die Vorticity, so
!! erhaelt man den rotationellen Wind (XLAM=Vrot,XPHI=-Urot).
!! Summiert man beide, erhaelt man den gesamten Scale wind
! GWSAVE ist ein Hilfsfeld fuer die FFT
! P enthaelt die assoziierten Legendrepolynome, H deren Ableitung
! MLAT enthaelt die Anzahl der Gitterpunkte pro Breitenkreis
! MNAUF gibt die spektrale Aufloesung an,
! NI = Anzahl der Gauss'schen Gitterpunkte pro Flaeche
! NJ = Anzahl der Gauss'schen Breiten,
! NK = Anzahl der Niveaus

    USE PHTOGR

    IMPLICIT NONE
    INTEGER J,N,NI,NJ,NK,MNAUF,GGIND(NJ/2)
    INTEGER MLAT(NJ),IFAX(10,NJ)
    REAL XMN(0:(MNAUF+1)*(MNAUF+2)-1,NK)
    REAL P(0:(MNAUF+3)*(MNAUF+4)/2,NJ/2)
    REAL H(0:(MNAUF+2)*(MNAUF+3)/2)
    REAL XLAM(NI,NK),XPHI(NI,NK)
    REAL GWSAVE(8*NJ+15,NJ/2)
    REAL SCR,SCI,ACR,ACI,MUSCR,MUSCI,MUACR,MUACI
    REAL RT,IT

    GGIND(1)=0
    DO 4 J = 2,NJ/2
      GGIND(J)=GGIND(J-1)+MLAT(J-1)
4   CONTINUE

!$OMP PARALLEL DO SCHEDULE(DYNAMIC)
    DO 5 J = 1,NJ/2
      CALL VDUVSUB(J,XMN,XLAM,XPHI,GWSAVE,IFAX,P,GGIND(J),MLAT,MNAUF,NI,NJ,NK)
5   CONTINUE
!$OMP END PARALLEL DO

    RETURN

  END SUBROUTINE VDTOUV

  SUBROUTINE VDUVSUB(J,XMN,XLAM,XPHI,GWSAVE,IFAX,P,GGIND,MLAT,MNAUF,NI,NJ,NK)

    USE PHTOGR

    IMPLICIT NONE

    INTEGER J,K,M,N,NI,NJ,NK,MNAUF,GGIND,LL,LLP,LLH,LLS,LLPS,LLHS
    INTEGER MLAT(NJ),IFAX(10,NJ)
    REAL UFOUC(0:MAXAUF),MUFOUC(0:MAXAUF)
    REAL VFOUC(0:MAXAUF),MVFOUC(0:MAXAUF)
    REAL XMN(0:(MNAUF+1)*(MNAUF+2)-1,NK)
    REAL P(0:(MNAUF+3)*(MNAUF+4)/2,NJ/2)
    REAL H(0:(MNAUF+2)*(MNAUF+3)/2)
    REAL XLAM(NI,NK),XPHI(NI,NK)
    REAL GWSAVE(8*NJ+15,NJ/2)
    REAL ERAD,SCR,SCI,ACR,ACI,MUSCR,MUSCI,MUACR,MUACI
    REAL FAC(0:MNAUF),RT,IT

    ERAD = 6367470.D0

    FAC(0)=0.D0
    DO 12 N=1,MNAUF
      FAC(N)=-ERAD/DBLE(N)/DBLE(N+1)
12  CONTINUE

    CALL DPLGND(MNAUF,P(0,J),H)
    DO 3 K = 1,NK
      LL=0
      LLP=0
      LLH=0
      DO 2 M = 0,MNAUF
        SCR=0.D0
        SCI=0.D0
        ACR=0.D0
        ACI=0.D0
        MUSCR=0.D0
        MUSCI=0.D0
        MUACR=0.D0
        MUACI=0.D0
        LLS=LL
        LLPS=LLP
        LLHS=LLH
        IF (2*M+1 .LT. MLAT(J)) THEN
          DO 1 N = M,MNAUF,2
            RT=XMN(2*LL,K)*FAC(N)
            IT=XMN(2*LL+1,K)*FAC(N)
            SCR =SCR+ RT*P(LLP,J)
            SCI =SCI+ IT*P(LLP,J)
            MUACR =MUACR+ RT*H(LLH)
            MUACI =MUACI+ IT*H(LLH)
            LL=LL+2
            LLP=LLP+2
            LLH=LLH+2
1         CONTINUE
          LL=LLS+1
          LLP=LLPS+1
          LLH=LLHS+1
          DO 11 N = M+1,MNAUF,2
            RT=XMN(2*LL,K)*FAC(N)
            IT=XMN(2*LL+1,K)*FAC(N)
            ACR =ACR+ RT*P(LLP,J)
            ACI =ACI+ IT*P(LLP,J)
            MUSCR =MUSCR+ RT*H(LLH)
            MUSCI =MUSCI+ IT*H(LLH)
            LL=LL+2
            LLP=LLP+2
            LLH=LLH+2
11        CONTINUE
        END IF
        LL=LLS+(MNAUF-M+1)
        LLP=LLPS+(MNAUF-M+3)
        LLH=LLHS+(MNAUF-M+2)

        UFOUC(2*M)=-M*(SCI-ACI)
        UFOUC(2*M+1)=M*(SCR-ACR)
        VFOUC(2*M)=-M*(SCI+ACI)
        VFOUC(2*M+1)=M*(SCR+ACR)

        MUFOUC(2*M)=-(MUSCR-MUACR)
        MUFOUC(2*M+1)=-(MUSCI-MUACI)
        MVFOUC(2*M)=-(MUSCR+MUACR)
        MVFOUC(2*M+1)=-(MUSCI+MUACI)
2     CONTINUE

      CALL RFOURTR(VFOUC,GWSAVE(:,J),IFAX(:,J),MNAUF,MLAT(J),1)
      XLAM(GGIND+1:GGIND+MLAT(J),K)=VFOUC(0:MLAT(J)-1)
      CALL RFOURTR(UFOUC,GWSAVE(:,J),IFAX(:,J),MNAUF,MLAT(J),1)
      XLAM(NI-GGIND-MLAT(J)+1:NI-GGIND,K)=UFOUC(0:MLAT(J)-1)

      CALL RFOURTR(MVFOUC,GWSAVE(:,J),IFAX(:,J),MNAUF,MLAT(J),1)
      XPHI(GGIND+1:GGIND+MLAT(J),K)=MVFOUC(0:MLAT(J)-1)
      CALL RFOURTR(MUFOUC,GWSAVE(:,J),IFAX(:,J),MNAUF,MLAT(J),1)
      XPHI(NI-GGIND-MLAT(J)+1:NI-GGIND,K)=MUFOUC(0:MLAT(J)-1)

3   CONTINUE

    RETURN

  END SUBROUTINE VDUVSUB


  SUBROUTINE PHGRAD(XMN,XLAM,XPHI,GWSAVE,IFAX,P,H,MLAT,MNAUF,NI,NJ,NK)

!! Berechnung des Gradienten eines Skalars aus dem Feld des
!! Skalars XMN im Phasenraum. Zurueckgegeben werden die Felder der
!! Komponenten des horizontalen Gradienten XLAM,XPHI auf dem Gauss'schen Gitter.
! GWSAVE ist ein Hilfsfeld fuer die FFT
! P enthaelt die assoziierten Legendrepolynome, H deren Ableitung
! MLAT enthaelt die Anzahl der Gitterpunkte pro Breitenkreis
! MNAUF gibt die spektrale Aufloesung an,
! NI = Anzahl der Gauss'schen Gitterpunkte,
! NJ = Anzahl der Gauss'schen Breiten,
! NK = Anzahl der Niveaus

    USE PHTOGR

    IMPLICIT NONE

    INTEGER J,K,M,N,NI,NJ,NK,MNAUF,GGIND,LL,LLP,LLH,LLS,LLPS,LLHS
    INTEGER MLAT(NJ),IFAX(10,NJ)
    REAL UFOUC(0:MAXAUF),MUFOUC(0:MAXAUF)
    REAL VFOUC(0:MAXAUF),MVFOUC(0:MAXAUF)
    REAL XMN(0:(MNAUF+1)*(MNAUF+2)-1,NK)
    REAL P(0:(MNAUF+3)*(MNAUF+4)/2,NJ/2)
    REAL H(0:(MNAUF+2)*(MNAUF+3)/2)
    REAL XLAM(NI,NK),XPHI(NI,NK)
    REAL GWSAVE(8*NJ+15,NJ/2)
    REAL ERAD
    REAL SCR,SCI,ACR,ACI,MUSCR,MUSCI,MUACR,MUACI,RT,IT

    ERAD = 6367470.0

    GGIND=0
    DO 4 J = 1,NJ/2
      CALL DPLGND(MNAUF,P(0,J),H)
      DO 3 K = 1,NK
        LL=0
        LLP=0
        LLH=0
        DO 2 M = 0,MNAUF
          SCR=0.D0
          SCI=0.D0
          ACR=0.D0
          ACI=0.D0
          MUSCR=0.D0
          MUSCI=0.D0
          MUACR=0.D0
          MUACI=0.D0
          LLS=LL
          LLPS=LLP
          LLHS=LLH
          IF (2*M+1 .LT. MLAT(J)) THEN
            DO 1 N = M,MNAUF,2
              RT=XMN(2*LL,K)
              IT=XMN(2*LL+1,K)
              SCR =SCR+ RT*P(LLP,J)
              SCI =SCI+ IT*P(LLP,J)
              MUACR =MUACR+RT*H(LLH)
              MUACI =MUACI+ IT*H(LLH)
              LL=LL+2
              LLP=LLP+2
              LLH=LLH+2
1           CONTINUE
            LL=LLS+1
            LLP=LLPS+1
            LLH=LLHS+1
            DO 11 N = M+1,MNAUF,2
              RT=XMN(2*LL,K)
              IT=XMN(2*LL+1,K)
              ACR =ACR+ RT*P(LLP,J)
              ACI =ACI+ IT*P(LLP,J)
              MUSCR =MUSCR+ RT*H(LLH)
              MUSCI =MUSCI+ IT*H(LLH)
              LL=LL+2
              LLP=LLP+2
              LLH=LLH+2
11          CONTINUE
          END IF
          LL=LLS+(MNAUF-M+1)
          LLP=LLPS+(MNAUF-M+3)
          LLH=LLHS+(MNAUF-M+2)

          UFOUC(2*M)=-M*(SCI-ACI)/ERAD
          UFOUC(2*M+1)=M*(SCR-ACR)/ERAD
          VFOUC(2*M)=-M*(SCI+ACI)/ERAD
          VFOUC(2*M+1)=M*(SCR+ACR)/ERAD

          MUFOUC(2*M)=-(MUSCR-MUACR)/ERAD
          MUFOUC(2*M+1)=-(MUSCI-MUACI)/ERAD
          MVFOUC(2*M)=-(MUSCR+MUACR)/ERAD
          MVFOUC(2*M+1)=-(MUSCI+MUACI)/ERAD
2       CONTINUE

        CALL RFOURTR(VFOUC,GWSAVE(:,J),IFAX(:,J),MNAUF,MLAT(J),1)
        XLAM(GGIND+1:GGIND+MLAT(J),K)=VFOUC(0:MLAT(J)-1)
        CALL RFOURTR(UFOUC,GWSAVE(:,J),IFAX(:,J),MNAUF,MLAT(J),1)
        XLAM(NI-GGIND-MLAT(J)+1:NI-GGIND,K)=UFOUC(0:MLAT(J)-1)

        CALL RFOURTR(MVFOUC,GWSAVE(:,J),IFAX(:,J),MNAUF,MLAT(J),1)
        XPHI(GGIND+1:GGIND+MLAT(J),K)=MVFOUC(0:MLAT(J)-1)
        CALL RFOURTR(MUFOUC,GWSAVE(:,J),IFAX(:,J),MNAUF,MLAT(J),1)
        XPHI(NI-GGIND-MLAT(J)+1:NI-GGIND,K)=MUFOUC(0:MLAT(J)-1)

3     CONTINUE
      GGIND=GGIND+MLAT(J)
4   CONTINUE


    RETURN

  END SUBROUTINE PHGRAD


  SUBROUTINE PHGRACUT(XMN,XLAM,XPHI,GWSAVE,IFAX,P,H,MAUF,MNAUF,NI,NJ,MANF,NK)

!! Berechnung des Gradienten eines Skalars aus dem Feld des
!! Skalars XMN im Phasenraum. Zurueckgegeben werden die Felder der
!! Komponenten des horizontalen Gradienten XLAM,XPHI auf dem Gauss'schen Gitter.
! GWSAVE ist ein Hilfsfeld fuer die FFT
! P enthaelt die assoziierten Legendrepolynome, H deren Ableitung
! MLAT enthaelt die Anzahl der Gitterpunkte pro Breitenkreis
! MNAUF gibt die spektrale Aufloesung an,
! NI = Anzahl der Gauss'schen Gitterpunkte,
! NJ = Anzahl der Gauss'schen Breiten,
! NK = Anzahl der Niveaus

    USE PHTOGR

    IMPLICIT NONE

    INTEGER J,K,M,N,NI,NJ,NK,MNAUF,GGIND,LL,LLP,LLH,LLS,LLPS,LLHS
    INTEGER MAUF,MANF,I,IFAX(10)
    REAL UFOUC(0:MAXAUF),MUFOUC(0:MAXAUF)
    REAL VFOUC(0:MAXAUF),MVFOUC(0:MAXAUF)
    REAL XMN(0:(MNAUF+1)*(MNAUF+2)-1,NK)
    REAL P(0:(MNAUF+3)*(MNAUF+4)/2,NJ)
    REAL H(0:(MNAUF+2)*(MNAUF+3)/2)
    REAL XLAM(NI,NJ,NK),XPHI(NI,NJ,NK)
    REAL HLAM(MAXAUF,2),HPHI(MAXAUF,2)
    REAL GWSAVE(4*MAUF+15)
    REAL ERAD
    REAL SCR,SCI,ACR,ACI,MUSCR,MUSCI,MUACR,MUACI,RT,IT

    ERAD = 6367470.0

    GGIND=0
    DO 4 J = 1,NJ
      CALL DPLGND(MNAUF,P(0,J),H)
      DO 3 K = 1,NK
        LL=0
        LLP=0
        LLH=0
        DO 2 M = 0,MNAUF
          SCR=0.D0
          SCI=0.D0
          ACR=0.D0
          ACI=0.D0
          MUSCR=0.D0
          MUSCI=0.D0
          MUACR=0.D0
          MUACI=0.D0
          LLS=LL
          LLPS=LLP
          LLHS=LLH
          IF (2*M+1 .LT. MAUF) THEN
            DO 1 N = M,MNAUF,2
              RT=XMN(2*LL,K)
              IT=XMN(2*LL+1,K)
              SCR =SCR+ RT*P(LLP,J)
              SCI =SCI+ IT*P(LLP,J)
              MUACR =MUACR+RT*H(LLH)
              MUACI =MUACI+ IT*H(LLH)
              LL=LL+2
              LLP=LLP+2
              LLH=LLH+2
1           CONTINUE
            LL=LLS+1
            LLP=LLPS+1
            LLH=LLHS+1
            DO 11 N = M+1,MNAUF,2
              RT=XMN(2*LL,K)
              IT=XMN(2*LL+1,K)
              ACR =ACR+ RT*P(LLP,J)
              ACI =ACI+ IT*P(LLP,J)
              MUSCR =MUSCR+ RT*H(LLH)
              MUSCI =MUSCI+ IT*H(LLH)
              LL=LL+2
              LLP=LLP+2
              LLH=LLH+2
11          CONTINUE
          END IF
          LL=LLS+(MNAUF-M+1)
          LLP=LLPS+(MNAUF-M+3)
          LLH=LLHS+(MNAUF-M+2)

          UFOUC(2*M)=-M*(SCI-ACI)/ERAD
          UFOUC(2*M+1)=M*(SCR-ACR)/ERAD
          VFOUC(2*M)=-M*(SCI+ACI)/ERAD
          VFOUC(2*M+1)=M*(SCR+ACR)/ERAD

          MUFOUC(2*M)=-(MUSCR-MUACR)/ERAD
          MUFOUC(2*M+1)=-(MUSCI-MUACI)/ERAD
          MVFOUC(2*M)=-(MUSCR+MUACR)/ERAD
          MVFOUC(2*M+1)=-(MUSCI+MUACI)/ERAD
2       CONTINUE

        CALL RFOURTR(VFOUC,GWSAVE,IFAX,MNAUF,MAUF,1)

        CALL RFOURTR(MVFOUC,GWSAVE,IFAX,MNAUF,MAUF,1)

        DO 6 I=0,NI-1
          IF (MANF+I .LE.  MAUF) THEN
            XLAM(I+1,J,K)=VFOUC(MANF+I-1)
            XPHI(I+1,J,K)=MVFOUC(MANF+I-1)
          ELSE
            XLAM(I+1,J,K)=VFOUC(MANF-MAUF+I-1)
            XPHI(I+1,J,K)=MVFOUC(MANF-MAUF+I-1)
          END IF
6       CONTINUE
3     CONTINUE
      GGIND=GGIND+MAUF
4   CONTINUE

    RETURN

  END SUBROUTINE PHGRACUT

  SUBROUTINE CONTGL(PS,DPSDL,DPSDM,DIV,U,V,BREITE,ETA,MLAT,A,B,NI,NJ,NK)

!! Berechnung der Divergenz aus dem Windfeld (U,V)
!! im Phasenraum. Zurueckgegeben werden die Felder der
!! Komponenten des horizontalen Gradienten XLAM,XPHI auf dem Gauss'schen Gitter.
! GWSAVE ist ein Hilfsfeld fuer die FFT
! P enthaelt die assoziierten Legendrepolynome, H deren Ableitung
! MLAT enthaelt die Anzahl der Gitterpunkte pro Breitenkreis
! MNAUF gibt die spektrale Aufloesung an,
! NI = Anzahl der Gauss'schen Gitterpunkte,
! NJ = Anzahl der Gauss'schen Breiten,
! NK = Anzahl der Niveaus
! Beachte, dass das Windfeld eine um 1 erhoehte Aufloesung in mu-Richtung hat.

    IMPLICIT NONE

    INTEGER NI,NJ,NK,I,J,K,MLAT(NJ),L

    REAL A(NK+1),B(NK+1)
    REAL PS(NI),DPSDL(NI),DPSDM(NI)
    REAL DIV(NI,NK),U(NI,NK),V(NI,NK),ETA(NI,NK)
    REAL BREITE(NJ)

    REAL DIVT1,DIVT2,POB,PUN,DPSDT,COSB

    L=0
    DO 4 J=1,NJ
      COSB=(1.0-BREITE(J)*BREITE(J))
      DO 3 I=1,MLAT(J)
        L=L+1
        DIVT1=0.0
        DIVT2=0.0
        DO 1 K=1,NK
          POB=A(K)+B(K)*PS(L)
          PUN=A(K+1)+B(K+1)*PS(L)

          DIVT1=DIVT1+DIV(L,K)*(PUN-POB)
          IF (COSB .GT. 0.) THEN
            DIVT2=DIVT2+(B(K+1)-B(K))*PS(L)* &
              (U(L,K)*DPSDL(L)+V(L,K)*DPSDM(L))/COSB
          END IF

          ETA(L,K)=-DIVT1-DIVT2
1       CONTINUE

        DPSDT=(-DIVT1-DIVT2)/PS(L)

        DO 2 K=1,NK
          ETA(L,K)=ETA(L,K)-DPSDT*B(K+1)*PS(L)
2       CONTINUE
        PS(L)=DPSDT*PS(L)
3     CONTINUE
4   CONTINUE

    RETURN

  END SUBROUTINE CONTGL

  SUBROUTINE OMEGA(PS,DPSDL,DPSDM,DIV,U,V,BREITE,E,MLAT,A,B,NGI,NGJ,MKK)

!! calculates $\omega$ in the hybrid ($\eta$-) coordinate system

! OMEGA berechnet omega im Hybridkoordinatensystem
! PS ist der Bodendruck,
! DPSDL,DPSDM sind die Komponenten des Gradienten des Logarithmus des
! Bodendrucks
! DIV,U,V sind die horizontale Divergenz und das horizontale Windfeld
! BREITE ist das Feld der Gauss'schen Breiten
! E ist omega,

    IMPLICIT NONE

    INTEGER I,J,K,L,NGI,NGJ,MKK,MLAT(NGJ)

    REAL PS(NGI),DPSDL(NGI),DPSDM(NGI),A(MKK+1),B(MKK+1)
    REAL DIV(NGI,MKK),U(NGI,MKK),V(NGI,MKK),E(NGI,MKK)
    REAL BREITE(NGJ)

    REAL DIVT1,DIVT2,POB,PUN,DP,X,Y,COSB
    REAL DIVT3(MKK+2)

    L=0
    DO 4 J=1,NGJ
      COSB=(1.0-BREITE(J)*BREITE(J))
      DO 3 I=1,MLAT(J)
        L=L+1
        DIVT1=0.0
        DIVT2=0.0
        DIVT3(1)=0.0
        DO 1 K=1,MKK
          POB=A(K)+B(K)*PS(L)
          PUN=A(K+1)+B(K+1)*PS(L)
          DP=PUN-POB

          Y=PS(L)*(U(L,K)*DPSDL(L)+V(L,K)*DPSDM(L))/COSB
          IF (K .LT. 3) THEN
            X=0.0
          ELSE
            X=(B(K+1)-B(K))*Y
          END IF

          DIVT1=DIVT1+DIV(L,K)*DP
          DIVT2=DIVT2+X

          DIVT3(K+1)=-DIVT1-DIVT2

          IF (K .GT. 1) THEN
            E(L,K) = 0.5*(POB+PUN)/ &
              DP*Y*((B(K+1)-B(K))+(A(K+1)*B(K)-A(K)*B(K+1))/DP*LOG(PUN/POB))
          ELSE
            E(L,K) = 0.0
          END IF

          E(L,K) = E(L,K)+0.5*(DIVT3(K)+DIVT3(K+1))

1       CONTINUE
3     CONTINUE
4   CONTINUE

    RETURN

  END SUBROUTINE OMEGA

END MODULE FTRAFO
