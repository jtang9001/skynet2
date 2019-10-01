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
    i = 0
    while i < mat.shape[0]:
        if np.mean(mat[i]) != 255:
            rowMat = mat[i]
            i += 1
            while np.mean(mat[i]) != 255:
                rowMat = np.vstack((rowMat, mat[i]))
                i += 1
            rows.append(pytesseract.image_to_string(rowMat))                
        else:
            i += 1
    return rows


for imgPath in getDivsForYear(2016)[:1]:
    rows = getRows(greyMatrixFromPath(imgPath))
    print(rows)