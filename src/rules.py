# -*- coding: utf-8 -*-
from gridutils import count_neighbor, labeled_sum


class MagnetRule:

    def __str__(self):
        return "_".join(map(str, ["magnet", self._gene, self._label]))

    def __init__(self, gene, mask, ideal, goal, label):
        self._gene = gene
        self._mask = mask
        self._ideal = float(ideal)
        self._goal = float(goal)
        self._label = label

    def evaluate(self, genes, cluster_result):
        result = sum(all(self._mask[r][c] == 0 for r, c in cluster["neighbor_coords"])
                     for cluster in cluster_result[self._gene])
        return (result - self._ideal) / (self._goal - self._ideal)

    def weigh(self, genes, r, c, gene):
        return 1
        return 10 if gene == self._gene and count_neighbor(self._mask, r, c, [1]) > 0 else 1


class AreaMaxRule:

    def __str__(self):
        return "_".join(map(str, ["area_max", self._gene, "{:.4f}".format(self._maximum)]))

    def __init__(self, gene, maximum, area_map, factor):
        self._gene = gene
        self._area_map = area_map
        self._maximum = float(maximum)
        self._factor = float(factor)

    def evaluate(self, genes, cluster_result):
        return max(0., labeled_sum(genes, self._area_map)[self._gene] - self._maximum) / (0.09 * self._factor)

    def weigh(self, genes, r, c, gene, accumulated_areas):
        if gene != self._gene:
            return 1
        return (self._maximum - accumulated_areas[gene]) / float(self._maximum)


class AreaMinRule:

    def __str__(self):
        return "_".join(map(str, ["area_min", self._gene, "{:.4f}".format(self._minimum)]))

    def __init__(self, gene, minimum, area_map, factor):
        self._gene = gene
        self._area_map = area_map
        self._minimum = float(minimum)
        self._factor = float(factor)

    def evaluate(self, genes, cluster_result):
        return max(0., self._minimum - labeled_sum(genes, self._area_map)[self._gene]) / (0.09 * self._factor)

    def weigh(self, genes, r, c, gene, accumulated_areas):
        if gene != self._gene:
            return 1
        return 10 if accumulated_areas[gene] < self._minimum else 1


class ClusterSizeMinRule:

    def __str__(self):
        return "_".join(map(str, ["cluster_size_min", self._gene, self._minimum]))

    def __init__(self, gene, minimum):
        self._gene = gene
        self._minimum = minimum

    def evaluate(self, genes, cluster_result):
        if self._gene in cluster_result:
            minimum = min(cluster["count"] for cluster in cluster_result[self._gene])
        else:
            minimum = 0
        return max(0, self._minimum - minimum)

    def weigh(self, genes, r, c, gene):
        return 1


class ClusterCountMaxRule:

    def __str__(self):
        return "cluster_count_max_" + str(self._maximum)

    def __init__(self, maximum):
        self._maximum = maximum

    @property
    def maximum(self):
        return self._maximum

    def evaluate(self, genes, cluster_result):
        cluster_count = sum(len(clusters) for clusters in cluster_result.values())
        return max(0, cluster_count - self._maximum)

    def weigh(self, genes, r, c, gene):
        return 1


class AttractionRule:

    def __str__(self):
        return "_".join(map(str, ["attraction", self._from_gene, self._to_gene]))

    def __init__(self, from_gene, to_gene, ideal, goal):
        self._from_gene = from_gene
        self._to_gene = to_gene
        self._ideal = float(ideal)
        self._goal = float(goal)

    def evaluate(self, genes, cluster_result):
        cost = sum(all(genes[r][c] != self._to_gene for r, c in cluster["neighbor_coords"])
                   for cluster in cluster_result[self._from_gene])
        return (cost - self._ideal) / (self._goal - self._ideal)

    def weigh(self, genes, r, c, gene):
        return 1
        if gene == self._from_gene and count_neighbor(genes, r, c, [self._to_gene]) > 0:
            return 10
        else:
            return 1


class RepulsionRule:

    def __str__(self):
        return "_".join(map(str, ["repulsion", self._gene1, self._gene2]))

    def __init__(self, gene1, gene2, ideal, goal):
        self._gene1 = gene1
        self._gene2 = gene2
        self._ideal = float(ideal)
        self._goal = float(goal)

    def evaluate(self, genes, cluster_result):
        cost = 0
        for r, row in enumerate(genes):
            for c, e in enumerate(row):
                if e != self._gene1:
                    continue
                cost += count_neighbor(genes, r, c, [self._gene2])
        return (cost - self._ideal) / (self._goal - self._ideal)

    def weigh(self, genes, r, c, gene):
        return 1
        if gene == self._gene1 and count_neighbor(genes, r, c, [self._gene2]) > 0:
            return 0
        elif gene == self._gene2 and count_neighbor(genes, r, c, [self._gene1]) > 0:
            return 0
        else:
            return 1


def main():
    from collections import defaultdict
    from gridutils import analyze_cluster
    genes = [1, 2, 3]
    grid = [
        [0, 1, 2, 2],
        [1, 3, 1, 3],
        [1, 3, 1, 3],
        [0, 0, 2, 1]
        ]
    cluster_result = analyze_cluster(grid)
    mask = [
        [0, 0, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 0, 1],
        [0, 0, 0, 0]
        ]
    area_map = [
        [1, 1, 1, 1],
        [1, 1, 1, 1],
        [1, 1, 1, 1],
        [1, 1, 1, 1]
        ]
    accumulated_areas = defaultdict(float)
    accumulated_areas[1] += 6

    rule = MagnetRule(1, mask, 0, 1, "mask")
    print(rule, rule.evaluate(grid, cluster_result))
    print([rule.weigh(grid, 2, 2, gene) for gene in genes])

    rule = AreaMaxRule(1, 8, area_map)
    print(rule, rule.evaluate(grid, cluster_result))
    print([rule.weigh(grid, 2, 2, gene, accumulated_areas) for gene in genes])

    rule = AreaMinRule(1, 7, area_map)
    print(rule, rule.evaluate(grid, cluster_result))
    print([rule.weigh(grid, 2, 2, gene, accumulated_areas) for gene in genes])

    rule = ClusterSizeMinRule(1, 3)
    print(rule, rule.evaluate(grid, cluster_result))
    print([rule.weigh(grid, 2, 2, gene) for gene in genes])

    rule = ClusterCountMaxRule(5)
    print(rule, rule.evaluate(grid, cluster_result))
    print([rule.weigh(grid, 2, 2, gene) for gene in genes])

    rule = AttractionRule(1, 2, 0, 1)
    print(rule, rule.evaluate(grid, cluster_result))
    print([rule.weigh(grid, 2, 2, gene) for gene in genes])

    rule = RepulsionRule(1, 2, 0, 1)
    print(rule, rule.evaluate(grid, cluster_result))
    print([rule.weigh(grid, 2, 2, gene) for gene in genes])

if __name__ == "__main__":
    main()
