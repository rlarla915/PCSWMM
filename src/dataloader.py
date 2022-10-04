# -*- coding: utf-8 -*-
import io
from collections import defaultdict

from gridutils import is_in, zeros


HEIGHT = 111
WIDTH = 71
TAG_TO_CODE = {
    "공동주택": 1,
    "주상복합": 2,
    "근린생활시설": 3,
    "상업시설1": 4,
    "유보형복합용지": 5,
    "자족복합용지": 6,
    "자족시설": 7,
    "업무시설1": 8,
    "공원": 9,
    "녹지": 10,
    "공공공지": 11,
    "보행자전용도로": 12,
    "상업시설2": 13,
    "업무시설2": 14,
    "근생용지": 15,
    }
CODE_TO_TAG = {TAG_TO_CODE[tag]: tag for tag in TAG_TO_CODE}
NEARGREEN_TAGS = [
    "커뮤니티시설",
    "교육시설"
    ]


def load_site_data(path):
    original_map = zeros(HEIGHT, WIDTH)
    mask = zeros(HEIGHT, WIDTH)
    area_map = zeros(HEIGHT, WIDTH)
    road_mask = zeros(HEIGHT, WIDTH)
    road_area_map = zeros(HEIGHT, WIDTH)
    neargreen_mask = zeros(HEIGHT, WIDTH)
    direction_vectors = defaultdict(list)
    original_areas = defaultdict(float)

    with io.open(path, encoding="utf-8-sig") as f:
        f.readline()

        for line in f:
            words = line.strip().split(",")
            key = words[0]
            tag = words[3]
            area = words[6]

            if key[1] == "D":
                r = int(key[2:5])
                c = int(key[5:7])
                road_mask[r][c] = 1
                road_area_map[r][c] = float(area)
                continue

            if key[1] == "N":
                r = int(key[2:5])
                c = int(key[5:7])
                if tag in NEARGREEN_TAGS:
                    neargreen_mask[r][c] = 1
            else:
                r = int(key[1:4])
                c = int(key[4:6])
                up, right, down, left = (truth == "T" for truth in key[6:10])

                if tag == "상업시설":
                    tag += "1" if r < 40 else "2"
                elif tag =="업무시설":
                    tag += "1" if c < 40 else "2"

                original_map[r][c] = TAG_TO_CODE[tag]
                mask[r][c] = 1
                area_map[r][c] = float(area)
                if up:
                    direction_vectors[r, c].append((-1, 0))
                if right:
                    direction_vectors[r, c].append((0, 1))
                if down:
                    direction_vectors[r, c].append((1, 0))
                if left:
                    direction_vectors[r, c].append((0, -1))
                original_areas[original_map[r][c]] += area_map[r][c]

    return (original_map, mask, area_map, road_mask, road_area_map,
           neargreen_mask, direction_vectors, original_areas)


def create_big_road_mask(road_area_map):
    big_road_mask = zeros(HEIGHT, WIDTH)
    for r in range(HEIGHT):
        for c in range(WIDTH):
            vectors = [(1, 0), (0, 1), (-1, 0), (0, -1)]
            coords = ((r + dr, c + dc) for dr, dc in vectors)
            total_area = sum([road_area_map[r][c] for r, c in coords if is_in(big_road_mask, r, c)])
            if total_area >= 0.14:
                big_road_mask[r][c] = 1
    return big_road_mask


def create_core_region_data(core, offset):
    core_mask = zeros(HEIGHT, WIDTH)
    region_mask = zeros(HEIGHT, WIDTH)
    core_mask[core[0]][core[1]] = 1
    for r in range(core[0] - offset[0], core[0] + offset[0] + 1):
        for c in range(core[1] - offset[1], core[1] + offset[1] + 1):
            region_mask[r][c] = 1
    return core_mask, region_mask


def create_quiet_region_mask(point1, point2):
    quiet_region_mask = zeros(HEIGHT, WIDTH)
    r1, c1 = point1
    r2, c2 = point2
    for r, row in enumerate(quiet_region_mask):
        for c, _ in enumerate(row):
            if (r2 - r1) * c + r1 * c2 <= (c2 - c1) * r + r2 * c1:
                quiet_region_mask[r][c] = 1
    return quiet_region_mask


def main():
    site_data = load_site_data("sub_og.csv")
    original_map = site_data[0]
    big_road_mask = create_big_road_mask(site_data[4])
    quiet_region_mask = create_quiet_region_mask((10, 10), (20, 20))
    core_mask, region_mask = create_core_region_data((30, 30), (2, 4))

    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    site_cmap = ListedColormap([
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
    plt.rc("image", cmap=site_cmap)
    plt.subplot(231)
    plt.imshow(original_map)
    plt.subplot(232)
    plt.imshow(big_road_mask)
    plt.subplot(233)
    plt.imshow(quiet_region_mask)
    plt.subplot(234)
    plt.imshow(core_mask)
    plt.subplot(235)
    plt.imshow(region_mask)
    plt.show()


if __name__ == "__main__":
    main()
