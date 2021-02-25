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
from typing import Dict, Optional, Tuple, List

import logs
from canteen import Canteen



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
                  arrival : int,
                  speed : int,
                  hungry : int
                  ) -> None:
        """
        Initialize.

        :param env: The simulation environment
        :param canteen: The canteen where the customer goes.
        :param arrival: When the customer arrives to the canteen.
        :param speed: An index that indicate how fast is the customer in the operations
                    such as self-service and paying.
        :param hungry: An index that says how much hungry is the customers.

        :attr exit: When the customer exists the canteen.
        :attr history: All the events and relative timestamps that concern the
                        customer.

        """
        self.env = env
        self.canteen = canteen
        self.speed = speed
        self.hungry = hungry

        self.arrival = arrival
        self.exit : Optional[int] = None

        self.history : List[logs.Event] = [logs.Event(arrival, "Arrive")]
