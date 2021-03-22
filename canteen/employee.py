from __future__ import annotations
# This file contains all the employees class. The employees are the people
# that work in the canteen.
# They carry out many taks such as serving food at some stations, refilling
# the self service station, and working and the cash point.
#
# Designed and developed by Mattia Neroni in March 2021.
# Author contact: mattianeroni@yahoo.it

import simpy
import math
from typing import Tuple



def source (experiences : Tuple[int,...], env : simpy.Environment) -> Tuple[Employee,...]:
    """
    This method allows a faster generation of the employees who work in the canteen.

    :param experiences: The experience level (a value between 1 and 3) of each employee.
    :param env: The simulation environment.

    :return: The set of employee.

    """
    return tuple(Employee(env, e, 100) for e in experiences)




class Employee (simpy.PriorityResource):
    """
    An instance of this class represents an employee of the canteen.
    The employees are essential for the functioning of the canteen. The serve the
    customers at some stations, prepare food at other station, take care of the
    cash point, and refill the self service station of food or cutlery.

    They are characterised by a certain experience or skill level, and a certain
    energy that decrease as the working time increase and the operations carried
    out grow up.

    (Concerning the energy decrease, a specific function per each employee could
    be eventually defined. Currently, a single function is used.)

    """

    def __init__ (self,
                  env : simpy.Environment,
                  experience : int,
                  energy : int
                  ) -> None:
        """
        Initilaize.

        :param env: The simulation environment.
        :param experience: The experience and skill-level of the employee.
        :param energy: The energy, which decrases with the working time and the
                        operations carried out.

        """
        self.env = env
        self.experience = experience
        self.energy = energy

        super(Employee, self).__init__(env, capacity=1)


    @property
    def energy_penalty (self) -> float:
        """
        The time penalty applied to the operations carried out by this employee
        because of his/her current energy.

        """
        return math.log(101.0 - self.energy) * 0.05


    @property
    def experience_penalty (self) -> float:
        """
        The time penalty applied to the operations carried out by this employee
        because of his/her current experience.
        """
        return 0.2 - (self.experience - 1)*0.2
