from __future__ import annotations
# This file contains the customers that visit the canteen.
# Each customer has of course a different arrival time.
# The arrival of customers could also be more frequent in some busy hours, and
# less frequent in th most quite times.
# Customers have also a indicator of how much they are hungry, as well as an
# index that define their speed.
#
# Designed and developed by Mattia Neroni in March 2021.
# Author contact: mattianeroni@yahoo.it


import simpy
import random
from typing import Optional, Tuple, List, Callable

import logs
#from canteen import Canteen


# These are the possible menus the customers select from depending on
# on how much they are hungry.
# The sequences can be read in the following way:
#        (starter, pizza, first, second, side, sweet, drink)
_menu = {
    0 : ((1,0,0,0,0,0,1), (0,0,0,0,1,0,1)),
    1 : ((0,0,1,0,0,0,1), (0,0,0,1,0,0,1)),
    2 : ((1,0,1,0,0,0,1), (1,0,0,1,0,0,1), (0,1,0,0,0,0,1), (0,0,0,1,1,0,1), (0,0,1,0,1,0,1)),
    3 : ((0,1,0,0,0,0,1), (0,1,0,0,0,1,1), (0,0,1,1,0,0,1), (0,1,0,0,1,0,1), (1,0,1,0,0,1,1), (1,0,0,1,1,0,1)),
    4 : ((0,1,0,0,1,0,1), (0,1,0,0,0,1,1), (0,0,1,1,1,0,1), (0,0,1,1,0,1,1), (1,0,1,0,1,0,1), (1,0,1,0,1,1,1)),
    5 : ((0,1,0,0,1,1,1), (1,1,0,0,0,1,1), (1,0,1,1,1,0,1), (1,0,1,1,1,1,1))
}




# This function is supposed to be the most appropriate for the canteen considered
# and for many others. It is a sort of parabolic function, where the interarrival
# is initially high, then decreases during the busy hours, and then increases again.
# The user is obviusly allowed to implement its own function to provide to the source.
arrivalFunction = lambda x: 0.0005 * (150.0 - x)**2 + 0.4






def source (arrivalFunction : Callable[[float], float],
            maxtime : float,
            env : simpy.Environment,
            canteen : Canteen

            ) -> Tuple[Customer,...]:
    """
    This method generates the customers.
    The callable arrivalFunction defines how the interarrivals change during the
    simulation. This aspect offers a great flexibility and allows the simulation
    of constant arrivals as well as busiest moments.

    :param arrivalFunction: The function that describes the interarrivals.
    :param maxtime: The duration of the simulation.
    :param env: The simulation environment.
    :param canteen: The canteen.

    :return: The set of customers that are going to enter the canteen.

    """
    customers = list()
    arrival = 0.0
    while arrival < maxtime:
        hungry = random.randint (0, 5)
        menu = random.choice (_menu[hungry])
        speed = random.randint (0, 10)
        customers.append(Customer(env, canteen, arrival, speed, hungry, menu))

        # Consider using += expovariate(1/arrivalFunction(arrival))
        # for a major variability and a more stochastic behaviour
        arrival += arrivalFunction(arrival)

    return tuple(customers)



class Customer (object):
    """
    An instance of this class represents a customer.

    Each customer has (i) an index of speed and (ii) an index of hungriness.
        (i) The index of speed say how much fast is the customer in the
            stochastic operations, such as paying or taking food from self
            service stations;
        (ii)The hungriness index says how much the customer wants to eat.
            The canteen would serve starters, pizza, fisrt dishes, second dishes,
            side dishes, drinks, and desserts. Each of these is served in a
            different station.
            The hungier is the customer the higher is the number of stations he/she
            will visit.

    He/She also keeps track of the moment when he arrives to the canteen, and the
    moment when, after paying, he exits and go to seat for eating.

    He/She also keeps track of all his/her history, in other words the timestamps
    for all the events that concerned the customer during the period into the canteen.

    """

    def __init__ (self,
                  env : simpy.Environment,
                  canteen : Canteen,
                  arrival : float,
                  speed : int,
                  hungry : int,
                  menu : Tuple[int,...]
                  ) -> None:
        """
        Initialize.

        :param env: The simulation environment
        :param canteen: The canteen where the customer goes.
        :param arrival: When the customer arrives to the canteen.
        :param speed: An index that indicate how fast is the customer in the operations
                    such as self-service and paying.
        :param hungry: An index that says how much hungry is the customers.
        :param menu: The menu the customer will choose.

        :attr exit: When the customer exists the canteen.
        :attr history: All the events and relative timestamps that concern the
                        customer.

        """
        self.env = env
        self.canteen = canteen
        self.speed = speed
        self.hungry = hungry
        self.menu = menu

        self.arrival = arrival
        self.exit : Optional[float] = None

        self.history : List[logs.Event] = [logs.Event(arrival, "Arrive")]


    @property
    def speed_penalty (self) -> float:
        """
        The time penalty applied to the operations carried out by this customer
        according to his/her speed.

        """
        return 0.3 - self.speed * 0.06
