from __future__ import annotations

import simpy
import random

from employee import Employee
from station import MultiStore
from customer import Customer
from station import ServiceStation, SelfServiceStation, Cash

from typing import Tuple, Generator, Union, cast



def simulation (env : simpy.Environment, canteen : Canteen, customers : Tuple[Customer,...]) -> Generator[simpy.Event, None, None]:
    """
    This is the simulation.

    """
    for customer in customers:
        if customer.arrival > env.now:
            yield env.timeout (customer.arrival - env.now)
        env.process (service(env, canteen, customer))




def service (env : simpy.Environment, canteen : Canteen, customer : Customer) -> Generator[simpy.Event, None, None]:
    with canteen.request() as req:
        yield req

        for i, visit in enumerate(customer.menu):
            if visit == 1:
                station = canteen.stations[i]
                product = random.choice(station.products)             # type: ignore
                yield env.process(station.serve(customer, product))   # type: ignore

        cash_point = cast(Cash, canteen.stations[-1])
        with cash_point.request() as req_cash_point:
            yield req_cash_point
            yield env.process(cash_point.pay(customer))

            customer.exit = env.now



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
                  employees : Tuple[Employee,...],
                  stations : Tuple[Union[ServiceStation, SelfServiceStation, Cash],...],
                  opening_time : float = 300.0,
                  capacity : int = 20

                  ) -> None:
        """
        Initialize.

        :param env: The simulation environment.

        :param opening_time: The time [minutes] that the canteen stays open.
        :param capacity: The maximum number of customers it can host.

        """
        self.env = env
        self.employees = employees
        self.stations = stations
        self.opening_time = opening_time

        super(Canteen, self).__init__(env, capacity)
