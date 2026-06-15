!----------------------------------------------------------------------
! Reduced Berton 3D fixed-point model for AUTO-07p validation.
!
! State variables:
!   U(1) = zeta [m]        altitude coordinate near zeta_star
!   U(2) = v    [m/s]      vertical velocity perturbation state
!   U(3) = r    [m]        ice crystal radius
!
! Continuation parameters:
!   PAR(1) = k              drag relaxation rate [s^-1]
!   PAR(2) = alpha_grad     multiplier on sigma_S + R_zeta [-]
!   PAR(3) = zeta_star      baseline fixed-point altitude [m]
!   PAR(4) = r_star         baseline fixed-point radius [m]
!   PAR(5) = beta           fall-speed coefficient in V_f=beta*r^2 [m^-1 s^-1]
!   PAR(6) = G              growth diffusivity in dr/dt=(G/r)*drive [m^2 s^-1]
!   PAR(7) = w_prime        -dW_a/dz at fixed point [s^-1]
!   PAR(8) = R_r            radiative derivative dR/dr [m^-1]
!   PAR(9) = sigma_plus_Rz  sigma_S + R_zeta [m^-1]
!
! Output-only diagnostic parameters set in PVLS:
!   PAR(10) = c             (G/r_star)*R_r [s^-1]
!   PAR(11) = d             (G/r_star)*alpha_grad*sigma_plus_Rz [s^-1 m^-1]
!   PAR(12) = a0            corrected cubic constant term [s^-3]
!   PAR(13) = rh_residual   a2*a1-a0; zero at Hopf [s^-3]
!   PAR(14) = hopf_alpha    analytic alpha_grad at the RH Hopf locus [-]
!
! The ODE is the audited local reduced model, represented by first-order local
! Berton ingredients rather than by multiplying by the Jacobian directly:
!
!   zeta_dot = v
!   v_dot    = -k * (v - (W_a(zeta)-V_f(r)))
!   r_dot    = (G/r) * (s(zeta)-R(zeta,r))
!
! with
!   W_a - V_f ~= -w_prime*(zeta-zeta*) - 2*beta*r_star*(r-r*)
!   s - R     ~= -alpha_grad*(sigma_S+R_zeta)*(zeta-zeta*) - R_r*(r-r*)
!----------------------------------------------------------------------

SUBROUTINE FUNC(NDIM,U,ICP,PAR,IJAC,F,DFDU,DFDP)
  IMPLICIT NONE
  INTEGER, INTENT(IN) :: NDIM, IJAC, ICP(*)
  DOUBLE PRECISION, INTENT(IN) :: U(NDIM), PAR(*)
  DOUBLE PRECISION, INTENT(OUT) :: F(NDIM)
  DOUBLE PRECISION, INTENT(INOUT) :: DFDU(NDIM,NDIM),DFDP(NDIM,*)

  DOUBLE PRECISION :: zeta, v, r, k, alpha_grad, zeta_star, r_star
  DOUBLE PRECISION :: beta, G, w_prime, R_r, sigma_plus_Rz
  DOUBLE PRECISION :: dz, dr, w_minus_vfall, drive

  zeta = U(1)
  v = U(2)
  r = U(3)

  k = PAR(1)
  alpha_grad = PAR(2)
  zeta_star = PAR(3)
  r_star = PAR(4)
  beta = PAR(5)
  G = PAR(6)
  w_prime = PAR(7)
  R_r = PAR(8)
  sigma_plus_Rz = PAR(9)

  dz = zeta - zeta_star
  dr = r - r_star
  w_minus_vfall = -w_prime*dz - 2.0D0*beta*r_star*dr
  drive = -alpha_grad*sigma_plus_Rz*dz - R_r*dr

  F(1) = v
  F(2) = -k*(v - w_minus_vfall)
  F(3) = (G/r)*drive

  IF (IJAC .NE. 0) THEN
    DFDU(1:NDIM,1:NDIM) = 0.0D0
    DFDU(1,2) = 1.0D0
    DFDU(2,1) = -k*w_prime
    DFDU(2,2) = -k
    DFDU(2,3) = -2.0D0*k*beta*r_star
    DFDU(3,1) = -(G/r)*alpha_grad*sigma_plus_Rz
    DFDU(3,3) = -(G/r)*R_r - (G/(r*r))*drive
  END IF

END SUBROUTINE FUNC

SUBROUTINE STPNT(NDIM,U,PAR,T)
  IMPLICIT NONE
  INTEGER, INTENT(IN) :: NDIM
  DOUBLE PRECISION, INTENT(INOUT) :: U(NDIM),PAR(*)
  DOUBLE PRECISION, INTENT(IN) :: T

  PAR(1) = 2.164883811499D1       ! k from LocalDiagnostics [s^-1]
  PAR(2) = 1.0D0                  ! baseline gradient multiplier
  PAR(3) = 9.618062976835217D3    ! zeta_star [m]
  PAR(4) = 6.55D-5                ! r_star [m]
  PAR(5) = 1.398519899773D8       ! beta [m^-1 s^-1]
  PAR(6) = 3.568753045458D-12     ! G [m^2 s^-1]
  PAR(7) = 0.0D0                  ! w_prime [s^-1] (updraft derivative vanishes here)
  PAR(8) = 3.369976459537D1       ! R_r [m^-1]
  PAR(9) = -5.640219674712D-5     ! sigma_S + R_zeta [m^-1]

  U(1) = PAR(3)
  U(2) = 0.0D0
  U(3) = PAR(4)
END SUBROUTINE STPNT

SUBROUTINE BCND(NDIM,PAR,ICP,NBC,U0,U1,FB,IJAC,DBC)
  IMPLICIT NONE
  INTEGER, INTENT(IN) :: NDIM, ICP(*), NBC, IJAC
  DOUBLE PRECISION, INTENT(IN) :: PAR(*), U0(NDIM), U1(NDIM)
  DOUBLE PRECISION, INTENT(OUT) :: FB(NBC)
  DOUBLE PRECISION, INTENT(INOUT) :: DBC(NBC,*)
END SUBROUTINE BCND

SUBROUTINE ICND(NDIM,PAR,ICP,NINT,U,UOLD,UDOT,UPOLD,FI,IJAC,DINT)
  IMPLICIT NONE
  INTEGER, INTENT(IN) :: NDIM, ICP(*), NINT, IJAC
  DOUBLE PRECISION, INTENT(IN) :: PAR(*)
  DOUBLE PRECISION, INTENT(IN) :: U(NDIM), UOLD(NDIM), UDOT(NDIM), UPOLD(NDIM)
  DOUBLE PRECISION, INTENT(OUT) :: FI(NINT)
  DOUBLE PRECISION, INTENT(INOUT) :: DINT(NINT,*)
END SUBROUTINE ICND

SUBROUTINE FOPT(NDIM,U,ICP,PAR,IJAC,FS,DFDU,DFDP)
  IMPLICIT NONE
  INTEGER, INTENT(IN) :: NDIM, ICP(*), IJAC
  DOUBLE PRECISION, INTENT(IN) :: U(NDIM), PAR(*)
  DOUBLE PRECISION, INTENT(OUT) :: FS
  DOUBLE PRECISION, INTENT(INOUT) :: DFDU(NDIM),DFDP(*)
END SUBROUTINE FOPT

SUBROUTINE PVLS(NDIM,U,PAR)
  IMPLICIT NONE
  INTEGER, INTENT(IN) :: NDIM
  DOUBLE PRECISION, INTENT(IN) :: U(NDIM)
  DOUBLE PRECISION, INTENT(INOUT) :: PAR(*)

  DOUBLE PRECISION :: k, alpha_grad, r_star, beta, G, w_prime, R_r, sigma_plus_Rz
  DOUBLE PRECISION :: B, a, bcoef, c, d, a0, a1, a2, positive_part

  k = PAR(1)
  alpha_grad = PAR(2)
  r_star = PAR(4)
  beta = PAR(5)
  G = PAR(6)
  w_prime = PAR(7)
  R_r = PAR(8)
  sigma_plus_Rz = PAR(9)

  B = 2.0D0*beta*r_star
  a = k*w_prime
  bcoef = k*B
  c = (G/r_star)*R_r
  d = (G/r_star)*alpha_grad*sigma_plus_Rz
  a2 = k + c
  a1 = k*c + a
  a0 = a*c - bcoef*d

  PAR(10) = c
  PAR(11) = d
  PAR(12) = a0
  PAR(13) = a2*a1 - a0

  positive_part = k*(k*c + a + c*c)
  IF (ABS(bcoef*(G/r_star)*sigma_plus_Rz) .GT. 0.0D0) THEN
    PAR(14) = -positive_part/(bcoef*(G/r_star)*sigma_plus_Rz)
  ELSE
    PAR(14) = 0.0D0
  END IF
END SUBROUTINE PVLS
