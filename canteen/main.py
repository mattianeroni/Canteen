import simpy
import canteen
import customer


def test (env, store):
    yield env.timeout (1)
    store.put(store.capacity - store.level)
    print(store.level)







if __name__ == '__main__':
    env = simpy.Environment()
    #c = canteen.Canteen(env)

    s = simpy.Container(env, capacity=5, init=2)
    env.process(test(env, s))
    env.run()
