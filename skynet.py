from PIL import Image
from matplotlib import pyplot as plt
from peewee import *
import numpy as np
import glob
import pytesseract
import traceback

YEAR = 2018

db = SqliteDatabase("{}.db".format(YEAR), pragmas = {
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
    rank = IntegerField()
    swimmer = ForeignKeyField(Swimmer, backref = "results")
    event = ForeignKeyField(Event, backref = "results")
    seedtime = FloatField()
    newtime = FloatField()

    class Meta:
        database = db

class RelayResult(Model):
    rank = IntegerField()
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
                    traceback.print_exc()
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
    return pytesseract.image_to_string(row, config="--psm 7 --dpi 400").replace('\n', ' ') + '\n'

db.connect()
db.create_tables([School, Swimmer, Event, Result, RelayResult, RelayParticipant])
db.close()

txtFile = open("{} cities.txt".format(YEAR), "w")

regexStr = r"([-\d]+)[. ]+([A-Za-z \-']+), ([A-Za-z \-']+)([\d.]+) ([A-Za-z \-']+) ((\d+:)?\d{2}\.?\d{2}|NT)\s+((\d+:)?\d{2}\.?\d{2}|[A-Z]{2,})[ .]*([a-z]*)"

for imgPath in getCitiesForYear(YEAR):
    rows = getRows(greyMatrixFromPath(imgPath))
    txtFile.writelines(rows)

txtFile.close()