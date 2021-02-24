import simpy


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
                  opening_time : int = 3000,
                  capacity : int = 100
                  ) -> None:
        """


        """
        self.opening_time = opening_time
        super(Canteen, self).__init__(env, capacity)
