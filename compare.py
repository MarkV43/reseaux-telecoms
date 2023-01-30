import multiprocessing
import static_main
import partage_main
import adaptatif_main
import matplotlib.pyplot as plt
from functools import partial


def main():
    import time
    start = time.time()

    with multiprocessing.Pool() as ex:
        xs = list(range(1, 1000, 10)) + \
             list(range(1020, 2000, 20))
        
        static          = list(ex.map(static_main.measure_probability, xs))
        partage         = list(ex.map(partage_main.measure_probability, xs))
        adaptatif       = list(ex.map(partial(adaptatif_main.measure_probability, delay=0), xs))
        adaptatif_delay = list(ex.map(partial(adaptatif_main.measure_probability, delay=30), xs))

        end = time.time()
        print(end - start)

        plt.plot(xs, [100*x for x in static], label="Static")
        plt.plot(xs, [100*x for x in partage], label="Partage de Charge")
        plt.plot(xs, [100*x for x in adaptatif], label="Adaptatif")
        plt.plot(xs, [100*x for x in adaptatif_delay], label="Adaptatif avec 3s délai")
        plt.xlabel("Nb d'appels concurrents")
        plt.ylabel("% d'appels perdus")
        plt.xlim((0, max(xs)))
        plt.ylim((0, 100))
        plt.grid(True)
        plt.legend()
        plt.show()


if __name__ == '__main__':
    main()