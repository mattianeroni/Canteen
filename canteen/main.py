import simpy

import canteen
import customer
import employee
import products
from station import SelfServiceStation, ServiceStation, ProductiveStation, Cash


if __name__ == '__main__':

    # Expressed in minutes
    SIM_TIME = 300.0

    env = simpy.Environment()
    employees = employee.source ( (3, 3, 2, 2, 1), env )

    stations = (
        # Starters
        SelfServiceStation(env,
                           supplier=ProductiveStation(),
                           products=(products.CAPRESE, products.COLDRICE, products.HAM),
                           capacities=(3, 3, 3),
                           service_times=(1.5, 1.5, 1.5),
                           refilling_times=(3.0, 3.0, 3.0),
                           reorder_levels=(0, 0, 0)
                           ),
        # Pizza
        ServiceStation(env,
                       employees,
                       supplier=ProductiveStation(),
                       products=(products.PIZZA, ),
                       capacities=(1, ),
                       service_times=(2.5, ),
                       refilling_times=(3.0, ),
                       reorder_levels=(0, )
                       ),
        # First
        ServiceStation(env,
                       employees,
                       supplier=ProductiveStation(),
                       products=(products.CARBONARA, products.RAGU, products.RICE),
                       capacities=(6, 6, 6),
                       service_times=(5.0, 5.0, 5.0),
                       refilling_times=(8.0, 8.0, 8.0),
                       reorder_levels=(2, 2, 2)
                       ),
        # Second
        ServiceStation(env,
                       employees,
                       supplier=ProductiveStation(),
                       products=(products.MEET, products.FISH, products.ROAST),
                       capacities=(10, 10, 10),
                       service_times=(2.0, 2.0, 2.0),
                       refilling_times=(8.0, 8.0, 8.0),
                       reorder_levels=(3, 3, 3)
                       ),
        # Side
        SelfServiceStation(env,
                           supplier=ProductiveStation(),
                           products=(products.SALAD, products.MAIS, products.POTATOES),
                           capacities=(3, 3, 3),
                           service_times=(6.0, 6.0, 6.0),
                           refilling_times=(1.0, 1.0, 1.0),
                           reorder_levels=(1, 1, 1)
                           ),
        # Sweet
        SelfServiceStation(env,
                           supplier=ProductiveStation(),
                           products=(products.YOGURT, products.CAKE, products.FRUIT),
                           capacities=(10, 10, 10),
                           service_times=(.5, .5, .5),
                           refilling_times=(5.0, 5.0, 5.0),
                           reorder_levels=(2, 2, 2)
                           ),
        # Drink
        SelfServiceStation(env,
                           supplier=ProductiveStation(),
                           products=(products.COKE, products.WATER, products.BEER),
                           capacities=(30, 30, 30),
                           service_times=(.5, .5, .5),
                           refilling_times=(15.0, 15.0, 15.0),
                           reorder_levels=(7, 7, 7)
                           ),
        # CashPoint
        Cash(env, payTime=5.0)
    )

    c = canteen.Canteen(env, employees, stations, SIM_TIME, capacity = 20)
    customers = customer.source ( customer.arrivalFunction, SIM_TIME, env, c )


    env.run(until=SIM_TIME)
