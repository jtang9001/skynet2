import pandas as pd
from tabulabuilder import Swimmer, Result

attendanceDf = pd.read_csv("attendance.csv")

swimmers = Result.select().where((Result.school == 3) & (Result.year == 2019)).objects()

for swimmer in swimmers:
    print(swimmer)