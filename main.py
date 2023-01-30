from functools import partial
import multiprocessing
import static_main
import partage_main
import adaptatif_main
from matplotlib import pyplot as plt


def main():
    print("""Do you want to
    1- See peak response for a specific algorithm?
    2- See loss probability graph for a specific algorithm?
    3- See efficiency comparison between the algorithms?
    4- Custom comparison""")
    try:
        choice = int(input())
    except:
        choice = -1

    if choice == 1:
        print("What algorithm do you want to see peak response for?\n\t1- Static\n\t2- Load Balancer\n\t3- Adaptative\n\t4- Adaptative with delay")
        alg = int(input())

        print("What is the peak size you want to check for?")
        peak = int(input())

        if alg == 1:
            static_main.main3(peak)
        elif alg == 2:
            partage_main.main3(peak)
        elif alg == 3:
            adaptatif_main.main3(peak)
        elif alg == 4:
            adaptatif_main.main3(peak, 3)
    elif choice == 2:
        print("What algorithm do you want to see the loss probability for?\n\t1- Static\n\t2- Load Balancer\n\t3- Adaptative\n\t4- Adaptative with delay")
        alg = int(input())

        if alg == 1:
            static_main.main()
        elif alg == 2:
            partage_main.main()
        elif alg == 3:
            adaptatif_main.main()
        elif alg == 4:
            adaptatif_main.main(3)
        else:
            print("Unknown option. Please choose a number from 1 to 4")
            exit(-1)
    elif choice == 3:
        import compare
        compare.main()
    elif choice == 4:
        print("What kind of graph do you want to plot?\n\t1- Loss probability\n\t2- Peak response")
        try:
            kind = int(input())
        except:
            kind = -1

        print("What algorithms do you want to plot? You can choose more than 1, separate by commas (1,2,4)")
        print("\t1- Static\n\t2- Load Balancer\n\t3- Adaptative\n\t4- Adaptative with delay")

        try:
            algs = set(map(lambda x: int(x.strip()), input().split(',')))
        except:
            print("Unknown option. Please choose a number from 1 to 4")
            exit(-1)

        if kind == 1:
            outs = []
            labels = []

            xs = [1] + list(range(10, 1000, 10)) + list(range(1020, 2000, 20))

            with multiprocessing.Pool() as ex:
                for alg in algs:
                    if alg == 1:
                        outs.append(list(ex.map(partial(static_main.measure_probability), xs)))
                        labels.append("Statique")
                    elif alg == 2:
                        outs.append(list(ex.map(partial(partage_main.measure_probability), xs)))
                        labels.append("Partage de Charge")
                    elif alg == 3:
                        outs.append(list(ex.map(partial(adaptatif_main.measure_probability, delay=0), xs)))
                        labels.append("Adaptatif")
                    elif alg == 4:
                        outs.append(list(ex.map(partial(adaptatif_main.measure_probability, delay=30), xs)))
                        labels.append("Adaptatif avec 30s délai")
            
            for ys, lab in zip(outs, labels):
                plt.plot(xs, [100*y for y in ys], label=lab)
            plt.xlabel("Densité d'appels")
            plt.ylabel("% d'appels perdus")
            plt.xlim((0, max(xs)))
            plt.ylim((0, 100))
            plt.grid(True)
            plt.legend()
            plt.show()
        elif kind == 2: # Peak response
            outs = []
            labels = []

            try:
                print("What should the total simulation time be, in minutes? Beware that 5 extra minutes will be added to the beginning\n(default: 15)")
                if len(i := input()) == 0:
                    time = 15
                else:
                    time = int(i)

                print("What should the result timestep be? (in seconds)\n(default: 20)")
                if len(i := input()) == 0:
                    out_step = 20
                else:
                    out_step = int(i)

                print("What should the peak size be?\n(default: 300)")
                if len(i := input()) == 0:
                    peak = 300
                else:
                    peak = int(i)

                print("What should the peak duration be?\n(default: 2)")
                if len(i := input()) == 0:
                    duration = 2
                else:
                    duration = int(i)
            except:
                print("Unknown option. Please choose a number from 1 to 4")
                exit(-1)

            xs = [20] * 7 + [peak] * duration + [20] * 100
            xf = lambda x: xs[x]

            for alg in algs:
                if alg == 1:
                    static_main.SIMULATION_MINUTES = time
                    outs.append(static_main.measure_loss(xf, out_step))
                    labels.append("Statique")
                elif alg == 2:
                    partage_main.SIMULATION_MINUTES = time
                    outs.append(partage_main.measure_loss(xf, out_step))
                    labels.append("Partage de Charge")
                elif alg == 3:
                    adaptatif_main.SIMULATION_MINUTES = time
                    outs.append(adaptatif_main.measure_loss(xf, out_step, 0))
                    labels.append("Adaptatif")
                elif alg == 4:
                    adaptatif_main.SIMULATION_MINUTES = time
                    outs.append(adaptatif_main.measure_loss(xf, out_step, 30))
                    labels.append("Adaptatif avec 30s délai")
            
            minute = (len(outs[0]) * out_step) // 60
            plt.step(list(range(minute)), xs[:minute], label="Appels démarrés par minute")

            for ys in outs:
                plt.step([i * out_step / 60 for i in range(len(ys))], ys, label="Appels perdus par minute")
            
            plt.xlabel("Minutes")
            plt.grid(True)
            plt.legend()
            plt.show()
        else:
            print("Unknown option. Please choose a number from 1 to 4")
            exit(-1)
    else:
        print("Unknown option. Please choose a number from 1 to 4")
        exit(-1)


if __name__ == '__main__':
    main()