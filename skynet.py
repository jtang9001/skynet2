import glob
import pytesseract
from PIL import Image
import numpy as np
from matplotlib import pyplot as plt

#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR'

def getDivsForYear(year):
    return glob.glob("data/{} divs/*.png".format(year))

def getCitiesForYear(year):
    return glob.glob("data/{} cities/*.png".format(year))

def greyMatrixFromPath(path):
    return np.array(Image.open(path).convert("L"))

MIN_ROW_HEIGHT_PX = 5

def getRows(mat):
    rows = []
    row = None
    for i in range(mat.shape[0]):
        if np.mean(mat[i]) == 255:
            if row is not None:
                try:
                    row = np.vstack(
                        (255*np.ones( (5,mat.shape[1]) ), row)
                    )
                    row = np.vstack(
                        (row, 255*np.ones( (5,mat.shape[1]) ))
                    )
                    # plt.imshow(row, cmap = "gray")
                    # plt.show()
                    ocrRow = pytesseract.image_to_string(row, config="--psm 7 --dpi 200").replace('\n', ' ')
                    rows.append(ocrRow)
                    print(ocrRow)
                except Exception:
                    print(row)
                row = None
        else:
            if row is None:
                row = mat[i]
            else:
                row = np.vstack((row, mat[i]))

    return rows


for imgPath in getDivsForYear(2016):
    rows = getRows(greyMatrixFromPath(imgPath))
    #print(rows)