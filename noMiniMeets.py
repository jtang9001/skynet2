import pandas as pd
import numpy as np
import tabula
import PyPDF2
import re
import traceback

NAME_PTN = re.compile(r"(?P<lastname>[A-Za-z\-']+),\ (?P<firstname>[A-Za-z\-']+)")
EVENT_PTN = re.compile(
    r'''Event\ \d+\ +
    (?P<gender>Boys|Girls|Mixed)\ 
    (?P<age>\d{2}|Open).+
    (?P<distance>50|100|200|400).+Meter\ 
    (?P<stroke>[A-Za-z]+)
    (?P<relay>\ Relay)?''',
    re.VERBOSE)

def getMinisForPerson(firstname, lastname):
    aliases = aliasesDf[
        aliasesDf["DivsName"].str.contains(firstname, case=False) & 
        aliasesDf["DivsName"].str.contains(lastname, case=False) 
    ]

    if not aliases.empty and pd.notna(aliases["MinisName"]).any():
        name = aliases["MinisName"].iloc[0]
        rows = minis[
            minis["Name"].str.contains(name, case=False)
        ]
    else:
        rows = minis[
            minis["Name"].str.contains(firstname, case=False) & 
            minis["Name"].str.contains(lastname, case=False) 
        ]

    if rows.empty:
        return None
    else:
        return rows.head(1)

if __name__ == "__main__":
    
    minis = pd.read_csv("data/2019minis.csv")
    aliasesDf = pd.read_csv("suspnames.csv")
    suspDf = pd.DataFrame()
    
    for line in open("data/2019heats.txt", "r").readlines():
        
        if EVENT_PTN.search(line):
            currentEvent = EVENT_PTN.search(line).groupdict()
            colName = f"{currentEvent['distance']} {currentEvent['stroke']}"
            print(line)

        elif NAME_PTN.search(line):
            person = NAME_PTN.search(line).groupdict()
            rows = getMinisForPerson(**person)

            if rows is not None:
                if pd.isna(rows[colName]).any():
                    print(line)
                    rows["DivsName"] = f"{person['lastname']}, {person['firstname']}"
                    rows["Event"] = colName
                    suspDf = pd.concat([suspDf, rows])

    suspDf.to_csv("nominimeets.csv")
    print(suspDf)
                    

