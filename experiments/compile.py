"""
Helper script for compiling results from multiple experiments. At this point, it only creates
average collisions and average of average ticks per map of all experiments. Four new files will be created:

- averages_avg_avg_ticks.csv = The average of average ticks per map of all experiments for the AVERAGE agent
- average_avg_collisions.csv = The average collisions per map of all experiments for the AVERAGE agent
- bests_avg_avg_ticks.csv = The average of average ticks per map of all experiments for the BEST agent
- bests_avg_collisions.csv = The average collisions per map of all experiments for the BEST agent

IMPORTANT NOTE: This is with the assumption that 2 experiments were run in parallel, with the first one
testing the BEST agent, and the second one testing the AVERAGE agent.
"""

import csv
import json
from pathlib import Path


def average_datas(dataset: list[dict], key: str):
    collisions = [[value[key] for k, value in data.items() if k.startswith("map")] for data in dataset]
    return [average([row[i] for row in collisions]) for i in range(len(collisions[0]))]


def write_csv(path: str, dataset: list[list]):
    with open(path, "w") as file:
        writer = csv.writer(file, delimiter=" ")
        writer.writerows(dataset)


def average(values: list):
    return sum(values) / len(values)


def read_file(path: str):
    with open(path, "r") as file:
        return json.load(file)


cwd = Path.cwd()
experiment_result = "experiment_results.json"
experiments = [folder for folder in cwd.iterdir() if folder.is_dir()]
bests: list[dict] = [read_file(best / experiment_result) for best in experiments[::2]]
averages: list[dict] = [read_file(avg / experiment_result) for avg in experiments[1::2]]
maps: list[int] = [int(key[3:]) for key, value in bests[0].items() if key.startswith("map")]

bests_avg_collisions = average_datas(bests, "collisions")
bests_avg_avg_ticks = average_datas(bests, "average_ticks")
averages_avg_collisions = average_datas(averages, "collisions")
averages_avg_avg_ticks = average_datas(averages, "average_ticks")

bests_avg_collisions_zipped = list(zip(maps, bests_avg_collisions))
bests_avg_avg_ticks_zipped = list(zip(maps, bests_avg_avg_ticks))
averages_avg_collisions_zipped = list(zip(maps, averages_avg_collisions))
averages_avg_avg_ticks_zipped = list(zip(maps, averages_avg_avg_ticks))

write_csv(cwd / "bests_avg_collisions.csv", bests_avg_collisions_zipped)
write_csv(cwd / "bests_avg_avg_ticks.csv", bests_avg_avg_ticks_zipped)
write_csv(cwd / "averages_avg_collisions.csv", averages_avg_collisions_zipped)
write_csv(cwd / "averages_avg_avg_ticks.csv", averages_avg_avg_ticks_zipped)
