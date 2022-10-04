# -*- coding: utf-8 -*-
import random
from copy import deepcopy
from operator import attrgetter

from gridutils import (analyze_cluster, configure, count_neighbor, get_diff_coords,
                       get_neighbor_coords_include, grid_sum, labeled_sum, ones, zeros)
from logger import GALogger27
from mathutils import lerp
from randutils import choices, randpop
from rules import ClusterCountMaxRule


class Chromosome:

    def __init__(self, genes, gene_ruler):
        self._genes = genes
        self._height = len(genes)
        self._width = len(genes[0])
        self._gene_ruler = gene_ruler
        self._costs = None

    @property
    def genes(self):
        return self._genes

    @property
    def cost(self):
        return self.cost_detail["total"]

    @property
    def cost_detail(self):
        if self._costs is None:
            self._evaluate()
        return self._costs

    def crossover(self, partner):
        child_genes1 = deepcopy(self._genes)
        child_genes2 = deepcopy(self._genes)

        diff_coords = get_diff_coords(self._genes, partner._genes)
        for (gene1, gene2), coords in diff_coords.items():
            mask = zeros(self._height, self._width)
            for r, c in coords:
                mask[r][c] = 1
                child_genes1[r][c] = 0
                child_genes2[r][c] = 0
            self._gene_ruler.fill(child_genes1, mask, [gene1, gene2])
            self._gene_ruler.fill(child_genes2, mask, [gene1, gene2])
        return Chromosome(child_genes1, self._gene_ruler), Chromosome(child_genes2, self._gene_ruler)

    def mutate(self):
        region_height = self._height // 5
        region_width = self._width // 5
        r_start = random.randint(0, self._height - region_height)
        c_start = random.randint(0, self._width - region_width)
        region_mask = zeros(self._height, self._width)
        for r in range(r_start, r_start + region_height):
            for c in range(c_start, c_start + region_width):
                region_mask[r][c] = 1
                self.genes[r][c] = 0
        self._gene_ruler.fill(self.genes, region_mask)
        self._cost = None

    def _evaluate(self):
        self._costs = self._gene_ruler.evaluate(self._genes)


class GeneticAlgorithm:

    def __init__(self, gene_ruler):
        self._gene_ruler = gene_ruler

    def run(self, size=20, strategy="age", elitism=2, child_count=20,
            mutation_rate=0.05, stable_step_for_exit=20, is_logging=True):
        if is_logging:
            logger = GALogger27("D:/_swmm_results", "now", self._gene_ruler.rule_names)

        population = self._initialize(size)
        generation = 1

        print(generation, ">>>", [int(x.cost) for x in population])
        # print(population[0].cost_detail)

        if is_logging:
            for i, chromosome in enumerate(population):
                costs = [chromosome.cost_detail[rule_name] for rule_name in self._gene_ruler.rule_names]
                logger.log(generation, i, chromosome.genes, chromosome.cost, costs)

        best_cost = population[0].cost
        stable_step = 0
        while stable_step < stable_step_for_exit:
            if strategy == "age":
                population = self._age_based_step(population, elitism, mutation_rate)
            elif strategy == "cost":
                population = self._cost_based_step(population, child_count, mutation_rate)
            else:
                raise ValueError("undefine survivor strategy")
            generation += 1

            print(generation, ">>>", [int(x.cost) for x in population])
            # print(population[0].cost_detail)

            if is_logging:
                for i, chromosome in enumerate(population):
                    costs = [chromosome.cost_detail[rule_name] for rule_name in self._gene_ruler.rule_names]
                    logger.log(generation, i, chromosome.genes, chromosome.cost, costs)

            if population[0].cost == best_cost:
                stable_step += 1
            elif population[0].cost < best_cost:
                best_cost = population[0].cost
                stable_step = 0
            else:
                print("Warning: cost increased??")

        return population[0]

    def _initialize(self, size):
        result = [Chromosome(self._gene_ruler.generate(), self._gene_ruler) for _ in range(size)]
        result.sort(key=attrgetter("cost"))
        return result

    def _cost_based_step(self, population, chlid_count, mutation_rate):
        result = population[:]
        for _ in range(chlid_count // 2):
            result += self._reproduce_two_children(population, mutation_rate)
        result.sort(key=attrgetter("cost"))
        return result[:len(population)]

    def _age_based_step(self, population, elitism, mutation_rate):
        result = population[:elitism]
        while len(result) < len(population):
            result += self._reproduce_two_children(population, mutation_rate)
        result.sort(key=attrgetter("cost"))
        return result

    def _reproduce_two_children(self, population, mutation_rate):
        parent1 = choices(population, list(lerp(1, 0.2, len(population))))
        parent2 = choices(population, list(lerp(1, 0.2, len(population))))
        child1, child2 = parent1.crossover(parent2)

        if random.random() < mutation_rate:
            child1.mutate()
        if random.random() < mutation_rate:
            child2.mutate()
        return child1, child2


class GeneRuler:

    CLUSTER_COHESION = 8
    MARGINAL_PENALTY_FACTOR = 4

    def __init__(self, height, width, codes, mask=None, direction_vectors=None, area_map=None):
        self._height = height
        self._width = width
        self._codes = codes

        if mask is None:
            self._target_mask = ones(height, width)
        else:
            self._target_mask = mask

        self._cluster_size = 1
        self._rules = []
        self._area_rules = []
        self._submasks = {}

        if direction_vectors is not None:
            configure(direction_vectors)

        if area_map is None:
            self._area_map = ones(height, width)
        else:
            self._area_map = area_map

    @property
    def _cell_count(self):
        return grid_sum(self._target_mask)

    @property
    def rule_names(self):
        return [str(rule) for rule in self._rules + self._area_rules]

    def add_rule(self, rule):
        if isinstance(rule, ClusterCountMaxRule):
            self._cluster_size = self._cell_count // (rule.maximum * 0.75)
        self._rules.append(rule)

    def add_area_rule(self, rule):
        self._area_rules.append(rule)

    def add_submask(self, code, submask):
        self._submasks[code] = submask

    def evaluate(self, genes):
        result = {}
        cluster_result = analyze_cluster(genes)
        for rule in self._rules + self._area_rules:
            result[str(rule)] = rule.evaluate(genes, cluster_result) ** GeneRuler.MARGINAL_PENALTY_FACTOR
        result["total"] = sum(result.values())
        return result

    def generate(self):
        grid = zeros(self._height, self._width)
        return self.fill(grid, self._target_mask, self._codes)

    def fill(self, genes, mask, codes=None):
        if codes is None:
            codes = self._codes

        target_coords = [(r, c) for r in range(len(mask))
                                for c in range(len(mask[0]))
                                if mask[r][c] != 0]
        accumulated_areas = labeled_sum(genes, self._area_map)

        while True:
            if not target_coords:
                break

            r, c = randpop(target_coords)
            weights = [self._get_weight_at(genes, r, c, code, accumulated_areas) for code in codes]
            code = choices(codes, weights)
            genes, target_coords, accumulated_areas = self._fill_cluster(genes, target_coords, accumulated_areas, r, c, code, mask)
        return genes

    def _fill_cluster(self, grid, target_coords, accumulated_areas, r, c, code, mask):
        grid[r][c] = code
        accumulated_areas[code] += self._area_map[r][c]
        current_cluster_size = 1
        neighbor_coords = []
        while True:
            neighbor_coords += [(r, c) for r, c in get_neighbor_coords_include(grid, r, c, [0])
                                       if mask[r][c] == 1
                                          and self._target_mask[r][c] == 1
                                          and (r, c) not in neighbor_coords]

            if not neighbor_coords:
                return grid, target_coords, accumulated_areas

            if current_cluster_size >= self._cluster_size:
                break

            neighbor_weights = [self._get_weight_at(grid, r, c, code, accumulated_areas) for r, c in neighbor_coords]
            if sum(neighbor_weights) == 0:
                break

            r, c = randpop(neighbor_coords, neighbor_weights)
            target_coords.remove((r, c))
            grid[r][c] = code
            accumulated_areas[code] += self._area_map[r][c]
            current_cluster_size += 1

        # second phase
        while neighbor_coords:
            r, c = randpop(neighbor_coords)
            target_coords.remove((r, c))

            weights = [self._get_weight_at(grid, r, c, code, accumulated_areas) for code in self._codes]
            factored_weights = [weight * 1 if target_code == code else weight for weight, target_code in zip(weights, self._codes)]
            new_code = choices(self._codes, factored_weights)

            if code != new_code:
                code = new_code
                break

            grid[r][c] = code
            accumulated_areas[code] += self._area_map[r][c]
            neighbor_coords += [(r, c) for r, c in get_neighbor_coords_include(grid, r, c, [0])
                                       if mask[r][c] == 1
                                          and self._target_mask[r][c] == 1
                                          and (r, c) not in neighbor_coords]
        return self._fill_cluster(grid, target_coords, accumulated_areas, r, c, code, mask)

    def _get_weight_at(self, grid, r, c, code, accumulated_areas):
        if code in self._submasks and self._submasks[code][r][c] == 0:
            return 0

        weight = self.CLUSTER_COHESION ** count_neighbor(grid, r, c, [code])
        for rule in self._rules:
            weight *= rule.weigh(grid, r, c, code)
        for rule in self._area_rules:
            weight *= rule.weigh(grid, r, c, code, accumulated_areas)
        return weight


def main():
    from pprint import pp
    from rules import AreaMinRule, AreaMaxRule, AttractionRule, RepulsionRule
    area_map = ones(8, 8)
    ruler = GeneRuler(8, 8, [1, 2, 3, 4])
    ruler.add_area_rule(AreaMinRule(1, 10, area_map))
    ruler.add_area_rule(AreaMaxRule(1, 20, area_map))
    ruler.add_area_rule(AreaMinRule(2, 10, area_map))
    ruler.add_area_rule(AreaMaxRule(2, 20, area_map))
    ruler.add_area_rule(AreaMinRule(3, 10, area_map))
    ruler.add_area_rule(AreaMaxRule(3, 20, area_map))
    ruler.add_area_rule(AreaMinRule(4, 10, area_map))
    ruler.add_area_rule(AreaMaxRule(4, 20, area_map))
    ruler.add_rule(ClusterCountMaxRule(16))
    ruler.add_rule(RepulsionRule(1, 2, 0, 1))
    ruler.add_rule(RepulsionRule(1, 4, 0, 1))
    ruler.add_rule(RepulsionRule(2, 3, 0, 1))
    ruler.add_rule(RepulsionRule(3, 4, 0, 1))
    ruler.add_rule(AttractionRule(1, 3, 0, 1))
    ga = GeneticAlgorithm(ruler)
    best = ga.run(size=100, strategy="age", elitism=2, mutation_rate=0.9,
                  stable_step_for_exit=20, is_logging=False)
    pp(best.genes, width=40)


if __name__ == "__main__":
    main()
