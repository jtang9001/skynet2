#from peewee import *
from playhouse.shortcuts import model_to_dict
from tabulabuilder import Result, Event, Swimmer
import pandas as pd
import numpy as np

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

def improvement():
    results = (
        Result.select(
            Swimmer.firstName,
            Swimmer.lastName,
            Event.distance,
            Event.stroke,
            Event.age,
            Event.gender,
            Result.divsRank, 
            Result.finalRank, 
            Result.seedTime, 
            Result.divsTime, 
            Result.finalTime
        ).join(Event, Swimmer)
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

        r["gender"] = event.gender
        r["distance"] = event.distance
        r["stroke"] = event.stroke
        r["points"] = result.points
        dfData.append(r)

    df = pd.DataFrame(dfData)

    return df

def tier4():
    _cache = {}
    events = Event.select().where(~(Event.isRelay)).objects()
    df = pd.DataFrame()

    for event in events:
        print(event)

        if event.isRelay:
            results = event.relayresults
        else:
            results = event.results

        resultDicts = []

        for result in results.objects():
            # if not result.qualified:
            #     continue
            rd = model_to_dict(result, recurse=False)

            for virtFieldName in result.virtFields:
                if hasattr(result, virtFieldName):
                    rd[virtFieldName] = getattr(result, virtFieldName)()

            for virtFieldName in event.virtFields:
                cacheKey = f"{event}{virtFieldName}{result.year}"
                if cacheKey in _cache:
                    rd[virtFieldName] = _cache[cacheKey]
                elif hasattr(event, virtFieldName):
                    rd[virtFieldName] = getattr(event, virtFieldName)(result.year)
                    _cache[cacheKey] = rd[virtFieldName]

            resultDicts.append(rd)

        resultsDf = pd.DataFrame(resultDicts)

        resultsDf["gender"] = event.gender
        resultsDf["distance"] = event.distance
        resultsDf["stroke"] = event.stroke

        means = resultsDf.mean()

        #resultsDf["seedTimePctOfMean"] = resultsDf["seedTime"]/means["seedTime"]
        resultsDf["divsTimePctOfMean"] = resultsDf["divsTime"]/means["divsTime"]
        #resultsDf["divsTimePctOfSeed"] = resultsDf["divsTime"]/resultsDf["seedTime"]
        #resultsDf["seedSpeedDiffFromMean"] = resultsDf["seedSpeed"] - means["seedSpeed"]
        resultsDf["divsSpeedDiffFromMean"] = resultsDf["divsSpeed"] - means["divsSpeed"]

        df = df.append(resultsDf, ignore_index = True, sort = False)

    df = df.drop([
        "swimmer", "school", "year", "id", "event",
        "seedTime", "divsTime", "finalTime", "finalRank"
    ], axis = 1)

    means = df.mean()
    stds = df.std()

    colsToNorm = [
        #"seedTimePctOfMean", 
        "divsTimePctOfMean", 
        #"seedSpeedDiffFromMean", 
        "divsSpeedDiffFromMean", 
        #"divsTimePctOfSeed", 
        #"seedSpeed", 
        "divsSpeed",
        "numSwimmers",
        "numQualified",
        "swimmerage",
        #"divsRank",
        #"distance",
        #"teamSize"
        ]

    for col in colsToNorm:
        df[f"normed_{col}"] = (df[col] - means[col])/stds[col]

    df["clipped_divsRank"] = (df["divsRank"].clip(upper = 24))/24
    df["normed_numRelays"] = df["numRelays"]/2
    #df["log_teamSize"] = np.log(df["teamSize"])

    means = df.mean()
    stds = df.std()

    print(means)
    print(stds)

    return df
        
def tier7():
    _cache = {}
    events = Event.select().objects()
    df = pd.DataFrame()

    for event in events:
        print(event)

        if event.isRelay:
            results = event.relayresults
        else:
            results = event.results

        resultDicts = []

        for result in results.objects():
            if result.year != 2019 or not result.qualified:
                continue

            rd = model_to_dict(result, recurse=False)

            for virtFieldName in result.virtFields:
                if hasattr(result, virtFieldName):
                    rd[virtFieldName] = getattr(result, virtFieldName)()

            resultDicts.append(rd)

        resultsDf = pd.DataFrame(resultDicts)

        resultsDf["isRelay"] = event.isRelay
        resultsDf["event"] = str(event)
        resultsDf["gender"] = event.gender
        resultsDf["distance"] = event.distance
        resultsDf["stroke"] = event.stroke

        means = resultsDf.mean()

        #resultsDf["seedTimePctOfMean"] = resultsDf["seedTime"]/means["seedTime"]
        resultsDf["divsTimePctOfMean"] = resultsDf["divsTime"]/means["divsTime"]
        #resultsDf["divsTimePctOfSeed"] = resultsDf["divsTime"]/resultsDf["seedTime"]
        #resultsDf["seedSpeedDiffFromMean"] = resultsDf["seedSpeed"] - means["seedSpeed"]
        resultsDf["divsSpeedDiffFromMean"] = resultsDf["divsSpeed"] - means["divsSpeed"]

        df = df.append(resultsDf, ignore_index = True, sort = False)

    # df = df.drop([
    #     "swimmer", "id", "event", "swimmerage", "qualified",
    #     "seedTime", "divsTime", "finalTime", "finalRank", "designation"
    # ], axis = 1)

    df = df.drop(["swimmer", "designation", "id", "finalTime", "qualified", "finalRank"], axis = 1)

    # means = df.mean()
    # stds = df.std()

    # colsToNorm = [
    #     "divsTimePctOfMean", 
    #     "divsSpeedDiffFromMean", 
    #     "divsSpeed",
    #     ]

    # for col in colsToNorm:
    #     df[f"normed_{col}"] = (df[col] - means[col])/stds[col]

    df["clipped_divsRank"] = df["divsRank"].clip(upper = 24)

    means = df.mean()
    stds = df.std()

    print(means)
    print(stds)

    return df

if __name__ == "__main__":
    tier1results().to_csv("data/2022_improvements.csv", index=False)