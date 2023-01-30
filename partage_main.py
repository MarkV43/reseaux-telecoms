from partage_router import LoadBalancerRouter
from router import RouterType
import random
from itertools import pairwise
import matplotlib.pyplot as plt
import multiprocessing
from collections.abc import Callable
import numpy as np

SIMULATION_MINUTES = 40

CTS1 = LoadBalancerRouter(RouterType.CTS, 'CTS1')
CTS2 = LoadBalancerRouter(RouterType.CTS, 'CTS2')
CA1 = LoadBalancerRouter(RouterType.CA, 'CA1')
CA2 = LoadBalancerRouter(RouterType.CA, 'CA2')
CA3 = LoadBalancerRouter(RouterType.CA, 'CA3')

CTS1.connect(CTS2)
CTS1.connect(CA1)
CTS1.connect(CA2)
CTS1.connect(CA3)
CTS2.connect(CA1)
CTS2.connect(CA2)
CTS2.connect(CA3)
CA1.connect(CA2)
CA2.connect(CA3)

stations = [CA1, CA2, CA3]

CA1.calculate_paths(stations)

# print(CA1.route(CA3))
# print(CA1.route(CA3))
# print(CA1.route(CA3))
# print(CA1.route(CA3))

# exit(0)


def simulation(calls_per_minute: int | Callable[[int], int]) -> tuple[float, float, float]:
    minutes = 0
    seconds = 0
    new_calls = [0] * 60

    lost_calls = 0

    durations = []

    total_calls = 0

    nb_concurrent_calls = []
    nb_lost_calls = []

    # reset routers
    for st in (CTS1, CTS2, CA1, CA2, CA3):
        st.reset()

    while minutes < SIMULATION_MINUTES + 5:
        if seconds == 0:
            new_calls = [0] * 60

            if type(calls_per_minute) is int:
                cpm = calls_per_minute
            else:
                cpm = calls_per_minute(minutes)

            for _ in range(cpm):
                sec = int(random.random() * 60)
                new_calls[sec] += 1
        
        now = minutes * 60 + seconds

        total_calls += new_calls[seconds]
        
        for _ in range(new_calls[seconds]):
            # choose source and destination
            i = random.randrange(3)
            while (j := random.randrange(3)) == i:
                pass

            source = stations[i]
            destination = stations[j]

            path = source.route(destination)
            
            if path is not None:
                # increment path
                for a, b in pairwise(path):
                    assert a.neighbors[b].increment()

                duration_seconds = int((random.random() * 4 + 1) * 60)
                durations.append((now + duration_seconds, path))
            else:
                if minutes > 5:
                    lost_calls += 1
                    total_calls -= 1

        for i, (duration, path) in enumerate(durations):
            if now >= duration:
                # decrement path
                for a, b in pairwise(path):
                    assert a.neighbors[b].decrement()
                    # connection = a.neighbors[b]
                    # connection.amount -= 1

                del durations[i]

                total_calls -= 1
        
        nb_concurrent_calls.append(total_calls)
        nb_lost_calls.append(lost_calls)

        seconds += 1
        if seconds >= 60:
            seconds -= 60
            minutes += 1

    # TODO: change cpm
    probability = lost_calls / (cpm * SIMULATION_MINUTES)
    # print(f"Total number of lost calls in {SIMULATION_MINUTES} minutes: {lost_calls}")
    # print(f"Probability of loss: {probability} %")

    return probability, nb_concurrent_calls, nb_lost_calls

def measure_probability(x):
    return simulation(x)[0]

def measure_count(x):
    return simulation(x)[1]

def measure_loss(x):
    print(x if type(x) is int else x(0))
    return simulation(x)[2]

def main():
    import time
    start = time.time()

    with multiprocessing.Pool() as ex:
        xs = list(range(100, 1000, 10)) + \
             list(range(1020, 2000, 20))
        
        static = list(ex.map(measure_probability, xs))

        end = time.time()
        print(end - start)

        plt.plot(xs, static, label="PC Routing")
        plt.grid(True)
        plt.legend()
        plt.show()


def main2():
    # cpm = list(map(int, np.random.randn(100) * 200 + 300))
    cpm = list(map(int, [20] * 7 + [700, 900] + [20] * 100))
    ys = measure_count(lambda x: cpm[x])
    # ys = measure_loss(lambda x: ([50, 50, 100, 50, 50, 1000, 1000, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20])[x])
    xs = range(len(ys))
    plt.plot(list(map(lambda x: x/60, xs)), ys, label="Nb appel concurrents")
    minute = max(map(lambda x: x//60, xs))
    plt.plot(list(range(minute)), cpm[:minute], label="Nb appel généré/min")
    plt.xlabel("Minutes")
    plt.legend()
    plt.show()

def main3(peak):
    global SIMULATION_MINUTES
    SIMULATION_MINUTES = 15
    
    cpm = list(map(int, [20] * 7 + [peak] * 2 + [20] * 100))
    out_step = 20
    ys = measure_loss(lambda x: cpm[x], out_step)
    print(ys)
    xs = range(len(ys))

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    minute = (len(ys) * out_step) // 60 + 1

    print("minute", minute)
    print(len(ys))

    ax1.step([i * out_step / 60 for i in range(len(ys))], ys, 'g-', label="Appels perdus par minute")

    ax2.step(list(range(minute)), cpm[:minute], 'b-', label="Appels démarrés par minute")

    ax1.set_xlabel("Minutes")
    ax1.set_ylabel("Appels perdus par minute", color='g')
    ax2.set_ylabel("Appels démarrés par minute", color='b')
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    main3()
