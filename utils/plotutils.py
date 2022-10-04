# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


SITE_CMAP = ListedColormap([
    "black",
    "orange",
    "chocolate",
    "wheat",
    "red",
    "lightsalmon",
    "palevioletred",
    "mediumslateblue",
    "blue",
    "lime",
    "palegreen",
    "olive",
    "green",
    "red",
    "blue",
    "pink"
])


def plot_grid(*args):
    if len(args) == 1:
        fig, ax = plt.subplots()
        img = ax.imshow(args[0].raw, cmap="gist_ncar")
        fig.colorbar(img, ax=ax, aspect=50)
    else:
        fig, axs = plt.subplots(1, len(args))

        for ax, grid in zip(axs, args):
            img = ax.imshow(grid.raw, cmap="gist_ncar")
            fig.colorbar(img, ax=ax, aspect=50)

    plt.show()


def plot_site(*args):
    if len(args) == 1:
        fig, ax = plt.subplots()
        img = ax.imshow(args[0], cmap=SITE_CMAP, vmin=0, vmax=15)
        fig.colorbar(img, ax=ax, aspect=50)
    else:
        fig, axs = plt.subplots(1, len(args))

        for ax, site in zip(axs, args):
            img = ax.imshow(site, cmap=SITE_CMAP, vmin=0, vmax=15)
            fig.colorbar(img, ax=ax, aspect=50)

    plt.show()


def main():
    gene = []
    with open("D:/_swmm_results/2021-11-11_05-55-08/404/0.csv") as f:
        for line in f:
            gene.append(list(map(int, line.split(","))))

    plot_site(gene)

if __name__ == "__main__":
    main()