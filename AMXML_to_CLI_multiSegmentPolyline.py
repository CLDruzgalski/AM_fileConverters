########################################################################
### This program converts IFF XML files to CLI files
########################################################################

from lxml import etree as ET
from datetime import datetime
import os
import numpy as np

layerThickness = 500.0
scale = 0.0001

first_n_lays=False ## write just the first n layers (n_lays)
between_n_lays=False ## write n layers (n_lays) on either side of some chosen layer (lay_between)
n_lays=5 ## number of layers to write
lay_between=250 ## layer number to write n_lays around
combineSegments=False ## combine segments that are the same P,U,SS in a given path
checkme=False ## write in the CLI file where the segments are/were the same in a give path

sourcePath =os.getcwd()+'/Path/To/XML/Folder/'
XMLFolder ='NameOfXMLFolder'

##name of the output cli file
if first_n_lays and combineSegments==False and between_n_lays==False:
    cliFile = XMLFolder + '_first'+str(n_lays)+'lays.cli'
elif first_n_lays and combineSegments and between_n_lays==False:
    cliFile = XMLFolder + '_first'+str(n_lays)+'lays_CombinedSegments.cli'
elif first_n_lays==False and combineSegments and between_n_lays==False:
    cliFile = XMLFolder + '_CombinedSegments.cli' 
elif between_n_lays and combineSegments==False and first_n_lays==False:
    cliFile = XMLFolder + '_lay'+str(lay_between)+'between_'+str(n_lays*2)+'lays.cli'
elif between_n_lays and combineSegments==True and first_n_lays==False:
    cliFile = XMLFolder + '_lay'+str(lay_between)+'between_'+str(n_lays*2)+'lays_CombinedSegments.cli'    
else:
    cliFile=XMLFolder+'.cli'

print('file being written',sourcePath+cliFile)

outputFile = open(sourcePath + cliFile, 'w')

def main():
    fileList = sorted(os.listdir(sourcePath + XMLFolder))
    numberOfLayers = getNumberOfLayers(fileList)
    print('total number of layers in XMLFolder',numberOfLayers)
    
    writeHeader(numberOfLayers)
    
    count=0
    for filename in fileList:
        if first_n_lays:
            if count<n_lays+1:
                writeLayer(filename)
            else:
                break
            count=count+1
        elif between_n_lays:
            if count>lay_between-n_lays-1:
                if count>=lay_between-n_lays and count<=lay_between+n_lays:
                    writeLayer(filename)                
                else:
                    break
            count=count+1
        else:
            writeLayer(filename)
            
    writeFooter() 
    
    outputFile.close()
    print('File conversion complete')

def getNumberOfLayers(fileList):
    
    ##If file numbering starts with 0
    if int(fileList[0][0:-4]) == 0:
        return int(fileList[-1][0:-4]) + 1

    else:
        return int(fileList[-1][0:-4])

def getElementsInPath(root):
    count=0
    Path = []
    for path in root.iter('Path'):
        ##Path = [Tag,NumSegments,Start,Segment,Segment,...,Segment]
        ##path[1].text = number of segments within a given path
        ##path[2][:]=[X,Y Start], path[3+][:]=[Power, Speed, Spotsize, End]
        X = [] ##x-position
        Y = [] ##y-position
        P = [] ##power
        U = [] ##speed
        SS = [] ##spotsize or focus
        X.append(float(path[2][0].text))
        Y.append(float(path[2][1].text))
        for segment in path.iter('Segment'):
            X.append(float(segment[3][0].text))
            Y.append(float(segment[3][1].text))
            P.append(float(segment[0].text))
            U.append(float(segment[1].text))
            SS.append(float(segment[2].text))

        pathElements = [X,Y,P,U,SS]
        ##X (and Y)=[x1,x2,x3,x4]-> x1=start, x2=end (also start of next segment), x3=end (also start of next segment),x4=end
        ##P (and U, SS)=[p1,p2,3]->p1=segment power for x1:x2 & y1:y2, p2=segment power for x2:x3 & y2:y3, p3=segement power of x3:x4 & y3:y4
        Path.append(pathElements)
        count=count+1
    ##len(root[1]) gives the number of paths and path[1].text gives the number of segments within a path
    ##final Path will be of length root[1] with subarrays of path[1].text for each element.

    return Path

##Put all the path elements in the right CLI format    
def writeLayer(filename):
    tree = ET.parse(sourcePath + XMLFolder + '/' + filename)
    root = tree.getroot()
    layer = int(filename[0:-4])*layerThickness
    if first_n_lays or between_n_lays:
        print('writting layer',layer)
    outputFile.write('$$LAYER/' + str(layer) + '\n')
    paths = getElementsInPath(root)
    countpath=0
    for path in paths:
        if combineSegments:
            if len(path[2])<=1:
                n=len(path[2])
                outputFile.write('$$POWER/' + str(path[2][n-1]) + '\n')
                outputFile.write('$$SPEED/' + str(path[3][n-1]) + '\n')
                outputFile.write('$$FOCUS/' + str(path[4][n-1]) + '\n')
                outputFile.write('$$POLYLINE/1,2,'+str(len(path[0]))+',' + str(int(path[0][n-1]/scale)) + ',' + str(int(path[1][n-1]/scale)) + ',' + str(int(path[0][n]/scale)) + ',' + str(int(path[1][n]/scale)) + '\n')
            else:
                truepoly=[]
                for segmentNum in range(1,len(path[3])):
                    if path[2][segmentNum-1]==path[2][segmentNum] and path[3][segmentNum-1]==path[3][segmentNum] and path[4][segmentNum-1]==path[4][segmentNum]:
                        elsetrigger=True
                        truepoly.append(segmentNum)
                        power=path[2][segmentNum]
                        speed=path[3][segmentNum]
                        focus=path[4][segmentNum]
                        if segmentNum==truepoly[0]:
                            polyline=str(int(path[0][segmentNum-1]/scale))+','+str(int(path[1][segmentNum-1]/scale))
                            polyline+=','+str(int(path[0][segmentNum]/scale))+','+str(int(path[1][segmentNum]/scale))
                        else:
                            polyline+=','+str(int(path[0][segmentNum]/scale))+','+str(int(path[1][segmentNum]/scale))
                            if segmentNum+1==len(path[0])-1:
                                polyline+=','+str(int(path[0][segmentNum+1]/scale))+','+str(int(path[1][segmentNum+1]/scale))
                        if checkme:
                            print('current path has/had equivalent segments',countpath)
                    else:
                        elsetrigger=False
                        if segmentNum==1:  ##still write segmentNum==0 if combine segments is not triggered
                            outputFile.write('$$POWER/' + str(path[2][segmentNum-1]) + '\n')
                            outputFile.write('$$SPEED/' + str(path[3][segmentNum-1]) + '\n')
                            outputFile.write('$$FOCUS/' + str(path[4][segmentNum-1]) + '\n')
                            outputFile.write('$$POLYLINE/1,2,'+'2'+',' + str(int(path[0][segmentNum-1]/scale)) + ',' + str(int(path[1][segmentNum-1]/scale)) + ',' + str(int(path[0][segmentNum]/scale)) + ',' + str(int(path[1][segmentNum]/scale)) + '\n')
                        ##still write segments if combine segments is not triggered
                        outputFile.write('$$POWER/' + str(path[2][segmentNum]) + '\n')
                        outputFile.write('$$SPEED/' + str(path[3][segmentNum]) + '\n')
                        outputFile.write('$$FOCUS/' + str(path[4][segmentNum]) + '\n')
                        outputFile.write('$$POLYLINE/1,2,'+'2'+',' + str(int(path[0][segmentNum]/scale)) + ',' + str(int(path[1][segmentNum]/scale)) + ',' + str(int(path[0][segmentNum+1]/scale)) + ',' + str(int(path[1][segmentNum+1]/scale)) + '\n')
                if elsetrigger: ##write the combined segments polyline
                    outputFile.write('$$POWER/' + str(power) + '\n')
                    outputFile.write('$$SPEED/' + str(speed) + '\n')
                    outputFile.write('$$FOCUS/' + str(focus) + '\n')
                    outputFile.write('$$POLYLINE/1,2,'+str(len(path[0]))+','+polyline+'\n')
        else:
            for segmentNum in range(len(path[3])):
                if checkme:
                    if segmentNum>0 and path[2][segmentNum-1]==path[2][segmentNum] and path[3][segmentNum-1]==path[3][segmentNum] and path[4][segmentNum-1]==path[4][segmentNum]:
                        print('current path has equivalent segments',countpath)
                outputFile.write('$$POWER/' + str(path[2][segmentNum]) + '\n')
                outputFile.write('$$SPEED/' + str(path[3][segmentNum]) + '\n')
                outputFile.write('$$FOCUS/' + str(path[4][segmentNum]) + '\n')
                outputFile.write('$$POLYLINE/1,2,2,' + str(int(path[0][segmentNum]/scale)) + ',' + str(int(path[1][segmentNum]/scale)) + ',' + str(int(path[0][segmentNum+1]/scale)) + ',' + str(int(path[1][segmentNum+1]/scale)) + '\n')
    
        countpath+=1


def writeHeader(numberOfLayers):
    outputFile.write('$$HEADERSTART\n'+ '$$ASCII\n' + '$$UNITS/0.0001\n' + '$$DATE/' + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + '\n' + '$$LABEL/ CLI file\n')
    outputFile.write('$$LAYERS/' + str(numberOfLayers) + '\n' + '$$HEADEREND\n' + '$$GEOMETRYSTART\n')

def writeFooter():
    outputFile.write('$$GEOMETRYEND\n')




if __name__ == "__main__":
    main()

