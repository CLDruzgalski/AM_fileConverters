"""
created by ashby7 10.27.2021
This script converts XML files to ParaView readable VTK files 
"""

import time
import vtk
import os

def main():
    ###enter information###
    XML_folder='/path/to/XML/files/'		    ##path to xml files, note no other files should be present in folder 
    VTK_folder='/path/to/output/VTK/files' 	    ##path to output vtk files
    filename_VTK='VTK_filename' 		    ##VTK output filename
    scale=0.05				 ##layer thickness, leave ==0 if this is defined by 'Thickness' tag in XML file
    unit_scale=1000.0			 ##factor that multiplys energy density
    printON=True			 ##print segment check for each file and other checks
    ###end enter information###

    print('output file',VTK_folder+filename_VTK)
    ###initialize variables###
    record=False
    layer_count=0
    strike_count=0
    grid,points,layer,power,speed,focus,energy,strike,line_list=initialize_VTK_variables()
    total_layers=len(os.listdir(XML_folder))
    initial_layer=float(sorted(os.listdir(XML_folder))[0][:-3])

    for f in sorted(os.listdir(XML_folder)):
        print('current XML file',f)
        file1=open(XML_folder+f,'r')
        lines=file1.readlines()
        number_of_segments=0
        strike_count=0
        points_check=[]
        for l in range(len(lines)):
            if scale==0 and '<Thickness>' in lines[l]:
                scale=float(lines[l][lines[l].find('>',10)+1:lines[l].find('<',10)])
            elif 'NumSegments' in lines[l]:
                path_segments=int(lines[l][lines[l].find('>',2)+1:lines[l].find('<',2)])
                number_of_segments=path_segments+number_of_segments
	    ###defines information for each segment###	
            if '<Start>' in lines[l] and '</Segment>' in lines[l+12]:
                if '<X>' in lines[l+1]:
                    start_x=float(lines[l+1][lines[l+1].find('>',1)+1:lines[l+1].find('<',1)])
                if '<Y>' in lines[l+2]:
                    start_y=float(lines[l+2][lines[l+2].find('>',1)+1:lines[l+2].find('<',1)])
                strike_count=strike_count+1
                if '<Segment>' in lines[l+4]:
                    strike_count=strike_count+1
                if '<Power>' in lines[l+5]:
                    current_power=float(lines[l+5][lines[l+5].find('>',1)+1:lines[l+5].find('<',1)])
                if '<Speed>' in lines[l+6]:
                    current_speed=float(lines[l+6][lines[l+6].find('>',1)+1:lines[l+6].find('<',1)])
                if '<Spotsize>' in lines[l+7] or '<Focus>' in lines[l+7]:
                    current_focus=float(lines[l+7][lines[l+7].find('>',1)+1:lines[l+7].find('<',1)])
                if '<End>' in lines[l+8] and '<X>' in lines[l+9] and '<Y>' in lines[l+10]:
                    end_x=float(lines[l+9][lines[l+9].find('>',1)+1:lines[l+9].find('<',1)])
                    end_y=float(lines[l+10][lines[l+10].find('>',1)+1:lines[l+10].find('<',1)])
                    record=True
            elif '<Segment>' in lines[l] and '</Segment>' in lines[l-1]:
                if '<X>' in lines[l-4] and '<Y>' in lines[l-3]: ##this assumes the end of the previous segement is the start of the next
                    start_x=float(lines[l-4][lines[l-4].find('>',1)+1:lines[l-4].find('<',1)])
                    start_y=float(lines[l-3][lines[l-3].find('>',1)+1:lines[l-3].find('<',1)])
                if '<Segment>' in lines[l] and '</Segment>' in lines[l+8]:
                    strike_count=strike_count+1
                if '<Power>' in lines[l+1]:
                    current_power=float(lines[l+1][lines[l+1].find('>',1)+1:lines[l+1].find('<',1)])
                if '<Speed>' in lines[l+2]:
                    current_speed=float(lines[l+2][lines[l+2].find('>',1)+1:lines[l+2].find('<',1)])
                if '<Spotsize>' in lines[l+3] or '<Focus>' in lines[l+3]:
                    current_focus=float(lines[l+3][lines[l+3].find('>',1)+1:lines[l+3].find('<',1)])
                if '<End>' in lines[l+4] and '<X>' in lines[l+5] and '<Y>' in lines[l+6]:
                    end_x=float(lines[l+5][lines[l+5].find('>',1)+1:lines[l+5].find('<',1)])
                    end_y=float(lines[l+6][lines[l+6].find('>',1)+1:lines[l+6].find('<',1)])
                    record=True
	    ###end defines each segment###
	    ###add information to itself for each segment###
            if record:
                current_height=layer_count*scale
                
                points_check.append([start_x,start_y,current_height])
                points_check.append([end_x,end_y,current_height])
                points.InsertNextPoint(start_x,start_y,current_height)
                points.InsertNextPoint(end_x,end_y,current_height)
           
                grid.InsertNextCell(vtk.VTK_LINE,2,[line_list,line_list+1])
                line_list=line_list+2
            
                layer.InsertNextTuple1(layer_count)
                power.InsertNextTuple1(current_power)
                speed.InsertNextTuple1(current_speed)
                focus.InsertNextTuple1(current_focus)
                energy.InsertNextTuple1(current_power/(current_speed*current_focus)*unit_scale)
                strike.InsertNextTuple1(strike_count)
                
                record=False
	    ###end add information###
	###add to array for current layer/file###
        grid.SetPoints(points)
        grid.GetCellData().AddArray(layer)
        grid.GetCellData().AddArray(power)
        grid.GetCellData().AddArray(speed)
        grid.GetCellData().AddArray(focus)
        grid.GetCellData().AddArray(energy)
        grid.GetCellData().AddArray(strike)
	###end add to array###
        
        if number_of_segments==strike_count:
            if printON:
                print('number of segments matches strikes',number_of_segments,'==',strike_count)
        else:
            if printON:
                print('number of segments and strikes do not match',number_of_segments,'=!',strike_count)
	
	###write the VTK file###
        write_layer_to_VTK(grid,VTK_folder+filename_VTK,layer_count)
	###end write###
        
        layer_count=layer_count+1	##add to layer count before moving to next xml file
        grid,points,layer,power,speed,focus,energy,strike,line_list=initialize_VTK_variables()   				##reset variables
    if printON:
        print('first layer',initial_layer)
        print('total layers',total_layers,layer_count)
     
def initialize_VTK_variables():
    """
    initializes all needed vtk variables:
    grid, points, layer, power, speed, focus, energy, strike
    """
    
    grid=vtk.vtkUnstructuredGrid()
    
    points=vtk.vtkPoints()
    
    layer=vtk.vtkIntArray()
    layer.SetNumberOfComponents(1)
    layer.SetName('Layer')
    
    power=vtk.vtkIntArray()
    power.SetNumberOfComponents(1)
    power.SetName('Power')
    
    speed=vtk.vtkIntArray()
    speed.SetNumberOfComponents(1)
    speed.SetName('Speed')
    
    focus=vtk.vtkIntArray()
    focus.SetNumberOfComponents(1)
    focus.SetName('Focus')
    
    energy=vtk.vtkIntArray()
    energy.SetNumberOfComponents(1)
    energy.SetName('Energy Density')
    
    strike=vtk.vtkUnsignedCharArray()
    strike.SetNumberOfComponents(1)
    strike.SetName('Strike Count')
    
    line_list=0
    
    return grid,points,layer,power,speed,focus,energy,strike,line_list

def write_layer_to_VTK(grid,filename,layer_count):
    """
    write VTK file
    """
    writer=vtk.vtkUnstructuredGridWriter()
    writer.SetFileName(filename+'_'+str(layer_count)+'.vtk')
    writer.SetInputData(grid)
    writer.SetFileTypeToBinary()
    writer.Write()



if __name__=='__main__':
    main()
