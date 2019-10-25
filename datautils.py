from peewee import *
from tabulabuilder import Result, Event
import pandas as pd

def zscore(val, mean, std):
    return (val - mean) / std

def normImprovement(seedtime, divstime, distance):
    return (divstime - seedtime) / distance

def tier1results():
    results = (
        Result.select(
            Result.divsRank, 
            Result.finalRank, 
            Result.seedTime, 
            Result.divsTime, 
            Event.distance
        ).join(Event)
        .where(Result.finalRank.is_null(False))
        .dicts()
    )

    df = pd.DataFrame(results)
    df["improvement"] = df.apply(
        lambda row: normImprovement(row["seedTime"], row["divsTime"], row["distance"]),
        axis = 1)

    improveMean = df.mean(axis=0)["improvement"]
    improveStd = df.std(axis=0)["improvement"]

    df["improveZscore"] = df.apply(
        lambda row: zscore(row["improvement"], improveMean, improveStd),
        axis = 1
    )

    return df

if __name__ == "__main__":
    tier1results().to_csv("tier1.csv")