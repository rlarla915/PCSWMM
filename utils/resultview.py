import matplotlib.pyplot as plt
import numpy as np
# from collections import defaultdict

# from numpy.core.numeric import ones
# from ..ga2d import Grid
from matplotlib.colors import ListedColormap


HEIGHT = 111
WIDTH = 71

TAG_TO_CODE = {
    "도로": -1,
    "공동주택": 1,
    "주상복합": 2,
    "근린생활시설": 3,
    "상업시설": 4,
    "유보형복합용지": 5,
    "자족복합용지": 6,
    "자족시설": 7,
    "업무시설": 8,
    "공원": 9,
    "녹지": 10,
    "공공공지": 11,
    "보행자전용도로": 12,
    # "상업시설2": 13,
    # "업무시설2": 14,
    "근생용지": 15,
    "교육시설": 16,
    "커뮤니티시설": 17
}

CODE_TO_TAG = {TAG_TO_CODE[tag]: tag for tag in TAG_TO_CODE}

NEARGREEN_TAGS = ["커뮤니티시설", "교육시설"]

def load_site_data(path):
    original_map = np.zeros((HEIGHT, WIDTH))
    area_map = np.zeros((HEIGHT, WIDTH))
    road_map = np.zeros((HEIGHT, WIDTH))
    road_area_map = np.zeros((HEIGHT, WIDTH))
    direction_masks = {
        "up": np.zeros((HEIGHT, WIDTH)),
        "down": np.zeros((HEIGHT, WIDTH)),
        "left": np.zeros((HEIGHT, WIDTH)),
        "right": np.zeros((HEIGHT, WIDTH))
    }

    with open(path, encoding="utf-8-sig") as f:
        f.readline()

        for line in f:
            key, _, _, tag, _, _, area, *_ = line.strip().split(",")

            if key[1] == "D":
                r = int(key[2:5])
                c = int(key[5:7])
                road_map[r, c] = -1
                road_area_map[r, c] = float(area)

                continue

            if key[1] == "N":
                r = int(key[2:5])
                c = int(key[5:7])

                if tag in NEARGREEN_TAGS:
                    original_map[r, c] = TAG_TO_CODE[tag]
                    area_map[r, c] = float(area)
            else:
                r = int(key[1:4])
                c = int(key[4:6])
                up, right, down, left = map(lambda x: 1 if x == "T" else 0, key[6:10])

                # if tag == "상업시설":
                #     tag += "1" if r < 40 else "2"
                # elif tag =="업무시설":
                #     tag += "1" if c < 40 else "2"

                original_map[r, c] = TAG_TO_CODE[tag]
                area_map[r, c] = float(area)
                direction_masks["up"][r, c] = up
                direction_masks["down"][r, c] = down
                direction_masks["left"][r, c] = left
                direction_masks["right"][r, c] = right

    for direction in direction_masks:
        direction_masks[direction] = direction_masks[direction].tolist()

    return original_map, area_map, road_map, road_area_map, direction_masks


SITE_CMAP = ListedColormap([
    "white",
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
    "magenta",
    "cyan",
    "skyblue"
])


def main():
    original_map, area_map, road_map, road_area_map, direction_masks = load_site_data("sub_og.csv")
    pure_original_map = original_map.copy()
    pure_original_map[original_map == 16] = 0
    pure_original_map[original_map == 17] = 0

    pure_new_map = np.loadtxt("D:/_swmm_results/2021-09-23_18-44-53/104/2.csv", delimiter=",")
    pure_new_map[pure_new_map == 13] = 4
    pure_new_map[pure_new_map == 14] = 8
    new_map = pure_new_map.copy()
    new_map[original_map == 16] = 16
    new_map[original_map == 17] = 17

    # area
    # original_areas = defaultdict(float)
    # new_areas = defaultdict(float)
    # for code in range(1, 18):
    #     original_areas[CODE_TO_TAG[code].strip("12")] += area_map[original_map == code].sum()
    # for code in range(1, 18):
    #     new_areas[CODE_TO_TAG[code].strip("12")] += area_map[new_map == code].sum()

    # for name in original_areas:
    #     print(name, original_areas[name], new_areas[name])

    # area_change_rate = {}
    # for name in original_areas:
    #     rate = (new_areas[name] - original_areas[name]) * 100 / original_areas[name]
    #     area_change_rate[name] = rate
    # print(area_change_rate)


    # cluster
    # original_grid = Grid(pure_original_map.tolist(), direction_masks=direction_masks)
    # print(original_grid.analyze_cluster()[1])

    # new_grid = Grid(pure_new_map.tolist(), direction_masks=direction_masks)
    # print(new_grid.analyze_cluster()[1])


    # # quite
    # new_map[new_map != 1] = 0
    # original_map[original_map != 1] = 0

    # # commercial, business
    # road_map[(original_map == 4) | (original_map == 13)] = 4
    # road_map[(original_map == 8) | (original_map == 14)] = 8

    # road_map[(new_map == 4) | (new_map == 13)] = 4
    # road_map[(new_map == 8) | (new_map == 14)] = 8

    # # road
    # road_map[original_map == 4] = 4
    # road_map[original_map == 5] = 5
    # road_map[original_map == 6] = 6
    # road_map[original_map == 7] = 7
    # road_map[original_map == 8] = 8

    # road_map[new_map == 4] = 4
    # road_map[new_map == 5] = 5
    # road_map[new_map == 6] = 6
    # road_map[new_map == 7] = 7
    # road_map[new_map == 8] = 8

    # green
    # mask = ((9 <= original_map) & (original_map <= 12)) | ((16 <= original_map) & (original_map <= 17))
    # original_map[~mask] = 0

    # mask = ((9 <= new_map) & (new_map <= 12)) | ((16 <= new_map) & (new_map <= 17))
    # new_map[~mask] = 0


    # mask = ((original_map == 1) | ((4 <= original_map) & (original_map <= 8)))
    # original_map[~mask] = 0

    # mask = ((new_map == 1) | ((4 <= new_map) & (new_map <= 8)))
    # new_map[~mask] = 0

    fig, ax = plt.subplots()
    img = ax.imshow(new_map, cmap=SITE_CMAP, vmin=-1, vmax=17)
    plt.colorbar(img)

    plt.show()


if __name__ == "__main__":
    main()
