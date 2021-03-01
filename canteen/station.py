from __future__ import annotations

import simpy

import priority
from employee import Employee

from simpy.resources.container import ContainerPut, ContainerGet
from simpy.resources.resource import PriorityRequest
from typing import Tuple, Dict, Optional, Generator, cast


class MultiStore (object):
    """
    Simpy only provides a Store or a Container.
      - The Store can handle more different items all together and admit to put or
        get only one element at a time. This is not suitable for our case, because
        we need to manage different products but separately, and we need to put even
        more than one at the same time (a for loop would be too expensive).
      - The Container allows the put or get of more items at once, but again it manage
        just one product at a time.

    The MultiStore is in the middle between them, and it is used to simulate
    the stations of the canteen.
    It manage more products keeping them separated, and it allows the storage or
    retrieve of more products at the same time.

    It basically just have many Container, and sort the requests coming from the
    calling process to the Container containing the product considered.

    """

    def __init__ (self,
                  env : simpy.Environment,
                  products : Tuple[str,...],
                  capacities : Tuple[int,...],
                  init : Optional[Tuple[int,...]] = None
                ) -> None:
        """
        Initialize.

        :param env: The simulation environment.
        :param products: The products handled.
        :param capacities: The capacity of the different Store incorporated.
        :param init: The initial quantities in the containers. If not provided is
                    set by default equal to the capacity.

        """
        self.env = env
        self.products = products
        self.capacities : Dict[str, int] = {p : q for p, q in zip(products,capacities)}

        init = init or tuple(capacities)
        self.containers : Dict[str, simpy.Container] = {
                                            p : simpy.Container(env, c, init=i)
                                            for p, c, i in zip(products, capacities, init)
                                            }


    def get (self, product : str, amount : int) -> ContainerGet:
        """
        This method just sorts the GET requests to the correct product handled
        by the MultiStore.
        The process that calls the GET, also has the responsibility to wait for it.

        :param product: The name of the product required.
        :param amount: The quatity insert into the MultiStore
        :return: The request to the Container containing the required product.

        """
        return self.containers[product].get(amount)




    def put (self, product : str, amount : int) -> ContainerPut:
        """
        This method just sorts the PUT requests to the correct product handled
        by the MultiStore.
        The process that calls the PUT, also has the responsibility to wait for it.

        :param product: The name of the product put into the container.
        :param amount: The quatity retrieved by the MultiStore
        :return: The request to the Container containing the required product.

        """
        return self.containers[product].put(amount)




class ProductiveStation (MultiStore):
    """
    An instance of this class represents a productive station of the canteen.
    A productive station is a station where the food is cooked, before bringing
    it to a SelfServiceStation or a ServiceStation.

    By default, these stations require an employee to start them (e.g., throwing
    the pasta in the boiling water or putting the meat on the grill). Then the employee
    is usually released and made free for other operations.
    However, setting the variable <keep> to TRUE, it is possible to ask to the
    ProductiveStation to keep the employee until the production time is passed.

    Each ProductiveStation has a corresponding ServiceStation or SelfServiceStation
    and the request to produce a new batch of a specific product arrives when
    the quantity remained in the ServiceStation goes under a certain threshold, i.e.,
    reorder level.

    Each time this station need a resource, a request is sent to each employee,
    and the first resource available is kept, while the other request are cancelled.

    """

    def __init__ (self,
                  env : simpy.Environment,
                  employees : Tuple[Employee,...],
                  products : Tuple[str,...],
                  capacities : Tuple[int,...],
                  production_times : Tuple[int,...],
                  preparation_times : Tuple[int,...],
                  keep : Optional[Tuple[bool, ...]] = None
                ) -> None:
        """
        Initialise.

        :param env: The simulation Environment.
        :param employees: The resources that might wotk on this station.
        :param products: The products handled by the production station.
        :param capacities: The capacity of each container.
        :param production_times: The time needed to produce a batch of the products.
        :param preparation_times: The preparation time needed to prepare each product
                                  before starting its production.
        :param keep: If true, while producing the respective product, the employee
                     is kept busy, otherwise he/she is released and required gain
                     when the food is ready. By default it is false.

        """
        super(ProductiveStation, self).__init__(env, products, capacities, tuple([0]*len(capacities)))
        self.employees = employees
        self.production_times : Dict[str, int] = {p : k for p, k in zip (products, production_times)}
        self.preparation_times : Dict[str, int] = {p : k for p, k in zip(products, preparation_times)}

        keep = keep or tuple([False] * len(products))
        self.keep : Dict[str, bool] = {p : k for p, k in zip(products, keep)}

        self.current_request : Optional[PriorityRequest] = None


    def work (self,
              product : str,
              priority_level : int = priority.NORMAL
            ) -> Generator[simpy.Event, None, None]:
        """


        :param product: The troduct to be cooked.
        :param priority_level: The priority given to the need for an employee. The higher is the
                               priority value the less is the hurry to complete the operation.

        """
        env = self.env
        capacity = self.capacities[product]
        prod_time, prep_time = self.production_times[product], self.preparation_times[product]
        # Make a request to all the employees
        requests = [employee.request(priority=priority_level, preempt = False) for employee in self.employees]
        # Wait for the first one to be free
        condition_value = yield env.any_of(requests)
        # Get the winner request and the relative employee
        req : PriorityRequest = condition_value.events[0] # type: ignore
        employee : Employee = req.resource                # type: ignore
        # Delete other requests
        # !NOTE! The winner is not cancelled because already triggered
        [r.cancel() for r in requests] # type: ignore
        # Prepare everything
        yield env.timeout(prep_time)
        # If the employee is not needed its released
        if not self.keep[product]:
            employee.release (req)
        # Produce
        yield env.timeout(prod_time)
        self.put(product, capacity)
        # Release the resource used
        employee.release (req)
        self.current_request = None


    def serve (self,
               service_station : MultiStore,
               product : str,
               priority_level : int = priority.URGENT
            ) -> Generator[simpy.Event, None, None]:
        """

        """
        # If there are no employees already working on this ProductiveStation
        # we look for another one.
        if not self.current_request:
            # Make a request to all the employees
            requests = [employee.request(priority = priority_level, preempt = False) for employee in self.employees]
            # Wait for the first one to be free
            condition_value = yield env.any_of(requests)
            # Get the winner request and the relative employee
            req = condition_value.events[0]     # type: ignore
            employee = req.resource             # type: ignore

        # Conclude and release the employee
        capacity = self.capacities[product]
        self.get(product, capacity)
        service_station.put(product, capacity)
        employee.release (req)



        #
