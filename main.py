def main():
    print("Do you want to\n\t1- See peak response for a specific algorithm?\n\t2- See efficiency comparison between the algorithms?")
    choice = int(input())

    if choice == 1:
        print("What algorithm do you want to see peak response for?\n\t1- Static\n\t2- Load Balancer\n\t3- Adaptative\n\t4- Adaptative with delay")
        alg = int(input())

        print("What is the peak size you want to check for?")
        peak = int(input())

        if alg == 1:
            import static_main
            static_main.main3(peak)
        elif alg == 2:
            import partage_main
            partage_main.main3(peak)
        elif alg == 3:
            import adaptatif_main
            adaptatif_main.main3(peak)
        elif alg == 4:
            import adaptatif_main
            adaptatif_main.main3(peak, 3)
    else:
        import compare
        compare.main()


if __name__ == '__main__':
    main()