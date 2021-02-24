import simpy
import canteen
import customer



if __name__ == '__main__':
    env = simpy.Environment()
    c = canteen.Canteen(env)

    p = customer.Customer(env, c, 10, 1, 1)
    print(p.history)
