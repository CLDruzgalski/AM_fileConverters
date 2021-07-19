# Script to convert Netfabb XML files to the IFF XML format
# LLNL-CODE-824510
####################################

import xmltodict
from lxml import etree as ET

# input file
xmlfile = 'input.xml'

# output folder
outfolder = 'XML/'

# set laser parameters
layerThickness = 0.05
spotsize = 130

# hatch
powerHatch = 300
speedHatch = 700
spotHatch = 130

# contour
powerContour = 0
speedContour = 700
spotContour = 130


# Open input XML file
with open(xmlfile)as tp:
    doc = xmltodict.parse(tp.read())

# Loop over layers
for layer in doc['xmlToolpath']['Layers']['Layer']:
    layerNum = int(round(float(layer['@z'])/layerThickness))

    if(layerNum==0):
        # No data for layer 0, skip
        continue

    print('Reading layer',layerNum)

    # Write new XML file header
    root = ET.Element('Build')
    thickness = ET.Element('Thickness')
    thickness.text = str("{:.6f}".format(layerThickness))
    root.append(thickness)
    trajectory = ET.Element('Trajectory')
    root.append(trajectory)

    # Loop over exposure/path
    for exposure in layer['Exposure']:

        # Find path type
        linetype = exposure['@polylineType']

        # Get segments
        segments = exposure['Segments']
        nseg = len(segments['Segment'])

        # If only 1 segment, don't loop
        if(nseg==1):
            # Write Path and Tag
            path = ET.SubElement(trajectory,'Path')
            tag = ET.SubElement(path,'Tag')
            if(linetype=='contour-open'):
                powerval = powerContour
                speedval = speedContour
                spotval = spotContour
                tag.text = str('Part 00; Layer {:02d}; Power {:d}; Speed {:d}; BeamSize {:d}; Contour;'.format(layerNum,powerval,speedval,spotval))
            else:
                powerval = powerHatch
                speedval = speedHatch
                spotval = spotHatch
                tag.text = str('Part 00; Layer {:02d}; Power {:d}; Speed {:d}; BeamSize {:d}; Hatch;'.format(layerNum,powerval,speedval,spotval))

            # Get points
            points = segments['Segment']['Point']
            # Set number of segments
            numseg = ET.SubElement(path,'NumSegments')
            numseg.text = str('{:d}'.format(len(points)-1))
            for i in range(len(points)):
                x=points[i]['@x']
                y=points[i]['@y']
                if i==0:
                    # Starting point
                    start = ET.SubElement(path,'Start')
                    xcoord = ET.SubElement(start, 'X')
                    xcoord.text = x #str('{:.6f}'.format(x))
                    ycoord = ET.SubElement(start, 'Y')
                    ycoord.text = y
                else:
                    # Set segment parameters and end point
                    seg = ET.SubElement(path, 'Segment')
                    p = ET.SubElement(seg,'Power')
                    p.text = str('{:.1f}'.format(powerval))
                    s = ET.SubElement(seg,'Speed')
                    s.text = str('{:.1f}'.format(speedval))
                    f = ET.SubElement(seg,'Spotsize')
                    f.text = str('{:.1f}'.format(spotval))
                    end = ET.SubElement(seg,'End')
                    xcoord = ET.SubElement(end, 'X')
                    xcoord.text = x
                    ycoord = ET.SubElement(end, 'Y')
                    ycoord.text = y

        else:
            # if multiple segment with segments, loop
            ind=0
            for s in segments['Segment']:
                # Write Path and Tag
                path = ET.SubElement(trajectory,'Path')
                tag = ET.SubElement(path,'Tag')
                if(linetype=='contour-open'):
                    powerval = powerContour
                    speedval = speedContour
                    spotval = spotContour
                    tag.text = str('Part 00; Layer {:02d}; Power {:d}; Speed {:d}; BeamSize {:d}; Contour;'.format(layerNum,powerval,speedval,spotval))
                else:
                    powerval = powerHatch
                    speedval = speedHatch
                    spotval = spotHatch
                    tag.text = str('Part 00; Layer {:02d}; Power {:d}; Speed {:d}; BeamSize {:d}; Hatch;'.format(layerNum,powerval,speedval,spotval))
                # Get points
                points = s['Point']

                # set number of segments, this should be double-checked
                numseg = ET.SubElement(path,'NumSegments')
                numseg.text = str('{:d}'.format(len(points)-1))
                for i in range(len(points)):
                    x=points[i]['@x']
                    y=points[i]['@y']
                    if i==0:
                        # Starting point
                        start = ET.SubElement(path,'Start')
                        xcoord = ET.SubElement(start, 'X')
                        xcoord.text = x
                        ycoord = ET.SubElement(start, 'Y')
                        ycoord.text = y
                    else:
                        # Set segment parameters and end point
                        seg = ET.SubElement(path, 'Segment')
                        p = ET.SubElement(seg,'Power')
                        p.text = str('{:.1f}'.format(powerval))
                        s = ET.SubElement(seg,'Speed')
                        s.text = str('{:.1f}'.format(speedval))
                        f = ET.SubElement(seg,'Spotsize')
                        f.text = str('{:.1f}'.format(spotval))
                        end = ET.SubElement(seg,'End')
                        xcoord = ET.SubElement(end, 'X')
                        xcoord.text = x
                        ycoord = ET.SubElement(end, 'Y')
                        ycoord.text = y
                    ind+=1

    # Write layer XML file
    tree = ET.ElementTree(root)
    with open (outfolder+str(layerNum).zfill(3)+'.xml', "wb") as files :
        tree.write(files, pretty_print=True)
