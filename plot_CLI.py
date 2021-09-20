########################################################################
### This program plots CLI files
########################################################################

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
from array import *
import os

layerThickness = 500.0
scale = 0.0001
layer_number=250 ##layer to plot, unless whole file is desired
powerMin=0 ##power minimum
powerMax=320 ##power maximum
rescale=False ## rescale x & y for plotting
### plot whole file or specific layer
whole_file=False ##plot whole .cli file
layer_only=True ##plot a specific layer
printme=True ##turn on print line(s)

sourcePath =os.getcwd()+'/Path/To/XML/Folder/' ##folder path
filename = 'filename_to_plot.cli' ##filename of cli
print('filename and path',sourcePath+filename)

file1 = open(sourcePath+filename)

### plot specific layer
if layer_only:
    layerNum=layerThickness*layer_number ##layer to plot
    layerTAG='$$LAYER/'+str(layerNum)
    
#### Put polyline data into arrays
polylines = []
polyline = []
countline=0
falseCountLine=True
false_countline=-1
keepRun=False
for line in file1:
    if whole_file:
        if len(polyline) == 4: #If the polyline is fully described, add to polylines array
            polylines.append(polyline)
            polyline = []
        if '$$POWER' in line:
            line = line.replace('$$POWER/', '')
            powerList=line.splitlines()
            powerList=[int(float(p)) for p in powerList]
            polyline.append(powerList)
        if '$$SPEED' in line:
            line = line.replace('$$SPEED/', '')
            speedList = line.split(',')
            speedList=[int(float(s)) for s in speedList]
            polyline.append(speedList)
        if '$$FOCUS' in line:
            line = line.replace('$$FOCUS/', '')
            spotsizeList = line.split(',')
            spotsizeList=[int(float(ss)) for ss in spotsizeList]
            polyline.append(spotsizeList)
        if '$$POLYLINE' in line:
            line = line.replace('$$POLYLINE/', '')
            polylineList = line.split(',')
            polylineList = polylineList[3:]
            if rescale:
                polylineList = list(map(float, polylineList)) #Convert array of str to array of floats
                polylineList = np.asarray(polylineList)*scale
                polyline.append(polylineList.tolist())
            else:
                polylineList = list(map(int, polylineList)) #Convert array of str to array of ints
                polyline.append(polylineList)

    elif layer_only:
        if '$$LAYER/' in line and float(line.replace('$$LAYER/','')) <= layerNum and float(line.replace('$$LAYER/',''))> layerNum-layerThickness:
            keepRun=True ##start of the desired layer
        elif '$$LAYER/' in line and float(line.replace('$$LAYER/','')) > float(layerTAG.replace('$$LAYER/','')):
            keepRun=False ##end of the desired layer
            if falseCountLine: ##to include the final line of desired layer
                false_countline=countline
                falseCountLine=False
            if printme:
                print('layer floats',float(line.replace('$$LAYER/','')), float(layerTAG.replace('$$LAYER/','')))
                print('keepRun==False & line',line)
                print('no longer adding to polyline(s)',countline,false_countline)
                printme=False
        if keepRun or countline==false_countline: ##add only the desired layers lines
            if len(polyline) == 4: ##If the polyline is fully described, add to polylines array
                polylines.append(polyline)
                polyline = []
            if '$$POWER' in line:
                line = line.replace('$$POWER/', '')
                powerList=line.splitlines()
                powerList=[int(float(p)) for p in powerList]
                polyline.append(powerList)
            if '$$SPEED' in line:
                line = line.replace('$$SPEED/', '')
                speedList = line.split(',')
                speedList=[int(float(s)) for s in speedList]
                polyline.append(speedList)
            if '$$FOCUS' in line:
                line = line.replace('$$FOCUS/', '')
                spotsizeList = line.split(',')
                spotsizeList=[int(float(ss)) for ss in spotsizeList]
                polyline.append(spotsizeList)
            if '$$POLYLINE' in line:
                line = line.replace('$$POLYLINE/', '')
                polylineList = line.split(',')
                polylineList = polylineList[3:]
                if rescale:
                    polylineList = list(map(float, polylineList)) #Convert array of str to array of ints
                    polylineList = np.asarray(polylineList)*scale
                    polyline.append(polylineList.tolist())
                else:
                    polylineList = list(map(int, polylineList)) #Convert array of str to array of ints
                    polyline.append(polylineList)
    countline=countline+1


print('len(polylines)',len(polylines))
print('last row of polylines',polylines[-1])

fig1, ax1 = plt.subplots()
cmap = plt.get_cmap('Reds')

xmaxmin=[]
ymaxmin=[]
for polylineNum in range(len(polylines)):

    polylineCoordinates = polylines[polylineNum][3]
    polylineXcoordinates = polylineCoordinates[::2]
    xmaxmin.append((np.max(polylineXcoordinates),np.min(polylineXcoordinates)))
    polylineYcoordinates = polylineCoordinates[1::2]
    ymaxmin.append((np.max(polylineYcoordinates),np.min(polylineYcoordinates)))
 

    listOfOrderedPairs = np.array([np.array(polylineXcoordinates), np.array(polylineYcoordinates)]).T.reshape(-1, 1, 2)
    segments = np.concatenate([listOfOrderedPairs[:-1], listOfOrderedPairs[1:]], axis=1)
    line_segments = LineCollection(segments, cmap = cmap)
    line_segments.set_array(np.array(polylines[polylineNum][0]))
    ax1.add_collection(line_segments)
    plt.sci(line_segments)
    plt.clim(powerMin, powerMax)
if printme:
    print('X max, min',np.max(xmaxmin),np.min(xmaxmin))
    print('Y max, min',np.max(ymaxmin),np.min(ymaxmin))
    

ax1.set_xlim(np.min(xmaxmin), np.max(xmaxmin))
ax1.set_ylim(np.min(ymaxmin), np.max(ymaxmin))

 
axcb = fig1.colorbar(line_segments)
if layer_only:
    plt.title('Laser Power. Layer: ' +str(layerNum)+' , '+filename)
else:
    plt.title('Laser Power: '+filename)
axcb.set_label('Laser Power')


plt.show()
