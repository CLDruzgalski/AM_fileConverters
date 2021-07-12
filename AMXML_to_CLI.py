########################################################################
### This program converts IFF XML files to CLI files
########################################################################

from lxml import etree as ET
from datetime import datetime
import os

sourcePath = '/Path/To/XML/Folder/'
XMLFolder = 'NameOfXMLFolder'
cliFile = XMLFolder + '.cli'
layerThickness = 500.0
scale = 0.0001

outputFile = open(sourcePath + cliFile, 'w')

def main():
    fileList = sorted(os.listdir(sourcePath + XMLFolder))
    numberOfLayers = getNumberOfLayers(fileList)
    
    writeHeader(numberOfLayers)

    for filename in fileList:
        writeLayer(filename)

    writeFooter()
    print('File conversion complete')

def getNumberOfLayers(fileList):
    
    #If file numbering starts with 0
    if int(fileList[0][0:-4]) == 0:
        return int(fileList[-1][0:-4]) + 1

    else:
        return int(fileList[-1][0:-4])

def getElementsInPath(root):
    Path = []
    for path in root.iter('Path'):
        X = []
        Y = []
        P = []
        U = []
        SS = []
        X.append(float(path[2][0].text))
        Y.append(float(path[2][1].text))
        for segment in path.iter('Segment'):
            X.append(float(segment[3][0].text))
            Y.append(float(segment[3][1].text))
            P.append(float(segment[0].text))
            U.append(float(segment[1].text))
            SS.append(float(segment[2].text))

        pathElements = [X,Y,P,U,SS]
        Path.append(pathElements)

    return Path

#Put all the path elements in the right CLI format
def writeLayer(filename):

    tree = ET.parse(sourcePath + XMLFolder + '/' + filename)
    root = tree.getroot()
    layer = int(filename[0:-4])*layerThickness

    outputFile.write('$$LAYER/' + str(layer) + '\n')
    paths = getElementsInPath(root)
    for path in paths:
        for segmentNum in range(len(path[3])):
            outputFile.write('$$POWER/' + str(path[2][segmentNum]) + '\n')
            outputFile.write('$$SPEED/' + str(path[3][segmentNum]) + '\n')
            outputFile.write('$$SPOTSIZE/' + str(path[4][segmentNum]) + '\n')
            outputFile.write('$$POLYLINE/1,2,2,' + str(int(path[0][segmentNum]/scale)) + ',' + str(int(path[1][segmentNum]/scale)) + ',' + str(int(path[0][segmentNum+1]/scale)) + ',' + str(int(path[1][segmentNum+1]/scale)) + '\n')


def writeHeader(numberOfLayers):
    outputFile.write('$$HEADERSTART\n'+ '$$ASCII\n' + '$$UNITS/0.0001\n' + '$$DATE/' + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + '\n' + '$$LABEL/ CLI file\n')
    outputFile.write('$$LAYERS/' + str(numberOfLayers) + '\n' + '$$HEADEREND\n' + '$$GEOMETRYSTART\n')

def writeFooter():
    outputFile.write('$$GEOMETRYEND')









if __name__ == "__main__":
    main()
