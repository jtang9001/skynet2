from peewee import *
from playhouse.shortcuts import model_to_dict
from tabulabuilder import Result, Event, Swimmer, methodsWithDecorator, trackedProperty
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

def tier2results():
    results = (
        Result.select(
            Result.divsRank,
            Result.finalRank,
            Result.seedTime,
            Result.divsTime,
            Result.qualified,
            Event.distance,
            Event.gender,
            Event.stroke)
            .join_from(Result, Event)
        .where(Result.divsRank.is_null(False))
        .dicts()
    )

    df = pd.DataFrame(results)

    # df["points"] = df.apply(
    #     lambda row: rankToPoints2017(row["finalRank"]),
    #     axis = 1)

    df["seedSpeed"] = df.apply(
        lambda row: row["distance"]/row["seedTime"],
        axis = 1)

    df["divsSpeed"] = df.apply(
        lambda row: row["distance"]/row["divsTime"],
        axis = 1)

    df["deltaSpeed"] = df.apply(
        lambda row: row["divsSpeed"]-row["seedSpeed"],
        axis = 1)

    # df["distBucket"] = df.apply(
    #     lambda row: str(row["distance"]),
    #     axis = 1)

    df["genderIndicator"] = df.apply(
        lambda row: 0 if row["gender"] == "Boys" else 1,
        axis = 1)

    df["isFly"] = df.apply(
        lambda row: 1 if row["stroke"] == "Butterfly" else 0,
        axis = 1)

    df["isBack"] = df.apply(
        lambda row: 1 if row["stroke"] == "Backstroke" else 0,
        axis = 1)

    df["isBreast"] = df.apply(
        lambda row: 1 if row["stroke"] == "Breaststroke" else 0,
        axis = 1)

    df["isFree"] = df.apply(
        lambda row: 1 if row["stroke"] == "Freestyle" else 0,
        axis = 1)

    df["isIM"] = df.apply(
        lambda row: 1 if row["stroke"] == "IM" else 0,
        axis = 1)

    df["isQl"] = df.apply(
        lambda row: 1 if row["qualified"] else 0,
        axis = 1)

    return df

def tier3results():
    results = (
        Result.select(
            Result, Event
        ).join(Event)
        .where((Result.divsRank.is_null(False)) & (Result.seedTime.is_null(False)))
    )

    dfData = []

    for result in results.objects():
        r = model_to_dict(result, recurse=False)
        event = result.event

        for methodName in methodsWithDecorator(event, trackedProperty):
            print(methodName)
            r[methodName] = getattr(event, methodName)

        r["gender"] = event.gender
        r["distance"] = event.distance
        r["stroke"] = event.stroke
        r["points"] = result.points
        dfData.append(r)

    df = pd.DataFrame(dfData)

    return df

def tier4():
    results = (
        Result.select(
            Result, Event
        ).join(Event)
        .where((Result.divsRank.is_null(False)) & (Result.seedTime.is_null(False)))
    )

if __name__ == "__main__":
    tier3results().to_csv("tier3.csv")