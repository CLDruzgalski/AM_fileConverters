#####################################################################################
#####################################################################################
### This script plots the power and velocity along the scan path
### contained in an XML file. 
#####################################################################################
#####################################################################################

import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import os
import matplotlib.cm as cm
import matplotlib.animation as ani

specificLayer=True
plotPower=True
plotVelocity=True
figureSave=True
zn=5	##number of fill zeros
filePath = 'path/to/XML_files/'
if specificLayer:
	fileName = 'xml_file_name'+'.xml'
else:
	fileName=sorted([f for f in os.listdir(filePath) if f.endswith('.xml')])
print('fileName contains:',fileName)

if figureSave:
	plotPath=filePath+'/XMLplots/'
	if os.path.exists(plotPath)==False:
		os.mkdir(plotPath)

maxPower = 300	##maximum power 
maxVelocity = 3000 ##maximum velocity

################################################################
#### Get power, velocity, and position data from XML file
################################################################
if specificLayer:
	layerFile = open(filePath + fileName)
	tree = ET.parse(layerFile)
	root = tree.getroot()
	Path = []
	for path in root.iter('Path'):
	    X = []
	    Y = []
	    P = []
	    U = []
	    X.append(float(path[2][0].text))
	    Y.append(float(path[2][1].text))
	    for segment in path.iter('Segment'):
	        X.append(float(segment[3][0].text))
	        Y.append(float(segment[3][1].text))
	        P.append(float(segment[0].text))
	        U.append(float(segment[1].text))
	
	    pathElements = [X,Y,P,U]
	    Path.append(pathElements)
else:
	Lay=[]
	for f in fileName:
		layerFile = open(filePath + f)
		tree = ET.parse(layerFile)
		root = tree.getroot()
		Path = []
		for path in root.iter('Path'):
		    X = []
		    Y = []
		    P = []
		    U = []
		    X.append(float(path[2][0].text))
		    Y.append(float(path[2][1].text))
		    for segment in path.iter('Segment'):
		        X.append(float(segment[3][0].text))
		        Y.append(float(segment[3][1].text))
		        P.append(float(segment[0].text))
		        U.append(float(segment[1].text))
		
		    pathElements = [X,Y,P,U]
		    Path.append(pathElements)
		Lay.append(Path)
	
#################################################################
#### Plot Power as a function of position 
#################################################################
if plotPower and specificLayer:
	fig1, ax1 = plt.subplots()
	cmap = plt.get_cmap('Reds')
	plt.xlim(-10, 10)
	plt.ylim(-10, 10)
	
	for pathNum in range(len(Path)):
	    listOfOrderedPairs = np.array([np.array(Path[pathNum][0]), np.array(Path[pathNum][1])]).T.reshape(-1, 1, 2)
	    segments = np.concatenate([listOfOrderedPairs[:-1], listOfOrderedPairs[1:]], axis=1)
	    line_segments = LineCollection(segments, cmap = cmap)
	    line_segments.set_array(np.array(Path[pathNum][2]))
	    ax1.add_collection(line_segments)
	    plt.sci(line_segments)
	    plt.clim(0, maxPower)
	
	
	axcb = fig1.colorbar(line_segments)
	plt.title('Laser Power. Layer: ' + fileName)
	axcb.set_label('Laser Power')
elif plotPower and specificLayer==False:
	counter=0
	for Path in Lay:
		fig1, ax1 = plt.subplots()
		cmap = plt.get_cmap('Reds')
		plt.xlim(-10, 10)
		plt.ylim(-10, 10)
		
		for pathNum in range(len(Path)):
		    listOfOrderedPairs = np.array([np.array(Path[pathNum][0]), np.array(Path[pathNum][1])]).T.reshape(-1, 1, 2)
		    segments = np.concatenate([listOfOrderedPairs[:-1], listOfOrderedPairs[1:]], axis=1)
		    line_segments = LineCollection(segments, cmap = cmap)
		    line_segments.set_array(np.array(Path[pathNum][2]))
		    ax1.add_collection(line_segments)
		    plt.sci(line_segments)
		    plt.clim(0, maxPower)
		
		
		axcb = fig1.colorbar(line_segments)
		plt.title('Laser Power. Layer: ' + fileName[counter])
		axcb.set_label('Laser Power')
		if figureSave:
			plt.savefig(plotPath+'powerPlot_'+str(counter).zfill(zn)+'.png')
		counter=counter+1
		
#################################################################
#### Plot Velocity as a function of position 
#################################################################
if plotVelocity and specificLayer:
	fig2, ax2 = plt.subplots()
	cmap2 = plt.get_cmap('Blues')
	plt.xlim(-10, 10)
	plt.ylim(-10, 10)
	
	for pathNum in range(len(Path)):
	    listOfOrderedPairs = np.array([np.array(Path[pathNum][0]), np.array(Path[pathNum][1])]).T.reshape(-1, 1, 2)
	    segments = np.concatenate([listOfOrderedPairs[:-1], listOfOrderedPairs[1:]], axis=1)
	    line_segments = LineCollection(segments, cmap = cmap2)
	    line_segments.set_array(np.array(Path[pathNum][3]))
	    ax2.add_collection(line_segments)
	    plt.sci(line_segments)
	    plt.clim(0, maxVelocity)
	
	axcb = fig2.colorbar(line_segments)
	plt.title('Laser Velocity. Layer: ' + fileName)
	axcb.set_label('Laser Velocity')
elif plotVelocity and specificLayer==False:
	counter=0
	for Path in Lay:
		fig2, ax2 = plt.subplots()
		cmap2 = plt.get_cmap('Blues')
		plt.xlim(-10, 10)
		plt.ylim(-10, 10)
		
		for pathNum in range(len(Path)):
		    listOfOrderedPairs = np.array([np.array(Path[pathNum][0]), np.array(Path[pathNum][1])]).T.reshape(-1, 1, 2)
		    segments = np.concatenate([listOfOrderedPairs[:-1], listOfOrderedPairs[1:]], axis=1)
		    line_segments = LineCollection(segments, cmap = cmap2)
		    line_segments.set_array(np.array(Path[pathNum][3]))
		    ax2.add_collection(line_segments)
		    plt.sci(line_segments)
		    plt.clim(0, maxVelocity)
		
		axcb = fig2.colorbar(line_segments)
		plt.title('Laser Velocity. Layer: ' + fileName[counter])
		axcb.set_label('Laser Velocity')
		if figureSave:
			plt.savefig(plotPath+'powerVelocity_'+str(counter).zfill(zn)+'.png')
		counter=counter+1
if specificLayer:
	plt.show()

