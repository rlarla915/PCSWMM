# -*- coding: utf-8 -*-
# subcatchments = pcpy.SWMM.Subcatchments
import random
import collections
import copy
import math

Subcatchment = collections.namedtuple("Subcatchment", ["Area"])

def read_subcatchments():
    result = {}

    with open("sub_og.csv") as f:
        f.readline()

        for line in f:
            key, _, _, _, _, _, _, area, *_ = line.strip().split(',')
            result[key] = Subcatchment(float(area))

    return result

subcatchments = read_subcatchments()


def create_grid(height, width, value):
    return [[value] * width for _ in range(height)]

whole_map = create_grid(111, 71, None)
map_direction = create_grid(111, 71, "")

for key in subcatchments.keys():
    if key[1] != 'D' and key[1] != 'N':
        tmp_x = int(key[1:4])
        tmp_y = int(key[4:6])
        tmp_dir = key[6:10]
        map_direction[tmp_x][tmp_y] = tmp_dir
        whole_map[tmp_x][tmp_y] = subcatchments[key]




max_subcatch_dict = {
    "공동주택": 63.924,
    "주상복합": 14.3891,
    "근린생활시설": 3.99112,
    "상업시설": 2.98405,
    "유보형복합용지": 8.28045,
    "자족복합용지": 13.2233,
    "자족시설": 62.2402,
    "업무시설": 1.75321,
    "공원": 51.1226,
    "녹지": 12.1783,
    "공공공지": 2.56442,
    "보행자전용도로": 2.01097,
}
rate_subcatch_dict = {
    "공동주택": 798,
    "주상복합": 173,
    "근린생활시설": 69,
    "상업시설": 37,
    "유보형복합용지": 112,
    "자족복합용지": 193,
    "자족시설": 925,
    "업무시설": 24,
    "공원": 766,
    "녹지": 316,
    "공공공지": 32,
    "보행자전용도로": 26,
}  # 애 비율 바꾸고 싶으면 바꿔도 됨.
imperv = {
    "공동주택": 0.65,
    "주상복합": 1,
    "근린생활시설": 0.9,
    "상업시설": 1,
    "유보형복합용지": 0.85,
    "자족복합용지": 0.85,
    "자족시설": 0.85,
    "업무시설": 0.85,
    "공원": 0.15,
    "녹지": 0,
    "공공공지": 0.6,
    "보행자전용도로": 1,
}
greenroof = {
    "공동주택": 0.05,
    "주상복합": 0.1,
    "근린생활시설": 0.1,
    "상업시설": 0.1,
    "유보형복합용지": 0.35,
    "자족복합용지": 0,
    "자족시설": 0.25,
    "업무시설": 0,
    "공원": 0,
    "녹지": 0,
    "공공공지": 0,
    "보행자전용도로": 0,
}
pavement = {
    "공동주택": 0.1,
    "주상복합": 0.2,
    "근린생활시설": 0.1,
    "상업시설": 0.1,
    "유보형복합용지": 0.25,
    "자족복합용지": 0.25,
    "자족시설": 0.25,
    "업무시설": 0.15,
    "공원": 0.05,
    "녹지": 0,
    "공공공지": 0.6,
    "보행자전용도로": 1,
}

max_subcatch = list(max_subcatch_dict.values())
weights = list(rate_subcatch_dict.values())


def choices(arr, weights):
    weighted_arr = []
    for elm, weight in zip(arr, weights):
        weighted_arr += [elm] * weight

    return random.choice(weighted_arr)

class Chromosome:

    def __init__(self, genes):
        self._genes = genes
        self._num_cluster = 0
        self._score = 100
        self._tag_areas = [0] * 12

    def first_generation(self):
        for i in range(111):
            for j in range(71):
                self._count = 0
                self.make_first_gene(i, j, -1)
        # print(self._num_cluster)

    def make_first_gene(self, x, y, parent_tag):
        if map_direction[x][y] == "":
            return

        if self._genes[x][y] != -1:
            return

        if self._count % 8 == 0: # 여기에 있는 숫자 8을 바꾸면 처음 만들 때 묶음 수를 바꿀 수 있음. 커질수록 클러스터 단위가 커짐.
            target_tags = [i for i in range(12) if max_subcatch[i] >= self._tag_areas[i]]
            target_weights = [weights[i] for i in range(12) if max_subcatch[i] >= self._tag_areas[i]]
            tmp_tag = random.choices(target_tags, weights=target_weights)[0]

            if tmp_tag != parent_tag:
                self._count = 0
                self._num_cluster = self._num_cluster + 1

            cur_tag = tmp_tag
        else:
            cur_tag = parent_tag

        self._count = self._count + 1
        self._genes[x][y] = cur_tag
        self._tag_areas[cur_tag] += whole_map[x][y].Area

        random_direction = [0, 1, 2, 3]
        random.shuffle(random_direction)

        for i in random_direction:
            if i == 0 and map_direction[x][y][0]== 'T' and x > 0:
                self.make_first_gene(x-1, y, cur_tag)
            if i == 1 and map_direction[x][y][2]== 'T' and x < 110:
                self.make_first_gene(x+1, y, cur_tag)
            if i == 2 and map_direction[x][y][1]== 'T' and y > 0:
                self.make_first_gene(x, y-1, cur_tag)
            if i == 3 and map_direction[x][y][3]== 'T' and y < 70:
                self.make_first_gene(x, y+1, cur_tag)

    def crossover1(self, second):
        first_genes = copy.deepcopy(self._genes)
        second_genes = copy.deepcopy(second._genes)

        for i in range(56):
            for j in range(71):
                first_genes[i][j] = second._genes[i][j]
                second_genes[i][j] = self._genes[i][j]

        child1 = Chromosome(first_genes)
        child2 = Chromosome(second_genes)
        random.random()

        return child1, child2

    def crossover2(self, second):
        first_genes = copy.deepcopy(self._genes)
        second_genes = copy.deepcopy(second._genes)

        for i in range(111):
            for j in range(36):
                first_genes[i][j] = second._genes[i][j]
                second_genes[i][j] = self._genes[i][j]

        child1 = Chromosome(first_genes)
        child2 = Chromosome(second_genes)

        return child1, child2

    def mutate(self, length, mutation_rate):
        if random.random() > mutation_rate:
            return

        x1 = random.randint(0, 110 - length)
        y1 = random.randint(0, 70 - length)
        x2 = random.randint(0, 110 - length)
        y2 = random.randint(0, 70 - length)

        tmp1 = [self._genes[x1 + i][y1:y1 + length] for i in range(length)]
        tmp2 = [self._genes[x2 + i][y2:y2 + length] for i in range(length)]

        for i in range(length):
            for j in range(length):
                if self._genes[x1 + i][y1 + j] != -1 and tmp2[i][j] != -1:
                    self._genes[x1 + i][y1 + j] = tmp2[i][j]

                if self._genes[x2 + i][y2 + j] != -1 and tmp1[i][j] != -1:
                    self._genes[x2 + i][y2 + j] = tmp1[i][j]

    def cluster(self):
        self._cluster_array = create_grid(111, 71, -1)

        for i in range(111):
            for j in range(71):
                self.count_cluster(i, j, -1)

        return self._num_cluster

    def count_cluster(self, x, y, parent_tag):
        tag = self._genes[x][y]

        if map_direction[x][y] == "":
            return

        if self._cluster_array[x][y] != -1:
            return

        self._cluster_array[x][y] = tag

        if parent_tag == -1:
            self._num_cluster = self._num_cluster + 1
            parent_tag = tag

        if tag == parent_tag:
            if map_direction[x][y][0] == 'T' and x > 0:
                self.count_cluster(x - 1, y, parent_tag)

            if map_direction[x][y][2] == 'T' and x < 110:
                self.count_cluster(x + 1, y, parent_tag)

            if map_direction[x][y][1] == 'T' and y > 0:
                self.count_cluster(x, y - 1, parent_tag)

            if map_direction[x][y][3] == 'T' and y < 70:
                self.count_cluster(x, y + 1, parent_tag)

    def update_tag_areas(self):
        self._tag_areas = [0] * 12

        for i in range(111):
            for j in range(71):
                if self._genes[i][j] != -1:
                    self._tag_areas[self._genes[i][j]] += whole_map[i][j].Area

    def rate_fitness(self, x):
        self.update_tag_areas()

        upper_bounds = [area * (1 + x) for area in max_subcatch]
        lower_bounds = [area * (1 - x) for area in max_subcatch]

        is_in_ranges = [lower <= area <= upper for upper, area, lower in zip(upper_bounds, self._tag_areas, lower_bounds)]

        # print("out of ranges", is_in_ranges.count(False))

        return all(is_in_ranges)

    def update_score(self):
        # global imperv, greenroof, pavement

        # for x in range(111):
        #     for y in range(71):
        #         tmp_subcatchment = whole_map[x][y]

        #         if tmp_subcatchment is None:
        #             continue

        #         if self._genes[x][y] == "":
        #             continue

        #         tmp_subcatchment.Tag = self._genes[x][y]
        #         tmp_subcatchment.ImpervPercent = imperv[tmp_subcatchment.Tag] * 100
        #         lids = tmp_subcatchment.LIDUsages
        #         lids['GreenRoof_2'].AreaOfEachUnit = tmp_subcatchment.Area * 10000 * greenroof[tmp_subcatchment.Tag]
        #         lids['GreenRoof_2'].SurfaceWidth = math.sqrt(lids['GreenRoof_2'].AreaOfEachUnit)
        #         lids['pavement_2'].AreaOfEachUnit = tmp_subcatchment.Area * 10000 * pavement[tmp_subcatchment.Tag]
        #         lids['pavement_2'].SurfaceWidth = math.sqrt(lids['pavement_2'].AreaOfEachUnit)

        # pcpy.SWMM.run()
        # report_file = pcpy.Graph.Files[0]
        # func = report_file.get_function('Runoff', 'm3/s', 'System')
        # tmp_loc = func.get_location('System')
        # tmp_obj = tmp_loc.get_objective_function(0, 0)
        # self._score = tmp_obj.Total


        self._score = sum([sum(row) for row in self._genes])


class GeneticAlgorithm:

    def __init__(self, population):
        self._population = population
        self._chromosomes = []

    def run(self, best_case=4, generation=100, mutation_rate=0.1):
        for i in range(self._population):
            tmp_chromosome = Chromosome(create_grid(111, 71, -1))
            tmp_chromosome.first_generation()
            tmp_chromosome.update_score()
            self._chromosomes.append(tmp_chromosome)

        self._chromosomes.sort(key=lambda x: x._score, reverse=False)

        print(f"----------- initial -----------")
        print(f"initial best: {self._chromosomes[0]._score}")
        print([ch._score for ch in self._chromosomes])
        save_list(f"initial.csv", self._chromosomes[0]._genes)

        for i in range(generation):
            print(f"----------- step {i} -----------")

            self._step(best_case, mutation_rate)

            print([ch._score for ch in self._chromosomes])
            save_list(f"step{i}.csv", self._chromosomes[0]._genes)

        print("best : " + str(self._chromosomes[0]._score))

        self._chromosomes[0].update_score()

    def _step(self, best_case, mutation_rate):
        next_chromosome_arr = []

        for i in range(best_case):
            next_chromosome_arr.append(self._chromosomes[i])

        count = 0
        hit = 0
        for i in range(len(self._chromosomes) - 1):
            # print(i)
            for j in range(i + 1, len(self._chromosomes)):
                children = []
                children.extend(self._chromosomes[i].crossover1(self._chromosomes[j]))
                children.extend(self._chromosomes[i].crossover2(self._chromosomes[j]))

                for child in children:
                    child.mutate(3, mutation_rate)

                # 비율 바꾸려면 아래에 있는 rate_fitness 안에 숫자를 바꾸면 됨 현재는 30%여서 0.3인 것.
                # 클러스터 수를 좀 더 타이트하게 가져가고 싶으면 아래에 있는 450이라는 숫자를 4개 전부 바꾸면 됨.
                # 450개 보다 작은 것만 통과시키게 만든거라, 작아질 수록 전체 클러스터 수가 적은 자식만 도출됨.
                # 대신 너무 작으면 자식이 잘 나오지 않음.
                for child in children:
                    if child.rate_fitness(0.15) and child.cluster() < 500:
                        child.update_score()
                        next_chromosome_arr.append(child)
                        count = count + 1
                        hit += 1

                if count >= self._population:
                    break

            if count >= self._population:
                break

        next_chromosome_arr.sort(key=lambda x: x._score, reverse=False)
        self._chromosomes = next_chromosome_arr
        print(f"{hit} hits")
        print("length : " + str(len(self._chromosomes)))

        if len(self._chromosomes) < self._population:
            print("population decrease!!")

        print("local best : " + str(self._chromosomes[0]._score))


def save_list(path, data):
    with open(path, "w") as f:
        for line in data:
            f.write(",".join(map(str, line)) + "\n")


def main():
    # ga = GeneticAlgorithm(population=20)
    # ga.run(best_case=6, generation=5, mutation_rate=0.05)

    with open("d:/galu.csv", "w", encoding="utf-8-sig") as f:
        f.write("tag,max_area,count,imperv,greenroof,pavement\n")
        for tag in max_subcatch_dict:
            words = []
            words.append(tag)
            words.append(max_subcatch_dict[tag])
            words.append(rate_subcatch_dict[tag])
            words.append(imperv[tag])
            words.append(greenroof[tag])
            words.append(pavement[tag])
            f.write(",".join(map(str, words)) + "\n")



if __name__ == "__main__":
    main()
