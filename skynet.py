from PIL import Image
from matplotlib import pyplot as plt
from peewee import *
import numpy as np
import glob
import pytesseract

db = SqliteDatabase("results.db", pragmas = {
    'foreign_keys': 1,
    'ignore_check_constraints': 0})

class School(Model):
    name = CharField()

    class Meta:
        database = db

class Swimmer(Model):
    firstname = CharField()
    lastname = CharField()
    grade = IntegerField()
    gender = CharField()
    school = ForeignKeyField(School, backref = "swimmers")

    class Meta:
        database = db

class Event(Model):
    grade = IntegerField()
    distance = IntegerField()
    stroke = CharField()
    gender = CharField()

    class Meta:
        database = db

class Result(Model):
    swimmer = ForeignKeyField(Swimmer, backref = "results")
    event = ForeignKeyField(Event, backref = "results")

    class Meta:
        database = db

class RelayResult(Model):
    seedtime = FloatField()
    newtime = FloatField()

    class Meta:
        database = db

class RelayParticipant(Model):
    swimmer = ForeignKeyField(Swimmer, backref = "relays")
    relay = ForeignKeyField(RelayResult, backref = "participants")

    class Meta:
        database = db


def getDivsForYear(year):
    return glob.glob("data/{} divs/*.png".format(year))

def getCitiesForYear(year):
    return glob.glob("data/{} cities/*.png".format(year))

def greyMatrixFromPath(path):
    return np.array(Image.open(path).convert("L"))

def getRows(mat):
    rows = []
    row = None
    for i in range(mat.shape[0]):
        if np.mean(mat[i]) == 255.0:
            if row is not None:
                try:
                    if np.mean(row) >= 100:
                        readRow = ocrRow(row)
                        rows.append(readRow)
                        print(readRow)
                except Exception:
                    print(row)
                row = None
        else:
            if row is None:
                row = mat[i]
            else:
                row = np.vstack((row, mat[i]))

    return rows

def ocrRow(row):
    row = np.vstack(
        (255*np.ones( (10,row.shape[1]) ), row)
    )
    row = np.vstack(
        (row, 255*np.ones( (10,row.shape[1]) ))
    )
    return pytesseract.image_to_string(row, config="--psm 7 --dpi 400").replace('\n', ' ')


for imgPath in getDivsForYear(2018):
    rows = getRows(greyMatrixFromPath(imgPath))
    #print(rows)