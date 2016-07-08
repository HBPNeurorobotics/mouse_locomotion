# coding=utf-8
##
# Mouse Locomotion Simulation
#
# Human Brain Project SP10
#
# This project provides the user with a framework based on 3D simulators allowing:
#  - Edition of a 3D model
#  - Edition of a physical controller model (torque-based or muscle-based)
#  - Edition of a brain controller model (oscillator-based or neural network-based)
#  - Simulation of the model
#  - Optimization and Meta-optimization of the parameters in distributed cloud simulations
#
# File created by: Gabriel Urbain <gabriel.urbain@ugent.be>
#                  Dimitri Rodarie <d.rodarie@gmail.com>
# February 2016
##

import math
from muscles import Muscle


class HillMuscle(Muscle):
    """
    This class implements Hill Model for muscle force
    """

    def __init__(self, params_, simulator):
        """
        Class initialization. Parameters can be found in D.F.B. Haeufle, M. Günther, A. Bayer, S. Schmitt (2014) \
        Hill-type muscle model with serial damping and eccentric force-velocity relation. Journal of Biomechanics
        :param params_: Dictionary containing parameter for the muscle
        :param simulator: SimulatorUtils class to access utility functions
        """

        Muscle.__init__(self, params_, simulator)

        # Contractile Element (CE)
        self.CE_F_max = 1420  # F_max in [N] for Extensor (Kistemaker et al., 2006)
        self.CE_l_CEopt = 0.092  # optimal length of CE in [m] for Extensor (Kistemaker et al., 2006)
        self.CE_DeltaW_limb_des = 0.35  # width of normalized bell curve in descending branch (Moerl et al., 2012)
        self.CE_DeltaW_limb_asc = 0.35  # width of normalized bell curve in ascending branch (Moerl et al., 2012)
        self.CE_v_CElimb_des = 1.5  # exponent for descending branch (Moerl et al., 2012)
        self.CE_v_CElimb_asc = 3.0  # exponent for ascending branch (Moerl et al., 2012)
        self.CE_A_rel0 = 0.25  # parameter for contraction dynamics: maximum value of A_rel (Guenther, 1997, S. 82)
        self.CE_B_rel0 = 2.25  # parameter for contraction dynmacis: maximum value of B_rel (Guenther, 1997, S. 82)
        # eccentric force-velocity relation:
        self.CE_S_eccentric = 2  # relation between F(v) slopes at v_CE=0 (van Soest & Bobbert, 1993)
        self.CE_F_eccentric = 1.5  # factor by which the force can exceed F_isom for large eccentric velocities (van Soest & Bobbert, 1993)

        # Parallel Elastic Element (PEE)
        self.PEE_L_PEE0 = 0.9  # rest length of PEE normalized to optimal lenght of CE (Guenther et al., 2007)
        self.PEE_l_PEE0 = self.PEE_L_PEE0 * self.CE_l_CEopt  # rest length of PEE (Guenther et al., 2007)
        self.PEE_v_PEE = 2.5  # exponent of F_PEE (Moerl et al., 2012)
        self.PEE_F_PEE = 2.0  # force of PEE if l_CE is stretched to deltaWlimb_des (Moerl et al., 2012)
        self.PEE_K_PEE = self.PEE_F_PEE * (
            self.CE_F_max / (self.CE_l_CEopt * (self.CE_DeltaW_limb_des + 1 - self.PEE_L_PEE0)) ** self.PEE_v_PEE)
        # factor of non-linearity in F_PEE (Guenther et al., 2007)

        # Serial Damping Element (SDE)
        self.SDE_D_SE = 0.3  # xxx dimensionless factor to scale d_SEmax (Moerl et al., 2012)
        self.SDE_R_SE = 0.01  # minimum value of d_SE normalised to d_SEmax (Moerl et al., 2012)
        self.SDE_d_SEmax = self.SDE_D_SE * (self.CE_F_max * self.CE_A_rel0) / (self.CE_l_CEopt * self.CE_B_rel0)
        # maximum value in d_SE in [Ns/m] (Moerl et al., 2012)

        # Serial Elastic Element (SEE)
        self.SEE_l_SEE0 = 0.172  # rest length of SEE in [m] (Kistemaker et al., 2006)
        self.SEE_DeltaU_SEEnll = 0.0425  # relativ stretch at non-linear linear transition (Moerl et al., 2012)
        self.SEE_DeltaU_SEEl = 0.017  # relativ additional stretch in the linear part providing a force increase of deltaF_SEE0 (Moerl, 2012)
        self.SEE_DeltaF_SEE0 = 568  # both force at the transition and force increase in the linear part in [N] (~ 40# of the maximal isometric muscle force)

        self.SEE_l_SEEnll = (1 + self.SEE_DeltaU_SEEnll) * self.SEE_l_SEE0
        self.SEE_v_SEE = self.SEE_DeltaU_SEEnll / self.SEE_DeltaU_SEEl
        self.SEE_KSEEnl = self.SEE_DeltaF_SEE0 / (self.SEE_DeltaU_SEEnll * self.SEE_l_SEE0) ** self.SEE_v_SEE
        self.SEE_KSEEl = self.SEE_DeltaF_SEE0 / (self.SEE_DeltaU_SEEl * self.SEE_l_SEE0)

    def update(self, **kwargs):
        """
        Computations are based on D.F.B. Haeufle, M. Günther, A. Bayer, S. Schmitt (2014) \
        Hill-type muscle model with serial damping and eccentric force-velocity relation. Journal of Biomechanics
        :param kwargs: Dictionary containing muscle updates
        """

        if "l_CE" in kwargs:
            l_CE = kwargs["l_CE"]
        else:
            self.logger.error("Muscle " + self.name + " deactivated: l_CE isn't defined." +
                              " Check your configuration file!")
            self.active = False
            l_CE = 0

        if "l_MTC" in kwargs:
            l_MTC = kwargs["l_MTC"]
        else:
            self.logger.error("Muscle " + self.name + " deactivated: l_MTC isn't defined." +
                              " Check your configuration file!")
            self.active = False
            l_MTC = 0

        if "dot_l_MTC" in kwargs:
            dot_l_MTC = kwargs["dot_l_MTC"]
        else:
            self.logger.error("Muscle " + self.name + " deactivated: dot_l_MTC isn't defined." +
                              " Check your configuration file!")
            self.active = False
            dot_l_MTC = 0

        if "q" in kwargs:
            q = kwargs["q"]
        else:
            self.logger.error("Muscle " + self.name + " deactivated: q isn't defined." +
                              " Check your configuration file!")
            self.active = False
            q = 0

        if self.active:
            # Isometric force (Force length relation)
            if l_CE >= self.CE_l_CEopt:  # descending branch
                F_isom = math.exp(
                    -(abs(((l_CE / self.CE_l_CEopt) - 1) / self.CE_DeltaW_limb_des)) ** self.CE_v_CElimb_des)
            else:  # ascending branch
                F_isom = math.exp(
                    -(abs(((l_CE / self.CE_l_CEopt) - 1) / self.CE_DeltaW_limb_asc)) ** self.CE_v_CElimb_asc)

            # Force of the parallel elastic element PEE
            if l_CE >= self.PEE_l_PEE0:
                F_PEE = self.PEE_K_PEE * (l_CE - self.PEE_l_PEE0) ** self.PEE_v_PEE
            else:  # shorter than slack length
                F_PEE = 0

            # Force of the serial elastic element SEE
            l_SEE = abs(l_MTC - l_CE)  # SEE length
            if (l_SEE > self.SEE_l_SEE0) and (l_SEE < self.SEE_l_SEEnll):  # non-linear part
                F_SEE = self.SEE_KSEEnl * ((l_SEE - self.SEE_l_SEE0) ** self.SEE_v_SEE)
            elif l_SEE >= self.SEE_l_SEEnll:  # linear part
                F_SEE = self.SEE_DeltaF_SEE0 + self.SEE_KSEEl * (l_SEE - self.SEE_l_SEEnll)
            else:  # salck length
                F_SEE = 0

            # Hill Parameters concentric contraction
            if l_CE < self.CE_l_CEopt:
                A_rel = 1
            else:
                A_rel = F_isom

            A_rel = A_rel * self.CE_A_rel0 * 1 / 4 * (1 + 3 * q)
            B_rel = self.CE_B_rel0 * 1 * 1 / 7 * (3 + 4 * q)

            # calculate CE contraction velocity
            D0 = self.CE_l_CEopt * B_rel * self.SDE_d_SEmax * (
                self.SDE_R_SE + (1 - self.SDE_R_SE) * (q * F_isom + F_PEE / self.CE_F_max))
            C2 = self.SDE_d_SEmax * (self.SDE_R_SE - (A_rel - F_PEE / self.CE_F_max) * (1 - self.SDE_R_SE))
            C1 = - C2 * dot_l_MTC - D0 - F_SEE + F_PEE - self.CE_F_max * A_rel
            C0 = D0 * dot_l_MTC + self.CE_l_CEopt * B_rel * (F_SEE - F_PEE - self.CE_F_max * q * F_isom)

            # solve the quadratic equation
            if (C1 ** 2 - 4 * C2 * C0) < 0:
                dot_l_CE = 0
            # warning('the quadratic equation in the muscle model would result in a complex solution to compensate, the CE contraction velocity was set to zero')
            else:
                dot_l_CE = (- C1 - math.sqrt(C1 ** 2 - 4 * C2 * C0)) / (2 * C2)

            # in case of an eccentric contraction:
            if dot_l_CE > 0:
                # calculate new Hill-parameters (asymptotes of the hyperbola)
                B_rel = (q * F_isom * (1 - self.CE_F_eccentric) / (q * F_isom + A_rel) * B_rel / self.CE_S_eccentric)
                A_rel = - self.CE_F_eccentric * q * F_isom

                # calculate CE eccentric velocity
                D0 = self.CE_l_CEopt * B_rel * self.SDE_d_SEmax * (
                    self.SDE_R_SE + (1 - self.SDE_R_SE) * (q * F_isom + F_PEE / self.CE_F_max))
                C2 = self.SDE_d_SEmax * (self.SDE_R_SE - (A_rel - F_PEE / self.CE_F_max) * (1 - self.SDE_R_SE))
                C1 = - C2 * dot_l_MTC - D0 - F_SEE + F_PEE - self.CE_F_max * A_rel
                C0 = D0 * dot_l_MTC + self.CE_l_CEopt * B_rel * (F_SEE - F_PEE - self.CE_F_max * q * F_isom)

                # solve the quadratic equation
                if (C1 ** 2 - 4 * C2 * C0) < 0:
                    dot_l_CE = 0
                # warning('the quadratic equation in the muscle model would result in a complex solution to compensate, the CE contraction velocity was set to zero')
                else:
                    dot_l_CE = (- C1 + math.sqrt(C1 ** 2 - 4 * C2 * C0)) / (
                        2 * C2)  # note that here +sqrt gives the correct solution

            # Contractile element force
            F_CE = self.CE_F_max * (((q * F_isom + A_rel) / (1 - dot_l_CE / (self.CE_l_CEopt * B_rel))) - A_rel)

            # Force of the serial damping element
            F_SDE = self.SDE_d_SEmax * ((1 - self.SDE_R_SE) * ((F_CE + F_PEE) / self.CE_F_max) + self.SDE_R_SE) * (
                dot_l_MTC - dot_l_CE)
            F_MTC = F_SEE + F_SDE

            return F_MTC
