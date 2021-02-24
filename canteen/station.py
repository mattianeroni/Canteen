from __future__ import annotations

import simpy

from simpy.resources.container import ContainerPut, ContainerGet
from typing import Tuple, Dict, Optional


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
                  capacities : Tuple[int,...]
                ) -> None:
        """
        Initialize.

        :param env: The simulation environment.
        :param products: The products handled.
        :param capacities: The capacity of the different Store incorporated.

        """
        self.env = env
        self.products = products
        self.containers : Dict[str, simpy.Container] = {
                                            p : simpy.Container(env, c, init=c)
                                            for p, c in zip(products, capacities)
                                            }


    def get (self, product : str) -> ContainerGet:
        """
        This method just sorts the GET requests to the correct product handled
        by the MultiStore.
        The process that calls the GET, also has the responsibility to wait for it.

        :param product: The name of the product required.

        :return: The request to the Container containing the required product.

        """
        return self.containers[product].get(1)




    def put (self, product : str, amount : int) -> ContainerPut:
        """
        This method just sorts the PUT requests to the correct product handled
        by the MultiStore.
        The process that calls the PUT, also has the responsibility to wait for it.

        :param product: The name of the product put into the container.

        :return: The request to the Container containing the required product.

        """
        return self.containers[product].put(amount)
