from __future__ import annotations

import simpy

from employee import Employee
from station import MultiStore
from typing import Tuple


class Canteen (simpy.Resource):
    """
    This class represents the canteen and it could represent
    any self service restaurant.
    It is handled as a resource, because it has a limited capacity
    and when this capacity is reached, people stay outside.

    Its capacity can be saturated by all people waiting for any meal.

    """

    def __init__ (self,
                  env : simpy.Environment,
                  employees : Tuple[Employee],
                  stations : Tuple[MultiStore],
                  opening_time : int = 3000,
                  capacity : int = 100

                  ) -> None:
        """
        Initialize.

        :param env: The simulation environment.

        :param opening_time: The time [minutes] that the canteen stays open.
        :param capacity: The maximum number of customers it can host.

        """
        self.opening_time = opening_time
        super(Canteen, self).__init__(env, capacity)
