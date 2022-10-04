import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap


def draw(original_map, area_map, up_map, down_map, left_map, right_map):
    cmap = ListedColormap([
        "gray",
        "wheat",
        "orange",
        "palegoldenrod",
        "red",
        "lightsalmon",
        "palevioletred",
        "slateblue",
        "blue",
        "green",
        "lime",
        "yellowgreen",
        "olivedrab",
        "yellow",
        "white"
    ])

    fig, axs = plt.subplots(2, 3)

    axs[0, 0].pcolormesh(original_map, cmap=cmap)
    axs[0, 1].pcolormesh(area_map)
    axs[0, 2].pcolormesh(up_map)
    axs[1, 0].pcolormesh(down_map)
    axs[1, 1].pcolormesh(left_map)
    axs[1, 2].pcolormesh(right_map)

    for ax in axs.reshape(-1):
        ax.invert_yaxis()
        ax.axis("equal")

    plt.show()


def main():
    pass


if __name__ == "__main__":
    main()
