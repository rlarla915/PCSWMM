import pathlib
import numpy as np
from main import load_site_data
from ga2d import Grid


original_map, mask, area_map, road_mask, road_area_map, neargreen_mask, direction_masks, original_areas = load_site_data("sub_og.csv")

area_map = Grid(area_map)

og_areas = area_map.masked_sum(Grid(original_map))
print(og_areas)


home_areas = {}
path = pathlib.Path("D:/_swmm_results/2021-09-23_18-44-53")
for directory in path.iterdir():
    if not directory.is_dir():
        continue

    generation = directory.name
    print(generation)

    for csv in directory.iterdir():
        ranking = csv.stem
        genes = np.loadtxt(csv, delimiter=",")
        grid = Grid(genes.tolist())

        areas = area_map.masked_sum(grid)
        home_areas[int(generation), int(ranking)] = areas[1]


with open("area_result.csv", "w") as f:
    f.write("generation,ranking,house_area,area_change_rate\n")
    for (generation, ranking), home_area in sorted(home_areas.items()):
        f.write(",".join(map(str, [generation, ranking, home_area, (home_area - og_areas[1]) / og_areas[1]])) + "\n")

