# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import sklearn as sk
from sklearn.model_selection import cross_val_score

from tradPointOut import rankToPoints2017

sns.set_style("whitegrid")


# %%
rawDf = pd.read_csv("data/tier7QLonly.csv")
df = rawDf.copy()
df.isRelay = df.isRelay.astype(int)

# strokes = df.pop("stroke")
# strokesOneHot = pd.get_dummies(strokes, prefix="stroke")
# df = pd.concat([df, strokesOneHot], axis=1)


# %%
df2018 = df.loc[df["year"] == 2018]
testSet = df2018.sample(frac = 0.7, random_state = 33)
testY = testSet.pop("points")
testX = testSet.copy()

trainSet = df[~df.index.isin(testSet.index)]
trainY = trainSet.pop("points")
trainX = trainSet.copy()

xCols = ["divsSpeed", "isRelay", "divsTimePctOfMean",  "clipped_divsRank"]
#, "stroke_Backstroke", "stroke_Breaststroke", "stroke_Freestyle", "stroke_Medley", "stroke_IM", "stroke_Butterfly"]

y2018 = df2018["points"]
x2018 = df2018[xCols]

trainX = trainX[xCols] 
testX = testX[xCols] 


# %%
from sklearn.svm import SVR

svr = SVR(gamma = "scale", kernel="rbf")
svr = svr.fit(trainX, trainY)
scores = cross_val_score(svr, trainX, trainY, cv=4)
print(f"R^2: {scores.mean()} (+/- {scores.std() * 2})")


# %%
svrY = svr.predict(x2018)
svrErrors = y2018 - svrY
print("MAE:", svrErrors.abs().mean())
df2018["svrPred"] = svrY
df2018["svrError"] = svrErrors


# %%
df2018["tradPred"] = df.apply(lambda row: rankToPoints2017(row["divsRank"]), axis=1)
df2018["tradError"] = df2018["points"] - df2018["tradPred"]


# %%
plt.figure(figsize = (10,8))
plt.xlabel("ML prediction")
plt.ylabel("Trad prediction")
lineX = np.linspace(0,20,20)
plt.plot(lineX, lineX)
plt.scatter(df2018["svrPred"], df2018["tradPred"])


# %%
from sklearn.ensemble import RandomForestRegressor

rfr = RandomForestRegressor(n_estimators=250, criterion="mse", min_samples_leaf=1)
rfr = rfr.fit(trainX, trainY)
scores = cross_val_score(rfr, trainX, trainY, cv=4)
print(f"R^2: {scores.mean()} (+/- {scores.std() * 2})")

rfrY = rfr.predict(x2018)
rfrErrors = y2018 - rfrY
print("MAE:", rfrErrors.abs().mean())
df2018["rfrPred"] = rfrY
df2018["rfrError"] = rfrErrors


# %%
plt.figure(figsize = (10,8))
plt.xlabel("Random Forest prediction")
plt.ylabel("Trad prediction")
lineX = np.linspace(0,20,20)
plt.plot(lineX, lineX)
plt.scatter(df2018["rfrPred"], df2018["tradPred"])


# %%
pd.DataFrame([xCols, rfr.feature_importances_])


# %%
from sklearn.ensemble import GradientBoostingRegressor

gbr = GradientBoostingRegressor(n_estimators=1000, criterion="friedman_mse", min_samples_leaf=64, learning_rate=0.1)
gbr = gbr.fit(trainX, trainY)
scores = cross_val_score(gbr, trainX, trainY, cv=4)
print(f"R^2: {scores.mean()} (+/- {scores.std() * 2})")

gbrY = gbr.predict(x2018)
gbrErrors = y2018 - gbrY
print("MAE:", gbrErrors.abs().mean())
df2018["gbrPred"] = gbrY
df2018["gbrError"] = gbrErrors

pd.DataFrame([xCols, gbr.feature_importances_])


# %%
plt.figure(figsize = (10,8))
plt.xlabel("Gradient boosting prediction")
plt.ylabel("Traditional prediction")
lineX = np.linspace(0,20,20)
plt.plot(lineX, lineX)
plt.scatter(df2018["gbrPred"], df2018["tradPred"])


# %%
estimators = ["svr", "gbr", "rfr", "trad"]
errorHistDf = pd.DataFrame(columns=["points", "error", "estimator"])
for estimator in estimators:
    errColName = f"{estimator}Error"
    estimatorErrorDf = df2018[["points", errColName]].copy()
    estimatorErrorDf["estimator"] = estimator
    estimatorErrorDf = estimatorErrorDf.rename(columns={errColName: "error"})
    errorHistDf = errorHistDf.append(estimatorErrorDf)


# %%
plt.figure(figsize = (20,12))
sns.boxplot(x = "points", y = "error", hue = "estimator", data = errorHistDf)


# %%
from tabulabuilder import School

for est in estimators:
    estSum = pd.pivot_table(
        df2018, 
        index = "school", 
        values = f"{est}Pred",
        aggfunc = np.sum
    )

    print(estSum)

    estSum["school"] = estSum.index.map(lambda idx: School.get_by_id(idx).name)

    print(estSum)
    


# %%


