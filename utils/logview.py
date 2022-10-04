import matplotlib.pyplot as plt
from collections import defaultdict


def main():
    data = defaultdict(list)
    finder = {}
    with open("D:/_swmm_results/2021-11-11_05-55-08/costs.csv") as f:
        cost_names = list(f.readline().split(","))[2:]
        print(cost_names)
        for line in f:
            generation, ranking, *costs = line.split(",")

            # if ranking == "0" or ranking == "1":
            #     finder[int(generation), int(ranking)] = float(costs[0])


            if ranking != "0":
                continue

            # data[int(generation)] = list(map(float, costs))

            for value, name in zip(costs, cost_names):
                data[name].append(float(value))

    # print(data)

    # counter = defaultdict(list)

    # for code, c in finder.items():
    #     counter[c].append(code)

    # for cost in sorted(counter, key=lambda x: len(counter[x]), reverse=True):
    #     print(f"{counter[cost][0][0]}세대 {counter[cost][0][1]}번, 지속세대수: {len(counter[cost])}, 코스트: {cost}")









    # fig, axs = plt.subplots(2, 4)  # Create a figure containing a single axes.

    # axs[0, 0].plot(data.keys(), [costs[0] for costs in data.values()])
    # axs[0, 0].set_title("total")

    # axs[0, 1].plot(data.keys(), [costs[1] for costs in data.values()], label="cluster_count")
    # axs[0, 1].set_title("cluster_count")

    # axs[0, 2].plot(data.keys(), [costs[2] for costs in data.values()], label="magnet")
    # axs[0, 2].set_title("magnet")

    # axs[1, 0].plot(data.keys(), [costs[3] for costs in data.values()], label="area")
    # axs[1, 0].set_title("area")

    # axs[1, 1].plot(data.keys(), [costs[4] for costs in data.values()], label="repulsion")
    # axs[1, 1].set_title("repulsion")

    # axs[1, 2].plot(data.keys(), [costs[5] for costs in data.values()], label="attraction")
    # axs[1, 2].set_title("attraction")

    # axs[1, 3].plot(data.keys(), [costs[6] for costs in data.values()], label="runoff")
    # axs[1, 3].set_title("runoff")


    # fig, axs = plt.subplots(1, 2)

    # axs[0].plot(data.keys(), [costs[0] for costs in data.values()])
    # axs[0].set_title("total")

    # axs[1].plot(data.keys(), [costs[6] for costs in data.values()], label="runoff")
    # axs[1].set_title("runoff")

    plt.subplot(121)
    plt.plot(range(len(data["total"])), data["total"])
    plt.subplot(122)
    plt.plot(range(len(data["total_runoff"])), data["total_runoff"])

    plt.show()


if __name__ == "__main__":
    main()
