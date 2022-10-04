# -*- coding: utf-8 -*-
from dataloader import CODE_TO_TAG, HEIGHT, WIDTH


class RunoffRule:

    def __str__(self):
        return "total_runoff"

    def __init__(self, ideal, goal):
        self._ideal = float(ideal)
        self._goal = float(goal)
        self._swmm_runner = SwmmRunner()

    def evaluate(self, genes, cluster_result):
        total_runoff = self._swmm_runner.calc_total_runoff(genes)
        return (total_runoff - self._ideal) / (self._goal - self._ideal)

    def weigh(self, genes, r, c, gene):
        return 1


class SwmmRunner:

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
        "근생용지": 0
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
        "근생용지": 0.2
        }

    impervs = {
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
        "근생용지": 1
        }

    def __init__(self):
        self._subcatchment_map = [[None] * WIDTH for _ in range(HEIGHT)]
        for name, subcatchment in pcpy.SWMM.Subcatchments.items():
            if name[1] == 'D' or name[1] == 'N':
                continue
            r = int(name[1:4])
            c = int(name[4:6])
            self._subcatchment_map[r][c] = subcatchment

    def calc_total_runoff(self, genes):
        for subcatchment_row, gene_row in zip(self._subcatchment_map, genes):
            for subcatchment, gene in zip(subcatchment_row, gene_row):
                if subcatchment is None:
                    continue
                subcatchment.Tag = CODE_TO_TAG[gene].strip("12")
                subcatchment.ImpervPercent = self.impervs[subcatchment.Tag] * 100
                lids = subcatchment.LIDUsages
                lids["GreenRoof_2"].AreaOfEachUnit = subcatchment.Area * 10000 * self.greenroof[subcatchment.Tag]
                lids["GreenRoof_2"].SurfaceWidth = lids["GreenRoof_2"].AreaOfEachUnit ** 0.5
                lids["pavement_2"].AreaOfEachUnit = subcatchment.Area * 10000 * self.pavement[subcatchment.Tag]
                lids["pavement_2"].SurfaceWidth = lids["pavement_2"].AreaOfEachUnit ** 0.5
        pcpy.SWMM.run()
        report_file = pcpy.Graph.Files[0]
        runoff = report_file.get_function("Runoff", "m3/s", "System")
        location = runoff.get_location("System")
        objective = location.get_objective_function(0, 0)
        return objective.Total


def load(path):
    with open(path) as f:
        genes = [[int(x) for x in line.split(",")] for line in f]
    runner = SwmmRunner()
    result = runner.calc_total_runoff(genes)
    print(result)


ORIGINAL_PATH = "D:/dev/uos/swmm/original.csv"


#load(ORIGINAL_PATH)