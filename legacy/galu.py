import copy
import matplotlib.pyplot as plt
import numpy as np
import random
from matplotlib.colors import ListedColormap


max_areas = {
    1: 63.924,
    2: 14.3891,
    3: 3.99112,
    5: 8.28045,
    6: 13.2233,
    7: 62.2402,
    9: 51.1226,
    10: 12.1783,
    11: 2.56442,
    12: 2.01097,
}
max_areas = {code: max_areas[code] * 1.2 for code in max_areas}


def choices(candidates, weights):
    normalized_weights = [weight / sum(weights) for weight in weights]
    accumulated_weights = [sum(normalized_weights[:i + 1]) for i in range(len(weights))]

    offset = random.random()
    for candidate, weight in zip(candidates, accumulated_weights):
        if offset <= weight:
            return candidate


class Chromosome:

    def __init__(self, base_map, is_random=True):
        self._genes = create_map()

        accumulated_areas = {code: 1 for code in max_areas}


        target_coords = base_map.target_coords
        weight_map = base_map.weight_map

        random.shuffle(target_coords)
        while target_coords:
            r, c = target_coords.pop(0)

            area_factors = [(max_areas[code] - accumulated_areas[code]) / max_areas[code] for code in max_areas]
            factored_weights = [factor * weight for factor, weight in zip(area_factors, weight_map[r, c].values())]

            chosen_code = choices(weight_map[r, c].keys(), factored_weights)
            self._genes[r][c] = chosen_code
            accumulated_areas[chosen_code] += base_map.get_area(r, c)

        print(accumulated_areas)


    def crossover(self):
        pass

    def mutate(self):
        pass

    def draw(self):
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

        fig, ax = plt.subplots()
        img = ax.imshow(self._genes, cmap=cmap, vmin=0, vmax=14)
        fig.colorbar(img)
        plt.show()


class GeneticAlgorithm:

    def __init__(self):
        pass

    def run(self):
        # init()
        # while condition:
        #   step()
        pass

    def _step(self):
        # select()
        # crossover()
        # mutate()
        pass


def create_map(height=111, width=71, initial=0):
    return [[initial] * width for _ in range(height)]


tag_to_code = {
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
    "교육시설": 13,
    "커뮤니티시설": 14
}

target_codes = [
    1, 2, 3, 5, 6, 7, 9, 10, 11, 12
]


class BaseMap:

    def __init__(self):
        self._original_map = create_map()
        self._area_map = create_map()
        self._road_map = create_map()
        self._big_road_map = create_map()
        self._road_area_map = create_map()
        self._up_map = create_map()
        self._down_map = create_map()
        self._left_map = create_map()
        self._right_map = create_map()
        self._target_coords = []

        with open("sub_og.csv") as f:
            f.readline()

            for line in f:
                key, _, _, tag, _, _, _, area, *_ = line.strip().split(",")

                if key[1] == "D":
                    r = int(key[2:5])
                    c = int(key[5:7])
                    self._road_map[r][c] = 1
                    self._road_area_map[r][c] = float(area)
                    continue

                if key[1] == "N":
                    r = int(key[2:5])
                    c = int(key[5:7])
                    up = right = down = left = 0
                else:
                    r = int(key[1:4])
                    c = int(key[4:6])
                    up, right, down, left = map(lambda x: 1 if x == "T" else 0, key[6:10])

                code = tag_to_code.get(tag, 0)
                self._original_map[r][c] = code

                if code in target_codes:
                    self._target_coords.append((r, c))

                self._area_map[r][c] = float(area)
                self._up_map[r][c] = up
                self._down_map[r][c] = down
                self._left_map[r][c] = left
                self._right_map[r][c] = right

        for r in range(111):
            for c in range(71):
                connected_areas = []

                for dr, dc in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                    if self._is_valid_coord(r + dr, c + dc):
                        connected_areas.append(self._road_area_map[r + dr][c + dc] + self._road_area_map[r][c])

                if any(True if area > 0.14 else False for area in connected_areas):
                    self._big_road_map[r][c] = 1


        self._weight_map = {}
        for coord in self._target_coords:
            self._weight_map[coord] = {
                1: 1,
                2: 1,
                3: 1,
                5: 1,
                6: 1,
                7: 1,
                9: 1,
                10: 1,
                11: 1,
                12: 1
            }

            for code in self._weight_map[coord]:
                if code in [5, 6, 7]:
                    self._weight_map[coord][code] *= 20 if self._is_near_big_road(*coord) else 1

                if code in [9, 10, 11, 12]:
                    self._weight_map[coord][code] *= 20 if self._is_near_school_or_community(*coord) else 1

                if code in [1]:
                    self._weight_map[coord][code] *= 0 if self._is_near_office(*coord) else 1

    @property
    def target_coords(self):
        return self._target_coords.copy()

    @property
    def weight_map(self):
        return copy.deepcopy(self._weight_map)

    def get_area(self, r, c):
        return self._area_map[r][c]

    def _is_near_big_road(self, r, c):
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            if not self._is_valid_coord(r + dr, c + dc):
                continue

            if self._big_road_map[r + dr][c + dc]:
                return True

        return False

    def _is_near_school_or_community(self, r, c):
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            if not self._is_valid_coord(r + dr, c + dc):
                continue

            if self._original_map[r + dr][c + dc] in [13, 14]:
                return True

        return False

    def _is_near_office(self, r, c):
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            if not self._is_valid_coord(r + dr, c + dc):
                continue

            if self._original_map[r + dr][c + dc] in [4, 5, 6, 7, 8]:
                return True

        return False

    def _is_valid_coord(self, r, c):
        if r < 0 or c < 0:
            return False

        if r >= 111 or c >= 71:
            return False

        return True

    def draw(self):
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

        fig, axs = plt.subplots(2, 2)

        # axs[0, 0].imshow(np.array(self._original_map) == 0, cmap=cmap, vmin=0, vmax=14)
        # axs[0, 1].imshow(self._area_map)
        # axs[1, 0].imshow(self._big_road_map)



        axs[0, 0].imshow(np.array(self._road_area_map) > 0.045)
        axs[0, 1].imshow(np.array(self._road_area_map) > 0.05)
        axs[1, 0].imshow(np.array(self._road_area_map) > 0.055)
        axs[1, 1].imshow(np.array(self._road_area_map) > 0.06)





        # axs[0, 2].pcolormesh(self._up_map)
        # axs[1, 0].pcolormesh(self._down_map)
        # axs[1, 1].pcolormesh(self._left_map)
        # axs[1, 2].pcolormesh(self._right_map)

        # fig.colorbar(img)
        plt.show()


from collections import defaultdict

class Chromosome2:

    def __init__(self, genes):
        self._genes = genes

    def crossover(self, partner):
        child_genes1 = copy.deepcopy(self._genes)
        child_genes2 = copy.deepcopy(self._genes)

        diff_coords = self._get_diff_coords(self._genes, partner._genes)

        for (gene1, gene2), coords in diff_coords.items():
            if random.randint(0, 1):
                coords.reverse()

            for r, c in coords[:len(coords) // 2]:
                child_genes1[r][c] = gene1
                child_genes2[r][c] = gene2

            for r, c in coords[len(coords) // 2:]:
                child_genes1[r][c] = gene2
                child_genes2[r][c] = gene1

        return Chromosome2(child_genes1), Chromosome2(child_genes2)

    def _get_diff_coords(self, genes1, genes2):
        result = defaultdict(list)

        for r in range(len(genes1)):
            for c in range(len(genes1[0])):
                if not genes1[r][c] or not genes2[r][c]:
                    continue

                if genes1[r][c] != genes2[r][c]:
                    result[frozenset([genes1[r][c], genes2[r][c]])].append((r, c))

        return result

    def __str__(self):
        lines = ["[" + " ".join(map(str, line)) + "]" for line in self._genes]
        aligned_lines = [" " + lines[i] if i else "[" + lines[i] for i in range(len(lines))]

        return "\n".join(aligned_lines) + "]"

def main():
    ch1 = Chromosome2([
        [0, 1, 3, 2],
        [3, 1, 2, 1],
        [2, 3, 2, 2],
        [2, 3, 1, 0]
    ])
    ch2 = Chromosome2([
        [0, 2, 2, 3],
        [1, 2, 2, 3],
        [1, 1, 3, 3],
        [3, 3, 3, 0]
    ])
    child1, child2 = ch1.crossover(ch2)
    print(ch1)
    print(ch2)
    print(child1)
    print(child2)


    base_map = BaseMap()

    # chromosome = Chromosome(base_map)

    # chromosome.draw()
    base_map.draw()





if __name__ == "__main__":
    main()
