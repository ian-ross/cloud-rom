!----------------------------------------------------------------------
! Full Berton (2023) four-state equilibrium problem for AUTO-07p.
!
! U(1)=z [m], U(2)=u [m/s], U(3)=w [m/s], U(4)=m [kg].
! x is omitted because it is cyclic.  Formulas are ported from
! src/cloud_rom/berton2023.py in physical SI units.
!----------------------------------------------------------------------
MODULE berton_full_model
  IMPLICIT NONE
  INTEGER, PARAMETER :: dp = KIND(1.0D0)
  DOUBLE PRECISION, PARAMETER :: pi = 3.1415926535897932384626433832795D0

  TYPE :: Local
    DOUBLE PRECISION :: T_a,p_a,p_v,p,p_vsl,p_vsi,H_l,S_l,S_i,rho_a,mu_a,D_v,K_a
    DOUBLE PRECISION :: U_a,W_a,V,a,c,c_B,Area,D_i,r_i,Cap,Re,C_D,k,Sc,f_v,eta,eta_a,Rad
    DOUBLE PRECISION :: driving_factor,m_dot,psi,rho_ie,vertical_force
  END TYPE Local

CONTAINS

  DOUBLE PRECISION FUNCTION plin(z,zs,ys,n)
    INTEGER, INTENT(IN) :: n
    DOUBLE PRECISION, INTENT(IN) :: z,zs(n),ys(n)
    INTEGER :: i
    IF (z <= zs(1)) THEN
      plin = ys(1); RETURN
    END IF
    DO i=1,n-1
      IF (z <= zs(i+1)) THEN
        plin = ys(i) + (ys(i+1)-ys(i))*(z-zs(i))/(zs(i+1)-zs(i))
        RETURN
      END IF
    END DO
    plin = ys(n)
  END FUNCTION plin

  SUBROUTINE init_defaults(par)
    DOUBLE PRECISION, INTENT(INOUT) :: par(*)
    par(1)=10000D0; par(2)=0.6D0; par(3)=1D0; par(4)=0.61D0; par(5)=1D0; par(6)=1D0
    par(7)=300D0
    par(8)=5000D0; par(9)=5D0; par(10)=8000D0; par(11)=10D0; par(12)=16000D0; par(13)=-30D0
    par(14)=0D0; par(15)=293.15D0; par(16)=2000D0; par(17)=273.15D0; par(18)=8000D0; par(19)=223.15D0
    par(20)=14000D0; par(21)=213.15D0; par(22)=20000D0; par(23)=213.15D0
    par(24)=0D0; par(25)=0.20D0; par(26)=2000D0; par(27)=0.30D0; par(28)=4000D0; par(29)=0.40D0
    par(30)=10000D0; par(31)=0.20D0; par(32)=15000D0; par(33)=0D0; par(34)=20000D0
    par(35)=9000D0; par(36)=0.9D0; par(37)=10000D0; par(38)=1.1D0; par(39)=0D0
    par(40)=2D0; par(41)=20.44D-6; par(42)=pi/4D0; par(43)=0D0; par(44)=2D0
    par(45)=920D0; par(46)=9.81D0; par(47)=7.27D-5; par(48)=287.05D0; par(49)=461D0
    par(50)=0.622D0; par(51)=2.837D6; par(52)=5.67D-8; par(53)=1D0
  END SUBROUTINE init_defaults

  DOUBLE PRECISION FUNCTION horizontal_wind(z,par)
    DOUBLE PRECISION, INTENT(IN) :: z,par(*)
    IF (z <= par(8)) THEN
      horizontal_wind = par(9)/par(8)*z
    ELSEIF (z <= par(10)) THEN
      horizontal_wind = par(9)+(par(11)-par(9))/(par(10)-par(8))*(z-par(8))
    ELSEIF (z <= par(12)) THEN
      horizontal_wind = par(13)+(par(11)-par(13))/(par(10)-par(12))*(z-par(12))
    ELSE
      horizontal_wind = par(13)
    END IF
  END FUNCTION horizontal_wind

  DOUBLE PRECISION FUNCTION updraft(z,par)
    DOUBLE PRECISION, INTENT(IN) :: z,par(*)
    DOUBLE PRECISION :: zW1
    zW1 = par(1)-par(7)
    IF (z <= zW1) THEN
      updraft = 0D0
    ELSEIF (z <= par(1)) THEN
      updraft = par(2)*(z-zW1)/(par(1)-zW1)
    ELSE
      updraft = par(2)
    END IF
  END FUNCTION updraft

  DOUBLE PRECISION FUNCTION temperature(z,par)
    DOUBLE PRECISION, INTENT(IN) :: z,par(*)
    DOUBLE PRECISION :: zs(5),ys(5)
    zs=(/par(14),par(16),par(18),par(20),par(22)/); ys=(/par(15),par(17),par(19),par(21),par(23)/)
    temperature=plin(z,zs,ys,5)
  END FUNCTION temperature

  DOUBLE PRECISION FUNCTION humidity(z,par)
    DOUBLE PRECISION, INTENT(IN) :: z,par(*)
    DOUBLE PRECISION :: zs(6),ys(6)
    zs=(/par(24),par(26),par(28),par(30),par(32),par(34)/)
    ys=(/par(25),par(27),par(29),par(4),par(31),par(33)/)
    humidity=plin(z,zs,ys,6)
  END FUNCTION humidity

  DOUBLE PRECISION FUNCTION eta_atm(z,par)
    DOUBLE PRECISION, INTENT(IN) :: z,par(*)
    DOUBLE PRECISION :: zs(2),ys(2)
    zs=(/par(35),par(37)/); ys=(/par(36),par(38)/)
    eta_atm=plin(z,zs,ys,2)
  END FUNCTION eta_atm

  DOUBLE PRECISION FUNCTION p_vsl(T)
    DOUBLE PRECISION, INTENT(IN) :: T
    p_vsl=EXP(-6096.9385D0/T + 21.2409642D0 - 2.711193D-2*T + 1.673952D-5*T*T + 2.433502D0*LOG(T))
  END FUNCTION p_vsl

  DOUBLE PRECISION FUNCTION p_vsi(T)
    DOUBLE PRECISION, INTENT(IN) :: T
    p_vsi=EXP(-6024.5282D0/T + 29.32707D0 + 1.0613868D-2*T - 1.3198825D-5*T*T - 0.49382577D0*LOG(T))
  END FUNCTION p_vsi

  SUBROUTINE geom_from_mass(m,par,V,aa,cc,cB,Area,Di,ri,Cap,psi,rhoie)
    DOUBLE PRECISION, INTENT(IN) :: m,par(*)
    DOUBLE PRECISION, INTENT(OUT) :: V,aa,cc,cB,Area,Di,ri,Cap,psi,rhoie
    DOUBLE PRECISION :: lo,hi,mid,phi,rhoi,fmid
    INTEGER :: it
    phi=par(40); cB=par(41); rhoi=par(45); V=m/rhoi
    lo=0D0; hi=MAX((V/MAX(phi,1D-30))**(1D0/3D0)*10D0,cB*10D0,1D-12)
    DO WHILE (SQRT(3D0)*(2D0*phi*hi+cB)*hi*hi - V <= 0D0)
      hi=2D0*hi
    END DO
    DO it=1,100
      mid=0.5D0*(lo+hi)
      fmid=SQRT(3D0)*(2D0*phi*mid+cB)*mid*mid - V
      IF (fmid > 0D0) THEN
        hi=mid
      ELSE
        lo=mid
      END IF
    END DO
    aa=0.5D0*(lo+hi); cc=phi*aa
    Area=6D0*aa*(2D0*cc+SQRT((cc-cB)**2+3D0*aa*aa/4D0))
    Di=(6D0*V/pi)**(1D0/3D0); ri=0.5D0*Di; Cap=0.751D0*aa+0.491D0*cc
    psi=1D0-cB/cc; rhoie=V/(3D0*SQRT(3D0)*aa*aa*cc)*rhoi
  END SUBROUTINE geom_from_mass

  DOUBLE PRECISION FUNCTION drag_coeff(Re)
    DOUBLE PRECISION, INTENT(IN) :: Re
    drag_coeff=64D0/(pi*Re)*(1D0+0.078D0*Re**0.945D0)
  END FUNCTION drag_coeff

  DOUBLE PRECISION FUNCTION damping(CD,Re,mu,ri,m)
    DOUBLE PRECISION, INTENT(IN) :: CD,Re,mu,ri,m
    damping=6D0*pi*CD*Re*mu*ri/(24D0*m)
  END FUNCTION damping

  DOUBLE PRECISION FUNCTION terminal_re(rho,ell,mu,m,g_eff)
    DOUBLE PRECISION, INTENT(IN) :: rho,ell,mu,m,g_eff
    DOUBLE PRECISION :: lo,hi,mid,CD,k,terminal_speed,fmid
    INTEGER :: it
    lo=1D-12; hi=100D0
    DO
      CD=drag_coeff(hi); k=damping(CD,hi,mu,0.5D0*ell,m); terminal_speed=g_eff/k
      IF (hi-rho*ell*terminal_speed/mu >= 0D0) EXIT
      hi=2D0*hi
      IF (hi > 1D8) EXIT
    END DO
    DO it=1,100
      mid=0.5D0*(lo+hi); CD=drag_coeff(mid); k=damping(CD,mid,mu,0.5D0*ell,m); terminal_speed=g_eff/k
      fmid=mid-rho*ell*terminal_speed/mu
      IF (fmid > 0D0) THEN; hi=mid; ELSE; lo=mid; END IF
    END DO
    terminal_re=0.5D0*(lo+hi)
  END FUNCTION terminal_re

  SUBROUTINE eval_local(z,u,w,m,par,L)
    DOUBLE PRECISION, INTENT(IN) :: z,u,w,m,par(*)
    TYPE(Local), INTENT(OUT) :: L
    DOUBLE PRECISION :: delta,speed,ell,X,Bi,Rsrc,denom,g_eff,radR
    L%T_a=temperature(z,par); L%p_a=101493D0*EXP(-z/7500D0); L%H_l=humidity(z,par)
    L%p_vsl=p_vsl(L%T_a); L%p_vsi=p_vsi(L%T_a)
    delta=SQRT((L%p_a-L%p_vsl)**2+4D0*L%H_l*L%p_a*L%p_vsl)
    L%p_v=(-L%p_a+L%p_vsl+delta)/2D0; L%p=L%p_a+L%p_v
    L%S_l=L%p_v/L%p_vsl; L%S_i=L%p_v/L%p_vsi
    L%rho_a=L%p_a/(par(48)*L%T_a)
    L%mu_a=1D-5*(1.718D0+0.0049D0*(L%T_a-273.15D0)-1.2D-5*(L%T_a-273.15D0)**2)
    L%D_v=8.28D-3*(L%T_a/L%p)*(293D0/(L%T_a+120D0))*(L%T_a/273D0)**1.5D0
    L%K_a=2.42D-2*(293D0/(L%T_a+120D0))*(L%T_a/273D0)**1.5D0
    L%U_a=horizontal_wind(z,par); L%W_a=updraft(z,par)
    CALL geom_from_mass(MAX(m,1D-30),par,L%V,L%a,L%c,L%c_B,L%Area,L%D_i,L%r_i,L%Cap,L%psi,L%rho_ie)
    ell=MERGE(L%D_i,L%r_i,par(44) >= 1.5D0)
    speed=SQRT((u-L%U_a)**2+(w-L%W_a)**2)
    L%Re=L%rho_a*ell*speed/L%mu_a
    IF (L%Re <= 1D-12) THEN
      g_eff=par(46)*(1D0-L%rho_a/par(45)); L%Re=terminal_re(L%rho_a,ell,L%mu_a,MAX(m,1D-30),g_eff)
    END IF
    L%Re=MAX(L%Re,1D-12); L%C_D=drag_coeff(L%Re)
    L%k=par(6)*damping(L%C_D,L%Re,L%mu_a,L%r_i,MAX(m,1D-30))
    L%Sc=L%mu_a/(L%rho_a*L%D_v)
    X=L%Sc**(1D0/3D0)*SQRT(L%Re); L%f_v=1D0+0.039D0*X+0.1447D0*X*X
    L%eta_a=eta_atm(z,par); L%eta=(1D0-par(39))*L%eta_a+par(39)*par(5)
    Bi=par(53)*par(52)*L%T_a**4; Rsrc=L%Area*(L%eta-1D0)*Bi
    L%Rad=Rsrc/(4D0*pi*L%Cap*L%K_a*L%T_a)*(par(51)/(par(49)*L%T_a)-1D0)
    radR=par(3)*L%Rad
    L%driving_factor=L%S_i-1D0-radR
    denom=par(49)*L%T_a/(L%p_vsi*L%D_v)+par(51)/(L%K_a*L%T_a)*(par(51)/(par(49)*L%T_a)-1D0)
    L%m_dot=4D0*pi*L%Cap*L%f_v*L%driving_factor/denom
    L%vertical_force=-L%k*(w-L%W_a)-par(46)*(1D0-L%rho_a/par(45))+2D0*(par(43)*par(47)*COS(par(42)))*u
  END SUBROUTINE eval_local

  SUBROUTINE rhs_full(uvec,par,f)
    DOUBLE PRECISION, INTENT(IN) :: uvec(4),par(*)
    DOUBLE PRECISION, INTENT(OUT) :: f(4)
    TYPE(Local) :: L
    DOUBLE PRECISION :: fc
    CALL eval_local(uvec(1),uvec(2),uvec(3),uvec(4),par,L)
    fc=par(43)*par(47)*COS(par(42))
    f(1)=uvec(3)
    f(2)=-L%k*(uvec(2)-L%U_a)-2D0*fc*uvec(3)
    f(3)=L%vertical_force
    f(4)=L%m_dot
  END SUBROUTINE rhs_full

  SUBROUTINE set_pvls(uvec,par)
    DOUBLE PRECISION, INTENT(IN) :: uvec(4)
    DOUBLE PRECISION, INTENT(INOUT) :: par(*)
    TYPE(Local) :: L,Lp,Lm
    DOUBLE PRECISION :: dz,dm,Fp(4),Fm(4),base(4),dmuse,z_force_slope,z_growth_slope,m_force_slope,m_growth_slope
    CALL eval_local(uvec(1),uvec(2),uvec(3),uvec(4),par,L)
    dz=1D0; base=uvec; base(1)=uvec(1)+dz; CALL eval_local(base(1),base(2),base(3),base(4),par,Lp)
    base=uvec; base(1)=uvec(1)-dz; CALL eval_local(base(1),base(2),base(3),base(4),par,Lm)
    par(60)=((Lp%S_i-1D0)-(Lm%S_i-1D0))/(2D0*dz)
    par(61)=(Lp%Rad-Lm%Rad)/(2D0*dz)
    base=uvec; base(1)=uvec(1)+dz; CALL rhs_full(base,par,Fp)
    base=uvec; base(1)=uvec(1)-dz; CALL rhs_full(base,par,Fm)
    z_force_slope=(Fp(3)-Fm(3))/(2D0*dz)
    z_growth_slope=(Fp(4)-Fm(4))/(2D0*dz)
    par(62)=par(60)+par(61)
    par(63)=L%Rad; par(64)=par(3)*L%Rad; par(65)=L%driving_factor; par(66)=L%m_dot
    par(67)=L%k; par(68)=L%Re; par(69)=L%C_D; par(70)=L%f_v; par(71)=L%Sc
    par(72)=L%T_a; par(73)=L%p_a; par(74)=L%p_v; par(75)=L%S_i; par(76)=L%H_l
    par(77)=L%eta; par(78)=L%eta_a; par(79)=L%W_a; par(80)=L%U_a; par(81)=L%rho_a
    par(82)=L%V; par(83)=L%a; par(84)=L%c; par(85)=L%Area; par(86)=L%D_i; par(87)=L%r_i
    par(88)=L%Cap; par(89)=L%psi; par(90)=L%rho_ie; par(91)=L%vertical_force; par(92)=L%driving_factor
    dmuse=MAX(ABS(uvec(4))*1D-4,1D-14); base=uvec; base(4)=uvec(4)+dmuse; CALL rhs_full(base,par,Fp)
    base=uvec; base(4)=MAX(uvec(4)-dmuse,1D-30); CALL rhs_full(base,par,Fm)
    m_force_slope=(Fp(3)-Fm(3))/(2D0*dmuse)
    m_growth_slope=(Fp(4)-Fm(4))/(2D0*dmuse)
    par(93)=m_force_slope
    par(94)=m_growth_slope
    par(95)=z_force_slope*m_growth_slope - m_force_slope*z_growth_slope
  END SUBROUTINE set_pvls
END MODULE berton_full_model

SUBROUTINE FUNC(NDIM,U,ICP,PAR,IJAC,F,DFDU,DFDP)
  USE berton_full_model
  IMPLICIT NONE
  INTEGER, INTENT(IN) :: NDIM,IJAC,ICP(*)
  DOUBLE PRECISION, INTENT(IN) :: U(NDIM),PAR(*)
  DOUBLE PRECISION, INTENT(OUT) :: F(NDIM)
  DOUBLE PRECISION, INTENT(INOUT) :: DFDU(NDIM,NDIM),DFDP(NDIM,*)
  DOUBLE PRECISION :: uu(4),ff(4),up(4),um(4),fp(4),fm(4),h,steps(4)
  INTEGER :: j
  uu(1:4)=U(1:4); CALL rhs_full(uu,PAR,ff); F(1:4)=ff(1:4)
  IF (IJAC .NE. 0) THEN
    DFDU(1:NDIM,1:NDIM)=0D0
    steps=(/1D0,1D-5,1D-5,MAX(ABS(uu(4))*1D-4,1D-14)/)
    DO j=1,4
      h=steps(j); up=uu; um=uu; up(j)=up(j)+h; um(j)=um(j)-h
      IF (j .EQ. 4 .AND. um(j) <= 0D0) um(j)=uu(j)*(1D0-1D-4)
      CALL rhs_full(up,PAR,fp); CALL rhs_full(um,PAR,fm)
      DFDU(1:4,j)=(fp(1:4)-fm(1:4))/(up(j)-um(j))
    END DO
  END IF
END SUBROUTINE FUNC

SUBROUTINE STPNT(NDIM,U,PAR,T)
  USE berton_full_model
  IMPLICIT NONE
  INTEGER, INTENT(IN) :: NDIM
  DOUBLE PRECISION, INTENT(INOUT) :: U(NDIM),PAR(*)
  DOUBLE PRECISION, INTENT(IN) :: T
  CALL init_defaults(PAR)
  ! Python steady solve at z_W0=10000 m, Case 0, include_coriolis=0.
  U(1)=1.017850407189D4
  U(2)=horizontal_wind(U(1),PAR)
  U(3)=0D0
  U(4)=1.057007179452D-9
END SUBROUTINE STPNT

SUBROUTINE BCND(NDIM,PAR,ICP,NBC,U0,U1,FB,IJAC,DBC)
  IMPLICIT NONE
  INTEGER, INTENT(IN) :: NDIM,ICP(*),NBC,IJAC
  DOUBLE PRECISION, INTENT(IN) :: PAR(*),U0(NDIM),U1(NDIM)
  DOUBLE PRECISION, INTENT(OUT) :: FB(NBC)
  DOUBLE PRECISION, INTENT(INOUT) :: DBC(NBC,*)
END SUBROUTINE BCND

SUBROUTINE ICND(NDIM,PAR,ICP,NINT,U,UOLD,UDOT,UPOLD,FI,IJAC,DINT)
  IMPLICIT NONE
  INTEGER, INTENT(IN) :: NDIM,ICP(*),NINT,IJAC
  DOUBLE PRECISION, INTENT(IN) :: PAR(*),U(NDIM),UOLD(NDIM),UDOT(NDIM),UPOLD(NDIM)
  DOUBLE PRECISION, INTENT(OUT) :: FI(NINT)
  DOUBLE PRECISION, INTENT(INOUT) :: DINT(NINT,*)
END SUBROUTINE ICND

SUBROUTINE FOPT(NDIM,U,ICP,PAR,IJAC,FS,DFDU,DFDP)
  IMPLICIT NONE
  INTEGER, INTENT(IN) :: NDIM,ICP(*),IJAC
  DOUBLE PRECISION, INTENT(IN) :: U(NDIM),PAR(*)
  DOUBLE PRECISION, INTENT(OUT) :: FS
  DOUBLE PRECISION, INTENT(INOUT) :: DFDU(NDIM),DFDP(*)
END SUBROUTINE FOPT

SUBROUTINE PVLS(NDIM,U,PAR)
  USE berton_full_model
  IMPLICIT NONE
  INTEGER, INTENT(IN) :: NDIM
  DOUBLE PRECISION, INTENT(IN) :: U(NDIM)
  DOUBLE PRECISION, INTENT(INOUT) :: PAR(*)
  DOUBLE PRECISION :: uu(4)
  uu(1:4)=U(1:4); CALL set_pvls(uu,PAR)
END SUBROUTINE PVLS
