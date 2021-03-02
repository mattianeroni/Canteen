from __future__ import annotations

import simpy

import priority
import logs
from employee import Employee

from simpy.resources.container import ContainerPut, ContainerGet
from simpy.resources.resource import PriorityRequest
from typing import Tuple, Dict, Optional, Generator


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

        NOTE: A problem in the simpy Container must be corrected. When trying to
        get an amount higher than the current level, the quantity retrieved is
        accually null. Here the problem (or feature???) is corrected by retrieving
        the biggest possible amount.

        :param product: The name of the product required.
        :param amount: The quatity insert into the MultiStore
        :return: The request to the Container containing the required product.

        """
        c = self.containers[product]
        return c.get(min(c.level, amount))




    def put (self, product : str, amount : int) -> ContainerPut:
        """
        This method just sorts the PUT requests to the correct product handled
        by the MultiStore.
        The process that calls the PUT, also has the responsibility to wait for it.

        NOTE: A problem in the simpy Container must be corrected. When trying to
        put an amount higher than the remaining space, the quantity put is
        accually null. Here the problem (or feature???) is corrected by storing
        the biggest possible amount.

        :param product: The name of the product put into the container.
        :param amount: The quatity retrieved by the MultiStore
        :return: The request to the Container containing the required product.

        """
        c = self.containers[product]
        return c.put(min(amount, c.capacity - c.level))



    def level (self, product : str) -> int:
        """
        This method just provide the quantity of products inside a specific container.

        :param product: The name of the product of interest.
        :return: The quantity currently on hand of that product.

        """
        return int(self.containers[product].level)




class ResourceManager (object):
    """
    This class is mainly made for inheritance and not for instantiation.
    It contains some methods and attributes usefull to get a resource (or employee)
    from a set of many. It basically sends the a request to each resource, and
    than wait until one gets free. In case a resource is already busy, it just make
    a further request to that resource using a extraordaniray priority, to avoid the
    resource to escape for doing something else.

    """
    def __init__ (self, env : simpy.Environment, employees : Tuple[Employee,...]) -> None:
        """
        Initialize.

        :param env: The simulation environment.
        :param employees: The pool of employees from which the station can take.

        """
        self.env = env
        self.employees = employees
        self.current_request : Optional[PriorityRequest] = None


    def getResource (self, priority_level : int) -> Generator[simpy.Event, None, None]:
        """
        This method get a resource.
        It basically sends the a request to each resource, and than wait until one
        gets free. In case a resource is already busy, itenv, store just make a further request
        to that resource using a extraordaniray priority, to avoid the resource to
        escape for doing something else.

        :param priority_level: The priority level.

        """
        req : PriorityRequest
        employee : Employee

        if not self.current_request:
            # Make a request to all the employees
            requests = [employee.request(priority=priority_level, preempt = False) for employee in self.employees]
            # Wait for the first one to be free
            condition_value = yield self.env.any_of(requests)
            # Get the winner request and the relative employee
            req = condition_value.events[0] # type: ignore
            employee = req.resource                # type: ignore
            self.current_request = req
            # Delete other requests
            # !NOTE! The winner is not cancelled because already triggered
            [r.cancel() for r in requests] # type: ignore
        else:
            # If an empoyee is already working in this station, wait for him/her to
            # be free, sending him an extraordinary request.
            req = employee.request(priority=priority.EXTRAORDINARY, preempt = False)
            yield req
            self.current_request = req


    def releaseResource (self) -> None:
        """
        This method just release the resource occupied by the current_request.

        """
        if self.current_request is None:
            raise logs.ResourceError("The resource released was never required")

        employee = self.current_request.resource
        employee.release (self.current_request)
        self.current_request = None




class ProductiveStation (MultiStore, ResourceManager):
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
        MultiStore.__init__(self, env, products, capacities, tuple([0]*len(capacities)))
        ResourceManager.__init__(self, env, employees)

        self.env = env

        self.production_times : Dict[str, int] = {p : k for p, k in zip (products, production_times)}
        self.preparation_times : Dict[str, int] = {p : k for p, k in zip(products, preparation_times)}

        keep = keep or tuple([False] * len(products))
        self.keep : Dict[str, bool] = {p : k for p, k in zip(products, keep)}





    def work (self,
              product : str,
              priority_level : int = priority.NORMAL,
              service_station : Optional[MultiStore] = None

              ) -> Generator[simpy.Event, None, None]:
        """
        This method is used by the ProductiveStation to prepare / cook a certain product.
        To this is given a certain priority that will depend on the necessity
        by the respective ServiceStation to refill. It is possible to require
        an immediate refilling after the production process by giving to the method
        the reference to the ServiceStation as argument.

        The resource required by the process is first resulting available with
        respect to the resource pool involved. In case a resource is already working
        on the station, that specific resource is used sending him/her a EXTRAORDINARY
        request with priority on everithing else.


        :param product: The troduct to be cooked.
        :param priority_level: The priority given to the need for an employee. The higher is the
                               priority value the less is the hurry to complete the operation.
        :param service_station: The service station for which the ProductiveStation
                                is producing. It is served as soon as the production
                                is concluded.

        """
        env = self.env
        capacity = self.capacities[product]
        prod_time = self.production_times[product]
        prep_time = self.preparation_times[product]
        # Wait for a resource
        yield env.process(self.getResource(priority_level))
        req : PriorityRequest = self.current_request        # type: ignore
        employee : Employee = req.resource                  # type: ignore

        # Prepare everything
        yield env.timeout(prep_time)
        # If the employee is not needed its released
        if not self.keep[product]:
            self.releaseResource()
        # Produce
        yield env.timeout(prod_time)
        self.put(product, capacity)

        # Eventually ask to the current occupied resource to take care of the downloading
        # operations before being released.
        if service_station:
            env.process (self.serve(service_station, product, priority_level))

        # Release the resource eventually used for working
        if self.keep[product]:
            self.releaseResource()


    def serve (self,
               service_station : MultiStore,
               product : str,
               priority_level : int = priority.MEDIUM
            ) -> Generator[simpy.Event, None, None]:
        """
        This method is used by the ProductiveStation to refill a specific ServiceStation.

        The resource required by the process is first resulting available with
        respect to the resource pool involved. In case a resource is already working
        on the station, that specific resource is used sending him/her a EXTRAORDINARY
        request with priority on everithing else.

        NOTE: By default the priority level of this process is higher than the priority
        of the production process, because, usually, when the food is ready must
        by removed from the production station as soon as possible. The risk could be
        to burn it.

        :param service_station: The service station to refill.
        :param product: The interested product.
        :param priority_level: The priority level of the request.

        """
        # Wait for a resource
        yield self.env.process(self.getResource(priority_level))
        req : PriorityRequest = self.current_request    # type: ignore
        employee : Employee = req.resource              # type: ignore

        # Refill the service station
        yield self.env.timeout(5)

        # Conclude and release the employee
        capacity = self.capacities[product]
        self.get(product, capacity)
        service_station.put(product, capacity)
        self.releaseResource()



class SelfServiceStation (MultiStore):
    """
    An instance of this class represents a self service station, in which the
    customers can be served without requiring an employee. However, when the
    station is empty or the quantity is under a certain level, it requires
    to the respective ProductiveStation to produce the missing product.

    The production of course takes time and need an employee, but also the service
    of customers and the refilling at the SelfServiceStation take time, and this
    time depends on the energy and experience of the employee involved.

    """

    def __init__ (self,
                  env : simpy.Environment,
                  supplier : ProductiveStation,
                  products : Tuple[str, ...],
                  capacities : Tuple[int, ...],
                  service_times : Tuple[int, ...],
                  refilling_times : Tuple[int, ...],
                  reorder_levels : Optional[Tuple[int,...]] = None

                ) -> None:
        """
        Initialize.

        :param env: The simulation environment.
        :param supplier: The respective productive station.
        :param products: The handled products.
        :param capacities: The maximum quantity that can be stored for each product.
        :param service_times: The average times needed to serve a customer with
                              each of the handled products.
        :param refilling_times: The average times needed to serve a customer with
                                each of the handled products.
        :param reorder_levels: The reorder level per each handled product.

        """
        super (SelfServiceStation, self).__init__(env, products, capacities, init=capacities)

        self.env = env
        self.supplier = supplier

        self.service_times : Dict[str, int] = {p : k for p, k in zip (products, service_times)}
        self.refilling_times : Dict[str, int] = {p : k for p, k in zip(products, refilling_times)}

        reorder_levels = reorder_levels or tuple(0 for _ in products)
        self.reorder_levels = {p : k for p, k in zip(products, reorder_levels)}
