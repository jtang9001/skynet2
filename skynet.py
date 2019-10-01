import glob
import pytesseract
from PIL import Image
import numpy as np

#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR'

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
        if np.mean(mat[i]) == 255:
            if row is not None:
                rows.append(pytesseract.image_to_string(row))
                row = None
        else:
            if row is None:
                row = mat[i]
            else:
                row = np.vstack((row, mat[i]))

    return rows


for imgPath in getDivsForYear(2016)[:1]:
    rows = getRows(greyMatrixFromPath(imgPath))
    print(rows)