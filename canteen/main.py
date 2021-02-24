import simpy
import canteen
import customer


def test (env, store):
    s.put(3)
    yield s.get(1)
    print(store.level)
    w = s.get(1)
    yield env.timeout(8)
    yield w
    print(env.now)
    print(store.level)




if __name__ == '__main__':
    env = simpy.Environment()
    c = canteen.Canteen(env)


    s = simpy.Container(env, capacity=3, init=3)
    env.process(test(env, s))
    env.run()
