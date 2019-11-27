import pandas as pd
import numpy as np
import tabula
import PyPDF2
import re
import traceback

NAME_PTN = re.compile(r"(?P<lastName>[A-Za-z\-']+),\ (?P<firstName>[A-Za-z\-']+)")

def getnames():
    return set(NAME_PTN.findall(
        "".join(open("2019heats.txt", "r").readlines())
    ))

NAMES = [line.lower() for line in open("validnames.txt", "r").readlines()]

def nameIsValid(lastname, firstname):
    #print(f"{lastname.lower()}, {firstname.lower()}")
    
    for line in NAMES:
        if firstname.lower() in line and lastname.lower() in line:
            return True

    return False


if __name__ == "__main__":
    for name in getnames():
        if not nameIsValid(*name):
            print(", ".join(name))
