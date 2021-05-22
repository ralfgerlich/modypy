"""
A collection of blocks useful for aerodynamics.
"""
import math

import numpy as np

from modypy.model import Block, Port, signal_method


class Propeller(Block):
    """A block representing a propeller.

    The block has two inputs:

    ``speed_rps``
        The speed of the propeller in revolutions per second
    ``density``
        The density of the air

    It provides three outputs:

    ``thrust``
        The total scalar thrust generated by the propeller
    ``torque``
        The total torque required by the propeller
    ``power``
        The total power required by the propeller

    The magnitudes of thrust, torque and power are determined by the following
    formulae::

        F = ct(n)*rho*D^5*n^2
        tau = cp(n)/(2*pi)*rho*D^5*n^2
        P = cp(n)*rho*D^5*n^3

    Here,
        - ``ct(n)`` is the thrust coefficient at speed ``n``,
        - ``cp(n)`` is the power coefficient at speed ``n``, and
        - ``D`` is the diameter.
    """

    def __init__(self,
                 parent,
                 thrust_coefficient,
                 power_coefficient,
                 diameter):
        Block.__init__(self, parent)
        if not callable(thrust_coefficient):
            thrust_coeff_value = thrust_coefficient
            thrust_coefficient = (lambda n: thrust_coeff_value)
        if not callable(power_coefficient):
            power_coeff_value = power_coefficient
            power_coefficient = (lambda n: power_coeff_value)

        self.thrust_coefficient = thrust_coefficient
        self.power_coefficient = power_coefficient
        self.diameter = diameter

        self.speed_rps = Port(shape=1)
        self.density = Port(shape=1)

    @signal_method
    def thrust(self, data):
        """Function used to calculate the ``thrust`` output
        """
        speed_rps = self.speed_rps(data)
        density = self.density(data)
        return self.thrust_coefficient(speed_rps) \
            * density * self.diameter ** 4 * speed_rps ** 2

    @signal_method
    def torque(self, data):
        """Function used to calculate the ``torque`` output
        """
        speed_rps = self.speed_rps(data)
        density = self.density(data)
        return self.power_coefficient(speed_rps) / (2 * math.pi) * \
            density * self.diameter ** 5 * speed_rps ** 2

    @signal_method
    def power(self, data):
        """Function used to calculate the ``power`` output
        """
        speed_rps = self.speed_rps(data)
        density = self.density(data)
        return self.power_coefficient(speed_rps) * \
            density * self.diameter ** 5 * np.abs(speed_rps ** 3)


class Thruster(Block):
    """A block representing a thruster.

    A thruster converts scalar thrust and torque to thrust and torque vectors.
    The thrust is considered to work in a (constant) thrust direction,
    determined by the thrust axis.

    Torque is combined thrust along the thrust axis and torque due to the thrust
    working at the end of a (constant) arm relative to the center of gravity
    (CoG) of a rigid body.

    The block has two inputs:
        - The scalar thrust in the direction of the thrust axis, and
        - the scalar torque along the thrust axis.

    The block has six outputs:
        - The thrust vector (3 components), and
        - the torque vector (3 components).

    It is configured by
        - the thrust axis (vector X,Y,Z),
        - the thrust arm (vector X,Y,Z), and
        - the turning direction (scalar: +1 or -1).

    The right-hand rule applied to the thrust axis gives the positive direction
    of the thruster. Torque acts in the *opposite* direction, i.e. if the
    thruster turns clockwise, torque acts counter-clockwise.
    """

    def __init__(self,
                 parent,
                 vector,
                 arm,
                 direction=1):
        Block.__init__(self, parent)
        self.vector = vector
        self.arm = arm
        self.direction = direction

        self.scalar_thrust = Port(shape=1)
        self.scalar_torque = Port(shape=1)

    @signal_method(shape=3)
    def thrust_vector(self, data):
        """Function used to calculate the ``thrust_vector`` output
        """
        thrust = self.scalar_thrust(data)
        thrust_vector = self.vector * thrust
        return thrust_vector

    @signal_method(shape=3)
    def torque_vector(self, data):
        """Function used to calculate the ``torque_vector`` output
        """
        thrust = self.scalar_thrust(data)
        torque = self.scalar_torque(data)

        thrust_vector = self.vector * thrust
        torque_vector = self.direction * self.vector * torque + \
            np.cross(self.arm, thrust_vector)

        return torque_vector
