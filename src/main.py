# -*- coding: utf-8 -*-
from dataloader import (create_big_road_mask, create_core_region_data, create_quiet_region_mask,
                        load_site_data, HEIGHT, TAG_TO_CODE, WIDTH)
from ga2d import GeneticAlgorithm, GeneRuler
from pprint import pprint
from rules import (AreaMaxRule, AreaMinRule, AttractionRule,
                   ClusterCountMaxRule, MagnetRule, RepulsionRule)
from swmm import RunoffRule


SUB_OG_PATH = "D:/dev/uos/swmm/sub_og.csv"


COMMERCIAL_CORE1 = (13, 52)
COMMERCIAL_CORE_OFFSET1 = (3, 4)
COMMERCIAL_CORE2 = (68, 48)
COMMERCIAL_CORE_OFFSET2 = (7, 7)

BUSINESS_CORE1 = (72, 32)
BUSINESS_CORE_OFFSET1 = (2, 2)
BUSINESS_CORE2 = (80, 42)
BUSINESS_CORE_OFFSET2 = (5, 5)

QUIET_DIVIDE_POINT1 = (43, 53)
QUIET_DIVIDE_POINT2 = (48, 67)


_, mask, area_map, _, road_area_map, neargreen_mask, direction_vectors, original_areas = load_site_data(SUB_OG_PATH)
big_road_mask = create_big_road_mask(road_area_map)
quiet_region_mask = create_quiet_region_mask(QUIET_DIVIDE_POINT1, QUIET_DIVIDE_POINT2)
commercial_core_mask1, commercial_region_mask1 = create_core_region_data(COMMERCIAL_CORE1, COMMERCIAL_CORE_OFFSET1)
commercial_core_mask2, commercial_region_mask2 = create_core_region_data(COMMERCIAL_CORE2, COMMERCIAL_CORE_OFFSET2)
business_core_mask1, business_region_mask1 = create_core_region_data(BUSINESS_CORE1, BUSINESS_CORE_OFFSET1)
business_core_mask2, business_region_mask2 = create_core_region_data(BUSINESS_CORE2, BUSINESS_CORE_OFFSET2)

ruler = GeneRuler(HEIGHT, WIDTH, list(range(1, 16)), mask, direction_vectors, area_map)

# condition 0
ruler.add_rule(ClusterCountMaxRule(250))
ruler.add_area_rule(AreaMinRule(TAG_TO_CODE["공동주택"], original_areas[TAG_TO_CODE["공동주택"]], area_map, 0.01))
ruler.add_area_rule(AreaMaxRule(TAG_TO_CODE["공동주택"], original_areas[TAG_TO_CODE["공동주택"]] * 1.2, area_map, 0.01))

# condition 1
ruler.add_submask(TAG_TO_CODE["상업시설1"], commercial_region_mask1)
ruler.add_submask(TAG_TO_CODE["상업시설2"], commercial_region_mask2)
ruler.add_submask(TAG_TO_CODE["업무시설1"], business_region_mask1)
ruler.add_submask(TAG_TO_CODE["업무시설2"], business_region_mask2)

ruler.add_rule(MagnetRule(TAG_TO_CODE["상업시설1"], commercial_core_mask1, 0, 0.01, "commercial_core1"))
ruler.add_rule(MagnetRule(TAG_TO_CODE["상업시설2"], commercial_core_mask2, 0, 0.01, "commercial_core2"))
ruler.add_rule(MagnetRule(TAG_TO_CODE["업무시설1"], business_core_mask1, 0, 0.01, "business_core1"))
ruler.add_rule(MagnetRule(TAG_TO_CODE["업무시설2"], business_core_mask2, 0, 0.01, "business_core2"))

ruler.add_area_rule(AreaMinRule(TAG_TO_CODE["상업시설1"], original_areas[TAG_TO_CODE["상업시설1"]] * 0.8, area_map, 0.01))
ruler.add_area_rule(AreaMaxRule(TAG_TO_CODE["상업시설1"], original_areas[TAG_TO_CODE["상업시설1"]] * 1.2, area_map, 0.01))

ruler.add_area_rule(AreaMinRule(TAG_TO_CODE["상업시설2"], original_areas[TAG_TO_CODE["상업시설2"]] * 0.8, area_map, 0.01))
ruler.add_area_rule(AreaMaxRule(TAG_TO_CODE["상업시설2"], original_areas[TAG_TO_CODE["상업시설2"]] * 1.2, area_map, 0.01))

ruler.add_area_rule(AreaMinRule(TAG_TO_CODE["업무시설1"], original_areas[TAG_TO_CODE["업무시설1"]] * 0.8, area_map, 0.01))
ruler.add_area_rule(AreaMaxRule(TAG_TO_CODE["업무시설1"], original_areas[TAG_TO_CODE["업무시설1"]] * 1.2, area_map, 0.01))

ruler.add_area_rule(AreaMinRule(TAG_TO_CODE["업무시설2"], original_areas[TAG_TO_CODE["업무시설2"]] * 0.8, area_map, 0.01))
ruler.add_area_rule(AreaMaxRule(TAG_TO_CODE["업무시설2"], original_areas[TAG_TO_CODE["업무시설2"]] * 1.2, area_map, 0.01))

# condition 2
ruler.add_submask(TAG_TO_CODE["공동주택"], quiet_region_mask)

# condition 3
ruler.add_rule(MagnetRule(TAG_TO_CODE["상업시설1"], big_road_mask, 0, 1, "big_road"))
ruler.add_rule(MagnetRule(TAG_TO_CODE["상업시설2"], big_road_mask, 0, 1, "big_road"))
ruler.add_rule(MagnetRule(TAG_TO_CODE["업무시설1"], big_road_mask, 0, 1, "big_road"))
ruler.add_rule(MagnetRule(TAG_TO_CODE["업무시설2"], big_road_mask, 0, 1, "big_road"))
ruler.add_rule(MagnetRule(TAG_TO_CODE["유보형복합용지"], big_road_mask, 0, 1, "big_road"))
ruler.add_rule(MagnetRule(TAG_TO_CODE["자족복합용지"], big_road_mask, 0, 1, "big_road"))
ruler.add_rule(MagnetRule(TAG_TO_CODE["자족시설"], big_road_mask, 0, 1, "big_road"))

# condition 4 & 5
ruler.add_rule(MagnetRule(TAG_TO_CODE["녹지"], neargreen_mask, 0, 1, "school_community"))
ruler.add_rule(AttractionRule(TAG_TO_CODE["공원"], TAG_TO_CODE["녹지"], 0, 1))
ruler.add_rule(AttractionRule(TAG_TO_CODE["공공공지"], TAG_TO_CODE["녹지"], 0, 1))
ruler.add_rule(AttractionRule(TAG_TO_CODE["보행자전용도로"], TAG_TO_CODE["녹지"], 0, 1))

# condition 6
ruler.add_rule(RepulsionRule(TAG_TO_CODE["공동주택"], TAG_TO_CODE["상업시설1"], 0, 1))
ruler.add_rule(RepulsionRule(TAG_TO_CODE["공동주택"], TAG_TO_CODE["상업시설2"], 0, 1))
ruler.add_rule(RepulsionRule(TAG_TO_CODE["공동주택"], TAG_TO_CODE["업무시설1"], 0, 1))
ruler.add_rule(RepulsionRule(TAG_TO_CODE["공동주택"], TAG_TO_CODE["업무시설2"], 0, 1))
ruler.add_rule(RepulsionRule(TAG_TO_CODE["공동주택"], TAG_TO_CODE["유보형복합용지"], 0, 1))
ruler.add_rule(RepulsionRule(TAG_TO_CODE["공동주택"], TAG_TO_CODE["자족복합용지"], 0, 1))
ruler.add_rule(RepulsionRule(TAG_TO_CODE["공동주택"], TAG_TO_CODE["자족시설"], 0, 1))

# runoff
ruler.add_rule(RunoffRule(50000, 75000))

ga = GeneticAlgorithm(ruler)
best = ga.run(size=40, strategy="cost", child_count=40, mutation_rate=0.9, stable_step_for_exit=50, is_logging=True)
# best = ga.run(size=40, strategy="age", elitism=4, mutation_rate=0.9, stable_step_for_exit=50, is_logging=True)
print("---- best chromosome details ----")
pprint(best.cost_detail)
